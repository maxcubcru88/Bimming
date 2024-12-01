# -*- coding: utf-8 -*-

# Imports
#==================================================
import random
import math

from decimal import Decimal, getcontext, ROUND_HALF_UP

from Snippets._convert import *

from Autodesk.Revit.DB import *
from pyrevit import forms

from collections import defaultdict

# Variables
#==================================================
app   = __revit__.Application
uidoc = __revit__.ActiveUIDocument
doc   = __revit__.ActiveUIDocument.Document #type:Document

# Reusable Snippets

def rotate_vector_with_transform(vector, axis, angle):
    """
    Rotates a vector using Revit's Transform class around a given axis by a specified angle.

    Parameters:
        vector: The vector to be rotated (XYZ object).
        axis: The axis of rotation (XYZ object, should be normalized).
        angle: The angle of rotation in radians.

    Returns:
        The rotated vector as an XYZ object.
    """
    # Create a rotation transform using the axis and angle
    rotation_transform = Transform.CreateRotationAtPoint(axis, angle, XYZ(0, 0, 0))

    # Apply the rotation transform to the vector (treated as a point from the origin)
    rotated_vector = rotation_transform.OfPoint(vector)

    return rotated_vector

# # Example usage
# vec = XYZ(1, 0, 0)  # Vector to rotate
# axis = XYZ(0, 0, 1)  # Rotation axis (Z-axis)
# angle = math.radians(90)  # Rotate by 90 degrees

def group_walls_by_direction(walls, directions, tolerance=1e-14):
    grouped_walls = []
    visited = []

    for i, wall in enumerate(walls):
        if i in visited:
            continue

        group = [wall]
        visited.append(i)
        direction = directions[i]

        for j, compare_wall in enumerate(walls):
            if j <= i or j in visited:
                continue

            compare_direction = directions[j]
            if are_vectors_parallel(direction, compare_direction, tolerance):
                group.append(compare_wall)
                visited.append(j)

        grouped_walls.append(group)

    return grouped_walls

def are_vectors_parallel(norm_vec1, norm_vec2, tolerance=1e-14):
    # Check if they are parallel or antiparallel by comparing normalized vectors
    return norm_vec1.IsAlmostEqualTo(norm_vec2, tolerance) or norm_vec1.IsAlmostEqualTo(-norm_vec2, tolerance)

def move_vector_to_first_quadrant(direction):
    if direction.X < 0 and direction.Y > 0:                         # second quadrant - The vector is rotated -90 degrees
        direction = rotate_vector_with_transform(vector=direction, axis=XYZ(0, 0, 1), angle=math.radians(-90))
        #print(direction)
    elif direction.X < 0 and direction.Y < 0:                       # third quadrant  - The vector is reversed, but it could be rotated +- 180 degrees
        direction = XYZ(-direction.X, -direction.Y, direction.Z)
        #print(direction)
    elif direction.X > 0 and direction.Y < 0:                       # fourth quadrant - The vector is rotated 90 degrees
        direction = rotate_vector_with_transform(vector=direction, axis=XYZ(0, 0, 1), angle=math.radians(90))
        #print(direction)
    else: pass
    return direction

def move_vector_to_first_and_second_quadrant(direction):
    # Set the precision high enough for calculations
    getcontext().prec = 50  # High precision for intermediate calculations

    X = Decimal(direction.X)
    Y = Decimal(direction.Y)

    rounded_value_X = X.quantize(Decimal('0.0000000000001'), rounding=ROUND_HALF_UP)
    rounded_value_Y = Y.quantize(Decimal('0.0000000000001'), rounding=ROUND_HALF_UP)
                                        # 0.1234567890123

    if rounded_value_X <= 0 and rounded_value_Y < 0:                       # third quadrant  - The vector is reversed, but it could be rotated +- 180 degrees
        direction = XYZ(-direction.X, -direction.Y, direction.Z)
    elif rounded_value_X >= 0 and rounded_value_Y < 0:                       # fourth quadrant - The vector is reversed to the second quadrant
        direction = XYZ(-direction.X, -direction.Y, direction.Z)
    else: pass
    return direction

def move_vector_to_first_and_fourth_quadrant(direction):
    # Set the precision high enough for calculations
    getcontext().prec = 50  # High precision for intermediate calculations

    X = Decimal(direction.X)
    Y = Decimal(direction.Y)

    rounded_value_X = X.quantize(Decimal('0.0000000000001'), rounding=ROUND_HALF_UP)
    rounded_value_Y = Y.quantize(Decimal('0.0000000000001'), rounding=ROUND_HALF_UP)
                                        # 0.1234567890123

    if rounded_value_X < 0 and rounded_value_Y >= 0:                       # second quadrant  - The vector is reversed, but it could be rotated +- 180 degrees
        direction = XYZ(-direction.X, -direction.Y, direction.Z)
    elif rounded_value_X < 0 and rounded_value_Y <= 0:                       # third quadrant - The vector is reversed to the second quadrant
        direction = XYZ(-direction.X, -direction.Y, direction.Z)
    else: pass
    return direction

