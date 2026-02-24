# -*- coding: utf-8 -*-


# Imports
#==================================================
from Snippets._bimming_strings import *

import clr

clr.AddReference("Microsoft.Office.Interop.Excel")
from Microsoft.Office.Interop import Excel

clr.AddReference("RevitAPIUI")
from Autodesk.Revit.UI import TaskDialog
from Autodesk.Revit.UI.Selection import *

# Variables
#==================================================
app   = __revit__.Application
uidoc = __revit__.ActiveUIDocument
doc   = __revit__.ActiveUIDocument.Document #type:Document

# Functions
#==================================================

def excel_read_via_com(path, sheet_name="Sheet1", required_col_index=1, stop_on_empty_first_row_col=True):
    """
    Reads data from an Excel sheet using the COM interface, returning rows as lists.
    Allows restricting the number of read columns based on the first row and skipping
    rows missing required column values.

    Args:
        path (str): Full file path to the Excel file.
        sheet_name (str, optional): Name of the sheet to read. Defaults to "Sheet1".
        required_col_index (int, optional): Column index that must have a value for
                                            a row to be included. If None, all rows
                                            are included. Defaults to 1.
        stop_on_empty_first_row_col (bool, optional): If True, stops reading columns
                                                      once an empty cell is found
                                                      in the first row. Determines
                                                      the effective max column count.
                                                      Defaults to True.

    Returns:
        list[list]: A 2D list representing the sheet contents,
                    where each inner list holds the cell values of a row.
    """

    excel = Excel.ApplicationClass()
    excel.Visible = False
    wb = excel.Workbooks.Open(path)

    try:
        sheet = wb.Worksheets(sheet_name)
    except:
        sheet = wb.ActiveSheet

    used = sheet.UsedRange
    max_row = used.Rows.Count
    max_col = used.Columns.Count

    # Determine max column from first row
    if stop_on_empty_first_row_col:
        effective_max_col = 0
        for c in range(1, max_col + 1):
            v = sheet.Cells(1, c).Value2
            if v is None or v == "":
                break
            effective_max_col = c
    else:
        effective_max_col = max_col

    data = []

    for r in range(1, max_row + 1):

        # REQUIRED COLUMN MUST HAVE A VALUE
        if required_col_index is not None:
            req_value = sheet.Cells(r, required_col_index).Value2
            if req_value is None or req_value == "":
                # skip row entirely
                continue

        # normal reading of row
        row_data = []
        for c in range(1, effective_max_col + 1):
            val = sheet.Cells(r, c).Text
            row_data.append(val)

        data.append(row_data)

    wb.Close(False)
    excel.Quit()

    return data

def excel_rows_to_dict(data, start_row, key_col=0, value_col=1, stop_on_empty=True):
    """
    Converts a 2D list into a simple dictionary {key: value}.

    Args:
        data (list[list]): Full dataset from Excel.
        start_row (int): Row index where data begins (0-based).
        key_col (int): Column index for dictionary key.
        value_col (int): Column index for dictionary value.
        stop_on_empty (bool): Stop reading when key cell is empty.

    Returns:
        dict

    Raises:
        ValueError: If duplicate keys are found.
    """

    result = {}
    duplicates = []

    for row in data[start_row:]:

        if not row or len(row) <= key_col:
            continue

        key = row[key_col]

        if key is None or key == "":
            if stop_on_empty:
                break
            continue

        value = None
        if len(row) > value_col:
            value = row[value_col]

        if key in result:
            duplicates.append(key)
            continue

        result[str(key)] = str(value) if value is not None else None

    # if duplicates:
    #     raise ValueError(
    #         "Duplicate keys found: {}".format(", ".join(map(str, duplicates)))
    #     )

    # ---------------------------------------
    # POP-UP WARNING AND STOP SCRIPT
    # ---------------------------------------
    if duplicates:
        message = (
            "Duplicate keys were found:\n\n{}\n\n"
            "Please fix the data and run the script again."
        ).format(", ".join(map(str, duplicates)))

        TaskDialog.Show("Duplicate Keys Found", message)
        raise SystemExit("Duplicate keys detected")

    return result

    return result