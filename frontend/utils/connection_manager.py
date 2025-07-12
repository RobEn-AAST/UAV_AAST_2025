from pymavlink import mavutil
from backend.modules.Uav import Uav

class ConnectionManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConnectionManager, cls).__new__(cls)
            cls._instance.uav = None
        return cls._instance

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = ConnectionManager()
        return cls._instance

    def connect_to_uav(self, connection_string: str, config_path: str):
        if self.uav is not None:
            print("Already connected")
            return True
        try:
            self.uav = Uav(connection_string, config_path)
            print("Connected via Uav instance")
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            self.uav = None
            return False

    def disconnect_from_uav(self):
        if self.uav:
            result = self.uav.disconnect()
            if result:
                self.uav = None
            return result
        print("No UAV connection to disconnect")
        return False

    def is_connected(self):
        return self.uav is not None
