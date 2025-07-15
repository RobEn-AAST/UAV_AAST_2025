from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog,
    QLabel, QComboBox, QTextEdit, QMessageBox, QProgressBar
)
from PyQt6.QtCore import Qt, QThread, QObject, pyqtSignal
import os
import sys
import json

# Add backend path to sys.path to import backend modules
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from modules.entries.Convertor import Convertor
from modules.entries.pdf_reader_files import convert_pdf


class ConversionWorker(QObject):
    """Worker thread for file conversion to avoid blocking the UI"""
    progress = pyqtSignal(str)  # For status messages
    finished = pyqtSignal(bool, str)  # Success status and message
    
    def __init__(self, file_path, file_type, config_data):
        super().__init__()
        self.file_path = file_path
        self.file_type = file_type
        self.config_data = config_data
    
    def run(self):
        try:
            if self.file_type == "PDF":
                self.progress.emit("Converting PDF file...")
                # Use the backend PDF converter
                convert_pdf(self.file_path)
                self.finished.emit(True, "PDF converted successfully! Check the Output folder for CSV files.")
                
            elif self.file_type == "Waypoints":
                self.progress.emit("Converting waypoint files...")
                converter = Convertor()
                
                # Get the base filename without extension for output
                base_name = os.path.splitext(os.path.basename(self.file_path))[0]
                output_dir = os.path.dirname(self.file_path)
                output_file = os.path.join(output_dir, f"{base_name}.csv")
                
                # Convert waypoint file to CSV
                converter.convert_to_csv(self.file_path, output_file)
                self.finished.emit(True, f"Waypoint file converted successfully! Output: {output_file}")
                
        except Exception as e:
            self.finished.emit(False, f"Conversion failed: {str(e)}")


class ReadingPage(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_file = None
        self.config_data = self.load_config()
        self.init_ui()

    def load_config(self):
        """Load configuration data from backend"""
        try:
            config_path = os.path.abspath(os.path.join(
                os.path.dirname(__file__), '..', '..', 'files', 'data.json'
            ))
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Could not load config: {e}")
            return {}

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Title
        title_label = QLabel("File Conversion Tool")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 20px;
            }
        """)
        layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel("Select file type and upload your file for conversion to CSV format")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #7f8c8d;
                margin-bottom: 30px;
            }
        """)
        layout.addWidget(desc_label)
        
        # File type selection
        type_layout = QHBoxLayout()
        type_label = QLabel("File Type:")
        type_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        self.file_type_combo = QComboBox()
        self.file_type_combo.addItems(["Select File Type...", "PDF", "Waypoints"])
        self.file_type_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                font-size: 14px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
            }
            QComboBox:focus {
                border-color: #3498db;
            }
        """)
        self.file_type_combo.currentTextChanged.connect(self.on_file_type_changed)
        
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.file_type_combo)
        type_layout.addStretch()
        layout.addLayout(type_layout)
        
        # File selection
        file_layout = QHBoxLayout()
        
        self.upload_button = QPushButton("Select File")
        self.upload_button.setEnabled(False)
        self.upload_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px 20px;
                font-size: 14px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        self.upload_button.clicked.connect(self.select_file)
        
        self.file_path_label = QLabel("No file selected")
        self.file_path_label.setStyleSheet("""
            QLabel {
                padding: 10px;
                border: 2px dashed #bdc3c7;
                border-radius: 5px;
                background-color: #ecf0f1;
                color: #7f8c8d;
            }
        """)
        
        file_layout.addWidget(self.upload_button)
        file_layout.addWidget(self.file_path_label, 1)
        layout.addLayout(file_layout)
        
        # Convert button
        self.convert_button = QPushButton("Convert to CSV")
        self.convert_button.setEnabled(False)
        self.convert_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 15px;
                font-size: 16px;
                font-weight: bold;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #219a52;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        self.convert_button.clicked.connect(self.convert_file)
        layout.addWidget(self.convert_button)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        layout.addWidget(self.progress_bar)
        
        # Status log
        log_label = QLabel("Conversion Log:")
        log_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 20px;")
        layout.addWidget(log_label)
        
        self.status_log = QTextEdit()
        self.status_log.setReadOnly(True)
        self.status_log.setMaximumHeight(200)
        self.status_log.setStyleSheet("""
            QTextEdit {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background-color: #f8f9fa;
                font-family: 'Courier New', monospace;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.status_log)
        
        # Add stretch to push everything up
        layout.addStretch()

    def on_file_type_changed(self, file_type):
        """Enable upload button when file type is selected"""
        self.upload_button.setEnabled(file_type != "Select File Type...")
        self.selected_file = None
        self.file_path_label.setText("No file selected")
        self.convert_button.setEnabled(False)

    def select_file(self):
        """Open file dialog based on selected file type"""
        file_type = self.file_type_combo.currentText()
        
        if file_type == "PDF":
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Select PDF File", "", "PDF Files (*.pdf)"
            )
        elif file_type == "Waypoints":
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Select Waypoint File", "", "Waypoint Files (*.waypoints *.plan *.mission)"
            )
        else:
            return
        
        if file_path:
            self.selected_file = file_path
            self.file_path_label.setText(os.path.basename(file_path))
            self.file_path_label.setStyleSheet("""
                QLabel {
                    padding: 10px;
                    border: 2px solid #27ae60;
                    border-radius: 5px;
                    background-color: #d5f4e6;
                    color: #27ae60;
                    font-weight: bold;
                }
            """)
            self.convert_button.setEnabled(True)
            self.log_message(f"Selected file: {os.path.basename(file_path)}")

    def convert_file(self):
        """Start the conversion process"""
        if not self.selected_file:
            QMessageBox.warning(self, "No File Selected", "Please select a file first.")
            return
        
        file_type = self.file_type_combo.currentText()
        
        # Disable UI during conversion
        self.convert_button.setEnabled(False)
        self.upload_button.setEnabled(False)
        self.file_type_combo.setEnabled(False)
        self.progress_bar.setVisible(True)
        
        # Start conversion in worker thread
        self.worker = ConversionWorker(self.selected_file, file_type, self.config_data)
        self.thread = QThread()
        
        self.worker.moveToThread(self.thread)
        
        # Connect signals
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.log_message)
        self.worker.finished.connect(self.on_conversion_finished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        
        # Start the thread
        self.thread.start()
        
        self.log_message(f"Starting conversion of {file_type} file...")

    def on_conversion_finished(self, success, message):
        """Handle conversion completion"""
        # Re-enable UI
        self.convert_button.setEnabled(True)
        self.upload_button.setEnabled(True)
        self.file_type_combo.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        # Log the result
        self.log_message(message)
        
        # Show result dialog
        if success:
            QMessageBox.information(self, "Conversion Successful", message)
        else:
            QMessageBox.critical(self, "Conversion Failed", message)

    def log_message(self, message):
        """Add a message to the status log with black text color"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_log.setTextColor(Qt.GlobalColor.black)
        self.status_log.append(f"[{timestamp}] {message}")
        self.status_log.setTextColor(Qt.GlobalColor.black)  # Ensure color stays black for next messages
        
        # Auto-scroll to bottom
        scrollbar = self.status_log.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())