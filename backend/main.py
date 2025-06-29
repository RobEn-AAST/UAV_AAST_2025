from modules.utils import apply_obs_avoidance
import json
from modules.missions import mission1, mission2
from modules.Uav import Uav
from modules.survey import camera_modules
from modules.entries import uav_connect,choose_mission,config_choose
if __name__ == "__main__":
    config_path = "../files/data.json"
    with open (config_path, 'r') as f:
        Json_data = json.load(f)
    connection_string = uav_connect(Json_data)
    

    uav = Uav(connection_string, config_path)
    # for testing, shall be taken from either frontend or trusted files

    fence_list = [
        [29.8224204464368, 30.8274435997009],
        [29.8225321426879, 30.8230876922607],
        [29.8147503386576, 30.8219075202942],
        [29.8224204464368, 30.8274435997009],
        
    ]
    obs_list = [
        [29.81924640, 30.82612400, 5],
        [29.81956280, 30.82399970, 5],
    ]
    # todo get this from the json file thingy
    wp_list = [
        [29.81771050, 30.82581300, 80],
        [29.82078220, 30.82649950, 80],
        [29.82126620, 30.82413910, 80],
        [29.81785940, 30.82386020, 80],
    ]
    payload_pos = [29.81638870, 30.82347390]
    survey_grid = [
        [29.8206891, 30.8250618],
        [29.8206519, 30.8269072],
        [29.8160349, 30.8260489],
        [29.8161466, 30.8241391],
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
