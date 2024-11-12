# -*- coding: utf-8 -*-
__title__   = "Delete\nScope Boxes"
__doc__     = """Version = 1.0
Date    = 12.11.2024
________________________________________________________________
Description:

Create a 3D view per workset and hide all the workset but one.

The name of the 3D View starts with Audit_Worset-"Workset Name"

To modify the prefix execute the script with Shift+Click

________________________________________________________________
How-To:

1. [Hold ALT + CLICK] on the button to open its source folder.
You will be able to override this placeholder.

2. Automate Your Boring Work ;)

________________________________________________________________
TODO:
[FEATURE] - Describe Your ToDo Tasks Here
________________________________________________________________
Last Updates:
<>
________________________________________________________________
Author: Maximo Cubero"""

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝
#==================================================
from Autodesk.Revit.DB import *

# pyRevit
from pyrevit import revit, forms

import sys

#.NET Imports
import clr
clr.AddReference('System')
from System.Collections.Generic import List


# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝
#==================================================
app    = __revit__.Application
uidoc  = __revit__.ActiveUIDocument
doc    = __revit__.ActiveUIDocument.Document #type:Document


# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝
#==================================================

# Step 1: Collect all Scope Boxes in the project
scope_boxes = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_VolumeOfInterest).WhereElementIsNotElementType().ToElements()

# Step 2: Collect all views and elements that might reference scope boxes
views = FilteredElementCollector(doc).OfClass(View).ToElements()
grids = FilteredElementCollector(doc).OfClass(Grid).ToElements()
reference_planes = FilteredElementCollector(doc).OfClass(ReferencePlane).ToElements()

# Set to store used scope box IDs
used_scope_box_ids = set()

# Step 3: Check which scope boxes are being used
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

# Step 4: Delete unused Scope Boxes
unused_scope_boxes = [scope_box for scope_box in scope_boxes if scope_box.Id not in used_scope_box_ids]

if unused_scope_boxes:
    t = Transaction(doc, 'MC-Delete Unused Scope Boxes')
    t.Start()
    counter = 0
    for scope_box in unused_scope_boxes:
        try:
            print("Deleted unused Scope Box: {scope_box.Name}".format(scope_box=scope_box))
            scope_box.Pinned = False
            doc.Delete(scope_box.Id)
            counter += 1
        except Exception as e:
            print("Error deleting Scope Box {scope_box.Name}: {e}".format(scope_box=scope_box, e=e))
    forms.alert("{} Scope Boxes Deleted.".format(len(unused_scope_boxes)))
    t.Commit()
else:
    forms.alert("No unused Scope Boxes found.")




