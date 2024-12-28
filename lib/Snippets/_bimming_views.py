# -*- coding: utf-8 -*-

# Imports
#==================================================
from Autodesk.Revit.DB import *

# Variables
#==================================================
app   = __revit__.Application
uidoc = __revit__.ActiveUIDocument
doc   = __revit__.ActiveUIDocument.Document #type:Document

# Reusable Snippets

def get_existing_3d_view_type(view_type_name):
    collector = FilteredElementCollector(doc).OfClass(ViewFamilyType)
    for vft in collector:
        name_param = vft.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString()
        if vft.ViewFamily == ViewFamily.ThreeDimensional and name_param == view_type_name:
            return vft
    return None