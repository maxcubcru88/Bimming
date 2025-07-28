# -*- coding: utf-8 -*-


# Imports
#==================================================
from Autodesk.Revit.DB import *
import csv
import codecs
import os
from Snippets._bimming_strings import *

# Variables
#==================================================
app   = __revit__.Application
uidoc = __revit__.ActiveUIDocument
doc   = __revit__.ActiveUIDocument.Document #type:Document

# Functions
#==================================================

def export_to_csv(file_path, data):
    """Exports the given data to a CSV file at the specified file path.

    Args:
        file_path (str): The path where the CSV file will be saved.
        data (list of lists): The data to write to the CSV file. Each inner list represents a row.

    Returns:
        str: The file path where the CSV file was saved.
    """
    # Open the file with codecs and utf-8 encoding
    with codecs.open(file_path, 'w', 'utf-8') as file:
        writer = csv.writer(file, lineterminator='\n')
        writer.writerows(data)
    return  file_path

def create_report_directory(folder_name="NEW DIRECTORY"):
    """Creates a directory with the specified folder name in the user's Documents folder if it doesn't already exist.

    Args:
        folder_name (str): The name of the folder to be created. Default is 'Bimming_Filter_Usage_Reports'.

    Returns:
        str: The full path of the created or existing directory.
    """
    # Get the user's Documents directory
    documents_folder = os.path.expanduser("~\\Documents\\{}".format(folder_name))

    # Check if the folder exists, if not, create it
    if not os.path.exists(documents_folder):
        os.makedirs(documents_folder)

    os.startfile(documents_folder)

    return documents_folder

import datetime

def generate_report_name(file_name):
    """Generates a report name by concatenating the file name with the current date and time.

    Args:
        file_name (str): The base file name.

    Returns:
        str: The formatted report name with the date and time.
        str: The formatted export date (YYYY-MM-DD).
        str: The formatted export time (HH:MM:SS).
    """
    # Get the current date and time
    now = datetime.datetime.now()

    # Format the date and time as 'YYYY-MM-DD_HH.MM.SS'
    formatted_datetime = now.strftime("%Y-%m-%d_%H.%M.%S")

    # Add export date and time to output_project_info (or return them)
    export_date = now.strftime("%Y-%m-%d")
    export_time = now.strftime("%H:%M:%S")

    # Concatenate the file name with the formatted date and time
    new_file_name = "{}_{}".format(file_name, formatted_datetime)

    # Return the new file name and export date/time
    return new_file_name, export_date, export_time


def get_project_info(doc, app):
    """Retrieves project information including file path, name, central file path, and export user.

    Args:
        doc (Document): The active Revit document.
        app (Application): The Revit application instance.

    Returns:
        list: A list of tuples containing project information.
    """
    model_path = doc.PathName
    output_project_info = [("PROJECT INFO", "")]

    output_project_info.append(("File Path", model_path))

    # Check if the document is workshared
    if doc.IsWorkshared:
        try:
            # Extract file info including the central path
            file_info = BasicFileInfo.Extract(model_path)

            # Get central model path
            model_path = file_info.CentralPath
            file_name = os.path.splitext(os.path.basename(model_path))[0]

            if not file_name:
                forms.alert('Save the model and try again.')
                sys.exit()

            central_path = file_info.CentralPath

        except Exception:
            # Handle detached central file cases
            file_name_detached = os.path.splitext(os.path.basename(model_path))[0]
            file_name = remove_detached_suffix(file_name_detached)
            central_path = "It is a detached model - No central file path found."
    else:
        file_name = os.path.splitext(os.path.basename(model_path))[0]
        central_path = "This document is not workshared."

    output_project_info.append(("File Name", file_name))
    output_project_info.append(("Central File Path", central_path))

    # Get the current user's name
    output_project_info.append(("Export by", app.Username))

    # Add an extra blank line
    output_project_info.append(("",""))

    return output_project_info