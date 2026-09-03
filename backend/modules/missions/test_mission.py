def test_mission(original_mission, payload_pos, fence_list, survey_grid,
             camera, uav):

    print("[TEST MISSION] Starting Mission ")

    # Add waypoints loaded from the mission file
    uav.add_mission_waypoints(original_mission)

    # Upload the mission
    success = uav.messages.upload_mission()

    if success:
        print("[TEST MISSION] Mission uploaded successfully")
        return True

    print("[TEST MISSION] Mission upload failed")
    return False