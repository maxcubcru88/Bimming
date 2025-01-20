# -*- coding: utf-8 -*-
__title__   = "Set Angle\nRotation"
__doc__     = """Sets the rotation of the scope box relative to the X-axis.

Author: Maximo Cubero"""

# IMPORTS
#==================================================
from Autodesk.Revit.DB import *
from pyrevit import revit, forms
import math
import clr
clr.AddReference('System')

# VARIABLES
#==================================================
app    = __revit__.Application
uidoc  = __revit__.ActiveUIDocument
doc    = __revit__.ActiveUIDocument.Document #type:Document

# MAIN
#==================================================
class MyOption(forms.TemplateListItem):
    def __init__(self, item, el_name, angle, checked=False):
        self.item = item #Id of the element
        self.el_name = el_name
        self.angle = angle
        self.checked = checked

    @property
    def name(self):
        el_id = str(self.item)
        return "Angle: {}  |  Name: {}".format(self.angle, self.el_name)

# Define a function to check if a vector is parallel to the Z-axis
def is_parallel_to_z(vector):
    # Z-axis vector
    z_axis = XYZ.BasisZ

    # Calculate the dot product between the input vector and Z-axis vector
    dot_product = vector.DotProduct(z_axis)

    # Check if the dot product is close to 1 or -1
    if abs(dot_product) > 0.9999:
        return True
    else:
        return False

def get_angles_against_x(vectors):
    angles = []

    # X-axis vector
    x_axis = XYZ.BasisY

    for vector in vectors:
        # Calculate the angle between the vector and X-axis
        angle = vector.AngleTo(x_axis)

        # Convert angle from radians to degrees
        angle_degrees = math.degrees(angle)

        angles.append(angle_degrees)

    return angles

def get_scope_box_angle(scope_box):
    options = Options()
    options.DetailLevel = ViewDetailLevel.Undefined

    geom = scope_box.Geometry[options]

    direction = []
    for line in geom:
        vector = line.Direction
        if not (is_parallel_to_z(vector)):
            direction.append(vector)

    scope_box_angle = get_angles_against_x(direction)[4]
    return scope_box_angle

# Function to rotate scope box
def rotate_scope_box(scope_box, angle_degrees):

    # Get the bounding box of the scope box
    bounding_box = scope_box.get_BoundingBox(doc.ActiveView)

    # Calculate the center point of the bounding box
    center_point = (bounding_box.Min + bounding_box.Max) / 2.0

    # Create a rotation axis
    axis = Line.CreateBound(center_point, XYZ(center_point.X, center_point.Y, center_point.Z + 1))

    # Convert angle from degrees to radians
    angle_radians = math.radians(angle_degrees)

    # Rotate the scope box
    ElementTransformUtils.RotateElement(doc, scope_box.Id, axis, angle_radians)

#1️⃣ Select Scope Boxes
scope_boxes = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_VolumeOfInterest).WhereElementIsNotElementType().ToElements()
scope_boxes_sorted = sorted(scope_boxes, key=lambda sb: get_scope_box_angle(sb))
scope_boxes_ids = [sb.Id for sb in scope_boxes]

if not scope_boxes:
    forms.alert("There are not any scope box in the model.", warn_icon=False, exitscript=True)

# Get Scope Boxes - Selected in the model
sel_el_ids          = uidoc.Selection.GetElementIds()
sel_elem            = [doc.GetElement(e_id) for e_id in sel_el_ids]
sel_elem_ids = [el.Id for el in sel_elem if el.Id in scope_boxes_ids]

#2️⃣ WPF Form to select scope boxes
scope_box_list = []
for sb in scope_boxes_sorted:
    scope_box_id = sb.Id
    scope_box_name = sb.Name
    scope_box_angle = get_scope_box_angle(sb)
    if sb.Id in sel_elem_ids:
        scope_box_checked = True
    else:
        scope_box_checked = False
    option = MyOption(scope_box_id, scope_box_name, scope_box_angle, scope_box_checked)
    scope_box_list.append(option)

res = forms.SelectFromList.show(scope_box_list, title='Scope Boxes List', multiselect=True, button_name='Set Angle')

#3️⃣ WPF Form to set the angle if any scope box is selected
if res:
    UI_angle = forms.ask_for_string(            # User Input (UI)
        default='30.0',
        prompt='Enter an angle: [degrees]',
        title='Scope Boxes - Set Angle')
    try:
        UI_angle_float = float(UI_angle.replace(',', '.'))
    except:
        forms.alert("Please enter a number and press 'OK'.\n\nSeparate the decimals with a ',' or '.'\n\ne.g. 30.5 or 30,5", exitscript=True)
else:
    forms.alert("No Scope Boxes selected. Try again.", exitscript=True)

# 4️⃣ Rotate the specified angle the scope box selected

t = Transaction(doc, 'Bimming-Rotate Scope Boxes')
t.Start()

scope_box_selected = [doc.GetElement(sb) for sb in res]

for scope_box in scope_box_selected:
    try:
        scope_box.Pinned = False
        scope_box_angle = get_scope_box_angle(scope_box)
        angle_to_be_rotated = UI_angle_float - scope_box_angle
        rotate_scope_box(scope_box, angle_to_be_rotated)
        scope_box.Pinned = True
    except:
        print("There was a problem rotating scope box: {}\nTry again.".format(scope_box.Name))

t.Commit()