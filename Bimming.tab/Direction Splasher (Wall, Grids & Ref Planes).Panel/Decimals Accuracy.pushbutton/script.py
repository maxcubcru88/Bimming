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

# 👆WPF Form to set the number of decimals to be checked

UI_angle = forms.ask_for_string(            # User Input (UI)
    default='2',
    prompt='Enter the maximum number of decimal places (0-12):',
    title='Splash!')

# Check that the input is correct
warning_message = "Please enter an integer between 0 and 12, then press 'Splash!'.\ne.g., '2' or '3'"

# Check that the input is a integer
try: UI_max_number_of_decimals = int(UI_angle)
except: forms.alert(warning_message, exitscript=True)

# Check that the integer is between 0 and 12
if UI_max_number_of_decimals in list(range(0, 13)): pass# list [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
else: forms.alert(warning_message, exitscript=True)

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
    angle_to_X  = get_angle_to_vector(direction, vector_X)[0]
    # print ('Angle to Axis X: {}'.format(angle_to_X))

    number_of_decimals = count_decimals_string(angle_to_X)
    # print ('Number of decimals: {}'.format(number_of_decimals))

    if  number_of_decimals <= UI_max_number_of_decimals:
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
