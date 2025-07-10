from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QFileDialog,
    QLabel, QTableWidget, QHBoxLayout, QTableWidgetItem
)
from PyQt6.QtCore import Qt
from frontend.utils.file_handlers import FileHandler
from frontend.utils.pdf_reader import convert_pdf
from csv import reader
import os

class ReadingPage(QWidget):
    def __init__(self):
        super().__init__()
        self.file_handler = FileHandler()
        self.init_ui()

        global current_self
        current_self = self

    def init_ui(self):
        layout = QVBoxLayout(self)

        header_label = QLabel("Displaying CSV tables containing mission waypoints.")

        # NEW: Add Upload CSV button
        upload_pdf_button = QPushButton("Upload PDF")
        upload_csv_button = QPushButton("Upload CSV")

        file_label = QLabel("Selected File:")
        selected_file_label = QLabel("")

        # Header layout with both buttons
        header_layout = QHBoxLayout()
        header_layout.addWidget(upload_pdf_button)
        header_layout.addWidget(upload_csv_button)
        header_layout.addWidget(file_label)
        header_layout.addWidget(selected_file_label)
        header_layout.addStretch()

        # Tables area
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

        # Connections
        upload_pdf_button.clicked.connect(lambda: self.browse_pdf_file(selected_file_label))
        upload_csv_button.clicked.connect(lambda: self.browse_csv_file(selected_file_label))

    def browse_pdf_file(self, label):
        global file_name, file_type
        file_name, file_type = QFileDialog.getOpenFileName(self, "Select PDF File", "", "PDF Files (*.pdf)")
        if file_name:
            clicker()

    def browse_csv_file(self, label):
        csv_file, _ = QFileDialog.getOpenFileName(self, "Select CSV File", "", "CSV Files (*.csv)")
        if not csv_file:
            return

        label.setText(os.path.basename(csv_file))

        try:
            with open(csv_file, 'r') as f:
                datareader = reader(f)
                all_coords = [row for row in datareader]

            # Divide into 4 chunks for 4 tables
            chunk_size = len(all_coords) // 4
            for i in range(4):
                start = i * chunk_size
                end = (i + 1) * chunk_size if i < 3 else len(all_coords)
                chunk = all_coords[start:end]
                self.populate_table(self.tables[i], chunk)

        except Exception as e:
            print(f"Error loading CSV: {e}")

    def populate_table(self, table, data):
        table.clearContents()
        for i, coord in enumerate(data):
            if len(coord) < 3:
                continue
            lat = QTableWidgetItem(coord[0])
            lon = QTableWidgetItem(coord[1])
            alt = QTableWidgetItem(coord[2])

            table.setItem(i, 0, lat)
            table.setItem(i, 1, lon)
            table.setItem(i, 2, alt)

def clicker():
    if file_name:
        if file_name.endswith(".pdf"):
            convert_pdf(file_name)
            for i in range(1, 5):
                list_to_table(current_self.tables[i - 1], i - 1)

def list_to_table(table, num):
    coord_list = csv_to_list()
    for i, coord in enumerate(coord_list[num]):
        lat_coord = QTableWidgetItem(coord[0])
        lon_coord = QTableWidgetItem(coord[1])
        alt_coord = QTableWidgetItem(coord[2])

        table.setItem(i, 0, lat_coord)
        table.setItem(i, 1, lon_coord)
        table.setItem(i, 2, alt_coord)

def csv_to_list():
    coord_list_list = []
    filepath = (__file__.replace("pages", "utils\\Output\\")).replace(os.path.basename(__file__), '')
    dirlist = os.listdir(filepath)

    dirlist = [f for f in dirlist if f.endswith(".csv")]

    for filename in dirlist:
        with open((filepath + filename), 'r') as csvfile:
            datareader = reader(csvfile)
            coord_list = []
            for row in datareader:
                coord_list.append(row)
            coord_list_list.append(coord_list)

    return coord_list_list
