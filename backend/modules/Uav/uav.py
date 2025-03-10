import json
from pymavlink import mavutil, mavwp
from modules.utils import new_waypoint
from modules.Uav.uav_messages import uav_messages


class Uav:
    def __init__(self, connection_string: str, config_data_path: str) -> None:
        master = mavutil.mavlink_connection(connection_string)
        if not master.wait_heartbeat(timeout=10):
            raise ConnectionError("Failed to establish connection with UAV - no heartbeat received")
        print('Connection established with UAV')

        with open(config_data_path, "r") as f:
            config_data = json.load(f)

        self.master = master
        self.config_data = config_data
        self.wp = mavwp.MAVWPLoader()
        self.messages = uav_messages(config_data, master)
        self.init_bearing = 10  # todo calculate this upon launch

    def takeoff_sequence(self) -> bool:
        # Add the return point
        takeoff_alt = self.config_data["take_off_alt"]
        home_lat = self.config_data["home_lat"]
        home_long = self.config_data["home_long"]
        take_off_angle = self.config_data["take_off_angle"]
        self.wp.insert(
            1,
            mavutil.mavlink.MAVLink_mission_item_message(
                self.master.target_system,
                self.master.target_component,  # component id
                0,  # seq (waypoint ID)
                mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,  # frame id (global relative altitude)
                mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,  # mav_cmd (waypoint command)
                0,  # current (false)
                0,  # auto continue (false)
                take_off_angle,
                0,
                0,
                0,  # params 1-4: hold time (s), acceptable radius (m), pass/orbit, yaw angle
                home_lat,
                home_long,
                takeoff_alt,  # lat/lon/alt
            ),
        )

        return True

    def landingSequence(self) -> bool:
        home_lat = self.config_data["home_lat"]
        home_long = self.config_data["home_long"]
        start_land_dist = self.config_data["start_land_dist"]
        loiter_alt = self.config_data["loiter_alt"]
        loiter_rad = self.config_data["loiter_rad"]

        loiter_lat, loiter_long = new_waypoint(
            home_lat, home_long, start_land_dist, self.init_bearing - 180
        )

        self.wp.add(
            mavutil.mavlink.MAVLink_mission_item_message(
                self.master.target_system,
                self.master.target_component,
                0,
                mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                mavutil.mavlink.MAV_CMD_NAV_LOITER_TO_ALT,
                0,
                1,
                0,
                loiter_rad,
                0,
                0,
                loiter_lat,
                loiter_long,
                loiter_alt,
            )
        )
        x, y = new_waypoint(home_lat, home_long, 50, self.init_bearing)
        self.wp.add(
            mavutil.mavlink.MAVLink_mission_item_message(
                self.master.target_system,
                self.master.target_component,
                0,
                mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                mavutil.mavlink.MAV_CMD_NAV_LAND,
                0,
                1,
                0,
                0,
                0,
                0,
                x,
                y,
                0,
            )
        )
        self.wp.add(
            mavutil.mavlink.MAVLink_mission_item_message(
                self.master.target_system,
                self.master.target_component,
                0,
                mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                mavutil.mavlink.MAV_CMD_DO_SET_SERVO,
                0,
                1,
                self.config_data["payload_servo_no"],
                self.config_data["PAYLOAD_CLOSE_PWM_VALUE"],
                0,
                0,
                0,
                0,
                0,
            )
        )

    # custom points related

    def servo_wp(self, is_open):
        self.wp.add(
            mavutil.mavlink.MAVLink_mission_item_message(
                self.master.target_system,
                self.master.target_component,
                0,
                mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                mavutil.mavlink.MAV_CMD_DO_SET_SERVO,
                0,
                1,
                self.config_data["payload_servo_no"],
                self.config_data[
                    "PAYLOAD_OPEN_PWM_VALUE" if is_open else "PAYLOAD_CLOSE_PWM_VALUE"
                ],
                0,
                0,
                0,
                0,
                0,
            )
        )

    def add_delay_wp(self, delay: float):
        """receives delay in seconds"""
        self.wp.add(
            mavutil.mavlink.MAVLink_mission_item_message(
                self.master.target_system,
                self.master.target_component,
                0,
                mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                mavutil.mavlink.MAV_CMD_CONDITION_DELAY,
                0,
                1,
                delay,
                0,
                0,
                0,
                0,
                0,
                0,
            )
        )

    def add_servo_dropping_wps(self):
        self.servo_wp(is_open=True)
        self.add_delay_wp(self.config_data["drop_close_delay"])
        self.servo_wp(is_open=False)

    # extra logic idk

    def add_mission_waypoints(self, wp_list: list[list[float]]) -> bool:
        """Expected wp_list format:
        [ [lat, long, alt] ]
        """
        for i in range(len(wp_list)):
            lat, long, alt = wp_list[i]
            self.wp.add(
                mavutil.mavlink.MAVLink_mission_item_message(
                    self.master.target_system,
                    self.master.target_component,  # component id
                    0,  # seq (waypoint ID)
                    mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,  # frame id (global relative altitude)
                    mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,  # mav_cmd (waypoint command)
                    0,  # current (false)
                    1,  # auto continue (false)
                    0,
                    0,
                    0,
                    0,  # params 1-4: hold time (s), acceptable radius (m), pass/orbit, yaw angle
                    lat,
                    long,
                    alt,  # lat/lon/alt
                )
            )

    def upload_missions(self):
        self.master.waypoint_count_send(self.wp.count())

        for _ in range(self.wp.count()):
            msg = self.master.recv_match(type="MISSION_REQUEST", blocking=True)
            self.master.mav.send(self.wp.wp(msg.seq))

    def add_home_wp(self):
        home = []
        msg = self.master.recv_match(type="GLOBAL_POSITION_INT", blocking=True)
        home = [msg.lat / 1e7, msg.lon / 1e7]

        self.wp.add(
            mavutil.mavlink.MAVLink_mission_item_message(
                self.master.target_system,
                self.master.target_component,
                0,
                mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                mavutil.mavlink.MAV_CMD_DO_SET_HOME,
                0,
                1,
                0,
                0,
                0,
                0,
                home[0],
                home[1],
                0,
            )
        )

    def before_mission_logic(self, fence_list: list[list[float]]):
        self.messages.upload_fence(fence_list)
        self.messages.clear_mission()
        self.add_home_wp()
        self.takeoff_sequence()

    def end_mission_logic(self):
        self.landingSequence()
        self.upload_missions()