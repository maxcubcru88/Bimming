# -*- coding: utf-8 -*-

# Imports
#==================================================
import sys
from pyrevit import forms
from Snippets._bimming_export import *
from Snippets._bimming_import import *
from Snippets._bimming_functions import *
from pyrevit import EXEC_PARAMS

# Variables
#==================================================
app   = __revit__.Application
uidoc = __revit__.ActiveUIDocument
doc   = __revit__.ActiveUIDocument.Document #type:Document


def rename_types(category):

    cat = category

    if     cat == 'Walls': elements = FilteredElementCollector(doc).OfClass(WallType).ToElements()
    elif   cat == 'Floors': elements = FilteredElementCollector(doc).OfClass(FloorType).ToElements()
    elif   cat == 'Ceilings': elements = FilteredElementCollector(doc).OfClass(CeilingType).ToElements()
    elif   cat == 'Roofs': elements = FilteredElementCollector(doc).OfClass(RoofType).ToElements()
    elif   cat == 'Windows': elements_symbols = (FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Windows).WhereElementIsElementType().OfClass(FamilySymbol))
    elif   cat == 'Doors': elements_symbols = (FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Doors).WhereElementIsElementType().OfClass(FamilySymbol))
    elif   cat == 'Generic Models': elements_symbols = (FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_GenericModel).WhereElementIsElementType().OfClass(FamilySymbol))

    if cat in ['Walls', 'Ceilings', 'Roofs', 'Floors']:
        fam_type = 'System Family'
    else:
        fam_type = 'Loadable Family'

    if fam_type == 'Loadable Family':

        # 2️⃣ Deduplicate families using ElementId
        families_by_id = {}

        for symbol in elements_symbols:
            fam = symbol.Family
            families_by_id[fam.Id.IntegerValue] = fam

        # 3️⃣ Final unique families list
        elements = list(families_by_id.values())

    # Define exclusions based on config mode
    # PUSH DATA
    if EXEC_PARAMS.config_mode:

        # 1️⃣ Read data from Excel and create dic
        directory = create_report_directory('Bimming_Rename Families {}'.format(cat), False)
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
            if fam_type == 'System Family':
                type_name = element.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString()
            else:
                type_name = element.Name
            try:
                dic_excel[type_name]
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

            directory = create_report_directory('Bimming_Rename {}_Error Report'.format(cat), open_directory=False)

            dic = list_to_dict(project_info)
            file_name = dic['File Name']
            report_name = generate_report_name(file_name)

            # Create the full file path with the .csv extension
            csv_file_path = os.path.join(directory, report_name[0] + ".csv")

            header = [[], ["ERROR REPORT", 'The following families/types were not found in the Excel']]

            data = project_info + header + element_not_in_dic
            export_to_csv(csv_file_path, data, open_file=True)

            if res == "Stop, and export an Excel Report":
                sys.exit()
            else: pass

        # 3️⃣ Start a transaction
        TRANSACTION_NAME = 'Bimming-Renaming'
        t = Transaction(doc, TRANSACTION_NAME)
        t.Start()

        for element in elements_to_rename:
            if fam_type == 'System Family':
                type_name = element.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString()
            else:
                type_name = element.Name
            try:
                new_type_name = str(dic_excel[type_name])
            except:
                continue
            element.Name = new_type_name

        t.Commit()

    # PULL DATA
    else:
        # 1️⃣ Get filter information to be exported
        output_data = [[],["DATA"], ["CURRENT TYPE NAME", "PROPOSED TYPE NAME"]]

        if fam_type == 'System Family':
            for element in elements:

                type_name = element.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString()

                output_data.append([type_name])
        else:
            for element in elements:

                family_name = element.Name

                output_data.append([family_name])

        # 2️⃣ Export report

        project_info = get_project_info(doc, app)

        directory = create_report_directory('Bimming_Rename Families {}'.format(cat))

        dic = list_to_dict(project_info)
        file_name = dic['File Name']
        report_name = generate_report_name(file_name)

        # Create the full file path with the .csv extension
        csv_file_path = os.path.join(directory, report_name[0] + ".csv")

        data = project_info + output_data
        export_to_csv(csv_file_path, data)