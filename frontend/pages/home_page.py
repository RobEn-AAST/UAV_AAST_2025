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
        self.ip_input.setPlaceholderText("Enter IP address (e.g., 172.18.224.1)")
        self.ip_input.setMinimumWidth(130)
        
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self.handle_connection)
        
        connection_layout.addWidget(QLabel("IP Address:"))
        connection_layout.addWidget(self.ip_input)
        connection_layout.addWidget(self.connect_btn)
        
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
        """Handle port selection from dropdown"""
        if port != "Select Port...":
            self.ip_input.setText(f"/dev/{port}" if port.startswith("tty") else port)

    def handle_connection(self):
        """Handle connection attempt"""
        ip_address = self.ip_input.text().strip()
        baud_rate = self.baud_combo.currentText()

        if not ip_address:
            QMessageBox.warning(self, "Error", "Please enter an IP address")
            return

        if baud_rate == "Select Baud Rate...":
            QMessageBox.warning(self, "Error", "Please select a baud rate")
            return

        if self.connection_manager.connect_to_uav(ip_address, int(baud_rate)):
            self.status_label.setText("Connected")
            self.status_label.setStyleSheet("color: green")
            self.connect_btn.setEnabled(False)
            self.ip_input.setEnabled(False)
            self.baud_combo.setEnabled(False)
            QMessageBox.information(self, "Success", "Successfully connected to UAV")
        else:
            self.status_label.setText("Connection Failed")
            self.status_label.setStyleSheet("color: red")
            QMessageBox.warning(self, "Error", "Failed to connect to UAV")
