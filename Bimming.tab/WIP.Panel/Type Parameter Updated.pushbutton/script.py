# -*- coding: utf-8 -*-
__title__ = "Type Parameter\nUpdater WN"
__doc__ = """Select instances.

Author: Máximo Cubero"""

__min_revit_ver__ = 2021
__max_revit_ver__ = 2025

# CONSTANTS
#==================================================
TRANSACTION_NAME    = "PARAMETER TYPES UPDATE"
KEYWORD             = "SKIP"
PATH_EXCEL          = r"C:\Users\34644\AppData\Roaming\Github pyRevit\Bimming.extension\Bimming.tab\Modify.Panel\Type Parameter Updated.pushbutton\test.xlsx"

# IMPORTS
#==================================================
import sys
import System
from System.Collections.Generic import List

from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import TaskDialog
from Snippets._bimcore_export import *
from Snippets._bimcore_functions import *

import clr
clr.AddReference("Microsoft.Office.Interop.Excel")
from Microsoft.Office.Interop import Excel

# VARIABLES
#==================================================
doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

# MAIN
#==================================================

def read_excel_via_com(path, sheet_name="Sheet1", required_col_index=1, stop_on_empty_first_row_col=True):
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
            val = sheet.Cells(r, c).Value2
            row_data.append(val)

        data.append(row_data)

    wb.Close(False)
    excel.Quit()

    return data

def list_to_dict_excel(data, key_col_index=0, keyword=None):
    """
    Converts a 2D list (such as data read from Excel) into a dictionary
    keyed by a specified column, optionally filtering out headers
    containing a keyword, and detecting duplicate keys.

    Args:
        data (list[list]): The full dataset where data[0] contains headers.
        key_col_index (int, optional): Index of the column used as the dictionary key.
                                       Default is 0.
        keyword (str, optional): If provided, any column whose header contains this keyword
                                 (case-insensitive) will be skipped.

    Returns:
        dict: A dictionary where each key is taken from key_col_index and maps to
              a sub-dictionary of remaining header/value pairs.

    Raises:
        SystemExit: If duplicate keys are found in key_col_index.
    """

    headers = data[0]
    result = {}
    duplicates = []

    for row in data[1:]:
        # Skip empty or insufficient rows
        if not row or len(row) <= key_col_index:
            continue

        key = row[key_col_index]
        if key is None:
            continue

        # Detect duplicates
        if key in result:
            duplicates.append(key)
            continue

        item = {}
        for i, value in enumerate(row):
            if i < len(headers):
                header = headers[i]

                # Skip the key column
                if i == key_col_index:
                    continue

                # Skip fields whose header contains the keyword
                if keyword and keyword.lower() in str(header).lower():
                    continue

                item[header] = value

        result[key] = item

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

def get_parameter_by_name(element, param_name):
    """
    Returns the Revit Parameter object from an element
    using the parameter's name text.

    Args:
        element: Revit element
        param_name (str): Parameter name

    Returns:
        Parameter object or None if not found
    """
    for param in element.Parameters:
        if param.Definition.Name == param_name:
            return param
    return None

# 1️⃣ EXTRACTING THE DATA FROM THE EXCEL
# Conver to a LIST the Excel
table = read_excel_via_com(PATH_EXCEL, sheet_name="Sheet1", required_col_index=1, stop_on_empty_first_row_col=True)

# Conver the LIST to a Dict with subDict
data_dict = list_to_dict_excel(table, key_col_index=0, keyword=None)

# COLLECTING PARAMETERS - Exclude first parameter (model/KEY) and any parameter name containing 'SKIP'
# parameters = [x for x in table[0][1:] if KEYWORD not in x.upper()] # only use in the future if we want to skip parameters from the header
parameters = table[0][1:]

# 2️⃣ COLLECTING THE ELEMENTS
iList = List[BuiltInCategory]()
iList.Add(BuiltInCategory.OST_Windows)
# iList.Add(BuiltInCategory.OST_Walls)

