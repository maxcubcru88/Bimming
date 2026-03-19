# -*- coding: utf-8 -*-


# Imports
#==================================================
from Autodesk.Revit.DB import *

from System.Collections.Generic import List  # .NET List

# Variables
#==================================================
app   = __revit__.Application
uidoc = __revit__.ActiveUIDocument
doc   = __revit__.ActiveUIDocument.Document #type:Document

# Functions
#==================================================

def select_elements_by_ids(uidoc, element_ids):
    """
    Selects elements in Revit given a list of ElementIds.

    Args:
        uidoc: The active Revit UI document.
        element_ids: A list of ElementId objects.

    Returns:
        None
    """
    if not element_ids:
        print("No elements to select.")
        return

    # Ensure all items are ElementId objects
    valid_ids = List[ElementId]([eid for eid in element_ids if isinstance(eid, ElementId)])

    if valid_ids:
        uidoc.Selection.SetElementIds(valid_ids)
        print("Selected {} elements.".format(len(valid_ids)))
    else:
        print("No valid ElementIds found.")
