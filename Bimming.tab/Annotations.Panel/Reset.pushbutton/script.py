# -*- coding: utf-8 -*-
__title__   = "Reset Temp.\nView Prop."
__doc__     = """Disables Temporary View Properties mode in the active view.

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

active_view = doc.ActiveView

t = Transaction(doc, TRANSACTION_NAME)
t.Start()

active_view.EnableTemporaryViewPropertiesMode(ElementId.InvalidElementId)

t.Commit()