from pymavlink import mavutil
from modules.utils import calc_drop_loc, get_bearing_2_points, new_waypoint
from modules.Uav import Uav


def mission1(
    wp_list: list[list[float]],
    payload_pos: list[float],
    fence_list: list[list[float]],
    survey_grid: list[list[float]],
    obs_list: list[list[float]],
    uav: Uav,
) -> bool:
    
    x = calc_drop_loc(
        uav.config_data["aircraftAltitude"],
        uav.config_data["aircraftVelocity"],
        uav.config_data["windSpeed"],
        uav.config_data["windBearing"],
    )
    # todo calculate the approaching payload equation and add it to the wp_list

    # todo survey grid
    uav.add_mission_waypoints(wp_list)
    # todo payload drop equation

    uav.add_servo_dropping_wps()

    print('done with mission')
    return True