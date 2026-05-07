# -*- coding: utf-8 -*-
__title__ = "Buildup\nUpdater"
__doc__ = """Select instances.

Author: Máximo Cubero"""

__min_revit_ver__ = 2021
__max_revit_ver__ = 2026

import sys

# CONSTANTS
#==================================================
TRANSACTION_NAME = "Set Buildup_KCASP"

# IMPORTS
#==================================================
import System
from System.Collections.Generic import List

from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import TaskDialog
from Snippets._bimcore_export import *
from Snippets._bimcore_functions import *

# VARIABLES
#==================================================
doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

# MAIN
#==================================================

def check_parameter_binding(doc, param_name, categories_to_check):
    """
    Checks whether a shared or project parameter exists in the document
    and is bound to the given Revit categories.

    If the parameter exists but is not bound to one or more categories,
    it shows a warning listing the missing ones and stops execution.

    Args:
        doc: The current Revit document.
        param_name (str): The name of the parameter to look for.
        categories_to_check (list[BuiltInCategory]): Categories to verify.

    Returns:
        None

    Raises:
        SystemExit: Stops the script if the parameter is missing or not bound to all categories.
    """
    binding_map = doc.ParameterBindings
    iterator = binding_map.ForwardIterator()
    iterator.Reset()

    while iterator.MoveNext():
        definition = iterator.Key
        binding = iterator.Current

        if definition.Name == param_name:
            # Get bound categories
            bound_cats = [cat for cat in binding.Categories]
            bound_cat_ids = [c.Id.IntegerValue for c in bound_cats]

            # Check which categories are missing
            missing_cats = []
            for bic in categories_to_check:
                cat = doc.Settings.Categories.get_Item(bic)
                if cat.Id.IntegerValue not in bound_cat_ids:
                    missing_cats.append(cat.Name)

            if missing_cats:
                msg = "⚠️ Parameter '{}' is not bound to the following categories:\n{}".format(
                    param_name, "\n".join(missing_cats)
                )
                TaskDialog.Show("Missing Binding", msg)
                sys.exit()  # Stop execution if any category is missing

            # Fully bound
            print("✅ Parameter '{}' is bound to all required categories.".format(param_name))
            return

    # Parameter not found at all
    TaskDialog.Show("Warning", "⚠️ Parameter '{}' not found in the project.".format(param_name))
    sys.exit()

def get_materials(wall_type):
    """
    This function retrieves all materials used in the compound structure of a given wall type.

    It inspects each layer of the wall type’s compound structure and collects the corresponding
    material elements. If a layer is defined as "By Category" (i.e., without a specific material),
    it adds a placeholder string '<by category>' instead.

    Args:
        wall_type: The Revit wall type element whose compound structure materials will be collected.

    Returns:
        list or str:
            - A list of Revit Material elements and/or placeholder strings ('<by category>')
              representing each layer's assigned material.
            - The string "Not Compound Structure" if the wall type has no compound structure.
    """
    materials = []
    comp_struct = wall_type.GetCompoundStructure()
    if not comp_struct:
        return "Not Compound Structure"

    for layer in comp_struct.GetLayers():
        mat_id = layer.MaterialId
        if mat_id.IntegerValue != -1:  # skip "By Category" layers
            mat = doc.GetElement(mat_id)
            if mat:
                materials.append(mat)
        else:
            materials.append('<by category>')
    return materials

def create_keynote_table_dict(doc):
    """
    This function creates a dictionary from the keynote table in a Revit document.

    The dictionary will have the keynote keys as the keys and their corresponding
    keynote text as the values.

    Args:
        doc: The Revit document containing the keynote table.

    Returns:
        dict: A dictionary where the keys are the keynote keys and the values are
              the corresponding keynote text.
    """

    # Get the keynote table from the Revit document
    keynote_table = KeynoteTable.GetKeynoteTable(doc)

    # Initialize an empty dictionary to store keynote data
    keynote_dict = {}

    # Loop through the keynote table entries
    for e in keynote_table.GetKeyBasedTreeEntries():
        key = e.Key  # Get the keynote key
        keynote_text = e.KeynoteText  # Get the keynote text

        # Add the key and keynote text to the dictionary
        keynote_dict[key] = keynote_text

    return keynote_dict

