import sys
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QTabWidget,
    QVBoxLayout,
    QLabel
)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.tabs = QTabWidget()

        self.missions_tab = QWidget()
        self.readings_tab = QWidget()
        self.parameters_tab = QWidget()
        self.camera_tab = QWidget()

        self.tabs.addTab(self.missions_tab, "Missions")
        self.tabs.addTab(self.readings_tab, "Readings")
        self.tabs.addTab(self.parameters_tab, "Parameters")
        self.tabs.addTab(self.camera_tab, "Camera")

        self.setup_tabs()

        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        self.setLayout(layout)
        self.setWindowTitle("Multi-Tab Window")
        self.resize(1000, 1000)

    def setup_tabs(self):
        missions_layout = QVBoxLayout()
        missions_layout.addWidget(QLabel("Choose a mission"))
        self.missions_tab.setLayout(missions_layout)

        readings_layout = QVBoxLayout()
        readings_layout.addWidget(QLabel("converting to csv"))
        self.readings_tab.setLayout(readings_layout)

        parameters_layout = QVBoxLayout()
        parameters_layout.addWidget(QLabel("for parameter uploading"))
        self.parameters_tab.setLayout(parameters_layout)

        camera_layout = QVBoxLayout()
        camera_layout.addWidget(QLabel("Camera details"))
        self.camera_tab.setLayout(camera_layout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())