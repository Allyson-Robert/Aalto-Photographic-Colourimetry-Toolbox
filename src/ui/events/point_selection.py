"""Point selection state machine for OpenCV mouse callbacks.

This module implements interactive two-point selection (e.g. for defining
a horizontal reference line, an arrow annotation, or a crop rectangle) via
an OpenCV mouse callback. Every class here exists purely to give the user
visual feedback while selecting points in a window -- none of it makes
sense with no window open, so it lives in ``ui``, not ``image``.

"""

import math
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable, Optional

from src.image.photograph import Photograph
from src.defaults import selection_zoom
from src.ui import draw
from src.ui.show_image import show_image
from image_ops.zoom_image import zoom_image

Point = tuple[int, int]
OptionalPoint = Optional[Point]

MOUSEWHEEL_UP_FLAG = 7864320
MOUSEWHEEL_DOWN_FLAG = -7864320


class PointSelectionMode(Enum):
    """The kind of selection currently being made in a window."""

    HORIZONTAL = auto() # Selecting two points to define a horizontal reference line.
    LINE = auto() # Selecting two points to define an arrow annotation.
    CROP = auto() # Selecting two points to define a crop rectangle.
    REF = auto()
    REF_TIMELINE = auto()

    @property
    def window_title(self) -> str:
        """The title of the OpenCV window for this mode."""
        return {
            PointSelectionMode.HORIZONTAL: "Drag horizontal line, then press ENTER.",
            PointSelectionMode.LINE: "Drag line to measure, then press ENTER. "
                   "You can adjust the width of the measured line using the mouse wheel.",
            PointSelectionMode.CROP: "Select crop, then press ENTER.",
            PointSelectionMode.REF: "Select reference points, then press ENTER.",
            PointSelectionMode.REF_TIMELINE: "Select reference points, then press ENTER. "
                            "To use the same ref. points for rest of images, press A prior to ENTER.",
        }[self]

    # These modes require additional markers to be drawn
    @property
    def draws_point_markers(self) -> bool:
        """ Does the mode call for markers to be drawn """
        return self in (PointSelectionMode.HORIZONTAL, PointSelectionMode.CROP)

    # These modes will all the user to zoom in on the image
    @property
    def zoom_enabled(self) -> bool:
        """ Is zooming enabled for this mode """
        return self not in (PointSelectionMode.HORIZONTAL, PointSelectionMode.LINE, PointSelectionMode.CROP)

    def draw_shape(self, image: Photograph, state: 'PointSelectionState', context: 'PointSelectionCallbackContext', preview: bool = False) -> Photograph:
        """Draw the shape for this mode."""
        if self == PointSelectionMode.HORIZONTAL:
            return draw.draw_line(image, state.current, state.previous, preview)
        elif self == PointSelectionMode.LINE:
            return draw.draw_arrow(image, state.current, state.previous, state.arrow.arrow_width, preview)
        elif self == PointSelectionMode.CROP:
            return draw.draw_rectangle(image, state.current, state.previous, preview)
        else:
            raise ValueError(f"Mode {self} does not support drawing a shape.")

@dataclass
class ArrowWidth:
    """ Arrow width can be changed so must persist. This class deals with those. """
    MIN_ARROW_WIDTH = 3
    ARROW_WIDTH_STEP = 2

    arrow_width: int = 3

    def grow_arrow(self) -> None:
        """Increase arrow width (mouse wheel up in LINE mode)."""
        self.arrow_width += self.ARROW_WIDTH_STEP

    def shrink_arrow(self) -> None:
        """Decrease arrow width, floored at MIN_ARROW_WIDTH."""
        self.arrow_width = max(self.MIN_ARROW_WIDTH, self.arrow_width - self.ARROW_WIDTH_STEP)

@dataclass
class PointSelectionCallbackContext:
    """Per-window configuration passed to `PointSelectionCallback` as the
    OpenCV mouse callback ``param``.

    Attributes:
        mode: The selection mode active for this window.
        image: The base image
        window_name: Name of the OpenCV window this context belongs to.
    """

    mode: PointSelectionMode
    image: Photograph
    window_name: str


@dataclass
class PointSelectionState:
    """ Mutable selection state for a single point-selection session.

    Attributes:
        current: The first selected point, or None if unset.
        previous: The second selected point, or None if unset.
    """

    arrow: ArrowWidth = field(default_factory=ArrowWidth)
    current: OptionalPoint = None
    previous: OptionalPoint = None
    zoom_point: OptionalPoint = None

    def is_complete(self) -> bool:
        """Whether both selection points have been set."""
        return self.current is not None and self.previous is not None

    def clear(self) -> None:
        """Reset both selection points (used on right-click cancel)."""
        self.current = None
        self.previous = None

    def offer_point(self, point: Point) -> None:
        """Insert `point` into the selection, replacing whichever existing
        point is closer to it if both are already assigned.

        Args:
            point: The newly clicked point.
        """
        if self.current is None and self.previous is not None:
            raise RuntimeError("Invalid PointSelectionState reached: previous is set but current is None. ")

        # If previous has room or is closer shift the registered points otherwise replace current point
        if self.previous is None or self._closer_to_previous(point):
            self.current, self.previous = point, self.current
        else:
            self.current = point

    def set_zoom_point(self, point: OptionalPoint) -> None:
        """Set the zoom point for this state."""
        self.zoom_point = point

    def clear_zoom_point(self) -> None:
        """Clear the zoom point for this state."""
        self.zoom_point = None

    def _closer_to_previous(self, point: OptionalPoint) -> bool:
        if point is None or self.previous is None or self.current is None:
            return False
        return math.dist(point, self.previous) < math.dist(point, self.current)


