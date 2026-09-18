import multiprocessing
import colour

# set to true to show additional prompts or images
debug = False

max_window = [1400, 680]        # width, height (px), window size limits
selection_zoom = 8              # Zoom ratio for selecting sample reference points
arrow_alpha = 0.5               # Transparency of measurement arrow
use_colored_printing = False    # Set to True if terminal used supports colored printing

prompt_focus_height = False     # Ask user to input focus height? (Not in use, requires new interpolation algorithm)
check_capture_settings = False  # Check if images match calibration capture settings?
save_gray_images = True        # Keep ref. gray images?
gray_warning_limit = 1.5        # ref. gray min. dE for warning

input_extension = 'tif'         # Input file extension

reference_illuminant = 'D50'    # Hardcoded for now, should be read from XML
output_illuminant = 'D50'       # 'D50' (recommended, common in printing), 'D65' (common in other applications)
output_color_space = 'PROPHOTO' # 'SRGB', 'ADOBE', 'PROPHOTO' (recommended)
output_depth = 16               # 8 or 16 (recommended) bit
output_extension = 'tif'        # Output file extension

uniformity_scale = 0.03         # Uniformity image_transformations resolution
ciede_max = 2.55                # CIEDE2000 value interpolated to max brightness

# Range of input LAB, max. range: (0, -100, -100), (100, 100, 100), natural colors usually (0, -40, -50), (100, 50, 60)
input_lab_domain = ((0, -100, -100), (100, 100, 100))
correction_epsilon = 1.0                            # Epsilon: smooth -> sharp curves
lut_size = 16                                      # Create 3D LUT of dimensions (lut_size x lut_size x lut_size x 3)
rbf_chunk_points = 50000                          # Number of query points per chunk for RBF evaluation, lower it if you get MemoryError

prompt_margin_utilization = True                   # Ask user if safety margins should be used? If not, will be used.
ref_margins = (0.2, 0.15)                           # Safety margins for reference gray images (x, y)

colour_models = {
    'SRGB': colour.models.RGB_COLOURSPACE_sRGB,
    'ADOBE': colour.models.RGB_COLOURSPACE_ADOBE_RGB1998,
    'PROPHOTO': colour.models.RGB_COLOURSPACE_PROPHOTO_RGB,
    'ACES': colour.models.RGB_COLOURSPACE_ACES2065_1
}
color_spaces = colour_models.keys()

bit_depths = (8, 16)                                # Supported bit depths
reference_types = ('colorcheckeroutdated', 'it87', 'it87t')              # Supported reference types

# EXIF data to save
exif_data = ('EXIF:XResolution', 'EXIF:YResolution', 'EXIF:ResolutionUnit', 'EXIF:Make', 'EXIF:Model', 'EXIF:FNumber',
             'EXIF:ExposureTime', 'EXIF:ISO', 'EXIF:ExposureCompensation', 'EXIF:FocalLength', 'EXIF:MaxApertureValue',
             'EXIF:MeteringMode', 'EXIF:Flash', 'EXIF:FocalLengthIn35mmFormat', 'EXIF:Contrast', 'EXIF:BrightnessValue',
             'EXIF:ExposureMode', 'EXIF:Saturation', 'EXIF:Sharpness', 'EXIF:WhiteBalance', 'EXIF:DigitalZoomRatio',
             'EXIF:ExifVersion', 'EXIF:DateTimeOriginal')

main_directory = r'/u/56/roberta2/unix/Pictures/Imaging System'                   # Main directory for images
directories = (r'Calibration/Image Uniformity', r'Calibration/Correction Profiles', r'Calibration/Spectra',
               r'Calibration/Calibration Images', r'Corrected Images', r'Exported Images', r'Remote Capture')

system_memory = 16000000                        # Bytes of system memory to utilize
# cpu_threads = multiprocessing.cpu_count() - 1   # Number of threads to utilize, 0 for no parallel processing
cpu_threads = 0

# Window prompts
prompts = {'horizontal': "Drag horizontal line, then press ENTER.",
           'crop': "Select crop, then press ENTER.",
           'ref': "Select reference points, then press ENTER.",
           'ref-timelapse': "Select reference points, then press ENTER. "
                            "To use the same ref. points for rest of images, press A prior to ENTER.",
           'line': "Drag line to measure, then press ENTER. "
                   "You can adjust the width of the measured line using the mouse wheel."}

# Console print color list
print_colors = {'error': '\033[91m', 'green': '\033[92m', 'warning': '\033[93m', 'blue': '\033[94m', 'end': '\033[0m'}

# Settings for automated testing
automated = True
auto_mode = 4
auto_calib_mode = 0
auto_ref = 'it87'
auto_height = '645'
auto_ref_points = ([-3760, 2449], [3916, -1700])
auto_template_ref_points = ([-906, 573], [898, -417])
auto_ref_crop = (0.0, ((-3896, 2605), (3873, -2558)))
auto_margins = False
auto_lut_filename = f'{auto_height}-{auto_margins}-{lut_size}.cube'

# Override a few things
if automated:
    prompt_margin_utilization = False
    debug = False