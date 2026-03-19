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

def flatten(nested_list):
    """
    Recursively flattens a nested list.

    Args:
        nested_list: A list that may contain nested lists.

    Returns:
        A flat list with all elements from the nested structure.
    """
    flat_list = []

    for item in nested_list:
        if isinstance(item, list):
            flat_list.extend(flatten_list(item))  # Recursively flatten
        else:
            flat_list.append(item)  # Append non-list elements directly

    return flat_list

def list_to_dict(data):
    """Convert a list of key-value tuples into a dictionary."""
    return dict(data)

def get_family_symbol_by_name(doc, family_name):
    """
    Retrieves a family symbol from the Revit document based on the family name.

    Parameters:
    doc (Document): The current Revit document.
    family_name (str): The name of the family whose symbol is to be retrieved.

    Returns:
    FamilySymbol: The family symbol that matches the specified family name, or None if no match is found.
    """
    # Collect all family symbols in the document
    collector = FilteredElementCollector(doc).OfClass(FamilySymbol)

    # Loop through the family symbols and check if they match the name 'Point'
    for symbol in collector:
        family = symbol.Family
        if family.Name == family_name:
            return symbol

    # If no matching family is found, return None
    return None

def get_3d_view_by_name(doc, view_name):
    """Retrieve a 3D view by its name."""
    return next(
        (view for view in FilteredElementCollector(doc)
         .OfClass(View3D)
         if view.Name == view_name),
        None
    )