"""Convert image color data between supported color spaces."""

import numpy as np
import colour
import src.defaults as defaults
from src.image.photograph import Photograph
from src.utils.calc.depth_to_max import depth_to_max

colour.utilities.set_default_float_dtype(np.float32)

def convert_image_colour(img: Photograph, input_space: str, output_space: str) -> Photograph:
    """Convert image data from one supported color space to another.

    Args:
        img: The image object to convert.
        input_space: The source representation, such as ``'BGR'`` or ``'LAB'``.
        output_space: The target representation, such as ``'RGB'`` or ``'LAB'``.

    Returns:
        A new Photograph instance containing the converted pixel data and copied metadata.

    Raises:
        ValueError: If the requested input or output space is unsupported.
    """
    # TODO: Reintroduce parallelisation for large images when performance becomes a concern.
    # Extract the metadata and image data as they will be referenced a lot below.
    image_data = img.get_image()
    image_depth = img.get_bit_depth()
    image_model = img.get_colour_model()

    # Validate possible input and output formats
    if not input_space in ('LAB', 'BGR'):
        raise ValueError(f"Unsupported input color space: {input_space}")

    if output_space not in ('LAB', 'BGR', 'RGB', 'xy'):
        raise ValueError(f"Unsupported output color space: {output_space}")

    # Deal with trivial conversions first (no conversion needed)
    if input_space == output_space:
        return img

    # Convert all possible inputs to XYZ first (central pivot)
    xyz_vals = None
    match input_space:
        case 'BGR':
            # Flip and rescale the BGR values to RGB (0 - 1)
            maximum = depth_to_max(image_depth)
            # rgb_vals = np.interp(np.flip(image_data, -1),(0, maximum), (0, 1))
            rgb_vals = np.flip(image_data, -1).astype(np.float32) / maximum

            # Use colour library to convert RGB to XYZ D50
            xyz_vals = colour.RGB_to_XYZ(image_model.cctf_decoding(rgb_vals),
                                         colourspace=image_model,
                                         illuminant=
                                         colour.CCS_ILLUMINANTS['CIE 1931 2 Degree Standard Observer']['D50'])

        case 'LAB':
            # LAB (0 - 100, -100 - 100, -100 - 100) -> XYZ (0 - 1)
            xyz_vals = colour.Lab_to_XYZ(image_data, illuminant=colour.CCS_ILLUMINANTS[
                'CIE 1931 2 Degree Standard Observer'][defaults.reference_illuminant])

            # XYZ (0 - 1) -> XYZ D50 (0 - 1)
            xyz_vals = colour.chromatic_adaptation(xyz_vals, colour.xy_to_XYZ(
                colour.CCS_ILLUMINANTS['CIE 1931 2 Degree Standard Observer'][defaults.reference_illuminant]),
                                                   colour.xy_to_XYZ(colour.CCS_ILLUMINANTS[
                                                                        'CIE 1931 2 Degree Standard Observer'][
                                                                        'D50']))

    # Convert XYZ D50 to the desired output format.
    converted_image_data = None
    match output_space:
        case 'BGR':
            # Use colour library to convert XYZ D50 to RGB (0 - 1)
            rgb_vals = defaults.colour_models[defaults.output_color_space].cctf_encoding(colour.XYZ_to_RGB(
                xyz_vals,
                colourspace=defaults.colour_models[defaults.output_color_space],
                illuminant=colour.CCS_ILLUMINANTS['CIE 1931 2 Degree Standard Observer'][defaults.output_illuminant]
            ))

            maximum = depth_to_max(defaults.output_depth)
            scaled = np.clip(np.flip(rgb_vals, -1), 0, 1) * maximum
            converted_image_data = np.round(scaled).astype(f'uint{defaults.output_depth}')

        case 'LAB':
            xyz_vals = colour.chromatic_adaptation(
                xyz_vals,
                colour.xy_to_XYZ(colour.CCS_ILLUMINANTS['CIE 1931 2 Degree Standard Observer']['D50']),
                colour.xy_to_XYZ(colour.CCS_ILLUMINANTS['CIE 1931 2 Degree Standard Observer'][defaults.output_illuminant])
            )
            converted_image_data = colour.XYZ_to_Lab(
                xyz_vals,
                illuminant=colour.CCS_ILLUMINANTS['CIE 1931 2 Degree Standard Observer'][defaults.output_illuminant]
            )

        case 'RGB':
            rgb_vals = defaults.colour_models[defaults.output_color_space].cctf_encoding(colour.XYZ_to_RGB(
                xyz_vals,
                colourspace=defaults.colour_models[defaults.output_color_space],
                illuminant=colour.CCS_ILLUMINANTS['CIE 1931 2 Degree Standard Observer'][defaults.output_illuminant]
            ))
            converted_image_data = np.clip(rgb_vals, 0, 1)

        case 'xy':
            # TODO: Review whether this should use xyY instead of xy, since xy alone is not a complete color representation.
            converted_image_data = colour.XYZ_to_xy(xyz_vals)

    # TODO: Revisit how metadata is copied for converted images to ensure it stays consistent with the new image data.
    # Copy the metadata from the original image.
    return Photograph(converted_image_data, img.get_metadata())

def convert_colour_depth(img: Photograph, input_depth: float | int, output_depth: float | int) -> Photograph:
    assert input_depth in (1.0, 8, 16), "Input scale must be 1.0, 8, or 16"
    assert output_depth in (1.0, 8, 16), "Output scale must be 1.0, 8, or 16"

    if input_depth == output_depth:
        return img

    factor = depth_to_max(output_depth) / depth_to_max(input_depth)
    img_content = img.get_image()

    scaled = img_content.astype(np.float32) * factor

    if output_depth == 1.0:
        converted_image_data = scaled.astype(np.float32)  # match your float convention
    elif output_depth == 8:
        converted_image_data = np.clip(np.round(scaled), 0, 255).astype(np.uint8)
    else:  # 16
        converted_image_data = np.clip(np.round(scaled), 0, 65535).astype(np.uint16)

    return Photograph(converted_image_data, img.get_metadata())