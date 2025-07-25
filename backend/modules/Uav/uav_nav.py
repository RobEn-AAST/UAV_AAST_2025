from pymavlink import mavutil, mavwp
from typing import Optional


class UavNav:
    def __init__(self, master: mavutil.mavlink_connection, config_data: dict) -> None:
        self.master = master
        self.config_data = config_data
        self.seq = -1

    def _create_waypoint(
        self,
        command: int,
        param1: float = 0,
        param2: float = 0,
        param3: float = 0,
        param4: float = 0,
        lat: float = 0,
        lon: float = 0,
        alt: float = 0,
    ):
        """Helper to create MAVLink waypoint messages with common parameters."""
        self.seq += 1
        return mavutil.mavlink.MAVLink_mission_item_message(
            self.master.target_system,
            self.master.target_component,
            self.seq,  # seq # todo attempt removing this
            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
            command,
            0,  # current
            1,  # auto continue
            param1,
            param2,
            param3,
            param4,
            lat,
            lon,
            alt,
        )

    def takeoff_wp(self, home_lat: float, home_lon: float):
        """Create takeoff waypoint at specified home position."""
        return self._create_waypoint(
            command=mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
            param1=self.config_data['flight']["take_off_angle"],
            lat=home_lat,
            lon=home_lon,
            alt=self.config_data['flight']["take_off_alt"],
        )

    def do_set_speed_wp(self, speed=10):
        """Create a DO_SET_SPEED (MAV_CMD_DO_CHANGE_SPEED) waypoint before loiter"""
        return self._create_waypoint(
            command=mavutil.mavlink.MAV_CMD_DO_CHANGE_SPEED,
            param1=0,    
            param2=speed, 
            param3=-1,  
            param4=0
        )

    def loiter_to_alt_wp(self, lat: float, lon: float):
        """Create loiter-to-altitude waypoint."""
        return self._create_waypoint(
            command=mavutil.mavlink.MAV_CMD_NAV_LOITER_TO_ALT,
            param2=self.config_data["flight"]["loiter_rad"],
            lat=lat,
            lon=lon,
            alt=self.config_data["flight"]["loiter_target_alt"],
        )

    def land_wp(self, lat: float, lon: float):
        """Create landing waypoint at specified coordinates."""
        return self._create_waypoint(
            command=mavutil.mavlink.MAV_CMD_NAV_LAND,
            lat=lat,
            lon=lon,
            alt=0,
        )

    def servo_wp(self, fl: str,is_open: bool):
        """Create servo control waypoint based on selected flight controller (fl)."""
        
        # Access the servo config dictionary for the given flight controller
        servo_config = self.config_data.get("servo_pwm", {}).get(fl, {})

        if not servo_config:
            raise ValueError(f"Flight controller '{fl}' not found in config_data['servo_pwm'].")

        pwm_value = servo_config["open"] if is_open else servo_config["close"]
        servo_no = servo_config["servo_no"]

        return self._create_waypoint(
            command=mavutil.mavlink.MAV_CMD_DO_SET_SERVO,
            param1=servo_no,
            param2=pwm_value,
        )

    def delay_wp(self, delay: float):
        """Create delay waypoint."""
        return self._create_waypoint(
            command=mavutil.mavlink.MAV_CMD_CONDITION_DELAY,
            param1=delay,
        )

    def nav_waypoint(self, lat: float, lon: float, alt: float):
        """Create navigation waypoint."""
        return self._create_waypoint(
            command=mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
            param2=25,
            lat=lat,
            lon=lon,
            alt=alt,
        )

    def home_wp(self, lat: float, lon: float):
        """Create SET_HOME waypoint."""
        return self._create_waypoint(
            command=mavutil.mavlink.MAV_CMD_DO_SET_HOME,
            param1=0,  # Use specified coordinates instead of current
            lat=lat,
            lon=lon,
        )
        
    def do_jump_wp(self, target_seq, repeat_count):
        return mavutil.mavlink.MAVLink_mission_item_message(
            self.master.target_system,
            self.master.target_component,
            seq=0,  # seq is set later by uploader or mission loader
            frame=mavutil.mavlink.MAV_FRAME_MISSION,
            command=mavutil.mavlink.MAV_CMD_DO_JUMP,
            current=0,
            autocontinue=1,
            param1=target_seq,
            param2=repeat_count,
            param3=0,
            param4=0,
            x=0,
            y=0,
            z=0
        )