keynote_table = create_keynote_table_dict(doc)

# COLLLECT CEILINGS AND FLOORS
iList = List[BuiltInCategory]()
iList.Add(BuiltInCategory.OST_Walls)
iList.Add(BuiltInCategory.OST_Floors)
iList.Add(BuiltInCategory.OST_Ceilings)
iList.Add(BuiltInCategory.OST_Roofs)

collector = FilteredElementCollector(doc)\
            .WherePasses(ElementMulticategoryFilter(iList))\
            .WhereElementIsElementType()\
            .ToElements()

# elem_types = FilteredElementCollector(doc)\
#     .OfCategory(BuiltInCategory.OST_Walls)\
#     .WhereElementIsElementType()\
#     .ToElements()

# 1️⃣Check if the parameter Buildup_KCASP is part of the model
parameter_name = "Buildup_KCASP"
categories_to_check = [
    BuiltInCategory.OST_Walls,
    BuiltInCategory.OST_Floors,
    BuiltInCategory.OST_Ceilings,
    BuiltInCategory.OST_Roofs]

# This will show warnings and stop the script if the parameter is missing or partially unbound
check_parameter_binding(doc, parameter_name, categories_to_check)


errors = [['Family Name', 'Type', 'Material Name', 'Keynote', 'Keynote Description', 'Error Description']]

for elem_type in collector:
    # safer name retrieval
    type_name = elem_type.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString()
    family_name = getattr(elem_type, "FamilyName", "Unknown Family")

    if any(name in family_name for name in ["Basic Wall", "Compound Ceiling", "Floor", "Basic Roof"]):
    # if fam_name == "Basic Wall":
        # print("\n\nFamily:\t\t{}\nType:\t\t\t{}".format(fam_name, type_name))
        buildup = []
        for material in get_materials(elem_type):
            error_description = ''

            if material == '<by category>':
                material_name = material
                keynote = 'null'
                keynote_description = 'null'
                error_description = "The material assigned to the layer is <by category> and does not have any keynote associated"

            else:
                material_name = material.Name
                if not "KEYNOTE NOT REQUIRED" in material_name.upper():  # skip materials which contain 'KEYNOTE NOT REQUIRED' in the material name
                    keynote = material.get_Parameter(BuiltInParameter.KEYNOTE_PARAM).AsString()
                    if keynote == '':
                        keynote = ''
                        keynote_description = ''
                        error_description = 'The material does not have any keynote associated'
                    else: # we're going to try to get the description from the keynote dict table
                        try:
                            keynote_description = keynote_table[keynote]
                        except:
                            keynote_description = ''
                            error_description = 'The keynote "{}" was not found in the keynote file'.format(keynote)
                else: continue

            if keynote and ("Pr" in keynote or "Ss" in keynote):
                layer_description = '{} - {}'.format(keynote, keynote_description)
            else:
                if keynote_description == '':
                    layer_description = '-'
                else:
                    layer_description = keynote_description

            buildup.append(layer_description)

            if error_description != "":
                error = [family_name, type_name, material_name, keynote, keynote_description, error_description]
                errors.append(error)

            # print('Material Name: {} - Keynote: {} - {}'.format(material_name, keynote, keynote_description))

        buildup_join = "\r\n".join(buildup)

        # 2️⃣ Start a transaction (needed to modify the model)
        t = Transaction(doc, TRANSACTION_NAME)
        t.Start()

        # 3️⃣ Set a parameter
        param = elem_type.LookupParameter(parameter_name)  # or any other parameter name
        param.Set(buildup_join)

        t.Commit()

        # print("\n---\n")

# for error in errors:
#     print (error)

# 4️⃣ Export report
if len(errors) > 1:

    project_info = get_project_info(doc, app)

    directory = create_report_directory('Bimming_Buildup Updater')

    dic = list_to_dict(project_info)
    file_name = dic['File Name']
    report_name = generate_report_name(file_name)

    # 4️⃣Export the report
    # Create the full file path with the .csv extension
    csv_file_path = os.path.join(directory, report_name[0] + ".csv")

    data = project_info + errors
    export_to_csv(csv_file_path, data)