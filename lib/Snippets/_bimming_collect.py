# -*- coding: utf-8 -*-


# Imports
#==================================================
from Autodesk.Revit.DB import *

# Variables
#==================================================
app   = __revit__.Application
uidoc = __revit__.ActiveUIDocument
doc   = __revit__.ActiveUIDocument.Document #type:Document

# Functions
#==================================================

def get_nested_detail_items(doc):
    """
    Retrieves all nested detail items (subcomponents) inside other detail items in the given Revit document.

    Args:
        doc: The current Revit document.

    Returns:
        A dictionary where keys are detail item IDs and values are lists of nested component IDs.
    """
    detail_items = FilteredElementCollector(doc).OfCategory(
        BuiltInCategory.OST_DetailComponents).WhereElementIsNotElementType().ToElements()

    nested_items = []

    for detail_item in detail_items:
        if isinstance(detail_item, FamilyInstance):  # Ensure it's a FamilyInstance
            dependent_ids = detail_item.GetSubComponentIds()  # Get ElementId list
            nested_items.extend(dependent_ids)

    return nested_items

def get_bounding_box_points(bounding_box):
    """
    Retrieves the 8 corner points of a bounding box.

    Parameters:
    bounding_box (BoundingBoxXYZ): The bounding box from which to extract the corner points.

    Returns:
    list: A list of 8 XYZ points representing the corners of the bounding box, or None if the bounding box is not valid.
    """
    if bounding_box:
        min_point = bounding_box.Min  # Minimum point (XYZ)
        max_point = bounding_box.Max  # Maximum point (XYZ)

        # The bounding box has 8 points in total (corners)
        points = [
            min_point,
            XYZ(min_point.X, min_point.Y, max_point.Z),  # (minX, minY, maxZ)
            XYZ(min_point.X, max_point.Y, min_point.Z),  # (minX, maxY, minZ)
            XYZ(min_point.X, max_point.Y, max_point.Z),  # (minX, maxY, maxZ)
            XYZ(max_point.X, min_point.Y, min_point.Z),  # (maxX, minY, minZ)
            XYZ(max_point.X, min_point.Y, max_point.Z),  # (maxX, minY, maxZ)
            XYZ(max_point.X, max_point.Y, min_point.Z),  # (maxX, maxY, minZ)
            max_point  # (maxX, maxY, maxZ)
        ]

        return points
    else:
        return None