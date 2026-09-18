from general_utils.object_types import Point
from src.image.photograph import Photograph
import cv2 as cv

def translate_image(image: Photograph, offset: Point):
    """
        Returns a translated copy of the input Photograph
    """

    # Copy the image so that the original is not edited
    img = image.get_image().copy()
    translation_matrix = np.float32([[1, 0, offset[0]], [0, 1, offset[1]]])
    translated_contents = cv.warpAffine(img, translation_matrix, (img.shape[1], img.shape[0]))
    translated_photo = Photograph(translated_contents, image.get_metadata())

    return translated_photo
