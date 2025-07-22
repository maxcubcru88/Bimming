# -*- coding: utf-8 -*-
__title__   = "Unhide\nSection Box"
__doc__     = """Ensures the Section Box is visible and active in the current view.

 - Unhides and activates the Section Box if needed
 - Enables Temporary View Properties and shows the 'Section Boxes' annotation category

Author: Maximo Cubero"""

__min_revit_ver__ = 2021
__max_revit_ver__ = 2025

__context__ = ["active-3d-view"]

# CONSTANTS
#==================================================
TRANSACTION_NAME = "Bimming-All Annotations OFF"

# IMPORTS
#==================================================
import clr
clr.AddReference('System')
from Snippets._bimming_views import *
from Snippets._bimming_convert import *

from Autodesk.Revit.UI import TaskDialog, TaskDialogCommonButtons, TaskDialogResult

# VARIABLES
#==================================================
app    = __revit__.Application
uidoc  = __revit__.ActiveUIDocument
doc    = __revit__.ActiveUIDocument.Document #type:Document

# MAIN
#==================================================
from System.Collections.Generic import List

t = Transaction(doc, TRANSACTION_NAME)
t.Start()

active_view = doc.ActiveView

# UNHIDE SECTION BOX IF NOT VISIBLE
section_box_element = get_section_box(doc, active_view)[0]
section_box_is_hidden = doc.GetElement(section_box_element.Id).IsHidden(active_view)
# print(section_box_is_hidden)
if section_box_is_hidden:
    active_view.UnhideElements(List[ElementId]([section_box_element.Id]))

# ACTIVATE SECTION BOX IN VIEW IF NOT ACTIVE
if not active_view.IsSectionBoxActive:
    active_view.IsSectionBoxActive = True
    doc.Regenerate()  # Optional but recommended
    TaskDialog.Show("Title", "The Section Box has been ACTIVATED in the view.")

# ACTIVATE THE ANNOT. CATEGORY SECTION BOX & THE TEMPORARY VIEW PROPERTIES OF THE VIEW
# Get 'Section Boxes' annotation category
for cat in doc.Settings.Categories:
    if cat.CategoryType == CategoryType.Annotation and cat.Name == "Section Boxes":
        annotation_category_section_box = cat
        break
annotation_category_section_box_ishidden = active_view.GetCategoryHidden(annotation_category_section_box.Id)
# print(annotation_category_section_box_ishidden)
if annotation_category_section_box_ishidden:
    if not active_view.IsTemporaryViewPropertiesModeEnabled():
        message = "The Temporary View Properties and the Annotation Category 'Section Boxes' has been ACTIVATED."
    else:
        message = "The Annotation Category 'Section Boxes' has been ACTIVATED."
    active_view.EnableTemporaryViewPropertiesMode(active_view.Id)
    active_view.SetCategoryHidden(annotation_category_section_box.Id, False)
    TaskDialog.Show("Title", message)

t.Commit()