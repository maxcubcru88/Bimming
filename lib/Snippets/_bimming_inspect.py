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

def is_detail_group(element):
    """Checks if the given element is a detail group.

    Args:
        element (Element): The Revit element to check.

    Returns:
        bool: True if the element is a detail group, False otherwise.
    """
    return element.Category and element.Category.Id.IntegerValue == int(BuiltInCategory.OST_IOSDetailGroups)


def is_revision_cloud(element):
    """Checks if the given element is a detail group.

    Args:
        element (Element): The Revit element to check.

    Returns:
        bool: True if the element is a revision cloud, False otherwise.
    """
    return element.Category and element.Category.Id.IntegerValue == int(BuiltInCategory.OST_RevisionClouds)


def is_shared(family_instance):
    """
    Checks if a shared family is nested within another family.

    Args:
        family_instance (FamilyInstance): The Revit family instance.

    Returns:
        bool: True if the family is shared and nested within another family, False otherwise.
    """
    # If you're in a project and want to check whether a loaded family is shared, you need to look at the "Shared" parameter in the family types

    if not isinstance(family_instance, FamilyInstance):
        return False

    family = family_instance.Symbol.Family  # Get the Family object
    shared_param = family.get_Parameter(BuiltInParameter.FAMILY_SHARED)
    if shared_param.AsInteger() == 1:
        return True
    else:
        return False

def is_element_hidden_permanent(view, element):
    """Checks if an element is hidden in the given view.

    Args:
        view (View): The Revit view in which to check visibility.
        element (Element): The Revit element to check.

    Returns:
        bool: True if the element is hidden, False otherwise.
    """
    if element.IsHidden(view):
        return True  # Element is hidden using 'Hide Elements'

    return False


def is_callout_view(view):
    """
    Checks if a view is a callout.

    Parameters:
        view (View): The Revit view to check.

    Returns:
        bool: True if the view is a callout, False otherwise.
    """
    return view.GetPrimaryViewId().IntegerValue != -1