# -*- coding: utf-8 -*-
__title__ = "Reset\nSplasher"
__doc__ = """Resets graphic overrides for walls, reference planes, and grids in the active view.

Author: Máximo Cubero"""

__min_revit_ver__ = 2021
__max_revit_ver__ = 2025

# CONSTANTS
#==================================================
TRANSACTION_NAME = "Bimming-Reset Splash"

# IMPORTS
#==================================================
# Custom Libraries
from Snippets._bimming_graphics_override import *

# Regular + Autodesk
from Autodesk.Revit.DB import *

# VARIABLES
#==================================================
doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app   = __revit__.Application

# MAIN
#==================================================

#1️⃣ Select Wall, Grid or Ref Planes
all_walls        = FilteredElementCollector(doc).OfClass(Wall).ToElements()
all_grids        = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Grids).WhereElementIsNotElementType().ToElements()
all_ref_planes   = FilteredElementCollector(doc, doc.ActiveView.Id).OfClass(ReferencePlane).ToElements()

collector = list(all_walls) + list(all_grids) + list(all_ref_planes)

# RESET GRAPHICS FOR ALL THE ELEMENTS
t = Transaction(doc, TRANSACTION_NAME)
t.Start()

for el in collector:
    settings = set_graphics_override_direction()
    doc.ActiveView.SetElementOverrides(el.Id, settings)

t.Commit()