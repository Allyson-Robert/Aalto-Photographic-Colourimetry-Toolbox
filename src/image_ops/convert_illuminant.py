from src.image.image_base import ImageBase
import colour

def convert_illuminant(img: ImageBase, input_illuminant: str, output_illuminant: str) -> ImageBase:
    """Convert the illuminant of an image or reference chart to a different illuminant.

    Args:
        img: The image or reference chart to convert.
        input_illuminant: The current illuminant of the image or reference chart.
        output_illuminant: The desired illuminant to convert to.
    """

    image_pixels = img.get_image()
    xyz_vals = colour.Lab_to_XYZ(
        image_pixels,
        illuminant=colour.CCS_ILLUMINANTS['CIE 1931 2 Degree Standard Observer'][input_illuminant]
    )

    xyz_vals = colour.chromatic_adaptation(
        xyz_vals,
        colour.xy_to_XYZ(colour.CCS_ILLUMINANTS['CIE 1931 2 Degree Standard Observer'][input_illuminant]),
        colour.xy_to_XYZ(colour.CCS_ILLUMINANTS['CIE 1931 2 Degree Standard Observer'][output_illuminant])
    )

    lab_vals = colour.XYZ_to_Lab(
        xyz_vals,
        illuminant=colour.CCS_ILLUMINANTS['CIE 1931 2 Degree Standard Observer'][output_illuminant]
    )

    return type(img).from_image_data(lab_vals, img.get_metadata())
