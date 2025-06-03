from pymavlink import mavutil

def send_message(master: mavutil.mavudp, msg: str):
    """Send a MAVLink message to the UAV"""
    master.mav.statustext_send(
        mavutil.mavlink.MAV_SEVERITY_NOTICE,
        str(f"uav: {msg}").encode()[:50]
    )

if __name__ == '__main__':
    master = mavutil.mavlink_connection(DEVICE, baud=BAUDRATE)
    print("Trying to connect")
    master.wait_heartbeat()
    print("Connected. Sending message…")

    send_message(master, "start_recording")
