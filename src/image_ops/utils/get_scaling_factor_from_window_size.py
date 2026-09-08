import src.defaults as defaults
from src.image.photograph import Photograph


def get_scaling_factor_from_window_size(photo: Photograph):
    """
        Returns the scaling factor to fit the input Photograph into the default window size
    """

    return min(defaults.max_window[0] / photo[0].shape[1],
               defaults.max_window[1] / photo[0].shape[0])