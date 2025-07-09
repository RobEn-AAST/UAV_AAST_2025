import sys
from PyQt6.QtWidgets import (QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QWidget, 
                            QPushButton, QApplication, QMessageBox)
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import QTimer, Qt, QSize
from utils.connection_manager import ConnectionManager
from mav_utils.send_message import send_message
import os

class CameraPage(QWidget):
    def __init__(self):
        super().__init__()
        self.connection_manager = ConnectionManager.get_instance()
        self.image_path = "/home/zeyadcode/Pictures/Screenshots/"
        self.initUI()
        self.last_displayed = None

    def initUI(self):
        layout = QVBoxLayout(self)
        
        # Connection status message
        self.connection_label = QLabel("Must connect first!")
        self.connection_label.setStyleSheet("""
            QLabel {
                color: red;
                font-size: 24px;
                font-weight: bold;
                padding: 20px;
            }
        """)
        self.connection_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.connection_label)
        
        # Recording controls
        recording_layout = QHBoxLayout()
        
        self.start_rec_btn = QPushButton("Start Recording")
        self.start_rec_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                padding: 10px;
                font-size: 16px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        self.start_rec_btn.clicked.connect(self.start_recording)
        
        self.stop_rec_btn = QPushButton("Stop Recording")
        self.stop_rec_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 10px;
                font-size: 16px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.stop_rec_btn.clicked.connect(self.stop_recording)
        
        recording_layout.addWidget(self.start_rec_btn)
        recording_layout.addWidget(self.stop_rec_btn)
        layout.addLayout(recording_layout)
        
        # Image viewer button
        self.view_btn = QPushButton("View Images")
        self.view_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px;
                font-size: 16px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.view_btn.clicked.connect(self.view_images)
        layout.addWidget(self.view_btn)
        
        # Update UI based on connection status
        self.update_ui_state()
        
        # Start connection checker timer
        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self.update_ui_state)
        self.check_timer.start(1000)  # Check every second

    def update_ui_state(self):
        """Update UI elements based on connection status"""
        is_connected = self.connection_manager.is_connected()
        
        if is_connected:
            self.connection_label.setText("Connected to UAV")
            self.connection_label.setStyleSheet("color: green; font-size: 24px; font-weight: bold; padding: 20px;")
        else:
            self.connection_label.setText("Must connect first!")
            self.connection_label.setStyleSheet("color: red; font-size: 24px; font-weight: bold; padding: 20px;")
        
        self.start_rec_btn.setEnabled(is_connected)
        self.stop_rec_btn.setEnabled(is_connected)
        self.view_btn.setEnabled(is_connected)

    def start_recording(self):
        """Send start recording command"""
        try:
            if not self.connection_manager.is_connected():
                raise ConnectionError("Not connected to UAV")
                
            send_message(self.connection_manager.master, "start_recording")
            QMessageBox.information(self, "Success", "Started recording")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ensure you are connected: {str(e)}")
            self.update_ui_state()

    def stop_recording(self):
        """Send stop recording command"""
        try:
            if not self.connection_manager.is_connected():
                raise ConnectionError("Not connected to UAV")
                
            send_message(self.connection_manager.master, "stop_recording")
            QMessageBox.information(self, "Success", "Stopped recording")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ensure you are connected: {str(e)}")
            self.update_ui_state()

    def view_images(self):
        self.images_window = QWidget()
        self.images_window.setObjectName("ImagesWindow")
        self.images_window.setWindowTitle("Images")
        
        # Correct way to get screen geometry in PyQt6
        screen = QApplication.primaryScreen()
        geometry = screen.geometry()
        self.images_window.setGeometry(0, 0, geometry.width(), geometry.height())     
        
        if hasattr(self, 'timer'):
            self.timer.stop()
    
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_new_images)
        self.timer.start(1000)
        
        self.last_displayed = None
 
        self.layout = QVBoxLayout(self.images_window)
        
        self.status_label = QLabel("Status: Monitoring folder")
        self.status_label.setObjectName("StatusLabel")
        self.layout.addWidget(self.status_label)
        
        self.image_label = QLabel("No image available")
        self.image_label.setObjectName("ImageLabel")
        self.layout.addWidget(self.image_label)

        self.images_window.show()    
        self.check_new_images()

    def check_new_images(self):
        try:
            image_files = [f for f in os.listdir(self.image_path) 
                          if f.endswith(('.jpg', '.png', '.jpeg'))]
                
            if image_files:
                latest_image = max(image_files, 
                                 key=lambda x: os.path.getmtime(
                                     os.path.join(self.image_path, x)))
                    
                if latest_image != self.last_displayed:
                    image_path = os.path.join(self.image_path, latest_image)
                    self.last_displayed = latest_image
                    self.display_image(image_path)
                    self.status_label.setText(
                        f"Status: \nNew image detected: {latest_image}")
        except Exception as e:
            self.status_label.setText(
                f"Status: \nError checking images - {str(e)}")
                
    def display_image(self, image_path):
        pixmap = QPixmap(image_path)
        scaled_pixmap = pixmap.scaled(
            QSize(2000, 2000),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setPixmap(scaled_pixmap)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    viewer = CameraPage()
    viewer.show()
    sys.exit(app.exec())
