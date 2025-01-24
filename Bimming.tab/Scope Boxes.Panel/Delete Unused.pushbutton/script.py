# -*- coding: utf-8 -*-
__title__   = "Delete\nUnused"
__doc__     = """Deletes unused scope boxes from the project.

Author: Maximo Cubero"""

#__helpurl__ = "https://www.bimming.uk"
__min_revit_ver__ = 2021
__max_revit_ver__ = 2025
#__context__ = 'zero-doc'
#__highlight__ = 'new'

# IMPORTS
#==================================================
from Autodesk.Revit.DB import *
from pyrevit import forms
import clr
clr.AddReference('System')
import sys

# VARIABLES
#==================================================
app    = __revit__.Application
uidoc  = __revit__.ActiveUIDocument
doc    = __revit__.ActiveUIDocument.Document #type:Document

# MAIN
#==================================================

class MyOption(forms.TemplateListItem):
    def __init__(self, item, el_name, checked=False):
        self.item = item #Id of the element
        self.el_name = el_name
        self.checked = checked

    @property
    def name(self):
        el_id = str(self.item)
        return "Name: {}".format(self.el_name)

# 1️⃣ Collect all Scope Boxes in the project
scope_boxes = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_VolumeOfInterest).WhereElementIsNotElementType().ToElements()

if not scope_boxes:
    forms.alert("There are not any scope box in the model.", warn_icon=False, exitscript=True)

# 2️⃣ Collect all views and elements that might reference scope boxes
views = FilteredElementCollector(doc).OfClass(View).ToElements()
grids = FilteredElementCollector(doc).OfClass(Grid).ToElements()
reference_planes = FilteredElementCollector(doc).OfClass(ReferencePlane).ToElements()

# Set to store used scope box IDs
used_scope_box_ids = set()

# 3️⃣ Check which scope boxes are being used
# Check views
for view in views:
    if view.IsTemplate:  # Skip view templates
        continue
    try:
        scope_box_id = view.get_Parameter(BuiltInParameter.VIEWER_VOLUME_OF_INTEREST_CROP).AsElementId()
        used_scope_box_ids.add(scope_box_id)
    except:
        continue

# Check grids
for grid in grids:
    try:
        scope_box_id = grid.get_Parameter(BuiltInParameter.DATUM_VOLUME_OF_INTEREST).AsElementId()
        used_scope_box_ids.add(scope_box_id)
    except:
        continue

# Check reference planes
for ref_plane in reference_planes:
    try:
        scope_box_id = ref_plane.get_Parameter(BuiltInParameter.DATUM_VOLUME_OF_INTEREST).AsElementId()
        used_scope_box_ids.add(scope_box_id)
    except:
        continue

# Unused Scope Boxes
unused_scope_boxes = [scope_box for scope_box in scope_boxes if scope_box.Id not in used_scope_box_ids]
scope_boxes_sorted = sorted(unused_scope_boxes, key=lambda sb: sb.Name)

if not unused_scope_boxes:
    forms.alert("All the scope boxes are in use.", warn_icon=False, exitscript=True)

# 4️⃣ WPF Form to select scope boxes
scope_box_list = []
for sb in scope_boxes_sorted:
    scope_box_id = sb.Id
    scope_box_name = sb.Name
    #scope_box_angle = get_scope_box_angle(sb)
    scope_box_checked = True
    option = MyOption(scope_box_id, scope_box_name, scope_box_checked)
    scope_box_list.append(option)

res = forms.SelectFromList.show(scope_box_list, title='Unused Scope Boxes List', multiselect=True, button_name='Delete') #Ids
if not res:
    sys.exit()
unused_scope_boxes = [doc.GetElement(i) for i in res]

# 5️⃣ Delete Scope Boxes
t = Transaction(doc, 'Bimming-Delete Unused Scope Boxes')
t.Start()
counter = 0
for scope_box in unused_scope_boxes:
    try:
        print("Scope Box '{scope_box.Name}' has been deleted".format(scope_box=scope_box))
        scope_box.Pinned = False
        doc.Delete(scope_box.Id)
        counter += 1
    except Exception as e:
        print("Error deleting Scope Box {scope_box.Name}: {e}".format(scope_box=scope_box, e=e))
t.Commit()