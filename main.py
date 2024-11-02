from pymavlink import mavutil
from modules.txt_csv import WaypointsConverter
from modules.mission1 import mission1
from modules.mission2 import mission2
from modules.mission3 import mission3
from modules.uav import uav
import json

config_file = 'C:/Users/Mostafa/PycharmProjects/fixed wing pymavlink/files/data.json'
converter = WaypointsConverter(config_file)
converter.convert()

try:
    with open(config_file, 'r') as f:
        # Load JSON data
        config_data = json.load(f)
except FileNotFoundError:
    print(f"JSON file '{config_file}' not found.")
except json.JSONDecodeError as e:
    print(f"Error decoding JSON: {e}")
except KeyError as e:
    print(f"KeyError: Missing key {e}")
except Exception as e:
    print(f"An error occurred: {e}")

print("choose the way of communication :")
print("connection 1 is '127.0.0.1:14550' for local host")
print("connection 2 is 'cocowawa' for raspberry pi")
connection_string1 = '172.30.64.1:14550'
connection_string2 = config_data["raspberry_pi_connection_string"]
the_choice = input("Enter connection number.....  \n")
if the_choice == '1':
    master = mavutil.mavlink_connection(connection_string1)
    master.wait_heartbeat()
elif the_choice == '2':
    master = mavutil.mavlink_connection(connection_string2)
    master.wait_heartbeat()

print("Heartbeat from system (system %u component %u)" % (master.target_system, master.target_component))
my_uav = uav(master, config_data["waypoints_file_csv"], config_data["fence_file_csv"], config_data["payload_file_csv"],
             config_file)
my_uav.upload_fence()
print("choose the mission you want :")
print("enter '1' for mission 1 'payload mission' ")
print("enter '2' for mission 2 'survey mission' ")
print("enter '3' for mission 3 'endurance' ")
the_mission_index = input("Enter mission number.....  \n")

if the_mission_index == '1':
    mission1(my_uav)
elif the_mission_index == '2':
    mission2()
elif the_mission_index == '3':
    mission3()


