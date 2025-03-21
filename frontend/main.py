import sys
import signal
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QTabWidget
from PyQt6.QtGui import QFont
from PyQt6.QtCore import QTimer
from pages import HomePage, ReadingPage, MissionsPage, ParametersPage, CameraPage

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
        
        # Create and add tab pages
        self.tab_widget.addTab(HomePage(), "Home")
        self.tab_widget.addTab(ReadingPage(), "Reading")
        self.tab_widget.addTab(MissionsPage(), "Missions")
        self.tab_widget.addTab(ParametersPage(), "Parameters")
        self.tab_widget.addTab(CameraPage(), "Camera")

def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully"""
    print("\nClosing application...")
    QApplication.quit()

def main():
    # Set up signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)

    app = QApplication(sys.argv)
    app.setFont(QFont('Arial', 10))
    
    # Create timer to allow Python to process system signals
    timer = QTimer()
    timer.timeout.connect(lambda: None)
    timer.start(100)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()