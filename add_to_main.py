
import sys

def universal_path_slash():

    path_slash = "\\"
    # Change file path if the code is running on Linux.
    if sys.platform == "linux" or sys.platform == "linux2":
        path_slash = "/"
    
    return path_slash

def convert(type, num):
    start_sentence = "self.{}_tab = QtWidgets.QWidget()".format(type)
    end_sentence = 'self.tabWidget.addTab(self.{}_tab, "")'.format(type)
    find_end = False
    write_lines = [
        "\n", "#! Anything written here will be deleted.\n", "\n",
        "from PyQt5 import QtCore, QtGui, QtWidgets\n",
        "from sys import path\n", 'path.append("../tab_widgets")\n',
        "from {}_tab_code import code\n".format(type), "\n",
        "def {}_tab(self):\n".format(type), "\n"
        ]
    
    tab_sentences = [
        'Dialog.setWindowTitle(_translate("Dialog", "RobEn_GUI_Utility"))',
        'self.tabWidget.setTabText(self.tabWidget.indexOf(self.mission_tab), _translate("Dialog", "Missions"))',
        'self.tabWidget.setTabText(self.tabWidget.indexOf(self.csv_tab), _translate("Dialog", "CSV"))',
        'self.tabWidget.setTabText(self.tabWidget.indexOf(self.parameter_tab), _translate("Dialog", "Parameters"))',
        'self.tabWidget.setTabText(self.tabWidget.indexOf(self.camera_tab), _translate("Dialog", "Camera"))']
    tab_write_lines = []
    find_tab_end = False
    if type == "mission":
        tab_index = 0
    elif type == "csv":
        tab_index = 1
    elif type == "parameter":
        tab_index = 1
    elif type == "camera":
        tab_index = 1

    with open(sys.argv[num], 'r') as code:
        lines = code.readlines()
        for line in lines:
            if line.find(start_sentence) != -1 and find_end == False:
                find_end = True

            if find_end:
                write_lines.append(line)

            if line.find(end_sentence) != -1 and find_end:
                find_end = False

            if line.find(tab_sentences[tab_index]) != -1 and find_tab_end == False:
                find_tab_end = True
            
            if find_tab_end:
                tab_write_lines.append(line)

            if line.find(tab_sentences[tab_index+1]) != -1 and find_tab_end:
                find_tab_end = False


    path_slash = universal_path_slash()

    new_file = open('Minimal_Editing'+path_slash+'{}_tab.py'.format(type), 'w')
    for i in write_lines:
        new_file.write(i)
    new_file.write("        code(self)")

    tab_write_lines.pop(0)
    tab_write_lines.pop(-1)
    tab_write_lines.insert(0, "        _translate = QtCore.QCoreApplication.translate\n")
    tab_write_lines.insert(0, "\n\ndef {}_elements(self):\n".format(type))
    for i in tab_write_lines:
        new_file.write(i)

    new_file.close()

    print("Successfully integrated your changes to {}.".format(type))


def switch(arg, num):
    if arg == ("m" or "mission"):
        convert("mission", num)
    elif arg == ("c" or "camera"):
        convert("camera", num)
    elif arg == ("p" or "parameter"):
        convert("parameter", num)
    elif arg == "csv":
        convert("csv", num)
    elif arg == "all":
        print("Please don't use this.")
        if input("Terminate immediately using ctrl + c.") == "y":
            if input("GitHub will record your actions.") == "y":
                convert("mission", num)
                convert("camera", num)
                convert("parameter", num)
                convert("csv", num)
    else:
        print("No tab type specifiec. Check if you used the correct letter.")

n = len(sys.argv)
if n > 3:
    print("Too many arguments passed.")
    exit()
elif n < 3:
    print("Too few arguments passed.")
    exit()

if sys.argv[1].endswith(".py"):
    switch(sys.argv[2], 1)
elif sys.argv[2].endswith(".py"):
    switch(sys.argv[1], 2)
else:
    print("No file specified. Check its name ends with '.py'")