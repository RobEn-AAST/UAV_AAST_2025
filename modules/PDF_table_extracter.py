
# Import libraries.
from pdf2docx import Converter
from sys import platform
import docx
import csv
import os
import Data_loader

# Function used to know if a number is a string.
def is_float(string):
    try:
        if string == string.replace(".", "") and float(string):
            return False
        elif float(string.replace(".", "")):
            return True
    except ValueError:
        return False

#? Do you want the number of each row to appear at the start?
#! If so, keep this variable True. If not, make it False.
row_numbers = True

# Automatically find file paths.
filepath = (__file__ + "\\").replace(os.path.basename(__file__), '')
input_path = "Input\\"
output_path = "Output\\"
# Change file path if the code is running on Linux.
if platform == "linux" or platform == "linux2":
    filepath = (__file__).replace(os.path.basename(__file__),'')
    input_path = "Input/"
    output_path = "Output/"

#! Rename "converted.pdf" to whatever the name of the provided PDF is!
#pdf = filepath + "converted.pdf"
config_file = 'C:/Users/Mostafa/PycharmProjects/fixed wing pymavlink/files/data.json'
data_loader = Data_loader(config_file)
data_loader.load_config()
pdf =
docx_file =

# Converting a PDF to a .docx file.
cv = Converter(pdf)
cv.convert(docx_file)

cv.close()
# Converting the PDF to .docx is done.

# Reading the text in the tables starts.
doc = docx.Document(docx_file)

# Printing the text in the cells of each row of each table.
# The entire row will be printed on the same line.
for table_count, table in enumerate(doc.tables):

    # Defining start and names of CSV files.
    new_csv_values = [["n", "lat", "lon"]]
    csv_name = output_path + "table_" + str(table_count) + ".csv"
    
    for row_count, row in enumerate(table.rows):

        inside_new_csv_values = []

        if row_numbers:
            print(row_count+1, end = '        ')

        next_line = False

        for cell_count, cell in enumerate(row.cells):
            # If it is the final value in the row, print a line break at the end.
            if cell_count == len(row.cells)-1:
                next_line = True

            if next_line == False:
                print(cell.text, end = '        ')
            else:
                print(cell.text)

            # Store the text to be written in the CSV.
            if is_float(cell.text):
                inside_new_csv_values.append(float(cell.text))

            # Determine drop location from the row comment.
            if (cell.text).replace(" ", "") == "DropLocation":

                payload_coords = [["n", "lat", "lon"]]
                payload_coords.append(inside_new_csv_values)
                inside_new_csv_values = []

                # Make a special CSV file for the drop location.
                with open((output_path + "Payloads.csv"), 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerows(payload_coords)

        # Add non-empty lists of numbers to the...
        #... 2D list that stores the entire CSV files.
        if inside_new_csv_values != []:
            new_csv_values.append(inside_new_csv_values)

    # Turn the current table into a CSV file.
    with open(csv_name, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(new_csv_values)