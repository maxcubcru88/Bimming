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

def remove_quotes(input_string):
    """Removes surrounding quotes from a string, if present.

    Args:
        input_string (str): The string to process.

    Returns:
        str: The string without leading and trailing quotes.
    """
    if input_string.startswith(("'", '"')) and input_string.endswith(("'", '"')):
        return input_string[1:-1]
    return input_string

def find_index_with_prefix(items, prefix):
    """Finds the index of the first item in a list that starts with a given prefix.

    Args:
        items (list of str): The list of strings.
        prefix (str): The prefix to search for.

    Returns:
        int: The index of the first matching item, or -1 if no match is found.
    """
    for index, item in enumerate(items):
        if item.startswith(prefix):
            return index
    return -1  # Returns -1 if no item starts with the prefix


def crop_number_string(s, decimals):
    """
    Crops a numeric string to a specified number of decimal places.

    Parameters:
    s (str): The input numeric string containing a decimal point.
    decimals (int): The number of decimal places to keep.

    Returns:
    str: The cropped string with the specified decimal places.
    """
    pos = s.find('.')
    if pos == -1:
        return s  # Return the original string if '.' is not found

    new_pos = pos + decimals + 1
    return s[:new_pos]  # Return substring up to the adjusted position