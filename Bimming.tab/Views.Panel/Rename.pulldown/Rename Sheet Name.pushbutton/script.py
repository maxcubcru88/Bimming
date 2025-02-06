# -*- coding: utf-8 -*-
__title__ = "Rename Sheet Name"
__doc__ = """Renames the sheet names of the selected sheets in the project.

Author: Máximo Cubero"""

__min_revit_ver__ = 2021
__max_revit_ver__ = 2025

# CONSTANTS
#==================================================
TRANSACTION_NAME = "Bimming-Rename Sheet Number"
ALERT_NO_SHEETS = "No Sheets Selected. Please Try Again"
ALERT_NO_RULES = "Rules to rename have not been defined. Please Try Again"

# IMPORTS
#==================================================
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import DockablePanes, DockablePane
from pyrevit import forms
from rpw.ui.forms import (FlexForm, Label, TextBox, Separator, Button)

# VARIABLES
#==================================================
doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

# MAIN
#==================================================

# 1️⃣Select Views
# Get Views - Selected in a projectBrowser
sel_el_ids  = uidoc.Selection.GetElementIds()
sel_elem    = [doc.GetElement(e_id) for e_id in sel_el_ids]
sel_sheets  = [el for el in sel_elem if issubclass(type(el), ViewSheet)]

# If None Selected - Prompt SelectViews from pyrevit.forms.select_views()
filter_sheet = ElementCategoryFilter(BuiltInCategory.OST_Sheets)
if not sel_sheets:
    sel_sheets = forms.select_sheets()

# Ensure Views Selected
if not sel_sheets:
    forms.alert(ALERT_NO_SHEETS, exitscript=True)

# 2️⃣Define Renaming Rules (UI FORM)
components = [Label('Prefix:'),  TextBox('prefix'),
              Label('Find:'),    TextBox('find'),
              Label('Replace:'), TextBox('replace'),
              Label('Suffix'),   TextBox('suffix'),
              Separator(),       Button('Rename Sheet Names')]

form = FlexForm('Title', components)
form.show()

# Ensure Components are Filled
try:
    user_inputs = form.values #type: dict
    prefix  = user_inputs['prefix']
    find    = user_inputs['find']
    replace = user_inputs['replace']
    suffix  = user_inputs['suffix']
except:
    forms.alert(ALERT_NO_RULES, exitscript=True)

# 3️⃣Renumber Sheets
t = Transaction(doc, TRANSACTION_NAME)
print('The following sheet names have been renamed:')
t.Start()

project_browser_id = DockablePanes.BuiltInDockablePanes.ProjectBrowser
project_browser = DockablePane(project_browser_id)
project_browser.Hide()

for sheet in sel_sheets:
    old_sheet_name = sheet.Name
    new_sheet_name = prefix + old_sheet_name.replace(find, replace) + suffix
    try:
        sheet.Name = new_sheet_name
        print('{} -> {}'.format(old_sheet_name, new_sheet_name))
    except Exception as e:
        # Handle errors explicitly
        print("Error renaming sheet '{}': {}".format(old_sheet_name, e))

t.Commit()

print ('---'*30)
print ('Job done!')