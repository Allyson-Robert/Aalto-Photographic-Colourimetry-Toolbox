from src.image.photograph import Photograph
from src.colour_ops.convert_image_colour import convert_image_colour
import src.ui.events.point_selection as pt_selection
from ui.events.run_point_selection import run_point_selection
from src.general_utils.calc.get_angle_from_points import get_angle_from_points

def select_tilt(image: Photograph):
    """ Request user to select a tilt line to rotate the given image. The user is prompted to select two points using
    the mouse. The selected points are used to calculate and return the tilt angle."""

    converted_image = convert_image_colour(image)

    callback_state, keypress_action = run_point_selection(converted_image, pt_selection.PointSelectionMode.HORIZONTAL)

    match keypress_action:
        case 'confirm':
            callback_state.sort()
            return get_angle_from_points(*callback_state.get_points())
        case _:
            return None

