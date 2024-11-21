# -*- coding: utf-8 -*-

# Imports
#==================================================
import random
import math
from decimal import Decimal, getcontext, ROUND_HALF_UP

from Autodesk.Revit.DB import *

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
    if isinstance(element, Wall):
        direction = element.Location.Curve.Direction
    elif isinstance(element, Grid):
        direction = element.Curve.Direction
    elif isinstance(element, ReferencePlane):
        direction = element.Direction
    else:
        pass
    return direction

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

def count_decimals(number):
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