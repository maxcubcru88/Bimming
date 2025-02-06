# -*- coding: utf-8 -*-


# Imports
#==================================================
from Autodesk.Revit.DB import *
import csv
import codecs

# Variables
#==================================================
app   = __revit__.Application
uidoc = __revit__.ActiveUIDocument
doc   = __revit__.ActiveUIDocument.Document #type:Document

# Functions
#==================================================

def export_to_csv(file_path, data):
    """Exports the given data to a CSV file at the specified file path.

    Args:
        file_path (str): The path where the CSV file will be saved.
        data (list of lists): The data to write to the CSV file. Each inner list represents a row.

    Returns:
        str: The file path where the CSV file was saved.
    """
    # Open the file with codecs and utf-8 encoding
    with codecs.open(file_path, 'w', 'utf-8') as file:
        writer = csv.writer(file, lineterminator='\n')
        writer.writerows(data)
    return  file_path
