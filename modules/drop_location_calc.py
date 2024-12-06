import csv
class payload:
    def __init__(self,config_data):
        self.config_data=config_data


    def get_drop_loc(self):
        try:
            with open(self.config_data['payload_file_csv'], mode='r') as file:
                csv_reader = csv.reader(file)

                # Convert CSV content to a list of lines
                lines = list(csv_reader)
                row = lines[1]
                row_data = row[0].split()
                drop_wp_lat, drop_wp_long = float(row_data[0]), float(row_data[1])
                return drop_wp_lat, drop_wp_long

        except FileNotFoundError:
            print(f"CSV file '{self.config_data['payload_file_csv']}' not found.")
            return
        except Exception as e:
            print(f"An error occurred while reading the CSV file: {e}")
            return