# -*- coding: utf-8 -*-
__title__ = "TYPES"
__doc__ = """Exports a CSV report listing all the wall types in the project.
Populate a name for each wall in Excel and push back into the model.

Click - EXPORT Excel List
Shift + Click - IMPORT Excel Report

Author: Máximo Cubero"""

__min_revit_ver__ = 2021
__max_revit_ver__ = 2026

# CONSTANTS
#==================================================
TRANSACTION_NAME    = "PARAMETER TYPES UPDATE"
KEYWORD             = "SKIP"
PATH_EXCEL          = r"C:\Users\34644\AppData\Roaming\Github pyRevit\Bimming.extension\Bimming.tab\Modify.Panel\Type Parameters.pushbutton\000-WALLS-External and Internal Wall Types.xlsx"

# IMPORTS
#==================================================

import sys
import os
import re
import clr
import sys
import traceback
from Snippets._bimcore_complex_def import *
from Snippets._bimcore_convert import *
from Snippets._bimcore_import import *
from Snippets._bimcore_functions import *

clr.AddReference("RevitServices")
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

clr.AddReference("RevitAPI")
from Autodesk.Revit.DB import *

clr.AddReference("RevitAPIUI")
from Autodesk.Revit.UI import TaskDialog

from System.Collections.Generic import List

import clr
clr.AddReference("Microsoft.Office.Interop.Excel")
from Microsoft.Office.Interop import Excel


# VARIABLES
#==================================================
doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app   = __revit__.Application

# MAIN
#==================================================

# File name
dic = excel_rows_to_dict(get_project_info_excel(doc, app), 1,0,1)
print(dic['File Name'])

# Project Number
test = r'Z:\{}\03 Technical\01 BIM\01 Revit\10 Resources\Type Parameters Tables'.format('test')
print(test)

# sys.exit()


TransactionManager.Instance.ForceCloseTransaction()
t = Transaction(doc, TRANSACTION_NAME)
t.Start()

# 1️⃣ EXTRACTING THE DATA FROM THE EXCEL
# Conver to a LIST the Excel
try:
    table = excel_read_via_com(PATH_EXCEL, sheet_name="Sheet1", required_col_index=1, stop_on_empty_first_row_col=True)
except:
    TaskDialog.Show("Warning-Excel Path", "Please ensure that both the Excel file and the Dynamo file are stored in the same folder and share the same file name.")
    sys.exit()

# PATH_EXCEL  = dynPath.rsplit('.', 1)[0] + ".xlsx"
# excel_file_name   = PATH_EXCEL.split('\\')[-1].replace('"', '')

# Conver the LIST to a Dict with subDict
data_dict = list_to_dict_excel(table, key_col_index=0, keyword=None)

# COLLECTING PARAMETERS - Exclude first parameter (model/KEY) and any parameter name containing 'SKIP'
# parameters = [x for x in table[0][1:] if KEYWORD not in x.upper()] # only use in the future if we want to skip parameters from the header
parameters = table[0][1:]

# 2️⃣ COLLECTING THE ELEMENTS
# We will select the CATEGORY base on the category name found in the Dynamo file name
# Normalize: remove non-letters and uppercase
excel_file_name = os.path.basename(PATH_EXCEL)

normalized_name = re.sub(r'[^A-Z]', '', excel_file_name.upper())

mapping = {
    "WINDOW": [BuiltInCategory.OST_Windows],
    "DOOR": [BuiltInCategory.OST_Doors],
    "WALL": [BuiltInCategory.OST_Walls],
    "FLOOR": [BuiltInCategory.OST_Roofs, BuiltInCategory.OST_Floors],
    "CEILING": [BuiltInCategory.OST_Ceilings],
    "GENERICMODEL": [BuiltInCategory.OST_GenericModel]
}

# Searching if the name of the dynamo file contains one of the categories listed
category_found_list = []
iList = List[BuiltInCategory]()
for keyword, categories in mapping.items():
    if keyword in normalized_name:
        for c in categories:
            iList.Add(c)
        category_found_list.append(keyword)

