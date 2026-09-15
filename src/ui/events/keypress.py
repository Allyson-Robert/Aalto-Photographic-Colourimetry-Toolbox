import cv2 as cv

KEY_CODES = {
    13: 'enter', # The enter key should trigger the validation of an operation/data entry
    27: 'escape', # Escape is to cancel operations
    32: 'space', # Spacebar is to set default values
    # 97: 'a' # The 'a' key is used for a special function, such as applying a setting to all items in a batch
}

KEY_ACTIONS = {
    'enter': 'confirm', # The enter key should trigger the validation of an operation/data entry
    'escape': 'abort', # Escape is to cancel operations
    'space': 'default', # Spacebar is to set default values
    # 'a': 'special' # The 'a' key is used for a special function, such as applying a setting to all items in a batch
}

def wait_for_valid_keypress():
    """ Wait for a keypress and return the corresponding action based on the key pressed """
    while True:
        k = cv.waitKey(0)
        if k in KEY_CODES:
            return KEY_ACTIONS[KEY_CODES[k]]

def process_keypress(key):
    raise NotImplementedError