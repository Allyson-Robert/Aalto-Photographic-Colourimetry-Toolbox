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
from typing import Optional

from src.image.photograph import Photograph
from src.defaults import selection_zoom
from src.ui import draw
from src.ui.show_image import show_image
from src.image_ops.zoom_image import zoom_image

from src.utils.object_types import Point, OptionalPoint

MOUSEWHEEL_UP_FLAG = 7864320
MOUSEWHEEL_DOWN_FLAG = -7864320


class PointSelectionMode(Enum):
    """ Class/Enum holding all the information related to the point selection mode. The class is aware of the available
    modes, the corresponding window titles, and the drawing functions for each mode. The class also provides information
    about whether the mode requires point markers to be drawn and whether zooming is enabled for the mode. Drawing
    functions can be called in definitive or in preview mode, in which case the current mouse position is used
    as the second point.

    """

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
        """Draw the shape for this mode. Use state points unless preview is True, in which case use the current mouse position as the second point."""
        if preview:
            second_point = state.preview_point
        else:
            second_point = state.previous

        if self == PointSelectionMode.HORIZONTAL:
            return draw.draw_line(image, state.current, second_point, preview)
        elif self == PointSelectionMode.LINE:
            return draw.draw_arrow(image, state.current, second_point, state.arrow.arrow_width, preview)
        elif self == PointSelectionMode.CROP:
            return draw.draw_rectangle(image, state.current, second_point, preview)
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
    """

    mode: PointSelectionMode
    image: Photograph


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
    preview_point: OptionalPoint = None

    def is_complete(self) -> bool:
        """Whether both selection points have been set."""
        return self.current is not None and self.previous is not None

    def clear(self) -> None:
        """Reset both selection points (used on right-click cancel)."""
        self.current = None
        self.previous = None
        self.preview_point = None

    def sort(self):
        """ Sorts the two selected points from left to right, assuming the top left is (0, 0) """
        if self.is_complete():
            if self.current[0] > self.previous[0]:
                self.current, self.previous = self.previous, self.current

    def offer_point(self, point: Point) -> None:
        """Insert `point` into the selection, replacing whichever existing
        point is closer to it if both are already assigned.

        Args:
            point: The newly clicked point.
        """
        if self.current is None and self.previous is not None:
            raise RuntimeError("Invalid PointSelectionState reached: previous is set but current is None. ")

        # If the point is already one of the selected points, do nothing
        if point in (self.current, self.previous):
            return None

        # If previous has room or is closer shift the registered points otherwise replace current point
        if self.previous is None or self._closer_to_previous(point):
            self.current, self.previous = point, self.current
        else:
            self.current = point
        return None

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
        """ Zoom to mouse position if not in two-pt selection mode and offer point to state """
        if context.mode.zoom_enabled:
            self.state.set_zoom_point((x, y))
            self._on_move(x, y, context)
        else:
            self.state.offer_point((x, y))

    def _on_left_up(self, x: int, y: int, context: PointSelectionCallbackContext) -> None:
        rendered = context.image

        # Offer (zoom) point and either release zoom or render shapes
        if context.mode.zoom_enabled:
            self.state.offer_point(self._scale_zoomed_coordinates((x, y)))
            self.state.clear_zoom_point()
        else:
            self.state.offer_point((x, y))
            if self.state.is_complete():
                rendered = context.mode.draw_shape(rendered, self.state, context, preview=False)

        # Add markers if the mode calls for them
        if context.mode.draws_point_markers:
            for selected in (self.state.current, self.state.previous):
                if selected is not None:
                    rendered = draw.draw_marker(rendered, selected)

        # Show the (un)modified image
        show_image(rendered, context.mode.window_title)

    def _on_right_up(self, x: int, y: int, context: PointSelectionCallbackContext) -> None:
        # Clear selection state on right-click release.
        self.state.clear()
        show_image(context.image, context.mode.window_title)

    def _on_move(self, x: int, y: int, context: PointSelectionCallbackContext) -> None:
        rendered = context.image

        # Check that the zoompoint was set before doing anything
        if context.mode.zoom_enabled and self.state.zoom_point is not None:
            zoom_coord = self._scale_zoomed_coordinates((x, y))
            rendered = zoom_image(rendered, zoom_coord, self.zoom_factor)
            rendered = draw.draw_marker(rendered, zoom_coord)

        # Draw preview shapes until selection is complete
        elif self.state.current is not None and self.state.previous is None:
            self.state.preview_point = (x, y)
            rendered = context.mode.draw_shape(rendered, self.state, context, preview=True)
            if context.mode.draws_point_markers:
                rendered = draw.draw_marker(rendered, self.state.current)
        # Skip
        else:
            return None

        # Show updated image with preview shapes
        show_image(rendered, context.mode.window_title)

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
        show_image(rendered, context.mode.window_title)

    def _scale_zoomed_coordinates(self, point: Point) -> Point:
        """Convert an on-screen click into image coordinates while a
        zoomed preview is active.
        """
        zoom_point = self.state.zoom_point
        dx = (point[0] - zoom_point[0]) / self.zoom_factor
        dy = (point[1] - zoom_point[1]) / self.zoom_factor
        return round(zoom_point[0] + dx), round(zoom_point[1] + dy)
