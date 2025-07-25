from .Convertor import Convertor
from .pdf_reader_files import convert_pdf
import csv


def uav_connect(My_data):
    print("Choose the way of communication:")
    print("1: '{}' for simulator".format(My_data['connection']['sim_connection_string']))
    print("2: '{}' for local network".format(My_data['connection']['Local_connection_string']))
    print("3: '{}' for telemetry".format(My_data['connection']['telem_link']))

    connection_type = input("Enter connection number: ")

    if connection_type == '1':
        return My_data['connection']['sim_connection_string']
    elif connection_type == '2':
        return My_data['connection']['Local_connection_string']
    elif connection_type == '3':
        return My_data['connection']['telem_link']
    else:
        print("Invalid input, defaulting to sim.")
        return My_data['connection']['sim_connection_string']


def config_choose(My_data):
    paths = My_data["paths"]

    print("\nDo you have ready CSV files or want to convert .waypoints?")
    print("1: I have ready CSV")
    print("2: Convert .waypoints to CSV")
    print("3: Convert mission PDF")

    data_type = input("Enter option number: ")

    if data_type == "2":
        convert = Convertor()
        convert.convert_to_csv(paths['obs_waypoints'], paths['obs_csv'])

        print("Enter a 4-digit binary string to choose which files to convert:")
        print("1st: waypoints, 2nd: fence, 3rd: payload, 4th: survey")
        print("Example: '1010' converts waypoints and payload only")

        valid_inputs = {f"{i:04b}" for i in range(16)}

        while True:
            the_choice = input("Enter your choice: ")
            if the_choice in valid_inputs:
                flags = [int(c) for c in the_choice]

                if flags[0]: convert.convert_to_csv(paths['waypoints_file_waypoint'], paths['waypoints_file_csv'])
                if flags[1]: convert.convert_to_csv(paths['fence_file_waypoint'], paths['fence_file_csv'])
                if flags[2]: convert.convert_to_csv(paths['payload_file_waypoint'], paths['payload_file_csv'])
                if flags[3]: convert.convert_to_csv(paths['survey_waypoints'], paths['survey_csv'])
                break
            else:
                print("Invalid input. Please use a 4-digit binary like '1100'.")

    elif data_type == "3":
        convert_pdf(paths['pdf_mission'], paths['docx_file'])


def choose_mission(mission_index=None):
    if mission_index is not None:
        return mission_index
    return int(input("Enter mission number: "))


def return_wp_list(*config_files) -> list:
    results = []
    for file_path in config_files:
        wp_list = []
        try:
            with open(file_path, mode='r') as f:
                csv_reader = csv.reader(f)
                lines = list(csv_reader)

                for i, row in enumerate(lines[1:]):
                    try:
                        row = ' '.join(row).split()
                        lat, long, alt = float(row[0]), float(row[1]), float(row[2])
                        wp_list.append([lat, long, alt])
                    except ValueError as ve:
                        print(f"Skipping malformed row at line {i + 2}: {row} (Error: {ve})")
            results.append(wp_list)
        except FileNotFoundError:
            print(f"CSV file '{file_path}' not found.")
            return
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return
    return (*results[:5],)

def choose_flight_controller():
    print("\nChoose flight controller:")
    print("1: Orange Cube")
    print("2: Pixhawk 2.4.8")

    choice = input("Enter number (1-2): ")

    if choice == "1":
        return "orange_cube"
    elif choice == "2":
        return "pixhawk_2_4_8"

    else:
        print("Invalid input. Defaulting to 'sim'")
        return "orange_cube"