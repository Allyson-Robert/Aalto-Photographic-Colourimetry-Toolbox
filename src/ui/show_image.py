from src.image.photograph import Photograph
import cv2 as cv

def show_image(image: Photograph, window_name: str):
    cv.imshow(window_name, image.get_image())
    cv.setWindowProperty(window_name, cv.WND_PROP_TOPMOST, 1)