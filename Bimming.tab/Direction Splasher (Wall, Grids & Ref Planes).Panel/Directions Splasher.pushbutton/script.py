# -*- coding: utf-8 -*-
__title__ = "Directions\nSplasher"
__doc__ = """Colors elements in the active view based on their alignment. Walls, reference planes, \
and grids that are parallel or perpendicular to each other are highlighted in the same color. \
Each unique alignment is represented by a different color.

Author: Máximo Cubero"""

__min_revit_ver__ = 2021
__max_revit_ver__ = 2025

import sys

# CONSTANTS
#==================================================
TRANSACTION_NAME = "Bimming-Directions Splasher"

# IMPORTS
#==================================================
# Custom Libraries
from Snippets._bimming_graphics_override import *
from Snippets._bimming_vectors import *
from Snippets._bimming_lists import *
# Regular + Autodesk
from Autodesk.Revit.DB import *

# VARIABLES
#==================================================
doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app   = __revit__.Application

# MAIN
#==================================================

lst_dict = {}
for e in range(1,12):
    lst_dict[str(e) + ' decimals'] = e

number_of_decimals = forms.ask_for_one_item(
                                            sorted(lst_dict.keys(), key=lambda x: int(x.split()[0])),
                                                default='6 decimals',
                                                prompt='Select the number of decimals to consider when checking\nif walls, ref. planes and grids are parallel/perpendicular',
                                                title='Bimming-Directions Splasher'
                                            )
if not number_of_decimals:
    sys.exit()

# 3️⃣COLLECTING WALLS, GRIDS AND REFERENCE PLANES IN THE ACTIVE VIEW
all_walls        = FilteredElementCollector(doc, doc.ActiveView.Id).OfClass(Wall).ToElements()
all_grids        = FilteredElementCollector(doc, doc.ActiveView.Id).OfCategory(BuiltInCategory.OST_Grids).WhereElementIsNotElementType().ToElements()
all_ref_planes   = FilteredElementCollector(doc, doc.ActiveView.Id).OfClass(ReferencePlane).ToElements()

collector = list(all_walls) + list(all_grids) + list(all_ref_planes)

# 4️⃣GROUPING THE ELEMENTS
elements_tuple = []

for element in collector:
    direction   = get_direction(element)
    if not direction:
        continue
    vector_X    = XYZ(1,0,0)
    angle  = get_angle_to_vector(direction, vector_X, scaled_decimal(1, lst_dict[number_of_decimals]))[0]
    # print ('Angle to Axis X: {}'.format(angle))
    angle_decimal = Decimal(angle)
    quadrant = get_vector_quadrant(direction)
    if angle_decimal == 0 or angle_decimal == 90 or angle_decimal == 180:
        angle = '%.12f' % (0)
    elif quadrant == 'Quadrant 1':
        angle = angle
    elif quadrant == 'Quadrant 2':
        angle = '%.12f' % (angle_decimal - 90)
    elif quadrant == 'Quadrant 3':
        angle = '%.12f' % (180 - angle_decimal)
    elif quadrant == 'Quadrant 4':
        angle = '%.12f' % (90 - angle_decimal)
    # print ('Angle to Axis X: {}'.format(angle))
    elements_tuple.append(tuple((element, angle)))

grouped_dict = group_by_second_arg(elements_tuple)

grouped_list = list(grouped_dict.values())

# 5️⃣OVERRIDING THE ELEMENTS
colors = generate_random_colors(len(grouped_list))

t = Transaction(doc, TRANSACTION_NAME)
t.Start()

solid_fill_pattern = FillPatternElement.GetFillPatternElementByName(doc, FillPatternTarget.Drafting, '<Solid Fill>').Id

for group, color in zip(grouped_list, colors):
    settings = set_graphics_override_direction(line_weight=5, color_lines=color, color_surfaces=lighten_color(color,0.45), fill_pattern_id=solid_fill_pattern)
    for el in group:
        doc.ActiveView.SetElementOverrides(el.Id, settings)

t.Commit()
