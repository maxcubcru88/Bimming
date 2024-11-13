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

#1️⃣ Select Scope Boxes

scope_boxes = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_VolumeOfInterest).WhereElementIsNotElementType().ToElementIds()

# Get Views - Selected in a projectBrowser
sel_el_ids          = uidoc.Selection.GetElementIds()
sel_elem            = [doc.GetElement(e_id) for e_id in sel_el_ids]
sel_scope_boxes      = [el for el in sel_elem if el.Id in scope_boxes]

# If None Selected - Prompt SelectViews from pyrevit.forms.select_views()
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


# items = [{'item 1','test'}, 'item 2', 'item 3']
# res = forms.SelectFromList.show(context = items, multiselect = True, title = 'Select Scope Boxes', button_name = 'Select Scope Boxes')

class MyOption(forms.TemplateListItem):
    def __init__(self, angle, item, checked=False):
        self.angle = angle
        self.item = item
        self.checked = checked

    @property
    def name(self):
        return "Angle: {}  |  Name: {}".format(self.angle, self.item)

# Creating instances of MyOption with the required arguments
ops = [
    MyOption('15.00000', 'op1'),
    MyOption('20.00000', 'op2', checked=True),
    MyOption('5.00000  ' , 'op3')
    ]

# Using the SelectFromList method to display options
res = forms.SelectFromList.show(ops, multiselect=True, button_name='Select Item')

if res:
    UI_angle = forms.ask_for_string(            # User Input (UI)
        default='30.0',
        prompt='Enter an angle: [degrees]',
        title='Rotate Scope Boxes'
    )
    try:
        UI_angle_float = float(UI_angle.replace(',', '.'))
        print(UI_angle_float)
    except:
        forms.alert("Please enter a number.\nA ',' or '.' can be used to separate the decimals. e.g. 30.5 or 30,5", exitscript=True)

