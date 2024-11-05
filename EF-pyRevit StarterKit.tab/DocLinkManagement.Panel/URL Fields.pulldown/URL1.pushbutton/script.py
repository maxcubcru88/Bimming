# -*- coding: utf-8 -*-
__title__ = "Doc Link01"
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

def remove_quotes(input_string):
    if input_string.startswith(("'", '"')) and input_string.endswith(("'", '"')):
        return input_string[1:-1]
    return input_string

def duplicate_and_replace_folder(folder_path):
    # Check if the folder exists and is a directory
    if not os.path.isdir(folder_path):
        raise ValueError("The specified folder path does not exist or is not a directory.")

    # Define the duplicated folder path
    temp_folder_path = folder_path + "_temp_copy"

    # Step 1: Duplicate the folder
    shutil.copytree(folder_path, temp_folder_path)

    # Step 2: Delete the original folder
    shutil.rmtree(folder_path)

    # Step 3: Rename the duplicated folder to the original name
    os.rename(temp_folder_path, folder_path)

# 1️⃣ Updating the info in the script.py file

# Get the script's onw path
script_path = os.path.abspath(__file__)
script_path = script_path.replace('DocLinkManagement.Panel\URL Fields.pulldown','DocLink.Panel')
yaml_path = script_path.replace('pushbutton\script.py', r'urlbutton\bundle.yaml')

# Read the current content of the script
with open(yaml_path, 'r') as file:
    content = file.readlines()

# # 2️⃣🅰️ Definining Button Name and URL or doc path
# assign_name = 'title: test\n'
# assign_url = 'hyperlink: "https://www.bbc.com/mundo"'

# 2️⃣🅱️ Define Renaming Rules (UI FORM)
# https://revitpythonwrapper.readthedocs.io/en/latest/ui/forms.html?highlight=forms#flexform
from rpw.ui.forms import (FlexForm, Label, TextBox, Separator, Button)

components = [Label('Button Name:'),                    TextBox('button_name', content[0].split(": ", 1)[1][:-1]),
              Label('URL, Directory or File Path:'),    TextBox('button_url', content[1].split(": ", 1)[1][1:-1]),
              Separator(),                              Button('Update')]

form = FlexForm('Title', components)
form.show()

# Ensure Components are Filled
try:
    user_inputs = form.values #type: dict
    assign_name = remove_quotes(user_inputs['button_name']).strip()
    assign_url  = remove_quotes(user_inputs['button_url']).strip()
except:
    sys.exit()

if assign_name == '':
    forms.alert('Title has to be defined. Please Try Again', exitscript=True)
elif assign_url == '':
    forms.alert('URL, directory or file path has to be defined. Please Try Again', exitscript=True)

# Formating the name and path
# e.g.: test -> 'title: test\n'
assign_name_format = "title: {}\n".format(assign_name)
assign_url_format  = "hyperlink: '{}'".format(assign_url)

# This example changes line 2
content[0] = assign_name_format
content[1] = assign_url_format

# Write the modified content back to the script
with open(yaml_path, 'w') as file:
    file.writelines(content)

url_folder_path = script_path.replace('pushbutton\script.py', r'urlbutton')
duplicate_and_replace_folder(url_folder_path)

# print (yaml_path)
# print (content[0])
# print (content[1])
# print ('-'*50)
# print ('Done!')
