import csv
import json
from typing import Optional, Tuple


class WaypointsConverter:
    def __init__(self, config_file) -> None:
        self._config_file = config_file
        self._waypoints_files :list[str] = []
        self._csv_files :list[str]= []
        self._config_data = {}
        self._load_config()  # Load config automatically

    def _load_config(self) -> None:
        """Load configuration data from JSON file."""
        try:
            with open(self._config_file, 'r') as f:
                # Load JSON data
                self._config_data = json.load(f)
                self._waypoints_files = [self._config_data["waypoints_file_waypoint"],
                                         self._config_data["fence_file_waypoint"],
                                         self._config_data["payload_file_waypoint"]]
                self._csv_files = [self._config_data["waypoints_file_csv"],
                                   self._config_data["fence_file_csv"],
                                   self._config_data["payload_file_csv"]]
        except FileNotFoundError:
            print(f"JSON file '{self._config_file}' not found.")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
        except KeyError as e:
            print(f"KeyError: Missing key {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

    @staticmethod
    def _pars_line(line: str) -> Optional[Tuple[str, str, str]]:
        words = line.strip().split()
        if len(words) >= 10:  # Ensure there are enough words in the line
            return words[8], words[9], words[10]
        else:
            print(f"Invalid format in line: {line}. Skipping.")
            return None

    def _convert_file(self, n):
        try:
            with open(self._waypoints_files[n], 'r') as txt_file, open(self._csv_files[n], 'w', newline='',
                                                                      encoding='utf-8') as csv_file:
                txt_data = txt_file.readlines()
                csv_data = csv.writer(csv_file)
                csv_data.writerow(["lat", "long", "alt"])
                for i, line in enumerate(txt_data):
                    if i <= 1:
                        continue
                    result = self._pars_line(str(line))
                    if result:
                        csv_data.writerow(result)
        except FileNotFoundError:
            print(f"The file '{self._waypoints_files[n]}' was not found.")
        except IOError:
            print(f"An error occurred while trying to read/write the files.")

    def convert(self):
        for n in range(len(self._waypoints_files)):
            self._convert_file(n)