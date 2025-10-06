# -*- coding: utf-8 -*-
__title__ = "Select\nCameras"
__doc__ = """Select cameras in Revit. This is especially useful when moving multiple 3D views at once. The crop view must be active in the 3D view.

Author: Máximo Cubero"""

__min_revit_ver__ = 2021
__max_revit_ver__ = 2025

# CONSTANTS
#==================================================
TRANSACTION_NAME = "Bimming-Select Cameras"
ALERT_NO_VIEWS = "No Views Selected. Please Try Again"
ALERT_NO_RULES = "Rules to rename have not been defined. Please Try Again"

# IMPORTS
#==================================================
from Autodesk.Revit.DB import *
from pyrevit import forms
from rpw.ui.forms import (FlexForm, Label, TextBox, Separator, Button)

from System.Collections.Generic import List
# VARIABLES
#==================================================
doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

# MAIN
#==================================================

from Autodesk.Revit.UI import TaskDialog

# 1️⃣Select Views
# Get Views Selected in the projectBrowser
sel_el_ids  = uidoc.Selection.GetElementIds()
sel_elem    = [doc.GetElement(e_id) for e_id in sel_el_ids]
sel_views   = [el for el in sel_elem if isinstance(el, View) and isinstance(el, View3D)]

# If None Selected - Prompt SelectViews from pyrevit.forms.select_views()
if not sel_views:
    sel_views = forms.select_views(title='Select 3D View', filterfunc=lambda v: isinstance(v, View3D))

if not sel_views:
    forms.alert(ALERT_NO_VIEWS, exitscript=True)

# 2️⃣Select Views/Cameras
# Create a .NET list of ElementIds
element_ids = List[ElementId]()
for view in sel_views:
    crop_view_id = ElementId(view.Id.IntegerValue - 2)
    element_ids.Add(crop_view_id)

# Select it in the Revit UI
uidoc.Selection.SetElementIds(element_ids)
