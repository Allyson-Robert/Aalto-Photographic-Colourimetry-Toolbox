import cv2 as cv
from src.image.photograph import Photograph

def scale_image(photo: Photograph , multiplier: float = None):
    """
        Returns a scaled copy of the input Photograph
    """

    # Copy the image so that the original is not edited
    photo_c = photo.copy()
    scaled_contents = cv.resize(photo_c.get_image(), None, fx=multiplier, fy=multiplier, interpolation=cv.INTER_NEAREST)
    scaled_photo = Photograph.from_image_data(scaled_contents, photo_c.get_metadata())

    return scaled_photo
