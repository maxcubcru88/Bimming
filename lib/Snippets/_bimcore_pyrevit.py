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
    """Write structured data to an Excel workbook.

    Behavior:
        - If `datadict` contains a single item, the worksheet is named "Sheet1".
        - If it contains multiple items, each key is used as a worksheet name.
        - Each value in the dictionary must be an iterable of rows, where each
          row is an iterable of cell values.

    Args:
        xlfile (str):
            Full file path of the target Excel file.

        datadict (dict[str, list[list]]):
            Dictionary mapping worksheet names to tabular data.
            Example:
                {
                    "SheetA": [
                        ["Header1", "Header2"],
                        [1, 2],
                        [3, 4]
                    ],
                    "SheetB": [
                        ["OnlyColumn"],
                        ["Value"]
                    ]
                }

    Notes:
        - Worksheet names are automatically set to "Sheet1" when only one
          dataset is provided, to match Excel defaults.
        - When multiple datasets are provided, worksheet names must be unique
          and comply with Excel naming rules (<= 31 chars, no []:*?/\\).
    """
    xlwb = xlsxwriter.Workbook(xlfile)

    single_sheet = len(datadict) == 1

    for i, (xlsheetname, xlsheetdata) in enumerate(datadict.items()):
        sheet_name = "Sheet1" if single_sheet else xlsheetname
        xlsheet = xlwb.add_worksheet(sheet_name)

        for idx, data in enumerate(xlsheetdata):
            if not isinstance(data, (list, tuple)):
                data = [data]
            xlsheet.write_row(idx, 0, data)

    xlwb.close()

def dump2(xlfile, datadict):
    """Write structured data to an Excel workbook with basic formatting.

    Features:
        - Single dataset → sheet named "Sheet1"
        - Multiple datasets → sheet names from dict keys
        - Auto column width (based on content)
        - Bold header row (first row)
        - Freeze top row
        - Autofilter applied to header row

    Args:
        xlfile (str): Full file path of the target Excel file
        datadict (dict[str, list[list]]): Sheet name → tabular data
    """
    xlwb = xlsxwriter.Workbook(xlfile)
    header_format = xlwb.add_format({'bold': True})

    single_sheet = len(datadict) == 1

    for xlsheetname, xlsheetdata in datadict.items():
        sheet_name = "Sheet1" if single_sheet else xlsheetname
        xlsheet = xlwb.add_worksheet(sheet_name)

        col_widths = {}
        max_width = 50  # cap to avoid huge columns

        for row_idx, data in enumerate(xlsheetdata):
            if not isinstance(data, (list, tuple)):
                data = [data]

            # Apply header format to first row
            fmt = header_format if row_idx == 0 else None
            xlsheet.write_row(row_idx, 0, data, fmt)

            # Track column widths
            for col_idx, cell in enumerate(data):
                cell_len = len(str(cell))
                col_widths[col_idx] = max(col_widths.get(col_idx, 0), cell_len)

        # Set column widths
        for col_idx, width in col_widths.items():
            width = min(width + 2, max_width)
            xlsheet.set_column(col_idx, col_idx, width)

        # Freeze top row
        xlsheet.freeze_panes(1, 0)

        # Apply autofilter (only if there's at least 1 data row)
        if xlsheetdata:
            last_col = len(xlsheetdata[0]) - 1
            last_row = len(xlsheetdata) - 1
            xlsheet.autofilter(0, 0, last_row, last_col)

    xlwb.close()