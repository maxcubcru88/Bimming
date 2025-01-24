# -*- coding: utf-8 -*-
__title__ = "Rename\nFilters"
__doc__ = """Automatically renames filters in your model using the format: 'Category/ies' + 'Rules' + #Description#

Author: Máximo Cubero"""

#__helpurl__ = "https://www.bimming.uk"
__min_revit_ver__ = 2021
__max_revit_ver__ = 2025
#__context__ = 'zero-doc'
#__highlight__ = 'new'

# IMPORTS
#==================================================
# Regular + Autodesk
from Autodesk.Revit.DB import *
import re
# pyRevit
from pyrevit import revit, forms

# VARIABLES
#==================================================
doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app   = __revit__.Application

# MAIN
#==================================================

def duplicate_tracker(lst):
    """
    Assigns a group name prefixed with 'DUPLICATED' to words that appear more than once in the list.
    Words that appear only once are labeled as 'NOT DUPLICATED'.
    """
    # Count occurrences of each word
    counts = {}
    for word in lst:
        counts[word] = counts.get(word, 0) + 1

    # Initialize variables
    group_mapping = {}
    group_counter = {}
    output = []

    for word in lst:
        if counts[word] > 1:  # If the word repeats
            if word not in group_mapping:
                # Assign a base label like "DUPLICATED 1", "DUPLICATED 2"
                group_mapping[word] = "DUPLICATED " + str(len(group_mapping) + 1)
                group_counter[word] = 0

            group_counter[word] += 1
            if group_counter[word] == 1:
                output.append(group_mapping[word])
            else:
                output.append("{} ({})".format(group_mapping[word], group_counter[word] - 1))
        else:  # If the word is unique
            output.append("NOT DUPLICATED")

    return output


# lst = ['11', '22', '11', '11', '222', '22']
# temp = duplicate_tracker(lst)
# print(temp)


def get_parameter_name_by_id(doc, param_id):
    """
    Get the name of a parameter by its ID.

    Args:
        doc: The current Revit document.
        param_id (ElementId or int): The parameter ID as an ElementId or an integer.

    Returns:
        str: The name of the parameter, or None if not found.
    """
    # Ensure param_id is an ElementId
    if not isinstance(param_id, ElementId):
        param_id = ElementId(param_id)

    # Check if it's a built-in parameter
    try:
        built_in_param = BuiltInParameter(param_id.IntegerValue)
        if built_in_param != BuiltInParameter.INVALID:
            return LabelUtils.GetLabelFor(built_in_param)
    except:
        pass

    # Check if it's a shared parameter
    shared_param = doc.GetElement(param_id)
    if shared_param:
        return shared_param.Name

    return None

# param_id = -1002053  # Workset parameter ID
# param_name = get_parameter_name_by_id(doc, param_id)
#
# if param_name:
#     print("Parameter Name: {}".format(param_name))
# else:
#     print("Parameter ID {} not found.".format(param_id))

def get_workset_by_id(doc, workset_id):
    """
    Get a workset by its ID.

    Args:
        doc: The current Revit document.
        workset_id (int): The ID of the workset to retrieve.

    Returns:
        Workset: The workset object if found, otherwise None.
    """
    workset_table = doc.GetWorksetTable()
    workset = workset_table.GetWorkset(WorksetId(workset_id))
    return workset

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
        return 'Is Greater Than'
    elif isinstance(filter_obj, FilterNumericGreaterOrEqual):
        return 'Is Greater Than Or Equal To'
    elif isinstance(filter_obj, FilterNumericLess):
        return 'Is Less Than'
    elif isinstance(filter_obj, FilterNumericLessOrEqual):
        return 'Is Less Than Or Equal To'
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
        return 'Is Greater Than'
    elif isinstance(filter_obj, FilterStringGreaterOrEqual):
        return 'Is Greater Than Or Equal To'
    elif isinstance(filter_obj, FilterStringLess):
        return 'Is Less Than'
    elif isinstance(filter_obj, FilterStringLessOrEqual):
        return 'Is Less Than Or Equal To'
    elif isinstance(filter_obj, FilterStringRuleEvaluator):
        return 'String Rule'

    elif isinstance(filter_obj, FilterValueRule):
        return 'Value Rule'



    # Add more cases as needed for other filter types
    else:
        return 'Unknown Filter Type'

