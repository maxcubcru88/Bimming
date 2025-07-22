# -*- coding: utf-8 -*-
__title__   = "Enable\nAnnotations"
__doc__     = """It temporarily shows annotation categories in the current view.

 - Normal mode: shows all annotation categories
 - Config mode (Shift+Click): shows Callouts, Elevations, Sections, and Section Boxes; hides all others

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
from pyrevit import EXEC_PARAMS
import Autodesk.Revit.DB as DB
from Snippets._bimming_views import *
from Snippets._bimming_functions import *
from Snippets._bimming_vectors import *
from Snippets._bimming_transform import *
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
    category_list = []

# Toggle visibility
for category in annotation_categories:
    try:
        should_hide = category.Name not in category_list if EXEC_PARAMS.config_mode else category.Name in category_list
        active_view.SetCategoryHidden(category.Id, should_hide)

    except Exception:
        pass  # Optionally log the exception for debugging

t.Commit()