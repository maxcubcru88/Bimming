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
    """Retrieves a 3D view family type by its name.

    Args:
        view_type_name (str): The name of the 3D view type to search for.

    Returns:
        ViewFamilyType or None: The matching 3D view family type, or None if not found.
    """
    collector = FilteredElementCollector(doc).OfClass(ViewFamilyType)
    for vft in collector:
        name_param = vft.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString()
        if vft.ViewFamily == ViewFamily.ThreeDimensional and name_param == view_type_name:
            return vft
    return None

def GetFilterIds(view):
    """Gets the filter IDs applied to a given view.

    Args:
        view (View): The view from which to retrieve filter IDs.

    Returns:
        list or None: A list of filter IDs if filters are applied, None otherwise.
    """
    try:
        filterIds = view.GetFilters()
    except Exception:
        filterIds = None
    return filterIds