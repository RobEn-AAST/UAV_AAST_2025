from backend.modules.utils.geo_math import (
    get_bearing_2_points,
    new_waypoint,
    calc_drop_loc,
)
from backend.modules.utils.math import get_dist_2_points
from backend.modules.Uav import Uav
from backend.modules.survey import generateSurveyFromList, Camera
from backend.modules.utils.obs_avoid import apply_obs_avoidance
from backend.modules.utils.payload_alg import get_payload_approach_bearing, create_straight_line_approach_simple
import math

def mission1(
    original_mission: list[list[float]],
    payload_pos: list[float],
    fence_list: list[list[float]],
    survey_grid: list[list[float]],
    camera: Camera,
    uav: Uav,
    fl,
) -> bool:

    # 1️ Add original mission waypoints
    print("Executing original mission waypoints...")
    uav.add_mission_waypoints(original_mission)

    # 2️ Calculate drop offset
    drop_offset = calc_drop_loc(
        uav.config_data["flight"]["aircraftAltitude"],
        uav.config_data["flight"]["aircraftVelocity"],
        uav.config_data["flight"]["windSpeed"],
        uav.config_data["flight"]["windBearing"],
    ) * 2

    # 3 Determine approach bearing inside temporary rectangle
    approach_bearing = get_payload_approach_bearing(fence_list, payload_pos)
    print(f"Payload approach bearing: {approach_bearing}°")

    # 4️ Generate straight line approach waypoints
    approach_waypoints = create_straight_line_approach_simple(
        target_point=payload_pos,
        approach_bearing=approach_bearing,
        total_distance=drop_offset,
        num_points=5,
        uav_altitude=uav.config_data["flight"]["aircraftAltitude"],
    )

    uav.add_mission_waypoints(approach_waypoints)

    # 5️ Add drop waypoint
    drop_wp = new_waypoint(
        payload_pos[0],
        payload_pos[1],
        10,
        (approach_bearing + 180) % 360,
    )
    uav.add_mission_waypoints([[*drop_wp, uav.config_data["flight"]["survey_alt"]]])

    uav.add_servo_dropping_wps(fl)

    # 6️ Final payload position
    payload_pos.append(70)
    uav.add_mission_waypoints([payload_pos])
    uav.add_mission_waypoints([[*new_waypoint(payload_pos[0],payload_pos[1],20,approach_bearing),70]])
    # 7️ Add survey waypoints
    search_wps = generateSurveyFromList(
        survey_grid,
        camera.spacing,
        original_mission[-1],
    )
    uav.add_mission_waypoints(search_wps)

    print("Mission 1 completed successfully")
    return True