# Stop the operation if not match found
if not category_found_list:
    message =   "The name of the script must contain the name of the " \
                "category of the elements to be collected:\n\nWindow, Door, " \
                "Wall, Floor, Ceiling, Roof or Generic Model.\n\n" \
                "Please rename and run the script again."
    TaskDialog.Show("Category", message)
    sys.exit()

# Stop the operation if more than one categories is found
if len(category_found_list) > 1:
    message =   "It has been found {} categories in the name of the script:\n\n Script Name:\n {}\n\nCatergories found:\n{}\n\n" \
                "Ensure that only one category appears in the name: WINDOW, DOOR, WALL, FLOOR, CEILING, " \
                "ROOF or GENERIC MODEL.".format(str(len(category_found_list)), dynName, ", ".join(map(str, category_found_list)))
    TaskDialog.Show("Category", message)
    sys.exit()

category_selected = category_found_list[0]

# For Generic Models, we have to collect only the one that starts with the prefixes used in the Excel
if category_selected == 'GENERICMODEL':

    collector_generic_models =  FilteredElementCollector(doc)\
                                .WherePasses(ElementMulticategoryFilter(iList))\
                                .WhereElementIsElementType()\
                                .ToElements()

    prefixes = []
    for c in data_dict.keys():
        match = re.match(r"[A-Za-z]+", c)
        if match:
            prefixes.append(match.group(0))

    unique_prefixes = sorted(set(prefixes))

    collector = []

    for elem_type in collector_generic_models:
        model_value = elem_type.get_Parameter(BuiltInParameter.ALL_MODEL_MODEL).AsString()
        if not model_value:
            continue
        if any(model_value.startswith(pref) for pref in unique_prefixes):
            collector.append(elem_type)

# For any other category, we collect all the Types
else:
    collector = FilteredElementCollector(doc)\
    .WherePasses(ElementMulticategoryFilter(iList))\
    .WhereElementIsElementType()\
    .ToElements()

errors_1 = [['Family Name', 'Type', 'Model', 'Error/Warning Description']] # Collects families which miss the model value or did not found a match in the Excel
errors_2 = [['Model', 'Parameter', 'Error Description']] # Collects parameters that could not be populated

