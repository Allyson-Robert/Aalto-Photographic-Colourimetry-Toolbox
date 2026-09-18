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

from general_utils.object_types import Point, CropPoints


@dataclass
class TransformationState:
    """Record of all transformations applied to (or planned for) an image.

    Fields are set once via ``set_*``. Use the corresponding ``reset_*``
    method if a value genuinely needs to be overwritten (e.g. redoing a
    selection step).
    """

    image_scale: float | None = None
    rotation_angle: float | None = None
    crop: CropPoints | None = None
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

    def get_crop(self) -> CropPoints:
        if self.crop is None:
            raise ValueError("crop is not set")
        return self.crop

    def set_crop(self, value: CropPoints) -> None:
        if self.crop is not None:
            raise ValueError("crop is already set")
        self.crop = value

    def reset_crop(self, value: CropPoints) -> None:
        self.crop = value

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