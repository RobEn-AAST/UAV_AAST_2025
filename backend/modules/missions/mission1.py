from pymavlink import mavutil
from modules.utils import calc_drop_loc, get_bearing_2_points, new_waypoint
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

    curr_plane_brng = get_bearing_2_points(
        before_last_wp[0], before_last_wp[1], last_wp[0], last_wp[1]
    )
    curr_plane_pos = [last_wp[0], last_wp[1], curr_plane_brng]

    best_brng = None
    min_cost = None
    best_path = None

    for brng in range(0, 360, 3):
        approach_wp = new_waypoint(payload_pos[0], payload_pos[1], drop_offset, brng + 180)

        path = get_optimum_path(
            [curr_plane_pos[0], curr_plane_pos[1], curr_plane_brng],
            [approach_wp[0], approach_wp[1], brng],
        )

        cost = calc_path_cost(path, fence_list)

        if min_cost is None or cost < min_cost:
            best_brng = brng
            min_cost = cost
            best_path = path

    assert best_path is not None, "Could not find a valid path to drop location"
    assert best_brng is not None, "Best bearing is none"

    drop_wp = new_waypoint(payload_pos[0], payload_pos[1], drop_offset, best_brng + 180)

    # todo reduce speed here
    uav.add_mission_waypoints(
        [[*pnt, MissionConfig.payload_alt] for pnt in best_path[:-1]]
    )
    uav.add_mission_waypoints([[*drop_wp, MissionConfig.payload_alt]])

    uav.add_servo_dropping_wps()

    # 3. do the survey grid exploration
    search_wps = generateSurveyFromList(
        survey_grid, camera.spacing, original_mission[-1]
    )
    uav.add_mission_waypoints(search_wps)

    print("done with mission")
    return True
