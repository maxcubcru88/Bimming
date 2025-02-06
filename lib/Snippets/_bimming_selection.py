# -*- coding: utf-8 -*-

# Imports
#==================================================
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI.Selection import ISelectionFilter

# Variables
#==================================================
app   = __revit__.Application
uidoc = __revit__.ActiveUIDocument
doc   = __revit__.ActiveUIDocument.Document #type:Document

# Reusable Snippets

def get_selected_elements(filter_types = None):
    """Function to get Selected Elements in Revit UI.
    You can provide a list of types for filter_types parameter (optionally)
    e.g.
    sel_walls = get_selected_elements([Wall])
    """
    selected_element_ids    = uidoc.Selection.GetElementIds()
    selected_elements       = [doc.GetElement(e_id) for e_id in selected_element_ids]
    #Filter Selection (Optionally)
    if filter_types:
        return [el for el in selected_elements if type(el) in filter_types]
    return selected_elements


class IselectionFilter_Classes(ISelectionFilter):
    def __init__(self, allowed_types):
        """ ISelectionFilter made to filter with types
        allowed_types: list of allowed Types"""
        self.allowed_types = allowed_types

    def AllowElement(self, element):
        if type(element) in self.allowed_types:
            return True

#THIS ONE DOES NOT WORK IN RVT 2021
class IselectionFilter_Categories(ISelectionFilter):
    def __init__(self, allowed_categories):
        """ ISelectionFilter made to filter with categories
        allowed_types: list of allowed Types"""
        self.allowed_categories = allowed_categories

    def AllowElement(self, element):
        if element.Category.BuiltInCategory in self.allowed_categories:
            return True