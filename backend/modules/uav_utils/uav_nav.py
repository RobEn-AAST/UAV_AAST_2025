
import csv

from pymavlink import mavutil, mavwp
from modules.uav_utils import new_waypoint,calc_drop_loc,get_bearing,distance
from modules.readers.drop_location_calc import payload
from modules.utils.obs_avoid import project_point_on_great_circle

class uav_nav:
    def __init__(self, config_data,vehicle):
        self.config_data = config_data
        self.vehicle=vehicle
        self.payload_calc=payload(config_data)
        self.wp = mavwp.MAVWPLoader()

    def takeoff_sequence(self):
            # Add the return point
            takeoff_alt = self.config_data["take_off_alt"]
            home_lat = self.config_data["home_lat"]
            home_long = self.config_data["home_long"]
            take_off_angle = self.config_data["take_off_angle"]
            self.wp.insert(1, mavutil.mavlink.MAVLink_mission_item_message(
                self.vehicle.target_system,
                self.vehicle.target_component,  # component id
                0,  # seq (waypoint ID)
                mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,  # frame id (global relative altitude)
                mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,  # mav_cmd (waypoint command)
                0,  # current (false)
                0,  # auto continue (false)
                take_off_angle, 0, 0, 0,  # params 1-4: hold time (s), acceptable radius (m), pass/orbit, yaw angle
                home_lat, home_long, takeoff_alt  # lat/lon/alt
            ))


    def landingSequence(self):
            home_lat = self.config_data["home_lat"]
            home_long = self.config_data["home_long"]
            start_land_dist = 100
            loiter_alt = 20
            loiter_rad = 50
            loiter_lat, loiter_long = new_waypoint(
                home_lat, home_long, start_land_dist, self.config_data["bearing"] - 180)

            self.wp.add(
                mavutil.mavlink.MAVLink_mission_item_message(
                    self.vehicle.target_system, self.vehicle.target_component, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                    mavutil.mavlink.MAV_CMD_NAV_LOITER_TO_ALT, 0, 1, 0, loiter_rad, 0, 0,
                    loiter_lat, loiter_long, loiter_alt)
            )
            x,y=new_waypoint(home_lat,home_long,50,self.config_data["bearing"])
            self.wp.add(
                mavutil.mavlink.MAVLink_mission_item_message(
                    self.vehicle.target_system, self.vehicle.target_component, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                    mavutil.mavlink.MAV_CMD_NAV_LAND, 0, 1, 0, 0, 0, 0,
                    x, y, 0))

    def close_servo_wp(self):
            self.wp.add(mavutil.mavlink.MAVLink_mission_item_message(
                self.vehicle.target_system,
                self.vehicle.target_component,
                0,
                mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                mavutil.mavlink.MAV_CMD_DO_SET_SERVO,
                0,
                1,
                self.config_data["servoNo"],
                self.config_data["PAYLOAD_CLOSE_PWM_VALUE"],
                0,
                0,
                0, 0, 0))

    def open_servo_wp(self):
            self.wp.add(mavutil.mavlink.MAVLink_mission_item_message(
                self.vehicle.target_system,
                self.vehicle.target_component,
                0,
                mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                mavutil.mavlink.MAV_CMD_DO_SET_SERVO,
                0,
                1,
                self.config_data["servoNo"],
                self.config_data["PAYLOAD_OPEN_PWM_VALUE"],
                0,
                0,
                0, 0, 0))

    def add_delay_wp(self):
                self.wp.add(mavutil.mavlink.MAVLink_mission_item_message(
                    self.vehicle.target_system,
                    self.vehicle.target_component,
                    0,
                    mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                    mavutil.mavlink.MAV_CMD_CONDITION_DELAY,
                    0,
                    1,
                    5,
                    0,
                    0,
                    0,
                    0, 0, 0))



    def add_mission_waypoints(self):

            wp_list=[]

            try:
                with open(self.config_data['wp_plus_obs_csv'], mode='r') as file:
                    csv_reader = csv.reader(file)

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
            except FileNotFoundError:
                print(f"CSV file '{self.config_data['wp_plus_obs_csv']}' not found.")
                return
            except Exception as e:
                print(f"An error occurred while reading the CSV file: {e}")
                return

            if not wp_list:
                print("No valid waypoints found in the file.")
            else:
                print(f"Successfully loaded {len(wp_list)} waypoints.")


            for i in range(len(wp_list)):
                lat, long, alt = wp_list[i]
                self.wp.add(mavutil.mavlink.MAVLink_mission_item_message(
                self.vehicle.target_system,
                self.vehicle.target_component,  # component id
                0,  # seq (waypoint ID)
                mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,  # frame id (global relative altitude)
                mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,  # mav_cmd (waypoint command)
                0,  # current (false)
                1,  # auto continue (false)
                0, 0, 0, 0,  # params 1-4: hold time (s), acceptable radius (m), pass/orbit, yaw angle
                lat, long, alt  # lat/lon/alt
            ))


    def upload_missions(self):
            self.vehicle.waypoint_count_send(self.wp.count())

            for _ in range(self.wp.count()):
                msg = self.vehicle.recv_match(type='MISSION_REQUEST', blocking=True)
                self.vehicle.mav.send(self.wp.wp(msg.seq))

    def add_home_wp(self):
            home = []
            msg = self.vehicle.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
            home = [msg.lat / 1e7, msg.lon / 1e7]

            self.wp.add(mavutil.mavlink.MAVLink_mission_item_message(
                self.vehicle.target_system, self.vehicle.target_component, 0,
                mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                mavutil.mavlink.MAV_CMD_DO_SET_HOME,
                0, 1, 0, 0, 0, 0,
                home[0], home[1], 0))

    def add_drop_location_wp(self):
            x = calc_drop_loc(self.config_data["aircraftAltitude"],self.config_data["aircraftVelocity"],self.config_data["windSpeed"],self.config_data["windBearing"])
            last_wp_lat, last_wp_long, last_wp_alt = self.get_last_wp()
            drop_wp_lat, drop_wp_long  = self.payload_calc.get_drop_loc()
            brng = get_bearing(last_wp_lat, last_wp_long,drop_wp_lat, drop_wp_long)
            open_lat,open_long=new_waypoint(drop_wp_lat,drop_wp_long,x,-brng)

            self.wp.add(mavutil.mavlink.MAVLink_mission_item_message(
                self.vehicle.target_system,
                self.vehicle.target_component,  # component id
                1,  # seq (waypoint ID)
                mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,  # frame id (global relative altitude)
                mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,  # mav_cmd (waypoint command)
                0,  # current (false)
                1,  # auto continue (false)
                0, 0, 0, 0,  # params 1-4: hold time (s), acceptable radius (m), pass/orbit, yaw angle
                open_lat, open_long, last_wp_alt  # lat/lon/alt
            ))
            self.open_servo_wp()
            self.add_delay_wp()
            self.close_servo_wp()

    def payload_seq_2(self):
            pass

    def get_last_wp(self):
        try:
            with open(self.config_data['waypoints_file_csv'], mode='r') as file:
                csv_reader = csv.reader(file)

                # Convert CSV content to a list of lines
                lines = list(csv_reader)
                row = lines[-1]
                row_data = row[0].split()
                last_wp_lat, last_wp_long, last_wp_alt = float(row_data[0]), float(row_data[1]), float(row_data[2])
                return last_wp_lat, last_wp_long, last_wp_alt
        except FileNotFoundError:
            print(f"CSV file '{self.config_data['waypoints_file_csv']}' not found.")
            return
        except Exception as e:
            print(f"An error occurred while reading the CSV file: {e}")
            return



    def do_survey(self):
        pass

    def do_obs_avoid(self):
        obs_list = []
        wp_list=[]

        with open(self.config_data['waypoints_file_csv'], mode='r') as file:
            csvfile=csv.reader(file,delimiter='\t')
            next(csvfile)
            for lines in csvfile:
                wp_list.append([float(lines[0]), float(lines[1]), float(lines[2])])
        with open(self.config_data['obs_csv'], mode='r') as file:
            csvfile=csv.reader(file,delimiter='\t')
            next(csvfile)
            for lines in csvfile:
                obs_list.append([float(lines[0]), float(lines[1])])
        for x in range(len(obs_list)):
            for y in range(len(wp_list)-1):
                    proj_lat,proj_lon = project_point_on_great_circle(wp_list[y][0],wp_list[y][1],wp_list[y+1][0],wp_list[y+1][1],obs_list[x][0],obs_list[x][1])
                    dist = distance(proj_lat,proj_lon,obs_list[x][0],obs_list[x][1])
                    if dist <= 7:
                        print("\n obs_avoid point added\n")
                        line_obs_brng = get_bearing(proj_lat,proj_lon,obs_list[x][0],obs_list[x][1])
                        obs_avoid_lat,obs_avoid_lon= new_waypoint(proj_lat,proj_lon,20,line_obs_brng+180)
                        wp_list.insert(y+1,[obs_avoid_lat,obs_avoid_lon,70])
        wp_list=wp_list
        # Empty the file first
        with open(self.config_data['wp_plus_obs_csv'], 'w', newline='') as file:
            pass  # This will clear the file

        # Write updated waypoints back to CSV
        with open(self.config_data['wp_plus_obs_csv'], 'w', newline='') as file:
            writer = csv.writer(file, delimiter='\t')
            writer.writerow(['lat', 'lon', 'alt'])  # Write header if necessary
            for waypoint in wp_list:
                writer.writerow(waypoint)  # Write each waypoint to the file

        print("Updated Waypoints List written to file:", wp_list)