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

def get_all_parameters_names_and_ids(doc):
    """
    Get the names and IDs of all parameters in the document.

    Args:
        doc: The current Revit document.

    Returns:
        A dictionary where the key is the parameter's ID and the value is the parameter's name.
    """
    parameter_info = {}

    # Collect all elements in the document (can be filtered if needed)
    elements = FilteredElementCollector(doc).WhereElementIsNotElementType().ToElements()

    # Iterate through all elements
    for element in elements:
        # Loop through all parameters of the element
        for param in element.Parameters:
            # Check if the parameter's Definition is not None before accessing its Name
            if param.Definition:
                parameter_info[param.Id] = param.Definition.Name  # Add to dictionary

    return parameter_info


""" Rename views on sheets
    SHEET NUMBER + DETAIL NUMBER + TITLE ON SHEET (IF POPULATED)
    SHEET NUMBER + DETAIL NUMBER + VIEW NAME
"""

#forms.alert("WIP-Rename Filters")

all_filter        = FilteredElementCollector(doc).OfClass(ParameterFilterElement).ToElements()

project_parameters = get_all_parameters_names_and_ids(doc)

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
                try:
                    rule_value = rule.RuleString
                except: rule_value = 'check!'
            elif hasattr(rule, "GetInnerRule"):
                rule_condition = rule.GetInnerRule()
                rule_value = rule_condition.RuleValue
            else:
                rule_condition = 'To be defined'
            print('Parameter: ID: {}, NAME: {}\n'
                  'Rule Condition: {}\n'
                  'Rule Value: {}'
                  .format(rule_parameter_id,rule_parameter, rule_condition, rule_value))


    print("-" * 100)
    # get_element_filter = f.GetElementFilter

