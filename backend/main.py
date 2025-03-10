from modules.utils import apply_obs_avoidance
from modules.missions import mission1, mission2
from modules.Uav import Uav

config_path = "./files/data.json"
connection_string = "172.18.224.1:14550"

uav = Uav(connection_string, config_path)

# execute mission 1

# now execute mission
# read fence

fence_list = []
obs_list = []
wps_list = []
payload_pos = []
survey_grid = []

wp_list = apply_obs_avoidance(wps_list, obs_list, uav.config_data["obs_safe_dist"])

uav.before_mission_logic(fence_list)
mission1(wp_list, payload_pos, uav)

uav.end_mission_logic()