import sys
import signal
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QTabWidget
from PyQt6.QtGui import QFont
from PyQt6.QtCore import QTimer

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import custom pages
from pages import HomePage, ReadingPage, MissionsPage, ParametersPage, CameraPage, AutoConnectionPage

# Handle Ctrl+C (SIGINT)
def signal_handler(sig, frame):
    print("\nSignal received, exiting...")
    sys.exit(0)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RobEn UAV Control Interface")
        self.setGeometry(100, 100, 1200, 800)
        
        # Central layout and tabs
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)

        # Add all tabs
        self.tab_widget.addTab(HomePage(), "Home")
        self.tab_widget.addTab(ReadingPage(), "Reading")
        self.tab_widget.addTab(MissionsPage(), "Missions")
        self.tab_widget.addTab(ParametersPage(), "Parameters")
        self.tab_widget.addTab(CameraPage(), "Camera")
        self.tab_widget.addTab(AutoConnectionPage(), "GCS Setup")

def main():
    signal.signal(signal.SIGINT, signal_handler)

    app = QApplication(sys.argv)
    app.setFont(QFont('Arial', 10))

    # Timer to keep Python responsive to SIGINT
    timer = QTimer()
    timer.timeout.connect(lambda: None)
    timer.start(100)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
    