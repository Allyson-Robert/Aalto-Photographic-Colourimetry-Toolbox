from image.photograph import Photograph
from image.transformations.crop_image import crop_image
from image.transformations.rotate_image import rotate_image
from image.transformations.scale_image import scale_image
from image.transformations.transformation_state import TransformationState
from image.transformations.translate_image import translate_image


def transform_image(image: Photograph, transformation_state: TransformationState | None = None):
    """ Transform an image according to the given transformation state. If none was passed request the user to select
    the transformations from the image before applying. """

    if transformation_state is None:
        raise ValueError("No transformations have been set in the transformation state.")

    if transformation_state.get_image_scale() is not None:
        image = scale_image(image, transformation_state.get_image_scale())

    if transformation_state.get_crop_points() is not None:
        image = crop_image(image, transformation_state.get_crop_points())

    if transformation_state.get_rotation_angle() is not None:
        image = rotate_image(image, transformation_state.get_rotation_angle())

    if transformation_state.get_translation_offset() is not None:
        image = translate_image(image, transformation_state.get_translation_offset())

    return image