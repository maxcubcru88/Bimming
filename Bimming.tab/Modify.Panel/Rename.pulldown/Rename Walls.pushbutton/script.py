# -*- coding: utf-8 -*-
__title__ = "Rename\nWalls"
__doc__ = """Exports a CSV report listing all the wall types in the project.
Populate a name for each wall in Excel and push back into the model.

Click - EXPORT Excel List
Shift + Click - IMPORT Excel Report

Author: Máximo Cubero"""

__min_revit_ver__ = 2021
__max_revit_ver__ = 2025

# IMPORTS
#==================================================

from Snippets._bimcore_complex_def import *

# VARIABLES
#==================================================
doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app   = __revit__.Application

# MAIN
#==================================================

rename_types(category='Walls')