from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QFileDialog, 
                            QLabel, QLineEdit, QGridLayout, QGroupBox)
from utils.file_handlers import FileHandler

class ReadingPage(QWidget):
    def __init__(self):
        super().__init__()
        self.file_handler = FileHandler()
        # Initialize dictionaries to store paths for each reader
        self.input_paths = {}
        self.output_paths = {}
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # PDF Section
        pdf_group = self.create_input_group("PDF Reader", self.read_pdf)
        layout.addWidget(pdf_group)
        
        # CSV Section
        csv_group = self.create_input_group("CSV Reader", self.read_csv)
        layout.addWidget(csv_group)
        
        layout.addStretch()

    def create_input_group(self, title, handler_func):
        group = QGroupBox(title)
        grid = QGridLayout()
        
        # Create unique input and output fields for this group
        self.input_paths[title] = QLineEdit()
        self.output_paths[title] = QLineEdit()
        
        # Input path
        input_label = QLabel("Input Path:")
        browse_input = QPushButton("Browse")
        browse_input.clicked.connect(
            lambda: self.browse_file(self.input_paths[title], "Select Input File"))
        
        # Output path
        output_label = QLabel("Output Path:")
        browse_output = QPushButton("Browse")
        browse_output.clicked.connect(
            lambda: self.browse_file(self.output_paths[title], "Select Output Location"))
        
        # Read button
        read_button = QPushButton(f"Read {title}")
        read_button.clicked.connect(lambda: handler_func(title))
        
        # Layout
        grid.addWidget(input_label, 0, 0)
        grid.addWidget(self.input_paths[title], 0, 1)
        grid.addWidget(browse_input, 0, 2)
        grid.addWidget(output_label, 1, 0)
        grid.addWidget(self.output_paths[title], 1, 1)
        grid.addWidget(browse_output, 1, 2)
        grid.addWidget(read_button, 2, 1)
        
        group.setLayout(grid)
        return group

    def browse_file(self, line_edit, title):
        filename, _ = QFileDialog.getOpenFileName(self, title, "", "All Files (*)")
        if filename:
            line_edit.setText(filename)

    def read_pdf(self, title):
        input_path = self.input_paths[title].text()
        output_path = self.output_paths[title].text()
        self.file_handler.handle_pdf(input_path, output_path)

    def read_csv(self, title):
        input_path = self.input_paths[title].text()
        output_path = self.output_paths[title].text()
        self.file_handler.handle_csv(input_path, output_path)