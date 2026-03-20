# -*- coding: utf-8 -*-
__title__ = "Select Loadable Families by Family Name"
__doc__ = """Select instances by family name.

Author: Máximo Cubero"""

__min_revit_ver__ = 2021
__max_revit_ver__ = 2025

# CONSTANTS
#==================================================
TRANSACTION_NAME = "Bimming-Select by Family Name"

# IMPORTS
#==================================================
import sys
import System
from Autodesk.Revit.DB import *
from pyrevit import forms
from System.Collections.Generic import List

# VARIABLES
#==================================================
doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

# MAIN
#==================================================

# 1️⃣ Collect all Family elements (loadable families)
families = FilteredElementCollector(doc)\
    .OfClass(Family)\
    .ToElements()

# 2️⃣ Get their names (unique and sorted)
family_names = sorted(set(family.Name for family in families))

# 3️⃣ WPF Form to select families
res = forms.SelectFromList.show(
    family_names,
    title='Loadable Families',
    multiselect=True,
    button_name='Select'
)

if not res:
    sys.exit()

selected_families = res

# 4️⃣ Collect all Family Instances elements in the model
# FAMILY INSTANCES (model elements)
model_elements = FilteredElementCollector(doc)\
    .OfClass(FamilyInstance)\
    .WhereElementIsNotElementType()\
    .ToElements()

# TAGS
all_built_in_categories = list(System.Enum.GetValues(BuiltInCategory))
cats_02 = []
for bic in all_built_in_categories:
    if 'tag' in str(bic).lower():
        cats_02.append(bic)
List_cats = List[BuiltInCategory](cats_02)
multi_cat_filter                 = ElementMulticategoryFilter(List_cats)
collector_tags                   = FilteredElementCollector(doc).WherePasses(multi_cat_filter).WhereElementIsNotElementType().ToElements()

# COLLECTOR
collector = []
collector.extend(list(model_elements))
collector.extend(list(collector_tags))

# 5️⃣ Filter only those whose Family.Name matches the selected families
selected_instances = []
for i in collector:
    try:
        if i.Symbol.Family.Name in selected_families:
            selected_instances.append(i)
    except:
        family_type = doc.GetElement(i.get_Parameter(BuiltInParameter.ELEM_TYPE_PARAM).AsElementId())
        family_name = family_type.get_Parameter(BuiltInParameter.SYMBOL_FAMILY_NAME_PARAM).AsString()
        if family_name in selected_families:
            selected_instances.append(i)

# 6️⃣ Select these elements in Revit’s UI
element_ids = List[ElementId]([i.Id for i in selected_instances])
uidoc.Selection.SetElementIds(element_ids)

forms.alert("{0} instances selected.".format(len(selected_instances)), title="Selection Complete")