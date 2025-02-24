# -*- coding: utf-8 -*-
__title__ = "Read\nAngle"
__doc__ = """Retrieve the angle between a wall, reference plane, or grid line and the X-axis.

Author: Máximo Cubero"""

__min_revit_ver__ = 2021
__max_revit_ver__ = 2022

# IMPORTS
#==================================================
# Custom Libraries
from Snippets._bimming_vectors import *
from Snippets._bimming_selection import *
from Snippets._bimming_strings import crop_number_string
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

from Autodesk.Revit.UI.Selection import ISelectionFilter
from Autodesk.Revit.DB import BuiltInCategory, ElementId

class ISelectionFilter_Categories(ISelectionFilter):
    def __init__(self, allowed_categories):
        """ ISelectionFilter made to filter by categories.
        allowed_categories: list of BuiltInCategory """
        self.allowed_category_ids = [
            ElementId(bic) for bic in allowed_categories
        ]

    def AllowElement(self, element):
        """ Determines if the element is allowed. """
        if element.Category and element.Category.Id in self.allowed_category_ids:
            return True
        return False

    def AllowReference(self, reference, position):
        """ Determines if the reference is allowed. """
        return False  # Only elements are filtered in this case.

lst_dict = {}
for e in range(1,12):
    lst_dict[str(e) + ' decimals'] = e

number_of_decimals = forms.ask_for_one_item(
                                            sorted(lst_dict.keys(), key=lambda x: int(x.split()[0])),
                                                default='6 decimals',
                                                prompt='Select the number of decimals to round',
                                                title='Bimming-Read Angle'
                                            )
if not number_of_decimals:
    sys.exit()

decimals = lst_dict[number_of_decimals]

# 🫳Select Wall, Grid or Ref Planes

# Get Views - Selected in a projectBrowser
sel_el_ids      = uidoc.Selection.GetElementIds()
sel_elem        = [doc.GetElement(e_id) for e_id in sel_el_ids]
sel_elem_filter = [el for el in sel_elem if issubclass(type(el), Wall) or issubclass(type(el), Grid) or issubclass(type(el), ReferencePlane)]

if len(sel_elem_filter) != 1:
    with forms.WarningBar(title='Select Wall, Grid or Ref Plane:'):
        try:
            # Prompt user to select an element from allowed categories
            sel_elem_reference = uidoc.Selection.PickObject(
                ObjectType.Element,
                ISelectionFilter_Categories([
                    BuiltInCategory.OST_Walls,
                    BuiltInCategory.OST_Grids,
                    BuiltInCategory.OST_CLines
                ]),
                "Select an element from the allowed categories"
            )
            # Get the selected element's ID and the element itself
            sel_elem_id = sel_elem_reference.ElementId
            sel_elem = doc.GetElement(sel_elem_id)
        except Exception as e:
            forms.alert('No Elements Selected. Please Try Again', exitscript=True)

else:
    sel_elem = sel_elem_filter[0] # Selecting the only element in the list
    pass

# 🔥Calculating the angle

# 1️⃣Getting the direction of the element
direction = get_direction(sel_elem)
if direction == None:
    forms.alert('The element has not the attribute direction. Select a linear one.', exitscript=True)

# print("Original direction: {}".format(direction))

# 2️⃣ANGLE TO VECTOR X --> XYZ(1,0,0)
vector_X = XYZ(1,0,0)
angle_to_X = get_angle_to_vector(direction, vector_X, scaled_decimal(1, 11))
angle_to_X_rounded = get_angle_to_vector(direction, vector_X, scaled_decimal(1, decimals))

vector_Y = XYZ(0,1,0)
angle_to_Y = get_angle_to_vector(direction, vector_Y, scaled_decimal(1, 11))
angle_to_Y_rounded = get_angle_to_vector(direction, vector_Y, scaled_decimal(1, decimals))

forms.alert(
    "ANGLE TO X&Y AXIS ROUNDED TO {} DECIMALS:\n\n"
    "X AXIS - {} [Angle]\n"
    "X AXIS - {} [Supplementary Angle]\n\n"
    "Y AXIS - {} [Angle]\n"
    "Y AXIS - {} [Supplementary Angle]"
    .format(
            decimals,
            crop_number_string(angle_to_X_rounded[0], decimals),
            crop_number_string(angle_to_X_rounded[1], decimals),
            crop_number_string(angle_to_Y_rounded[0], decimals),
            crop_number_string(angle_to_Y_rounded[1], decimals)),
    sub_msg='See details to check the angles with all decimals (11)',
    expanded =  "X AXIS - {} [Angle]\n"
                "X AXIS - {} [Supplementary Angle]\n\n"
                "Y AXIS - {} [Angle]\n"
                "Y AXIS - {} [Supplementary Angle]"
    .format(crop_number_string(angle_to_X[0], 11),
            crop_number_string(angle_to_X[1],11),
            crop_number_string(angle_to_Y[0],11),
            crop_number_string(angle_to_Y[1],11)),
    warn_icon=False
)