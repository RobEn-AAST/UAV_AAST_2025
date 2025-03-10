from modules.readers.Data_loader import DataLoader
from modules.missions import mission1, mission2
from modules.readers import config_choose

config_file = './files/data.json'
Data_obj = DataLoader(config_file)
uav_data = Data_obj.load_config()

config_choose(uav_data)

# with uav initialize connection

# now execute mission
mission1(connection_type, uav_data)