import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QStackedWidget, QTabWidget)
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
        
        # Add pages
        self.home_page = HomePage()
        self.reading_page = ReadingPage()
        
        # Add tabs
        self.tab_widget.addTab(self.home_page, "Home")
        self.tab_widget.addTab(self.reading_page, "Reading")

def main():
    app = QApplication(sys.argv)
    
    # Set application-wide font
    app.setFont(QFont('Arial', 10))
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()