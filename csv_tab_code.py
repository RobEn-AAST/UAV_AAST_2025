
from PyQt5 import QtCore, QtGui, QtWidgets
QTableWidgetItem = QtWidgets.QTableWidgetItem
from PDF_Reader_Files.PDF_table_extracter import convert_pdf
from csv import reader
import os

#! \/ Main function.
def code(self):
    self.PDFButton.clicked.connect(clicker)
    #! Write any code in this function above this line.
    global current_self
    current_self = self

def clicker():
    file_name, file_type = QtWidgets.QFileDialog.getOpenFileName(None, "Open File", "",
                                                      "PDF(*.pdf)")
    if file_name:
        current_self.Selected_label.setText(file_name)
        if file_name.endswith(".pdf"):
            convert_pdf(file_name)
            for i in range(1, 5):
                list_to_table(eval("current_self.csv_table_" + str(i)), i-1)
        else:
            current_self.Selected_label.setText("Please choose a PDF.")

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
    filepath = (__file__ + "\\PDF_Reader_Files\\Output\\").replace(os.path.basename(__file__), '')
    dirlist = os.listdir(filepath)

    for i in range(len(dirlist)-1):
        if str(dirlist[i]).endswith(".csv") == False:
            dirlist.pop(i)
    #print(dirlist)

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