# -*- coding: utf-8 -*-


# Imports
#==================================================
import Autodesk
from Autodesk.Revit.DB import *

# Variables
#==================================================
app   = __revit__.Application
uidoc = __revit__.ActiveUIDocument
doc   = __revit__.ActiveUIDocument.Document #type:Document

# Functions
#==================================================

def place_family_at_point(doc, family_symbol, point):
    """
    Places a family instance at a specified point in the Revit document.

    Parameters:
    doc (Document): The current Revit document.
    family_symbol (FamilySymbol): The family symbol used to create the instance.
    point (XYZ): The point where the family instance will be placed.

    Returns:
    FamilyInstance: The created family instance at the specified point.
    """
    # Start a transaction to modify the document
    with Transaction(doc, "Place Family") as t:
        t.Start()

        # Create an instance of the family at the given point
        family_instance = doc.Create.NewFamilyInstance(
            point, family_symbol, Autodesk.Revit.DB.Structure.StructuralType.NonStructural)

        t.Commit()

    return family_instance