Enter connection string with a drop down for available options
def uav_connect():
    print("choose the way of communication :")
    print("connection 1 is '127.0.0.1:14550' for local host")
    print("connection 2 is for network sharing")
    print("connection 3 for telemetry system")
    connection_type = input("Enter connection number:  ")


adjust initial bearing during takeoff