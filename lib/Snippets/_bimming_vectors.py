# -*- coding: utf-8 -*-

# Imports
#==================================================
import math
from Autodesk.Revit.DB import *

# Variables
#==================================================
app   = __revit__.Application
uidoc = __revit__.ActiveUIDocument
doc   = __revit__.ActiveUIDocument.Document #type:Document

# Reusable Snippets
#==================================================
def is_parallel_to_z(vector):
    """Checks if a given vector is parallel to the Z-axis.

    Args:
        vector (XYZ): The vector to check.

    Returns:
        bool: True if the vector is parallel to the Z-axis, False otherwise.
    """
    z_axis = XYZ.BasisZ
    dot_product = vector.DotProduct(z_axis)
    if abs(dot_product) > 0.9999: # Check if the dot product is close to 1 or -1
        return True
    else:
        return False

def get_angles_against_x(vectors):
    """Calculates the angles of given vectors relative to the X-axis.

    Args:
        vectors (list of XYZ): A list of vectors.

    Returns:
        list of float: A list of angles in degrees between each vector and the X-axis.
    """
    angles = []
    x_axis = XYZ.BasisY
    for vector in vectors:
        angle = vector.AngleTo(x_axis)
        angle_degrees = math.degrees(angle)
        angles.append(angle_degrees)
    return angles