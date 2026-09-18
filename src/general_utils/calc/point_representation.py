"""
These functions convert a point between coordinate representations used in this codebase. These representations are:
image, relative, and polar. Four conversions are provided:
    - polar_to_relative(radius, degrees) -> (x, y)
    - relative_to_polar(x, y) -> (radius, degrees)
    - relative_to_corner(x, y, img_shape) -> (x, y)
    - corner_to_relative(x, y, img_shape) -> (x, y)

These representations are defined as follows:
    - image coordinates: (x, y) with origin at the top-left corner of the image, x increasing to the right, and y
            increasing downward (OpenCV / NumPy convention).
    - relative coordinates: (x, y) with origin at the center of the image, x increasing to the right, and y increasing
            upward (mathematical convention).
    - polar coordinates: (radius, degrees) with origin at the center of the image, radius increasing outward, and
            degrees measured counterclockwise from the positive x-axis (mathematical convention).

"""

import math
from src.general_utils.object_types import Point
from src.general_utils.calc.get_angle_from_points import get_angle_from_points

def polar_to_relative(radius: float, degrees: float) -> tuple[float, float]:
    """Convert polar coordinates to relative (image-center-origin, Y-up) coordinates."""
    angle = math.radians(degrees)
    return math.cos(angle) * radius, math.sin(angle) * radius

def relative_to_polar(x: float, y: float) -> tuple[float, float]:
    """Convert relative (image-center-origin, Y-up) coordinates to polar coordinates."""
    return math.dist((0, 0), (x, y)), get_angle_from_points((0, 0), (x, y), range=[0, 360])


def relative_to_corner(x: float, y: float, img_shape: tuple[int, int, int]) -> Point:
    """Convert relative (image-center-origin, Y-up) coordinates to corner (top-left-origin, Y-down) coordinates."""
    height, width = img_shape[0], img_shape[1]
    return round(width / 2 + x), round(height / 2 - y)


def corner_to_relative(point: Point, img_shape: tuple[int, int, int]) -> tuple[int, int]:
    """Convert corner (top-left-origin, Y-down) coordinates to relative (image-center-origin, Y-up) coordinates."""
    height, width = img_shape[0], img_shape[1]
    return round(point[0] - width / 2), round(height / 2 - point[1])
