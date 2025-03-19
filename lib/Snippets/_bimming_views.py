# -*- coding: utf-8 -*-

# Imports
#==================================================
from Autodesk.Revit.DB import *
import math
from math import degrees, atan2

# Variables
#==================================================
app   = __revit__.Application
uidoc = __revit__.ActiveUIDocument
doc   = __revit__.ActiveUIDocument.Document #type:Document

# Reusable Snippets

def get_existing_3d_view_type(view_type_name):
    """Retrieves a 3D view family type by its name.

    Args:
        view_type_name (str): The name of the 3D view type to search for.

    Returns:
        ViewFamilyType or None: The matching 3D view family type, or None if not found.
    """
    collector = FilteredElementCollector(doc).OfClass(ViewFamilyType)
    for vft in collector:
        name_param = vft.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString()
        if vft.ViewFamily == ViewFamily.ThreeDimensional and name_param == view_type_name:
            return vft
    return None

def GetFilterIds(view):
    """Gets the filter IDs applied to a given view.

    Args:
        view (View): The view from which to retrieve filter IDs.

    Returns:
        list or None: A list of filter IDs if filters are applied, None otherwise.
    """
    try:
        filterIds = view.GetFilters()
    except Exception:
        filterIds = None
    return filterIds

def get_view_type_name(doc, view):
    """Gets the name of the view type for a given view.

    Args:
        doc (Document): The active Revit document.
        view (View): The view whose type name needs to be retrieved.

    Returns:
        str or None: The name of the view type if found, None otherwise.
    """
    view_type = doc.GetElement(view.GetTypeId())  # Get ViewFamilyType element
    if view_type:
        return view_type.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString()  # Get name
    return None

def get_section_box(doc, view):
    """Collect all dependent elements of a view that belong to the OST_SectionBox category."""
    if isinstance(view, View):
        # Get all dependent element IDs of the view
        dependent_element_ids = view.GetDependentElements(None)

        # Filter dependent elements by the OST_SectionBox category
        section_boxes = []
        for element_id in dependent_element_ids:
            element = doc.GetElement(element_id)
            if element and element.Category and element.Category.Id.IntegerValue == int(BuiltInCategory.OST_SectionBox):
                section_boxes.append(element)

        return section_boxes
    else:
        raise ValueError("The provided element is not a valid view.")

def get_plan_view_rotation(view):
    """Returns the rotation angle of a Plan View in degrees."""
    if not isinstance(view, ViewPlan):
        return None  # Not a Plan View

    right_direction = view.RightDirection  # XYZ vector
    angle_radians = math.atan2(right_direction.Y, right_direction.X)  # Calculate angle
    angle_degrees = math.degrees(angle_radians)  # Convert to degrees

    return angle_degrees if angle_degrees >= 0 else angle_degrees + 360  # Normalize to 0-360°

def get_detail_view_rotation(view):
    """Returns the rotation angle of a Detail View in degrees."""
    if not view or not hasattr(view, "CropBox"):
        return None  # Ensure the view has a CropBox property

    transform = view.CropBox.Transform
    x_axis = transform.BasisX

    angle_radians = atan2(x_axis.Y, x_axis.X)
    angle_degrees = round(degrees(angle_radians), 12)  # Round to 12 decimals

    return angle_degrees

def get_plan_view_rotation1(view):
    """Returns the rotation angle of a Plan View in degrees, including Callout Views."""
    if not isinstance(view, ViewPlan):
        return None  # Not a Plan View

    # If it's a callout view, we need to get the parent view's rotation
    if hasattr(view, 'ViewType') and view.ViewType == 4:  # ViewType.Callout is typically 4
        parent_view = view.GetPrimaryViewId()
        if parent_view:
            parent_view_element = view.Document.GetElement(parent_view)
            if isinstance(parent_view_element, ViewPlan):
                view = parent_view_element  # Set the view to be the parent plan view

    # Get the RightDirection vector
    right_direction = view.RightDirection  # XYZ vector
    angle_radians = math.atan2(right_direction.Y, right_direction.X)  # Calculate angle
    angle_degrees = math.degrees(angle_radians)  # Convert to degrees

    # Normalize to 0-360 degrees
    return angle_degrees if angle_degrees >= 0 else angle_degrees + 360


def get_view_range_points(view):
    """Returns a dictionary of XYZ points (0,0,Z) for the View Range of a Plan View."""
    if not isinstance(view, ViewPlan):
        return None  # Not a Plan View

    view_range = view.GetViewRange()
    doc = view.Document

    def get_plane_point(plane):
        """Helper function to return XYZ(0,0,Z) for a given plane."""
        level_id = view_range.GetLevelId(plane)
        level = doc.GetElement(level_id)
        if level:
            return XYZ(0, 0, level.Elevation + view_range.GetOffset(plane))
        return None

    return {
        "TopClipPlane": get_plane_point(PlanViewPlane.TopClipPlane),
        "CutPlane": get_plane_point(PlanViewPlane.CutPlane),
        "BottomClipPlane": get_plane_point(PlanViewPlane.BottomClipPlane),
        "ViewDepthPlane": get_plane_point(PlanViewPlane.ViewDepthPlane)
    }

# dic_view_range = get_view_range_points(active_view)
# cut_plane = dic_view_range['CutPlane']
# view_depth = dic_view_range['ViewDepthPlane']

def open_3d_view_by_id(doc, uidoc, view_id):
    """
    Opens a 3D view by its ID and brings it to the front.

    Args:
        doc: The active Revit document.
        uidoc: The active Revit UI document.
        view_id (ElementId): The ID of the 3D view to open.

    Returns:
        bool: True if the view was found and activated, False otherwise.
    """
    # Get the 3D view by ID
    view_3d = doc.GetElement(view_id)

    # If the view exists and is a View3D, activate it
    if isinstance(view_3d, View3D):
        uidoc.ActiveView = view_3d
        return True

    return False