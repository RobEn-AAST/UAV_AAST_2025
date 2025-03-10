
#! Anything written here will be deleted.

from PyQt5 import QtCore, QtGui, QtWidgets
from sys import path
path.append("../tab_widgets")
from camera_tab_code import code

def camera_tab(self):

        self.camera_tab = QtWidgets.QWidget()
        self.camera_tab.setObjectName("camera_tab")
        self.camera_label = QtWidgets.QLabel(self.camera_tab)
        self.camera_label.setGeometry(QtCore.QRect(10, 10, 221, 31))
        self.camera_label.setObjectName("camera_label")
        self.tabWidget.addTab(self.camera_tab, "")
        code(self)

def camera_elements(self):
        _translate = QtCore.QCoreApplication.translate
        self.csv_label.setText(_translate("Dialog", "Displaying CSV tables containing mission waypoints."))
        self.PDFButton.setText(_translate("Dialog", "Upload PDF"))
        self.Selection_label.setText(_translate("Dialog", "Selected File:"))
