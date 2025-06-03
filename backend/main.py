from modules.utils import apply_obs_avoidance
from modules.missions import mission1, mission2
from modules.Uav import Uav
from modules.survey import camera_modules

if __name__ == "__main__":
    config_path = "./files/data.json"
    connection_string = "172.18.224.1:14550"

    uav = Uav(connection_string, config_path)
    # for testing, shall be taken from either frontend or trusted files
    fence_list = [
        [-35.3637859, 149.1648209],
        [-35.3620536, 149.1644239],
        [-35.3618611, 149.1661835],
        [-35.3635497, 149.1665268],
    ]
    obs_list = []
    wp_list = [
        [-35.3627010,	149.1644239, 100],
        [-35.3617648,	149.1655612, 100],
    ]
    payload_pos = [-35.3625260,	149.1690803]
    survey_grid = [
        [-35.3614324, 149.1694236],
        [-35.3628410, 149.1696274],
        [-35.3628148, 149.1722023],
        [-35.3612399, 149.1718376],
    ]

    camera = camera_modules["sonya6000"]
    # end for testing

    # this is how we run a mission
    wp_list = apply_obs_avoidance(wp_list, obs_list, uav.config_data["obs_safe_dist"])
    uav.before_mission_logic(fence_list)
    mission1(
        original_mission=wp_list,
        payload_pos=payload_pos,
        fence_list=fence_list,
        survey_grid=survey_grid,
        camera=camera,
        uav=uav,
    )
    uav.end_mission_logic()
