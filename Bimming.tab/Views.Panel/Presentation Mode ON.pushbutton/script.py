# -*- coding: utf-8 -*-
__title__   = "Enable\nPresentation"
__doc__     = """Prepares the active view for presentation.

 - Enables Temporary View Properties Mode (non-destructive)
 - Hides all Annotation categories
 - Hides Analytical Model categories
 - Hides CAD Links / Imports
 - Enables "Smooth Lines with Anti-Aliasing" for the view

Use "Disable Presentation" to revert all of the above.

Author: Maximo Cubero"""

__min_revit_ver__ = 2021
__max_revit_ver__ = 2026

# CONSTANTS
#==================================================
TRANSACTION_NAME = "Bimming-Presentation Mode"

# IMPORTS
#==================================================
import clr
from traceback import print_tb
clr.AddReference('System')
from pyrevit.compat import get_elementid_value_func
from Snippets._bimcore_convert import *

# VARIABLES
#==================================================
app    = __revit__.Application
uidoc  = __revit__.ActiveUIDocument
doc    = __revit__.ActiveUIDocument.Document #type:Document

get_elementid_value = get_elementid_value_func()  # Returns .Value (2024+) or .IntegerValue (<2024), compatible across Revit versions

# MAIN
#==================================================
active_view = doc.ActiveView

t = Transaction(doc, TRANSACTION_NAME)
t.Start()

# 1️⃣ TEMPORARY VIEW MODE
active_view.EnableTemporaryViewPropertiesMode(active_view.Id)

# 2️⃣ HIDE ALL ANNOTATION CATEGORIES
annotation_categories = [cat for cat in doc.Settings.Categories if cat.CategoryType == CategoryType.Annotation]
for category in annotation_categories:
    try:
        active_view.SetCategoryHidden(category.Id, True)
    except Exception:
        pass  # Category can't be hidden in this view type

# 3️⃣ HIDE ANALYTICAL MODEL CATEGORIES
try:
    active_view.AreAnalyticalModelCategoriesHidden = True
except Exception:
    pass  # Not supported in this view type

# 4️⃣ HIDE CAD LINKS / IMPORTS
cad_category_ids = {}  # keyed by element id value to avoid duplicate categories (multiple layers per import)
for cad_link in FilteredElementCollector(doc, active_view.Id).OfClass(ImportInstance).WhereElementIsNotElementType():
    if cad_link.Category:
        cad_category_ids[get_elementid_value(cad_link.Category.Id)] = cad_link.Category.Id

for cat_id in cad_category_ids.values():
    try:
        active_view.SetCategoryHidden(cat_id, True)
    except Exception:
        pass

# 5️⃣ ENABLE SMOOTH LINES WITH ANTI-ALIASING
try:
    display_model = active_view.GetViewDisplayModel()
    display_model.SmoothEdges = True
    active_view.SetViewDisplayModel(display_model)
except Exception:
    pass  # View type does not support display-related properties (e.g. schedules)

t.Commit()
