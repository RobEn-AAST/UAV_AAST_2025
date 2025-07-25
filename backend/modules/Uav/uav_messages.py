import pymavlink.dialects.v20.all as dialect
import pymavlink.mavwp as mavwp
from pymavlink import mavutil

import time


class UavMessages:
    def __init__(
        self, master: dialect.MAVLink, config_data: dict, wp_loader: mavwp.MAVWPLoader
    ) -> None:
        self.master = master
        self.config_data = config_data
        self.wp_loader = wp_loader

        self.timeout = 10

    def upload_mission(self):
        """Upload mission using proper MAVLink protocol sequence"""
        if not self.master or self.wp_loader.count() == 0:
            print("No points to upload or no connection")
            return False

        print(f"Uploading {self.wp_loader.count()} waypoints")

        # Send mission count first
        self.master.mav.mission_count_send(
            self.master.target_system,
            self.master.target_component,
            self.wp_loader.count(),
            0,  # Mission type (0 = mission)
        )

        # try:
        # Handle mission items requests
        while True:
            # Wait for mission request (new or retry)
            req = self.master.recv_match(
                type="MISSION_REQUEST", blocking=True, timeout=self.timeout
            )

            # Get requested waypoint from loader
            wp = self.wp_loader.wp(req.seq)

            # Send the waypoint
            self.master.mav.send(wp)
            print(f"Sent waypoint {req.seq + 1}/{self.wp_loader.count()}")

            # Check if we've sent all items
            if req.seq == self.wp_loader.count() - 1:
                break

        # Wait for final acknowledgment
        ack = self.master.recv_match(
            type="MISSION_ACK", blocking=True, timeout=self.timeout
        )

        if ack.type == mavutil.mavlink.MAV_MISSION_ACCEPTED:
            print("Mission upload successful")
            return True

        print(f"Upload failed: {ack.type}")
        return False

        # except Exception as e:
        #     print(f"Upload failed: {str(e)}")
        #     return False

    def clear_mission(self) -> bool:
        """Clear current mission with timeout handling"""

        print("Clearing mission...")
        self.master.mav.mission_clear_all_send(
            self.master.target_system, self.master.target_component
        )

        try:
            ack = self.master.recv_match(
                type="MISSION_ACK", blocking=True, timeout=self.timeout
            )
            if ack.type == mavutil.mavlink.MAV_MISSION_ACCEPTED:
                print("Mission cleared successfully")
                return True
            print(f"Clear failed: {ack.type}")
            return False
        except Exception as e:
            print(f"Clear mission timeout: {str(e)}")
            return False

    def upload_fence(self, fence_list: list[list[float]],given_lat,given_long):
        """expected format: [[lat, long]]"""
        if len(fence_list) == 0:
            # todo add steps to skip fence aka parameters logic stuff
            return

        lat, long = given_lat,given_long
        fence_list.insert(0, [lat, long])

        FENCE_TOTAL = "FENCE_TOTAL".encode(encoding="utf-8")
        FENCE_ACTION = "FENCE_ACTION".encode(encoding="utf8")
        FENCE_ENABLE = "FENCE_ENABLE".encode(encoding="utf-8")
        PARAM_INDEX = -1

        self.master.wait_heartbeat()

        print(
            "Connected to system:",
            self.master.target_system,
            ", component:",
            self.master.target_component,
        )

        # making a request to recv message

        message = dialect.MAVLink_param_request_read_message(
            target_system=self.master.target_system,
            target_component=self.master.target_component,
            param_id=FENCE_ACTION,
            param_index=PARAM_INDEX,
        )

        self.master.mav.send(message)

        while True:
            # wait for PARAM_VALUE message
            message = self.master.recv_match(
                type=dialect.MAVLink_param_value_message.msgname, blocking=True
            )

            # convert the message to dictionary
            message = message.to_dict()

            # make sure this parameter value message is for FENCE_ACTION
            if message["param_id"] == "FENCE_ACTION":
                # get the original fence action parameter from vehicle

                fence_action_original = int(message["param_value"])

                # break the loop
                break
        # debug parameter value
        print("FENCE_ACTION parameter original:", fence_action_original)

        # now we want to set paramter FENCE_ACTION

        while True:
            message = dialect.MAVLink_param_set_message(
                target_system=self.master.target_system,
                target_component=self.master.target_component,
                param_id=FENCE_ACTION,
                param_value=0,
                param_type=dialect.MAV_PARAM_TYPE_REAL32,
            )

            # now we are setting the parameter

            self.master.mav.send(message)

            # now we are going to check that the parameter have been set successfully

            message = self.master.recv_match(
                type=dialect.MAVLink_param_value_message.msgname, blocking=True
            )

            message = message.to_dict()

            if message["param_id"] == "FENCE_ACTION":
                fence_action_original = int(message["param_value"])

                print("FENCE_ACTION parameter now is :", fence_action_original)

                break

            else:
                print("Failed to reset FENCE_ACTION to 0, trying again")

        # now we will set FENCE_TOTAL

        while True:
            message = dialect.MAVLink_param_set_message(
                target_system=self.master.target_system,
                target_component=self.master.target_component,
                param_id=FENCE_TOTAL,
                param_value=0,
                param_type=dialect.MAV_PARAM_TYPE_REAL32,
            )

            self.master.mav.send(message)

            message = self.master.recv_match(
                type=dialect.MAVLink_param_value_message.msgname, blocking=True
            )

            message = message.to_dict()

            if message["param_id"] == "FENCE_TOTAL":
                # make sure that parameter value set successfully
                if int(message["param_value"]) == 0:
                    print("FENCE_TOTAL reset to 0 successfully")

                    # break the loop
                    break

                # should send param reset message again
                else:
                    print("Failed to reset FENCE_TOTAL to 0")

        while True:
            # create parameter set message
            message = dialect.MAVLink_param_set_message(
                target_system=self.master.target_system,
                target_component=self.master.target_component,
                param_id=FENCE_TOTAL,
                param_value=len(fence_list),
                param_type=dialect.MAV_PARAM_TYPE_REAL32,
            )

            # send parameter set message to the vehicle
            self.master.mav.send(message)

            # wait for PARAM_VALUE message
            message = self.master.recv_match(
                type=dialect.MAVLink_param_value_message.msgname, blocking=True
            )

            # convert the message to dictionary
            message = message.to_dict()

            # make sure this parameter value message is for FENCE_TOTAL
            if message["param_id"] == "FENCE_TOTAL":
                # make sure that parameter value set successfully
                if int(message["param_value"]) == len(fence_list):
                    print("FENCE_TOTAL set to {0} successfully".format(len(fence_list)))

                    # break the loop
                    break

                # should send param set message again
                else:
                    print("Failed to set FENCE_TOTAL to {0}".format(len(fence_list)))

        idx = 0

        while idx < len(fence_list):
            message = dialect.MAVLink_fence_point_message(
                target_system=self.master.target_system,
                target_component=self.master.target_component,
                idx=idx,
                count=len(fence_list),
                lat=fence_list[idx][0],
                lng=fence_list[idx][1],
            )

            # send this message to vehicle
            self.master.mav.send(message)

            # create FENCE_FETCH_POINT message
            message = dialect.MAVLink_fence_fetch_point_message(
                target_system=self.master.target_system,
                target_component=self.master.target_component,
                idx=idx,
            )

            # send this message to vehicle
            self.master.mav.send(message)

            # wait until receive FENCE_POINT message
            message = self.master.recv_match(
                type=dialect.MAVLink_fence_point_message.msgname, blocking=True
            )

            # convert the message to dictionary
            message = message.to_dict()

            # get the latitude and longitude from the fence item
            latitude = message["lat"]
            longitude = message["lng"]

            # check the fence point is uploaded successfully
            if latitude != 0.0 and longitude != 0:
                # increase the index of the fence item
                idx += 1

                print(f"point {idx} uploaded successfully")

        print("All the fence items uploaded successfully")

        while True:
            # create parameter set message
            message = dialect.MAVLink_param_set_message(
                target_system=self.master.target_system,
                target_component=self.master.target_component,
                param_id=FENCE_ACTION,
                param_value=fence_action_original,
                param_type=dialect.MAV_PARAM_TYPE_REAL32,
            )

            # send parameter set message to the vehicle
            self.master.mav.send(message)

            # wait for PARAM_VALUE message
            message = self.master.recv_match(
                type=dialect.MAVLink_param_value_message.msgname, blocking=True
            )

            # convert the message to dictionary
            message = message.to_dict()

            # make sure this parameter value message is for FENCE_ACTION
            if message["param_id"] == "FENCE_ACTION":
                # make sure that parameter value set successfully
                if int(message["param_value"]) == fence_action_original:
                    print(
                        "FENCE_ACTION set to original value {0} successfully".format(
                            fence_action_original
                        )
                    )

                    # break the loop
                    break

                # should send param set message again
                else:
                    print(
                        "Failed to set FENCE_ACTION to original value {0} ".format(
                            fence_action_original
                        )
                    )
        message = dialect.MAVLink_command_long_message(
            target_system=self.master.target_system,
            target_component=self.master.target_component,
            command=dialect.MAV_CMD_DO_FENCE_ENABLE,
            confirmation=0,
            param1=1,
            param2=0,
            param3=0,
            param4=0,
            param5=0,
            param6=0,
            param7=0,
        )

        # send the message to the vehicle
        self.master.mav.send(message)
