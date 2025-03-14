from pymavlink import mavutil
from modules.utils import calc_drop_loc, get_bearing_2_points, new_waypoint
from modules.Uav import Uav
from modules.survey import generateSurveyFromList, Camera
from modules.shortest_path_generator import get_optimum_path


def mission1(
    original_mission: list[list[float]],
    payload_pos: list[float],
    fence_list: list[list[float]],
    survey_grid: list[list[float]],
    obs_list: list[list[float]],
    camera: Camera,
    uav: Uav,
) -> bool:
    search_wps = generateSurveyFromList(
        survey_grid, camera.spacing, original_mission[-1], uav.config_data["survey_alt"]
    )
    uav.add_mission_waypoints(search_wps)

    uav.add_mission_waypoints(original_mission)

    # get the last 2 points for our drop location

    last_wp = original_mission[-1]
    before_last_wp = original_mission[-2]
    drop_offset = calc_drop_loc(
        uav.config_data["aircraftAltitude"],
        uav.config_data["aircraftVelocity"],
        uav.config_data["windSpeed"],
        uav.config_data["windBearing"],
    )

    plane_brng = get_bearing_2_points(before_last_wp[0], before_last_wp[1], last_wp[0], last_wp[1])
    plane_wp = [last_wp[0], last_wp[1], plane_brng]

    drop_brng = 30  # TODO CALCULATE THIS BASED ON WHAT IS THE BEST
    drop_wp = new_waypoint(payload_pos[0], payload_pos[1], drop_offset, drop_brng)

    get_optimum_path(
        [plane_wp[0], plane_wp[1], plane_brng], [drop_wp[0], drop_wp[1], drop_brng], uav.config_data['bank_angle'], uav.config_data['aircraftVelocity']
    )

    uav.add_servo_dropping_wps()

    print("done with mission")
    return True