collector = FilteredElementCollector(doc)\
            .WherePasses(ElementMulticategoryFilter(iList))\
            .WhereElementIsElementType()\
            .ToElements()

errors_1 = [['Family Name', 'Type', 'Model', 'Error Description']] # Collects families which miss the model value or did not found a match in the Excel
errors_2 = [['Model', 'Parameter', 'Error Description']] # Collects parameters that could not be populated

# 🔓 Start a transaction
t = Transaction(doc, TRANSACTION_NAME)
t.Start()

for elem_type in collector:

    # 3️⃣ FIRST WE CHECK THE MODELS VALUES IN THE TYPES
    type_name = elem_type.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString()
    family_name = getattr(elem_type, "FamilyName", "Unknown Family")
    model_value = elem_type.get_Parameter(BuiltInParameter.ALL_MODEL_MODEL).AsString()

    # checking if the model value is populated and there is a match in the Excel
    error = False

    if not model_value or model_value == "":
        error_description_1 = "A MODEL value has not yet been assigned to this type."
        error = True
    elif model_value and model_value not in data_dict.keys():
        error_description_1 = "The model '{}' is not found in the Excel Table '{}'".format(model_value, PATH_EXCEL)
        error = True

    if error:
        errors_1.append([family_name, type_name, model_value, error_description_1])
        continue

    # 4️⃣ POPULATING THE PARAMETERS
    for parameter in parameters:
        revit_parameter = get_parameter_by_name(elem_type, parameter)
        error = False
        if revit_parameter:
            parameter_storage_type = revit_parameter.StorageType
            # print([parameter, revit_parameter, parameter_storage_type])
            parameter_value_from_excel = data_dict[model_value][parameter]
            if parameter_storage_type == StorageType.Integer:
                try:
                    parameter_value = int(parameter_value_from_excel)
                except:
                    storage_type = "INTEGER"
                    error = True
            elif parameter_storage_type == StorageType.Double:
                try:
                    parameter_value = float(parameter_value_from_excel)
                except:
                    storage_type = "DOUBLE"
                    error = True
            elif parameter_storage_type == StorageType.String:
                try:
                    parameter_value = str(parameter_value_from_excel)
                except:
                    storage_type = "STRING"
                    error = True

            if not parameter_value_from_excel or parameter_value_from_excel == "":
                error_description_2 = ("The cell in the Excel is EMPTY. Please fill it with an appropriate value.\n"
                                       "If it is a text parameter, use something like 'TBC', 'N/A', or '-'.\n"
                                       "If it is a number or area, use '0' if it is not applicable.")
                errors_2.append([model_value, parameter, error_description_2])
                continue

            if error:
                error_description_2 = ("There parameter '{}' is an {} and '{}' could not be converted to it."
                                       .format(parameter, storage_type, str(parameter_value_from_excel)))
                errors_2.append([model_value, parameter, error_description_2])
                continue

            revit_parameter.Set(parameter_value)

        else:
            error_description_2 = ("The parameter '{}' couldn’t be found in the model. Possible reasons:\n"
                                   "A. The parameters does not exits in the project.\n"
                                   "B. The parameter exists but it is not associated with the appropriate category.\n"
                                   "C. The parameter exists but it is not a Type parameter.").format(parameter)
            errors_2.append([model_value, parameter, error_description_2])

# 🔒Closing transaction
t.Commit()

# for error in errors_1:
#     for e in error:
#         print(e)
#     print("\n  ")
# for error in errors_2:
#     for e in error:
#         print(e)
#     print("\n  ")

# Combining reports
errors = errors_1 + [[]] +  errors_2

# 5️⃣ Export report
if len(errors) > 1:

    project_info = get_project_info(doc, app)

    directory = create_report_directory('Bimming_Type Parameter Updater')
    dic = list_to_dict(project_info)
    file_name = dic['File Name']
    report_name = generate_report_name(file_name)

    # 4️⃣Export the report
    # Create the full file path with the .csv extension
    csv_file_path = os.path.join(directory, report_name[0] + ".csv")

    data = project_info + errors
    export_to_csv(csv_file_path, data)