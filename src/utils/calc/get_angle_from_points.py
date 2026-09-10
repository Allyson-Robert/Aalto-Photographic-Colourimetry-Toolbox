import math

def get_angle_from_points(point_a, point_b, return_radians=False, range=[-180, 180]):
    """Get angle of the line connecting two points in degrees or radians, with the option to specify a range. Default
    range is [-180, 180] degrees. The angle is measured counterclockwise from the positive x-axis.

    Attributes:
        point_a: The first point (x1, y1)
        point_b: The second point (x2, y2)
        return_radians: If True, returns the angle in radians. If False, returns the angle in degrees.
        range: The range of the angle. Default is [-180, 180] degrees. Can be set to any range, e.g., [0, 360] or
    """
    # Get angle in range [-180, 180]
    angle = math.degrees(math.atan2((point_b[1] - point_a[1]), point_b[0] - point_a[0]))

    # Add or remove 360 degrees to get the angle in the specified range
    if abs(range[1] - range[0]) != 360:
        raise ValueError("Range must be 360 degrees to span all possible angles. Please specify a range of 360 degrees, e.g., "
                         "[0, 360] or [-180, 180].")
    while angle < range[0]:
        angle += 360
    while angle > range[1]:
        angle -= 360

    if return_radians:
        return math.radians(angle)  # Convert angle to radians
    else:
        return angle
