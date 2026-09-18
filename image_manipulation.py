from colour.appearance.nayatani95 import scaling_coefficient

import settings
import utilities
import image_utilities
import main_script

import os
import math
import numpy as np
import cv2 as cv
import colour

from image.photograph import Photograph

set_all = False  # Set rest of ref. points based on current selection?


def adjust_color(in_img, in_lut, is_thread=False, gray_refs=((0, 0, 0), None), operations=1):
    """Correct image with LUT"""
    if is_thread or settings.cpu_threads == 0 or max(in_img[0].shape) < settings.cpu_threads:
        # Split image by memory usage
        if len(in_img[0].shape) > 1:
            memory_usage = np.prod(in_img[0].shape) * operations
            split_img = np.array_split(in_img[0], math.ceil(memory_usage / settings.system_memory))

            out_img = []
            for i in range(len(split_img)):
                split_img[i] = (split_img[i], in_img[1])  # Include metadata in split image

                # Convert image to flat format
                start_col = split_img[i][0]
                lab_i = np.array((np.take(start_col, 0, axis=2).flatten(),
                                  np.take(start_col, 1, axis=2).flatten(),
                                  np.take(start_col, 2, axis=2).flatten()))

                # Apply LUT and gray card difference
                fit_col = in_lut.apply(lab_i.T).reshape(start_col.shape[0], start_col.shape[1], 3)
                if gray_refs[1] is not None:
                    fit_col = convert_color((fit_col, in_img[1]), 'gray-adapt', gray_refs=gray_refs)[0]

                out_img.append(fit_col)

            out_img = (np.concatenate(out_img), in_img[1])  # Combine split image
        else:
            # Apply LUT and gray card difference
            fit_col = in_lut.apply(in_img[0])
            if gray_refs[1] is not None:
                fit_col = convert_color((fit_col, in_img[1]), 'gray-adapt', gray_refs=gray_refs)[0]
            out_img = (fit_col, in_img[1])

        return out_img
    else:
        # Perform multithreaded operation
        out_img = image_utilities.parallel_process(adjust_color, in_img,
                                                   (in_lut, True, gray_refs, settings.cpu_threads))
        return out_img


