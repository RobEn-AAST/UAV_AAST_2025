from pymavlink import mavutil, mavwp


class MavWp:
    def __init__(self, master: mavutil.mavlink_connection, config_data: dict) -> None:
        self.master = master
        self.config_data = config_data

    def takeoff_wp(self, home_lat, home_long):
        takeoff_alt = self.config_data["take_off_alt"]
        takeoff_angle = self.config_data["take_off_angle"]

        return mavutil.mavlink.MAVLink_mission_item_message(
            self.master.target_system,
            self.master.target_component,
            0,  # seq (waypoint ID)
            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,  # frame id (global relative altitude)
            mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,  # mav_cmd (waypoint command)
            0,  # current (false)
            1,  # auto continue (false)
            takeoff_angle,
            0,  # unused
            0,  # unused
            float("nan"),  # yaw (nan for system default)
            home_lat,
            home_long,
            takeoff_alt,  # lat/lon/alt
        )

    def loiter_to_alt_wp(self, lat, long):
        loiter_target_alt = self.config_data["loiter_target_alt"]
        loiter_rad = self.config_data["loiter_rad"]

        return mavutil.mavlink.MAVLink_mission_item_message(
            self.master.target_system,
            self.master.target_component,
            0,  # seq
            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
            mavutil.mavlink.MAV_CMD_NAV_LOITER_TO_ALT,
            0,  # current
            1,  # auto continue
            0,  # leave circle once heading to next waypoint, 0 false
            loiter_rad,  # loiter radius
            0,  # unused
            0,  # xtrack, 0 to make it try to align better with next waypoint during the circle
            lat,  # lat
            long,  # long
            loiter_target_alt,  # alt
        )

    def land_wp(self, lat: float, long: float):
        """Creates a landing waypoint at the specified coordinates

        Args:
            x (float): Latitude for landing point
            y (float): Longitude for landing point

        Returns:
            MAVLink_mission_item_message: Landing waypoint
        """

        return mavutil.mavlink.MAVLink_mission_item_message(
            self.master.target_system,
            self.master.target_component,
            0,
            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
            mavutil.mavlink.MAV_CMD_NAV_LAND,
            0,  # current
            1,  # auto continue
            0,  # abort alt (0 to use system default)
            0,  # precision mode # todo look at this
            0,  # unuseed
            float("nan"),  # desired yaw (yaw for system defeault)
            lat,  # lat
            long,  # long
            0,  # altitude (always 0 for landing)
        )

    def servo_wp(self, is_open: bool) -> mavutil.mavlink.MAVLink_mission_item_message:
        """Creates a servo control waypoint

        Args:
            is_open (bool): Whether to open or close the servo

        Returns:
            MAVLink_mission_item_message: Servo control waypoint
        """
        return mavutil.mavlink.MAVLink_mission_item_message(
            self.master.target_system,
            self.master.target_component,
            0,
            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
            mavutil.mavlink.MAV_CMD_DO_SET_SERVO,
            0,  # current
            1,  # auto continue
            self.config_data["payload_servo_no"],  # servo instance
            self.config_data[
                "PAYLOAD_OPEN_PWM_VALUE" if is_open else "PAYLOAD_CLOSE_PWM_VALUE"
            ],  # Pwm
            0,  # unused
            0,  # unused
            0,  # unused
            0,  # unused
            0,  # unused
        )

    def delay_wp(self, delay: float) -> mavutil.mavlink.MAVLink_mission_item_message:
        """Creates a delay waypoint

        Args:
            delay (float): Delay time in seconds

        Returns:
            MAVLink_mission_item_message: Delay waypoint
        """
        return mavutil.mavlink.MAVLink_mission_item_message(
            self.master.target_system,
            self.master.target_component,
            0,
            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
            mavutil.mavlink.MAV_CMD_CONDITION_DELAY,
            0,  # current
            1,  # auto continue
            delay,
            0,  # unused
            0,  # unused
            0,  # unused
            0,  # unused
            0,  # unused
            0,  # unused
        )

    def nav_waypoint(self, lat: float, long: float, alt: float):
        """Creates a navigation waypoint at the specified coordinates and altitude

        Args:
            lat (float): Latitude
            long (float): Longitude
            alt (float): Altitude in meters (relative)

        Returns:
            MAVLink_mission_item_message: Navigation waypoint
        """
        return mavutil.mavlink.MAVLink_mission_item_message(
            self.master.target_system,
            self.master.target_component,
            0,  # seq (waypoint ID)
            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
            mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
            0,  # current (false)
            1,  # auto continue
            0,  # hold time (s), ignored for fixed wing
            0,  # acceptable radius (m)
            0,  # pass radius (m)
            float("nan"),  # yaw angle (nan to use system default)
            lat,
            long,
            alt,
        )

    def home_wp(self, lat: float, long: float):
        """Creates a SET_HOME waypoint at the specified coordinates

        Args:
            lat (float): Home latitude
            long (float): Home longitude

        Returns:
            MAVLink_mission_item_message: Set home waypoint
        """
        return mavutil.mavlink.MAVLink_mission_item_message(
            self.master.target_system,
            self.master.target_component,
            0,  # seq
            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
            mavutil.mavlink.MAV_CMD_DO_SET_HOME,
            0,  # current
            1,  # auto continue
            0,  # use current location (1 true, 0 use specified)
            0,  # roll (0/nan means not set, 0.01 means zero)
            0,  # pitch (0/nan means not set, 0.01 means zero)
            float("nan"),  # yaw (nan for default)
            lat,  # lat
            long,  # long
            0,  # altitude (0 for home position)
        )
