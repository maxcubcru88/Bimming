# -*- coding: utf-8 -*-
__title__   = "Template"
__doc__     = """Adjusts the section box of a 3D view to match the crop region of the active 2D view (Section, Elevation, Plan, or Callout).  

Shift+Click: Opens a menu to select a specific 3D view and apply a view template.  

Author: Maximo Cubero"""

__min_revit_ver__ = 2021
__max_revit_ver__ = 2025

# CONSTANTS
#==================================================
TRANSACTION_NAME = "View Auto Section Box"

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
