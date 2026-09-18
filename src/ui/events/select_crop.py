from src.image.photograph import Photograph
from src.general_utils.object_types import CropPoints
import src.ui.events.point_selection as pt_selection
from general_utils.calc.get_corners_from_points import  get_corners_from_points
from ui.events.run_point_selection import run_point_selection

def select_crop(image: Photograph) -> CropPoints:
    """ Request user to select a crop region from the given image. The user is prompted to select a rectangular region
    of interest (ROI) using the mouse. The selected ROI is returned as a tuple of two points: the top-left and
    bottom-right corners of the rectangle."""

    converted_image = convert_image_colour(image)

    callback_state, keypress_action = run_point_selection(converted_image, pt_selection.PointSelectionMode.CROP)

    match keypress_action:
        case 'confirm':
            corners = get_corners_from_points(*callback_state.get_points())
            return CropPoints(top_left=corners[0], bottom_right=corners[1])
        case _:
            return None

