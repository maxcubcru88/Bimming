# -*- coding: utf-8 -*-
# Regular + Autodesk
from Autodesk.Revit.DB import *

# pyRevit
from pyrevit import script, revit, forms
output = script.get_output()

def message_learning(btn_name):
    # 👀 Print Message
    forms.alert('Message from reuse library is working! ^^. The scrip {btn_name} is working'.format(btn_name=btn_name))

