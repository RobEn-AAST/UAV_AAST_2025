from pymavlink import mavutil
from modules.utils import calc_drop_loc, get_bearing_2_points, new_waypoint,distance
from modules.Uav import Uav
from modules.survey import generateSurveyFromList, Camera
from modules.path_finder import get_optimum_path, calc_path_cost
from modules.config import MissionConfig


def mission1(
    original_mission: list[list[float]],
    payload_pos: list[float],
    fence_list: list[list[float]],
    survey_grid: list[list[float]],
    camera: Camera,
    uav: Uav,
) -> bool:
    # 1. do original mission

    
    uav.add_mission_waypoints(original_mission)

    # 2. drop the payload
    last_wp = original_mission[-1]
    before_last_wp = original_mission[-2]

    drop_offset = calc_drop_loc(
        uav.config_data["aircraftAltitude"],
        uav.config_data["aircraftVelocity"],
        uav.config_data["windSpeed"],
        uav.config_data["windBearing"],
    )

    # params:
    min_distance=40
    speed=22
    bankangle=60
    lastwp_dropwp_bearing=0
    navl1=15
    #uav.modifi_navl()
    # 1_ calculate min distance

    act_dist=distance(last_wp[0],last_wp[1],payload_pos[0], payload_pos[1])
    if act_dist >= min_distance:
        pass
    else:#put the path
        pass


    curr_plane_brng = get_bearing_2_points(before_last_wp[0], before_last_wp[1], last_wp[0], last_wp[1])


    drop_wp = new_waypoint(payload_pos[0], payload_pos[1], drop_offset, curr_plane_brng + 180)


    uav.add_mission_waypoints([[*drop_wp, uav.config_data["survey_alt"]]])

    uav.add_servo_dropping_wps()

    payload_pos.append(uav.config_data["aircraftAltitude"])

    uav.add_mission_waypoints([payload_pos])

    # 3. do the survey grid exploration
    # search_wps = generateSurveyFromList(
    #     survey_grid, camera.spacing, original_mission[-1]
    # )
    # uav.add_mission_waypoints(search_wps)

    print("done with mission")
    return True
