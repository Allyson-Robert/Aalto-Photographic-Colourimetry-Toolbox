"""Image container and metadata helpers for image IO and color handling."""

import cv2 as cv
import src.defaults as defaults
from src.image_transformations.utils.read_metadata_from_image import read_metadata_from_image
from src.image_transformations.utils.parse_bitdepth_from_exif_metadata import parse_bitdepth_from_exif_metadata
from src.image.image_base import ImageBase

class Photograph(ImageBase):
    """Container for image pixel data and associated metadata."""

    @classmethod
    def from_image_location(cls, image_location: str) -> "Photograph":
        """Read image pixels and metadata from a file on disk."""
        image = cv.imread(image_location, cv.IMREAD_UNCHANGED)
        if image is None:
            raise ValueError(f"Image not found at {image_location}")
        metadata = ExifMetaData.from_image_location(image_location)
        return cls(image, metadata)

    def write(self, output_location: str) -> None:
        """Write the stored image to disk using OpenCV."""
        cv.imwrite(output_location, self.image)

    def get_color_space(self) -> str:
        """Return the image color space from the attached metadata."""
        return self.metadata.get_color_space()

    def get_colour_model(self):
        """Return the colour-science model matching the image color space."""
        return defaults.colour_models[self.get_color_space()]

    def get_bit_depth(self) -> int:
        """Return the bit depth stored in the image metadata."""
        return self.metadata.get_bit_depth()

class ExifMetaData:
    """Metadata container for image color and EXIF values."""

    # Define a subset of metadata keys that are relevant for the project
    METADATA_SUBSET = [
        'ICC_Profile:ProfileDescription',
        'EXIF:BitsPerSample',
        'File:BitsPerSample',
        'EXIF:Make',
        'EXIF:Model',
        'EXIF:FNumber',
        'EXIF:ExposureTime',
        'EXIF:ISO',
        'EXIF:FocalLength'
    ]

    def __init__(self, color_space: str, bit_depth: int, exif_data: dict):
        """Initialize metadata from provided values."""
        self.color_space = color_space
        self.bit_depth = bit_depth
        self.exif_data = exif_data

    @classmethod
    def from_image_location(cls, image_location: str) -> "ExifMetaData":
        """Initialize metadata from an image file path.

        Args:
            image_location: Path to the image file to read metadata from.
        """
        exif_data = {}
        if isinstance(image_location, str):
            exif = read_metadata_from_image(image_location)
            for key in cls.METADATA_SUBSET:
                if key in exif:
                    exif_data[key] = exif[key]
        else:
            raise ValueError("Metadata must be a file path")

        # Colour space found in Profile Description as str 'PROFILE STANDARD'
        colourspace = exif_data.get('ICC_Profile:ProfileDescription').split(' ')[0]
        color_space = next(filter(lambda x: x.upper() == colourspace.upper(), defaults.color_spaces))

        # Bit depth can come from either EXIF or File metadata, so we check both
        bit_depth = exif_data.get('EXIF:BitsPerSample') or exif_data.get('File:BitsPerSample')
        bit_depth = parse_bitdepth_from_exif_metadata(bit_depth)

        return cls(color_space, bit_depth, exif_data)

    @classmethod
    def from_data(cls, color_space: str, bit_depth: int, exif_data: dict) -> "ExifMetaData":
        return cls(color_space, bit_depth, exif_data)

    # TODO: implement
    def set_color_space(self, color_space: str):
        """Set the color space for the metadata object."""
        raise NotImplementedError

    def set_bit_depth(self, bit_depth: int):
        """Set the bit depth for the metadata object."""
        raise NotImplementedError

    def get_color_space(self):
        """Return the color space stored in the metadata."""
        return self.color_space

    def get_bit_depth(self):
        """Return the bit depth stored in the metadata."""
        return self.bit_depth

    def get_exif_data(self):
        """Return the full EXIF data dictionary."""
        return self.exif_data

    def __eq__(self, other: object) -> bool:
        """Compare metadata objects using the project metadata subset."""
        if not isinstance(other, ExifMetaData):
            return NotImplemented
        return all(
            self.exif_data.get(key) == other.exif_data.get(key)
            for key in self.METADATA_SUBSET
        )