from src.utils.object_types import Point
from src.image.photograph import Photograph
from src.utils.calc.get_angle_from_points import get_angle_from_points
from src.image_ops.rotate_image import rotate_image

def apply_tilt(image: Photograph, left: Point, right: Point) -> Photograph:
    """ Takes an image and a left-to-right sorted pair of points and returns a new image that is rotated to align the
    line defined by those points horizontally. """

    angle = get_angle_from_points(left, right)
    return rotate_image(image, angle)