
#! Anything written here will be deleted.

from PyQt5 import QtCore, QtGui, QtWidgets
from sys import path
path.append("../tab_widgets")
from mission_tab_code import code

def mission_tab(self):

        self.mission_tab = QtWidgets.QWidget()
        self.mission_tab.setObjectName("mission_tab")
        self.mission_label = QtWidgets.QLabel(self.mission_tab)
        self.mission_label.setGeometry(QtCore.QRect(10, 10, 171, 31))
        self.mission_label.setObjectName("mission_label")
        self.tabWidget.addTab(self.mission_tab, "")
        code(self)

def mission_elements(self):
        _translate = QtCore.QCoreApplication.translate
        self.mission_label.setText(_translate("Dialog", "Mission selection and monitoring"))
