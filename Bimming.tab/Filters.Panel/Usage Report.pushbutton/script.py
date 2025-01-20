# -*- coding: utf-8 -*-
__title__ = "Usage\nReport"
__doc__ = """Exports a .csv report listing the filters currently in use.

TIP: Use the 'Power BI Template' command to download the template and link the .csv file, allowing you to track where filters are applied in your project.

Author: Máximo Cubero"""

import sys

# IMPORTS
#==================================================
from Autodesk.Revit.DB import *
from System.Collections.Generic import List
import csv
import codecs
import os
import datetime
from pyrevit import forms

# VARIABLES
#==================================================
doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app   = __revit__.Application

# MAIN
#==================================================

# ADD PROJECT INFO
# Current file name: Project1.rvt
# Project Name: Project Name
# Project Number: Project Number
# Client Name: Owner

# ADD SCRIP INFO:
# Date of execution: DDMMYYYY HH:MM:SS
# Execution Time: 29 seconds


def export_to_csv(file_path, data):
    # Open the file with codecs and utf-8 encoding
    with codecs.open(file_path, 'w', 'utf-8') as file:
        writer = csv.writer(file, lineterminator='\n')
        writer.writerows(data)
    return  file_path
    # print("Data exported to: " + file_path)

def GetFilterIds(view):
    filterIds = None
    try:
        filterIds = view.GetFilters()
    except Exception as e:
        #print("Error collecting filters in view: {}".format(view), e)
        filterIds = None
    return filterIds

def GetUsedFilterIds(doc):
    views = FilteredElementCollector(doc).OfClass(View).ToElements()
    usedFilterIds = List[ElementId]()
    for view in views:
        viewFilterIds = []
        try:
            viewFilterIds = view.GetFilters()
            for filter in viewFilterIds:
                usedFilterIds.Add(filter)
        except:
            pass  # this exception happens when a view doesn't support filters
    return usedFilterIds

def GetUnusedFilters(doc):
    usedFilterIds = GetUsedFilterIds(doc)
    unusedFilters = FilteredElementCollector(doc).OfClass(ParameterFilterElement).Excluding(usedFilterIds).ToElements()
    return list(unusedFilters)

# 🫷Check if the model is saved
# Get the model path (supports both local and central models)
model_path = doc.PathName
if model_path == "":
    forms.alert('Model has not been saved yet.\nSave the model and try again.')
    sys.exit()

# 1️⃣Get filter information to be exported

filters_used   = GetUsedFilterIds(doc)
filters_unused = GetUnusedFilters(doc)

output_filters, output_views = [], []
output_data = [["DATA"], ["Filter Id", "Filter Name", "Filter Enable", "Filter Visibility", "View Type", "View Name", "Is View Template", "View Template Name Applied", "Sheet Info"]]

views = FilteredElementCollector(doc).OfClass(View).ToElements()

for v in views:

    sheetInfo = v.get_Parameter(BuiltInParameter.VIEW_SHEET_VIEWPORT_INFO).AsString()
    if sheetInfo:
        sheetInfo = sheetInfo
    else:
        sheetInfo = "Not in sheet"

    if v.IsTemplate:
        vType = "View Template"
        vTemplate = "N/A"
    else:
        vType = v.ViewType
        vTemplateFam = doc.GetElement(v.get_Parameter(BuiltInParameter.VIEW_TEMPLATE).AsElementId())
        try:
            vTemplate = vTemplateFam.Name
        except:
            vTemplate = "Not View Template Assigned"

    filters_in_view = GetFilterIds(v)

    if filters_in_view:
        for f in filters_in_view:
            aux = []

            aux.append(f.IntegerValue)              # Filter Id
            aux.append(doc.GetElement(f).Name)      # Filter Name <string>
            aux.append(v.GetIsFilterEnabled(f))     # Filter Enable <True/False>
            aux.append(v.GetFilterVisibility(f))    # Filter Visibility <True/False>
            aux.append(str(vType))                  # View Type <string>
            aux.append(v.Name)                      # View Name
            aux.append(v.IsTemplate)                # IsViewTemplate <True/False>
            aux.append(vTemplate)                   # Name of the view template assigned to the view <string>
            aux.append(sheetInfo)                   # Sheet Info <string>


            output_data.append(aux)


# 2️⃣PROJECT INFO

output_project_info = [["PROJECT INFO"]]

output_project_info.append(("File Path", model_path))
#print("File Path: " + model_path)

# Extract the file name without the extension
file_name = os.path.splitext(os.path.basename(model_path))[0]
output_project_info.append(("File Name", file_name))
#print("File Name: " + file_name)

# Check if the document is workshared
if doc.IsWorkshared:
    try:
        # Get the central file path
        # Extract basic file info, including the central path
        file_info = BasicFileInfo.Extract(model_path)

        # Retrieve the central model path
        central_path = file_info.CentralPath
        if central_path:
            central_path = central_path
            #print("Central File Path: " + central_path)
        else:
            central_path = "File hasn't been saved as a central model yet."
            #print("Central File Path: " + central_path)
    except Exception as e:
        central_path = "Error extracting central file path: {}".format(e)
else:
    central_path = "This document is not workshared."
    #print("Central File Path: " + central_path)

output_project_info.append(("Central File Path", central_path))
#print(output_project_info)

# Get the current user's name
user_name = app.Username
output_project_info.append(("Export by", user_name))
#print("Export by: " + user_name)



# 2️⃣Create directory where the report will be saved

# Get the user's Documents directory
documents_folder = os.path.expanduser("~\\Documents\\Bimming_Filter_Usage_Reports")

# Check if the Bimming folder exists, if not, create it
if not os.path.exists(documents_folder):
    os.makedirs(documents_folder)

# print("Reports will be saved in:", documents_folder)

# Open the folder in File Explorer
os.startfile(documents_folder)


# 3️⃣Name of the report: File Name + Date + Time

# Get the current date and time
now = datetime.datetime.now()

# Format the date and time as 'YYYY-MM-DD_HH.MM.SS'
formatted_datetime = now.strftime("%Y-%m-%d_%H.%M.%S")
output_project_info.append((("Export Date", now.strftime("%Y-%m-%d"))))
output_project_info.append((("Export Time", now.strftime("%H:%M:%S"))))


# Concatenate the file name with the formatted date and time
new_file_name = "{}_{}".format(file_name, formatted_datetime)

# Print the result
# print("Concatenated File Name:", new_file_name)

# 4️⃣Export the report

# Create the full file path with the .csv extension
csv_file_path = os.path.join(documents_folder, new_file_name + ".csv")
# print(csv_file_path)

output = output_project_info + output_data
export_to_csv(csv_file_path, output)


