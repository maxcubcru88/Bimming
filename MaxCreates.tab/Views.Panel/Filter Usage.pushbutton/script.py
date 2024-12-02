# -*- coding: utf-8 -*-
__title__ = "Filter\nUsage"
__doc__ = """Version = 1.0
Date    = 28.10.2024
_____________________________________________________________________
Description:
Rename Views in Revit by using Find/Replace Logic
_____________________________________________________________________
How-to:
-> Click on the button
-> Select Views
-> Define Renaming Rules
-> Rename Views
_____________________________________________________________________
Last update:
- [28.10.2024] - 1.1 First Release
_____________________________________________________________________
Author: Máximo Cubero"""

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
#==================================================
# Regular + Autodesk
from Autodesk.Revit.DB import *
from System.Collections.Generic import List
import csv

# pyRevit
from pyrevit import revit, forms

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
#==================================================
doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app   = __revit__.Application

# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝ MAIN
#==================================================

def export_to_csv(path, data):
    # Writing to the CSV file
    with open(file_path, 'w') as file:
        writer = csv.writer(file, lineterminator='\n')
        writer.writerows(data)
    print("Data exported to:", file_path)

# # Data to export
# data = [[1, 2, 3, 4, 5], ['a', 'b', 'c', 'd', 'e']]
# # Filepath for the CSV
# file_path = r'C:\\Users\\34644\\Downloads\\test\\test01.csv'
#
# export_to_csv(file_path, data)



# #🔒 Start Transaction to make changes in project
# t = Transaction(doc, 'MC-Rename Views')
#
# t.Start()  #🔓
# for view in sel_views:
#
#     #3️⃣ Create New View Name
#     old_name = view.Name
#     new_name = prefix + old_name.replace(find, replace) + suffix
#
#     #4️⃣ Rename Views (Ensure unique view name)
#     for i in range(20):
#         try:
#             view.Name = new_name
#             print('{} -> {}'.format(old_name, new_name))
#             break
#         except:
#             new_name += '*'
#
# t.Commit() #🔒
#
# print ('-'*50)
# print ('Done!')"""


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

filters_used   = GetUsedFilterIds(doc)
filters_unused = GetUnusedFilters(doc)

# print(type(filters_unused))
# print(list(filters_unused))


output_filters, output_views = [], []
output = [["View Type", "View Name", "IsViewTemplate", "Sheet Info", "View Template Applied", "Filter Name", "Filter Id", "IsEnabled"]]

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
            aux.append(str(vType))
            aux.append(v.Name)
            aux.append(v.IsTemplate)
            aux.append(sheetInfo)
            aux.append(vTemplate)
            aux.append(doc.GetElement(f).Name)
            aux.append(f.IntegerValue)
            aux.append(v.GetIsFilterEnabled(f))

            output.append(aux)

OUT = output


file_path = r'C:\\Users\\34644\\Downloads\\test\\test01.csv'
export_to_csv(file_path, output)

# for e in output:
# #     print(e)



