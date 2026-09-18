"""Accumulator for image transformations determined over a pipeline run.

Each field starts unset (``None``) and is expected to be written exactly
once via its ``set_*`` method as the corresponding pipeline stage runs
(e.g. ``select_tilt`` calls ``set_rotation_angle``). Consumers that need a
value call the matching ``get_*`` accessor and handle the resulting
``ValueError`` themselves if the field may legitimately be absent at that
point in the pipeline — this class has no opinion on which fields any
particular consumer needs.
"""

from dataclasses import dataclass

from general_utils.object_types import Point


@dataclass
class TransformationState:
    """Record of all transformations applied to (or planned for) an image.

    Fields are set once via ``set_*``. Use the corresponding ``reset_*``
    method if a value genuinely needs to be overwritten (e.g. redoing a
    selection step).
    """

    image_scale: float | None = None
    rotation_angle: float | None = None
    crop_top_left: Point | None = None
    crop_bottom_right: Point | None = None
    translation_offset: Point | None = None

    # -- image_scale ---------------------------------------------------

    def get_image_scale(self) -> float:
        if self.image_scale is None:
            raise ValueError("image_scale is not set")
        return self.image_scale

    def set_image_scale(self, value: float) -> None:
        if self.image_scale is not None:
            raise ValueError("image_scale is already set")
        self.image_scale = value

    def reset_image_scale(self, value: float) -> None:
        self.image_scale = value

    # -- rotation_angle --------------------------------------------------

    def get_rotation_angle(self) -> float:
        if self.rotation_angle is None:
            raise ValueError("rotation_angle is not set")
        return self.rotation_angle

    def set_rotation_angle(self, value: float) -> None:
        if self.rotation_angle is not None:
            raise ValueError("rotation_angle is already set")
        self.rotation_angle = value

    def reset_rotation_angle(self, value: float) -> None:
        self.rotation_angle = value

    # -- crop_top_left ---------------------------------------------------

    def get_crop_top_left(self) -> Point:
        if self.crop_top_left is None:
            raise ValueError("crop_top_left is not set")
        return self.crop_top_left

    def set_crop_top_left(self, value: Point) -> None:
        if self.crop_top_left is not None:
            raise ValueError("crop_top_left is already set")
        self.crop_top_left = value

    def reset_crop_top_left(self, value: Point) -> None:
        self.crop_top_left = value

    # -- crop_bottom_right -------------------------------------------------

    def get_crop_bottom_right(self) -> Point:
        if self.crop_bottom_right is None:
            raise ValueError("crop_bottom_right is not set")
        return self.crop_bottom_right

    def set_crop_bottom_right(self, value: Point) -> None:
        if self.crop_bottom_right is not None:
            raise ValueError("crop_bottom_right is already set")
        self.crop_bottom_right = value

    def reset_crop_bottom_right(self, value: Point) -> None:
        self.crop_bottom_right = value

    # -- translation_offset -----------------------------------------------

    def get_translation_offset(self) -> Point:
        if self.translation_offset is None:
            raise ValueError("translation_offset is not set")
        return self.translation_offset

    def set_translation_offset(self, value: Point) -> None:
        if self.translation_offset is not None:
            raise ValueError("translation_offset is already set")
        self.translation_offset = value

    def reset_translation_offset(self, value: Point) -> None:
        self.translation_offset = value