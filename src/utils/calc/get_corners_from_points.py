from utils.object_types import Point

def get_corners_from_points(point_a: Point, point_b: Point) -> tuple[Point, Point]:
    """Given two non-collinear points, return (top_left, bottom_right) of the rectangle they define."""
    top_left = (min(point_a[0], point_b[0]), min(point_a[1], point_b[1]))
    bottom_right = (max(point_a[0], point_b[0]), max(point_a[1], point_b[1]))
    return top_left, bottom_right