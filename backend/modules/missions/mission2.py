from pymavlink import mavutil

def mission2(original_mission, payload_pos, fence_list, survey_grid, camera, uav, repeat_count):
    print("[MISSION 2] Starting Mission 2")


    uav.add_mission_waypoints(original_mission)
    # Add DO_JUMP to loop back to first waypoint (seq=2)
    uav.add_mission_item(
        command=mavutil.mavlink.MAV_CMD_DO_JUMP,
        param1=1,          
        param2=repeat_count 
    )

