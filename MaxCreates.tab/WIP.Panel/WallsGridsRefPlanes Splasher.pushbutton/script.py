# -*- coding: utf-8 -*-
__title__ = "Direction\nSplasher"
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

import random
import math

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
#==================================================
# Regular + Autodesk
from Autodesk.Revit.DB import *

# pyRevit
from pyrevit import revit, forms

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
#==================================================
doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app   = __revit__.Application

# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝ MAIN
#==================================================

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

def group_walls_by_direction(walls, directions):
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
            if are_vectors_parallel(direction, compare_direction):
                group.append(compare_wall)
                visited.append(j)

        grouped_walls.append(group)

    return grouped_walls

def are_vectors_parallel(norm_vec1, norm_vec2, tolerance=1e-9):
    # Check if they are parallel or antiparallel by comparing normalized vectors
    return norm_vec1.IsAlmostEqualTo(norm_vec2, tolerance) or norm_vec1.IsAlmostEqualTo(-norm_vec2, tolerance)

#1️⃣ Select Wall, Grid or Ref Planes

# # Get Views - Selected in a projectBrowser
# sel_el_ids  = uidoc.Selection.GetElementIds()
# sel_elem    = [doc.GetElement(e_id) for e_id in sel_el_ids]
# sel_views   = [el for el in sel_elem if issubclass(type(el), View)]
#
# # If None Selected - Promp SelectViews from pyrevit.forms.select_views()
# if not sel_views:
#     sel_views = forms.select_views()
#
# # Ensure Views Selected
# if not sel_views:
#     forms.alert('No Views Selected. Please Try Again', exitscript=True)

all_walls        = FilteredElementCollector(doc).OfClass(Wall).ToElements()
all_grids        = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Grids).WhereElementIsNotElementType().ToElements()

all_walls_vectors = [w.Location.Curve.Direction for w in all_walls]
# print(all_grids[1].Curve.Direction)

# MOVING ALL THE VECTORS TO THE 1ST QUADRANT

items = []
vectors = []

for wall in all_walls:
    direction = wall.Location.Curve.Direction
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
    items.append(wall)
    vectors.append(direction)


def set_graphics_override_direction(color_lines, color_surfaces):
    # Create an OverrideGraphicSettings object
    override_settings = OverrideGraphicSettings()

    # Set color override lines
    override_settings.SetProjectionLineColor(color_lines)
    override_settings.SetCutLineColor(color_lines)

    # Set color override surfaces
    override_settings.SetSurfaceBackgroundPatternColor(color_surfaces)
    override_settings.SetSurfaceForegroundPatternColor(color_surfaces)
    override_settings.SetCutBackgroundPatternColor(color_surfaces)
    override_settings.SetCutForegroundPatternColor(color_surfaces)

    solid_fill_pattern = FillPatternElement.GetFillPatternElementByName(doc, FillPatternTarget.Drafting, '<Solid Fill>')

    override_settings.SetSurfaceBackgroundPatternId(solid_fill_pattern.Id)
    override_settings.SetSurfaceForegroundPatternId(solid_fill_pattern.Id)
    override_settings.SetCutBackgroundPatternId(solid_fill_pattern.Id)
    override_settings.SetCutForegroundPatternId(solid_fill_pattern.Id)

    return override_settings

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

groups = (group_walls_by_direction(items, vectors))

colors = generate_random_colors(len(groups))

t = Transaction(doc, 'MC-Elements Splasher')
t.Start()

for group, color in zip(groups, colors):
    settings = set_graphics_override_direction(color, lighten_color(color,0.6))
    for el in group:
        # print(el.Id)
        # print(settings)
        doc.ActiveView.SetElementOverrides(el.Id, settings)

t.Commit()