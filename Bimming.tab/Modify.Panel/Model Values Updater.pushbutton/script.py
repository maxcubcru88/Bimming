# -*- coding: utf-8 -*-
__title__ = "Model\nCode"
__doc__ = """Sets the Model parameter based on the Family Type Name..

Family Type names must comply with KCA naming standards.

Format:

<ModelCode> - <Description>

Example:
WN01A - W910 x H1310mm

The Type Name must begin with the model code, followed by a hyphen (-) and then the descriptive text. The model code portion is extracted and assigned to the Model parameter.

Author: Máximo Cubero"""

__min_revit_ver__ = 2021
__max_revit_ver__ = 2025

# CONSTANTS
#==================================================
TRANSACTION_NAME = "KCA-Set WNs Model Value"

# IMPORTS
#==================================================
import re
from Autodesk.Revit.DB import *

# VARIABLES
#==================================================
doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app   = __revit__.Application

# MAIN
#==================================================

pattern = re.compile(r'^([A-Za-z]{2}\d{2}[A-Za-z])\s?-.+$')

elements_symbols = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Windows).WhereElementIsElementType().OfClass(FamilySymbol).ToElements()

t = Transaction(doc, TRANSACTION_NAME)
t.Start()

for e in elements_symbols:
    type_name = e.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString()
    if not pattern.match(type_name):
        print("INVALID TYPE NAME: {}".format(type_name))
        continue

    match = pattern.match(type_name)
    model_code = match.group(1)
    model_param = e.get_Parameter(BuiltInParameter.ALL_MODEL_MODEL)

    if model_param and not model_param.IsReadOnly:
        model_param.Set(model_code)
    else:
        print("ERROR SETTING THE MODE:: {}".format(type_name))

t.Commit()
