from .Convertor import Convertor
from .pdf_reader_files import convert_pdf
import csv
from sys import platform
from os import path


def uav_connect(My_data):
    print("choose the way of communication: ")
    print("connection 1 is '127.0.0.1:14550' for local host")
    print("connection 2 is for network sharing")
    print("connection 3 for telemetry system")
    connection_type = input("Enter connection number:  ")
    if connection_type == '1':
        connection_string=My_data['sim_connection_string']
    if connection_type == '2':
        connection_string = My_data['Local_connection_string']
    if connection_type == '3':
        connection_string = My_data['telem_link']
    return connection_string


def config_choose(My_data):
    print("\nDo you have ready csv files or you want to convert .waypoints to csv")
    print("enter 1 if you have ready csv file")
    print("enter 2 if you want to me to convert .waypoint files")
    print("enter 3 for .pdf file")

    data_type = input("Enter the option number: ")

    if data_type == "2":
        convert = Convertor()
        convert.convert_to_csv(My_data['obs_waypoints'], My_data['obs_csv'])
        print("Enter 111 to convert waypoint,fence and payload files.")
        print("For any file you don't want to convert, use '0'." \
        "For example, '101' will convert the waypoint and payload" \
        "files while leaving the fencefile unchanged.")

        valid_inputs = {f"{i:04b}" for i in range(2**4)}
        while True:
            the_choice = input("Enter the option number: ")
            if the_choice in valid_inputs:
                pars_the_choice = [int(char) for char in the_choice]
                if pars_the_choice[0]== 1:
                    convert.convert_to_csv(My_data['waypoints_file_waypoint'], My_data['waypoints_file_csv'])
                if pars_the_choice[1]== 1:
                    convert.convert_to_csv(My_data['fence_file_waypoint'], My_data['fence_file_csv'])
                if pars_the_choice[2]==1:
                    convert.convert_to_csv(My_data['payload_file_waypoint'], My_data['payload_file_csv'])
                if pars_the_choice[3]==1:
                    convert.convert_to_csv(My_data['survey_waypoints'], My_data['survey_csv'])
                break
                        
                
            else:
                print("Invalid option. Please enter a valid 3-digit code (e.g., '111', '101').")

    elif data_type == "3":

        filepath = (__file__).replace(path.basename(__file__), '')
        convert_pdf(filepath + My_data['pdf_mission'])


def choose_mission():

    print("\nChoose the mission you want :")
    print("enter '1' for mission 1 'payload mission' ")
    print("enter '2' for mission 2 'survey mission' ")
    print("enter '3' for mission 3 'endurance' ")

    the_mission_index = input("Enter mission number: ")

    return the_mission_index



def return_wp_list(*config_data)->list:
        results=[]
        for file in config_data: 
            wp_list=[]
            try:
                    with open(file, mode='r') as f:
                        csv_reader = csv.reader(f)

                        # Convert CSV content to a list of lines
                        lines = list(csv_reader)

                        # Iterate over the rows, skipping the header
                        for i, row in enumerate(lines[1:]):
                            try:
                                # Ensure the row is processed correctly
                                row = ' '.join(row).split()
                                lat, long, alt = float(row[0]), float(row[1]), float(row[2])
                                wp_list.append([lat, long, alt])
                            except ValueError as ve:
                                print(f"Skipping malformed row at line {i + 2}: {row} (Error: {ve})")
                    results.append(wp_list)
            except FileNotFoundError:
                    print(f"CSV file '{config_data}' not found.")
                    return
            except Exception as e:
                    print(f"An error occurred while reading the CSV file: {e}")
                    return
        return (*results[:5],)            

