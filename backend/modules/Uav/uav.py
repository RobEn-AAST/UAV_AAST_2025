import json
from pymavlink import mavutil, mavwp
from modules.utils import new_waypoint
from modules.Uav.uav_messages import uav_messages
from .mav_wp import MavWp


class Uav:
    def __init__(self, connection_string: str, config_data_path: str) -> None:
        master = self.establish_connection(connection_string)
        self.home_lat, self.home_long = None, None

        with open(config_data_path, "r") as f:
            config_data = json.load(f)

        self.master = master
        self.config_data = config_data
        self.wp_loader = mavwp.MAVWPLoader()
        self.messages = uav_messages(master, config_data)
        self.mav_wp = MavWp(master, config_data)
        self.init_bearing = 10  # todo calculate this upon launch

    def establish_connection(self, connection_string) -> mavutil.mavlink_connection:
        master = mavutil.mavlink_connection(connection_string)
        if not master.wait_heartbeat(timeout=10):
            raise ConnectionError(
                "Failed to establish connection with UAV - no heartbeat received"
            )
        print("Connection established with UAV")

        return master

    def takeoff_sequence(self):
        self.wp_loader.insert(1, self.mav_wp.takeoff_wp(self.home_lat, self.home_long))

    def landingSequence(self) -> bool:
        start_land_dist = self.config_data["start_land_dist"]

        loiter_lat, loiter_long = new_waypoint(
            self.home_lat, self.home_long, start_land_dist, self.init_bearing - 180
        )

        self.wp_loader.add(self.mav_wp.loiter_to_alt_wp(loiter_lat, loiter_long))

        land_lat, land_long = new_waypoint(
            self.home_lat, self.home_long, 50, self.init_bearing
        )
        self.wp_loader.add(self.mav_wp.land_wp(land_lat, land_long))

    def add_servo_dropping_wps(self):
        self.wp_loader.add(self.mav_wp.servo_wp(is_open=True))

        delay_wp = self.mav_wp.delay_wp(self.config_data["drop_close_delay"])
        self.wp_loader.add(delay_wp)

        self.wp_loader.add(self.mav_wp.servo_wp(is_open=True))

    # extra logic idk

    def add_mission_waypoints(self, wp_list: list[list[float]]) -> bool:
        """Expected wp_list format:
        [ [lat, long, alt] ]
        """
        for i in range(len(wp_list)):
            lat, long, alt = wp_list[i]
            self.wp_loader.add(self.mav_wp.waypoint(lat, long, alt))

    def add_home_wp(self):
        msg = self.master.recv_match(type="GLOBAL_POSITION_INT", blocking=True)
        self.home_lat, self.home_long = (
            msg.lat / 1e7,
            msg.lon / 1e7,
        )  # ? todo shall we make this conditional

        self.wp_loader.add(self.mav_wp.home_wp(self.home_lat, self.home_long))

    def upload_missions(self) -> bool:
        """Upload all waypoints to the vehicle with proper sequencing"""
        try:
            self.master.waypoint_count_send(self.wp_loader.count())

            for i in range(self.wp_loader.count()):
                msg = self.master.recv_match(
                    type="MISSION_REQUEST", blocking=True, timeout=10
                )
                if msg is None:
                    print(f"No response for waypoint {i}")
                    return False

                wp = self.wp_loader.wp(i)
                wp.seq = i

                self.master.mav.send(wp)

            msg = self.master.recv_match(type="MISSION_ACK", blocking=True, timeout=10)
            if msg is None:
                print("No mission acknowledgment received")
                return False

            return True
        except Exception as e:
            print(f"Error uploading mission: {e}")
            return False

    def before_mission_logic(self, fence_list: list[list[float]]):
        self.messages.upload_fence(fence_list)
        self.messages.clear_mission()
        self.add_home_wp()
        self.takeoff_sequence()

    def end_mission_logic(self):
        self.landingSequence()
        self.upload_missions()
