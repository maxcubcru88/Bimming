# -*- coding: utf-8 -*-
__title__ = "One-Direction\nSplasher"
__doc__ = """Colors elements in the active view based on their alignment with the selected wall, reference plane, or grid:\
elements parallel or perpendicular to the selected one are highlighted in green, while all others are highlighted in red.

Author: Máximo Cubero"""

__min_revit_ver__ = 2023
__max_revit_ver__ = 2025

# CONSTANTS
#==================================================
TRANSACTION_NAME = "Bimming-One Direction Splasher"

# IMPORTS
#==================================================
# Custom Libraries
from Snippets._bimming_graphics_override import *
from Snippets._bimming_selection import *
# Regular + Autodesk
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI.Selection import ObjectType
# pyRevit
from pyrevit import forms

# VARIABLES
#==================================================
doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app   = __revit__.Application

# MAIN
#==================================================

# 🫳Select Wall, Grid or Ref Planes

# Get Views - Selected in a projectBrowser
sel_el_ids      = uidoc.Selection.GetElementIds()
sel_elem        = [doc.GetElement(e_id) for e_id in sel_el_ids]
sel_elem_filter = [el for el in sel_elem if issubclass(type(el), Wall) or issubclass(type(el), Grid) or issubclass(type(el), ReferencePlane)]

if len(sel_elem_filter) != 1:
    with forms.WarningBar(title='Select Wall, Grid or Ref Plane:'):
        try:
            # Get Element - Selected in a projectBrowser
            sel_elem_reference  = uidoc.Selection.PickObject(ObjectType.Element,
                                                             IselectionFilter_Categories([BuiltInCategory.OST_Walls,
                                                                                          BuiltInCategory.OST_Grids,
                                                                                          BuiltInCategory.OST_CLines]),
                                                             "Select elements")
            sel_elem_id = sel_elem_reference.ElementId
            sel_elem = doc.GetElement(sel_elem_id)
        except:
            # If None Selected - Prompt SelectViews from pyrevit.forms.select_views()
            forms.alert('No Elements Selected. Please Try Again', exitscript=True)
else:
    sel_elem = sel_elem_filter[0] # Selecting the only element in the list
    pass

# 🔥Splashing!
# 1️⃣Getting the direction of the element selected
direction = get_direction(sel_elem)
if direction == None:
    forms.alert('The element has not the attribute direction. Select a linear one.', exitscript=True)

# 2️⃣"Reversing" and "Rotating" vectors to have them all in the first quadrant to read the angle against X axis
sel_angle = get_angle_to_vector(direction, XYZ(1,0,0))[0]
# print ('Angle to Axis X: {}'.format(sel_angle))
sel_angle_decimal = Decimal(sel_angle)
sel_quadrant = get_vector_quadrant(direction)
if sel_angle_decimal == 0 or sel_angle_decimal == 90 or sel_angle_decimal == 180:
    sel_angle = '%.12f' % (0)
elif sel_quadrant == 'Quadrant 1':
    sel_angle = sel_angle
elif sel_quadrant == 'Quadrant 2':
    sel_angle = '%.12f' % (sel_angle_decimal - 90)
elif sel_quadrant == 'Quadrant 3':
    sel_angle = '%.12f' % (180 - sel_angle_decimal)
elif sel_quadrant == 'Quadrant 4':
    sel_angle = '%.12f' % (90 - sel_angle_decimal)
# print ('Angle in the first quadrant - sel_angle: {}'.format(sel_angle))
# print ('Type: {}'.format(type(sel_angle)))

# 3️⃣COLLECTING WALLS, GRIDS AND REFERENCE PLANES IN THE ACTIVE VIEW
all_walls        = FilteredElementCollector(doc, doc.ActiveView.Id).OfClass(Wall).ToElements()
all_grids        = FilteredElementCollector(doc, doc.ActiveView.Id).OfCategory(BuiltInCategory.OST_Grids).WhereElementIsNotElementType().ToElements()
all_ref_planes   = FilteredElementCollector(doc, doc.ActiveView.Id).OfClass(ReferencePlane).ToElements()

collector = list(all_walls) + list(all_grids) + list(all_ref_planes)

# 4️⃣GROUPING THE ELEMENTS
items_group_1 = [] # Group that includes the elements which are parallel or perpendicular to the one selected
items_group_2 = [] # Group for the rest of the elements

for element in collector:
    direction   = get_direction(element)
    if not direction:
        continue
    vector_X    = XYZ(1,0,0)
    angle  = get_angle_to_vector(direction, vector_X)[0]
    # print ('Angle to Axis X: {}'.format(angle))
    angle_decimal = Decimal(angle)
    quadrant = get_vector_quadrant(direction)
    if angle_decimal == 0 or angle_decimal == 90 or angle_decimal == 180:
        angle = '%.12f' % (0)
        case = 'case 1'
    elif quadrant == 'Quadrant 1':
        angle = angle
        case = 'case 2'
    elif quadrant == 'Quadrant 2':
        angle = '%.12f' % (angle_decimal - 90)
        case = 'case 3'
    elif quadrant == 'Quadrant 3':
        angle = '%.12f' % (180 - angle_decimal)
        case = 'case 4'
    elif quadrant == 'Quadrant 4':
        angle = '%.12f' % (90 - angle_decimal)
        case = 'case 5'
    # print ('Angle in the first quadrant: {} - {}'.format(angle, case))

    if  angle == sel_angle:
        items_group_1.append(element)
    else:
        items_group_2.append(element)

# 5️⃣OVERRIDING THE ELEMENTS
color_green = Color(0, 210, 0)
color_red   = Color(255, 0, 0)

t = Transaction(doc, TRANSACTION_NAME)
t.Start()

solid_fill_pattern = FillPatternElement.GetFillPatternElementByName(doc, FillPatternTarget.Drafting, '<Solid Fill>').Id

for element in items_group_1:
    settings = set_graphics_override_direction(line_weight=5, color_lines=color_green, color_surfaces=lighten_color(color_green,0.45), fill_pattern_id=solid_fill_pattern)
    doc.ActiveView.SetElementOverrides(element.Id, settings)

for element in items_group_2:
    settings = set_graphics_override_direction(line_weight=5, color_lines=color_red, color_surfaces=lighten_color(color_red,0.45), fill_pattern_id=solid_fill_pattern)
    doc.ActiveView.SetElementOverrides(element.Id, settings)

t.Commit()
