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

info = [["Filter Name",
         "Enable Filter",
         "Visibility",
         "Projection Line Pattern",
         "Projection Line Color",
         "Projection Line Weight",
         "Projection Patterns Foreground Visible",
         "Projection Patterns Foreground Pattern",
         "Projection Patterns Foreground Color",
         "Projection Patterns Background Visible",
         "Projection Patterns Background Pattern",
         "Projection Patterns Background Color",
         "Projection Transparency",
         "Cut Line Pattern",
         "Cut Line Color",
         "Cut Line Weight",
         "Cut Patterns Foreground Visible",
         "Cut Patterns Foreground Pattern",
         "Cut Patterns Foreground Color",
         "Cut Patterns Background Visible",
         "Cut Patterns Background Pattern",
         "Cut Patterns Background Color",
         "Halftone",
         ]]

# Get the active view
view = doc.ActiveView

default_ogs = OverrideGraphicSettings()
filter_ids = view.GetFilters()



for filter_id in filter_ids:

    aux = []

    filter_elem = doc.GetElement(filter_id)
    aux.append(filter_elem.Name)

    overrides = view.GetFilterOverrides(filter_id)

    ########################################### ENABLE FILTER AND VISIBILITY ###########################################

    is_enabled = view.GetIsFilterEnabled(filter_id)
    aux.append(is_enabled)

    is_visible = view.GetFilterVisibility(filter_id)
    aux.append(is_visible)

    ########################################### PROJECTION OVERRIDES ###########################################

    # Projection Line Pattern
    projection_line_pattern = doc.GetElement(overrides.ProjectionLinePatternId)
    aux.append(projection_line_pattern.Name if projection_line_pattern else None)

    # Projection Line Color
    try:
        color = overrides.ProjectionLineColor
        aux.append([color.Red, color.Green, color.Blue])
    except:
        aux.append(None)

    # Projection Line Weight
    weight = overrides.ProjectionLineWeight
    aux.append(None if weight == -1 else weight)

    # Projection Patterns Foreground Visible
    aux.append(overrides.IsSurfaceForegroundPatternVisible)

    # Projection Patterns - Foreground Pattern
    projection_foreground_pattern = doc.GetElement(overrides.SurfaceForegroundPatternId)
    aux.append(projection_foreground_pattern.Name if projection_foreground_pattern else None)

    # Projection Patterns - Foreground Color
    try:
        color = overrides.SurfaceForegroundPatternColor
        aux.append([color.Red, color.Green, color.Blue])
    except:
        aux.append(None)

    # Projection Patterns Background Visible
    aux.append(overrides.IsSurfaceBackgroundPatternVisible)


    # Projection Patterns - Background Pattern
    projection_background_pattern = doc.GetElement(overrides.SurfaceBackgroundPatternId)
    aux.append(projection_foreground_pattern.Name if projection_foreground_pattern else None)

    # Projection Patterns - Background Color
    try:
        color = overrides.SurfaceBackgroundPatternColor
        aux.append([color.Red, color.Green, color.Blue])
    except:
        aux.append(None)

    # Projection Transparency
    projection_transparency = overrides.Transparency
    aux.append(projection_transparency)

    ########################################### CUT OVERRIDES ###########################################

    # Cut Line Pattern
    Cut_line_pattern = doc.GetElement(overrides.CutLinePatternId)
    aux.append(Cut_line_pattern.Name if Cut_line_pattern else None)

    # Cut Line Color
    try:
        color = overrides.CutLineColor
        aux.append([color.Red, color.Green, color.Blue])
    except:
        aux.append(None)

    # Cut Line Weight
    weight = overrides.CutLineWeight
    aux.append(None if weight == -1 else weight)

    # Cut Patterns Foreground Visible
    aux.append(overrides.IsCutForegroundPatternVisible)

    # Cut Patterns - Foreground Pattern
    Cut_foreground_pattern = doc.GetElement(overrides.CutForegroundPatternId)
    aux.append(Cut_foreground_pattern.Name if Cut_foreground_pattern else None)

    # Cut Patterns - Foreground Color
    try:
        color = overrides.CutForegroundPatternColor
        aux.append([color.Red, color.Green, color.Blue])
    except:
        aux.append(None)

    # Cut Patterns Background Visible
    aux.append(overrides.IsCutBackgroundPatternVisible)

    # Cut Patterns - Background Pattern
    Cut_background_pattern = doc.GetElement(overrides.CutBackgroundPatternId)
    aux.append(Cut_foreground_pattern.Name if Cut_foreground_pattern else None)

    # Cut Patterns - Background Color
    try:
        color = overrides.CutBackgroundPatternColor
        aux.append([color.Red, color.Green, color.Blue])
    except:
        aux.append(None)


    ########################################### HALTONE ###########################################

    is_halftone = overrides.Halftone
    aux.append(is_halftone)

    ###############################################################################################



    info.append(aux)

for e in info:
    print(e)

test = [True,None,False]

if any(test):
    print("TRUE")
else:
    print("FALSE")

print(test)

# __beta__ = False
# forms.inform_wip()