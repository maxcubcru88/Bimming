# -*- coding: utf-8 -*-
__title__   = "Is Mirrored"
__doc__     = """Adjusts the section box of a 3D view to match the crop region of the active 2D view (Section, Elevation, Plan, or Callout).  

Shift+Click: Opens a menu to select a specific 3D view and apply a view template.  

Author: Maximo Cubero"""

__min_revit_ver__ = 2021
__max_revit_ver__ = 2025

# CONSTANTS
#==================================================
TRANSACTION_NAME = "View Auto Section Box"

# IMPORTS
#==================================================
import clr
clr.AddReference('System')
from Snippets._bimming_views import *
from Snippets._bimming_functions import *
from Snippets._bimming_vectors import *
from Snippets._bimming_transform import *
from Snippets._bimming_convert import *

import sys
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *

# VARIABLES
#==================================================
app    = __revit__.Application
uidoc  = __revit__.ActiveUIDocument
doc    = __revit__.ActiveUIDocument.Document #type:Document

# MAIN
#==================================================

# Define shared parameter name
PARAMETER_NAME = "BIMMING_is_shared"

# Define shared parameter group
PARAMETER_GROUP = BuiltInParameterGroup.PG_GENERAL

# Define categories (Doors, Windows, Generic Models)
CATEGORIES = [BuiltInCategory.OST_Doors, BuiltInCategory.OST_Windows, BuiltInCategory.OST_GenericModel]

# Get the shared parameter file
appSharedParamsFile = app.OpenSharedParameterFile()
if not appSharedParamsFile:
    TaskDialog.Show("Error", "No Shared Parameter File is set. Please set it in Revit.")
    sys.exit()

# Check if parameter already exists in the project
def parameter_exists(param_name):
    for param in doc.ParameterBindings:
        if param.Definition.Name == param_name:
            return True
    return False

if parameter_exists(PARAMETER_NAME):
    TaskDialog.Show("Info", "Parameter '{}' already exists in the project.".format(PARAMETER_NAME))
    sys.exit()

# Get the first group in the shared parameters file
paramGroups = list(appSharedParamsFile.Groups)  # Convert to a list
if not paramGroups:
    TaskDialog.Show("Error", "No parameter groups found in Shared Parameters file.")
    sys.exit()

paramGroup = paramGroups[0]  # Use the first group

# Try to get the parameter definition
paramDefinition = None
for definition in paramGroup.Definitions:
    if definition.Name == PARAMETER_NAME:
        paramDefinition = definition
        break

# If parameter does not exist, create it
if not paramDefinition:
    paramDefinition = paramGroup.Definitions.Create(PARAMETER_NAME, str(ParameterType.Text), False)

# Start a transaction
t = Transaction(doc, "Add Shared Parameter")
t.Start()

# Get category set
categorySet = app.Create.NewCategorySet()
for cat in CATEGORIES:
    categorySet.Insert(doc.Settings.Categories.get_Item(cat))

# Create binding
binding = app.Create.NewInstanceBinding(categorySet)
doc.ParameterBindings.Insert(paramDefinition, binding, PARAMETER_GROUP)

# Enable "Vary by Group"
paramElem = doc.get_Parameter(paramDefinition.Name)
if paramElem:
    paramElem.SetAllowVaryBetweenGroups(doc, True)

t.Commit()

TaskDialog.Show("Success", "Shared Parameter '{}' added to Doors, Windows, and Generic Models.".format(PARAMETER_NAME))