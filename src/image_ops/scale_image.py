import settings
import cv2 as cv
from src.image.photograph import Photograph

def scale_image(photo: Photograph , multiplier: float = None):
    """
        Returns a scaled copy of the input Photograph
    """

    # Copy the image so that the original is not edited
    photo_copy = photo.copy()

    if multiplier is None:
       multiplier = min(settings.max_window[0] / photo_copy[0].shape[1],
                        settings.max_window[1] / photo_copy[0].shape[0])

    scaled_contents = cv.resize(photo_copy.get_image(), None, fx=multiplier, fy=multiplier, interpolation=cv.INTER_NEAREST)
    scaled_photo = Photograph.from_image_data(scaled_contents, photo_copy.get_metadata())

    return scaled_photo
