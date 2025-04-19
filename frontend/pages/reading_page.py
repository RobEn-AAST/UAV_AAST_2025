from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QFileDialog, 
                            QLabel, QLineEdit, QGridLayout, QGroupBox,
                            QTableWidget, QHBoxLayout, QTableWidgetItem)
from PyQt6.QtCore import Qt
from utils.file_handlers import FileHandler
from utils.pdf_reader import convert_pdf
from csv import reader
import os

# todo read csv to csv option as well, along with the pdf option to table to csv, ensure to save outputs
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
        #print(self.tables[1])
        global file_name, file_type
        file_name, file_type = QFileDialog.getOpenFileName(self, "Select PDF File", "", "PDF Files (*.pdf)")
        if file_name:
            #label.setText(file_name)
            clicker()

def clicker():
    #file_name, file_type = QFileDialog.getOpenFileName(None, "Open File", "", "PDF(*.pdf)")
    if file_name:
        #current_self.selected_file_label.setText(file_name)
        if file_name.endswith(".pdf"):
            convert_pdf(file_name)
            for i in range(1, 5):
                #list_to_table(eval("current_self.csv_table_" + str(i)), i-1)
                list_to_table(current_self.tables[i-1], i-1)
        else:
            #current_self.selected_file_label.setText("Please choose a PDF.")
            pass

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

    for i in range(len(dirlist)-1):
        if str(dirlist[i]).endswith(".csv") == False:
            dirlist.pop(i)

    for i in dirlist:
        with open((filepath + i), 'r') as csvfile:
            datareader = reader(csvfile)
            coord_list = []
            for row in datareader:
                coord_sublist = []
                for column in row:
                    coord_sublist.append(column)
                coord_list.append(coord_sublist)
            coord_list_list.append(coord_list)

    return coord_list_list