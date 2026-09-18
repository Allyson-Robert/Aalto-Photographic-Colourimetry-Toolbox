import numpy as np

from src.image.photograph import Photograph
from src.image_transformations.scale_image import scale_image
from src.image_transformations.translate_image import translate_image

def zoom_image(image: Photograph, zoom_coord: tuple | None, zoom_factor: float):
    # Compute offset to center zoom around the specified coordinate. If no coordinate is provided, zoom to the center of the image.
    if zoom_coord is None:
        offset = np.array((0, 0))
    else:
        offset = np.divide((image.get_image().shape[1] / 2 - zoom_coord[0], zoom_coord[1] - image.get_image().shape[0] / 2),
                           1 + 1 / (zoom_factor - 1))
    zoomed_image = scale_image(translate_image(image,  offset), zoom_factor)

    return zoomed_image
