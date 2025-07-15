from pymavlink import mavutil
from backend.modules.Uav import Uav
import serial.tools.list_ports
import traceback

class ConnectionManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConnectionManager, cls).__new__(cls)
            cls._instance.uav = None
            cls._instance.connection_string = None
            cls._instance.baud_rate = None
            cls._instance.config_path = None
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
            # Save these values
            self.connection_string = connection_string
            self.config_path = config_path
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            self.uav = None
            return False

    def get_connection_info(self):
        return {
            "port_or_ip": getattr(self, "port_or_ip", None),
            "config_path": getattr(self, "config_path", None)
        }

    def disconnect_from_uav(self):
        if self.uav:
            result = self.uav.disconnect()
            if result:
                self.uav = None
                self.connection_string = None
                self.baud_rate = None
                self.config_path = None
            return result
        print("No UAV connection to disconnect")
        return False

    def is_connected(self):
        return self.uav is not None

    def get_available_ports(self):
        """
        Returns a list of available serial ports.
        """
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]

    def get_available_baud_rates(self):
        """
        Returns common baud rates as strings.
        """
        return ["9600", "19200", "38400", "57600", "115200"]

    def get_connection_info(self):
        """
        Return the last-used connection details for reuse in other pages.
        """
        return {
            "port_or_ip": self.connection_string,
            "baud_rate": self.baud_rate,
            "config_path": self.config_path
        }
