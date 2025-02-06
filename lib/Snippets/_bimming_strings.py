# -*- coding: utf-8 -*-


# Imports
#==================================================
from Autodesk.Revit.DB import *

# Variables
#==================================================
app   = __revit__.Application
uidoc = __revit__.ActiveUIDocument
doc   = __revit__.ActiveUIDocument.Document #type:Document

# Functions
#==================================================

def remove_detached_suffix(string):
    """Removes the '_detached' suffix from a string if present.

    Args:
        string (str): The input string.

    Returns:
        str: The string without the '_detached' suffix.
    """
    if string.endswith('_detached'):
        return string[:-9]  # Remove the last 9 characters
    return string