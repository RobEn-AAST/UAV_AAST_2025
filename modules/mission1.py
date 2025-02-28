import pymavlink.mavutil as utility
import pymavlink.dialects.v20.all as dialect
from pymavlink import mavutil
from modules.uav import uav
from modules.Data_loader import DataLoader


def mission1(connection_type,config_data):
    if connection_type == '1':
        connection_string = config_data['sim_connection_string']
    elif connection_type == '2':
        connection_string = config_data['raspberry_pi_connection_string']
    elif connection_type == '3':
        connection_string = config_data['telem_link']

    master = mavutil.mavlink_connection(connection_string)
    master.wait_heartbeat()

    my_uav= uav(master,config_data)

    my_uav.upload_fence()
    my_uav.clear_mission()
    my_uav.add_home_wp()
    my_uav.takeoff_sequence()
    my_uav.do_obs_avoid()
    my_uav.add_mission_waypoints()
    my_uav.add_drop_location_wp()
    my_uav.landingSequence()
    my_uav.upload_missions()

