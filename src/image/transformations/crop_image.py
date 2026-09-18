from general_utils.object_types import CropPoints
from src.general_utils.object_types import Point
from src.image.photograph import Photograph

def crop_image(image: Photograph, points: CropPoints) -> Photograph:
    """ Takes an image and a sorted pair of points representing the top-left and bottom-right corners of a rectangle,
    and returns a new image that is cropped to that rectangle by slicing. """

    cropped_image = image.get_image()[points.top_left[1]:points.bottom_right[1], points.top_left[0]:points.bottom_right[0]]
    return Photograph(cropped_image, image.get_metadata())
