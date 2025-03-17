from pymavlink import mavutil
from modules.utils import calc_drop_loc, get_bearing_2_points, new_waypoint
from modules.uav import Uav
from modules.survey import generateSurveyFromList, Camera
from modules.path_finder import get_optimum_path, calc_path_cost
from modules.config import MissionConfig


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

    # drop equation logic
    last_wp = original_mission[-1]
    before_last_wp = original_mission[-2]
    drop_offset = calc_drop_loc(
        uav.config_data["aircraftAltitude"],
        uav.config_data["aircraftVelocity"],
        uav.config_data["windSpeed"],
        uav.config_data["windBearing"],
    )
    approach_offset = drop_offset + MissionConfig.safe_approach_throw

    curr_plane_brng = get_bearing_2_points(
        before_last_wp[0], before_last_wp[1], last_wp[0], last_wp[1]
    )
    curr_plane_pos = [last_wp[0], last_wp[1], curr_plane_brng]

    best_brng = None
    min_cost = None

    for brng in range(0, 360, 1):
        approach_wp = new_waypoint(
            payload_pos[0], payload_pos[1], approach_offset, brng
        )

        path = get_optimum_path(
            [curr_plane_pos[0], curr_plane_pos[1], curr_plane_brng],
            [approach_wp[0], approach_wp[1], brng],
        )

        cost = calc_path_cost(path)

        if min_cost is None or cost < min_cost:
            best_brng = brng
            min_cost = cost

    approach_wp = new_waypoint(payload_pos[0], payload_pos[1], approach_offset, best_brng)
    drop_wp = new_waypoint(payload_pos[0], payload_pos[1], drop_offset, best_brng)

    # add them in order approach_wp -> drop_wp then the servo logic
    uav.add_servo_dropping_wps()

    print("done with mission")
    return True
