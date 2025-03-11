from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class CameraPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Here goes camera code"))