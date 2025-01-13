# -*- coding: utf-8 -*-
__title__ = "Read\nAngle"
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

# IMPORTS
#==================================================
# Custom Libraries
from Snippets._MaxCreates import *
from Snippets._selection import *

# Regular + Autodesk
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI.Selection import ObjectType

# pyRevit
from pyrevit import forms

# VARIABLES
#==================================================
doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app   = __revit__.Application

# MAIN
#==================================================

#🫳 Select Wall, Grid or Ref Planes

# Get Views - Selected in a projectBrowser
sel_el_ids      = uidoc.Selection.GetElementIds()
sel_elem        = [doc.GetElement(e_id) for e_id in sel_el_ids]
sel_elem_filter = [el for el in sel_elem if issubclass(type(el), Wall) or issubclass(type(el), Grid) or issubclass(type(el), ReferencePlane)]

if len(sel_elem_filter) != 1:
    with forms.WarningBar(title='Select Wall, Grid or Ref Plane:'):
        try:
            # Get Element - Selected in a projectBrowser
            sel_elem_reference  = uidoc.Selection.PickObject(ObjectType.Element,
                                                             IselectionFilter_Categories([BuiltInCategory.OST_Walls,
                                                                                          BuiltInCategory.OST_Grids,
                                                                                          BuiltInCategory.OST_CLines]),
                                                             "Select elements")
            sel_elem_id = sel_elem_reference.ElementId
            sel_elem = doc.GetElement(sel_elem_id)
        except:
            # If None Selected - Prompt SelectViews from pyrevit.forms.select_views()
            forms.alert('No Elements Selected. Please Try Again', exitscript=True)
else:
    sel_elem = sel_elem_filter[0] # Selecting the only element in the list
    pass

#🔥 Calculating the angle

#1️⃣ Getting the direction of the element
direction = get_direction(sel_elem)
if direction == None:
    forms.alert('The element has not the attribute direction. Select a linear one.', exitscript=True)

# print("Original direction: {}".format(direction))

#2️⃣ ANGLE TO VECTOR X --> XYZ(1,0,0)
vector_X = XYZ(1,0,0)
angle_to_X = get_angle_to_vector(direction, vector_X)
vector_Y = XYZ(0,1,0)
angle_to_Y = get_angle_to_vector(direction, vector_Y)

forms.alert(
            "ANGLES TO VECTORS X & Y\n\n"
            "VECTOR X - XYZ(1,0,0)\n"
            "{} [Angle]\n"
            "{} [Supplementary Angle]\n\n"
            "VECTOR Y - XYZ (0,1,0)\n"
            "{} [Angle]\n"
            "{} [Supplementary Angle]"
            .format(angle_to_X[0], angle_to_X[1], angle_to_Y[0], angle_to_Y[1])
            )