# -*- coding: utf-8 -*-
__title__ = "Select\nby Family Name"
__doc__ = """Select instances.

Author: Máximo Cubero"""

__min_revit_ver__ = 2021
__max_revit_ver__ = 2025

# CONSTANTS
#==================================================
TRANSACTION_NAME = "Bimming-Rename Views"
ALERT_NO_VIEWS = "No Views Selected. Please Try Again"
ALERT_NO_RULES = "Rules to rename have not been defined. Please Try Again"

# IMPORTS
#==================================================
import sys
from Autodesk.Revit.DB import *
from pyrevit import forms
from System.Collections.Generic import List
from rpw.ui.forms import (FlexForm, Label, TextBox, Separator, Button)

# VARIABLES
#==================================================
doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

# MAIN
#==================================================

# # 1️⃣Select Views
# # Get Views Selected in the projectBrowser
# sel_el_ids  = uidoc.Selection.GetElementIds()
# sel_elem    = [doc.GetElement(e_id) for e_id in sel_el_ids]
#
# for e in sel_elem:
#     print(e)
#     # family_name = doc.GetElement(e.GetTypyeId())
#     family_type = doc.GetElement(e.get_Parameter(BuiltInParameter.ELEM_TYPE_PARAM).AsElementId())
#     family_name = family_type.get_Parameter(BuiltInParameter.SYMBOL_FAMILY_NAME_PARAM).AsString()
#     print(family_name)

########################################################################################

# 1️⃣ Collect all Family elements (loadable families)
families = FilteredElementCollector(doc)\
    .OfClass(Family)\
    .ToElements()

# 2️⃣ Get their names (unique and sorted)
family_names = sorted(set(family.Name for family in families))

# 3️⃣ WPF Form to select families
res = forms.SelectFromList.show(
    family_names,
    title='Loadable Families',
    multiselect=True,
    button_name='Select'
)

if not res:
    sys.exit()

selected_families = res

# 4️⃣ Collect all FamilyInstance elements in the model
instances = FilteredElementCollector(doc)\
    .OfClass(FamilyInstance)\
    .WhereElementIsNotElementType()\
    .ToElements()
print(instances)

# 5️⃣ Filter only those whose Family.Name matches the selected families
selected_instances = []
for i in instances:
    try:
        if i.Symbol.Family.Name in selected_families:
            selected_instances.append(i)
    except:
        family_type = doc.GetElement(i.get_Parameter(BuiltInParameter.ELEM_TYPE_PARAM).AsElementId())
        family_name = family_type.get_Parameter(BuiltInParameter.SYMBOL_FAMILY_NAME_PARAM).AsString()
        if family_name in selected_families:
            selected_instances.append(i)
print(selected_families)

# 6️⃣ Select these elements in Revit’s UI
element_ids = List[ElementId]([i.Id for i in instances])
uidoc.Selection.SetElementIds(element_ids)

forms.alert("{0} instances selected.".format(len(selected_instances)), title="Selection Complete")

########################################################################################

# # 1️⃣Select Views
# # Get Views Selected in the projectBrowser
# sel_el_ids  = uidoc.Selection.GetElementIds()
# sel_elem    = [doc.GetElement(e_id) for e_id in sel_el_ids]
# sel_views   = [el for el in sel_elem if issubclass(type(el), View)]
#
# # If None Selected - Prompt SelectViews from pyrevit.forms.select_views()
# if not sel_views:
#     sel_views = forms.select_views()
#
# if not sel_views:
#     forms.alert(ALERT_NO_VIEWS, exitscript=True)
#
# # 2️⃣Define Renaming Rules (UI FORM)
# components = [Label('Prefix:'),  TextBox('prefix'),
#               Label('Find:'),    TextBox('find'),
#               Label('Replace:'), TextBox('replace'),
#               Label('Suffix'),   TextBox('suffix'),
#               Separator(),       Button('Rename Views')]
#
# form = FlexForm('Title', components)
# form.show()
#
# # Ensure Components are Filled
# try:
#     user_inputs = form.values #type: dict
#     prefix  = user_inputs['prefix']
#     find    = user_inputs['find']
#     replace = user_inputs['replace']
#     suffix  = user_inputs['suffix']
# except:
#     forms.alert(ALERT_NO_RULES, exitscript=True)
#
# t = Transaction(doc, TRANSACTION_NAME)
#
# # 3️⃣Rename Views
# print('The following views have been renamed:')
#
# t.Start()
#
# for view in sel_views:
#     old_name = view.Name
#     new_name = prefix + old_name.replace(find, replace) + suffix
#
#     # Ensure unique view name
#     for i in range(20):
#         try:
#             view.Name = new_name
#             print('{} -> {}'.format(old_name, new_name))
#             break
#         except:
#             new_name += '*'
#
# t.Commit()
#
# print ('---'*30)
# print ('Job done!')