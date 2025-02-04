# -*- coding: utf-8 -*-
__title__   = "Set of 3D Views to audit Worksets"
__doc__     = """Creates a 3D view for each workset in the project.

Author: Maximo Cubero"""

#__helpurl__ = "https://www.bimming.uk"
__min_revit_ver__ = 2021
__max_revit_ver__ = 2025
#__context__ = 'zero-doc'
#__highlight__ = 'new'

# IMPORTS
from Snippets._bimming_views import get_existing_3d_view_type
from Autodesk.Revit.DB import *
# pyRevit
from pyrevit import forms
import sys
#.NET Imports
import clr
clr.AddReference('System')

# VARIABLES
app    = __revit__.Application
uidoc  = __revit__.ActiveUIDocument
doc    = __revit__.ActiveUIDocument.Document #type:Document

#MAIN
# 📝Constants
VIEW_PREFIX = "Audit_Workset-"
THREE_D_VIEW_FAMILY_NAME = "Audit_Worksets"

# ✍️Name of views that are going to be created
all_worksets = FilteredWorksetCollector(doc).OfKind(WorksetKind.UserWorkset)
view_names_to_create = [VIEW_PREFIX + workset.Name for workset in all_worksets]

# 🕵️CHECKS
# 1️⃣Check in the model is workshared
if not forms.check_workshared(doc): sys.exit()

# 2️⃣Check if the Active View belongs to the threeD_view_family_type_name = "Audit_Workset"
threeD_view_family_type = get_existing_3d_view_type(THREE_D_VIEW_FAMILY_NAME)
message = 'The current view needs to be deleted.\nPlease switch to another view, ideally a non 3D-View'

if threeD_view_family_type:
    doc.ActiveView.GetTypeId() == threeD_view_family_type.Id
    forms.alert(message,exitscript=True)

if doc.ActiveView.Name in view_names_to_create:
    forms.alert(message, exitscript=True)

t = Transaction(doc, 'Bimming-Set of Workset Views Created')
t.Start()

# 3️⃣Check in the 3D View Types 'Audit_Workset' is already created, if not, a new one will be created
if not threeD_view_family_type:
    # Get a default 3D ViewFamilyType to duplicate
    default_threeD_view_family_type_id = doc.GetDefaultElementTypeId(ElementTypeGroup.ViewType3D)
    default_threeD_view_family_type = doc.GetElement(default_threeD_view_family_type_id)
    # Duplicate the default 3D ViewFamilyType to create a new one
    threeD_view_family_type = default_threeD_view_family_type.Duplicate(THREE_D_VIEW_FAMILY_NAME)
    #print("Created new 3D View Type '{}'.".format(new_view_type_name))

# 🔥Creating Set of Views

# 1️⃣Delete all views in the new 3D View Type or with Name already in use
all_views       = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Views).WhereElementIsNotElementType().ToElements()
all_3D_views    = [view for view in all_views if view.ViewType == ViewType.ThreeD]

for view in all_3D_views:
    if view.GetTypeId() == threeD_view_family_type.Id:
        doc.Delete(view.Id)
    elif view.Name in view_names_to_create:
        doc.Delete(view.Id)

# 2️⃣Creating the new set of 3D views
all_worksets     = FilteredWorksetCollector(doc).OfKind(WorksetKind.UserWorkset)
all_worksets_2   = list(all_worksets)   #Created for the 2nd loop within the 1st loop

count = 0

for workset in all_worksets:
    View_name = VIEW_PREFIX + workset.Name

    # Create 3D View
    view_3d_iso = View3D.CreateIsometric(doc, threeD_view_family_type.Id)

    # Rename 3D View
    view_3d_iso.Name = View_name

    # Set Detail Level to Fine
    view_3d_iso.DetailLevel = ViewDetailLevel.Fine

    # Set workset visibility
    for w in all_worksets_2:
        if workset.Id == w.Id:
            view_3d_iso.SetWorksetVisibility(w.Id, WorksetVisibility.Visible)
        else:
            view_3d_iso.SetWorksetVisibility(w.Id, WorksetVisibility.Hidden)

    count += 1

forms.alert("Job done! {} Views created/updated.\nCheck the views in your project browser starting with the prefix "
            "'Audit_Workset' which are part of the 3D View Family Type (Audit_Workset)".format(str(count)),warn_icon=False)

t.Commit()