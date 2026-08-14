import os
import colour
from ast import literal_eval as make_tuple

from image.photograph import Photograph
from image.reference import ReferenceChart


class LUTProfile:
    def __init__(self, lut, gray, metadata):
        """Initialize LUTProfile from data."""
        self.lut_data = lut
        self.gray = gray
        self.metadata = metadata

    @classmethod
    def from_file_location(cls, profile_location) -> "LUTProfile":
        """Read calibration profile based on the name"""
        # Read 3D LUT
        lut = colour.read_LUT(profile_location)

        # Read profile reference gray LAB
        gray = make_tuple(lut.comments[1].split(';')[1])

        # Read profile metadata
        metadata = {}
        for md in make_tuple(lut.comments[2]):
            metadata[md.split(';')[0]] = md.split(';')[1]

        return cls(lut, gray, metadata)

    @classmethod
    def from_data(cls, lut, gray, metadata) -> "LUTProfile":
        """Initialize LUTProfile from data."""
        return cls(lut, gray, metadata)

    def get_lut(self):
        return self.lut_data

    def get_gray(self):
        return self.gray

    def get_metadata(self):
        return self.metadata

    def write_profile(self, write_location: str , reference_chart: ReferenceChart, sample_data: Photograph, calibration_gray):
        """Write correction profile 3D LUT"""
        if not os.path.exists(write_location):
            os.makedirs(write_location)

        # Gather image format data in comments
        comments = ['(x, y, z): (L*, a*, b*)', f'gray;{str(calibration_gray)}',
                    [f'ColorSpace;{in_metadata[0][0]}', f'BitDepth;{in_metadata[0][1]}'], [], []]

        # Gather image metadata in comments
        for key in in_metadata[1].keys():
            comments[2].append(key + ';' + str(in_metadata[1][key]))
        comments[2] = str(tuple(comments[2]))

        # Add calibration accuracy information in comments
        ref_data_types = ('avg_ciede2000', 'min_ciede2000', 'max_ciede', 'avg_dL', 'avg_da', 'avg_db')
        for i in range(6):
            comments[3].append(ref_data_types[i] + ';' + str(in_ref_data[i]))
        comments[3] = str(tuple(comments[3]))

        # Add color sample information in comments
        sample_data_types = ['ciede2000', 'dL', 'da', 'db']
        for l_y in range(ref_grid[1]):
            for l_x in range(ref_grid[0]):
                sample_text = f'({l_x + 1}, {l_y + 1})'
                for i in range(4):
                    sample_text += ';' + sample_data_types[i] + ';' + str(in_sample_data[i, l_x, l_y])
                comments[4].append(sample_text)
        comments[4] = str(tuple(comments[4]))

        # Create final 3D LUT
        out_lut = colour.LUT3D(in_lut.table, in_name, in_lut.domain, in_lut.size,
                               comments)
        print(out_lut)

        # Write 3D LUT as .cube file
        colour.write_LUT(out_lut, os.path.join(profile_path, in_name) + '.cube')

        print(f"Profile '{in_name}' saved.")


