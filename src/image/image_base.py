from abc import ABC, abstractmethod

class ImageBase(ABC):
    """Abstract base class for image containers."""

    def __init__(self, image, metadata):
        self.image = image
        self.metadata = metadata

    def get_image(self):
        """Return the underlying image pixel data."""
        return self.image

    def get_metadata(self):
        """Return the metadata object attached to the image."""
        return self.metadata

    @classmethod
    def from_image_data(cls, image_data, metadata) -> "ImageBase":
        """Create an image container from pixel data and metadata."""
        return cls(image_data, metadata)

    @classmethod
    @abstractmethod
    def from_image_location(cls, image_location: str) -> "ImageBase":
        """Read image pixels and metadata from a file on disk."""
        pass
