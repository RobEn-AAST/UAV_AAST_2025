from pymavlink import mavutil
from flask import Flask, render_template, request, jsonify
from modules.Data_loader import DataLoader
from modules.mission1 import mission1
from modules.mission2 import mission2
from modules.entries import uav_connect, config_choose, choose_mission

app = Flask(__name__)

config_file = 'C:/Users/Mostafa/PycharmProjects/fixed wing pymavlink/files/data.json'
Data_obj = DataLoader(config_file)
uav_data= Data_obj.load_config()

connection_type = uav_connect()

config_choose(uav_data)

the_mission_index = choose_mission()



if the_mission_index == '1':
    mission1(connection_type,uav_data)
elif the_mission_index == '2':
    mission2(connection_type)




