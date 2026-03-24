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

def get_views_to_delete(doc, prefix_to_keep="MX_", view_types_to_keep=None):
    """
    Returns a list of View Ids that are safe to delete based on multiple filters.

    Args:
        doc: Revit document
        prefix_to_keep (str): Views starting with this prefix will NOT be deleted
        view_types_to_keep (set): Set of ViewType enums to preserve

    Returns:
        List[ElementId]: View Ids sorted so dependent views are deleted first
    """

    # Ensure we always work with a set (avoids mutable default argument issues)
    if view_types_to_keep is None:
        view_types_to_keep = set()

    views = FilteredElementCollector(doc).OfClass(View).ToElements()
    views_to_delete = []

    for v in views:

        # Skip splash screen sheet (special case)
        if isinstance(v, ViewSheet) and v.Name.strip().replace(" ", "").lower() == "splashscreen":
            continue

        # Skip view templates
        if v.IsTemplate:
            continue

        # Skip revision schedules inside titleblocks
        if hasattr(v, "IsTitleblockRevisionSchedule") and v.IsTitleblockRevisionSchedule:
            continue

        # Skip key schedules
        try:
            if v.ViewType == ViewType.Schedule and v.Definition.IsKeySchedule:
                continue
        except:
            pass

        # Skip views whose type is explicitly protected (custom view types)
        if v.ViewType in view_types_to_keep:
            continue

        # Skip views with protected prefix
        if prefix_to_keep and v.Name.startswith(prefix_to_keep):
            continue

        # Skip system/internal browser views
        if v.ViewType in (ViewType.ProjectBrowser, ViewType.SystemBrowser):
            continue

        # Skip views that cannot be printed (except schedules)
        if v.ViewType != ViewType.Schedule and not v.CanBePrinted:
            continue

        # If none of the "keep" conditions matched → mark for deletion
        views_to_delete.append(v)

    # ✅ Sort: dependent views first
    # Dependent views must be deleted before their parent views
    def is_dependent(v):
        try:
            return v.GetPrimaryViewId() != ElementId.InvalidElementId
        except:
            return False

    views_sorted = sorted(views_to_delete, key=lambda v: is_dependent(v), reverse=True)

    return [v.Id for v in views_sorted]

def get_cad_links_to_delete(doc):
    """Collect all ImportInstance (CAD links) to delete."""
    return [e.Id for e in FilteredElementCollector(doc)
            .OfClass(ImportInstance)
            .WhereElementIsNotElementType()
            .ToElements()]

def get_revit_links_to_delete(doc):
    """Collects only top-level Revit link types (excludes nested attachments)."""
    # Collect all link types in the document
    all_links = FilteredElementCollector(doc).OfClass(RevitLinkType).ToElements()

    # Filter for types that are NOT nested attachments
    return [link.Id for link in all_links if not link.IsNestedLink]

def get_images_to_delete(doc):
    """Collect all raster images to delete."""
    return [e.Id for e in FilteredElementCollector(doc)
            .OfCategory(BuiltInCategory.OST_RasterImages)
            .WhereElementIsElementType()
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

def get_data_schedules(list_schedules):
    """Collect data from schedule"""

    if not hasattr(list_schedules, "__iter__"):
        list_schedules = [list_schedules]

    result = {}
    for schedule in list_schedules:
        table = schedule.GetTableData().GetSectionData(SectionType.Body)
        schedule_name = Element.Name.GetValue(schedule)
        nRows = table.NumberOfRows
        nColumns = table.NumberOfColumns

        dataListRow = []
        for row in range(nRows):
            dataListColum = []
            for column in range(nColumns):
                dataListColum.append(
                    TableView.GetCellText(schedule, SectionType.Body, row, column)
                )
            dataListRow.append(dataListColum)

        result[schedule_name] = dataListRow

    return result