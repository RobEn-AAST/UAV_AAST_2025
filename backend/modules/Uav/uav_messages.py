import time

import pymavlink.dialects.v20.all as dialect
import pymavlink.mavwp as mavwp
from pymavlink import mavutil


class UavMessages:
    def __init__(
        self,
        master: dialect.MAVLink,
        config_data: dict,
        wp_loader: mavwp.MAVWPLoader,
    ) -> None:
        self.master = master
        self.config_data = config_data
        self.wp_loader = wp_loader

        self.timeout = 10

    # ============================================================
    # MISSION UPLOAD
    # ============================================================

    def upload_mission(self):
        """Upload mission using MAVLink mission protocol."""

        if not self.master:
            print("No MAVLink connection")
            return False

        if self.wp_loader.count() == 0:
            print("No waypoints to upload")
            return False

        count = self.wp_loader.count()

        print(f"Uploading {count} waypoints")

        # --------------------------------------------------------
        # Send mission count
        # --------------------------------------------------------

        self.master.mav.mission_count_send(
            self.master.target_system,
            self.master.target_component,
            count,
            0,  # MAV_MISSION_TYPE_MISSION
        )

        # --------------------------------------------------------
        # Handle mission requests
        # --------------------------------------------------------

        uploaded = 0

        while uploaded < count:

            req = self.master.recv_match(
                type=["MISSION_REQUEST", "MISSION_REQUEST_INT"],
                blocking=True,
                timeout=self.timeout,
            )

            if req is None:
                print("Timeout waiting for mission request")
                return False

            seq = req.seq

            if seq < 0 or seq >= count:
                print(f"Invalid mission request sequence: {seq}")
                continue

            wp = self.wp_loader.wp(seq)

            self.master.mav.send(wp)

            print(f"Sent waypoint {seq + 1}/{count}")

            uploaded += 1

        # --------------------------------------------------------
        # Wait for final acknowledgment
        # --------------------------------------------------------

        ack = self.master.recv_match(
            type="MISSION_ACK",
            blocking=True,
            timeout=self.timeout,
        )

        if ack is None:
            print("Timeout waiting for mission acknowledgment")
            return False

        if ack.type == mavutil.mavlink.MAV_MISSION_ACCEPTED:
            print("Mission upload successful")
            return True

        print(f"Mission upload failed. ACK type: {ack.type}")
        return False

    # ============================================================
    # CLEAR MISSION
    # ============================================================

    def clear_mission(self) -> bool:
        """Clear the current mission."""

        if not self.master:
            print("No MAVLink connection")
            return False

        print("Clearing mission...")

        self.master.mav.mission_clear_all_send(
            self.master.target_system,
            self.master.target_component,
        )

        ack = self.master.recv_match(
            type="MISSION_ACK",
            blocking=True,
            timeout=self.timeout,
        )

        if ack is None:
            print("Clear mission timeout")
            return False

        if ack.type == mavutil.mavlink.MAV_MISSION_ACCEPTED:
            print("Mission cleared successfully")
            return True

        print(f"Clear mission failed. ACK type: {ack.type}")
        return False

    # ============================================================
    # GET PARAMETER
    # ============================================================

    def _get_parameter(self, parameter_name: str):
        """Read a parameter from the flight controller."""

        param_id = parameter_name.encode("utf-8")

        request = dialect.MAVLink_param_request_read_message(
            target_system=self.master.target_system,
            target_component=self.master.target_component,
            param_id=param_id,
            param_index=-1,
        )

        self.master.mav.send(request)

        start_time = time.time()

        while time.time() - start_time < self.timeout:

            message = self.master.recv_match(
                type="PARAM_VALUE",
                blocking=True,
                timeout=1,
            )

            if message is None:
                continue

            try:
                received_name = message.param_id

                if isinstance(received_name, bytes):
                    received_name = received_name.decode(
                        "utf-8", errors="ignore"
                    )

                received_name = received_name.rstrip("\x00")

                if received_name == parameter_name:
                    return message.param_value

            except Exception as e:
                print(f"Error reading parameter {parameter_name}: {e}")

        print(f"Timeout waiting for parameter {parameter_name}")
        return None

    # ============================================================
    # SET PARAMETER
    # ============================================================

    def _set_parameter(
        self,
        parameter_name: str,
        value: float,
        retries: int = 3,
    ) -> bool:
        """Set a parameter and verify the returned value."""

        param_id = parameter_name.encode("utf-8")

        for attempt in range(1, retries + 1):

            print(
                f"[DEBUG] Setting {parameter_name} = {value} "
                f"(attempt {attempt}/{retries})"
            )

            message = dialect.MAVLink_param_set_message(
                target_system=self.master.target_system,
                target_component=self.master.target_component,
                param_id=param_id,
                param_value=float(value),
                param_type=dialect.MAV_PARAM_TYPE_REAL32,
            )

            self.master.mav.send(message)

            start_time = time.time()

            while time.time() - start_time < self.timeout:

                response = self.master.recv_match(
                    type="PARAM_VALUE",
                    blocking=True,
                    timeout=1,
                )

                if response is None:
                    continue

                try:
                    received_name = response.param_id

                    if isinstance(received_name, bytes):
                        received_name = received_name.decode(
                            "utf-8",
                            errors="ignore",
                        )

                    received_name = received_name.rstrip("\x00")

                    if received_name != parameter_name:
                        continue

                    received_value = response.param_value

                    # Parameters are returned as float32.
                    # Use a tolerance rather than exact comparison.
                    if abs(float(received_value) - float(value)) < 0.01:

                        print(
                            f"[SUCCESS] {parameter_name} "
                            f"set to {received_value}"
                        )

                        return True

                    print(
                        f"[WARNING] {parameter_name} returned "
                        f"{received_value}, expected {value}"
                    )

                    break

                except Exception as e:
                    print(
                        f"[ERROR] Error verifying "
                        f"{parameter_name}: {e}"
                    )
                    break

        print(f"[ERROR] Failed to set {parameter_name}")
        return False

    # ============================================================
    # UPLOAD FENCE
    # ============================================================

    def upload_fence(self, fence_list: list[list[float]]):
        """
        Upload a polygon geofence using the modern MAVLink mission protocol.

        Expected input:
            [
                [lat1, lon1],
                [lat2, lon2],
                [lat3, lon3],
                ...
            ]

        IMPORTANT:
            Do NOT add the home position as a fence vertex.
        """

        if not self.master:
            print("[ERROR] No MAVLink connection")
            return False

        # ============================================================
        # 1. VALIDATE FENCE POINTS
        # ============================================================

        valid_points = []

        for point in fence_list:

            if point is None or len(point) < 2:
                print(f"[WARNING] Invalid fence point: {point}")
                continue

            try:
                lat = float(point[0])
                lng = float(point[1])
            except (TypeError, ValueError):
                print(f"[WARNING] Invalid coordinates: {point}")
                continue

            if not (-90.0 <= lat <= 90.0):
                print(f"[WARNING] Invalid latitude: {lat}")
                continue

            if not (-180.0 <= lng <= 180.0):
                print(f"[WARNING] Invalid longitude: {lng}")
                continue

            valid_points.append([lat, lng])

        # Polygon needs at least 3 points
        if len(valid_points) < 3:
            print(
                f"[ERROR] A polygon fence requires at least 3 points. "
                f"Received {len(valid_points)}."
            )
            return False

        total = len(valid_points)

        print()
        print("========================================")
        print("        POLYGON FENCE UPLOAD")
        print("========================================")
        print(f"Total polygon vertices: {total}")

        for i, point in enumerate(valid_points):
            print(f"  {i}: [{point[0]}, {point[1]}]")

        print("========================================")
        print()

        # ============================================================
        # 2. WAIT FOR HEARTBEAT
        # ============================================================

        print("[DEBUG] Waiting for heartbeat...")

        try:
            self.master.wait_heartbeat(timeout=self.timeout)
        except Exception as e:
            print(f"[ERROR] Heartbeat timeout: {e}")
            return False

        print(
            "Connected to system:",
            self.master.target_system,
            ", component:",
            self.master.target_component,
        )

        # ============================================================
        # 3. MAKE SURE WE ARE USING MAVLINK 2
        # ============================================================

        print(
            "[DEBUG] MAVLink protocol:",
            "MAVLink 2" if self.master.mavlink20() else "MAVLink 1"
        )

        if not self.master.mavlink20():
            print()
            print("[ERROR] Fence upload requires MAVLink 2.")
            print(
                "[ERROR] ArduPilot requires MAVLink 2 for "
                "fence/rally mission transfer."
            )
            return False

        # ============================================================
        # 4. FENCE MISSION TYPE
        # ============================================================

        FENCE_MISSION_TYPE = dialect.MAV_MISSION_TYPE_FENCE

        print(
            f"[DEBUG] Mission type: FENCE ({FENCE_MISSION_TYPE})"
        )

        # ============================================================
        # 5. CLEAR EXISTING FENCE
        # ============================================================

        print("[DEBUG] Clearing existing fence...")

        try:

            self.master.mav.mission_clear_all_send(
                self.master.target_system,
                self.master.target_component,
                FENCE_MISSION_TYPE,
            )

            # Wait for ACK, but don't fail immediately if the
            # autopilot doesn't send one.
            clear_ack = self.master.recv_match(
                type="MISSION_ACK",
                blocking=True,
                timeout=3,
            )

            if clear_ack is not None:

                print(
                    f"[DEBUG] Fence clear ACK: "
                    f"{clear_ack.type}"
                )

                if clear_ack.type != dialect.MAV_MISSION_ACCEPTED:
                    print(
                        f"[WARNING] Fence clear returned "
                        f"ACK type {clear_ack.type}"
                    )

            else:
                print(
                    "[WARNING] No ACK received for fence clear"
                )

        except Exception as e:
            print(f"[WARNING] Could not clear old fence: {e}")

        # ============================================================
        # 6. SEND MISSION COUNT
        # ============================================================

        print(
            f"[DEBUG] Sending MISSION_COUNT = {total}"
        )

        self.master.mav.mission_count_send(
            self.master.target_system,
            self.master.target_component,
            total,
            FENCE_MISSION_TYPE,
        )

        # ============================================================
        # 7. RESPOND TO MISSION_REQUEST_INT
        # ============================================================

        uploaded = 0

        while uploaded < total:

            print(
                f"[DEBUG] Waiting for request "
                f"({uploaded + 1}/{total})..."
            )

            request = self.master.recv_match(
                type=[
                    "MISSION_REQUEST_INT",
                    "MISSION_REQUEST",
                ],
                blocking=True,
                timeout=self.timeout,
            )

            if request is None:

                print(
                    "[ERROR] Timeout waiting for "
                    "MISSION_REQUEST_INT"
                )

                return False

            seq = request.seq

            print(
                f"[DEBUG] Vehicle requested fence item "
                f"{seq}"
            )

            # --------------------------------------------------------
            # Validate requested sequence
            # --------------------------------------------------------

            if seq < 0 or seq >= total:

                print(
                    f"[ERROR] Vehicle requested invalid "
                    f"sequence {seq}"
                )

                return False

            lat = valid_points[seq][0]
            lng = valid_points[seq][1]

            # Convert degrees -> 1e7 integer format
            lat_int = int(round(lat * 10_000_000))
            lng_int = int(round(lng * 10_000_000))

            print(
                f"[DEBUG] Sending fence vertex {seq}: "
                f"[{lat}, {lng}]"
            )

            # ========================================================
            # POLYGON INCLUSION VERTEX
            # ========================================================

            self.master.mav.mission_item_int_send(
                self.master.target_system,
                self.master.target_component,

                # sequence
                seq,

                # frame
                dialect.MAV_FRAME_GLOBAL,

                # command
                dialect.MAV_CMD_NAV_FENCE_POLYGON_VERTEX_INCLUSION,

                # current
                0,

                # autocontinue
                1,

                # param1 = total number of vertices
                float(total),

                # param2 = inclusion group
                0.0,

                # param3
                0.0,

                # param4
                0.0,

                # x = latitude * 1e7
                lat_int,

                # y = longitude * 1e7
                lng_int,

                # z
                0.0,

                # mission type = FENCE
                FENCE_MISSION_TYPE,
            )

            print(
                f"[SUCCESS] Sent fence vertex "
                f"{seq + 1}/{total}"
            )

            uploaded += 1

        # ============================================================
        # 8. WAIT FOR FINAL MISSION ACK
        # ============================================================

        print()
        print("[DEBUG] Waiting for final fence ACK...")

        ack = self.master.recv_match(
            type="MISSION_ACK",
            blocking=True,
            timeout=self.timeout,
        )

        if ack is None:

            print(
                "[ERROR] Timeout waiting for final "
                "fence MISSION_ACK"
            )

            return False

        print(
            f"[DEBUG] Fence MISSION_ACK type: "
            f"{ack.type}"
        )

        if ack.type != dialect.MAV_MISSION_ACCEPTED:

            print(
                f"[ERROR] Fence upload rejected. "
                f"ACK type = {ack.type}"
            )

            return False

        print(
            "[SUCCESS] Fence uploaded successfully "
            "to the flight controller"
        )

        # ============================================================
        # 9. ENABLE POLYGON FENCE TYPE
        # ============================================================

        print("[DEBUG] Checking FENCE_TYPE...")

        current_fence_type = self._get_parameter(
            "FENCE_TYPE"
        )

        if current_fence_type is None:

            print(
                "[WARNING] Could not read FENCE_TYPE"
            )

        else:

            current_fence_type = int(current_fence_type)

            print(
                f"[DEBUG] Current FENCE_TYPE: "
                f"{current_fence_type}"
            )

            # Bit 2 = polygon/circle inclusion/exclusion
            POLYGON_BIT = 1 << 2

            new_fence_type = (
                current_fence_type | POLYGON_BIT
            )

            if new_fence_type != current_fence_type:

                print(
                    f"[DEBUG] Enabling polygon fence type: "
                    f"{current_fence_type} -> "
                    f"{new_fence_type}"
                )

                if self._set_parameter(
                    "FENCE_TYPE",
                    new_fence_type,
                ):
                    print(
                        "[SUCCESS] Polygon fence type enabled"
                    )
                else:
                    print(
                        "[WARNING] Could not enable "
                        "polygon fence type"
                    )

            else:

                print(
                    "[DEBUG] Polygon fence type already enabled"
                )

        # ============================================================
        # 10. ENABLE FENCE
        # ============================================================

        print("[DEBUG] Enabling geofence...")

        enable_message = dialect.MAVLink_command_long_message(
            target_system=self.master.target_system,
            target_component=self.master.target_component,

            command=dialect.MAV_CMD_DO_FENCE_ENABLE,

            confirmation=0,

            # 1 = enable
            param1=1,

            param2=0,
            param3=0,
            param4=0,
            param5=0,
            param6=0,
            param7=0,
        )

        self.master.mav.send(enable_message)

        enable_ack = self.master.recv_match(
            type="COMMAND_ACK",
            blocking=True,
            timeout=self.timeout,
        )

        if enable_ack is not None:

            print(
                f"[DEBUG] Fence enable ACK: "
                f"{enable_ack.result}"
            )

            if enable_ack.result != dialect.MAV_RESULT_ACCEPTED:

                print(
                    f"[WARNING] Fence enable returned "
                    f"result {enable_ack.result}"
                )

        else:

            print(
                "[WARNING] No COMMAND_ACK received "
                "for fence enable"
            )

        # ============================================================
        # 11. VERIFY FENCE_TOTAL
        # ============================================================

        fence_total = self._get_parameter(
            "FENCE_TOTAL"
        )

        if fence_total is not None:

            print(
                f"[DEBUG] Flight controller reports "
                f"FENCE_TOTAL = {int(fence_total)}"
            )

            if int(fence_total) == total:

                print(
                    "[SUCCESS] FENCE_TOTAL matches "
                    "uploaded polygon"
                )

            else:

                print(
                    f"[WARNING] Expected FENCE_TOTAL = "
                    f"{total}, but vehicle reports "
                    f"{int(fence_total)}"
                )

        # ============================================================
        # DONE
        # ============================================================

        print()
        print("========================================")
        print("       FENCE UPLOAD COMPLETE")
        print("========================================")
        print(f"Uploaded vertices: {total}")
        print("Fence type: Polygon Inclusion")
        print("Fence enabled: Yes")
        print("========================================")
        print()

        return True