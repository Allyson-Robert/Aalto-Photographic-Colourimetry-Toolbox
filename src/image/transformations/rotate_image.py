from src.image.photograph import Photograph
import numpy as np
import cv2 as cv

from general_utils.calc.get_angle_from_points import get_angle_from_points
from general_utils.object_types import Point


def rotate_image(img: Photograph, angle, interpolate=True):
    """ Return a rotated copy of the given image. Rotation is performed around the center of the image. The angle is
    specified in degrees, counterclockwise. If interpolate is True, cubic interpolation is used; otherwise,
    nearest-neighbor interpolation is used.

    Attributes:
        img: The image to rotate
        angle: The angle to rotate the image, in degrees. Positive values rotate counterclockwise
        interpolate: If True, use cubic interpolation; otherwise, use nearest-neighbor interpolation
    """
    image_pixels = img.get_image().copy()
    image_center = tuple(np.array(image_pixels.shape[1::-1]) / 2)
    rot_mat = cv.getRotationMatrix2D(image_center, angle, 1.0)

    if interpolate:
        interpolation = cv.INTER_CUBIC
    else:
        interpolation = cv.INTER_NEAREST

    # Apply rotation to copy of given image
    rotated_image = cv.warpAffine(image_pixels, rot_mat, image_pixels.shape[1::-1], flags=interpolation)

    return Photograph(rotated_image, img.get_metadata())


def apply_tilt(image: Photograph, left: Point, right: Point) -> Photograph:
    """ Takes an image and a left-to-right sorted pair of points and returns a new image that is rotated to align the
    line defined by those points horizontally. """

    angle = get_angle_from_points(left, right)
    return rotate_image(image, angle)
