# -*- coding: utf-8 -*-


# Imports
#==================================================
from Autodesk.Revit.DB import *
from collections import defaultdict

# Variables
#==================================================
app   = __revit__.Application
uidoc = __revit__.ActiveUIDocument
doc   = __revit__.ActiveUIDocument.Document #type:Document

# Functions
#==================================================

def group_by_second_arg(items):
    """
    Groups items by the second element in each tuple.

    Args:
        items (list of tuples): A list where each tuple contains two elements.

    Returns:
        dict: A dictionary where keys are the second tuple elements and values are lists of first elements.
    """
    grouped = defaultdict(list)
    for item in items:
        key = item[1]  # The second element of the tuple
        grouped[key].append(item[0])  # Append the first element to the group
    return dict(grouped)