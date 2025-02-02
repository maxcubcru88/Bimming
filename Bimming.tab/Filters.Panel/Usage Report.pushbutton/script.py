# -*- coding: utf-8 -*-
__title__ = "Usage\nReport"
__doc__ = """Exports a .csv report listing the filters currently in use.

TIP: Use the 'Power BI Template' command to download the template and link the .csv file, allowing you to track where filters are applied in your project.

Author: Máximo Cubero"""

#__helpurl__ = "https://www.bimming.uk"
__min_revit_ver__ = 2021
__max_revit_ver__ = 2025
#__context__ = 'zero-doc'
#__highlight__ = 'new'

# IMPORTS
#==================================================
from Autodesk.Revit.DB import *
from System.Collections.Generic import List
import csv
import codecs
import os
import datetime
from pyrevit import forms
import sys

# VARIABLES
#==================================================
doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app   = __revit__.Application

# MAIN
#==================================================

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

def remove_detached_suffix(s):
    if s.endswith('_detached'):
        return s[:-9]  # Remove the last 9 characters
    return s

# 🫷Check if the model is saved
# Get the model path (supports both local and central models)
model_path = doc.PathName
if model_path == "":
    forms.alert('Model has not been saved yet.\nSave the model and try again.')
    sys.exit()

# 1️⃣Get filter information to be exported

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

# Check if the document is workshared
if doc.IsWorkshared:
    try:
        # Get the central file path
        # Extract basic file info, including the central path
        file_info = BasicFileInfo.Extract(model_path)

        # Instead of getting the PathName which have the user appended, we get the CentralPath
        model_path = file_info.CentralPath

        # Extract the file name without the extension
        file_name = os.path.splitext(os.path.basename(model_path))[0]
        output_project_info.append(("File Name", file_name))
        # print("File Name: " + file_name)
        if file_name == "":
            forms.alert('Save the model and try again.')
            sys.exit()

        # Retrieve the central model path
        central_path = file_info.CentralPath
        # if central_path:
        #     central_path = central_path
        #     #print("Central File Path: " + central_path)
        # else:
        #     central_path = "File hasn't been saved as a central model yet."
        #     #print("Central File Path: " + central_path)
    except Exception as e:
        # We will have exceptions when we open a central file as detached
        # Extract the file name without the extension
        file_name_detached = os.path.splitext(os.path.basename(model_path))[0]
        file_name = remove_detached_suffix(file_name_detached)
        output_project_info.append(("File Name", file_name))
        # print("File Name: " + file_name)

        central_path = "It is a detached model - Not central file path found."
else:
    # Extract the file name without the extension
    file_name = os.path.splitext(os.path.basename(model_path))[0]
    output_project_info.append(("File Name", file_name))
    # print("File Name: " + file_name)

    central_path = "This document is not workshared."
    #print("Central File Path: " + central_path)

output_project_info.append(("Central File Path", central_path))
#print(output_project_info)

# Get the current user's name
user_name = app.Username
output_project_info.append(("Export by", user_name))
#print("Export by: " + user_name)

if len(output_data) == 2:
    forms.alert("No filters are currently applied.\nThe report will not be exported.", exitscript=True)

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