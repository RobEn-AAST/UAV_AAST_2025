from pymavlink import mavutil
from modules.utils import calc_drop_loc, get_bearing_2_points, new_waypoint
from modules.uav import Uav
from modules.survey import generateSurveyFromList, Camera


def mission1(
    original_mission: list[list[float]],
    payload_pos: list[float],
    fence_list: list[list[float]],
    survey_grid: list[list[float]],
    obs_list: list[list[float]],
    camera: Camera,
    uav: Uav,
) -> bool:
    x = calc_drop_loc(
        uav.config_data["aircraftAltitude"],
        uav.config_data["aircraftVelocity"],
        uav.config_data["windSpeed"],
        uav.config_data["windBearing"],
    )
    
    search_wps = generateSurveyFromList(survey_grid, camera.spacing, original_mission[-1], uav.config_data['survey_alt'])
    uav.add_mission_waypoints(search_wps)

    uav.add_mission_waypoints(original_mission)
    # todo payload drop equation

    uav.add_servo_dropping_wps()

    print("done with mission")
    return True
