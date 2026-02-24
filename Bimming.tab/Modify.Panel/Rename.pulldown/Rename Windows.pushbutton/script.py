# -*- coding: utf-8 -*-
__title__ = "Rename\nWindows"
__doc__ = """Exports a CSV report listing all the wall types in the project.
Populate a name for each wall in Excel and push back into the model.

Click - EXPORT Excel List
Shift + Click - IMPORT Excel Report

Author: Máximo Cubero"""

__min_revit_ver__ = 2021
__max_revit_ver__ = 2025

import sys

# IMPORTS
#==================================================

from Snippets._bimming_complex_def import *

# VARIABLES
#==================================================
doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app   = __revit__.Application

# MAIN
#==================================================

rename_types(category='Windows')
sys.exit()
# 1️⃣ Collect window type elements (FamilySymbol)
window_symbols = (
    FilteredElementCollector(doc)
    .OfCategory(BuiltInCategory.OST_Windows)
    .WhereElementIsElementType()
    .OfClass(FamilySymbol)
)

# 2️⃣ Deduplicate families using ElementId
families_by_id = {}

for symbol in window_symbols:
    fam = symbol.Family
    families_by_id[fam.Id.IntegerValue] = fam

# 3️⃣ Final unique families list
unique_families = list(families_by_id.values())

# Optional: print result
for fam in unique_families:
    print(fam.Name, fam.Id.IntegerValue)

sys.exit()

window_families = list(window_families)

for e in set(window_families):
    print(e.Id)

t = Transaction(doc, "Append TEST to Window Families")
t.Start()

window_families[0].Name = "TEST"

t.Commit()
