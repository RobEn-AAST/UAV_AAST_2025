from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit,
    QProgressBar, QMessageBox, QHBoxLayout
)
from PyQt6.QtCore import pyqtSignal, Qt, QTimer, QThread, QObject
from datetime import datetime
import os
import json
 
from backend.main import mission1
from backend.modules.Uav import Uav
from backend.modules.survey import camera_modules
from backend.modules.entries import uav_connect, config_choose, choose_mission, return_wp_list
from backend.modules.utils import apply_obs_avoidance


class Mission1Worker(QObject):
    log = pyqtSignal(str)
    progress = pyqtSignal(int)
    finished = pyqtSignal()

    def __init__(self):
        super().__init__()

    def run(self):
        try:
            self.log.emit("[INIT] Preparing mission parameters...")

            filepath = os.path.dirname(__file__)
            config_path = os.path.abspath(os.path.join(filepath, "..", "..", "files", "data.json"))

            self.log.emit("[INIT] Loading configuration file...")
            with open(config_path, 'r') as f:
                Json_data = json.load(f)

            self.log.emit("[INIT] Connecting to UAV...")
            connection_string = uav_connect(Json_data)
            uav = Uav(connection_string, config_path)

            self.log.emit("[CONFIG] Applying configuration and selecting mission...")
            config_choose(Json_data)
            mission_index = choose_mission()

            self.log.emit("[UPLOAD] Reading mission files and waypoints...")
            wp_list, fence_list, obs_list, payload_pos, survey_grid = return_wp_list(
                Json_data['waypoints_file_csv'],
                Json_data['fence_file_csv'],
                Json_data['obs_csv'],
                Json_data['payload_file_csv'],
                Json_data['survey_csv']
            )

            payload_pos[0].pop()
            for obs in obs_list:
                obs[-1] = Json_data['obs_raduies']
            for x in fence_list:
                x.pop()

            self.log.emit("[UPLOAD] Initializing camera configuration...")
            camera = camera_modules["sonya6000"]

            self.log.emit("[UPLOAD] Performing obstacle avoidance calculations...")
            wp_list = apply_obs_avoidance(wp_list, obs_list, uav.config_data["obs_safe_dist"])

            self.log.emit("[UPLOAD] Uploading waypoints to UAV...")
            self.progress.emit(30)

            self.log.emit("[MISSION] Starting Mission 1 execution...")
            success = mission1(
                original_mission=wp_list,
                payload_pos=payload_pos[0],
                fence_list=fence_list,
                survey_grid=survey_grid,
                camera=camera,
                uav=uav,
            )

            self.progress.emit(100)
            if success:
                self.log.emit("[COMPLETE] Mission 1 execution completed successfully.")
            else:
                self.log.emit("[FAILURE] Mission 1 execution failed.")

        except Exception as e:
            self.log.emit(f"[ERROR] {str(e)}")
        finally:
            self.finished.emit()


class MissionsPage(QWidget):
    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("RobEn Mission Control")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: grey; margin-bottom: 15px;")
        layout.addWidget(title)

        self.log_display = QTextEdit(self)
        self.log_display.setReadOnly(True)
        self.log_display.setPlaceholderText("Mission logs will appear here...")
        layout.addWidget(QLabel("Mission Logs:"))
        layout.addWidget(self.log_display)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(QLabel("Mission Progress:"))
        layout.addWidget(self.progress_bar)

        # Buttons
        self.btn_mission1 = QPushButton("Start Mission 1", self)
        self.btn_mission1.setStyleSheet("font-size: 18px; padding: 10px; background-color: #3498db; color: white;")
        self.btn_mission1.clicked.connect(self.run_mission1)
        layout.addWidget(self.btn_mission1)

        self.btn_mission2 = QPushButton("Start Mission 2", self)
        self.btn_mission2.setStyleSheet("font-size: 18px; padding: 10px; background-color: #3498db; color: white;")
        self.btn_mission2.clicked.connect(lambda: self.log_signal.emit("[INFO] Mission 2 not implemented yet."))
        layout.addWidget(self.btn_mission2)

        self.btn_manual_override = QPushButton("Manual Override", self)
        self.btn_manual_override.setStyleSheet("font-size: 18px; padding: 10px; background-color: red; color: white;")
        self.btn_manual_override.clicked.connect(self.manual_override)
        layout.addWidget(self.btn_manual_override)

        # Save/Clear logs layout
        log_buttons = QHBoxLayout()
        self.btn_save_logs = QPushButton("Save Logs", self)
        self.btn_save_logs.clicked.connect(self.save_logs)
        log_buttons.addWidget(self.btn_save_logs)

        self.btn_clear_logs = QPushButton("Clear Logs", self)
        self.btn_clear_logs.clicked.connect(self.clear_logs)
        log_buttons.addWidget(self.btn_clear_logs)

        layout.addLayout(log_buttons)

        self.log_signal.connect(self.update_log)
        self.progress_signal.connect(self.update_progress)

    def run_mission1(self):
        reply = QMessageBox.question(self, "Mission Confirmation",
                                     "Are you sure you want to start Mission 1?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.start_mission1_thread()

    def start_mission1_thread(self):
        self.worker = Mission1Worker()
        self.thread = QThread()

        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.log.connect(self.log_signal.emit)
        self.worker.progress.connect(self.progress_signal.emit)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def update_log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        full_message = f"[{timestamp}] {message}"
        self.log_display.append(full_message)

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def manual_override(self):
        self.log_signal.emit("[MANUAL] Manual Override Activated: Autopilot disengaged, switching to RC control.")

    def save_logs(self):
        filename = f"mission_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        try:
            with open(filename, 'w') as f:
                f.write(self.log_display.toPlainText())
            self.log_signal.emit(f"[LOG] Saved logs to {filename}")
        except Exception as e:
            self.log_signal.emit(f"[ERROR] Failed to save logs: {str(e)}")

    def clear_logs(self):
        self.log_display.clear()
        self.log_signal.emit("[LOG] Cleared log window.")
