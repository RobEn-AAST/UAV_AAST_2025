from .convertor20 import Convertor

def config_choose(My_data):
    print("do you have ready csv files or you want to convert .waypoints to csv\n")
    print("enter 1 if you have ready csv file")
    print("enter 2 if you want to me to convert .waypoint files\n")
    print("enter 3 for .pdf file")

    data_type = input("Enter the option number:  ")

    if data_type == "2":
        convert = Convertor()
        convert.convert_to_csv(My_data.config_data['obs_waypoints'], My_data.config_data['obs_csv'])
        print("Enter 111 to convert waypoint,fence and payload files.")
        print(
            "For any file you don't want to convert, use '0'. For example, '101' will convert the waypoint and payload files while leaving the fence file unchanged.")

        valid_inputs = {'111', '110', '101', '100', '011', '010', '001', '000'}
        while True:
            the_choice = input("Enter the option number: ")

            if the_choice in valid_inputs:
                if the_choice == '111':
                    convert.convert_to_csv(My_data.config_data['waypoints_file_waypoint'], My_data.config_data['waypoints_file_csv'])
                    convert.convert_to_csv(My_data.config_data['fence_file_waypoint'], My_data.config_data['fence_file_csv'])
                    convert.convert_to_csv(My_data.config_data['payload_file_waypoint'], My_data.config_data['payload_file_csv'])
                elif the_choice == '110':
                    convert.convert_to_csv(My_data.config_data['waypoints_file_waypoint'], My_data.config_data['waypoints_file_csv'])
                    convert.convert_to_csv(My_data.config_data['fence_file_waypoint'], My_data.config_data['fence_file_csv'])
                elif the_choice == '101':
                    convert.convert_to_csv(My_data.config_data['waypoints_file_waypoint'], My_data.config_data['waypoints_file_csv'])
                    convert.convert_to_csv(My_data.config_data['payload_file_waypoint'], My_data.config_data['payload_file_csv'])
                elif the_choice == '100':
                    convert.convert_to_csv(My_data.config_data['waypoints_file_waypoint'], My_data.config_data['waypoints_file_csv'])
                elif the_choice == '011':
                    convert.convert_to_csv(My_data.config_data['fence_file_waypoint'], My_data.config_data['fence_file_csv'])
                    convert.convert_to_csv(My_data.config_data['payload_file_waypoint'], My_data.config_data['payload_file_csv'])
                elif the_choice == '010':
                    convert.convert_to_csv(My_data.config_data['fence_file_waypoint'], My_data.config_data['fence_file_csv'])
                elif the_choice == '001':
                    convert.convert_to_csv(My_data.config_data['payload_file_waypoint'], My_data.config_data['payload_file_csv'])
                elif the_choice == '000':
                    print("No files selected for conversion.")
                break  # Exit the loop after processing a valid input
            else:
                print("Invalid option. Please enter a valid 3-digit code (e.g., '111', '101').")