from .dubins import calcDubinsPath, dubins_traj
from .utils import format_for_dubins, format_path_to_latlon
from ..config import UavConfig


def get_optimum_path(wp1_lat_lon_brng, wp2_lat_lon_brng, wps_step_size=40):
    bank_angle = UavConfig.bank_angle
    velocity = UavConfig.aircraft_velocity
    wp1, zone = format_for_dubins(wp1_lat_lon_brng)
    wp2, _ = format_for_dubins(wp2_lat_lon_brng)

    param = calcDubinsPath(wp1, wp2, velocity, bank_angle)
    path_xy = dubins_traj(param, 1)
    path = format_path_to_latlon(path_xy, zone, wps_step_size)

    return path


if __name__ == "__main__":
    wp1_latlon = [-35.3625567, 149.1651696, 0]  # format: lat long, brng
    wp2_latlon = [-35.3619136, 149.1673797, 90]

    path = get_optimum_path(wp1_latlon, wp2_latlon)

    print(f"path len: {len(path)}")
