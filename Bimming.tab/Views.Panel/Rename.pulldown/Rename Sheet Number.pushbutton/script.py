# -*- coding: utf-8 -*-
__title__ = "Rename\nSheet Number"
__doc__ = """Renames the sheet numbers of the selected sheets in the project.

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

#1️⃣ Select Views
# Get Views - Selected in a projectBrowser
sel_el_ids  = uidoc.Selection.GetElementIds()
sel_elem    = [doc.GetElement(e_id) for e_id in sel_el_ids]
sel_sheets  = [el for el in sel_elem if issubclass(type(el), ViewSheet)]

# If None Selected - Promp SelectViews from pyrevit.forms.select_views()
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
              Separator(),       Button('Rename Sheet Numbers')]

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


# 3️⃣Rename Sheets
t = Transaction(doc, TRANSACTION_NAME)
print('The following sheet numbers have been renamed:')
t.Start()

project_browser_id = DockablePanes.BuiltInDockablePanes.ProjectBrowser
project_browser = DockablePane(project_browser_id)
project_browser.Hide()

for sheet in sel_sheets:
    old_sheet_number = sheet.get_Parameter(BuiltInParameter.SHEET_NUMBER)
    old_sheet_number_str = old_sheet_number.AsString()
    new_sheet_number = prefix + old_sheet_number_str.replace(find, replace) + suffix
    try:
        old_sheet_number.Set(new_sheet_number)
        print('{} -> {}'.format(old_sheet_number_str, new_sheet_number))
    except Exception as e:
        # Handle errors explicitly
        print("Error renaming sheet '{}': {}".format(old_sheet_number_str, e))

project_browser.Show()

t.Commit()

print ('---'*30)
print ('Job done!')