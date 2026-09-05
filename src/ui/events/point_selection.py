"""Point selection state machine for OpenCV mouse callbacks.

This module implements interactive two-point selection (e.g. for defining
a horizontal reference line, an arrow annotation, or a crop rectangle) via
an OpenCV mouse callback. Every class here exists purely to give the user
visual feedback while selecting points in a window -- none of it makes
sense with no window open, so it lives in ``ui``, not ``image``.

WHY?/TODO-ADR: the "closer point" replacement logic in
`PointSelectionState.offer_point`/`resolve_release`, and the LINE-mode
point-reversal step in `PointSelectionCallback._on_button_up`, are ported
directly from the legacy `image_event` implementation (module-level
globals, `(-1, -1)` sentinel tuples, `np.sum(...) == -2` unset-checks).
They have not yet been covered by characterization tests against the
original behavior. Do not trust this extraction over the legacy original
until such tests exist. See docs/adr/ for tracking.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable, Optional, Protocol

from src.image.photograph import Photograph
from src.defaults import selection_zoom

Point = tuple[int, int]
OptionalPoint = Optional[Point]

MOUSEWHEEL_UP_FLAG = 7864320
MOUSEWHEEL_DOWN_FLAG = -7864320


class PointSelectionMode(Enum):
    """The kind of selection currently being made in a window."""

    HORIZONTAL = auto() # Selecting two points to define a horizontal reference line.
    LINE = auto() # Selecting two points to define an arrow annotation.
    CROP = auto() # Selecting two points to define a crop rectangle.
    ZOOM = auto() # No point selection in progress; clicking pans/zooms the view.

    @property
    def is_two_point_mode(self) -> bool:
        """Whether this mode collects two selection points."""
        return self in (
            PointSelectionMode.HORIZONTAL,
            PointSelectionMode.LINE,
            PointSelectionMode.CROP,
        )

    @property
    def draws_point_markers(self) -> bool:
        """Whether individual selected points get a cross marker.

        LINE mode is the one exception: the arrow itself communicates both
        endpoints, so no separate cross markers are drawn on top of it.
        """
        return self.is_two_point_mode and self is not PointSelectionMode.LINE

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
    """Mutable selection state for a single point-selection session.

    Replaces the legacy module-level globals (`selected_points`,
    `zoom_point`, `arrow_width`). One instance belongs to exactly one
    `PointSelectionCallback` / window.

    Attributes:
        next: The first selected point, or None if unset.
        previous: The second selected point, or None if unset.
        zoom_point: The point currently being zoomed around, or None.
        arrow_width: Current arrow annotation width, adjustable via mouse
            wheel in LINE mode.
    """

    next: OptionalPoint = None
    previous: OptionalPoint = None
    zoom_point: OptionalPoint = None
    arrow_width: int = 3

    MIN_ARROW_WIDTH = 3
    ARROW_WIDTH_STEP = 2

    def is_complete(self) -> bool:
        """Whether both selection points have been set."""
        return self.next is not None and self.previous is not None

    def clear(self) -> None:
        """Reset both selection points (used on right-click cancel)."""
        self.next = None
        self.previous = None

    def offer_point(self, point: Point) -> None:
        """Insert `point` into the selection, replacing whichever existing
        point is closer to it if both are already assigned.

        Args:
            point: The newly clicked point.
        """
        # Shift unless both are already set, in which case we replace the closer one
        if self.previous is None:
            self.next, self.previous = point, self.next
        elif self._distance(point, self.previous) < self._distance(point, self.next):
            self.next = None
        else:
            self.previous = None

    def resolve_release(self, point: OptionalPoint) -> None:
        """Resolve selection state on mouse button release.

        Args:
            point: The finalized point for this release (already adjusted
                for any active zoom), or None to cancel/clear the pending
                slot without setting a new point.
        """
        # If next is empty, reset shift to enable shifting
        if self.next is None:
            self.next, self.previous = self.previous, self.next

        replace_first = (point is not None and self.previous is None) or (
                self.previous is not None and self._closer_to_previous(point)
        )
        if replace_first:
            self.next, self.previous = point, self.next
        else:
            self.next = point

    def reverse(self) -> None:
        """Swap first/second. Used for LINE mode, where selection order
        controls arrow direction (tail -> head).
        """
        self.next, self.previous = self.previous, self.next

    def _closer_to_previous(self, point: OptionalPoint) -> bool:
        if point is None or self.previous is None or self.next is None:
            return False
        return self._distance(point, self.previous) < self._distance(point, self.next)

    def grow_arrow(self) -> None:
        """Increase arrow width (mouse wheel up in LINE mode)."""
        self.arrow_width += self.ARROW_WIDTH_STEP

    def shrink_arrow(self) -> None:
        """Decrease arrow width, floored at MIN_ARROW_WIDTH."""
        self.arrow_width = max(self.MIN_ARROW_WIDTH, self.arrow_width - self.ARROW_WIDTH_STEP)

    @staticmethod
    def _distance(a: Point, b: Point) -> float:
        return math.dist(a, b)


# Callable signatures for injected drawing/display behavior. Drawing is
# injected via the constructor (rather than imported directly from
# `ui.drawing`) so the state machine can be unit-tested with zero OpenCV
# window or image fixtures involved.
#
# `draw_marker` is deliberately factored out from shape drawing (arrow /
# line / rect) so the same marker renderer can be reused both for the
# tilted-cross point markers and for the zoom crosshair, instead of the
# legacy code's two independent `cv.drawMarker` call sites.
DrawShape = Callable[[object, PointSelectionState, PointSelectionCallbackContext], object]
DrawMarker = Callable[[object, Point], object]
ShowImage = Callable[[str, object, bool], None]
ZoomImage = Callable[[object, Point], object]


@dataclass
class PointSelectionCallback:
    """OpenCV mouse callback implementing two-point selection with live
    visual feedback.

    One instance should be constructed per window and passed directly to
    ``cv2.setMouseCallback``. All drawing/display behavior is injected as
    callables so this class carries no `ui.drawing` import of its own,
    keeping the state machine independently testable.

    Attributes:
        state: The selection state this callback mutates.
        draw_shape: Mode-keyed callables invoked on button release to
            render the finalized shape (line / arrow / rect). Markers are
            drawn separately via `draw_marker`.
        draw_shape_preview: Mode-keyed callables invoked on mouse move to
            render a live shape preview while the second point is unset.
        draw_marker: Callable drawing a single point marker. Reused both
            for selected-point crosses and the zoom-preview crosshair.
        zoom_image: Callable producing a zoomed view around a point.
        show_image: Callable that pushes a rendered frame to the window.
        zoom_factor: Zoom multiplier used to convert on-screen clicks back
            to image coordinates while a zoomed preview is active. Defaults
            to `src.defaults.SELECTION_ZOOM`; override for tests.
    """

    state: PointSelectionState
    draw_shape: dict[PointSelectionMode, DrawShape]
    draw_shape_preview: dict[PointSelectionMode, DrawShape]
    draw_marker: DrawMarker
    zoom_image: ZoomImage
    show_image: ShowImage
    zoom_factor: float = SELECTION_ZOOM

    def __call__(self, event: int, x: int, y: int, flags: int,
                 context: PointSelectionCallbackContext) -> None:
        """Dispatch an OpenCV mouse event to the appropriate handler."""
        import cv2 as cv  # local import: keeps cv2 optional for pure-state tests

        if event == cv.EVENT_LBUTTONDOWN:
            self._on_left_down(x, y, context)
        elif event in (cv.EVENT_LBUTTONUP, cv.EVENT_RBUTTONUP):
            self._on_button_up(event, x, y, context)
        elif event == cv.EVENT_MOUSEMOVE:
            self._on_move(x, y, context)
        elif event == cv.EVENT_MOUSEWHEEL:
            self._on_wheel(flags, context)

    def _on_left_down(self, x: int, y: int, context: PointSelectionCallbackContext) -> None:
        if context.mode.is_two_point_mode:
            self.state.offer_point((x, y))
        else:
            self.state.zoom_point = (x, y)
            self._on_move(x, y, context)

    def _on_button_up(self, event: int, x: int, y: int,
                       context: PointSelectionCallbackContext) -> None:
        import cv2 as cv

        if self.state.zoom_point is not None:
            point: OptionalPoint = self._unzoom((x, y), self.state.zoom_point)
        else:
            point = (x, y)

        if event == cv.EVENT_RBUTTONUP:
            point = None
            if context.mode.is_two_point_mode:
                self.state.clear()

        self.state.resolve_release(point)

        if context.mode is PointSelectionMode.LINE:
            # Legacy `image_event` reverses selection order specifically
            # for LINE mode, since order controls arrow direction.
            self.state.reverse()

        if context.mode.is_two_point_mode:
            rendered = context.image
            if context.mode.draws_point_markers:
                for selected in (self.state.next, self.state.previous):
                    if selected is not None:
                        rendered = self.draw_marker(rendered, selected)
            if self.state.is_complete():
                shape = self.draw_shape.get(context.mode)
                if shape is not None:
                    rendered = shape(rendered, self.state, context)
            self.show_image(context.window_name, rendered, False)

        self.state.zoom_point = None

    def _on_move(self, x: int, y: int, context: PointSelectionCallbackContext) -> None:
        if context.mode.is_two_point_mode:
            if self.state.next is not None and self.state.previous is None:
                rendered = context.image
                preview = self.draw_shape_preview.get(context.mode)
                if preview is not None:
                    rendered = preview(rendered, self.state, context)
                if context.mode.draws_point_markers:
                    rendered = self.draw_marker(rendered, self.state.next)
                self.show_image(context.window_name, rendered, False)
        elif self.state.zoom_point is not None:
            zoom_coord = self._unzoom((x, y), self.state.zoom_point)
            rendered = self.zoom_image(context.image, zoom_coord)
            rendered = self.draw_marker(rendered, zoom_coord)
            self.show_image(context.window_name, rendered, False)

    def _on_wheel(self, flags: int, context: PointSelectionCallbackContext) -> None:
        if context.mode != PointSelectionMode.LINE or not self.state.is_complete():
            return

        if flags == MOUSEWHEEL_UP_FLAG:
            self.state.grow_arrow()
        elif flags == MOUSEWHEEL_DOWN_FLAG:
            self.state.shrink_arrow()
        else:
            return

        shape = self.draw_shape.get(context.mode)
        if shape is not None:
            rendered = shape(context.image, self.state, context)
            self.show_image(context.window_name, rendered, False)

    def _unzoom(self, screen_point: Point, zoom_point: Point) -> Point:
        """Convert an on-screen click into image coordinates while a
        zoomed preview is active.

        Mirrors the legacy `image_event` math:
        ``zoom_point + (screen_point - zoom_point) / zoom_factor``,
        rounded to the nearest integer pixel.
        """
        dx = (screen_point[0] - zoom_point[0]) / self.zoom_factor
        dy = (screen_point[1] - zoom_point[1]) / self.zoom_factor
        return (round(zoom_point[0] + dx), round(zoom_point[1] + dy))