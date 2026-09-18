from dataclasses import dataclass
from general_utils.object_types import Point


@dataclass
class TransformationState:
    """ Keeps track of all the transformation applied to images to apply in batch/repeated contexts """
    image_scale: float

    rotation_angle: float

    crop_top_left: Point
    crop_bottom_right: Point

    translation_offset: float
