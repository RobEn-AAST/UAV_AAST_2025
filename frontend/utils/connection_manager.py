from pymavlink import mavutil, mavwp

class ConnectionManager:
    _instance = None
    _master = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConnectionManager, cls).__new__(cls)
        return cls._instance

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = ConnectionManager()
        return cls._instance

    @property
    def master(self):
        return self._master

    def connect_to_uav(self, ip_address: str):
        try:
            master = mavutil.mavlink_connection(ip_address)
            if not master.wait_heartbeat(timeout=15):
                raise ConnectionError(
                    "Failed to establish connection with UAV - no heartbeat received"
                )
            print("Connection established with UAV")

            self._master = master
            return True

        except Exception as e:
            print(f"Connection error: {str(e)}")
            self._master = None
            return False

    def is_connected(self):
        return self._master is not None