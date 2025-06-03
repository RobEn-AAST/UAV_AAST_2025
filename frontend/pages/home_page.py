from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLineEdit, QLabel, QMessageBox, QComboBox)
from PyQt6.QtCore import Qt
from utils.connection_manager import ConnectionManager


class HomePage(QWidget):
    def __init__(self):
        super().__init__()
        self.connection_manager = ConnectionManager.get_instance()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("RobEn")
        title.setStyleSheet(
            """
            font-size: 48px;
            font-weight: bold;
            color: #2c3e50;
            margin: 20px;
        """
        )
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Subtitle
        subtitle = QLabel("UAV Control System")
        subtitle.setStyleSheet(
            """
            font-size: 24px;
            color: #34495e;
            margin-bottom: 40px;
        """
        )
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(title)
        layout.addWidget(subtitle)

        # Connection section
        connection_layout = QHBoxLayout()

        # Port selection dropdown
        self.port_combo = QComboBox()
        self.port_combo.addItems([
            "Select Port...",
            "ttyUSB0",
            "ttyACM0",
            "COM4"
        ])
        self.port_combo.currentTextChanged.connect(self.handle_port_selection)

        # IP Address input
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("Enter IP address (e.g., 172.18.224.1)")
        self.ip_input.setMinimumWidth(200)

        # Connect button
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self.handle_connection)

        # Status label
        self.status_label = QLabel("Not Connected")
        self.status_label.setStyleSheet("color: red")

        connection_layout.addWidget(QLabel("Port:"))
        connection_layout.addWidget(self.port_combo)
        connection_layout.addWidget(QLabel("IP Address:"))
        connection_layout.addWidget(self.ip_input)
        connection_layout.addWidget(self.connect_btn)
        connection_layout.addWidget(self.status_label)
        connection_layout.addStretch()

        layout.addLayout(connection_layout)
        layout.addStretch()

    def handle_port_selection(self, port):
        """Handle port selection from dropdown"""
        if port != "Select Port...":
            self.ip_input.setText(f"/dev/{port}" if port.startswith("tty") else port)

    def handle_connection(self):
        ip_address = self.ip_input.text().strip()
        if not ip_address:
            QMessageBox.warning(self, "Error", "Please enter an IP address")
            return

        if self.connection_manager.connect_to_uav(ip_address):
            self.status_label.setText("Connected")
            self.status_label.setStyleSheet("color: green")
            self.connect_btn.setEnabled(False)
            self.ip_input.setEnabled(False)
            QMessageBox.information(self, "Success", "Successfully connected to UAV")
        else:
            self.status_label.setText("Connection Failed")
            self.status_label.setStyleSheet("color: red")
            QMessageBox.warning(self, "Error", "Failed to connect to UAV")
