# -*- coding: utf-8 -*-

# Imports
#==================================================
from Snippets._bimming_numbers import *
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

def get_direction(element):
    """Returns the direction vector of a given Revit element.

    Args:
        element (Element): The Revit element (Wall, Grid, or ReferencePlane).

    Returns:
        XYZ: The direction vector of the element, or None if not applicable.
    """
    direction = None
    try:
        if isinstance(element, Wall):
            direction = element.Location.Curve.Direction
        elif isinstance(element, Grid):
            direction = element.Curve.Direction
        elif isinstance(element, ReferencePlane):
            direction = element.Direction
        else:
            pass
    except: pass
    return direction

def get_vector_quadrant(direction):
    """Determines the quadrant of a given 2D direction vector.

    Args:
        direction (XYZ): The direction vector.

    Returns:
        str: The quadrant name ('Quadrant 1', 'Quadrant 2', etc.)
             or 'Align with X or Y Axis' if the vector lies on an axis.
    """
    X = direction.X
    Y = direction.Y
    if X > 0 and Y > 0:
        return 'Quadrant 1'
    elif X < 0 and Y > 0:
        return 'Quadrant 2'
    elif X < 0 and Y < 0:
        return 'Quadrant 3'
    elif X > 0 and Y < 0:
        return 'Quadrant 4'
    else:
        return 'Align with X or Y Axis'

def get_angle_to_vector(vector1, vector2=XYZ(1, 0, 0)):
    """
    Calculates the angle and its supplementary angle between two vectors.

    Args:
        vector1 (XYZ): The first vector.
        vector2 (XYZ, optional): The second vector (default: X-axis unit vector).

    Returns:
        tuple (str, str): Angle and supplementary angle, formatted to 12 decimal places.
    """
    # Calculate angle using the method 'AngleTo' of the Revit API
    angle_to_X = vector1.AngleTo(vector2)

    # Convert radians to degrees - Maximum number of decimals is 9
    angle_to_X_degrees = convert_internal_units(angle_to_X, False, 'degrees')
    # print('Angle from radians {} to degrees:\n{}'.format(angle_to_X, angle_to_X_degrees))

    # Set the precision high enough for calculations -- Not entirely sure why we need this.
    getcontext().prec = 50  # High precision for intermediate calculations

    # With 'Decimals' we read up to 44 decimals
    angle_to_X_decimals = Decimal(angle_to_X_degrees)
    # print('Angle with more precision using the modulo "Decimals":\n{}'.format(angle_to_X_decimals))

    # We use the function 'custom_round' which Rounds a given value to the nearest multiple of 0.000000000005 (12 decimals) with high precision.
    angle_to_X_rounded = custom_round(angle_to_X_decimals, precision='0.000000000005', rounding=ROUND_HALF_UP)
    supplementary_angle = 180 - angle_to_X_rounded

    # Format the output to always show 12 decimal places and avoid results like E0-12
    angle_to_X_formated = '%.12f' % (angle_to_X_rounded)
    supplementary_angle_formated = '%.12f' % (supplementary_angle)

    return angle_to_X_formated, supplementary_angle_formated