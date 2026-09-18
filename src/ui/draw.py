"""
Drawing utilities for the Aalto Photographic Colourimetry Toolbox.

Returns a copy of the image with the specified shape drawn on it. The original image is not modified.
"""
import math

from src.image.photograph import Photograph
from src.defaults import arrow_alpha
from src.general_utils.calc.depth_to_max import depth_to_max
import cv2 as cv

def draw_arrow(image: Photograph, start_point: tuple[int, int], end_point: tuple[int, int], width: int, preview: bool = False) -> Photograph:
    """Draw transparent arrow on image"""
    img = image.get_image().copy()
    tiplen = (25 / (math.dist(start_point, end_point) + 1))

    cv.arrowedLine(img=img, pt1=start_point, pt2=end_point, color=_shape_colour(image, preview),
        thickness=width, tipLength=tiplen)
    cv.addWeighted(src1=img, alpha=arrow_alpha, src2=image.get_image(), beta=1 - arrow_alpha, gamma=0, dst=img)

    return Photograph(img, image.get_metadata())

def draw_marker(image: Photograph, point: tuple[int, int], preview: bool = False) -> Photograph:
    img = image.get_image().copy()

    cv.drawMarker(img=img, position=point, color=_shape_colour(image, preview),
                  markerType=cv.MARKER_TILTED_CROSS, markerSize=15, thickness=2)
    return Photograph(img, image.get_metadata())

# TODO: Check this implementation against legacy code
def draw_line(image: Photograph, start_point: tuple[int, int], end_point: tuple[int, int], preview: bool = False) -> Photograph:
    img = image.get_image().copy()
    cv.line(img, start_point, end_point, _shape_colour(image, preview), thickness=2)
    return Photograph(img, image.get_metadata())

def draw_rectangle(image: Photograph, upper_left: tuple[int, int], lower_right: tuple[int, int], preview: bool = False) -> Photograph:
    img = image.get_image().copy()
    cv.rectangle(img, upper_left, lower_right, _shape_colour(image, preview), 2)
    return Photograph(img, image.get_metadata())

def _shape_colour(image: Photograph, preview: bool = False) -> tuple[int, int, int]:
    """ Return a colour for drawing shapes on the image. The colour is based on the bit depth of the image. For preview purposes, the colour is set to half of the maximum value for the bit depth."""
    if preview:
        return 0, 0, int(depth_to_max(image.get_bit_depth()) / 2)
    return 0, 0, depth_to_max(image.get_bit_depth())
