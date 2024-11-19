# -*- coding: utf-8 -*-
__title__ = "Wall Angle"
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
import math

# Custom Libraries
from Snippets._MaxCreates import *
from Snippets._selection import *

# Regular + Autodesk
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI.Selection import ObjectType

# pyRevit
from pyrevit import forms

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
#==================================================
doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app   = __revit__.Application


def calculate_angle_with_x(vector):
    """
    Calculate the angle between the given vector and the X-axis.

    Args:
        vector (XYZ): The input vector.

    Returns:
        tuple: A tuple containing the angle in radians and degrees.
    """
    # Define the X-axis vector
    x_vector = XYZ(1, 0, 0)

    # Calculate the dot product of the vectors
    dot_product = vector.DotProduct(x_vector)

    # Calculate the magnitude of the vectors
    magnitude_vector = vector.GetLength()
    magnitude_x_vector = x_vector.GetLength()

    # Ensure non-zero magnitude to avoid division by zero
    if magnitude_vector == 0 or magnitude_x_vector == 0:
        raise ValueError("Vector magnitudes cannot be zero.")

    # Calculate the cosine of the angle
    cos_angle = dot_product / (magnitude_vector * magnitude_x_vector)

    # Clamp the cosine value to avoid precision errors outside [-1, 1]
    cos_angle = max(min(cos_angle, 1.0), -1.0)

    # Calculate the angle in radians
    angle_radians = math.acos(cos_angle)

    # Convert radians to degrees
    angle_degrees = math.degrees(angle_radians)

    print (angle_degrees)

    return angle_radians, angle_degrees


def calculate_angle_with_x_B(vector):
    """
    Calculate the signed angle between the given vector and the X-axis.

    Args:
        vector (XYZ): The input vector.

    Returns:
        tuple: A tuple containing the signed angle in radians and degrees.
    """
    # Define the X-axis vector
    x_vector = XYZ(1, 0, 0)

    # Normalize the input vector to avoid magnitude issues
    if vector.GetLength() == 0:
        raise ValueError("The input vector cannot have zero length.")

    normalized_vector = vector.Normalize()
    normalized_x_vector = x_vector.Normalize()

    # Calculate the dot product and magnitudes
    dot_product = normalized_vector.DotProduct(normalized_x_vector)
    cross_product = normalized_vector.CrossProduct(normalized_x_vector)

    # Clamp the dot product to avoid precision issues
    dot_product = max(min(dot_product, 1.0), -1.0)

    # Calculate the angle in radians
    angle_radians = math.acos(dot_product)

    # Use the cross product to determine the sign (direction)
    if cross_product.Z < 0:  # Assumes 2D comparison; checks Z for 2D vectors
        angle_radians = -angle_radians  # Make angle negative for clockwise

    # Convert to degrees
    angle_degrees = math.degrees(angle_radians)

    return "direction angle", angle_degrees

# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝ MAIN
#==================================================

#1️⃣ Select Wall, Grid or Ref Planes
# Get Views - Selected in a projectBrowser
sel_el_ids      = uidoc.Selection.GetElementIds()
sel_elem        = [doc.GetElement(e_id) for e_id in sel_el_ids]
sel_elem_filter = [el for el in sel_elem if issubclass(type(el), Wall) or issubclass(type(el), Grid) or issubclass(type(el), ReferencePlane)]

if not sel_elem_filter:
    with forms.WarningBar(title='Select Wall, Grid or Ref Plane:'):
        try:
            # Get Views - Selected in a projectBrowser
            sel_elem_reference  = uidoc.Selection.PickObjects(ObjectType.Element,
                                                             IselectionFilter_Categories([BuiltInCategory.OST_Walls,
                                                                                          BuiltInCategory.OST_Grids,
                                                                                          BuiltInCategory.OST_CLines]),
                                                             "Select elements")
            sel_elem_id = [el.ElementId for el in sel_elem_reference]
            sel_elem = [doc.GetElement(id) for id in sel_elem_id]
        except:
            # If None Selected - Promp SelectViews from pyrevit.forms.select_views()
            forms.alert('No Elements Selected. Please Try Again', exitscript=True)
else:
    pass

for elem in sel_elem:
    if isinstance(elem, Wall):
        direction = elem.Location.Curve.Direction
    elif isinstance(elem, Grid):
        direction = elem.Curve.Direction
    elif isinstance(elem, ReferencePlane):
        direction = elem.Direction
    else:
        pass
    print(calculate_angle_with_x_B(direction))

# if isinstance(sel_elem, Wall):
#     direction = sel_elem.Location.Curve.Direction
# elif isinstance(sel_elem, Grid):
#     direction = sel_elem.Curve.Direction
# elif isinstance(sel_elem, ReferencePlane):
#     direction = sel_elem.Direction
# else:
#     pass
# print(calculate_angle_with_x(direction))
# print(calculate_angle_with_x_B(direction))

# angle_to_X = round(math.degrees(direction.AngleTo(XYZ(1,0,0))),10) # number max of decimas is 10
# print(angle_to_X)
#
# print ('-'*100)
# number = 1.231654984651321354987654321321
# print(str(number))



# print(calculate_angle_with_x(direction))