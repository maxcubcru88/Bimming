# -*- coding: utf-8 -*-
__title__ = "Doc Link03"
__doc__ = """Version = 1.0
Date    = 28.10.2024
_____________________________________________________________________
Description:
Custom shortcut to a URL or a document in your PC
_____________________________________________________________________
How-to:
-> Click on the button
-> Define a name for the button
-> Introduce a path (file, directory or URL)
-> Click in the button to open that file
_____________________________________________________________________
Last update:
- [30.10.2024] - 1.1 First Release
_____________________________________________________________________
Author: Máximo Cubero"""

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
#==================================================
import os
import sys
import shutil

# Regular + Autodesk
from Autodesk.Revit.DB import *

# pyRevit
from pyrevit import revit, forms
from Snippets._buttonupdates import button_update_title_and_path

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

# 1️⃣ Updating the info in the script.py file
# Get the script's onw path
current_script_path = os.path.abspath(__file__)
yaml_folder_path = current_script_path.replace('DocLinkManagement.Panel\URL Fields.pulldown', 'DocLink.Panel')
yaml_file_path = yaml_folder_path.replace('pushbutton\script.py', r'urlbutton\bundle.yaml')

button_update_title_and_path(yaml_folder_path, yaml_file_path)