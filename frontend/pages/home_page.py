from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel, QMessageBox, QComboBox
from utils.connection_manager import ConnectionManager

class HomePage(QWidget):
    def __init__(self):
        super().__init__()
        self.connection_manager = ConnectionManager.get_instance()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Port selection section
        port_layout = QHBoxLayout()
        self.port_combo = QComboBox()
        self.port_combo.addItems([
            "Select Port...",
            "ttyUSB0",
            "ttyACM0",
            "COM4"
        ])
        self.port_combo.currentTextChanged.connect(self.handle_port_selection)
        port_layout.addWidget(QLabel("Port:"))
        port_layout.addWidget(self.port_combo)
        port_layout.addStretch()
        
        # Baud rate section
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
        
        # Connection section
        connection_layout = QHBoxLayout()
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("Enter IP address or port (e.g., 172.18.224.1 or /dev/ttyUSB0)")
        self.ip_input.setMinimumWidth(130)
        
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self.handle_connection)
        
        self.disconnect_btn = QPushButton("Disconnect")
        self.disconnect_btn.clicked.connect(self.handle_disconnection)
        self.disconnect_btn.setEnabled(False)  # Disabled initially

        connection_layout.addWidget(QLabel("IP Address / Port:"))
        connection_layout.addWidget(self.ip_input)
        connection_layout.addWidget(self.connect_btn)
        connection_layout.addWidget(self.disconnect_btn)
        
        # Status section
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Not Connected")
        self.status_label.setStyleSheet("color: red")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        
        # Add all sections to main layout with some spacing
        layout.addSpacing(20)
        layout.addLayout(port_layout)
        layout.addSpacing(10)
        layout.addLayout(baud_layout)
        layout.addSpacing(10)
        layout.addLayout(connection_layout)
        layout.addSpacing(10)
        layout.addLayout(status_layout)
        layout.addStretch()

    def handle_port_selection(self, port):
        if port != "Select Port...":
            self.ip_input.setText(f"/dev/{port}" if port.startswith("tty") else port)

    def handle_connection(self):
        ip_address = self.ip_input.text().strip()
        baud_rate = self.baud_combo.currentText()

        if not ip_address:
            QMessageBox.warning(self, "Error", "Please enter an IP address or port")
            return

        if baud_rate == "Select Baud Rate...":
            QMessageBox.warning(self, "Error", "Please select a baud rate")
            return

        config_path = config_path = r"C:\Users\maria\UAV project\UAV_AAST_2025\files\data.json"

        if self.connection_manager.connect_to_uav(ip_address, config_path):
            self.status_label.setText("Connected")
            self.status_label.setStyleSheet("color: green")
            self.connect_btn.setEnabled(False)
            self.disconnect_btn.setEnabled(True)
            self.ip_input.setEnabled(False)
            self.baud_combo.setEnabled(False)
            QMessageBox.information(self, "Success", "Successfully connected to UAV")
        else:
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
            QMessageBox.information(self, "Disconnected", "Disconnected from UAV")
        else:
            QMessageBox.warning(self, "Error", "Failed to disconnect from UAV")