for elem_type in collector:

    # 3 FIRST WE CHECK THE MODELS VALUES IN THE TYPES
    type_name = elem_type.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString()
    family_name = getattr(elem_type, "FamilyName", "Unknown Family")
    model_value = elem_type.get_Parameter(BuiltInParameter.ALL_MODEL_MODEL).AsString()

    # checking if the model value is populated and there is a match in the Excel
    error = False
    categories_model_value_mandatory = ["WINDOW", "CEILING", "ROOF"] # "WALL", "FLOOR", could have types for placeholder that do not need a code.

    if not model_value or model_value == "":
        error_description_1 = "WARNING: MODEL value empty"
        error = True
    elif model_value and model_value not in data_dict.keys() and category_selected in categories_model_value_mandatory:
        error_description_1 = "ERROR: The model '{}' is not found in the Excel Table '{}'".format(model_value, excel_file_name)
        error = True
    elif model_value and model_value not in data_dict.keys():
        error_description_1 = "WARNING: The model '{}' was not found in the Excel Table '{}'. You can ignore this if the code is not applicable to the package".format(model_value, excel_file_name)
        error = True

    if error:
        errors_1.append([family_name, type_name, model_value, error_description_1])
        continue

    # 4 POPULATING THE PARAMETERS
    for parameter in parameters:
        revit_parameter = get_parameter_by_name(elem_type, parameter)
        error = False

        if revit_parameter:
            parameter_storage_type = revit_parameter.StorageType
            data_type = revit_parameter.Definition.GetDataType()
            parameter_value_from_excel = data_dict[model_value][parameter]

            # --- EMPTY CHECK FIRST (avoid unnecessary processing)
            if parameter_value_from_excel is None or parameter_value_from_excel == "":
                error_description_2 = ("The Excel cell is EMPTY. Please provide an appropriate value: "
                                       "for text parameters, use 'TBC', 'N/A', or '-'; "
                                       "for numeric parameters, use '0' if not applicable.")
                errors_2.append([model_value, parameter, error_description_2])
                continue

            # --- INTEGER
            if parameter_storage_type == StorageType.Integer:
                if data_type == SpecTypeId.Boolean.YesNo:
                    val = str(parameter_value_from_excel).upper()
                    if val == 'TRUE':
                        parameter_value = 1
                    elif val == 'FALSE':
                        parameter_value = 0
                    else:
                        storage_type = "YES/NO"
                        error = True
                else:
                    try:
                        parameter_value = int(parameter_value_from_excel)
                    except:
                        storage_type = "INTEGER"
                        error = True

            # --- DOUBLE
            elif parameter_storage_type == StorageType.Double:
                try:
                    parameter_value_ = float(parameter_value_from_excel)

                    if data_type == SpecTypeId.Length:
                        parameter_value = convert_internal_units(parameter_value_, get_internal=True, units='mm')

                    elif data_type == SpecTypeId.Area:
                        parameter_value = convert_internal_units(parameter_value_, get_internal=True, units='m2')

                    elif data_type == SpecTypeId.Number:
                        parameter_value = parameter_value_

                    else:
                        storage_type = "DOUBLE"
                        error = True

                except:
                    storage_type = "DOUBLE"
                    error = True

            # --- STRING
            elif parameter_storage_type == StorageType.String:
                try:
                    parameter_value = str(parameter_value_from_excel)
                except:
                    storage_type = "STRING"
                    error = True

            # --- ERROR HANDLING
            if error:
                if data_type == SpecTypeId.Boolean.YesNo:
                    error_description_2 = (
                        "The parameter '{}' is an {} (SpecTypeId = YesNo) and '{}' could not be converted. Use TRUE or FALSE."
                        .format(parameter, storage_type, str(parameter_value_from_excel))
                    )
                else:
                    error_description_2 = (
                        "The parameter '{}' is an {} (DataType = {}) and '{}' could not be converted."
                        .format(parameter, storage_type, data_type.TypeId, str(parameter_value_from_excel))
                    )

                errors_2.append([model_value, parameter, error_description_2])
                continue

            # --- SET VALUE
            revit_parameter.Set(parameter_value)

        else:
            error_description_2 = ("The parameter could not be found in the model. Possible reasons: "
                                   "A. The parameter does not exist in the project. "
                                   "B. The parameter exists but is not associated with the correct category. "
                                   "C. The parameter exists but is not a Type parameter.")
            errors_2.append([model_value, parameter, error_description_2])

#result = modules["rvt"].setParameterValue(element, parameter, value)

#modules["gen"].excelDispose(excel, wb, None, *lst)

t.Commit()
t.Dispose()

# ----------------------------------------------------------------------------------------------------- # OUTPUT

# if len(errors_1) == 1 and len(errors_2) == 1:
#     message = "No issues found."
# elif len(errors_1) == 1 and len(errors_2) > 1:
#     message = "{} element(s) found that require review.\n\nPlease check the Excel table that will open once you close this window.".format(len(errors_2) - 1)
# elif len(errors_1) > 1 and len(errors_2) == 1:
#     message = "{} element(s) found that require review.\n\nPlease check the Excel table that will open once you close this window.".format(len(errors_1) - 1)
# else:
#     message = "{} element(s) found that require review.\n\nPlease check the TWO Excel tables that will open once you close this window.".format(len(errors_1) - 1 + len(errors_2) - 1)
#
# modules["rvt"].showExecutionDialog(message)
# modules["gen"].excelReport(dynName, errors_1) if len(errors_1) > 1 else None
# modules["gen"].excelReport(dynName, errors_2) if len(errors_2) > 1 else None
# # modules["gen"].addLogDynamo(app, doc, dynVersion, dynPath, "", message)
#
# OUT = errors_1, errors_2, table


