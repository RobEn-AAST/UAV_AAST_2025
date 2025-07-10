from pymavlink import mavutil

def mission2(original_mission, payload_pos, fence_list, survey_grid, camera, uav, repeat_count):
    print("[MISSION 2] Starting Mission 2")

    uav.messages.clear_mission()

    uav.add_home_wp()
    uav.takeoff_sequence()

    # Add first 4 waypoints only
    for wp in original_mission[:4]:
        lat, lon, alt = wp
        uav.add_mission_item(
            command=mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
            lat=lat, lon=lon, alt=alt
        )

    # Add DO_JUMP to loop back to first waypoint (seq=2)
    uav.add_mission_item(
        command=mavutil.mavlink.MAV_CMD_DO_JUMP,
        param1=2,          # waypoint index to jump to
        param2=repeat_count # number of repeats (0 = infinite)
    )

    uav.end_mission_logic()
