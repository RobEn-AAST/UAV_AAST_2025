import pymavlink.mavutil as utility
import pymavlink.dialects.v20.all as dialect

def mission1(my_uav):
    my_uav.clear_mission()
    my_uav.takeoff_sequence()
    my_uav.add_mission_waypoints()
    my_uav.upload_missions()
