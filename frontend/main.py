import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QStackedWidget, QTabWidget, QLabel)
from PyQt6.QtGui import QFont
from pages.home_page import HomePage
from pages.reading_page import ReadingPage

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RobEn UAV Control Interface")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # Create tab widget for navigation
        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)
        
        # Create tab pages
        self.home_page = HomePage()
        self.reading_page = ReadingPage()
        self.missions_tab = QWidget()
        self.parameters_tab = QWidget()
        self.camera_tab = QWidget()
        
        # Add tabs
        self.tab_widget.addTab(self.home_page, "Home")
        self.tab_widget.addTab(self.reading_page, "Reading")
        self.tab_widget.addTab(self.missions_tab, "Missions")
        self.tab_widget.addTab(self.parameters_tab, "Parameters")
        self.tab_widget.addTab(self.camera_tab, "Camera")
        
        self.setup_tabs()

    def setup_tabs(self):
        # Missions tab
        missions_layout = QVBoxLayout()
        missions_layout.addWidget(QLabel("Choose a mission"))
        self.missions_tab.setLayout(missions_layout)

        # Parameters tab
        parameters_layout = QVBoxLayout()
        parameters_layout.addWidget(QLabel("for parameter uploading"))
        self.parameters_tab.setLayout(parameters_layout)

        # Camera tab
        camera_layout = QVBoxLayout()
        camera_layout.addWidget(QLabel("Camera details"))
        self.camera_tab.setLayout(camera_layout)

def main():
    app = QApplication(sys.argv)
    app.setFont(QFont('Arial', 10))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()