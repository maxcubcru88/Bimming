# -*- coding: utf-8 -*-

# Imports
#==================================================
import os
import shutil
import time
import stat
import sys

from pyrevit import forms
from Autodesk.Revit.DB import *
from rpw.ui.forms import (FlexForm, Label, TextBox, Separator, Button)
from Snippets._bimming_strings import *
# Variables
#==================================================
app   = __revit__.Application
uidoc = __revit__.ActiveUIDocument
doc   = __revit__.ActiveUIDocument.Document #type:Document

# Reusable Snippets
#==================================================
def url_folder_path (path):
    """Generates a modified folder path by replacing specific substrings.

    Args:
        path (str): The original file path.

    Returns:
        str: The modified folder path.
    """
    url_folder_path = path.replace('\Link Settings.pulldown', '')
    url_folder_path = url_folder_path.replace('pushbutton\script.py', r'urlbutton')
    return url_folder_path

def yaml_file_path (yaml_folder_path):
    """Constructs the full path to a YAML file within a given folder.

    Args:
        yaml_folder_path (str): The folder containing the YAML file.

    Returns:
        str: The full path to 'bundle.yaml'.
    """
    return yaml_folder_path + r'\bundle.yaml'

def handle_remove_readonly(func, path, exc_info):
    """Removes the read-only attribute from a file and retries the operation.

    Args:
        func (callable): The function that attempted to remove the file.
        path (str): The file path.
        exc_info (tuple): Exception information.
    """
    os.chmod(path, stat.S_IWRITE)
    func(path)

def delete_folder_with_retries(folder_path, retries=5, delay=1):
    """Attempts to delete a folder with retries to handle file locks.

    Args:
        folder_path (str): The path of the folder to delete.
        retries (int, optional): Number of retry attempts. Defaults to 5.
        delay (int, optional): Delay in seconds between retries. Defaults to 1.

    Raises:
        Exception: If the folder cannot be deleted after the specified attempts.
    """
    for attempt in range(retries):
        try:
            shutil.rmtree(folder_path, onerror=handle_remove_readonly)
            return  # Exit if deletion is successful
        except Exception as e:
            print("Attempt {} failed to delete folder: {}".format(attempt + 1, e))
            time.sleep(delay)  # Wait before retrying
    raise Exception("Failed to delete the folder after {} attempts".format(retries))

def rename_folder_with_retries(src, dst, retries=5, delay=1):
    """Attempts to rename a folder with retries to handle file locks.

    Args:
        src (str): The current folder path.
        dst (str): The new folder path.
        retries (int, optional): Number of retry attempts. Defaults to 5.
        delay (int, optional): Delay in seconds between retries. Defaults to 1.

    Raises:
        Exception: If renaming fails after the specified attempts.
    """
    for attempt in range(retries):
        try:
            os.rename(src, dst)
            return  # Exit if renaming succeeds
        except Exception as e:
            print("Attempt {} failed to rename folder: {}".format(attempt + 1, e))
            time.sleep(delay)  # Wait before retrying
    raise Exception("Failed to rename the folder after {} attempts".format(retries))

def duplicate_and_replace_folder(folder_path):
    """Duplicates a folder, deletes the original, and renames the copy to the original name.

    Args:
        folder_path (str): The path of the folder to duplicate.

    Raises:
        ValueError: If the specified folder does not exist or is not a directory.
    """
    if not os.path.isdir(folder_path):
        raise ValueError("The specified folder path does not exist or is not a directory.")

    # Define the duplicated folder path and final destination path
    temp_folder_path = folder_path + "_temp_copy"

    # Step 1: Duplicate the folder
    shutil.copytree(folder_path, temp_folder_path)

    # Step 2: Delete the original folder with retries in case of file locks
    delete_folder_with_retries(folder_path)

    # Step 3: Rename the duplicated folder to the original name with retries
    rename_folder_with_retries(temp_folder_path, folder_path)

def button_update_title_and_path (url_folder_path, yaml_file_path):
    """Updates the title and hyperlink fields in a YAML file based on user input.

    Args:
        url_folder_path (str): The directory where the YAML file is located.
        yaml_file_path (str): The full path to the YAML file.

    Returns:
        list: A list containing the updated title and hyperlink values.

    Raises:
        SystemExit: If the user cancels the form or leaves required fields empty.
        Exception: If the YAML file cannot be modified.
    """
    # Read the current content_new of the script
    with open(yaml_file_path, 'r') as file:
        content_current = file.readlines()
        content_new = list(content_current)

    # Define Renaming Rules (UI FORM)
    # https://revitpythonwrapper.readthedocs.io/en/latest/ui/forms.html?highlight=forms#flexform
    components = [Label('Button Name:'),                    TextBox('button_name', content_new[0].split(": ", 1)[1][:-1]),
                  Label('URL, Directory or File Path:'),    TextBox('button_url', content_new[1].split(": ", 1)[1][1:-1]),
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
    content_new[0] = assign_name_format
    content_new[1] = assign_url_format

    if content_current == content_new:
        forms.alert('No changes made. Please Try Again', exitscript=True)

    try:
        # Write the modified content_new back to the script
        with open(yaml_file_path, 'w') as file:
            file.writelines(content_new)
    except Exception as e:
         # Alert on any exception
         forms.alert('Yaml file could not be modified. Please try again. Error: {e}', exitscript=True)

    return [assign_name, assign_url]
