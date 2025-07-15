import sys
import os

# Add project root to path for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Import the smart path manager
from path_manager import PathManager

# Import backend modules
from backend.modules.utils import apply_obs_avoidance
from backend.modules.missions import mission1, mission2
from backend.modules.Uav import Uav
from backend.modules.survey import camera_modules
from backend.modules.entries import uav_connect, choose_mission, config_choose, return_wp_list
from frontend.utils import autoconnect

def main():
    # Initialize smart path manager
    path_manager = PathManager()
    
    # Ensure all necessary directories exist
    path_manager.ensure_directories_exist()
    
    # Load configuration with smart paths
    print("Loading configuration with smart path resolution...")
    config_data = path_manager.load_config()
    
    print(f"Project root: {path_manager.project_root}")
    print(f"Config loaded from: {path_manager.get_file_path('data.json')}")
    
    # Connect to UAV
    connection_string = uav_connect(config_data)
    
    # Adapt connection string for current platform if needed
    connection_string = path_manager.get_connection_string_for_platform(connection_string)
    print(f"Using connection string: {connection_string}")
    
    # Create UAV instance
    config_path = path_manager.get_file_path("data.json")
    uav = Uav(connection_string, config_path)

    # Configure mission
    config_choose(config_data)
    mission_index = int(choose_mission())
    
    # Load waypoint files using smart paths
    wp_list, fence_list, obs_list, payload_pos, survey_grid = return_wp_list(
        config_data['waypoints_file_csv'],
        config_data['fence_file_csv'], 
        config_data['obs_csv'],
        config_data['payload_file_csv'],
        config_data['survey_csv']
    )
    
    # Process data
    payload_pos[0].pop()
    for obs in obs_list:
        obs[-1] = config_data['obs_raduies']
    for x in fence_list[0::]:
        x.pop()

    # Initialize camera
    camera = camera_modules["sonya6000"]

    # Apply obstacle avoidance
    wp_list = apply_obs_avoidance(wp_list, obs_list, uav.config_data["obs_safe_dist"])
    
    # Prepare mission
    uav.before_mission_logic(fence_list)
    
    # Execute mission based on selection
    if mission_index == 1:
        print("Executing Mission 1...")
        mission1(
            original_mission=wp_list,
            payload_pos=payload_pos[0],
            fence_list=fence_list,
            survey_grid=survey_grid,
            camera=camera,
            uav=uav,
        )
        
    elif mission_index == 2:
        print("Executing Mission 2...")
        repeat_count = config_data.get("do_jump_repeat_count")         
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
    
    # Complete mission
    uav.end_mission_logic()
    
    # Start MAVProxy with adapted connection string
    autoconnect.start_mavproxy(connection_string)
    
    print("Mission completed successfully!")


if __name__ == "__main__":
    main()