def set_graphics_override_direction(line_weight = -1 ,
                                    color_lines = Color.InvalidColorValue,
                                    color_surfaces = Color.InvalidColorValue,
                                    fill_pattern_id = ElementId.InvalidElementId):

    # Color.InvalidColorValue       -> means no override for the color is set.
    # ElementId.InvalidElementId    -> means no override for the fill pattern is set

    # Create an OverrideGraphicSettings object
    override_settings = OverrideGraphicSettings()

    # Set weight override Ref Planes
    override_settings.SetCutLineWeight(line_weight)
    override_settings.SetProjectionLineWeight(line_weight)

    # Set color override lines
    override_settings.SetProjectionLineColor(color_lines)
    override_settings.SetCutLineColor(color_lines)

    # Set color override surfaces
    override_settings.SetSurfaceBackgroundPatternColor(color_surfaces)
    override_settings.SetSurfaceForegroundPatternColor(color_surfaces)
    override_settings.SetCutBackgroundPatternColor(color_surfaces)
    override_settings.SetCutForegroundPatternColor(color_surfaces)

    override_settings.SetSurfaceBackgroundPatternId(fill_pattern_id)
    override_settings.SetSurfaceForegroundPatternId(fill_pattern_id)
    override_settings.SetCutBackgroundPatternId(fill_pattern_id)
    override_settings.SetCutForegroundPatternId(fill_pattern_id)

    return override_settings

def get_direction(element):
    """
    get direction of element
    :param element
    :return XYZ vector
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

def generate_random_colors(n):
    colors = []
    for _ in range(n):
        # Generate random RGB values
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)

        # Create Revit Color and add to list
        color = Color(r, g, b)
        colors.append(color)

    return colors


def lighten_color(color, factor=0.2):
    """
    Lightens the given color by increasing its RGB values.

    :param color: Autodesk.Revit.DB.Color object
    :param factor: Float value (0 to 1) to determine how much lighter to make the color.
                   Default is 0.2 (20% lighter).
    :return: New Autodesk.Revit.DB.Color object with lightened RGB values.
    """
    # Ensure the factor is between 0 and 1
    factor = max(0, min(factor, 1))

    # Extract original RGB values
    r, g, b = color.Red, color.Green, color.Blue

    # Lighten the color by increasing its RGB values proportionally
    new_r = min(int(r + (255 - r) * factor), 255)
    new_g = min(int(g + (255 - g) * factor), 255)
    new_b = min(int(b + (255 - b) * factor), 255)

    # Return the new lightened color
    return Color(new_r, new_g, new_b)

def count_decimals_float(number):
    """
    count the number of decimals

    :number: Float value
    :return:
    """
    # Convert the float to a Decimal
    decimal_number = Decimal(str(number))
    # Get the decimal part only
    decimal_part = abs(decimal_number - decimal_number.to_integral())
    # Convert the decimal part to string and count the digits after the '.'
    return max(0, -decimal_part.as_tuple().exponent)

def count_decimals_string(string):
    """
    count the number of decimals
    :string: Float value
    :return:
    """
    # Convert the float to a Decimal
    decimal_number = Decimal(str(string)).normalize()  # normalize() removes trailing zeros
    # This expression calculates the number of decimal places in a Decimal number.
    # - decimal_number.as_tuple().exponent: Retrieves the exponent of the Decimal number,
    #   which indicates the position of the decimal point relative to the integer part.
    # - The negative sign (-) reverses the exponent to give the count of decimal places.
    # - max(0, ...): Ensures that the result is non-negative, returning 0 if the number has no decimal part.
    number_of_decimals = max(0, -decimal_number.as_tuple().exponent)
    return number_of_decimals

def custom_round(value, precision='0.000000000005', rounding=ROUND_HALF_UP):
    """
    Rounds a given value to the nearest multiple of 0.000000000005 with high precision.

    This function uses the Decimal module to ensure precision and avoids
    floating-point errors. It first converts the input value to a Decimal,
    defines a quantization step of 0.000000000005 to manage rounding, and
    performs the rounding using the ROUND_HALF_UP method.

    Parameters:
        value (float or str): The value to be rounded.

    Returns:
        Decimal: The value rounded to the nearest 0.000000000005.
    """
    # Convert to Decimal for precision
    decimal_value = Decimal(value)

    # Define the quantization step (0.0001, to control 4th decimal place)
    step = Decimal(precision)

    # Quantize the value to the nearest 0.0005
    rounded_value = (decimal_value / step).quantize(Decimal('1'), rounding) * step
    return rounded_value

def get_angle_to_vector(vector1, vector2=XYZ(1, 0, 0)):
    """
    Input vector 1 and vector 2, and the script will return the angle between them + the
    supplementary angle.
    : vector1: vector 1
    : vector2: vector 2
    : return: angle between vector 1 and vector 2
    : return: supplementary angle between vector 1 and vector 2
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

def group_by_second_arg(items):
    """
    Group items by the second element in each tuple.

    :param items: List of tuples
    :return: Dictionary with grouped items
    """
    grouped = defaultdict(list)
    for item in items:
        key = item[1]  # The second element of the tuple
        grouped[key].append(item[0])  # Append the first element to the group
    return dict(grouped)

def dict_to_list(grouped_dict):
    """
    Convert a grouped dictionary into a list of lists.

    :param grouped_dict: Dictionary with grouped items
    :return: List of lists
    """
    return list(grouped_dict.values())

"""# Test data
test = [('elem1', 'D'), ('elem2', 'A'), ('elem3', 'B'), ('elem4', 'D'), ('elem5', 'B')]

# Group the items into a dictionary
grouped_dict = group_by_second_arg(test)

# Convert the dictionary to a list of lists
grouped_list = dict_to_list(grouped_dict)

# Print the results
print("Grouped Dictionary:", grouped_dict)
print("List of Lists:", grouped_list)"""