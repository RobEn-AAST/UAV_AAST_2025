from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QTextEdit,
    QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView, QAbstractScrollArea
)
from PyQt6.QtCore import Qt
from pymavlink import mavutil
import yaml

class ParametersPage(QWidget):
    def __init__(self):
        super().__init__()
        self.parameters = {}  # Store loaded parameters
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Load Button
        self.load_button = QPushButton("Load Parameters (YAML)")
        self.load_button.setFixedHeight(40)
        self.load_button.setStyleSheet("font-size: 16px;")
        self.load_button.clicked.connect(self.load_yaml)
        layout.addWidget(self.load_button)

        # Table to Display Parameters (4 Columns)
        self.param_table = QTableWidget(10, 4)  # Start with 10 empty rows
        self.param_table.setHorizontalHeaderLabels(["Parameter", "Value", "Parameter", "Value"])
        self.param_table.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.param_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.param_table.verticalHeader().setVisible(False)
        self.param_table.itemChanged.connect(self.manual_param_edit)  # Track manual edits
        layout.addWidget(self.param_table)

        # Buttons Layout (Clear Table + Upload)
        button_layout = QHBoxLayout()

        # Clear Table Button (Left)
        self.clear_button = QPushButton("Clear Table")
        self.clear_button.setFixedHeight(40)
        self.clear_button.setStyleSheet("font-size: 16px;")
        self.clear_button.clicked.connect(self.clear_table)
        button_layout.addWidget(self.clear_button)

        # Upload Button (Right)
        self.upload_button = QPushButton("Upload to UAV")
        self.upload_button.setFixedHeight(40)
        self.upload_button.setStyleSheet("font-size: 16px;")
        self.upload_button.clicked.connect(self.confirm_upload)
        button_layout.addWidget(self.upload_button)

        layout.addLayout(button_layout)  # Add the buttons to the main layout

        # Status Log
        self.status_log = QTextEdit()
        self.status_log.setReadOnly(True)
        layout.addWidget(self.status_log)

        self.setLayout(layout)

    def log_message(self, message):
        """Log only important messages to the status text area."""
        self.status_log.append(f"> {message}")

    def load_yaml(self):
        """Open file dialog to load YAML file and display its content."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select YAML File", "", "YAML Files (*.yaml *.yml)")
        if not file_path:
            return  # User canceled

        try:
            with open(file_path, "r") as file:
                yaml_data = yaml.safe_load(file)

            self.parameters.clear()
            self.param_table.setRowCount(10)  # Reset table with 10 rows

            param_list = []
            for section, params in yaml_data.items():
                for param_name, param_value in params.items():
                    param_list.append((param_name, param_value))

            # Add parameters to table (2 per row)
            for i in range(len(param_list)):
                row = i // 2  # Every 2 parameters go in one row
                col_offset = (i % 2) * 2  # Either (0,1) or (2,3)

                self.param_table.setItem(row, col_offset, QTableWidgetItem(param_list[i][0]))  # Parameter
                self.param_table.setItem(row, col_offset + 1, QTableWidgetItem(str(param_list[i][1])))  # Value

                self.parameters[param_list[i][0]] = param_list[i][1]  # Store in dictionary

            self.log_message(f"Loaded {len(param_list)} parameters successfully.")

        except Exception as e:
            self.log_message(f"Error loading YAML: {str(e)}")

    def clear_table(self):
        """Clear only the parameter values, keeping the names intact."""
        for row in range(self.param_table.rowCount()):
            for col in [1, 3]:  # Only clear value columns
                if self.param_table.item(row, col):
                    self.param_table.setItem(row, col, QTableWidgetItem(""))  # Clear the value
        self.parameters.clear()
        self.log_message("Cleared all parameter values.")

    def manual_param_edit(self, item):
        """Update the parameters dictionary when a user manually edits a value."""
        row = item.row()
        col = item.column()

        if col % 2 == 0:  # Parameter name column (0 or 2)
            param_name = item.text().strip()
            param_value_item = self.param_table.item(row, col + 1)
            param_value = param_value_item.text().strip() if param_value_item else ""
        else:  # Value column (1 or 3)
            param_value = item.text().strip()
            param_name_item = self.param_table.item(row, col - 1)
            param_name = param_name_item.text().strip() if param_name_item else ""

        if param_name:
            self.parameters[param_name] = param_value  # Store in dictionary

    def confirm_upload(self):
        """Ask for confirmation before uploading."""
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
        """Upload parameters to UAV using MAVLink."""
        port = "/dev/ttyUSB0"  # Update if needed
        baudrate = 57600

        try:
            connection = mavutil.mavlink_connection(port, baud=baudrate)
            connection.wait_heartbeat()

            for param_name, param_value in self.parameters.items():
                connection.mav.param_set_send(
                    connection.target_system, connection.target_component,
                    param_name.encode(), float(param_value), mavutil.mavlink.MAV_PARAM_TYPE_REAL32
                )

            self.log_message("Parameters uploaded successfully.")
            QMessageBox.information(self, "Upload Complete", "All parameters have been successfully uploaded.")

        except Exception as e:
            self.log_message(f"Upload failed: {str(e)}")
            QMessageBox.critical(self, "Upload Failed", f"Error uploading parameters: {str(e)}")
