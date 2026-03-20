# -*- coding: utf-8 -*-
__title__   = "Select Scope Box"
__doc__     = """Select scope Boxes.

Author: Maximo Cubero"""

__min_revit_ver__ = 2021
__max_revit_ver__ = 2025

# CONSTANTS
#==================================================
TRANSACTION_NAME = "Bimming-Rotate Scope Boxes"

# IMPORTS
#==================================================
from pyrevit import forms
import clr
clr.AddReference('System')
from Snippets._bimcore_scope_boxes import *
from System.Collections.Generic import List


# VARIABLES
#==================================================
app    = __revit__.Application
uidoc  = __revit__.ActiveUIDocument
doc    = __revit__.ActiveUIDocument.Document #type:Document

# CLASS
#==================================================
class MyOption(forms.TemplateListItem):
    def __init__(self, item, el_name, angle, checked=False):
        self.item = item #Id of the element
        self.el_name = el_name
        self.angle = angle
        self.checked = checked

    @property
    def name(self):
        el_id = str(self.item)
        return "Angle: {}  |  Name: {}".format(self.angle, self.el_name)

# MAIN
#==================================================

#1️⃣ Select Scope Boxes
scope_boxes = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_VolumeOfInterest).WhereElementIsNotElementType().ToElements()
scope_boxes_sorted = sorted(scope_boxes, key=lambda sb: get_scope_box_angle(sb))
scope_boxes_ids = [sb.Id for sb in scope_boxes]

if not scope_boxes:
    forms.alert("There are not any scope box in the model.", warn_icon=False, exitscript=True)

# Get Scope Boxes - Selected in the model
sel_el_ids          = uidoc.Selection.GetElementIds()
sel_elem            = [doc.GetElement(e_id) for e_id in sel_el_ids]
sel_elem_ids = [el.Id for el in sel_elem if el.Id in scope_boxes_ids]

#2️⃣ WPF Form to select scope boxes
scope_box_list = []
for sb in scope_boxes_sorted:
    scope_box_id = sb.Id
    scope_box_name = sb.Name
    scope_box_angle = get_scope_box_angle(sb)
    if sb.Id in sel_elem_ids:
        scope_box_checked = True
    else:
        scope_box_checked = False
    option = MyOption(scope_box_id, scope_box_name, scope_box_angle, scope_box_checked)
    scope_box_list.append(option)

res = forms.SelectFromList.show(scope_box_list, title='Scope Boxes List', multiselect=True, button_name='Select Scope Boxes')

# Ensure Views Selected
if not res:
    forms.alert("No Scope Boxes Selected. Please Try Again", exitscript=True)

#3️⃣ Select it in the Revit UI

element_ids = List[ElementId]()

for e in res:
    element_ids.Add(e)

uidoc.Selection.SetElementIds(element_ids)

#4️⃣ Message
if len(element_ids) > 1:
    message = '{} Scope Boxes have been selected'.format(len(element_ids))
else:
    message = '{} Scope Box has been selected'.format(len(element_ids))
forms.alert(message, 'Scope Box Select', warn_icon=False)