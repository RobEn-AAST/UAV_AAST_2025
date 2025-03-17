from .geo_utils import latlon_to_xy, xy_to_latlon
from .dubins import Waypoint


def format_for_dubins(wp: list):
    """
    wp should be in format (lat, long)
    """

    x, y, zone = latlon_to_xy(wp[0], wp[1])

    return Waypoint(x, y, wp[2]), zone


def format_path_to_latlon(path_xy: list[Waypoint], zone, step_size=1):
    path = []

    for i, point in enumerate(path_xy):
        if i % step_size == 0:
            path.append(xy_to_latlon(point[0], point[1], zone))

    return path
