
# Import libraries.
from pdf2docx import Converter
from sys import platform
from os import path
import docx
import csv

# Function used to know if a number is a string.
def is_float(string):
    try:
        if string == string.replace(".", "") and float(string):
            return False
        elif float(string.replace(".", "")):
            return True
    except ValueError:
        return False

def convert_pdf(pdf):
    filepath = (__file__ + "\\").replace(path.basename(__file__), '')
    output_path = filepath + "Output\\"
    if platform == "linux" or platform == "linux2":
        filepath = (__file__).replace(path.basename(__file__), '')
        output_path = filepath + "Output/"
    docx_file = output_path + "new_converted.docx"

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
        new_csv_values = [["lat", "lon", "alt"]]
        csv_name = output_path + "table_" + str(table_count) + ".csv"
        
        for row_count, row in enumerate(table.rows):

            inside_new_csv_values = []

            next_line = False

            for cell_count, cell in enumerate(row.cells):
                # If it is the final value in the row, print a line break at the end.
                if cell_count == len(row.cells)-1:
                    next_line = True

                """if next_line == False:
                    print(cell.text, end = '        ')
                else:
                    print(cell.text)"""

                # Store the text to be written in the CSV.
                if is_float(cell.text):
                    inside_new_csv_values.append(float(cell.text))

                # Determine drop location from the row comment.
                if (cell.text).replace(" ", "") == "DropLocation":
                    if len(inside_new_csv_values) == 2:
                        inside_new_csv_values.append(80)

                    payload_coords = [["lat", "lon", "alt"]]
                    payload_coords.append(inside_new_csv_values)
                    inside_new_csv_values = []

                    # Make a special CSV file for the drop location.
                    with open((output_path + "Payloads.csv"), 'w', newline='') as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerows(payload_coords)

            # Add non-empty lists of numbers to the...
            #... 2D list that stores the entire CSV files.
            if inside_new_csv_values != []:
                if len(inside_new_csv_values) == 2:
                    inside_new_csv_values.append(80)
                new_csv_values.append(inside_new_csv_values)

        # Turn the current table into a CSV file.
        with open(csv_name, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(new_csv_values)