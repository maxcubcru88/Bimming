# -*- coding: utf-8 -*-
__title__ = "Select\nRef Planes"
__doc__ = """Version = 1.0
Date    = 28.10.2024
_____________________________________________________________________
Description:
Rename Views in Revit by using Find/Replace Logic
_____________________________________________________________________
How-to:
-> Click on the button
-> Select Views
-> Define Renaming Rules
-> Rename Views
_____________________________________________________________________
Last update:
- [28.10.2024] - 1.1 First Release
_____________________________________________________________________
Author: Máximo Cubero"""

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
#==================================================
# Regular + Autodesk
from Autodesk.Revit.DB import *

# pyRevit
from pyrevit import revit, forms

# Regular + Autodesk
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI.Selection import ObjectType
from select import select
from Autodesk.Revit.UI.Selection import ISelectionFilter

from System.Collections.Generic import List
from Autodesk.Revit.UI import TaskDialog

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
#==================================================
doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app   = __revit__.Application

# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝ MAIN
#==================================================

""" Rename views on sheets
    SHEET NUMBER + DETAIL NUMBER + TITLE ON SHEET (IF POPULATED)
    SHEET NUMBER + DETAIL NUMBER + VIEW NAME
"""

# forms.alert("WIP-Rename Filters")

"""#1️⃣ Select Views

# Get Views - Selected in a projectBrowser
sel_el_ids  = uidoc.Selection.GetElementIds()
sel_elem    = [doc.GetElement(e_id) for e_id in sel_el_ids]
sel_views   = [el for el in sel_elem if issubclass(type(el), View)]

# If None Selected - Promp SelectViews from pyrevit.forms.select_views()
if not sel_views:
    sel_views = forms.select_views()

# Ensure Views Selected
if not sel_views:
    forms.alert('No Views Selected. Please Try Again', exitscript=True)
"""



class IselectionFilter_Categories(ISelectionFilter):
    def __init__(self, allowed_categories):
        """ ISelectionFilter made to filter with categories
        allowed_types: list of allowed Types"""
        self.allowed_categories = allowed_categories

    def AllowElement(self, element):
        if element.Category.BuiltInCategory in self.allowed_categories:
            return True

# Get Views - Selected in a projectBrowser
# sel_el_ids      = uidoc.Selection.GetElementIds()
# sel_elem        = [doc.GetElement(e_id) for e_id in sel_el_ids]
# sel_elem_filter = [el for el in sel_elem if issubclass(type(el), ReferencePlane)]
# sel_elem        = sel_elem_filter

# if len(sel_elem_filter) != 1:
#     try:
#         # Get Element - Selected in a projectBrowser
#         sel_elem_reference  = uidoc.Selection.PickObject(ObjectType.Element,
#                                                          IselectionFilter_Categories([BuiltInCategory.OST_CLines]),
#                                                          "Select elements")
#         sel_elem_id = sel_elem_reference.ElementId
#         sel_elem = doc.GetElement(sel_elem_id)
#     except:
#         # If None Selected - Prompt SelectViews from pyrevit.forms.select_views()
#         TaskDialog.Show('No Elements Selected. Please Try Again')
#
# else:
#     sel_elem = sel_elem_filter[0] # Selecting the only element in the list
#     pass

try:
    # Get Element - Selected in a projectBrowser
    sel_elem_reference  = uidoc.Selection.PickObject(ObjectType.Element,
                                                     IselectionFilter_Categories([BuiltInCategory.OST_CLines]),
                                                     "Select elements")
    sel_elem_id = sel_elem_reference.ElementId
    sel_elem = doc.GetElement(sel_elem_id)
except:
    # If None Selected - Prompt SelectViews from pyrevit.forms.select_views()
    TaskDialog.Show('No Elements Selected. Please Try Again')

# sel_elem_filter_name = Element.Name.GetValue(sel_elem)
# print(sel_elem_filter_name)
subcategory_id = sel_elem.get_Parameter(BuiltInParameter.CLINE_SUBCATEGORY).AsElementId()
subcategory = doc.GetElement(subcategory_id)
sel_subcategory_name = Element.Name.GetValue(subcategory)
# sel_elem_filter_name = Element.Name.GetValue(sel_elem)
#
print(sel_subcategory_name)


all_ref_planes   = FilteredElementCollector(doc).OfClass(ReferencePlane).ToElements()

dic = {}

for rp in all_ref_planes:
    subcategory_id = rp.get_Parameter(BuiltInParameter.CLINE_SUBCATEGORY).AsElementId()
    subcategory = doc.GetElement(subcategory_id)
    subcategory_name = Element.Name.GetValue(subcategory)
    if not isinstance(subcategory_name, str):
        subcategory_name = '<None>'
    dic[subcategory_name] = dic.get(subcategory_name, []) + [rp]
    # print(subcategory_name)

selection = dic[sel_subcategory_name]


# icollection[ElementId]() = []
selection_ids = List[ElementId]()
for e in selection:
    selection_ids.Add(e.Id)


# Set the selection to the collected reference planes
uidoc.Selection.SetElementIds(selection_ids)

# Optionally, show a message to confirm the selection
TaskDialog.Show("Selection", "{} Reference Planes selected.".format(len(selection_ids)))
