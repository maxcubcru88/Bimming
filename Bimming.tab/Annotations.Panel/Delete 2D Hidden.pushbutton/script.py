# -*- coding: utf-8 -*-
__title__   = "Delete\n2D Hidden"
__doc__     = """It identifies and removes hidden 2D annotation elements including:

 - Detail Groups
 - Dimensions
 - Detail Lines
 - Detail Components (Components, Filled and Mask Regions)
 - Insulation Lines
 - Text Notes
 - Tags
 
It provides an option to review and export a report before deletion.

Shift+Click:
It will display a menu to select specific categories from above

Author: Maximo Cubero"""

__min_revit_ver__ = 2021
__max_revit_ver__ = 2025

# CONSTANTS
#==================================================
TRANSACTION_NAME = "Bimming-Delete 2D Hidden"

# IMPORTS
#==================================================
from Autodesk.Revit.DB import *
from pyrevit import forms
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
app    = __revit__.Application
uidoc  = __revit__.ActiveUIDocument
doc    = __revit__.ActiveUIDocument.Document #type:Document

# CLASS
#==================================================
class MyOption(forms.TemplateListItem):
    def __init__(self, item, el_name, checked=False):
        self.item = item #Id of the element
        self.el_name = el_name
        self.checked = checked

    @property
    def name(self):
        el_id = str(self.item)
        return "Name: {}".format(self.el_name)


# MAIN
#==================================================
from pyrevit import EXEC_PARAMS

items = ['Detail Groups', 'Dimensions', 'Detail Lines', 'Detail Components (Components, Filled and Mask Regions)',
         'Insulation Lines', 'Text Notes', 'Tags']
if EXEC_PARAMS.config_mode: #if SHIFT-Click
    res = forms.SelectFromList.show(items, button_name='Select Item',multiselect=True)
else:
    res = items

if not res:
    sys.exit()

# 1️⃣Collecting elements
# DETAIL GROUPS
collector_detail_groups_all = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_IOSDetailGroups).WhereElementIsNotElementType().ToElements()

exclusion_list_groups_members = []
for detail_group in collector_detail_groups_all:
    members = collect_all_group_members(doc, detail_group)
    for member in members:
        exclusion_list_groups_members.append(member.Id)

collector_detail_groups = []
for detail_group in collector_detail_groups_all:
    if detail_group.Id not in exclusion_list_groups_members:
        collector_detail_groups.append(detail_group)

# DIMENSIONS
cats_01 =  [BuiltInCategory.OST_Dimensions,
            BuiltInCategory.OST_SpotElevations,
            BuiltInCategory.OST_SpotCoordinates,
            BuiltInCategory.OST_SpotSlopes]
List_cats = List[BuiltInCategory](cats_01)
multi_cat_filter = ElementMulticategoryFilter(List_cats)
collector_dimensions_all         = FilteredElementCollector(doc).WherePasses(multi_cat_filter).ToElements()
collector_dimensions             = [e for e in collector_dimensions_all if e.Id not in exclusion_list_groups_members]

# DETAIL - DETAIL LINES
collector_detail_lines_all       = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Lines).WhereElementIsNotElementType().ToElements()
collector_detail_lines           = [e for e in collector_detail_lines_all if e.Id not in exclusion_list_groups_members]

# DETAIL - COMPONENTS, FILLED REGIONS AND MASK REGIONS
collector_detail_items_all       = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_DetailComponents).WhereElementIsNotElementType().ToElementIds()
exclusion_detail_item_nested     = get_nested_detail_items(doc) # DB.ElementId of elements nested in Detail Items

collector_detail_items = []
for e in collector_detail_items_all:
    if e in exclusion_detail_item_nested: continue
    if e in exclusion_list_groups_members: continue
    collector_detail_items.append(doc.GetElement(e))

# DETAIL - INSULATION
collector_insulation_lines_all   = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_InsulationLines).WhereElementIsNotElementType().ToElements()
collector_insulation_lines       = [e for e in collector_insulation_lines_all if e.Id not in exclusion_list_groups_members]

# TEXT
collector_text_notes_all         = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_TextNotes).WhereElementIsNotElementType().ToElements()
collector_text_notes             = [e for e in collector_text_notes_all if e.Id not in exclusion_list_groups_members]

# TAGS
all_built_in_categories = list(System.Enum.GetValues(BuiltInCategory))
cats_02 = []
for bic in all_built_in_categories:
    if 'tag' in str(bic).lower():
        cats_02.append(bic)
