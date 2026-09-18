import src.defaults as defaults
from src.image.photograph import Photograph


def get_scaling_factor_from_window_size(photo: Photograph):
    """
        Returns the scaling factor to fit the input Photograph into the default window size
    """
    width = photo.get_image().shape[1]
    height = photo.get_image().shape[0]

    return min(defaults.max_window[0] / width,
               defaults.max_window[1] / height)