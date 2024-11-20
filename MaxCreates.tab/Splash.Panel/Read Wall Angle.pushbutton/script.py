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
from decimal import Decimal, getcontext, ROUND_HALF_UP

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

    # Calculate the cross product to determine direction
    cross_product = vector.CrossProduct(x_vector)

    # Use the Z-component of the cross product to determine direction
    if cross_product.Z > 0:  # Clockwise direction
        angle_degrees = -angle_degrees

    # Set the precision high enough for calculations
    getcontext().prec = 50  # High precision for intermediate calculations

    # Define the number and round to 12 decimal places
    if angle_degrees <= 90:
        value = Decimal(angle_degrees)
    else:
        value = Decimal(angle_degrees)

    rounded_value = value.quantize(Decimal('0.000000000001'), rounding=ROUND_HALF_UP)

    # Format the output to always show 12 decimal places
    #rounded_value = '%.12f' % rounded_value

    return rounded_value

def calculate_angle_with_y(vector):
    """
    Calculate the angle between the given vector and the X-axis.

    Args:
        vector (XYZ): The input vector.

    Returns:
        tuple: A tuple containing the angle in radians and degrees.
    """
    # Define the X-axis vector
    x_vector = XYZ(0, 1, 0)

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

    # Calculate the cross product to determine direction
    cross_product = vector.CrossProduct(x_vector)

    # Use the Z-component of the cross product to determine direction
    if cross_product.Z < 0:  # Clockwise direction
        angle_degrees = -angle_degrees

    # Set the precision high enough for calculations
    getcontext().prec = 50  # High precision for intermediate calculations

    # Define the number and round to 12 decimal places
    if angle_degrees <= 90:
        value = Decimal(angle_degrees)
    else:
        value = Decimal(angle_degrees)

    rounded_value = value.quantize(Decimal('0.000000000001'), rounding=ROUND_HALF_UP)

    # Format the output to always show 12 decimal places
    #rounded_value = '%.12f' % rounded_value

    return rounded_value

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

for element in sel_elem:
    direction = get_direction(element)
    #print("Original direction: {}".format(direction))
    direction_1st_2nd_quadrant = move_vector_to_first_and_second_quadrant(direction)
    direction_1st_4th_quadrant = move_vector_to_first_and_fourth_quadrant(direction)

    #print("Direction 1st and 2nd quadrant: {}".format(direction_1st_2nd_quadrant))
    #print("Direction 1st and 4th quadrant: {}".format(direction_1st_4th_quadrant))

    angle_against_X = calculate_angle_with_x(direction_1st_2nd_quadrant)
    #print('The angle against Vector X is: {}'.format(angle_against_X))
    angle_against_Y = calculate_angle_with_y(direction_1st_4th_quadrant)
    #print('The angle against Vector Y is: {}'.format(angle_against_Y))

    if angle_against_X < 5 or angle_against_X > 175:
        angle_against_X = 90 - angle_against_Y
        #print('IF')

    elif angle_against_X > 85 and angle_against_X < 95:
        angle_against_Y = 90 - angle_against_X
        #print('ELIF')

    else:
        print('PASS')
        #pass

    # Format the output to always show 12 decimal places
    angle_against_X = '%.12f' % angle_against_X
    print('The angle against Vector X is: {}'.format(angle_against_X))

    angle_against_Y = '%.12f' % angle_against_Y
    print('The angle against Vector Y is: {}'.format(angle_against_Y))
