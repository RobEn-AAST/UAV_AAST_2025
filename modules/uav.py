import time
import pymavlink.mavutil as utility
import pymavlink.dialects.v20.all as dialect
import csv
import json
from pymavlink import mavutil, mavwp
from modules.utils import new_waypoint, calc_drop_loc, get_bearing

from modules.uav_nav import uav_nav
from modules.uav_messages import uav_messages
from modules.drop_location_calc import payload
from modules.Data_loader import DataLoader
from modules.survey import Survey


class uav:
    def __init__(self, vehicle, config_data) -> None:
        self.vehicle = vehicle
        self.config_data = config_data
        self.nav = uav_nav(self.config_data, self.vehicle )
        self.messages = uav_messages (self.config_data,self.vehicle,)
        self.survey=Survey(self.config_data)

    def upload_fence(self):
        self.messages.upload_fence()

    def clear_mission(self):
        self.messages.clear_mission()

    def takeoff_sequence(self):
        self.nav.takeoff_sequence()

    def landingSequence(self):
        self.nav.landingSequence()

    def close_servo_wp(self):
        self.nav.close_servo_wp()

    def open_servo_wp(self):
        self.nav.open_servo_wp()

    def add_delay_wp(self):
        self.nav.add_delay_wp()

    def add_mission_waypoints(self):
        self.nav.add_mission_waypoints()

    def upload_missions(self):
        self.nav.upload_missions()

    def add_home_wp(self):
        self.nav.add_home_wp()

    def add_drop_location_wp(self):
        self.nav.add_drop_location_wp()

    def payload_seq_2(self):
        self.nav.payload_seq_2()

    def do_survey(self):
        self.nav.do_survey()
    def do_obs_avoid(self):
        self.nav.do_obs_avoid()
