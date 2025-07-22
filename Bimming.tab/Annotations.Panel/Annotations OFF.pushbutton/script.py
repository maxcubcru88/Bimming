# -*- coding: utf-8 -*-
__title__   = "Disable\nAnnotations"
__doc__     = """It temporarily hides annotation categories in the current view to reduce visual noise.

 - Normal mode: hides all annotation categories
 - Config mode (Shift+Click): hides only Callouts, Elevations, Sections, and Section Boxes; shows all others

Uses Temporary View Properties to ensure changes are non-destructive.

Author: Maximo Cubero"""

__min_revit_ver__ = 2021
__max_revit_ver__ = 2025

# CONSTANTS
#==================================================
TRANSACTION_NAME = "Bimming-All Annotations OFF"

# IMPORTS
#==================================================
import clr
from traceback import print_tb
clr.AddReference('System')
from Snippets._bimming_convert import *

# VARIABLES
#==================================================
app    = __revit__.Application
uidoc  = __revit__.ActiveUIDocument
doc    = __revit__.ActiveUIDocument.Document #type:Document

# MAIN
#==================================================
from pyrevit import EXEC_PARAMS

t = Transaction(doc, TRANSACTION_NAME)
t.Start()

active_view = doc.ActiveView
active_view.EnableTemporaryViewPropertiesMode(active_view.Id)

# Get annotation categories
annotation_categories = [cat for cat in doc.Settings.Categories if cat.CategoryType == CategoryType.Annotation]

# Define exclusions based on config mode
if EXEC_PARAMS.config_mode:
    category_list = ['Callouts', 'Elevations', 'Sections', 'Section Boxes']
else:
    category_list = ['Section Boxes']

# Toggle visibility
for category in annotation_categories:
    try:
        if category.Name == 'Section Boxes' and isinstance(active_view, View3D) and not active_view.IsTemplate:
            active_view.SetCategoryHidden(category.Id, True)
        else:
            should_hide = category.Name in category_list if EXEC_PARAMS.config_mode else category.Name not in category_list
            active_view.SetCategoryHidden(category.Id, should_hide)
    except Exception:
        pass  # Optionally log the exception for debugging

t.Commit()