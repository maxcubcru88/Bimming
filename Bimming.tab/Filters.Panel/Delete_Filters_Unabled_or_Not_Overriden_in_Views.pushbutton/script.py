# -*- coding: utf-8 -*-
__title__ = "Clean Up\nFlts in Views"
__doc__ = """Finds filters in views that are either disabled or not overriding graphics.

Author: Máximo Cubero"""

# CONSTANTS
#==================================================
TRANSACTION_NAME = "Bimming-Clean Up Filters in Views"

# IMPORTS
#==================================================
# Regular + Autodesk
from Autodesk.Revit.DB import *

# pyRevit
from pyrevit import revit, forms

import clr
clr.AddReference('System')
import System
from System.Collections.Generic import List
from Snippets._bimming_views import *
from Snippets._bimming_inspect import *
from Snippets._bimming_groups import *
from Snippets._bimming_collect import *
from Snippets._bimming_export import *
from Snippets._bimming_functions import *
import sys

# VARIABLES
#==================================================
doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app   = __revit__.Application

# FUNCTIONS
#==================================================

def filters_is_overidden(view, filter_id):
    aux = []

    overrides = view.GetFilterOverrides(filter_id)

    ########################################### VISIBILITY ###########################################

    is_visible = view.GetFilterVisibility(filter_id)
    aux.append(not(is_visible))

    ########################################### PROJECTION OVERRIDES ###########################################
    # LINE
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

    # PATTERN
    # Projection Patterns Foreground Visible
    aux.append(not (overrides.IsSurfaceForegroundPatternVisible))

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
    aux.append(not (overrides.IsSurfaceBackgroundPatternVisible))

    # Projection Patterns - Background Pattern
    projection_background_pattern = doc.GetElement(overrides.SurfaceBackgroundPatternId)
    aux.append(projection_foreground_pattern.Name if projection_foreground_pattern else None)

    # Projection Patterns - Background Color
    try:
        color = overrides.SurfaceBackgroundPatternColor
        aux.append([color.Red, color.Green, color.Blue])
    except:
        aux.append(None)

    #TRANSPARENCY
    # Projection Transparency
    projection_transparency = overrides.Transparency
    aux.append(projection_transparency)

    ########################################### CUT OVERRIDES ###########################################
    # LINE
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

    # PATTERN
    # Cut Patterns Foreground Visible
    aux.append(not (overrides.IsCutForegroundPatternVisible))

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
    aux.append(not (overrides.IsCutBackgroundPatternVisible))

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

    return any(aux)

# MAIN
#==================================================

# 1️⃣COLLECT ALL VIEWS IN THE MODEL

views = FilteredElementCollector(doc).OfClass(View).WhereElementIsNotElementType().ToElements()

ok, errors = [], []
views_to_check = []
elements_to_delete = []
info_report = [['View Name', 'View Type', 'Filter Name', 'Description']]

# 2️⃣IDENTIFY VIEWS TO CHECK

for view in views:
    try:
        filter_ids = view.GetFilters()

        if view.IsTemplate:
            views_to_check.append(view)

        elif view.ViewTemplateId == ElementId(-1):
            views_to_check.append(view)

        else:
            # 1. Parameter to check
            param_id_to_check = ElementId(BuiltInParameter.VIS_GRAPHICS_FILTERS)

            # 2. Get the list of non-controlled parameters
            view_template = doc.GetElement(view.ViewTemplateId)
            non_controlled_param_ids = view_template.GetNonControlledTemplateParameterIds()

            # 3. Check if the parameter is NOT in the non_controlled_param_ids list
            is_included = param_id_to_check not in non_controlled_param_ids

            if not is_included:
                views_to_check.append(view)
    except:
        pass
        # print(view.Name)

# 3️⃣CHECK FILTERS IN EACH VIEW

for v in views_to_check:
    # print([v.IsTemplate, type(v),v.Name])
    if v.IsTemplate:
         view_type = "View Template"
    else:
         try: view_type = doc.GetElement(v.GetTypeId()).FamilyName
         except: view_type = "Unknown"
    filter_ids = v.GetFilters()
    # print(filter_ids)

    for filter_id in filter_ids:
        is_enabled = v.GetIsFilterEnabled(filter_id)
        filter_elem = doc.GetElement(filter_id)
        filter_elem_name = filter_elem.Name
        # print("NAME: {}".format(filter_elem_name))
        # print("ENABLE: {}".format(str(is_enabled)))
        # print("OVERRIDEN: {}".format(str(filters_is_overidden(v, filter_id))))
        # print("############################")
        if not is_enabled:
            info_report.append([v.Name, view_type, filter_elem_name, "The filter is not enabled."])
            elements_to_delete.append((v, filter_id))
            continue
        elif is_enabled and not filters_is_overidden(v, filter_id):
            info_report.append([v.Name, view_type, filter_elem_name, "The filter is not overriding the graphics."])
            elements_to_delete.append((v, filter_id))
            continue
        else:
            pass

# 4️⃣EXIT EARLY IF ANYTHING TO CLEAN

if not elements_to_delete:
    forms.alert('There are no filters to clean up. Good job!', warn_icon=False, exitscript=True)
    sys.exit()

# 5️⃣USER DECISION

# OPTIONS:
option_1 = "Delete the filters and save an Excel Report"
option_2 = "Don't delete the filters and save an Excel Report"
option_3 = "Exit. Thanks for the information"

# If there are elements to be deleted, decide what to do
res = forms.alert("{} filters can be deleted. How would you like to proceed?".format(len(info_report)),
                  options=[option_1,
                           option_2,
                           option_3],
                  warn_icon = False)

# Actions based of the decision
if res == option_1 or res == option_2:

    project_info = get_project_info(doc, app)

    directory = create_report_directory('Bimming_Filters_Clean_Up')

    dic = list_to_dict(project_info)
    file_name = dic['File Name']
    report_name = generate_report_name(file_name)

    # Export the report
    # Create the full file path with the .csv extension
    csv_file_path = os.path.join(directory, report_name[0] + ".csv")
    data = project_info + info_report
    export_to_csv(csv_file_path, data)

if res == option_1:
    with Transaction(doc, TRANSACTION_NAME) as t:
        t.Start()
        for element in elements_to_delete:
            try:
                print(element)
                element[0].RemoveFilter(element[1])
            except: pass #problems_to_delete.append(element_id)
        t.Commit()  # Commit the transaction

    message = '{} Elements have been deleted'.format(len(info_report))
    forms.alert(message,'title', warn_icon=False)