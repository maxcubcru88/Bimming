# -*- coding: utf-8 -*-
__title__ = "Accuracy\nPrecision"
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
# Custom Libraries
from Snippets._MaxCreates import *

# Regular + Autodesk
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI.Selection import ObjectType

# pyRevit
from pyrevit import forms
from pyrevit.revit.report import print_view

#Others
import math

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

#3️⃣ WPF Form to set the angle if any scope box is selected

UI_angle = forms.ask_for_string(            # User Input (UI)
    default='2',
    prompt='Enter maximum number of decimals allowed: [degrees]',
    title='Splash!')
try:
    UI_max_number_of_decimals = int(UI_angle)
except:
    forms.alert("Please enter a number and press 'Splash!'.\n\ne.g. '2' or '3'", exitscript=True)


all_walls        = FilteredElementCollector(doc).OfClass(Wall).ToElements()
all_grids        = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Grids).WhereElementIsNotElementType().ToElements()
all_ref_planes   = FilteredElementCollector(doc, doc.ActiveView.Id).OfClass(ReferencePlane).ToElements()

collector = list(all_walls) + list(all_grids) + list(all_ref_planes)

# GROUPING PARALLEL AND PERPENDICULAR ELEMENTS USING THEIR VECTOR DIRECTION
# MOVING ALL THE VECTORS TO THE 1ST QUADRANT

items_group_1 = []
items_group_2 = []

for element in collector:

    if isinstance(element, Wall):
        direction = element.Location.Curve.Direction
    elif isinstance(element, Grid):
        direction = element.Curve.Direction
    elif isinstance(element, ReferencePlane):
        direction = element.Direction
    else:
        continue

    angle_to_X = round(math.degrees(direction.AngleTo(XYZ(1,0,0))),12)

    if count_decimals(angle_to_X) <= UI_max_number_of_decimals:
        items_group_1.append(element)
    else:
        items_group_2.append(element)

# OVERRIDING THE ELEMENTS
#colors = generate_random_colors(len(groups))
color_green = Color(0, 210, 0)
color_red   = Color(255, 0, 0)

t = Transaction(doc, 'MC-One Elements Splasher')
t.Start()

solid_fill_pattern = FillPatternElement.GetFillPatternElementByName(doc, FillPatternTarget.Drafting, '<Solid Fill>').Id

for element in items_group_1:
    settings = set_graphics_override_direction(line_weight=5, color_lines=color_green, color_surfaces=lighten_color(color_green,0.45), fill_pattern_id=solid_fill_pattern)
    doc.ActiveView.SetElementOverrides(element.Id, settings)

for element in items_group_2:
    settings = set_graphics_override_direction(line_weight=5, color_lines=color_red, color_surfaces=lighten_color(color_red,0.45), fill_pattern_id=solid_fill_pattern)
    doc.ActiveView.SetElementOverrides(element.Id, settings)

t.Commit()