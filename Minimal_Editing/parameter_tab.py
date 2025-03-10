
#! Anything written here will be deleted.

from PyQt5 import QtCore, QtGui, QtWidgets
from sys import path
path.append("../tab_widgets")
from parameter_tab_code import code

def parameter_tab(self):

        self.parameter_tab = QtWidgets.QWidget()
        self.parameter_tab.setObjectName("parameter_tab")
        self.parameter_label = QtWidgets.QLabel(self.parameter_tab)
        self.parameter_label.setGeometry(QtCore.QRect(10, 10, 91, 31))
        self.parameter_label.setObjectName("parameter_label")
        self.tabWidget.addTab(self.parameter_tab, "")
        code(self)

def parameter_elements(self):
        _translate = QtCore.QCoreApplication.translate
        self.csv_label.setText(_translate("Dialog", "Displaying CSV tables containing mission waypoints."))
        self.PDFButton.setText(_translate("Dialog", "Upload PDF"))
        self.Selection_label.setText(_translate("Dialog", "Selected File:"))