List_cats = List[BuiltInCategory](cats_02)
multi_cat_filter                 = ElementMulticategoryFilter(List_cats)
collector_tags_all               = FilteredElementCollector(doc).WherePasses(multi_cat_filter).ToElements()
collector_tags                   = [e for e in collector_tags_all if e.Id not in exclusion_list_groups_members]

# COLLECTOR
collector = []
for e in res:
    if     e == 'Dimensions': collector.extend(list(collector_dimensions))
    elif   e == 'Detail Lines': collector.extend(list(collector_detail_lines))
    elif   e == 'Detail Components (Components, Filled and Mask Regions)': collector.extend(list(collector_detail_items))
    elif   e == 'Insulation Lines': collector.extend(list(collector_insulation_lines))
    elif   e == 'Text Notes': collector.extend(list(collector_text_notes))
    elif   e == 'Tags': collector.extend(list(collector_tags))
    elif   e == 'Detail Groups': collector.extend(list(collector_detail_groups))


# 2️⃣Extracting data
elements_to_delete = []
info_report = [[],["DATA"],['CATEGORY', 'ELEMENT ID', 'FAMILLY NAME', 'TYPE NAME','SHEET INFO', 'VIEW TYPE', 'VIEW TYPE NAME', 'VIEW NAME', 'IS HIDDEN']]
for e in collector:
    if e.ViewSpecific:
        # Info Start
        cat = e.Category.Name
        element_id = e.Id.IntegerValue
        type_name = Element.Name.GetValue(e)
        if type_name == 'Detail Filled Region': type_name = Element.Name.GetValue(doc.GetElement(e.GetTypeId()))
        view = doc.GetElement(e.OwnerViewId)
        view_type = doc.GetElement(view.GetTypeId()).FamilyName
        view_type_name = get_view_type_name(doc,view)
        view_name = view.Name
        sheet_info = view.get_Parameter(BuiltInParameter.VIEW_SHEET_VIEWPORT_INFO).AsString()

        if type_name == 'Masking Region':
            family_name = 'Masking Region'
        else:
            try: family_name = doc.GetElement(e.GetTypeId()).FamilyName
            except: family_name = e.Id.IntegerValue
        # Info Ends

        if is_detail_group(e):
            is_hidden = True
            #group_members = e.GetMemberIds()
            group_members = collect_all_group_members(doc, e)
            for member in group_members:
                # member = doc.GetElement(member_id)
                # print(member_id)
                if is_detail_group(member): continue
                if is_revision_cloud(member):
                    is_hidden = False
                    break
                if is_element_hidden_permanent(view,member):
                    continue
                else:
                    is_hidden = False
                    break
        else:
            is_hidden = e.IsHidden(doc.GetElement(e.OwnerViewId))

        if is_hidden:
            elements_to_delete.append(e.Id)
            info_report.append([cat, element_id, family_name, type_name, sheet_info, view_type, view_type_name, view_name, is_hidden])

# Check if there are elements to be deleted
if not elements_to_delete:
    forms.alert('There are no elements to be deleted. Good job!', warn_icon=False, exitscript=True)
    sys.exit()


# 3️⃣Deciding what to do with the elements that can be deleted
# If there are elements to be deleted, decide what to do
res = forms.alert("{} instances can be deleted. How would you like to proceed?".format(len(elements_to_delete)),
                  options=["Delete the instances and save an Excel Report",
                           "Don't delete the instances and save an Excel Report",
                           "Exit. Thanks for the information"],
                  warn_icon = False)

# Actions based of the decision
if res == "Delete the instances and save an Excel Report" or res == "Don't delete the instances and save an Excel Report":

    project_info = get_project_info(doc, app)

    directory = create_report_directory('Bimming_2D_Annotation_Purge')

    dic = list_to_dict(project_info)
    file_name = dic['File Name']
    report_name = generate_report_name(file_name)

    # 4️⃣Export the report
    # Create the full file path with the .csv extension
    csv_file_path = os.path.join(directory, report_name[0] + ".csv")

    data = project_info + info_report
    export_to_csv(csv_file_path, data)

# problems_to_delete = []
if res == "Delete the instances and save an Excel Report":
    with Transaction(doc, TRANSACTION_NAME) as t:
        t.Start()
        for element_id in elements_to_delete:
            try: doc.Delete(element_id)
            except: pass #problems_to_delete.append(element_id)
        t.Commit()  # Commit the transaction

    message = '{} Elements have been deleted'.format(len(elements_to_delete))
    forms.alert(message,'title', warn_icon=False)