# -*- coding: utf-8 -*-
__title__ = "One Direction\nSplasher"
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
# Regular + Autodesk
from Autodesk.Revit.DB import *

from Autodesk.Revit.UI.Selection import ObjectType
import random
import math

# pyRevit
from pyrevit import revit, forms
from rpw.ui import Selection

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

#1️⃣ Select Wall, Grid or Ref Planes

# # Get Views - Selected in a projectBrowser
# sel_el_ids  = uidoc.Selection.GetElementIds()
# sel_elem    = [doc.GetElement(e_id) for e_id in sel_el_ids]
# sel_views   = [el for el in sel_elem if issubclass(type(el), View)]

try:
    # Get Views - Selected in a projectBrowser
    sel_elem_reference  = uidoc.Selection.PickObject(ObjectType.Element, "Select elements")
    sel_elem_id = sel_elem_reference.ElementId
    sel_elem = doc.GetElement(sel_elem_id)
except:
    # If None Selected - Promp SelectViews from pyrevit.forms.select_views()
    forms.alert('No Elements Selected. Please Try Again', exitscript=True)

if isinstance(sel_elem, Wall):
    sel_elem_direction = sel_elem.Location.Curve.Direction
elif isinstance(sel_elem, Grid):
    sel_elem_direction = sel_elem.Curve.Direction
elif isinstance(sel_elem, ReferencePlane):
    sel_elem_direction = sel_elem.Direction
else:
    pass

sel_elem_direction_first_quadrant = move_vector_to_first_quadrant(sel_elem_direction)

all_walls        = FilteredElementCollector(doc).OfClass(Wall).ToElements()
all_grids        = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Grids).WhereElementIsNotElementType().ToElements()
all_ref_planes   = FilteredElementCollector(doc, doc.ActiveView.Id).OfClass(ReferencePlane).ToElements()

collector = list(all_walls) + list(all_grids) + list(all_ref_planes)

# GROUPING PARALLEL AND PERPENDICULAR ELEMENTS USING THEIR VECTOR DIRECTION
# MOVING ALL THE VECTORS TO THE 1ST QUADRANT

items_parallels_perpendicular = []
items_NO_parallels_perpendicular = []

for element in collector:

    if isinstance(element, Wall):
        direction = element.Location.Curve.Direction
    elif isinstance(element, Grid):
        direction = element.Curve.Direction
    elif isinstance(element, ReferencePlane):
        direction = element.Direction
    else:
        continue

    direction_first_quadrant = move_vector_to_first_quadrant(direction)

    if are_vectors_parallel(sel_elem_direction_first_quadrant, direction_first_quadrant):
        items_parallels_perpendicular.append(element)
    else:
        items_NO_parallels_perpendicular.append(element)

# OVERRIDING THE ELEMENTS
#colors = generate_random_colors(len(groups))
color_green = Color(0, 210, 0)
color_red   = Color(255, 0, 0)

t = Transaction(doc, 'MC-One Elements Splasher')
t.Start()

solid_fill_pattern = FillPatternElement.GetFillPatternElementByName(doc, FillPatternTarget.Drafting, '<Solid Fill>').Id

for element in items_parallels_perpendicular:
    settings = set_graphics_override_direction(line_weight=5, color_lines=color_green, color_surfaces=lighten_color(color_green,0.45), fill_pattern_id=solid_fill_pattern)
    doc.ActiveView.SetElementOverrides(element.Id, settings)

for element in items_NO_parallels_perpendicular:
    settings = set_graphics_override_direction(line_weight=5, color_lines=color_red, color_surfaces=lighten_color(color_red,0.45), fill_pattern_id=solid_fill_pattern)
    doc.ActiveView.SetElementOverrides(element.Id, settings)

t.Commit()