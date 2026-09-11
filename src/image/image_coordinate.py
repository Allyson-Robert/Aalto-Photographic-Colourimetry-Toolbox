"""
ImageCoordinate represents a single point's location in the coordinate systems used throughout this codebase.

An ImageCoordinate always stores its position as image coordinates (see point_representation.py for the
definitions of the image, relative, and polar coordinate systems) -- this is the single source of truth.
The relative and polar representations are computed on demand from the stored image coordinates, never
cached, so no representation can go stale relative to another: there is exactly one stored value per point.

Relative and polar coordinates are both defined with the image center as their origin, so converting to or
from either representation requires the image shape (to locate that center). Image coordinates carry no
such dependency, which is part of why they were chosen as the stored representation.
"""

from dataclasses import dataclass

from src.utils.object_types import Point
from src.utils.calc.point_representation import (
    corner_to_relative,
    polar_to_relative,
    relative_to_corner,
    relative_to_polar,
)


@dataclass(frozen=True)
class ImageCoordinate:
    """A point's location, stored as image coordinates and convertible to relative or polar form on request.

    Image coordinates are the single point of truth: `x` and `y` follow OpenCV/NumPy convention (origin
    top-left, Y increasing downward). Relative and polar forms are computed fresh on each call to
    `get_relative_coord` / `get_polar_coord` rather than stored, so they can never drift out of sync with
    the image coordinates.

    Attributes:
        x: Horizontal image coordinate, origin at the left edge.
        y: Vertical image coordinate, origin at the top edge.
    """

    x: int
    y: int

    def get_image_coord(self) -> Point:
        """Return this point's image coordinates (top-left origin, Y-down)."""
        return self.x, self.y

    def get_relative_coord(self, img_shape: tuple[int, int, int]) -> tuple[int, int]:
        """Return this point's relative coordinates (image-center origin, Y-up).

        Args:
            img_shape: Shape of the image this point belongs to, used to locate the center.
        """
        return corner_to_relative((self.x, self.y), img_shape)

    def get_polar_coord(self, img_shape: tuple[int, int, int]) -> tuple[float, float]:
        """Return this point's polar coordinates as (radius, degrees), measured from the image center.

        Args:
            img_shape: Shape of the image this point belongs to, used to locate the center.
        """
        relative_x, relative_y = self.get_relative_coord(img_shape)
        return relative_to_polar(relative_x, relative_y)

    @classmethod
    def from_relative_coord(cls, x: float, y: float, img_shape: tuple[int, int, int]) -> ImageCoordinate:
        """Construct an ImageCoordinate from relative coordinates (image-center origin, Y-up).

        Args:
            x: Horizontal relative coordinate, origin at image center.
            y: Vertical relative coordinate, origin at image center, increasing upward.
            img_shape: Shape of the image this point belongs to, used to locate the center.
        """
        corner_x, corner_y = relative_to_corner(x, y, img_shape)
        return cls(corner_x, corner_y)

    @classmethod
    def from_polar_coord(cls, radius: float, degrees: float, img_shape: tuple[int, int, int]) -> ImageCoordinate:
        """Construct an ImageCoordinate from polar coordinates, measured from the image center.

        Args:
            radius: Distance from the image center.
            degrees: Angle counterclockwise from the positive x-axis.
            img_shape: Shape of the image this point belongs to, used to locate the center.
        """
        relative_x, relative_y = polar_to_relative(radius, degrees)
        return cls.from_relative_coord(relative_x, relative_y, img_shape)