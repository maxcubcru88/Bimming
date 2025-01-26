# -*- coding: utf-8 -*-
__title__ = "Filter Usage\nTemplate"
__doc__ = """Description

Author: Máximo Cubero"""

# IMPORTS
#==================================================
# Regular + Autodesk
from Autodesk.Revit.DB import *

# pyRevit
from pyrevit import revit, forms

# VARIABLES
#==================================================
doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app   = __revit__.Application

# MAIN
#==================================================

__beta__ = True
forms.inform_wip()