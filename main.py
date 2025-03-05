from modules.readers.Data_loader import DataLoader
from missions import mission1, mission2
from modules.readers.entries import uav_connect, config_choose, choose_mission

config_file = './files/data.json'
Data_obj = DataLoader(config_file)
uav_data= Data_obj.load_config()

connection_type = uav_connect()

config_choose(uav_data)

the_mission_index = choose_mission()



if the_mission_index == '1':
    mission1(connection_type,uav_data)
elif the_mission_index == '2':
    mission2(connection_type)




