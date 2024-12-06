import json
import csv
class DataLoader:
    def __init__(self, config_file):
        self.config_file = config_file
        self.config_data = self.load_config()

    def load_config(self):
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"JSON file '{self.config_file}' not found.")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")
        return {}

