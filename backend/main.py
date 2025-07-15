from modules.utils import apply_obs_avoidance
import json
from modules.missions import mission1, mission2
from modules.Uav import Uav
from modules.survey import camera_modules
from modules.entries import uav_connect,choose_mission,config_choose,return_wp_list
if __name__ == "__main__":
    config_path = "../files/data.json"
    with open (config_path, 'r') as f:
        Json_data = json.load(f)
    connection_string = uav_connect(Json_data)
    uav = Uav(connection_string, config_path)
    config_choose(Json_data)
    mission_index = choose_mission()
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
    if mission_index == '1' :
        mission1(
            original_mission=wp_list,
            payload_pos=payload_pos[0],
            fence_list=fence_list,
            survey_grid=survey_grid,
            camera=camera,
            uav=uav,
        )
        uav.end_mission_logic()
    if mission_index == '2':
        mission2()
