# -*- coding: utf-8 -*-
__title__   = "Worksets\n3D Views"
__doc__     = """Version = 1.0
Date    = 12.11.2024
________________________________________________________________
Description:

Create a 3D view per workset and hide all the workset but one.

The name of the 3D View starts with Audit_Worset-"Workset Name"

To modify the prefix execute the script with Shift+Click

________________________________________________________________
How-To:

1. [Hold ALT + CLICK] on the button to open its source folder.
You will be able to override this placeholder.

2. Automate Your Boring Work ;)

________________________________________________________________
TODO:
[FEATURE] - Describe Your ToDo Tasks Here
________________________________________________________________
Last Updates:
<>
________________________________________________________________
Author: Maximo Cubero"""

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝
#==================================================
from Autodesk.Revit.DB import *

# pyRevit
from pyrevit import revit, forms

import sys

#.NET Imports
import clr
clr.AddReference('System')
from System.Collections.Generic import List


# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝
#==================================================
app    = __revit__.Application
uidoc  = __revit__.ActiveUIDocument
doc    = __revit__.ActiveUIDocument.Document #type:Document


# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝
#==================================================

t = Transaction(doc, 'MC-Audit Worksets Create 3D Views')
t.Start()

# Define the desired name for the new 3D View Type
new_view_type_name = "Audit_Workset"

# Function to get existing ViewFamilyType for 3D views
def get_existing_3d_view_type(view_type_name):
    collector = FilteredElementCollector(doc).OfClass(ViewFamilyType)
    for vft in collector:
        name_param = vft.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString()
        if vft.ViewFamily == ViewFamily.ThreeDimensional and name_param == view_type_name:
            return vft
    return None

# Check if a 3D view type with the specified name already exists
existing_view_type = get_existing_3d_view_type(new_view_type_name)

if existing_view_type:
    existing_view_type_name = existing_view_type.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString()
    #print("3D View Type '{new_view_type_name}' already exists.".format(new_view_type_name=existing_view_type_name))
    new_view_type = existing_view_type
    new_view_type_boolean = False
else:
    # Find the base 3D ViewFamilyType to duplicate
    base_3d_view_type_id = doc.GetDefaultElementTypeId(ElementTypeGroup.ViewType3D)
    base_3d_view_type = doc.GetElement(base_3d_view_type_id)
    # Duplicate the existing 3D View Type to create a new one
    new_view_type = base_3d_view_type.Duplicate(new_view_type_name)
    #print("Created new 3D View Type '{}'.".format(new_view_type_name))
    new_view_type_boolean = True

if doc.ActiveView.GetTypeId() == new_view_type.Id:
    forms.alert('The current view has to be deleted.\nPlease go to another view.')

else:
    # Delete all views in the new 3D View Type
    all_views       = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Views).WhereElementIsNotElementType().ToElements()
    all_3D_views    = [view for view in all_views if view.ViewType == ViewType.ThreeD]

    for view in all_3D_views:
        if view.GetTypeId() == new_view_type.Id:
            doc.Delete(view.Id)
            #print("Deleted existing 3D View '{}'.".format(view.Id))


    all_worksets     = FilteredWorksetCollector(doc).OfKind(WorksetKind.UserWorkset)
    all_worksets_2   = list(all_worksets)   #Created for the 2nd loop within the 1st loop

    for workset in all_worksets:
        View_name = "Audit_Workset-" + workset.Name

        # Create 3D View
        # view_type_3D_id = doc.GetDefaultElementTypeId(ElementTypeGroup.ViewType3D)
        view_3d_iso = View3D.CreateIsometric(doc, new_view_type.Id)

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

    if new_view_type_boolean:
        forms.alert("A new 3D View Family Type {} has been created.".format(new_view_type_name))
    else:
        forms.alert("The views int the 3D View Family Type {} has been updated.".format(new_view_type_name))

t.Commit()


