# -*- coding: utf-8 -*-
__title__ = "Rename\nFilters"
__doc__ = """Version = 1.0
Date    = 28.10.2024
_____________________________________________________________________
Description:
Rename Views in Revit by using Find/Replace Logic
_____________________________________________________________________
How-to:
-> Click on the button
-> Select Views
-> Define Renaming Rules
-> Rename Views
_____________________________________________________________________
Last update:
- [28.10.2024] - 1.1 First Release
_____________________________________________________________________
Author: Máximo Cubero"""

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
#==================================================
# Regular + Autodesk
from Autodesk.Revit.DB import *

# pyRevit
from pyrevit import revit, forms

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
#==================================================
doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app   = __revit__.Application

# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝ MAIN
#==================================================

def get_filter_type_text(filter_obj):
    """
    Get the string representation of a Revit filter type.

    Args:
        filter_obj: The filter object (e.g., FilterStringEquals, FilterNumericEquals, etc.).

    Returns:
        A string that represents the filter type (e.g., 'Equals', 'Contains', etc.).
    """
    if isinstance(filter_obj, FilterIntegerRule):
        return 'Integer'
    elif isinstance(filter_obj, FilterInverseRule):
        return 'Not'

    elif isinstance(filter_obj, FilterNumericEquals):
        return 'Equals'
    elif isinstance(filter_obj, FilterNumericGreater):
        return 'Greater'
    elif isinstance(filter_obj, FilterNumericGreaterOrEqual):
        return 'Greater or Equal'
    elif isinstance(filter_obj, FilterNumericLess):
        return 'Less'
    elif isinstance(filter_obj, FilterNumericLessOrEqual):
        return 'Less or Equal'
    elif isinstance(filter_obj, FilterNumericRuleEvaluator):
        return 'Numeric Rule'
    elif isinstance(filter_obj, FilterNumericValueRule):
        return 'Numeric Value'

    elif isinstance(filter_obj, FilterStringBeginsWith):
        return 'Begins With'
    elif isinstance(filter_obj, FilterStringContains):
        return 'Contains'
    elif isinstance(filter_obj, FilterStringEndsWith):
        return 'Ends With'
    elif isinstance(filter_obj, FilterStringEquals):
        return 'Equals'
    elif isinstance(filter_obj, FilterStringGreater):
        return 'Greater'
    elif isinstance(filter_obj, FilterStringGreaterOrEqual):
        return 'Greater or Equal'
    elif isinstance(filter_obj, FilterStringLess):
        return 'Less'
    elif isinstance(filter_obj, FilterStringLessOrEqual):
        return 'Less or Equal'
    elif isinstance(filter_obj, FilterStringRuleEvaluator):
        return 'String Rule'

    elif isinstance(filter_obj, FilterValueRule):
        return 'Value Rule'




    # Add more cases as needed for other filter types
    else:
        return 'Unknown Filter Type'

# def get_all_parameters_names_and_ids(doc):
#     """
#     Get the names and IDs of all parameters in the document.
#
#     Args:
#         doc: The current Revit document.
#
#     Returns:
#         A dictionary where the key is the parameter's ID and the value is the parameter's name.
#     """
#     parameter_info = {}
#
#     # Collect all elements in the document (can be filtered if needed)
#     elements = FilteredElementCollector(doc).WhereElementIsNotElementType().ToElements()
#
#     # Iterate through all elements
#     for element in elements:
#         # Loop through all parameters of the element
#         for param in element.Parameters:
#             # Check if the parameter's Definition is not None before accessing its Name
#             if param.Definition:
#                 parameter_info[param.Id] = param.Definition.Name  # Add to dictionary
#
#     return parameter_info


def get_all_parameters(doc):
    """
    Get the names and IDs of all parameters in the document.

    Args:
        doc: The current Revit document.

    Returns:
        A dictionary where the key is the parameter's ID and the value is the parameter's name.
    """
    # Initialize an empty dictionary to store parameter IDs and names
    param_dict = {}

    # Collect all elements in the document
    collector = FilteredElementCollector(doc).WhereElementIsNotElementType()

    # Iterate through each element in the collector
    for element in collector:
        # Get all parameters for this element
        params = element.Parameters
        for param in params:
            # Check if the parameter is valid and has a definition
            if param and param.Definition:
                param_dict[param.Id] = param.Definition.Name

    # Collect built-in parameters (e.g., instance, type)
    built_in_params = doc.ParameterBindings
    for binding in built_in_params:
        definition = binding.Definition
        if definition and definition.Id not in param_dict:
            param_dict[definition.Id] = definition.Name

    # Collect shared parameters
    # This assumes that you have access to shared parameter definitions
    # Note: You'll need to reference the shared parameter file and load it for this to work
    shared_param_file = doc.Application.SharedParametersFilename
    if shared_param_file:
        shared_param_file = doc.Application.SharedParametersFile
        for group in shared_param_file.Groups:
            for definition in group.Definitions:
                if definition and definition.Id not in param_dict:
                    param_dict[definition.Id] = definition.Name

    return param_dict


""" Rename views on sheets
    SHEET NUMBER + DETAIL NUMBER + TITLE ON SHEET (IF POPULATED)
    SHEET NUMBER + DETAIL NUMBER + VIEW NAME
"""

#forms.alert("WIP-Rename Filters")

all_filter        = FilteredElementCollector(doc).OfClass(ParameterFilterElement).ToElements()

project_parameters = get_all_parameters(doc)

for filter in all_filter:

    filter_name = filter.Name
    print('FILTER NAME: {}'.format(filter_name))

    get_categories_id = filter.GetCategories()
    categories = [Category.GetCategory(doc, category_id).Name for category_id in get_categories_id]
    print('CATEGORIES SELECTED: {}'.format(categories))

    print('CONDITIONS/RULES:')
    get_element_filters = filter.GetElementFilter().GetFilters()

    for f in get_element_filters:
        rules = f.GetRules()
        for rule in rules:
            # print('Rules: {}'.format(rule))
            # Parameter

            rule_parameter_id = rule.GetRuleParameter()
            try:    rule_parameter = project_parameters[rule_parameter_id]
            except: rule_parameter = 'check!'

            if hasattr(rule, "GetEvaluator"):
                rule_condition = rule.GetEvaluator()
                rule_condition_name = get_filter_type_text(rule_condition)
                try:
                    rule_value = rule.RuleString
                except: rule_value = 'check!'
            elif hasattr(rule, "GetInnerRule"):
                rule_condition = rule.GetInnerRule()
                rule_condition_name = get_filter_type_text(rule_condition)
                rule_value = rule_condition.RuleValue
            else:
                rule_condition_name = 'To be defined'
                rule_value = 'To be defined'
            print('Parameter: ID: {}, NAME: {}\n'
                  'Rule Condition: {}\n'
                  'Rule Value: {}'
                  .format(rule_parameter_id,rule_parameter, rule_condition_name, rule_value))


    print("-" * 100)
    # get_element_filter = f.GetElementFilter

