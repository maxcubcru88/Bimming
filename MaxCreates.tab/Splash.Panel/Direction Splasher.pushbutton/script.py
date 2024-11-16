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

# import random

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
#==================================================
# Custom Libraries
from Snippets._MaxCreates import *

# Regular + Autodesk
from Autodesk.Revit.DB import *

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

#1️⃣ Collect Walls, Grids and Ref Planes

all_walls        = FilteredElementCollector(doc).OfClass(Wall).ToElements()
all_grids        = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Grids).WhereElementIsNotElementType().ToElements()
all_ref_planes   = FilteredElementCollector(doc, doc.ActiveView.Id).OfClass(ReferencePlane).ToElements()

collector = list(all_walls) + list(all_grids) + list(all_ref_planes)

# GROUPING PARALLEL AND PERPENDICULAR ELEMENTS USING THEIR VECTOR DIRECTION
# MOVING ALL THE VECTORS TO THE 1ST QUADRANT

items = []
vectors = []

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

    items.append(element)
    vectors.append(direction_first_quadrant)

#GROUPING BY THEIR DIRECTION
groups = (group_walls_by_direction(items, vectors, tolerance=1e-14))

# OVERRIDING THE ELEMENTS
colors = generate_random_colors(len(groups))

t = Transaction(doc, 'MC-Elements Splasher')
t.Start()

solid_fill_pattern = FillPatternElement.GetFillPatternElementByName(doc, FillPatternTarget.Drafting, '<Solid Fill>').Id

for group, color in zip(groups, colors):
    settings = set_graphics_override_direction(line_weight=5, color_lines=color, color_surfaces=lighten_color(color,0.45), fill_pattern_id=solid_fill_pattern)
    for el in group:
        doc.ActiveView.SetElementOverrides(el.Id, settings)

t.Commit()