# -*- coding: utf-8 -*-


# Imports
#==================================================
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import TaskDialog
import sys

# Variables
#==================================================
app   = __revit__.Application
uidoc = __revit__.ActiveUIDocument
doc   = __revit__.ActiveUIDocument.Document #type:Document

# Functions
#==================================================

def check_parameter_binding(doc, param_name, categories_to_check):
    """
    Checks whether a shared or project parameter exists in the document
    and is bound to the given Revit categories.

    If the parameter exists but is not bound to one or more categories,
    it shows a warning listing the missing ones and stops execution.

    Args:
        doc: The current Revit document.
        param_name (str): The name of the parameter to look for.
        categories_to_check (list[BuiltInCategory]): Categories to verify.

    Returns:
        None

    Raises:
        SystemExit: Stops the script if the parameter is missing or not bound to all categories.
    """
    binding_map = doc.ParameterBindings
    iterator = binding_map.ForwardIterator()
    iterator.Reset()

    while iterator.MoveNext():
        definition = iterator.Key
        binding = iterator.Current

        if definition.Name == param_name:
            # Get bound categories
            bound_cats = [cat for cat in binding.Categories]
            bound_cat_ids = [c.Id.IntegerValue for c in bound_cats]

            # Check which categories are missing
            missing_cats = []
            for bic in categories_to_check:
                cat = doc.Settings.Categories.get_Item(bic)
                if cat.Id.IntegerValue not in bound_cat_ids:
                    missing_cats.append(cat.Name)

            if missing_cats:
                msg = "⚠️ Parameter '{}' is not bound to the following categories:\n{}".format(
                    param_name, "\n".join(missing_cats)
                )
                TaskDialog.Show("Missing Binding", msg)
                sys.exit()  # Stop execution if any category is missing

            # Fully bound
            # print("✅ Parameter '{}' is bound to all required categories.".format(param_name))
            return

    # Parameter not found at all
    TaskDialog.Show("Warning", "⚠️ Parameter '{}' not found in the project.".format(param_name))
    sys.exit()

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