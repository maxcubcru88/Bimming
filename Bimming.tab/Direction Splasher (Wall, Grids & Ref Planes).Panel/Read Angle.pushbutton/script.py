# -*- coding: utf-8 -*-
__title__ = "Read\nAngle"
__doc__ = """Retrieve the angle between a wall, reference plane, or grid line and the X-axis.

Author: Máximo Cubero"""

__min_revit_ver__ = 2021
__max_revit_ver__ = 2025

# IMPORTS
#==================================================
# Custom Libraries
from Snippets._bimming_graphics_override import *
from Snippets._bimming_selection import *

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

# 🫳Select Wall, Grid or Ref Planes

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

# 🔥Calculating the angle

# 1️⃣Getting the direction of the element
direction = get_direction(sel_elem)
if direction == None:
    forms.alert('The element has not the attribute direction. Select a linear one.', exitscript=True)

# print("Original direction: {}".format(direction))

# 2️⃣ANGLE TO VECTOR X --> XYZ(1,0,0)
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