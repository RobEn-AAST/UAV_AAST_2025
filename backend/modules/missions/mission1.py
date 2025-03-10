from pymavlink import mavutil
from modules.utils import calc_drop_loc, get_bearing, new_waypoint
from modules.Uav import Uav


def mission1(wp_list: list[list[float]], payload_pos: list[float], uav: Uav) -> bool:
    uav.add_mission_waypoints(wp_list)

    x = calc_drop_loc(
        uav.config_data["aircraftAltitude"],
        uav.config_data["aircraftVelocity"],
        uav.config_data["windSpeed"],
        uav.config_data["windBearing"],
    )
    # todo calculate the approaching payload equation and add it to the wp_list
    uav.add_mission_waypoints(wp_list)

    uav.add_servo_dropping_wps()

    uav.add_mission_waypoints(wp_list)

    uav.add_drop_location_wps()