def crop_samples(sample_name, adjust=False, ref_gray=False, crop_settings=None):
    """Crop sample images"""
    global set_all

    if adjust:
        set_all = False

    # Set sample path
    if len(sample_name.split('-')) > 1:
        if sample_name.split('-')[1].split('_')[0] == 'gray':
            ref_gray = True
        path = rf"Corrected Images\{sample_name.split('-')[0]}\{sample_name}"
    else:
        path = rf"Corrected Images\{sample_name}"
        for sub_path in os.listdir(os.path.join(settings.main_directory, path)):  # Crop each sample in directory
            if len(sub_path.split('.')) == 1 and sub_path != 'Measurements':
                crop_samples(sub_path, adjust, ref_gray)
        return

    print()
    print("Cropping", sample_name)

    file_names = utilities.get_files(path, match_extension=settings.output_extension)  # Get files in order
    if not ref_gray:  # If cropping reference gray, no need to read reference data
        ref_crop_data = image_utilities.read_crop(file_names[0])
        if ref_crop_data is not None:
            start_file = ref_crop_data[1][0] + '.' + settings.output_extension
            # Check if cropped image exists, otherwise ignore existing data
            crop_exists = os.path.exists(os.path.join(rf'{os.path.join(settings.main_directory, path)}\Cropped',
                                                      start_file.split('.')[0] + '_cropped.'
                                                      + settings.output_extension))
        else:
            start_file = file_names[0]  # Use first file alphabetically
            crop_exists = False

        if not crop_exists or adjust:
            img = None
            while img is None:  # Wait for successful read
                img = image_utilities.read_image(start_file, path, convert=False)
            if adjust and ref_crop_data is not None and crop_exists:
                # Start with previous crop data
                ref_crop = match_crop(img, 0, (ref_crop_data[2], ref_crop_data[3]), convert=False)
            else:
                ref_crop = match_crop(img, 0, convert=False)
            if ref_crop is None:
                utilities.print_color("Discarding crop data.", 'warning')
                return

            if adjust and ref_crop_data is not None and crop_exists:
                start_points = match_crop(img, 1, ref_crop_data[1][1], convert=False)  # Start with previous crop data
            else:
                start_points = match_crop(img, 1, convert=False, first=True)
            if start_points is None:
                utilities.print_color("Discarding crop data.", 'warning')
                return
            img_scale = scale_image(img)[1]
        else:
            # Use existing data
            start_file = ref_crop_data[1][0] + '.' + settings.output_extension
            img = image_utilities.read_image(start_file, path, convert=False)
            img_scale = scale_image(img)[1]
            ref_crop = (ref_crop_data[2], ref_crop_data[3])
            start_points = ref_crop_data[1][1]

        ref_point_list = []
        gray_refs = None
    else:
        ref_point_list = []
        gray_refs = {}
        ref_crop_data = None
        img = None
        img_scale = None
        start_points = None
        start_file = None
        ref_crop = None

    if set_all:
        print("Setting rest of series ref. points based on first.")
    img_refs = []
    write_dict = {}
    img_c = None
    new_crop_settings = [None, None]
    for i in range(len(file_names)):
        # Check if crop data exists
        crop_exists = os.path.exists(os.path.join(rf'{os.path.join(settings.main_directory, path)}\Cropped',
                                                  file_names[i].split('.')[0] + '_cropped.'
                                                  + settings.output_extension))
        data_exists = False
        if ((ref_gray or (ref_crop_data is not None and file_names[i].split('.')[0] in ref_crop_data[0]))
                and crop_exists):
            data_exists = True
            if not adjust:
                continue

        if not ref_gray:
            if len(img_refs) == 0:
                # Show zoomed in reference points
                for o in range(2):
                    img_ref = zoom_image((np.interp(img[0],
                                                    (0, main_script.max_val[img[1][0][1]]), (0, main_script.max_val[0])
                                                    ).astype(main_script.bit_type[0]), img[1]),
                                         zoom_point=image_utilities.cvt_point(start_points[o], -1, img[0].shape))
                    cv.drawMarker(img_ref[0],
                                  image_utilities.cvt_point(start_points[o], -1, img_ref[0].shape),
                                  (0, 0, main_script.max_val[img_ref[1][0][1]]), cv.MARKER_TILTED_CROSS,
                                  round(15 / img_scale * 2), round(2 / img_scale * 2))  # Match regular size
                    img_refs.append(img_ref[0])

                image_utilities.show_image("Reference points", scale_image((np.concatenate(img_refs), img[1]))[0],
                                           False)

            img = image_utilities.read_image(file_names[i], path,
                                             convert=False)
            if file_names[i] != start_file and not set_all:
                if data_exists:
                    ref_points = match_crop(img, 1, ref_crop_data[0][file_names[i].split('.')[0]], convert=False)
                else:
                    ref_points = match_crop(img, 1, convert=False)
            else:
                ref_points = start_points

            if ref_points is None:  # Esc pressed, skip sample
                print("Discarding crop data.")
                return

            ref_point_list.append((file_names[i].split('.')[0], ref_points))  # Save ref. points

            ref_angle, ref_scale, ref_translation = image_utilities.get_transformation(start_points, ref_points)

            # Apply rotation, scaling, translation
            img = translate_image(scale_image(rotate_image(img, ref_angle), ref_scale)[0],
                                  ref_translation)
        else:  # No need to save cropping data for ref. grays
            if len(ref_point_list) == 0:
                ref_point_list.append([file_names[i].split('.')[0]])  # Save ref. gray names

            img = image_utilities.read_image(file_names[i], path, convert=False)
            if crop_settings is not None:  # Apply previous rotation and crop
                img_c = get_image_range(rotate_image(img, crop_settings[0]), crop_settings[1])
                ref_crop = crop_settings
            else:
                ref_crop = match_crop(img, 0, convert=False)
            

        if crop_settings is None:
            new_crop_settings[0] = ref_crop[0]
            img_c = rotate_image(img, new_crop_settings[0])  # Apply crop rotation

            # Apply crop
            crop_corner = (image_utilities.cvt_point(ref_crop[1][0], -1, img_c[0].shape),
                           image_utilities.cvt_point(ref_crop[1][1], -1, img_c[0].shape))
            new_crop_settings[1] = ((crop_corner[0][0], crop_corner[1][0]), (crop_corner[0][1], crop_corner[1][1]))
            img_c = get_image_range(img_c, new_crop_settings[1])

        write_dict[file_names[i]] = img_c  # Add image to writing dictionary

        if ref_gray:
            # Write average color
            gray_refs[file_names[i].split('.')[0].split('_')[1]] = tuple(elem for elem in
                                                                         image_utilities
                                                                         .get_average_color(convert_color(img_c, 'in')))
    set_all = False

    if len(write_dict) > 0:
        image_utilities.write_crop(ref_point_list, ref_crop[0], ref_crop[1], gray_refs)
        print("Writing cropped images ...")
        if not gray_refs or settings.save_gray_images:
            for key in write_dict:
                # Write images in dictionary
                image_utilities.write_image(write_dict[key], key.split('.')[0], rf'{path}\Cropped',
                                            '_cropped.' + settings.output_extension, convert=False)
    else:
        print("No new data written.")

    cv.destroyAllWindows()

    if ref_gray:
        return new_crop_settings


