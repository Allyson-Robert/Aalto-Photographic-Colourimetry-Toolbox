import os
import ast
import colour
from src.profile.utils.parse_cube_comments import parse_cube_comments
from src.profile.utils.format_cube_comments import format_cube_comments

class LUTProfile:
    """ Container for LUT profile data.

     Class reads and writes a 3D LUT profile from a .cube file and extracts relevant information such as the LUT content, calibration gray values, color space, bit depth, EXIF metadata, statistics, and sample data.

     Attributes:
        lut_data (colour.LUT3D): The 3D LUT data read from the .cube file.
        gray (tuple): The reference gray values in Lab color space.
        colour_space (str): The color space of the LUT profile.
        bit_depth (int): The bit depth of the LUT profile.
        exif_metadata (ExifMetaData): The EXIF metadata associated with the LUT profile.
        statistics (dict): Statistics related to the calibration, such as average and maximum CIEDE2000 values.
        sample_data (dict): Color coordinates of the sample data used for calibration.
     """

    def __init__(self, lut, gray, colour_space, bit_depth, exif_metadata, statistics, sample_data):
        """Initialize LUTProfile from data."""
        self.gray = gray
        self.colour_space = colour_space
        self.bit_depth = bit_depth
        self.exif_metadata = exif_metadata
        self.statistics = statistics
        self.sample_data = sample_data
        self.lut_data = lut

    @classmethod
    def from_file_location(cls, profile_location) -> "LUTProfile":
        """Read calibration profile from a file on disk and extract data such as LUT content
        and calibration conditions."""
        # Read 3D LUT and comments
        lut = colour.read_LUT(profile_location)
        comments = lut.comments

        # Parse the comments
        parsed_comments = parse_cube_comments(comments)
        gray = parsed_comments['gray']
        colour_space = parsed_comments['color_space']
        bit_depth = parsed_comments['bit_depth']
        exif_metadata = parsed_comments['exit_metadata']
        statistics = parsed_comments['statistics']
        sample_data = parsed_comments['sample_data']

        return cls(lut, gray, colour_space, bit_depth, exif_metadata, statistics, sample_data)

    def get_lut(self):
        return self.lut_data

    def get_gray(self):
        return self.gray

    def write_profile(self, save_location):
        """Write correction profile 3D LUT"""

        # Verify filename extension, add .cube or replace if needed
        if not save_location.lower().endswith('.cube'):
            save_location = os.path.splitext(save_location)[0] + '.cube'

        # Include image format data
        comments = format_cube_comments(self.gray, self.colour_space, self.bit_depth, self.exif_metadata, self.statistics, self.sample_data)

        # Create final 3D LUT
        out_lut = colour.LUT3D(self.lut_data.table, save_location, self.lut_data.domain, self.lut_data.size,
                               comments=comments)
        # Write 3D LUT as .cube file
        colour.write_LUT(out_lut, save_location)

        print(f"Profile '{save_location}' saved.")

