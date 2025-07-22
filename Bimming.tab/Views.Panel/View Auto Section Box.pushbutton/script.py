# -*- coding: utf-8 -*-
__title__   = "View Auto\nSection Box"
__doc__     = """Adjusts the section box of a 3D view to match the crop region of the active 2D view (Section, Elevation, Plan, or Callout).  

Shift+Click: Opens a menu to select a specific 3D view and apply a view template.  

Author: Maximo Cubero"""

__min_revit_ver__ = 2021
__max_revit_ver__ = 2025

import sys

# CONSTANTS
#==================================================
TRANSACTION_NAME = "Bimming-View Auto Section Box"

# IMPORTS
#==================================================
import clr
from traceback import print_tb
clr.AddReference('System')
from pyrevit import EXEC_PARAMS
import Autodesk.Revit.DB as DB
from Snippets._bimming_views import *
from Snippets._bimming_functions import *
from Snippets._bimming_vectors import *
from Snippets._bimming_transform import *
from Snippets._bimming_convert import *

# VARIABLES
#==================================================
app    = __revit__.Application
uidoc  = __revit__.ActiveUIDocument
doc    = __revit__.ActiveUIDocument.Document #type:Document

# MAIN
#==================================================
# 1️⃣CHECK THAT THE ACTIVE VIEW IS VALID
active_view = doc.ActiveView

if active_view.ViewType not in [ViewType.Section, ViewType.Elevation, ViewType.Detail, ViewType.AreaPlan, ViewType.FloorPlan]:
    forms.alert(msg='The active view "{}" is not valid. Select a plan, section, elevation, or callout view.'.format(active_view.ViewType), exitscript = True)

if not active_view.CropBoxActive:
    forms.alert(msg='The crop of the view must be active. Activate it, adjust it, and execute it again.\n\n'
                    'View Type: {}\n'
                    'View Name: {}'.format(active_view.ViewType, active_view.Name), exitscript = True)

crop_box = active_view.CropBox #Returns a bounding box

# 2️⃣BOUNDING BOX FOR SECTIONS, ELEVATIONS, AND DETAIL CALLOUTS HAS TO BE ADJUSTED - They are point down, and they have to be rotated.
if active_view.ViewType in [ViewType.Section, ViewType.Elevation]:
    angle_to_rotate_bounding_box = 90
elif active_view.ViewType in [ViewType.AreaPlan, ViewType.FloorPlan, ViewType.Detail]:
    angle_to_rotate_bounding_box = 0
# Rotate the bounding box
new_box = rotate_bounding_box(crop_box,XYZ(0,0,0),XYZ(1,0,0),angle_to_rotate_bounding_box)

# And for Plan Views, the depth has to be adjusted from the view range planes
if active_view.ViewType in [ViewType.AreaPlan, ViewType.FloorPlan]:
    dic_view_range = get_view_range_points(active_view)
    cut_plane = dic_view_range['CutPlane'].Z
    view_depth = dic_view_range['ViewDepthPlane']
    if view_depth:  view_depth = view_depth.Z
    else:           view_depth = convert_internal_units(-2000) # This is in case that is view depth is set to Unlimited
    new_box = adjust_bounding_box_z(new_box,new_min_z=view_depth, new_max_z=cut_plane)

# 3️⃣SELECTING THE 3D VIEW WE WANT TO USE

if EXEC_PARAMS.config_mode: #if SHIFT-Click
    ThreeD_view = forms.select_views(
        title='Select 3D Views',
        filterfunc=lambda x: x.ViewType == DB.ViewType.ThreeD)
    if ThreeD_view: ThreeD_view = ThreeD_view[0]
    else: sys.exit()
else:
    view_name = 'Bimming - Auto Section Box'
    if get_3d_view_by_name(doc, view_name):
        ThreeD_view = get_3d_view_by_name(doc, view_name)
    else:
        # Get a default 3D ViewFamilyType to duplicate
        default_threeD_view_family_type_id = doc.GetDefaultElementTypeId(ElementTypeGroup.ViewType3D)
        default_threeD_view_family_type = doc.GetElement(default_threeD_view_family_type_id)
        # Create 3D View
        with DB.Transaction(doc, "Bimming-Create 3D View") as t:
            t.Start() #🔓
            ThreeD_view = View3D.CreateIsometric(doc, default_threeD_view_family_type.Id)
            # Rename 3D View
            ThreeD_view.Name = view_name
            # Set Detail Level to Fine
            ThreeD_view.DetailLevel = ViewDetailLevel.Fine
            t.Commit() #🔒

# 4️⃣ASSIGNING THE BOUNDING BOX TO THE 3D VIEW
t =  DB.Transaction(doc, TRANSACTION_NAME)
t.Start() #🔓
section_box = ThreeD_view.SetSectionBox(new_box)

# 5️⃣SELECTING AND TRANSFORMING (MOVE AND ROTATE) THE SECTION BOX
# SELECT
section_box_element = get_section_box(doc, ThreeD_view)[0]

# ROTATE
if active_view.ViewType in [ViewType.Section, ViewType.Elevation]:
    angle_to_rotate = angle_with_y_axis(doc.ActiveView.ViewDirection.Negate())
elif active_view.ViewType in [ViewType.AreaPlan, ViewType.FloorPlan]:
    angle_to_rotate = get_plan_view_rotation(active_view)
elif active_view.ViewType in [ViewType.Detail]:
    angle_to_rotate = get_detail_view_rotation(active_view)
rotate_element(doc, section_box_element, XYZ(0, 0, 0), XYZ(0, 0, 1), angle_to_rotate)

# MOVE
origin = active_view.Origin
if active_view.ViewType in [ViewType.Section, ViewType.Elevation, ViewType.Detail]:
    move_element(doc, section_box_element, XYZ(0,0,0), origin)
elif active_view.ViewType in [ViewType.AreaPlan, ViewType.FloorPlan]:
    move_element_xy(doc, section_box_element, XYZ(0,0,0), origin)
t.Commit() #🔒

# 6️⃣SETTING THE ORIENTATION OF THE 2D VIEW TO THE 3D VIEW
view_direction = active_view.ViewDirection  # Forward direction (typically Z)
up_direction = active_view.UpDirection      # Up direction (typically Y)
orientation = DB.ViewOrientation3D(origin, up_direction, view_direction.Negate())
ThreeD_view.SetOrientation(orientation)

# 7️⃣OPENING THE 3D VIEW
open_3d_view_by_id(doc, uidoc, view_id=ThreeD_view.Id)