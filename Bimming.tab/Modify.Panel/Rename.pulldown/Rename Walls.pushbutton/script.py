# -*- coding: utf-8 -*-
__title__ = "Rename\nWalls"
__doc__ = """Exports a CSV report listing all the wall types in the project.
Populate a name for each wall in Excel and push back into the model.

Click - EXPORT Excel List
Shift + Click - IMPORT Excel Report

Author: Máximo Cubero"""

__min_revit_ver__ = 2021
__max_revit_ver__ = 2025

# CONSTANTS
#==================================================
TRANSACTION_NAME = "Rename Wall Types"

# IMPORTS
#==================================================
import sys
from pyrevit import forms
from Snippets._bimming_export import *
from Snippets._bimming_import import *
from Snippets._bimming_functions import *
from pyrevit import EXEC_PARAMS

# VARIABLES
#==================================================
doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app   = __revit__.Application

# MAIN
#==================================================

elements = FilteredElementCollector(doc).OfClass(WallType).ToElements()

# Define exclusions based on config mode
# PUSH DATA
if EXEC_PARAMS.config_mode:

    # 1️⃣ Read data from Excel and create dic
    directory = create_report_directory('Bimming_Rename Wall Types', False)
    excel_path = forms.pick_file(title="Select Excel file with new wall names", file_ext='xlsx',init_dir=directory)
    if not(excel_path):
        sys.exit()
    data = excel_read_via_com(excel_path, required_col_index=1, stop_on_empty_first_row_col=False)
    dic_excel = excel_rows_to_dict(data,7) # to skip all the project info data from the Excel

    # Check whether there are duplicates values for different keys to avoid to have different families with the same name
    duplicated_values = list(set([x for x in dic_excel.values() if dic_excel.values().count(x) > 1]))

    if duplicated_values:
        message = (
            "Duplicate values were found:\n\n{}\n\n"
            "Please fix the data and run the script again."
        ).format(", ".join(map(str, duplicated_values)))

        TaskDialog.Show("Duplicate Keys Found", message)
        raise SystemExit("Duplicate keys detected")

    # 2️⃣ Check if there are families/types NOT in the Excel and report

    elements_to_rename, element_not_in_dic = [], []

    for element in elements:
        type_name = element.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString()
        try:
            new_type_name = dic_excel[type_name]
            elements_to_rename.append(element)
        except:
            element_not_in_dic.append([type_name])
            continue

    if element_not_in_dic:
        # If there are elements to be deleted, decide what to do
        res = forms.alert("{} family/types were not found in the Excel.\nAn Excel report will be export with more detailed information.\n\n"
                          "Are you sure you want to continuing renaming the rest of the families/types?".format(len(element_not_in_dic)),
                          options=["Continue, and export an Excel Report",
                                   "Stop, and export an Excel Report"],
                          warn_icon=False)

        # Export report

        project_info = get_project_info(doc, app)

        directory = create_report_directory('Bimming_Rename Wall Types_Error Report')

        dic = list_to_dict(project_info)
        file_name = dic['File Name']
        report_name = generate_report_name(file_name)

        # Create the full file path with the .csv extension
        csv_file_path = os.path.join(directory, report_name[0] + ".csv")

        header = [[], ["ERROR REPORT", 'The following families/types were not found in the Excel']]

        data = project_info + header + element_not_in_dic
        export_to_csv(csv_file_path, data)

        if res == "Stop, and export an Excel Report":
            sys.exit()
        else: pass

    # 3️⃣ Start a transaction
    t = Transaction(doc, TRANSACTION_NAME)
    t.Start()

    for element in elements_to_rename:
        type_name = element.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString()
        try:
            new_type_name = dic_excel[type_name]
        except:
            continue
        element.Name = new_type_name

    t.Commit()

# PULL DATA
else:
    # 1️⃣ Get filter information to be exported
    output_data = [[],["DATA"], ["CURRENT TYPE NAME", "PROPOSED TYPE NAME"]]

    for element in elements:

        type_name = element.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString()

        output_data.append([type_name])

    # 2️⃣ Export report

    project_info = get_project_info(doc, app)

    directory = create_report_directory('Bimming_Rename Wall Types')

    dic = list_to_dict(project_info)
    file_name = dic['File Name']
    report_name = generate_report_name(file_name)

    # Create the full file path with the .csv extension
    csv_file_path = os.path.join(directory, report_name[0] + ".csv")

    data = project_info + output_data
    export_to_csv(csv_file_path, data)