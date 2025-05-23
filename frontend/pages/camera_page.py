import sys
from PyQt6.QtWidgets import (QMainWindow, QLabel, QVBoxLayout, QWidget, 
                            QPushButton, QApplication)
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import QTimer, Qt, QSize
import os

class CameraPage(QWidget):
    def __init__(self):
        super().__init__()
        self.image_path = "/home/zeyadcode/Pictures/Screenshots/"  # Update with your path
        self.initUI()
        self.last_displayed = None

    def initUI(self):
        layout = QVBoxLayout(self)
        self.button = QPushButton("View Images")
        self.button.setFixedSize(600, 50)
        self.button.clicked.connect(self.view_images)
        layout.addWidget(self.button)
        
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
