## Minimal Editing Branch.

Each tab of the program has its own .py file ending in "_tab_code".
Only these should be edited.

The file "editable_menu_tabs.ui" should be opened in Qt Designer located at `C:\Users\[user]\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.9_qbz5n2kfra8p0\LocalCache\local-packages\Python39\site-packages\qt5_applications\Qt\bin\designer.exe` after writing `pip install pyqt5` and `pip install pyqt5-tools`

After editing it as needed, write `python -m PyQt5.uic.pyuic -x editable_menu_tabs.ui -o editable_menu_tabs.py` to convert it to a .py file.

Then, write `python .\add_to_main.py "[letter]" "editable_menu_tabs.py"`, with the letter being m, c, or p for the mission, camera, and parameter tabs respectively depending on what you worked on. Don't edit other people's tabs.

Finally, run "main.py" from the "Minimal_Editing" folder but **never** edit it.

Use the CSV tab codes as examples.