from src.image.photograph import Photograph
from src.image.transformations.transformation_state import TransformationState

def match_crop(img: Photograph, transformation_state: TransformationState, mode=1, ref_points=(((0, 0), (0, 0)), ((0, 0), (0, 0))), convert=True, first=False,
               force_prompt=None, close_window=True):
    """Mode 0: Crop first image, 1: Match crop"""

    from src.colour_ops.convert_image_colour import convert_image_colour, convert_colour_depth
    from src.image.transformations.utils.get_scaling_factor_from_window_size import get_scaling_factor_from_window_size

    from src.image.transformations.scale_image import scale_image
    from src.image.transformations.rotate_image import rotate_image
    from src.image.transformations.crop_image import crop_image
    from src.ui.events.select_tilt import select_tilt
    from src.ui.events.select_crop import select_crop

    assert isinstance(img, Photograph), "img must be an instance of Photograph"

    if convert:
        # Convert to sRGB 8bit (stuck to BGR for now)
        img = convert_image_colour(img, input_space='LAB', output_space='BGR')
    img = convert_colour_depth(img, input_depth=img.get_bit_depth(), output_depth=8)

    if mode == 0:  # Crop first imageB
        transformation_state.set_image_scale(get_scaling_factor_from_window_size(img))
        img = scale_image(img, transformation_state.get_image_scale())

        # if ref_points[0] != ((0, 0), (0, 0)):
            # Previous rotation data exists -> Apply
            # img_r = rotate_image(img, ref_points[0])
            # ref_rotated = ref_points[0]
        # else:
            # No rotation
            # img_r = img
            # ref_rotated = 0

        # Tilt-shift the image
        selected_tilt = select_tilt(img)
        transformation_state.set_rotation_angle(selected_tilt)
        img = rotate_image(img, transformation_state.get_rotation_angle())

        # Crop the (rotated) image
        cropping_corners = select_crop(img)
        transformation_state.set_crop(cropping_corners)
        img = crop_image(img, *transformation_state.get_crop())

        return transformation_state

    elif mode == 1:  # Match crop
        img_c, img_scale = scale_image(in_img)  # Scale to max window size
        if np.sum(ref_points) != 0:
            # Scale existing ref. points
            image_utilities.selected_points = ([round(sel_point * img_scale) for sel_point in
                                                image_utilities.cvt_point(ref_points[0], -1,
                                                                          np.divide(img_c[0].shape, img_scale))],
                                               [round(sel_point * img_scale) for sel_point in
                                                image_utilities.cvt_point(ref_points[1], -1,
                                                                          np.divide(img_c[0].shape, img_scale))])
        # Select reference points
        global set_all

        if force_prompt is None:
            if first:
                prompt = settings.prompts['ref-timelapse']
            else:
                prompt = settings.prompts['ref']
        else:
            prompt = force_prompt
        key_pressed = None

        # Only accept reference with both selection points
        while key_pressed is None or any(np.sum(elem) == -2 for elem in image_utilities.selected_points):
            image_utilities.show_image(prompt, img_c, False)
            cv.setMouseCallback(prompt, image_utilities.image_event, param=[prompt, img_c])

            # Call image event to initialize window properly
            image_utilities.image_event(cv.EVENT_LBUTTONUP,
                                        image_utilities.selected_points[0][0], image_utilities.selected_points[0][1],
                                        None, [prompt, img_c])
            key_pressed = image_utilities.wait_key()
            if key_pressed == 'escape':
                # Skip image
                return None
            elif key_pressed == 'space':
                # Use defaults
                break
        if close_window:
            cv.destroyWindow(prompt)

        if key_pressed == 'space':
            # Default reference to corners
            print("Setting default ref. points: corners.")
            ref_points = ((-in_img[0].shape[1] / 2, in_img[0].shape[0] / 2),
                          (in_img[0].shape[1] / 2, -in_img[0].shape[0] / 2))
        else:
            # Use selected reference points
            ref_points = np.divide((image_utilities.cvt_point(image_utilities.selected_points[0], 1, img_c[0].shape),
                                    image_utilities.cvt_point(image_utilities.selected_points[1], 1, img_c[0].shape)),
                                   img_scale)
            if ref_points[0][0] > ref_points[1][0]:
                ref_points = (ref_points[1], ref_points[0])

        image_utilities.selected_points = ((-1, -1), (-1, -1))  # Clear selection

        if not first:
            set_all = False  # Make sure set_all can't be adjusted

        # Round ref. point values
        return [round(ref_point) for ref_point in ref_points[0]], [round(ref_point) for ref_point in ref_points[1]]
    else:
        print("Invalid cropping mode.")
        return None


