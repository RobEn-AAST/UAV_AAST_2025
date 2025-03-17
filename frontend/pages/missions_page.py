from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit, QProgressBar, QMessageBox
from PyQt6.QtCore import pyqtSignal, Qt, QTimer


class MissionsPage(QWidget):
    log_signal = pyqtSignal(str)  # Signal to update logs
    progress_signal = pyqtSignal(int)  # Signal to update progress bar

    def __init__(self, start_mission1=None, start_mission2=None):  # ✅ Allow None
        super().__init__()

        # ✅ Set default empty functions if None is passed
        self.start_mission1 = start_mission1 if start_mission1 else self.default_mission
        self.start_mission2 = start_mission2 if start_mission2 else self.default_mission

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # ✅ Title
        title = QLabel("RobEn Mission Control")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: grey; margin-bottom: 15px;")
        layout.addWidget(title)

        # ✅ Mission status log
        self.log_display = QTextEdit(self)
        self.log_display.setReadOnly(True)
        self.log_display.setPlaceholderText("Mission logs will appear here...")
        layout.addWidget(QLabel("Mission Logs:"))
        layout.addWidget(self.log_display)

        # ✅ Progress Bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(QLabel("Mission Progress:"))
        layout.addWidget(self.progress_bar)

        # ✅ Buttons to start missions
        self.btn_mission1 = QPushButton("✈️ Start Mission 1", self)
        self.btn_mission1.setStyleSheet("font-size: 18px; padding: 10px;")
        self.btn_mission1.clicked.connect(lambda: self.confirm_mission(self.start_mission1))
        layout.addWidget(self.btn_mission1)

        self.btn_mission2 = QPushButton("🛫 Start Mission 2", self)
        self.btn_mission2.setStyleSheet("font-size: 18px; padding: 10px;")
        self.btn_mission2.clicked.connect(lambda: self.confirm_mission(self.start_mission2))
        layout.addWidget(self.btn_mission2)

        # ✅ Emergency Manual Override Button
        self.btn_manual_override = QPushButton("🎮 Manual Override", self)
        self.btn_manual_override.setStyleSheet("font-size: 18px; padding: 10px; background-color: red; color: white;")
        self.btn_manual_override.clicked.connect(self.manual_override)
        layout.addWidget(self.btn_manual_override)

        # Connect signals
        self.log_signal.connect(self.update_log)
        self.progress_signal.connect(self.update_progress)

    def default_mission(self, log_signal):
        """Default function if no mission function is provided."""
        log_signal.emit("No mission function assigned.")

    def confirm_mission(self, mission_func):
        """Show confirmation popup before starting mission."""
        reply = QMessageBox.question(self, "Mission Confirmation",
                                     "Are you sure you want to start this mission?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            mission_func(self.log_signal)

    def update_log(self, message):
        """Update log display and show a notification popup (clears after 8s)."""
        self.log_display.append(message)
        self.show_popup("Mission Status", message)

    def update_progress(self, value):
        """Update progress bar based on UAV status."""
        self.progress_bar.setValue(value)

    def show_popup(self, title, message):
        """Display a popup notification with mission status (clears after 8s)."""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.show()

        # ✅ Auto-close notification after 8 seconds
        QTimer.singleShot(8000, msg_box.close)

    def manual_override(self):
        """Handle emergency manual override."""
        self.log_signal.emit("⚠️ Manual Override Activated: Autopilot disengaged, switching to RC control!")

