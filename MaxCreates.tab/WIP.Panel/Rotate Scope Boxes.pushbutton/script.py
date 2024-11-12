# -*- coding: utf-8 -*-
__title__   = "Rotate\nScope Boxes"
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
import math

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
"""
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
"""

#1️⃣ Select Views

scope_boxes = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_VolumeOfInterest).WhereElementIsNotElementType().ToElementIds()

# Get Views - Selected in a projectBrowser
sel_el_ids          = uidoc.Selection.GetElementIds()
sel_elem            = [doc.GetElement(e_id) for e_id in sel_el_ids]
sel_scope_boxes      = [el for el in sel_elem if el.Id in scope_boxes]

# If None Selected - Promp SelectViews from pyrevit.forms.select_views()
if not sel_scope_boxes:
    sel_views = forms.select_views()

# Ensure Views Selected
if not sel_scope_boxes:
    forms.alert('No Views Selected. Please Try Again', exitscript=True)

#print([e for e in sel_scope_boxes])


# Define a function to check if a vector is parallel to the Z-axis
def is_parallel_to_z(vector):
    # Z-axis vector
    z_axis = XYZ.BasisZ

    # Calculate the dot product between the input vector and Z-axis vector
    dot_product = vector.DotProduct(z_axis)

    # Check if the dot product is close to 1 or -1
    if abs(dot_product) > 0.9999:
        return True
    else:
        return False


def get_angles_against_x(vectors):
    angles = []

    # X-axis vector
    x_axis = XYZ.BasisY

    for vector in vectors:
        # Calculate the angle between the vector and X-axis
        angle = vector.AngleTo(x_axis)

        # Convert angle from radians to degrees
        angle_degrees = math.degrees(angle)

        angles.append(angle_degrees)

    return angles


# Function to rotate scope box
def rotate_scope_box(scope_box, angle_degrees):

    # Get the bounding box of the scope box
    bounding_box = scope_box.get_BoundingBox(doc.ActiveView)

    # Calculate the center point of the bounding box
    center_point = (bounding_box.Min + bounding_box.Max) / 2.0

    # Create a rotation axis
    axis = Line.CreateBound(center_point, XYZ(center_point.X, center_point.Y, center_point.Z + 1))

    # Convert angle from degrees to radians
    angle_radians = math.radians(angle_degrees)

    # Rotate the scope box
    ElementTransformUtils.RotateElement(doc, scope_box.Id, axis, angle_radians)


# Get all scope boxes in the document
scope_boxes = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_VolumeOfInterest).ToElements()

t = Transaction(doc, 'MC-Rotate Scope Boxes')
t.Start()

sb = sel_scope_boxes[0]
# rotate_scope_box(sb, -5)

angle = -30

# Iterate over each scope box and rotate by 5 degrees
# for scope_box in scope_boxes:
#    rotate_scope_box(scope_box, 5)

# Define options
options = Options()
options.DetailLevel = ViewDetailLevel.Undefined

geom = sb.Geometry[options]

direction = []
for line in geom:
    vector = line.Direction
    if not (is_parallel_to_z(vector)):
        direction.append(vector)

scope_box_angle = get_angles_against_x(direction)[4]

angle_to_be_rotated = angle - scope_box_angle

rotate_scope_box(sb, angle_to_be_rotated)

# Output the rotated scope boxes
OUT = sb


t.Commit()