import json
import os
import sys
from datetime import datetime
from PyQt6.QtCore import pyqtSignal, Qt, QThread, QObject
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit,
    QProgressBar, QMessageBox, QHBoxLayout, QFileDialog
)

# Add backend path to sys.path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Now import backend modules
from backend.modules.missions import mission1, mission2
from backend.modules.Uav import Uav
from backend.modules.survey import camera_modules
from backend.modules.entries import uav_connect, config_choose, choose_mission, return_wp_list
from backend.modules.utils import apply_obs_avoidance


class Mission1Worker(QObject):
    log = pyqtSignal(str)
    progress = pyqtSignal(int)
    finished = pyqtSignal()

    def run(self):
        try:
            self.log.emit("[INIT] Preparing mission 1 parameters...")
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


class Mission2Worker(QObject):
    log = pyqtSignal(str)
    progress = pyqtSignal(int)
    finished = pyqtSignal()

    def run(self):
        try:
            self.log.emit("[INIT] Preparing Mission 2 parameters...")
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

            repeat_count = Json_data.get("do_jump_repeat_count", 3)

            self.log.emit("[UPLOAD] Uploading waypoints to UAV for Mission 2...")
            self.progress.emit(30)

            self.log.emit("[MISSION] Starting Mission 2 execution...")
            mission2(
                original_mission=wp_list,
                payload_pos=payload_pos[0],
                fence_list=fence_list,
                survey_grid=survey_grid,
                camera=camera,
                uav=uav,
                repeat_count=repeat_count
            )

            self.progress.emit(100)
            self.log.emit("[COMPLETE] Mission 2 execution completed.")

        except Exception as e:
            self.log.emit(f"[ERROR] {str(e)}")
        finally:
            self.finished.emit()


class MissionsPage(QWidget):
    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.mission_running = False
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("Mission Control")
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
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #555;
                border-radius: 5px;
                background-color: #222;
                color: white;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                width: 20px;
            }
        """)

        layout.addWidget(QLabel("Mission Progress:"))
        layout.addWidget(self.progress_bar)

        self.btn_mission1 = QPushButton("Start Mission 1", self)
        self.btn_mission1.setStyleSheet("font-size: 18px; padding: 10px; background-color: #3498db; color: white;")
        self.btn_mission1.clicked.connect(self.run_mission1)
        layout.addWidget(self.btn_mission1)

        self.btn_mission2 = QPushButton("Start Mission 2", self)
        self.btn_mission2.setStyleSheet("font-size: 18px; padding: 10px; background-color: #3498db; color: white;")
        self.btn_mission2.clicked.connect(self.run_mission2)
        layout.addWidget(self.btn_mission2)

        self.btn_manual_override = QPushButton("Manual Override", self)
        self.btn_manual_override.setEnabled(False)
        self.btn_manual_override.setStyleSheet("font-size: 18px; padding: 10px; background-color: grey; color: white;")
        self.btn_manual_override.clicked.connect(self.manual_override)
        layout.addWidget(self.btn_manual_override)

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
        if self.mission_running:
            reply = QMessageBox.warning(
                self, "Mission Already Running",
                "Another mission is in progress.\nDo you want to stop it and start Mission 1?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
            self.manual_override()

        reply = QMessageBox.question(self, "Mission Confirmation",
                                     "Are you sure you want to start Mission 1?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.start_mission1_thread()

    def run_mission2(self):
        if self.mission_running:
            reply = QMessageBox.warning(
                self, "Mission Already Running",
                "Another mission is in progress.\nDo you want to stop it and start Mission 2?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
            self.manual_override()

        reply = QMessageBox.question(self, "Mission Confirmation",
                                     "Are you sure you want to start Mission 2?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.start_mission2_thread()

    def start_mission1_thread(self):
        self.mission1_worker = Mission1Worker()
        self.mission1_thread = QThread()
        self.mission1_worker.moveToThread(self.mission1_thread)
        self.mission1_thread.started.connect(self.mission1_worker.run)
        self.mission1_worker.log.connect(self.log_signal.emit)
        self.mission1_worker.progress.connect(self.progress_signal.emit)
        self.mission1_worker.finished.connect(self.mission1_thread.quit)
        self.mission1_worker.finished.connect(self.mission1_worker.deleteLater)
        self.mission1_thread.finished.connect(self.mission1_thread.deleteLater)
        self.mission1_thread.start()

        self.mission_running = True
        self.update_manual_override_state()

    def start_mission2_thread(self):
        self.mission2_worker = Mission2Worker()
        self.mission2_thread = QThread()
        self.mission2_worker.moveToThread(self.mission2_thread)
        self.mission2_thread.started.connect(self.mission2_worker.run)
        self.mission2_worker.log.connect(self.log_signal.emit)
        self.mission2_worker.progress.connect(self.progress_signal.emit)
        self.mission2_worker.finished.connect(self.mission2_thread.quit)
        self.mission2_worker.finished.connect(self.mission2_worker.deleteLater)
        self.mission2_thread.finished.connect(self.mission2_thread.deleteLater)
        self.mission2_thread.start()

        self.mission_running = True
        self.update_manual_override_state()

    def manual_override(self):
        if self.mission_running:
            if hasattr(self, 'mission1_thread') and self.mission1_thread.isRunning():
                self.mission1_thread.quit()
            if hasattr(self, 'mission2_thread') and self.mission2_thread.isRunning():
                self.mission2_thread.quit()
            self.log_signal.emit("[MANUAL] Manual Override Activated: Mission halted, pilot has manual control.")
            self.mission_running = False
            self.update_manual_override_state()
        else:
            self.log_signal.emit("[MANUAL] Manual Override pressed, but no mission is currently active.")

    def update_manual_override_state(self):
        if self.mission_running:
            self.btn_manual_override.setEnabled(True)
            self.btn_manual_override.setStyleSheet("font-size: 18px; padding: 10px; background-color: red; color: white;")
        else:
            self.btn_manual_override.setEnabled(False)
            self.btn_manual_override.setStyleSheet("font-size: 18px; padding: 10px; background-color: grey; color: white;")

    def update_log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        full_message = f"[{timestamp}] {message}"
        self.log_display.append(full_message)
        scrollbar = self.log_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    from PyQt6.QtWidgets import QFileDialog

    def save_logs(self):
        default_filename = f"mission_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Mission Log",
            default_filename,
            "Text Files (*.txt);;All Files (*)"
        )

        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write(self.log_display.toPlainText())
                self.log_signal.emit(f"[LOG] Saved logs to {file_path}")
            except Exception as e:
                self.log_signal.emit(f"[ERROR] Failed to save logs: {str(e)}")
        else:
            self.log_signal.emit("[LOG] Save cancelled.")

    def clear_logs(self):
        self.log_display.clear()
        self.log_signal.emit("[LOG] Cleared log window.")

