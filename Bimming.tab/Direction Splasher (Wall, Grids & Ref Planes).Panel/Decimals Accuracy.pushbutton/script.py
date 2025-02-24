# -*- coding: utf-8 -*-
__title__ = "Decimals\nAccuracy"
__doc__ = """Colors elements in the active view based on decimal precision: \
walls, reference planes, and grids are highlighted green if their decimal \
places are less than or equal to the specified number, and red if they exceed it.

Author: Máximo Cubero"""

__min_revit_ver__ = 2021
__max_revit_ver__ = 2025

# CONSTANTS
#==================================================
TRANSACTION_NAME = "Bimming-Decimals Accuracy"

# IMPORTS
#==================================================
# Custom Libraries
from Snippets._bimming_graphics_override import *
from Snippets._bimming_vectors import *
# Regular + Autodesk
import sys
from Autodesk.Revit.DB import *
# pyRevit
from pyrevit import forms

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
                                                default='2 decimals',
                                                prompt='Select the maximum number of decimal places that walls, grids\n'
                                                       'reference planes should have. Elements with a higher number of\n'
                                                       'decimals will be highlighted in red in the current view.',
                                                title='Bimming-Directions Splasher'
                                            )
if not number_of_decimals:
    sys.exit()

UI_max_number_of_decimals = lst_dict[number_of_decimals]
# 🔥Splashing walls

# 1️⃣COLLECTING WALLS, GRIDS AND REFERENCE PLANES IN THE ACTIVE VIEW
all_walls        = FilteredElementCollector(doc, doc.ActiveView.Id).OfClass(Wall).ToElements()
all_grids        = FilteredElementCollector(doc, doc.ActiveView.Id).OfCategory(BuiltInCategory.OST_Grids).WhereElementIsNotElementType().ToElements()
all_ref_planes   = FilteredElementCollector(doc, doc.ActiveView.Id).OfClass(ReferencePlane).ToElements()

collector = list(all_walls) + list(all_grids) + list(all_ref_planes)

# 2️⃣GROUPING THE ELEMENTS
items_group_1 = [] # Group that includes the elements with the maximun number of decimals allowed
items_group_2 = [] # Group that includes the elements with more decimals that the maximum allowed

for element in collector:
    direction   = get_direction(element)
    if not direction:
        continue
    vector_X    = XYZ(1,0,0)
    angle_to_X  = get_angle_to_vector(direction, vector_X, scaled_decimal(1, 11))[0]
    # print ('Angle to Axis X: {}'.format(angle_to_X))

    counting_decimals = count_decimals_string(angle_to_X)
    # print ('Number of decimals: {}'.format(counting_decimals))

    if  counting_decimals <= UI_max_number_of_decimals:
        items_group_1.append(element)
    else:
        items_group_2.append(element)

# 3️⃣OVERRIDING THE ELEMENTS
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
