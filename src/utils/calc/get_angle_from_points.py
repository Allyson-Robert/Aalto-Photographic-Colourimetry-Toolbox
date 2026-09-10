import math

def get_angle_from_points(point_a, point_b, return_radians=False, range=[-180, 180]):
    """Get angle between 2 points"""
    # Get angle in range [-180, 180]
    angle = math.degrees(math.atan2((point_b[1] - point_a[1]), point_b[0] - point_a[0]))

    # Add or remove 360 degrees to get the angle in the specified range
    while angle < range[0]:
        angle += 360
    while angle > range[1]:
        angle -= 360

    if return_radians:
        return math.radians(angle)  # Convert angle to radians
    else:
        return angle
