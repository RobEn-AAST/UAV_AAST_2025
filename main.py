from pymavlink import mavutil
from modules.mission1 import mission1
from modules.mission2 import mission2
from modules.mission3 import mission3
from modules.uav import uav
from modules.convertor20 import Convertor
import json


print("Hello to plane mission automation for simulation or real flight\n"
      "pleas read the Docs for more info and how to deal with it\n \n")

config_file = 'C:/Users/Mostafa/PycharmProjects/fixed wing pymavlink/files/data.json'

config_data = None
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

connection_string1 = '172.30.64.1:14550'
connection_string2 = config_data["raspberry_pi_connection_string"]

print("choose the way of communication :")
print("connection 1 is '127.0.0.1:14550' for local host")
print("connection 2 is for raspberry pi")
print("connection 3 for telemetry system")

the_choice = input("Enter connection number:  ")
master = None
if the_choice == '1':
    master = mavutil.mavlink_connection(connection_string1)
    master.wait_heartbeat()
elif the_choice == '2':
    master = mavutil.mavlink_connection(connection_string2)
    master.wait_heartbeat()
elif the_choice == '3':
    master = mavutil.mavlink_connection(connection_string2)
    master.wait_heartbeat()

print("\nHeartbeat from system (system %u component %u)\n" % (master.target_system, master.target_component))

print("do you have ready csv files or you want to convert .waypoints to csv\n")
print("enter 1 if you have ready csv file")
print("enter 2 if you want to me to convert .waypoint files\n")

the_choice = input("Enter the option number:  ")

if the_choice == "2":
    convert = Convertor()
    print("Enter 111 to convert waypoint,fence and payload files.")
    print(
        "For any file you don't want to convert, use '0'. For example, '101' will convert the waypoint and payload files while leaving the fence file unchanged.")

    valid_inputs = {'111', '110', '101', '100', '011', '010', '001', '000'}
    while True:
        the_choice = input("Enter the option number: ")

        if the_choice in valid_inputs:
            if the_choice == '111':
                convert.convert_to_csv(config_data['waypoints_file_waypoint'], config_data['waypoints_file_csv'])
                convert.convert_to_csv(config_data['fence_file_waypoint'], config_data['fence_file_csv'])
                convert.convert_to_csv(config_data['payload_file_waypoint'], config_data['payload_file_csv'])
            elif the_choice == '110':
                convert.convert_to_csv(config_data['waypoints_file_waypoint'], config_data['waypoints_file_csv'])
                convert.convert_to_csv(config_data['fence_file_waypoint'], config_data['fence_file_csv'])
            elif the_choice == '101':
                convert.convert_to_csv(config_data['waypoints_file_waypoint'], config_data['waypoints_file_csv'])
                convert.convert_to_csv(config_data['payload_file_waypoint'], config_data['payload_file_csv'])
            elif the_choice == '100':
                convert.convert_to_csv(config_data['waypoints_file_waypoint'], config_data['waypoints_file_csv'])
            elif the_choice == '011':
                convert.convert_to_csv(config_data['fence_file_waypoint'], config_data['fence_file_csv'])
                convert.convert_to_csv(config_data['payload_file_waypoint'], config_data['payload_file_csv'])
            elif the_choice == '010':
                convert.convert_to_csv(config_data['fence_file_waypoint'], config_data['fence_file_csv'])
            elif the_choice == '001':
                convert.convert_to_csv(config_data['payload_file_waypoint'], config_data['payload_file_csv'])
            elif the_choice == '000':
                print("No files selected for conversion.")
            break  # Exit the loop after processing a valid input
        else:
            print("Invalid option. Please enter a valid 3-digit code (e.g., '111', '101').")



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