def get_filter_rule(doc, rule, parameter_id):

    rule_filter = "TBC"
    rule_value = "TBC"

    if isinstance(rule, FilterIntegerRule):
        rule_filter = get_filter_type_text(rule.GetEvaluator())
        rule_value = rule.RuleValue
        #print('Integer Rule')
    elif isinstance(rule, FilterStringRule):
        rule_filter = get_filter_type_text(rule.GetEvaluator())
        rule_value = rule.RuleString
        #print ('String Rule')
    elif isinstance(rule, FilterDoubleRule):
        rule_filter = get_filter_type_text(rule.GetEvaluator())
        rule_value = rule.RuleValue
        #print('Double Rule')
    elif isinstance(rule, FilterInverseRule):
        rule_filter_inverse_rule = get_filter_rule(doc, rule.GetInnerRule(), parameter_id)
        rule_filter = rule_filter_inverse_rule[0]
        rule_value_id = rule_filter_inverse_rule[1]
        #rule_value = get_workset_by_id(doc, rule_value_id).Name
        rule_value = 'TBC'
        #print('Inverse Rule')
    elif isinstance(rule, FilterElementIdRule):
        # if rule.UsesLevelFiltering(doc, parameter_id):
        #     rule_filter = 'Level'
        # else:
        #     rule_filter = 'Element Id'
        rule_filter = 'Element Id'
        rule_value = doc.GetElement(rule.RuleValue).Name
        #print('Element Id Rule')
    elif isinstance(rule, HasValueFilterRule):
        rule_filter = 'Has Value'
        rule_value = 'Empty'
        #print('Has Value Rule')
    elif isinstance(rule, HasNoValueFilterRule):
        rule_filter = 'Has No Value'
        rule_value = 'Empty'
        #print('Has No Value Rule')
    else:
        pass
        #print('Other Rule')

    return (rule_filter, rule_value)

def check_condition_type(element_filter):
    if isinstance(element_filter, LogicalAndFilter):
        return " AND "
    elif isinstance(element_filter, LogicalOrFilter):
        return " OR "
    else:
        return "Unknown"


def extract_hash_value_from_end(text):
    """
    This function reverses the input text, extracts the second value
    enclosed in hash symbols (#), and then reverses the extracted value.

    Parameters:
    - text (str): The input string containing values enclosed in hash symbols.

    Returns:
    - str: The reversed value enclosed in the second pair of hash symbols.
    """
    # Step 1: Reverse the entire text
    reversed_text = text[::-1]

    # Step 2: Apply the regex to extract the second #enclosed value
    match = re.search(r'(#[^#]*#)', reversed_text)

    if match:
        # Step 3: Reverse the extracted value
        reversed_output = match.group(1)[::-1]
        return reversed_output
    return None


def remove_specific_characters(input_string):
    """
    Removes the characters \:{}[]|;<>?~ from the input string.

    Args:
        input_string (str): The string to process.

    Returns:
        str: A string with the specified characters removed.
    """
    # Define the characters to remove
    characters_to_remove = r"\:{}[]|;<>?~"

    # Use str.replace in a loop to remove each character
    for char in characters_to_remove:
        input_string = input_string.replace(char, '')

    return input_string


# Example usage
# example = "-*#Sample: text {with} special |characters| to remove? ~Test!"
# result = remove_specific_characters(example)
# print(result)  # Output: "Sample text with special characters to remove Test!"

"""
IMPROVE THE INPUTS
EVALUATOR ELEMENT ID TEST
UNITS, CONVERT TO PROJECTS UNITS
"""

MAX_CATEGORIES = 3
MAX_RULES = 4

# 2️⃣🅱️ Define Renaming Rules (UI FORM)
# https://revitpythonwrapper.readthedocs.io/en/latest/ui/forms.html?highlight=forms#flexform
from rpw.ui.forms import (FlexForm, Label, TextBox, Separator, Button)

