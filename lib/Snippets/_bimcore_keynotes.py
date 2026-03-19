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

def create_keynote_table_dict(doc):
    """
    This function creates a dictionary from the keynote table in a Revit document.

    The dictionary will have the keynote keys as the keys and their corresponding
    keynote text as the values.

    Args:
        doc: The Revit document containing the keynote table.

    Returns:
        dict: A dictionary where the keys are the keynote keys and the values are
              the corresponding keynote text.
    """

    # Get the keynote table from the Revit document
    keynote_table = KeynoteTable.GetKeynoteTable(doc)

    # Initialize an empty dictionary to store keynote data
    keynote_dict = {}

    # Loop through the keynote table entries
    for e in keynote_table.GetKeyBasedTreeEntries():
        key = e.Key  # Get the keynote key
        keynote_text = e.KeynoteText  # Get the keynote text

        # Add the key and keynote text to the dictionary
        keynote_dict[key] = keynote_text

    return keynote_dict