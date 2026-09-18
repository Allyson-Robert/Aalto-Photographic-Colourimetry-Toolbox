import cv2 as cv
from src.image.photograph import Photograph

def scale_image(image: Photograph, multiplier: float = 1.0):
    """
        Returns a scaled copy of the input Photograph
    """

    # Copy the image so that the original is not edited
    img = image.get_image().copy()
    scaled_contents = cv.resize(img, None, fx=multiplier, fy=multiplier, interpolation=cv.INTER_NEAREST)
    scaled_photo = Photograph(scaled_contents, image.get_metadata())

    return scaled_photo
