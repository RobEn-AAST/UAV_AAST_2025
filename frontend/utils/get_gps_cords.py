from pymavlink import mavutil
from pymavlink.dialects.v20.common import MAVLink_set_gps_global_origin_message



master = mavutil.mavlink_connection("172.30.64.1:14550")


while True:
    # Wait for the GLOBAL_POSITION_INT message
    message = master.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
    latitude = message.lat / 1e7  # Convert to degrees
    longitude = message.lon / 1e7  # Convert to degrees
    altitude = message.alt / 1000  # Convert to meters
    print(f"Latitude: {latitude}°")
    print(f"Longitude: {longitude}°")
    print(f"Altitude: {altitude} meters")
