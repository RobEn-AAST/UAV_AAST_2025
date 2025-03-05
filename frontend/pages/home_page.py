from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel)
from PyQt6.QtCore import Qt

class HomePage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("RobEn")
        title.setStyleSheet("""
            font-size: 48px;
            font-weight: bold;
            color: #2c3e50;
            margin: 20px;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Subtitle
        subtitle = QLabel("UAV Control System")
        subtitle.setStyleSheet("""
            font-size: 24px;
            color: #34495e;
            margin-bottom: 40px;
        """)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addStretch()