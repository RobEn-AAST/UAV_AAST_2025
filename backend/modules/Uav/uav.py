import json
from pymavlink import mavutil, mavwp
from modules.utils import new_waypoint
from .uav_messages import UavMessages
from .uav_nav import UavNav


class Uav:
    def __init__(self, connection_string: str, config_data_path: str) -> None:
        master = self.establish_connection(connection_string)
        self.home_lat, self.home_long = None, None

        with open(config_data_path, "r") as f:
            config_data = json.load(f)
        self.config_data = config_data

        self.init_bearing = 10  # todo calculate this upon launch

        self.master = master
        self.wp_loader = mavwp.MAVWPLoader()

        self.messages = UavMessages(master=self.master, config_data=self.config_data, wp_loader=self.wp_loader)
        self.nav = UavNav(master=self.master, config_data=self.config_data)

    def establish_connection(self, connection_string) -> mavutil.mavlink_connection:
        master = mavutil.mavlink_connection(connection_string)
        if not master.wait_heartbeat(timeout=10):
            raise ConnectionError(
                "Failed to establish connection with UAV - no heartbeat received"
            )
        print("Connection established with UAV")

        return master

    def takeoff_sequence(self):
        self.wp_loader.insert(1, self.nav.takeoff_wp(self.home_lat, self.home_long))

    def landingSequence(self) -> bool:
        start_land_dist = self.config_data["start_land_dist"]

        loiter_lat, loiter_long = new_waypoint(
            self.home_lat, self.home_long, start_land_dist, self.init_bearing - 180
        )

        self.wp_loader.add(self.nav.loiter_to_alt_wp(loiter_lat, loiter_long))

        land_lat, land_long = new_waypoint(
            self.home_lat, self.home_long, 50, self.init_bearing
        )
        self.wp_loader.add(self.nav.land_wp(land_lat, land_long))

    def add_servo_dropping_wps(self):
        self.wp_loader.add(self.nav.servo_wp(is_open=True))

        delay_wp = self.nav.delay_wp(self.config_data["drop_close_delay"])
        self.wp_loader.add(delay_wp)

        self.wp_loader.add(self.nav.servo_wp(is_open=True))

    # extra logic idk

    def add_mission_waypoints(self, wp_list: list[list[float]]) -> bool:
        """Expected wp_list format:
        [ [lat, long, alt] ]
        """
        for i in range(len(wp_list)):
            lat, long, alt = wp_list[i]
            self.wp_loader.add(self.nav.nav_waypoint(lat, long, alt))

    def add_home_wp(self):
        msg = self.master.recv_match(type="GLOBAL_POSITION_INT", blocking=True)
        self.home_lat, self.home_long = (
            msg.lat / 1e7,
            msg.lon / 1e7,
        )  # ? todo shall we make this conditional

        self.wp_loader.add(self.nav.home_wp(self.home_lat, self.home_long))

    def before_mission_logic(self, fence_list: list[list[float]]):
        self.messages.upload_fence(fence_list)
        self.messages.clear_mission()
        self.add_home_wp()
        self.takeoff_sequence()

    def end_mission_logic(self):
        self.landingSequence()
        self.messages.upload_mission()
