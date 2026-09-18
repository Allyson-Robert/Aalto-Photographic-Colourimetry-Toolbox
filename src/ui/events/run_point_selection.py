from src.image.photograph import Photograph
from src.ui.events.point_selection import PointSelectionMode, PointSelectionState, PointSelectionCallbackContext
from src.ui.events.point_selection import PointSelectionCallback
from src.ui.show_image import show_image
import cv2 as cv
from ui.events.keypress import wait_for_valid_keypress

def run_point_selection(image: Photograph, mode: PointSelectionMode) -> tuple[PointSelectionState, str]:
    """Run point-selection UI, blocking until the user completes the point selection and presses a valid key,
    to be processed by the caller
    """
    state = PointSelectionState()
    context = PointSelectionCallbackContext(mode=mode, image=image)
    callback = PointSelectionCallback(state)

    show_image(image, mode.window_title)
    cv.setMouseCallback(mode.window_title, callback, context)

    keypress_action = None
    while not (keypress_action and state.is_complete()):
        keypress_action = wait_for_valid_keypress()

    cv.destroyWindow(mode.window_title)
    return state, keypress_action