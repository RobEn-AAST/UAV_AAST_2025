
class Survey:
    def __init__(self,config_data):
        self.config_data=config_data

    def Calculate_GSD(self):
        gsd=(self.config_data["survey_alt"]*self.config_data["Sensor_width"])/(self.config_data["focal_length_max"]*self.config_data["image_width"])
        return gsd
