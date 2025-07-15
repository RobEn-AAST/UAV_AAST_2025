import sys
import os

# Add project root to path for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit,
    QLabel, QMessageBox, QComboBox
)
from frontend.utils.connection_manager import ConnectionManager
from path_manager import PathManager  # Assuming you have this utility


class HomePage(QWidget):
    def __init__(self):
        super().__init__()

        self.connection_manager = ConnectionManager.get_instance()
        self.path_manager = PathManager()

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # ------------------- INFO SECTION -------------------
        info_layout = QVBoxLayout()
        info_layout.addWidget(self._make_label(f"Project Root: {self.path_manager.project_root}", "#7f8c8d", 12))
        info_layout.addWidget(self._make_label(f"Config: {self.path_manager.get_file_path('data.json')}", "#7f8c8d", 12))
        layout.addLayout(info_layout)
        layout.addSpacing(10)

        # ------------------- PORT SELECTION -------------------
        port_layout = QHBoxLayout()
        self.port_combo = QComboBox()
        port_options = self._get_platform_ports()
        self.port_combo.addItems(port_options)
        self.port_combo.currentTextChanged.connect(self.handle_port_selection)

        port_layout.addWidget(QLabel("Port:"))
        port_layout.addWidget(self.port_combo)
        port_layout.addStretch()

        # ------------------- BAUD RATE -------------------
        baud_layout = QHBoxLayout()
        self.baud_combo = QComboBox()
        self.baud_combo.addItems([
            "Select Baud Rate...",
            "57600",
            "115200"
        ])
        baud_layout.addWidget(QLabel("Baud Rate:"))
        baud_layout.addWidget(self.baud_combo)
        baud_layout.addStretch()

        # ------------------- CONNECTION -------------------
        connection_layout = QHBoxLayout()
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("Enter IP address or port (e.g., 172.18.224.1 or COM4)")
        self.ip_input.setMinimumWidth(150)

        try:
            config = self.path_manager.load_config()
            default_conn = config.get('sim_connection_string', '172.26.16.1:14550')
            self.ip_input.setText(default_conn)
        except Exception as e:
            print(f"[WARN] Failed to load config: {e}")

        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self.handle_connection)

        self.disconnect_btn = QPushButton("Disconnect")
        self.disconnect_btn.clicked.connect(self.handle_disconnection)
        self.disconnect_btn.setEnabled(False)

        connection_layout.addWidget(QLabel("IP Address / Port:"))
        connection_layout.addWidget(self.ip_input)
        connection_layout.addWidget(self.connect_btn)
        connection_layout.addWidget(self.disconnect_btn)

        # ------------------- STATUS -------------------
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Not Connected")
        self.status_label.setStyleSheet("color: red")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()

        platform_label = self._make_label(f"Platform: {self.path_manager.os_type.title()}", "#3498db", 12)
        status_layout.addWidget(platform_label)

        # ------------------- LAYOUT ASSEMBLY -------------------
        layout.addSpacing(20)
        layout.addLayout(port_layout)
        layout.addSpacing(10)
        layout.addLayout(baud_layout)
        layout.addSpacing(10)
        layout.addLayout(connection_layout)
        layout.addSpacing(10)
        layout.addLayout(status_layout)
        layout.addStretch()

    # ------------------- HELPERS -------------------
    def _make_label(self, text, color, size):
        label = QLabel(text)
        label.setStyleSheet(f"color: {color}; font-size: {size}px;")
        return label

    def _get_platform_ports(self):
        if self.path_manager.os_type == "windows":
            return ["Select Port...", "COM3", "COM4", "COM5", "COM6"]
        else:
            return ["Select Port...", "ttyUSB0", "ttyACM0", "ttyUSB1", "ttyACM1"]

    def handle_port_selection(self, port):
        if port != "Select Port...":
            if self.path_manager.os_type == "windows":
                formatted_port = port if port.startswith("COM") else f"COM{port}"
            else:
                formatted_port = port if port.startswith("/dev/") else f"/dev/{port}"
            self.ip_input.setText(formatted_port)

    def handle_connection(self):
        try:
            ip_address = self.ip_input.text().strip()
            baud_rate = self.baud_combo.currentText()

            if not ip_address:
                QMessageBox.warning(self, "Error", "Please enter an IP address or port")
                return

            # For serial connections, validate baud rate
            if ":" not in ip_address and baud_rate == "Select Baud Rate...":
                QMessageBox.warning(self, "Error", "Please select a baud rate for serial connections")
                return

            config_path = self.path_manager.get_file_path("data.json")
            adapted_connection = self.path_manager.get_connection_string_for_platform(ip_address)

            if self.connection_manager.connect_to_uav(adapted_connection, config_path):
                self._set_connected_state(adapted_connection)
            else:
                self._set_failed_state()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred:\n{e}")

    def _set_connected_state(self, connection):
        self.status_label.setText("Connected")
        self.status_label.setStyleSheet("color: green")
        self.connect_btn.setEnabled(False)
        self.disconnect_btn.setEnabled(True)
        self.ip_input.setEnabled(False)
        self.baud_combo.setEnabled(False)
        self.port_combo.setEnabled(False)
        QMessageBox.information(self, "Success", f"Successfully connected to UAV\nUsing: {connection}")

    def _set_failed_state(self):
        self.status_label.setText("Connection Failed")
        self.status_label.setStyleSheet("color: red")
        QMessageBox.warning(self, "Error", "Failed to connect to UAV")

    def handle_disconnection(self):
        if self.connection_manager.disconnect_from_uav():
            self.status_label.setText("Disconnected")
            self.status_label.setStyleSheet("color: red")
            self.connect_btn.setEnabled(True)
            self.disconnect_btn.setEnabled(False)
            self.ip_input.setEnabled(True)
            self.baud_combo.setEnabled(True)
            self.port_combo.setEnabled(True)
            QMessageBox.information(self, "Disconnected", "Disconnected from UAV")
        else:
            QMessageBox.warning(self, "Error", "Failed to disconnect from UAV")
