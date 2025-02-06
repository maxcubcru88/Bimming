# -*- coding: utf-8 -*-

# Imports
#==================================================
from Snippets._bimming_vectors import  *

# Variables
#==================================================
app   = __revit__.Application
uidoc = __revit__.ActiveUIDocument
doc   = __revit__.ActiveUIDocument.Document #type:Document

# Reusable Snippets
#==================================================
def get_scope_box_angle(scope_box):
    """Returns the rotation angle of a scope box relative to the X-axis.

    The angle is measured in degrees and ranges from -180 to 180.
    A positive value indicates counterclockwise rotation, while a
    negative value indicates clockwise rotation.

    Args:
        scope_box (Element): The scope box whose angle is to be determined.

    Returns:
        float: The angle of the scope box in degrees.
    """
    options = Options()
    options.DetailLevel = ViewDetailLevel.Undefined

    geom = scope_box.Geometry[options]

    direction = []
    for line in geom:
        vector = line.Direction
        if not (is_parallel_to_z(vector)):
            direction.append(vector)
    scope_box_angle = get_angles_against_x(direction)[4]
    if direction[4].X <= 0:
        return scope_box_angle
    else:
        return -scope_box_angle

# Function to rotate scope box
def rotate_scope_box(scope_box, angle_degrees):
    """Rotates a given scope box by the specified angle in degrees.

    Args:
        scope_box (Element): The scope box to rotate.
        angle_degrees (float): The rotation angle in degrees.

    Raises:
        Exception: If the rotation operation fails.
    """
    # Get the bounding box of the scope box
    bounding_box = scope_box.get_BoundingBox(doc.ActiveView)

    # Calculate the center point of the bounding box
    center_point = (bounding_box.Min + bounding_box.Max) / 2.0

    # Create a rotation axis
    axis = Line.CreateBound(center_point, XYZ(center_point.X, center_point.Y, center_point.Z + 1))

    # Convert angle from degrees to radians
    angle_radians = math.radians(angle_degrees)

    # Rotate the scope box
    ElementTransformUtils.RotateElement(doc, scope_box.Id, axis, angle_radians)