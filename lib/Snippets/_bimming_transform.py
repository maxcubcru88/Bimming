# -*- coding: utf-8 -*-

# Imports
#==================================================
from Autodesk.Revit.DB import *
import math

# Variables
#==================================================
app   = __revit__.Application
uidoc = __revit__.ActiveUIDocument
doc   = __revit__.ActiveUIDocument.Document #type:Document

def move_element(doc, element, pointA, pointB):
    """Moves an element from pointA to pointB."""
    translation_vector = pointB - pointA  # Compute translation vector
    ElementTransformUtils.MoveElement(doc, element.Id, translation_vector)

def move_element_xy(doc, element, pointA, pointB):
    """Moves an element from pointA to pointB but only in the XY plane."""
    translation_vector = XYZ(pointB.X - pointA.X, pointB.Y - pointA.Y, 0)  # Ignore Z movement
    ElementTransformUtils.MoveElement(doc, element.Id, translation_vector)

def rotate_element(doc, element, pivot, axis, angle_degrees):
    """
    Rotates a Revit element around a specified pivot point and axis by a given angle.

    Parameters:
    doc (Document): The current Revit document.
    element (Element): The element to be rotated.
    pivot (XYZ): The point around which the element will be rotated.
    axis (XYZ): The axis along which the rotation will occur.
    angle_degrees (float): The rotation angle in degrees.

    Returns:
    None
    """
    angle_radians = math.radians(angle_degrees)  # Convert degrees to radians
    rotation_axis = Line.CreateUnbound(pivot, axis)  # Define rotation axis
    ElementTransformUtils.RotateElement(doc, element.Id, rotation_axis, angle_radians)

def rotate_bounding_box(bounding_box, pivot_point, rotation_axis, angle_degrees):
    """
    Rotates the bounding box around a specified pivot point and axis by a given angle.

    Parameters:
    bounding_box (BoundingBoxXYZ): The original bounding box to rotate.
    pivot_point (XYZ): The point around which the bounding box will be rotated.
    rotation_axis (XYZ): The axis around which the rotation will occur.
    angle_degrees (float): The rotation angle in degrees.

    Returns:
    BoundingBoxXYZ: The new rotated bounding box.
    """
    # Create the rotation transform
    rotation_transform = Transform.CreateRotationAtPoint(rotation_axis, angle_degrees * (3.14159265358979 / 180),
                                                         pivot_point)

    # Get the corners of the bounding box
    min_point = bounding_box.Min
    max_point = bounding_box.Max

    # Define the 8 corners of the bounding box
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

    # Apply the rotation to all points
    rotated_points = [rotation_transform.OfPoint(point) for point in points]

    # Optionally, create a new bounding box with the rotated points
    min_rotated = XYZ(min(p.X for p in rotated_points), min(p.Y for p in rotated_points),
                      min(p.Z for p in rotated_points))
    max_rotated = XYZ(max(p.X for p in rotated_points), max(p.Y for p in rotated_points),
                      max(p.Z for p in rotated_points))

    rotated_bounding_box = BoundingBoxXYZ()
    rotated_bounding_box.Min = min_rotated
    rotated_bounding_box.Max = max_rotated

    return rotated_bounding_box


def adjust_bounding_box_z(bbox, new_min_z, new_max_z):
    """Modifies the Z-values of an existing BoundingBoxXYZ."""
    if not bbox:
        return None  # Ensure bbox is valid

    # Create new Min and Max with updated Z-values
    new_min = XYZ(bbox.Min.X, bbox.Min.Y, new_min_z)
    new_max = XYZ(bbox.Max.X, bbox.Max.Y, new_max_z)

    # Apply changes
    bbox.Min = new_min
    bbox.Max = new_max

    return bbox  # Return modified bounding box