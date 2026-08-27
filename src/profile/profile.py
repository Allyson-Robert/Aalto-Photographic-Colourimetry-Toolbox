import os
import ast
import colour
from src.image.photograph import ExifMetaData
from src.profile.utils.parse_cube_comments import parse_cube_comments

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
        # Read 3D LUT
        lut = colour.read_LUT(profile_location)
        comments = lut.comments

        """ Obtain calibration gray values, colour space, bit depth, exit metadata, statistics and sample data from .cube comments. """
        # Read profile reference gray LAB
        gray = ast.literal_eval(comments[1].split(';')[1])

        # Third line contains colour space, bit depth and EXIF metadata
        colour_space, bit_depth = ast.literal_eval(comments[2])[:2]
        metadata_dict = {}
        for md in ast.literal_eval(comments[2]):
            metadata_dict[md.split(';')[0]] = md.split(';')[1]
        exif_metadata = ExifMetaData.from_data(colour_space, bit_depth, metadata_dict)

        # Fourth line contains some sample statistics of the calibration
        statistics = {}
        for field in ast.literal_eval(comments[3]):
            statistics[field.split(';')[0]] = float(field.split(';')[1])

        # Fifth line contains the colour coordinates of the sample data
        sample_data = {}
        for entry in ast.literal_eval(comments[4]):
            parts = entry.split(';')
            grid_point = ast.literal_eval(parts[0])
            lx, ly = grid_point
            if lx not in sample_data.keys():
                sample_data[lx] = {}
            if ly not in sample_data[lx].keys():
                sample_data[lx][ly] = {}
            sample_data[lx][ly] = {
                parts[i]: float(parts[i + 1]) for i in range(1, len(parts), 2)
            }

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
        comments = ['(x, y, z): (L*, a*, b*)', f'gray;{str(self.gray)}',
                    [f'ColorSpace;{self.exif_metadata.color_space}', f'BitDepth;{self.exif_metadata.bit_depth}'], [], []]

        # Include image metadata
        for key in self.exif_metadata.get_exif_data().keys():
            comments[2].append(key + ';' + str(self.exif_metadata.get_exif_data()[key]))
        comments[2] = str(tuple(comments[2]))

        # Include calibration accuracy information
        ref_data_types = ('avg_ciede2000', 'min_ciede2000', 'max_ciede', 'avg_dL', 'avg_da', 'avg_db')
        for i in range(6):
            comments[3].append(ref_data_types[i] + ';' + str(self.statistics[ref_data_types[i]]))
        comments[3] = str(tuple(comments[3]))

        # Include color sample information
        sample_data_types = ['ciede2000', 'dL', 'da', 'db']
        for l_y in range(len(self.sample_data)):
            for l_x in range(len(self.sample_data[0])):
                sample_text = f'({l_x + 1}, {l_y + 1})'
                for i in range(4):
                    sample_text += ';' + sample_data_types[i] + ';' + str(self.sample_data[i, l_x, l_y])
                comments[4].append(sample_text)
        comments[4] = str(tuple(comments[4]))

        # Create final 3D LUT
        out_lut = colour.LUT3D(self.lut_data.table, save_location, self.lut_data.domain, self.lut_data.size,
                               comments)
        print(out_lut)

        # Write 3D LUT as .cube file
        colour.write_LUT(out_lut, save_location)

        print(f"Profile '{save_location}' saved.")

