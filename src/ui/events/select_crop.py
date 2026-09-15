from src.image.photograph import Photograph
from src.colour_ops.convert_image_colour import convert_image_colour
from src.ui.show_image import show_image
import src.ui.events.point_selection as pt_selection
import cv2 as cv

from ui.events.keypress import wait_for_valid_keypress
from utils.calc.get_corners_from_points import  get_corners_from_points

def select_crop(image: Photograph):
    """ Request user to select a crop region from the given image. The user is prompted to select a rectangular region
    of interest (ROI) using the mouse. The selected ROI is returned as a tuple of two points: the top-left and
    bottom-right corners of the rectangle."""

    converted_image = convert_image_colour(image)

    callback_state = pt_selection.PointSelectionState()
    context = pt_selection.PointSelectionCallbackContext(mode=pt_selection.PointSelectionMode.CROP,
                                                                 image=converted_image)
    keypress_action = None
    while not (keypress_action or callback_state.is_complete()):
        show_image(converted_image)
        callback_callable = pt_selection.PointSelectionCallback(callback_state)
        cv.setMouseCallback(context.mode.window_title,
                            callback_callable,
                            context)
        keypress_action = wait_for_valid_keypress()
    cv.destroyWindow(context.mode.window_title)

    match keypress_action:
        case 'confirm':
            return get_corners_from_points(*callback_state.get_points())
        case _:
            return None

