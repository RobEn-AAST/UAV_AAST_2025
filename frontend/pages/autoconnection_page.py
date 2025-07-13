import os
import subprocess
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QPushButton, QTextEdit
)
from PyQt6.QtGui import QFont, QTextCursor
from PyQt6.QtCore import Qt

from utils.connection_manager import ConnectionManager


class Terminal(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setFont(QFont("Consolas", 12))
        self.setStyleSheet("background-color: black; color: lime;")
        self.setCursorWidth(2)

    def append_text(self, text: str):
        self.moveCursor(QTextCursor.MoveOperation.End)
        self.insertPlainText(text + "\n")
        self.moveCursor(QTextCursor.MoveOperation.End)
        self.ensureCursorVisible()


class AutoConnectionPage(QWidget):
    def __init__(self):
        super().__init__()
        self.connection_manager = ConnectionManager.get_instance()
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.script_path = os.path.join(project_root, "utils", "autoconnect.py")
        self.process = None
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # Header label
        title = QLabel("Ground Control Station Setup")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: grey; margin-bottom: 15px;")
        main_layout.addWidget(title)

        # Communication type section with Scan button on the right
        top_layout = QHBoxLayout()
        comm_label = QLabel("Communication Type:")
        self.comm_combo = QComboBox()
        self.comm_combo.addItems(["Serial", "UDP"])
        self.comm_combo.setCurrentText("UDP")  # UDP as default
        self.comm_combo.currentTextChanged.connect(self.on_comm_type_changed)

        top_layout.addWidget(comm_label)
        top_layout.addWidget(self.comm_combo)
        top_layout.addStretch()

        # Scan button with styling
        self.scan_btn = QPushButton("Scan for IPs")
        self.scan_btn.setFixedWidth(140)
        self.scan_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        self.scan_btn.clicked.connect(self.run_scan_script)

        top_layout.addWidget(self.scan_btn)
        main_layout.addLayout(top_layout)

        # Serial options container below
        self.serial_options_layout = QHBoxLayout()

        port_label = QLabel("Port:")
        self.port_combo = QComboBox()
        self.port_combo.setMinimumWidth(120)
        self.serial_options_layout.addWidget(port_label)
        self.serial_options_layout.addWidget(self.port_combo)

        baud_label = QLabel("Baud Rate:")
        self.baud_combo = QComboBox()
        self.baud_combo.setMinimumWidth(120)
        self.serial_options_layout.addWidget(baud_label)
        self.serial_options_layout.addWidget(self.baud_combo)

        self.serial_options_layout.addStretch()
        main_layout.addLayout(self.serial_options_layout)

        main_layout.addSpacing(20)  # space before terminal

        # Terminal widget
        self.terminal = Terminal()
        main_layout.addWidget(self.terminal, stretch=1)

        # Initialize combos
        self.load_ports(self.comm_combo.currentText())
        self.load_baud_rates()
        self.on_comm_type_changed(self.comm_combo.currentText())


    def load_ports(self, comm_type):
        self.port_combo.clear()
        cm = self.connection_manager
        if comm_type == "Serial":
            ports = cm.get_available_ports()
            self.port_combo.addItems(ports)
        elif comm_type == "UDP":
            self.port_combo.addItems(["14550", "14551", "14552"])

    def load_baud_rates(self):
        cm = self.connection_manager
        rates = cm.get_available_baud_rates()
        self.baud_combo.clear()
        self.baud_combo.addItems(rates)

    def on_comm_type_changed(self, comm_type):
        self.load_ports(comm_type)

        if comm_type == "Serial":
            for i in range(self.serial_options_layout.count()):
                widget = self.serial_options_layout.itemAt(i).widget()
                if widget:
                    widget.setVisible(True)
        elif comm_type == "UDP":
            from PyQt6.QtWidgets import QLabel
            for i in range(self.serial_options_layout.count()):
                widget = self.serial_options_layout.itemAt(i).widget()
                if widget:
                    if widget == self.port_combo or (isinstance(widget, QLabel) and widget.text() == "Port:"):
                        widget.setVisible(True)
                    elif widget == self.baud_combo or (isinstance(widget, QLabel) and widget.text() == "Baud Rate:"):
                        widget.setVisible(False)
                    else:
                        widget.setVisible(True)

    def log_message(self, message: str):
        self.terminal.append_text(message)

    def run_scan_script(self):
        import threading
        if self.process is not None:
            self.log_message("Scan already running...")
            return

        if not os.path.exists(self.script_path):
            self.log_message(f"Script not found: {self.script_path}")
            return

        self.process = subprocess.Popen(
            ["python", self.script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
        )
        self.log_message(f"Started scan script: {self.script_path}")

        def read_output():
            for line in self.process.stdout:
                self.log_message(line.rstrip())
            self.process.stdout.close()
            self.process.wait()
            self.log_message("Scan script finished.")
            self.process = None

        threading.Thread(target=read_output, daemon=True).start()
