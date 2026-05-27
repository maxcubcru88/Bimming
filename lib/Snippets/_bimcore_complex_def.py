# -*- coding: utf-8 -*-

# Imports
#==================================================
import sys
from pyrevit import forms
from Snippets._bimcore_export import *
from Snippets._bimcore_import import *
from Snippets._bimcore_functions import *
from pyrevit import EXEC_PARAMS

from System.Collections.Generic import List

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

def create_folder_dictionary(directory_path):
    folder_dict = {}

    pattern = re.compile(r'^(\d{3})_(.+)$')

    try:
        for item in os.listdir(directory_path):
            full_path = os.path.join(directory_path, item)
            if os.path.isdir(full_path):
                match = pattern.match(item)
                if match:
                    number = match.group(1)
                    description = match.group(2)

                    folder_dict[number] = item

    except OSError:
        print("Cannot access path '{0}'".format(directory_path))

    return folder_dict

def parameter_type_updater(category, excel_file_path):
    # type: (str, str) -> tuple
    """
    Reads an Excel Type Parameter Table for the given category,
    matches element types in the model by their MODEL parameter,
    and populates the corresponding Revit type parameters.

    Args:
        category        (str): Must match a key in the mapping dict.
                               e.g. "CEILING TYPES", "DOORS TYPES EXTERNAL", "DOORS TYPES INTERNAL",
                               "FLOOR & ROOF TYPES", "METALWORK TYPES", "PRECAST ELEMENTS", "WALL TYPES", "WINDOW TYPES"
        excel_file_path (str): Full path to the Excel file.
                               e.g. r"C:\Projects\123_ProjectName\...\123-WALL TYPES.xlsx"
    """

    # MAPPING
    #==================================================
    mapping = {
        "CEILING TYPES":        [BuiltInCategory.OST_Ceilings],
        "DOOR TYPES EXTERNAL": [BuiltInCategory.OST_Doors],
        "DOOR TYPES INTERNAL": [BuiltInCategory.OST_Doors],
        "FLOOR & ROOF TYPES":   [BuiltInCategory.OST_Roofs, BuiltInCategory.OST_Floors],
        "METALWORK TYPES":      [BuiltInCategory.OST_GenericModel],
        "PRECAST ELEMENTS":     [BuiltInCategory.OST_GenericModel],
        "WALL TYPES":           [BuiltInCategory.OST_Walls],
        "WINDOW TYPES":         [BuiltInCategory.OST_Windows],
    }

    categories_model_value_mandatory = ["WINDOW TYPES", "CEILING TYPES", "FLOOR & ROOF TYPES"]

    # VALIDATE INPUT
    #==================================================
    category = category.upper().strip()
    if category not in mapping:
        forms.alert(
            "Category '{}' not found in mapping.\n\nValid options:\n{}".format(
                category, "\n".join(mapping.keys())
            ),
            "Invalid Category",
            exitscript=True
        )

    # 1️⃣ READ EXCEL
    #==================================================
    try:
        table = excel_read_via_com(excel_file_path, sheet_name="Sheet1", required_col_index=1, stop_on_empty_first_row_col=True)
    except:
        forms.alert(
            "The Excel document could not be found:\n\n{}".format(excel_file_path),
            "Warning - Excel Path",
            sub_msg="Talk to the BIM Team for support",
            exitscript=True
        )

    data_dict  = list_to_dict_excel(table, key_col_index=0, keyword=None)
    parameters = table[0][1:]

    # 2️⃣ COLLECT ELEMENTS
    #==================================================
    category_selected = mapping[category]

    iList = List[BuiltInCategory]()
    for cat in category_selected:
        iList.Add(cat)

    if BuiltInCategory.OST_GenericModel in category_selected:
        all_generic = (
            FilteredElementCollector(doc)
            .WherePasses(ElementMulticategoryFilter(iList))
            .WhereElementIsElementType()
            .ToElements()
        )
        prefixes = sorted(set(
            m.group(0)
            for key in data_dict.keys()
            for m in [re.match(r"[A-Za-z]+", key)]
            if m
        ))
        collector = [
            e for e in all_generic
            if e.get_Parameter(BuiltInParameter.ALL_MODEL_MODEL).AsString()
            and any(e.get_Parameter(BuiltInParameter.ALL_MODEL_MODEL).AsString().startswith(p) for p in prefixes)
        ]
    else:
        collector = (
            FilteredElementCollector(doc)
            .WherePasses(ElementMulticategoryFilter(iList))
            .WhereElementIsElementType()
            .ToElements()
        )

    # 3️⃣ POPULATE PARAMETERS
    #==================================================
    errors_1 = [['ID', 'Family Name', 'Type', 'Model', 'Error/Warning Description']]
    errors_2 = [['Model', 'Parameter', 'Error Description']]

    t = Transaction(doc, "KCA-Parameter Types Update-{}".format(category))
    t.Start()

    for elem_type in collector:
        elem_id     = str(elem_type.Id)
        type_name   = elem_type.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString()
        family_name = getattr(elem_type, "FamilyName", elem_id)
        model_value = elem_type.get_Parameter(BuiltInParameter.ALL_MODEL_MODEL).AsString()

        error = False
        if not model_value:
            error_description_1 = "WARNING: MODEL value empty"
            error = True
        elif model_value not in data_dict and category in categories_model_value_mandatory:
            error_description_1 = "ERROR: '{}' not found in Excel table '{}'".format(model_value, excel_file_path)
            error = True
        elif model_value not in data_dict:
            error_description_1 = "WARNING: '{}' not found in '{}'. Ignore if code is not applicable.".format(model_value, excel_file_path)
            error = True

        if error:
            errors_1.append([elem_id, family_name, type_name, model_value, error_description_1])
            continue

        for parameter in parameters:
            revit_parameter = get_parameter_by_name(elem_type, parameter)

            if not revit_parameter:
                errors_2.append([model_value, parameter,
                    "Parameter not found. Check: A) exists in project  B) linked to category  C) is a Type parameter."])
                continue

            parameter_storage_type = revit_parameter.StorageType
            data_type              = revit_parameter.Definition.GetDataType()
            raw_value              = data_dict[model_value][parameter]

            if raw_value is None or raw_value == "":
                errors_2.append([model_value, parameter,
                    "Excel cell is EMPTY. Use 'TBC', 'N/A', '-' for text or '0' for numeric."])
                continue

            if parameter_storage_type == StorageType.Integer:
                if data_type == SpecTypeId.Boolean.YesNo:
                    val = str(raw_value).upper()
                    if   val == 'TRUE':  parameter_value = 1
                    elif val == 'FALSE': parameter_value = 0
                    else:
                        errors_2.append([model_value, parameter,
                            "'{}' is YES/NO — value '{}' invalid. Use TRUE or FALSE.".format(parameter, raw_value)])
                        continue
                else:
                    try:    parameter_value = int(raw_value)
                    except:
                        errors_2.append([model_value, parameter,
                            "'{}' is INTEGER — '{}' could not be converted.".format(parameter, raw_value)])
                        continue

            elif parameter_storage_type == StorageType.Double:
                try:
                    fval = float(raw_value)
                    if   data_type == SpecTypeId.Length: parameter_value = convert_internal_units(fval, get_internal=True, units='mm')
                    elif data_type == SpecTypeId.Area:   parameter_value = convert_internal_units(fval, get_internal=True, units='m2')
                    elif data_type == SpecTypeId.Number: parameter_value = fval
                    else:
                        errors_2.append([model_value, parameter,
                            "'{}' is DOUBLE (DataType={}) — unsupported spec type.".format(parameter, data_type.TypeId)])
                        continue
                except:
                    errors_2.append([model_value, parameter,
                        "'{}' is DOUBLE — '{}' could not be converted.".format(parameter, raw_value)])
                    continue

            elif parameter_storage_type == StorageType.String:
                try:    parameter_value = str(raw_value)
                except:
                    errors_2.append([model_value, parameter,
                        "'{}' is STRING — '{}' could not be converted.".format(parameter, raw_value)])
                    continue

            revit_parameter.Set(parameter_value)

    t.Commit()
    return errors_1, errors_2