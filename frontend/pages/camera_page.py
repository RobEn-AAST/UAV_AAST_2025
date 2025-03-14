import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, Qt, QSize
from PyQt5.QtWidgets import QDesktopWidget
import os

class ImageViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.image_path = "C:/Users/maria/test pic" #provide file path
        self.initUI()

        self.last_displayed = None

    def initUI(self):
        self.setWindowTitle("Image Viewer")
        screen = QDesktopWidget().screenGeometry()
        self.setGeometry(0, 0, screen.width(), screen.height())  
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)

        self.button = QPushButton("View Images")
        self.button.setFixedSize(600, 50)
        self.button.clicked.connect(self.view_images)
        self.layout.addWidget(self.button)
        
    def view_images(self):
        self.images_window = QWidget()
        self.images_window.setObjectName("ImagesWindow")
        self.images_window.setWindowTitle("Images")
        screen = QDesktopWidget().screenGeometry()
        self.images_window.setGeometry(0, 0, screen.width(), screen.height())     
        
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
            image_files = [f for f in os.listdir(self.image_path) if f.endswith(('.jpg', '.png', '.jpeg'))]
                
            if image_files:
                latest_image = max(image_files, key=lambda x: os.path.getmtime(os.path.join(self.image_path, x)))
                    
                if latest_image != self.last_displayed:
                    image_path = os.path.join(self.image_path, latest_image)
                    self.last_displayed = latest_image
                    self.display_image(image_path)
                    self.status_label.setText(f"Status: \nNew image detected: {latest_image}")
        except Exception as e:
                    self.status_label.setText(f"Status: \nError checking images - {str(e)}")
                
    def display_image(self, image_path):
        pixmap = QPixmap(image_path)
        scaled_pixmap = pixmap.scaled(
            QSize(2000,2000),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.SmoothTransformation
            )
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setPixmap(scaled_pixmap)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    viewer = ImageViewer()
    viewer.show()
    sys.exit(app.exec_())
