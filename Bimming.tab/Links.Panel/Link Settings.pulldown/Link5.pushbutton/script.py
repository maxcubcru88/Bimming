# -*- coding: utf-8 -*-
__title__ = 'Link5'
__doc__ = """Sets the button name and the URL, directory, or file path for Link 5.

Author: Máximo Cubero"""

__min_revit_ver__ = 2021
__max_revit_ver__ = 2025

# IMPORTS
#==================================================
from Snippets._bimming_buttonupdates import *

# VARIABLES
#==================================================
doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app   = __revit__.Application

# MAIN
#==================================================
current_script_path = os.path.abspath(__file__)
current_url_folder_path = url_folder_path(current_script_path)
current_yaml_file_path = yaml_file_path(current_url_folder_path)

# Update the title and the URL Path in the yaml file
title_and_path = button_update_title_and_path(current_url_folder_path, current_yaml_file_path)

# Attempt to duplicate and replace the folder otherwise pyRevit does not acquire the changes
duplicate_and_replace_folder(current_url_folder_path)

# Update the title of the current script
title = title_and_path[0]
path = title_and_path[1]

# Open the current file script.py
with open(current_script_path, 'r') as file:
    content = file.readlines()

# Replacing the line wih the description of the title
title_index = (find_index_with_prefix(content, '__title__'))
title_format = "__title__ = '{}'\n".format(title)
content[title_index] = title_format

# Write the current file script.py
with open(current_script_path, 'w') as file:
    file.writelines(content)

# Alert on successful execution
forms.alert('Good!\nReload PyRevit to catch the updates.', exitscript=True)