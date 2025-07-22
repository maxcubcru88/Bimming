# -*- coding: utf-8 -*-
__title__   = "Hide\nSection Box"
__doc__     = """It checks whether the Section Box is visible in the current view and hides it.

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

# HIDE SECTION BOX IF NOT VISIBLE
section_box_element = get_section_box(doc, active_view)[0]
section_box_is_hidden = doc.GetElement(section_box_element.Id).IsHidden(active_view)
if not section_box_is_hidden:
    active_view.HideElements(List[ElementId]([section_box_element.Id]))
else:
    TaskDialog.Show("Title", "The Section Box is already hidden")

t.Commit()