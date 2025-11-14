# -*- coding: utf-8 -*-
__title__ = "Select\nTitleblocks by Sheet"
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
from pyrevit import forms
from System.Collections.Generic import List

# VARIABLES
#==================================================
doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

# MAIN
#==================================================

def get_titleblocks_by_sheet(doc):
    """
    Returns a dict where:
        key   = sheet number (string)
        value = list of ElementIds of titleblocks placed on that sheet
    """
    titleblock_dict = {}

    # Collect all title blocks in the document
    titleblocks = FilteredElementCollector(doc)\
        .OfCategory(BuiltInCategory.OST_TitleBlocks)\
        .WhereElementIsNotElementType()\
        .ToElements()

    for tb in titleblocks:
        # Every title block belongs to a ViewSheet via its OwnerViewId
        sheet_id = tb.OwnerViewId
        sheet = doc.GetElement(sheet_id)

        # Skip if not actually placed on a sheet
        if not isinstance(sheet, ViewSheet):
            continue

        sheet_number = sheet.SheetNumber

        # Add to dict
        if sheet_number not in titleblock_dict:
            titleblock_dict[sheet_number] = []

        titleblock_dict[sheet_number].append(tb.Id)

    return titleblock_dict


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

#2️⃣ Collect Titleblocks in sheets
dict_titleblocks = get_titleblocks_by_sheet(doc)

element_ids = List[ElementId]()

for sheet in sel_sheets:
    sheet_number = sheet.get_Parameter(BuiltInParameter.SHEET_NUMBER).AsString()
    titleblock_ids = dict_titleblocks[sheet_number]
    for titleblock_id in titleblock_ids:
        element_ids.Add(titleblock_id)

#3️⃣ Select it in the Revit UI
uidoc.Selection.SetElementIds(element_ids)

#4️⃣ Message
message = '{} Titleblocks have been selected'.format(len(element_ids))
forms.alert(message, 'Titleblocks Select', warn_icon=False)