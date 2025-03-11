from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QFileDialog, 
                            QLabel, QLineEdit, QGridLayout, QGroupBox,
                            QTableWidget, QHBoxLayout)
from PyQt6.QtCore import Qt
from utils.file_handlers import FileHandler

# todo read csv to csv option as well, along with the pdf optioni to table to csv, ensure to save outputs
class ReadingPage(QWidget):
    def __init__(self):
        super().__init__()
        self.file_handler = FileHandler()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        header_label = QLabel("Displaying CSV tables containing mission waypoints.")
        upload_button = QPushButton("Upload PDF")
        file_label = QLabel("Selected File:")
        selected_file_label = QLabel("")
        
        header_layout = QHBoxLayout()
        header_layout.addWidget(upload_button)
        header_layout.addWidget(file_label)
        header_layout.addWidget(selected_file_label)
        header_layout.addStretch()
        
        tables_layout = QHBoxLayout()
        table_names = ["Payload", "Table_0", "Table_1", "Table_2"]
        self.tables = []
        
        labels_layout = QHBoxLayout()
        for name in table_names:
            label = QLabel(name)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            labels_layout.addWidget(label)
        
        for _ in range(4):
            table = QTableWidget(11, 3)
            table.horizontalHeader().setVisible(False)
            table.horizontalHeader().setDefaultSectionSize(85)
            table.verticalHeader().setVisible(False)
            self.tables.append(table)
            tables_layout.addWidget(table)
        
        layout.addWidget(header_label)
        layout.addLayout(header_layout)
        layout.addLayout(labels_layout)
        layout.addLayout(tables_layout)
        
        upload_button.clicked.connect(lambda: self.browse_file(selected_file_label))

    def browse_file(self, label):
        filename, _ = QFileDialog.getOpenFileName(self, "Select PDF File", "", "PDF Files (*.pdf)")
        if filename:
            label.setText(filename)
            # todo continue rest of pdf reading logic