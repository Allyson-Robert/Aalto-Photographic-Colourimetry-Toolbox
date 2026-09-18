from image.photograph import Photograph
from image.transformations.crop_image import crop_image
from image.transformations.rotate_image import rotate_image
from image.transformations.scale_image import scale_image
from image.transformations.transformation_state import TransformationState
from image.transformations.translate_image import translate_image
from image.transformations.utils.get_scaling_factor_from_window_size import get_scaling_factor_from_window_size
from ui.events.select_crop import select_crop
from ui.events.select_tilt import select_tilt


def transform_image(image: Photograph, transformation_state: TransformationState | None = None):
    """ Transform an image according to the given transformation state. If none was passed request the user to select
    the transformations from the image before applying. """

    if transformation_state is None:
        # Initialise a transformation state to record the transformations applied to the image
        transformation_state = TransformationState()
        selection_image = image.copy()

        # Automatically detect the scale based on the window size and scale the image accordingly
        transformation_state.set_image_scale(get_scaling_factor_from_window_size(selection_image))
        selection_image = scale_image(selection_image, transformation_state.get_image_scale())

        # Tilt-shift the image
        selected_tilt = select_tilt(selection_image)
        transformation_state.set_rotation_angle(selected_tilt)
        selection_image = rotate_image(selection_image, transformation_state.get_rotation_angle())

        # Crop the (rotated) image
        cropping_corners = select_crop(selection_image)
        transformation_state.set_crop_points(cropping_corners)
        crop_image(selection_image, transformation_state.get_crop_points())

    # Apply all transformations to the original image in order of scale -> crop -> rotate -> translate
    if transformation_state.get_image_scale() is not None:
        image = scale_image(image, transformation_state.get_image_scale())

    if transformation_state.get_crop_points() is not None:
        image = crop_image(image, transformation_state.get_crop_points())

    if transformation_state.get_rotation_angle() is not None:
        image = rotate_image(image, transformation_state.get_rotation_angle())

    if transformation_state.get_translation_offset() is not None:
        image = translate_image(image, transformation_state.get_translation_offset())

    return image