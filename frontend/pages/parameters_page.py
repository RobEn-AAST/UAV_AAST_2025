from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class ParametersPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Here goes parameters code"))