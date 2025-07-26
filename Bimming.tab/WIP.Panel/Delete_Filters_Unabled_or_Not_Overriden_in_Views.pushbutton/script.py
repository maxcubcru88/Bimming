# -*- coding: utf-8 -*-
__title__ = "Remove Not USed\nFilters"
__doc__ = """Description:
Delete_Filters_Unabled_or_Not_Overriden_in_Views.pushbutton

Author: Máximo Cubero"""

# IMPORTS
#==================================================
# Regular + Autodesk
from Autodesk.Revit.DB import *

# pyRevit
from pyrevit import revit, forms

# VARIABLES
#==================================================
doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app   = __revit__.Application

# MAIN
#==================================================

views_with_VT, views_with_no_VT = [], [] # views WITH and WITHOUT view templates

# Get the active view
view = doc.ActiveView

default_ogs = OverrideGraphicSettings()
filter_ids = view.GetFilters()

for fid in filter_ids:
    filter_elem = doc.GetElement(fid)
    overrides = view.GetFilterOverrides(fid)

    print("Filter: {}".format(filter_elem.Name))
    print(" - Enable Filter: {}".format(view.GetIsFilterEnabled(fid)))
    print(" - Visible: {}".format(view.GetFilterVisibility(fid)))
    print(" - Halftone: {}".format(overrides.Halftone))
    print(" - Transparency: {}".format(overrides.Transparency))

    # PROJECTION LINE OVERRIDES
    try:
        color = overrides.ProjectionLineColor
        color.Red
        print(" - Projection Line Color overridden: ({}, {}, {})".format(color.Red, color.Green, color.Blue))
    except:
        pass
    if overrides.ProjectionLineWeight != default_ogs.ProjectionLineWeight:
        print(" - Projection Line Weight overridden: {}".format(overrides.ProjectionLineWeight))
    if overrides.ProjectionLinePatternId != default_ogs.ProjectionLinePatternId:
        pattern = doc.GetElement(overrides.ProjectionLinePatternId)
        print(" - Projection Line Pattern overridden: {}".format(pattern.Name if pattern else "None"))

    # SURFACE PATTERN OVERRIDES
    if overrides.SurfaceForegroundPatternId != default_ogs.SurfaceForegroundPatternId:
        pattern = doc.GetElement(overrides.SurfaceForegroundPatternId)
        print(" - Surface Foreground Pattern overridden: {}".format(pattern.Name if pattern else "None"))
    try:
        color = overrides.SurfaceForegroundPatternColor
        color.Red
        print(" - Projection Line Color overridden: ({}, {}, {})".format(color.Red, color.Green, color.Blue))
    except:
        pass
    if overrides.SurfaceBackgroundPatternId != default_ogs.SurfaceBackgroundPatternId:
        pattern = doc.GetElement(overrides.SurfaceBackgroundPatternId)
        print(" - Surface Background Pattern overridden: {}".format(pattern.Name if pattern else "None"))
    try:
        color = overrides.SurfaceBackgroundPatternColor
        color.Red
        print(" - Projection Line Color overridden: ({}, {}, {})".format(color.Red, color.Green, color.Blue))
    except:
        pass

    # CUT LINE OVERRIDES
    try:
        color = overrides.CutLineColor
        color.Red
        print(" - Projection Line Color overridden: ({}, {}, {})".format(color.Red, color.Green, color.Blue))
    except:
        pass
    if overrides.CutLineWeight != default_ogs.CutLineWeight:
        print(" - Cut Line Weight overridden: {}".format(overrides.CutLineWeight))
    if overrides.CutLinePatternId != default_ogs.CutLinePatternId:
        pattern = doc.GetElement(overrides.CutLinePatternId)
        print(" - Cut Line Pattern overridden: {}".format(pattern.Name if pattern else "None"))

    print("-" * 40)


# __beta__ = False
# forms.inform_wip()