components = [Label('Max number of categories to be included in the name\nof the filter'),  TextBox('cat'),
              Label('Max number of rules to show in the name of the filter'),    TextBox('rules'),
              Separator(),
              Button('Rename Views')]

form = FlexForm('Title', components)
form.show()

# Ensure Components are Filled
try:
    user_inputs     = form.values #type: dict
    MAX_CATEGORIES  = int(user_inputs['cat'])
    MAX_RULES       = int(user_inputs['rules'])
except:
    forms.alert('Rules to rename have not been defined. Please Try Again', exitscript=True)

print(MAX_CATEGORIES)
print(MAX_RULES)

#1️⃣ Collecting filters and filter rules
DEBUG_MODE_1 = False
DEBUG_MODE_2 = False
DEBUG_MODE_3 = True

all_filter        = FilteredElementCollector(doc).OfClass(ParameterFilterElement).ToElements()

filters_and_rules = []

for filter in all_filter:
    aux = []
    # GET FILTER NAME
    filter_name = filter.Name
    if DEBUG_MODE_1: print('FILTER NAME: {}'.format(filter_name))
    aux.append(filter)

    # GET CATEGORIES
    categories_ids = filter.GetCategories()
    categories = [Category.GetCategory(doc, category_id).Name for category_id in categories_ids]
    categories = sorted(categories, key=lambda x: x)
    if DEBUG_MODE_1: print('CATEGORIES SELECTED: {}'.format(categories))
    aux.append(categories)
    if DEBUG_MODE_1: print('CONDITIONS/RULES:')

    # RULES
    # Check if there are not any rules:
    try:
        get_element_filters = filter.GetElementFilter().GetFilters()
    except:
        number_of_rules = 'N/A'
        rule = '(There are not any rules set)'
        if DEBUG_MODE_1: print(rule)
        if DEBUG_MODE_1: print("-" * 100)
        aux.append(rule)
        aux.append(number_of_rules)
        filters_and_rules.append(aux)
        continue

    # Check if there are sets in the filter:
    check_set = any([isinstance(e, LogicalAndFilter) or isinstance(e, LogicalOrFilter) for e in get_element_filters])
    if check_set:
        number_of_rules = 'N/A'
        rule = '(Contains Sets)'
        if DEBUG_MODE_1: print(rule)
        if DEBUG_MODE_1: print("-" * 100)
        aux.append(rule)
        aux.append(number_of_rules)
        filters_and_rules.append(aux)
        continue

    # Check the condition
    element_filter = filter.GetElementFilter()
    condition = check_condition_type(element_filter)

    # Collect rules:
    rules_all = []

    for enum, f in enumerate(get_element_filters, 1):
        rules = f.GetRules()
        for rule in rules:
            rule_number = '\nRule ' + str(enum) + ':'
            if DEBUG_MODE_1: print(rule_number)

            # PARAMETER NAME
            rule_parameter_id = rule.GetRuleParameter()
            #print(type(rule_parameter_id))
            try:    rule_parameter = get_parameter_name_by_id(doc, rule_parameter_id)
            except: rule_parameter = "It couldn't get the parameter name. Check!"
            #get_filter_rule(doc, rule, rule_parameter_id)
            #print('Rule Type: {}'.format(get_filter_type_text(rule)))

            # RULE FILTER
            rule_type = type(rule)
            rule_filter = get_filter_rule(doc,rule, rule_parameter_id)[0]
            rule_value = get_filter_rule(doc,rule, rule_parameter_id)[1]
            #aux.append(rule_type)

            r = [rule_parameter, rule_filter, str(rule_value)]
            rule_compact = '(' + '-'.join(r) + ')'
            rules_all.append(rule_compact)

            if DEBUG_MODE_1: print(rule_compact)

    number_of_rules = len(rules_all)
    rules_all = sorted(rules_all, key=lambda x: x)
    rules_all_compact = '(' + condition.join(rules_all) + ')'
    if DEBUG_MODE_1:
        print('\nRULES COMPACTED:')
        print(rules_all_compact)

    if DEBUG_MODE_1:
        print('\nNUMBER OF RULES:')
        print(number_of_rules)
    aux.append(rules_all_compact)
    aux.append(number_of_rules)
    filters_and_rules.append(aux)

    if DEBUG_MODE_1: print("-" * 100)

