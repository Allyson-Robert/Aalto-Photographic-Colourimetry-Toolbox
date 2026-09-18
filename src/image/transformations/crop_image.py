from src.general_utils.object_types import Point
from src.image.photograph import Photograph

def crop_image(image: Photograph, topleft: Point, bottomright: Point) -> Photograph:
    """ Takes an image and a sorted pair of points representing the top-left and bottom-right corners of a rectangle,
    and returns a new image that is cropped to that rectangle by slicing. """

    cropped_image = image.get_image()[topleft[1]:bottomright[1], topleft[0]:bottomright[0]]
    return Photograph(cropped_image, image.get_metadata())