def crop_target(in_img, template):
    """Crop calibration target using reference points"""

    ref_points = match_crop(in_img, 1, force_prompt=settings.prompts['ref'] + ' ', close_window=False)

    template_ref_points = match_crop(template, 1)

    cv.destroyAllWindows()  # Close both windows

    ref_angle, ref_scale = image_utilities.get_transformation(template_ref_points, ref_points)[:2]

    # Convert to polar coordinates for applying calculated angle and scale
    ref_polar = image_utilities.cvt_point(ref_points[0], 2)
    new_ref = image_utilities.cvt_point((ref_polar[0] * ref_scale, ref_polar[1] + ref_angle), -2)
    # Apply rotation and scaling
    out_img = scale_image(rotate_image(in_img, ref_angle, interpolate=False), ref_scale)[0]

    overlay_offset = (round(template[0].shape[1] / 2 + template_ref_points[0][0]
                            - (out_img[0].shape[1] / 2 + new_ref[0])),
                      round(template[0].shape[0] / 2 - template_ref_points[0][1]
                            - (out_img[0].shape[0] / 2 - new_ref[1])))

    return out_img, overlay_offset


def rotate_image(in_img, rot_angle, interpolate=True):
    """Rotate image by given angle (in mathematically positive direction = counter-clockwise)"""
    image_center = tuple(np.array(in_img[0].shape[1::-1]) / 2)
    rot_mat = cv.getRotationMatrix2D(image_center, rot_angle, 1.0)

    if interpolate:
        interpolation = cv.INTER_CUBIC
    else:
        interpolation = cv.INTER_NEAREST
    # Apply rotation to copy of given image
    img_rot = (cv.warpAffine(in_img[0].copy(), rot_mat, in_img[0].shape[1::-1], flags=interpolation), in_img[1])

    return img_rot


def get_image_range(in_img, in_range):  # in_range format (corner): ((left x, right x), (top y, bottom y))
    """Get given range of image"""
    in_range = ([round(r_pos) for r_pos in in_range[0]], [round(r_pos) for r_pos in in_range[1]])

    # Calculate amount of overflow
    oversize = ((max(-in_range[0][0], 0), max(in_range[0][1] - in_img[0].shape[1], 0)),
                (max(-in_range[1][0], 0), max(in_range[1][1] - in_img[0].shape[0], 0)))

    out_img = (in_img[0][max(0, in_range[1][0]):min(in_img[0].shape[0], in_range[1][1]),
               max(0, in_range[0][0]):min(in_img[0].shape[1], in_range[0][1])], in_img[1])

    # Set pixel values outside image frame to black
    if oversize[0][0] > 0:
        out_img = (np.concatenate((np.zeros((out_img[0].shape[0], oversize[0][0], 3),
                                            dtype=main_script.bit_type[settings.output_depth]), out_img[0]), axis=1),
                   out_img[1])
    if oversize[0][1] > 0:
        out_img = (np.concatenate((out_img[0], np.zeros((out_img[0].shape[0], oversize[0][1], 3),
                                                        dtype=main_script.bit_type[settings.output_depth])), axis=1),
                   out_img[1])
    if oversize[1][0] > 0:
        out_img = (np.concatenate((np.zeros((oversize[1][0], out_img[0].shape[1], 3),
                                            dtype=main_script.bit_type[settings.output_depth]), out_img[0]), axis=0),
                   out_img[1])
    if oversize[1][1] > 0:
        out_img = (np.concatenate((out_img[0], np.zeros((oversize[1][1], out_img[0].shape[1], 3),
                                                        dtype=main_script.bit_type[settings.output_depth])), axis=0),
                   out_img[1])

    return out_img