#2️⃣ GROUPING CATS AND FILTER TO FIND DUPLICATES

categories_and_filters = []
for instance in filters_and_rules:
    # JOINING CATEGORIES
    filter_categories   = instance[1]
    filter_categories_concat = '_'.join(filter_categories)
    # FILTER RULES
    filter_rules        = instance[2]
    # UNIQUE NAME
    unique_name = '#CATS: ' + filter_categories_concat + ' #RULES: ' + filter_rules
    categories_and_filters.append(unique_name)
    #print(unique_name)

cats_filters_duplicated = duplicate_tracker(categories_and_filters)

for a, b in zip(filters_and_rules, cats_filters_duplicated):
    a.append(b)

for lst in filters_and_rules:
    for l in lst:
        if DEBUG_MODE_2:
            print(l)
    if DEBUG_MODE_2:
        print('-'*100)


#3️⃣ RENAMING FILTERS

# 🔓 Starting Transaction
t = Transaction(doc, 'Bimming-Rename Filters')
t.Start()

for f in filters_and_rules:

    filter              = f[0]          # Revit.DB.ParameterFilterElement
    filter_name         = filter.Name   # Name of the filter
    filter_categories   = f[1]          # List       -> ['Doors', 'Floors', 'Ramps', 'Stairs', 'Walls']
    filter_rules        = f[2]          # String     -> ((Assembly Description-Has Value-Empty)AND(Cut-Has Value-Empty)AND(Workset-Equals-TBC))
    number_of_rules     = f[3]          # String/Int -> 'N/A', 2, 3...
    duplicated          = f[4]          # String     -> 'NOT DUPLICATED', 'DUPLICATED_001', 'DUPLICATED_002', ETC

    if DEBUG_MODE_3:
        print(filter_name)
        print(filter_categories)
        print(number_of_rules)
        print(filter_rules)
        print(duplicated)
        print('-'*100)

    # We assume that a description is not need in principle
    description_cat = False
    description_rules = False

    if len(filter_categories) <= MAX_CATEGORIES:
        filter_categories_concat = '* ' + '_'.join(filter_categories)
    else:
        filter_categories_concat = '+' + str(MAX_CATEGORIES) + ' categories'
        description_cat = True
    #print(filter_categories_concat)

    if number_of_rules != 'N/A' and number_of_rules > MAX_RULES:
        filter_rules ='(+' + str(MAX_RULES) + ' rules)'
        description_rules = True
    elif filter_rules == '(Contains Sets)':
        description_rules = True
    else: pass

    if extract_hash_value_from_end(filter_name):
        description = ' - ' + extract_hash_value_from_end(filter_name)
    else:
        if description_cat or description_rules:
            description = ' - ' + '#Description#'
        else: description = ''

    if duplicated == 'NOT DUPLICATED':
        duplicated = ''
    else:
        duplicated = ' - ' + duplicated

    # Check if the current name of the filer contains any description

    filter_name_new = filter_categories_concat + ' - RULES ' + filter_rules + description + duplicated

    # Adding (1), (2), etc to have unique names:
    filter_names_used = []
    iteration = 0
    while filter_name_new in filter_names_used:
        iteration += 1
        filter_name_new = "{}({})".format(filter_name_new, iteration)
    filter_names_used.append(filter_name_new)

    # Renaming the filters
    # Removing special characters if any, some subcategories had the special characters '<' and '>'
    filter_name_new = remove_specific_characters(filter_name_new)
    try:
        filter.Name = filter_name_new
    except Exception as e:
        if DEBUG_MODE_3: print("Error renaming filter:", e)

    message =   ('--------------------------------------------------' + '\n'
                'FILTER NAME OLD: {}\n'
                'FILTER NAME NEW: {}\n'
                '---------------------------------------------------'
                .format(filter_name, filter_name_new))
    if DEBUG_MODE_3: print (message)

t.Commit()
# 🔐 Finishing Transaction




