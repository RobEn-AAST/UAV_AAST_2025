from modules.utils import apply_obs_avoidance
from modules.missions import mission1, mission2
from modules.Uav import Uav
from modules.survey import camera_modules

if __name__ == "__main__":
    config_path = "./files/data.json"
    connection_string = "172.17.176.1:14550"

    uav = Uav(connection_string, config_path)
    fence_list = []
    obs_list = []
    wp_list = [
        [-35.3626223, 149.1652286, 100],
        [-35.3583262, 149.1657114, 100],
        [-35.3561212, 149.1634798, 100],
        [-35.3559112, 149.1563129, 100],
        [-35.3596212, 149.1558409, 100],
    ]
    payload_pos = [-35.3613186, 149.1546607]
    survey_grid = [
        [-35.3654658, 149.1718483],
        [-35.3499959, 149.1711617],
        [-35.3495058, 149.1543388],
        [-35.3653958, 149.1555405],
    ]
    camera = camera_modules["sonya6000"]

    # this is how we run a mission
    wp_list = apply_obs_avoidance(wp_list, obs_list, uav.config_data["obs_safe_dist"])
    uav.before_mission_logic(fence_list)
    mission1(
        original_mission=wp_list,
        payload_pos=payload_pos,
        fence_list=fence_list,
        survey_grid=survey_grid,
        obs_list=obs_list,
        camera=camera,
        uav=uav,
    )
    uav.end_mission_logic()