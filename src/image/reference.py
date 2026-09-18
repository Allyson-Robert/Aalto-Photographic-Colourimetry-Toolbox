from src.image.image_base import ImageBase
from ast import literal_eval as make_tuple
import xml.etree.ElementTree as ET
import numpy as np


class ReferenceChart(ImageBase):
    # TODO: Worth considering if this needs to sit here or if it should be in a separate module, since there are fundamental incompatibilities with Photograph
    """ Container for reference chart pixel data and associated metadata.

        Reference chart pixels are stored in XML files, which contain the color target format, illuminant, grid information and sample Lab values.
        This class reads data from the XML file and constructs a ReferenceChart object with the pixel data and metadata.

        Attributes:
            image (np.ndarray): The pixel data of the reference chart.
            metadata (ReferenceChartMetaData): The metadata associated with the reference chart, including illuminant and grid information.
    """
    @classmethod
    def from_image_location(cls, image_location: str) -> "ImageBase":
        # Try reading the XML file for the reference chart
        root = ET.parse(image_location).getroot()
        print(f"Read reference '{image_location}' values.")

        # Read color target format
        illuminant = root.find('illuminant').text
        grid = root.find('grid')
        offset = (make_tuple(grid.find(f"offset[@type='top-left']").text),
                  make_tuple(grid.find(f"offset[@type='spacing']").text),
                  make_tuple(grid.find(f"offset[@type='sample']").text))
        grid_indices = make_tuple(grid.text.strip())

        # Read color target sample Lab values for each square, order is column-major (x, y) with (1, 1) being the top-left square
        image = np.zeros((grid_indices[0], grid_indices[1], 3))
        for l_y in range(grid_indices[1]):
            for l_x in range(grid_indices[0]):
                for i, coord in enumerate(('L', 'a', 'b')):
                    current_value = root.find('samples').find(f"sample[@grid='({l_x + 1}, {l_y + 1})']").find(f"data[@type='{coord}']")
                    image[l_x, l_y, i] = float(current_value.text)

        # TODO: Let the caller deal with the illuminant conversion
        # Convert ref. data to LAB D50
        # if illuminant != 'D50':
        #     image = convert_illuminant(image, illuminant, 'D50')

        # Construct the metadata
        metadata = ReferenceChartMetaData(illuminant, offset, grid_indices)

        return cls(image, metadata)

class ReferenceChartMetaData:
    """ Metadata for a reference chart, including illuminant and grid information.

        Attributes:
            illuminant (str): The illuminant of the reference chart.
            offset (tuple): The offset values for the reference chart grid.
            grid_indices (tuple): The grid indices of the reference chart.
    """

    def __init__(self, illuminant: str, offset: tuple, grid_indices: tuple):
        self.illuminant = illuminant
        self.offset = offset
        self.grid_indices = grid_indices

    def get_illuminant(self):
        """Return the illuminant of the reference chart."""
        return self.illuminant

    def get_offset(self):
        """Return the offset values for the reference chart grid."""
        return self.offset

    def get_grid_indices(self):
        """Return the grid indices of the reference chart."""
        return self.grid_indices
