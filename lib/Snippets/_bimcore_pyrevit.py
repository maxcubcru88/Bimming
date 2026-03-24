# -*- coding: utf-8 -*-

# Imports
#==================================================
from Autodesk.Revit.DB import *
import xlsxwriter

# Variables
#==================================================
app   = __revit__.Application
uidoc = __revit__.ActiveUIDocument
doc   = __revit__.ActiveUIDocument.Document #type:Document

# Functions
#==================================================

def dump(xlfile, datadict):
    """Write data to Excel file.

    Creates a worksheet for each item of the input dictionary.

    Args:
        xlfile (str): full path of the target Excel file
        datadict (dict[str, list]): dictionary of worksheets names and data
    """
    xlwb = xlsxwriter.Workbook(xlfile)
    # bold = xlwb.add_format({'bold': True})
    for xlsheetname, xlsheetdata in datadict.items():
        # xlsheet = xlwb.add_worksheet(xlsheetname)
        xlsheet = xlwb.add_worksheet("Sheet1")
        for idx, data in enumerate(xlsheetdata):
            xlsheet.write_row(idx, 0, data)
    xlwb.close()