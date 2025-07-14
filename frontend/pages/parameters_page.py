from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QTextEdit,
    QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView, QAbstractScrollArea,
    QComboBox
)
from PyQt6.QtCore import Qt
from pymavlink import mavutil
import yaml
import serial.tools.list_ports

class ParametersPage(QWidget):
    def __init__(self):
        super().__init__()
        self.parameters = {}
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Serial Port and Baudrate Dropdowns
        serial_layout = QHBoxLayout()

        self.port_dropdown = QComboBox()
        self.port_dropdown.setFixedHeight(30)
        self.refresh_ports()
        serial_layout.addWidget(self.port_dropdown)

        self.baud_dropdown = QComboBox()
        self.baud_dropdown.setFixedHeight(30)
        self.baud_dropdown.addItems(["57600", "115200"])
        self.baud_dropdown.setCurrentText("57600")
        serial_layout.addWidget(self.baud_dropdown)

        layout.addLayout(serial_layout)

        self.refresh_button = QPushButton("Refresh Ports")
        self.refresh_button.setFixedHeight(30)
        self.refresh_button.clicked.connect(self.refresh_ports)
        layout.addWidget(self.refresh_button)

        self.load_button = QPushButton("Load Parameters (YAML)")
        self.load_button.setFixedHeight(40)
        self.load_button.clicked.connect(self.load_yaml)
        layout.addWidget(self.load_button)

        # Table
        self.param_table = QTableWidget(10, 4)
        self.param_table.setHorizontalHeaderLabels(["Parameter", "Value", "Parameter", "Value"])
        self.param_table.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.param_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.param_table.verticalHeader().setVisible(False)
        self.param_table.itemChanged.connect(self.manual_param_edit)
        layout.addWidget(self.param_table)

        # Buttons
        button_layout = QHBoxLayout()

        self.clear_button = QPushButton("Clear Table")
        self.clear_button.setFixedHeight(40)
        self.clear_button.clicked.connect(self.clear_table)
        button_layout.addWidget(self.clear_button)

        self.upload_button = QPushButton("Upload to UAV")
        self.upload_button.setFixedHeight(40)
        self.upload_button.clicked.connect(self.confirm_upload)
        button_layout.addWidget(self.upload_button)

        layout.addLayout(button_layout)

        self.status_log = QTextEdit()
        self.status_log.setReadOnly(True)
        layout.addWidget(self.status_log)

        self.setLayout(layout)
        self.apply_styles()
        self.init_table_items()

    def apply_styles(self):
        # Button Styles with consistent non-white hover
        self.load_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #5dade2;
            }
        """)
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #58d68d;
            }
        """)
        self.upload_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #58d68d;
            }
        """)
        self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #ec7063;
            }
        """)

        # Table Header
        self.param_table.setStyleSheet("""
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                padding: 4px;
                border: 1px solid white;
            }
            QTableView::item:selected {
                background: none;
            }
            QTableWidget::item {
                border-right: 1px solid #ddd;
                border-bottom: 1px solid #ddd;
            }
        """)

    def init_table_items(self):
        for row in range(self.param_table.rowCount()):
            for col in range(self.param_table.columnCount()):
                item = QTableWidgetItem("")
                if col in [1, 3]:
                    item.setBackground(Qt.GlobalColor.lightGray)
                self.param_table.setItem(row, col, item)

    def refresh_ports(self):
        self.port_dropdown.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.port_dropdown.addItem(port.device)
        if not ports:
            self.port_dropdown.addItem("No Ports Found")

    def log_message(self, message):
        self.status_log.append(f"> {message}")

    def load_yaml(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select YAML File", "", "YAML Files (*.yaml *.yml)")
        if not file_path:
            return

        try:
            with open(file_path, "r") as file:
                yaml_data = yaml.safe_load(file)

            self.parameters.clear()
            self.param_table.setRowCount(10)

            param_list = []
            for section, params in yaml_data.items():
                for param_name, param_value in params.items():
                    param_list.append((param_name, param_value))

            for i in range(len(param_list)):
                row = i // 2
                col_offset = (i % 2) * 2
                self.param_table.setItem(row, col_offset, QTableWidgetItem(param_list[i][0]))
                value_item = QTableWidgetItem(str(param_list[i][1]))
                value_item.setBackground(Qt.GlobalColor.lightGray)
                self.param_table.setItem(row, col_offset + 1, value_item)
                self.parameters[param_list[i][0]] = param_list[i][1]

            self.add_middle_separator()
            self.log_message(f"Loaded {len(param_list)} parameters successfully.")

        except Exception as e:
            self.log_message(f"Error loading YAML: {str(e)}")

    def clear_table(self):
        for row in range(self.param_table.rowCount()):
            for col in [1, 3]:
                item = QTableWidgetItem("")
                item.setBackground(Qt.GlobalColor.lightGray)
                self.param_table.setItem(row, col, item)
            for col in [0, 2]:
                self.param_table.setItem(row, col, QTableWidgetItem(""))
        self.parameters.clear()
        self.add_middle_separator()
        self.log_message("Cleared all parameter values.")

    def add_middle_separator(self):
        # Ensure the middle vertical separator is thicker
        header = self.param_table.horizontalHeader()
        for i in range(self.param_table.columnCount() - 1):
            if i == 1:
                header.setStyleSheet("""
                    QHeaderView::section {
                        border-right: 3px solid white;
                    }
                """)
            else:
                header.setStyleSheet("""
                    QHeaderView::section {
                        border-right: 1px solid white;
                    }
                """)

    def manual_param_edit(self, item):
        row = item.row()
        col = item.column()

        if col % 2 == 0:
            param_name = item.text().strip()
            param_value_item = self.param_table.item(row, col + 1)
            param_value = param_value_item.text().strip() if param_value_item else ""
        else:
            param_value = item.text().strip()
            param_name_item = self.param_table.item(row, col - 1)
            param_name = param_name_item.text().strip() if param_name_item else ""

        if col in [1, 3]:
            item.setBackground(Qt.GlobalColor.lightGray)

        if param_name:
            self.parameters[param_name] = param_value

    def confirm_upload(self):
        if not self.parameters:
            QMessageBox.warning(self, "No Parameters", "No parameters loaded or entered. Please add parameters first.")
            return

        reply = QMessageBox.question(
            self, "Confirm Upload",
            "Are you sure you want to upload these parameters?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.upload_parameters()

    def upload_parameters(self):
        port = self.port_dropdown.currentText().strip()
        baudrate_text = self.baud_dropdown.currentText().strip()

        if not port or port == "No Ports Found":
            QMessageBox.critical(self, "Upload Failed", "Please select a valid serial port.")
            return

        try:
            baudrate = int(baudrate_text)
        except ValueError:
            QMessageBox.critical(self, "Upload Failed", "Invalid baudrate.")
            return

        try:
            self.log_message(f"Connecting to {port} at {baudrate}...")
            connection = mavutil.mavlink_connection(port, baud=baudrate)
            connection.wait_heartbeat()
            self.log_message("Heartbeat received. Starting upload...")

            for param_name, param_value in self.parameters.items():
                try:
                    value = float(param_value)
                except ValueError:
                    self.log_message(f"Skipping {param_name}: invalid number")
                    continue

                connection.mav.param_set_send(
                    connection.target_system, connection.target_component,
                    param_name.encode(), value, mavutil.mavlink.MAV_PARAM_TYPE_REAL32
                )

            self.log_message("Parameters uploaded successfully.")
            QMessageBox.information(self, "Upload Complete", "All parameters have been successfully uploaded.")

        except Exception as e:
            self.log_message(f"Upload failed: {str(e)}")
            QMessageBox.critical(self, "Upload Failed", f"Error uploading parameters: {str(e)}")
