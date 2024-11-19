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
# Custom Libraries
from Snippets._MaxCreates import *
from Snippets._selection import *

# Regular + Autodesk
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI.Selection import ObjectType

# pyRevit
from pyrevit import forms
from pyrevit.revit import selection as py_selection

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

#1️⃣ Select Wall, Grid or Ref Planes
# Get Views - Selected in a projectBrowser
sel_el_ids      = uidoc.Selection.GetElementIds()
sel_elem        = [doc.GetElement(e_id) for e_id in sel_el_ids]
sel_elem_filter = [el for el in sel_elem if issubclass(type(el), Wall) or issubclass(type(el), Grid) or issubclass(type(el), ReferencePlane)]

if not sel_elem_filter or len(sel_elem_filter) != 1:
    with forms.WarningBar(title='Select Wall, Grid or Ref Plane:'):
        try:
            # Get Views - Selected in a projectBrowser
            sel_elem_reference  = uidoc.Selection.PickObject(ObjectType.Element,
                                                             IselectionFilter_Categories([BuiltInCategory.OST_Walls,
                                                                                          BuiltInCategory.OST_Grids,
                                                                                          BuiltInCategory.OST_CLines]),
                                                             "Select elements")
            sel_elem_id = sel_elem_reference.ElementId
            sel_elem = doc.GetElement(sel_elem_id)
        except:
            # If None Selected - Promp SelectViews from pyrevit.forms.select_views()
            forms.alert('No Elements Selected. Please Try Again', exitscript=True)
else:
    sel_elem = sel_elem_filter[0]

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

    if are_vectors_parallel(sel_elem_direction_first_quadrant, direction_first_quadrant,tolerance=1e-14):
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