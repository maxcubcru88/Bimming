# -*- coding: utf-8 -*-
__title__ = "Doc Link"
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
#import os
import os
import codecs   # Import codecs for encoding support

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

#1️⃣ Definining Button Name and URL or doc path
button_name = "New Button Name 01"
button_path = "www.youtube.com"

#2️⃣ Updating the info in the script.py file

# Get the script's onw path
script_path = os.path.abspath(__file__)

# Read the current content of the script
with open(script_path, 'r') as file:
    content = file.readlines()

# This example changes line 2
content[1] = '__title__ = "Doc Link"\n'

# Write the modified content back to the script
with open(script_path, 'w') as file:
    file.writelines(content)

print(script_path)
print(content[1])
print ('-'*50)
print ('Done!')