@dataclass
class PointSelectionCallback:
    """OpenCV mouse callback implementing two-point selection with live
    visual feedback.

    One instance should be constructed per window and passed directly to
    ``cv2.setMouseCallback``. All draw/display behavior is injected as
    callables so this class carries no `ui.draw` import of its own,
    keeping the state machine independently testable.

    Attributes:
        state: The selection state this callback mutates.
        zoom_factor: Zoom multiplier used to convert on-screen clicks back
            to image coordinates while a zoomed preview is active. Defaults
            to `src.defaults.selection_zoom`; override for tests.
    """

    state: PointSelectionState
    zoom_factor: float = selection_zoom

    def __call__(self, event: int, x: int, y: int, flags: int,
                 context: PointSelectionCallbackContext) -> None:
        """Dispatch an OpenCV mouse event to the appropriate handler."""
        import cv2 as cv  # local import: keeps cv2 optional for pure-state tests

        if event == cv.EVENT_LBUTTONDOWN:
            self._on_left_down(x, y, context)
        elif event == cv.EVENT_LBUTTONUP:
            self._on_left_up(x, y, context)
        elif event == cv.EVENT_RBUTTONUP:
            self._on_right_up(x, y, context)
        elif event == cv.EVENT_MOUSEMOVE:
            self._on_move(x, y, context)
        elif event == cv.EVENT_MOUSEWHEEL:
            self._on_wheel(flags, context)
        else:
            # Ignore other events (e.g. right button down, middle button, etc.)
            pass

    def _on_left_down(self, x: int, y: int, context: PointSelectionCallbackContext) -> None:
        """ Zoom to mouse position if not in two-pt selection mode """
        if context.mode.zoom_enabled:
            self.state.set_zoom_point((x, y))
            self._on_move(x, y, context)

    def _on_left_up(self, x: int, y: int, context: PointSelectionCallbackContext) -> None:
        if context.mode.zoom_enabled:
            # Offer zoom point to state
            self.state.offer_point(self._scale_zoomed_coordinates((x, y)))
            self.state.clear_zoom_point()
        else:
            # Offer coordinate to state and render shapes/markers
            self.state.offer_point((x, y))
            rendered = context.image
            if context.mode.draws_point_markers:
                for selected in (self.state.current, self.state.previous):
                    if selected is not None:
                        rendered = draw.draw_marker(rendered, selected)
            if self.state.is_complete():
                rendered = context.mode.draw_shape(rendered, self.state, context, preview=False)
            rendered_image = Photograph(rendered, context.image.get_metadata())
            show_image(rendered_image, context.window_name)

    def _on_right_up(self, x: int, y: int, context: PointSelectionCallbackContext) -> None:
        # Clear selection state on right-click release.
        self.state.clear()
        show_image(context.window_name, context.image, False)

    def _on_move(self, x: int, y: int, context: PointSelectionCallbackContext) -> None:
        # Check that the zoompoint was set before doing anything
        if context.mode.zoom_enabled and self.state.zoom_point is not None:
            zoom_coord = self._scale_zoomed_coordinates((x, y))
            # TODO: deal with ZOOMING
            rendered = zoom_image(context.image, zoom_coord)
            rendered = draw.draw_marker(rendered, zoom_coord)
            # TODO: deal with image showing method
            show_image(context.window_name, rendered, False)
        else:
            if self.state.current is not None and self.state.previous is None:
                rendered = context.mode.draw_shape(context.image, self.state, context, preview=True)
                if context.mode.draws_point_markers:
                    rendered = draw.draw_marker(rendered, self.state.current)

        rendered_image = Photograph(rendered, context.image.get_metadata())
        show_image(rendered_image, context.window_name)

    def _on_wheel(self, flags: int, context: PointSelectionCallbackContext) -> None:
        if context.mode != PointSelectionMode.LINE or not self.state.is_complete():
            return

        if flags == MOUSEWHEEL_UP_FLAG:
            self.state.arrow.grow_arrow()
        elif flags == MOUSEWHEEL_DOWN_FLAG:
            self.state.arrow.shrink_arrow()
        else:
            return

        rendered = draw.draw_arrow(context.image, start_point=self.state.previous, end_point=self.state.current,
                                   width=self.state.arrow.arrow_width)
        rendered_image = Photograph(rendered, context.image.get_metadata())
        show_image(rendered_image, context.window_name)

    def _scale_zoomed_coordinates(self, point: Point) -> Point:
        """Convert an on-screen click into image coordinates while a
        zoomed preview is active.
        """
        zoom_point = self.state.zoom_point
        dx = (point[0] - zoom_point[0]) / self.zoom_factor
        dy = (point[1] - zoom_point[1]) / self.zoom_factor
        return round(zoom_point[0] + dx), round(zoom_point[1] + dy)
