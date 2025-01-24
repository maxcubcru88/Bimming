# -*- coding: utf-8 -*-
__title__ = "Rename Sheet Name"
__doc__ = """Renames the sheet names of the selected sheets in the project.

Author: Máximo Cubero"""

#__helpurl__ = "https://www.bimming.uk"
__min_revit_ver__ = 2021
__max_revit_ver__ = 2025
#__context__ = 'zero-doc'
#__highlight__ = 'new'

# IMPORTS
#==================================================
from Autodesk.Revit.DB import *
from pyrevit import forms

# VARIABLES
#==================================================
doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app   = __revit__.Application

# MAIN
#==================================================

#1️⃣ Select Views

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
    forms.alert('No Sheets Selected. Please Try Again', exitscript=True)


# #2️⃣🅰️ Define Renaming Rules
# prefix  = 'pre-'
# find    = 'Level'
# replace = 'MC-Level'
# suffix  = '-suf'

# 2️⃣🅱️ Define Renaming Rules (UI FORM)
# https://revitpythonwrapper.readthedocs.io/en/latest/ui/forms.html?highlight=forms#flexform
from rpw.ui.forms import (FlexForm, Label, TextBox, Separator, Button)

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
    forms.alert('Rules to rename have not been defined. Please Try Again', exitscript=True)

#🔒 Start Transaction to make changes in project
t = Transaction(doc, 'Bimming-Rename Sheet Name')

print('The following sheet names have been renamed:')

t.Start()  #🔓
for sheet in sel_sheets:

    #3️⃣ Create New View Name
    old_sheet_name = sheet.Name
    new_sheet_name = prefix + old_sheet_name.replace(find, replace) + suffix

    #4️⃣ Rename Sheets (Sheet can be the same)
    try:
        sheet.Name = new_sheet_name
        print('{} -> {}'.format(old_sheet_name, new_sheet_name))
    except Exception as e:
        # Handle errors explicitly
        print("Error renaming sheet '{}': {}".format(old_sheet_name, e))

t.Commit() #🔒

print ('---'*30)
print ('Job done!')