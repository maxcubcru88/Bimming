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

def get_views_to_delete(doc, prefix_to_keep="MX_"):
    """
    Collects all views in the model that are safe to delete, excluding:
    - Revision Schedule views
    - View Templates
    - Views whose name starts with prefix_to_keep
    - Splashscreen sheet
    - System / Project Browser views
    - Views that cannot be printed

    Returns a list of ElementIds.
    """
    views = FilteredElementCollector(doc).OfClass(View).ToElements()

    views_to_delete = []

    for v in views:

        # --- EXCLUSIONS ---

        # Splashscreen sheet
        if isinstance(v, ViewSheet) and v.Name == "Splashscreen":
            continue

        # View Templates
        if v.IsTemplate:
            continue

        # Revision Schedules
        if hasattr(v, "IsTitleblockRevisionSchedule") and v.IsTitleblockRevisionSchedule:
            continue

        # Key Schedules
        try:
            if v.ViewType == ViewType.Schedule and v.Definition.IsKeySchedule:
                continue
        except:
            pass

        # Prefix-based protection
        if prefix_to_keep and v.Name.startswith(prefix_to_keep):
            continue

        # System views
        if v.ViewType in (ViewType.ProjectBrowser, ViewType.SystemBrowser):
            continue

        # Keep schedules even if not printable
        if v.ViewType != ViewType.Schedule and not v.CanBePrinted:
            continue

        views_to_delete.append(v.Id)

    return views_to_delete

def get_cad_links_to_delete(doc):
    """Collect all ImportInstance (CAD links) to delete."""
    return [e.Id for e in FilteredElementCollector(doc)
            .OfClass(ImportInstance)
            .WhereElementIsNotElementType()
            .ToElements()]

def get_revit_links_to_delete(doc):
    """Collect all Revit links to delete (instances, not types)."""
    return [e.Id for e in FilteredElementCollector(doc)
            .OfCategory(BuiltInCategory.OST_RvtLinks)
            .WhereElementIsNotElementType()  # Use instance, not type
            .ToElements()]

def get_images_to_delete(doc):
    """Collect all raster images to delete."""
    return [e.Id for e in FilteredElementCollector(doc)
            .OfCategory(BuiltInCategory.OST_RasterImages)
            .WhereElementIsNotElementType()
            .ToElements()]

def get_unused_scope_boxes(doc):
    """
    Returns a list of unused ScopeBox ElementIds.
    Checks Views, Levels, Grids, and Reference Planes.
    """
    # Collect all scope boxes
    scope_boxes = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_VolumeOfInterest).WhereElementIsNotElementType().ToElements()
    if not scope_boxes:
        return []

    used_scope_box_ids = set()

    # --- Collect all related elements ---
    views = FilteredElementCollector(doc).OfClass(View).ToElements()
    levels = FilteredElementCollector(doc).OfClass(Level).ToElements()
    grids = FilteredElementCollector(doc).OfClass(Grid).ToElements()
    reference_planes = FilteredElementCollector(doc).OfClass(ReferencePlane).ToElements()

    # --- Views ---
    for v in views:
        if v.IsTemplate:
            continue
        try:
            sb_id = v.get_Parameter(BuiltInParameter.VIEWER_VOLUME_OF_INTEREST_CROP).AsElementId()
            if sb_id != ElementId.InvalidElementId:
                used_scope_box_ids.add(sb_id)
        except:
            continue

    # --- Levels ---
    for level in levels:
        try:
            sb_id = level.get_Parameter(BuiltInParameter.DATUM_VOLUME_OF_INTEREST).AsElementId()
            if sb_id != ElementId.InvalidElementId:
                used_scope_box_ids.add(sb_id)
        except:
            continue

    # --- Grids ---
    for grid in grids:
        try:
            sb_id = grid.get_Parameter(BuiltInParameter.DATUM_VOLUME_OF_INTEREST).AsElementId()
            if sb_id != ElementId.InvalidElementId:
                used_scope_box_ids.add(sb_id)
        except:
            continue

    # --- Reference Planes ---
    for rp in reference_planes:
        try:
            sb_id = rp.get_Parameter(BuiltInParameter.DATUM_VOLUME_OF_INTEREST).AsElementId()
            if sb_id != ElementId.InvalidElementId:
                used_scope_box_ids.add(sb_id)
        except:
            continue

    # --- Determine unused scope boxes ---
    unused_scope_boxes = [sb for sb in scope_boxes if sb.Id not in used_scope_box_ids]
    unused_scope_boxes_sorted = sorted(unused_scope_boxes, key=lambda sb: sb.Name)

    return [sb.Id for sb in unused_scope_boxes_sorted]