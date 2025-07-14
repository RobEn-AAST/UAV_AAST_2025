import sys
import os
import json
from sys import platform

# Make sure project root (UAV_AAST_2025) is in sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from backend.modules.utils import apply_obs_avoidance
from backend.modules.missions import mission1, mission2
from backend.modules.Uav import Uav
from backend.modules.survey import camera_modules
from backend.modules.entries import uav_connect, choose_mission, config_choose, return_wp_list
from frontend.utils import autoconnect
if __name__ == "__main__":

    filepath = os.path.dirname(__file__)

    config_path = filepath + "\\..\\files\\data.json"
    if platform == "linux" or platform == "linux2":
        config_path = filepath + "../files/data.json"

    with open (config_path, 'r') as f:
        Json_data = json.load(f)
    
    connection_string = uav_connect(Json_data)
    uav = Uav(connection_string, config_path)

    config_choose(Json_data)
    mission_index = int(choose_mission())
    wp_list,fence_list,obs_list,payload_pos,survey_grid=return_wp_list(Json_data['waypoints_file_csv']
                                                                       ,Json_data['fence_file_csv']
                                                                       ,Json_data['obs_csv']
                                                                       ,Json_data['payload_file_csv']
                                                                       ,Json_data['survey_csv']
                                                                       )
    payload_pos[0].pop()
    for obs in obs_list:
        obs[-1]=Json_data['obs_raduies']
    for x in fence_list[0::]:
        x.pop()
    

    camera = camera_modules["sonya6000"]
    # end for testing

    # this is how we run a mission
    wp_list = apply_obs_avoidance(wp_list, obs_list, uav.config_data["obs_safe_dist"])
    uav.before_mission_logic(fence_list)
    
    if(mission_index == 1):
        mission1(
            original_mission=wp_list,
            payload_pos=payload_pos[0],
            fence_list=fence_list,
            survey_grid=survey_grid,
            camera=camera,
            uav=uav,
        )
        
    elif(mission_index == 2):

        repeat_count = Json_data.get("do_jump_repeat_count")         
        mission2(
            original_mission=wp_list,
            payload_pos=payload_pos[0],
            fence_list=fence_list,
            survey_grid=survey_grid,
            camera=camera,
            uav=uav,
            repeat_count=repeat_count
            )
        
    else:
        raise ValueError(f"Invalid choice: {mission_index}. Please select 1 or 2.")
    
    uav.end_mission_logic()
    autoconnect.start_mavproxy(connection_string)