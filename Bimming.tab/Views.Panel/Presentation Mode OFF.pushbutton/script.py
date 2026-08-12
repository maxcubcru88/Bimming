# -*- coding: utf-8 -*-
__title__   = "Disable\nPresentation"
__doc__     = """Reverts the active view from presentation mode.

 - Disables Temporary View Properties Mode, restoring Annotations, Analytical
   Model, and CAD Links / Imports visibility to how they were before
 - Disables "Smooth Lines with Anti-Aliasing" for the view

Author: Maximo Cubero"""

__min_revit_ver__ = 2021
__max_revit_ver__ = 2026

# CONSTANTS
#==================================================
TRANSACTION_NAME = "Bimming-Presentation Mode OFF"

# IMPORTS
#==================================================
import clr
from traceback import print_tb
clr.AddReference('System')
from Snippets._bimcore_convert import *

# VARIABLES
#==================================================
app    = __revit__.Application
uidoc  = __revit__.ActiveUIDocument
doc    = __revit__.ActiveUIDocument.Document #type:Document

# MAIN
#==================================================
active_view = doc.ActiveView

t = Transaction(doc, TRANSACTION_NAME)
t.Start()

# 1️⃣ EXIT TEMPORARY VIEW MODE (restores Annotations, Analytical Model, and CAD Links visibility)
active_view.EnableTemporaryViewPropertiesMode(ElementId.InvalidElementId)

# 2️⃣ DISABLE SMOOTH LINES WITH ANTI-ALIASING
try:
    display_model = active_view.GetViewDisplayModel()
    display_model.SmoothEdges = False
    active_view.SetViewDisplayModel(display_model)
except Exception:
    pass  # View type does not support display-related properties (e.g. schedules)

t.Commit()
