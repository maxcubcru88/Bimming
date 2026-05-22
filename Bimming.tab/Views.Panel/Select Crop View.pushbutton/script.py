# -*- coding: utf-8 -*-
__title__ = "Select\nCrop Views"
__doc__ = """Selects the physical Crop Box elements of Section and Elevation views.

This is especially useful when you need to move, rotate, or modify multiple view crop boundaries simultaneously. To be listed, the view must have both its crop box active and its crop boundary visible.

Author: Máximo Cubero"""

__min_revit_ver__ = 2021
__max_revit_ver__ = 2026

# CONSTANTS
#==================================================
TRANSACTION_NAME = "Bimming-Select Cameras"
ALERT_NO_VIEWS = "No Views Selected. Please Try Again"
ALERT_NO_RULES = "Rules to rename have not been defined. Please Try Again"

# IMPORTS
#==================================================
from pyrevit import forms
from Autodesk.Revit.DB import *
from System.Collections.Generic import List

from System.Collections.Generic import List
# VARIABLES
#==================================================
doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

# Filter: Must be an Active/Visible crop box AND either a Section or an Elevation view
allowed_types = [ViewType.Section, ViewType.Elevation]

sel_views = forms.select_views(
    title='Select Sections or Elevations',
    filterfunc=lambda v: v.CropBoxActive
                         and v.CropBoxVisible
                         and v.ViewType in allowed_types
)

if not sel_views:
    forms.alert("No views selected.", exitscript=True)

# 2️⃣ Select Views/Cameras
element_ids = List[ElementId]()

for view in sel_views:
    # Find the Crop Box element belonging to this specific view
    crop_box_collector = FilteredElementCollector(doc, view.Id) \
        .OfCategory(BuiltInCategory.OST_Viewers) \
        .ToElements()

    # Filter so we ONLY grab the viewer that belongs to this view
    for crop_box in crop_box_collector:
        if crop_box.Name == view.Name:
            element_ids.Add(crop_box.Id)
            break

# Select it in the Revit UI
if element_ids.Count > 0:
    uidoc.Selection.SetElementIds(element_ids)
else:
    forms.alert("No active crop boxes found for the selected views.")