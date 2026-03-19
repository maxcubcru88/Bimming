# -*- coding: utf-8 -*-

# Imports
#==================================================
from Autodesk.Revit.DB import *

from pyrevit import revit, DB
from pyrevit import script

# Variables
#==================================================
app   = __revit__.Application
uidoc = __revit__.ActiveUIDocument
doc   = __revit__.ActiveUIDocument.Document #type:Document

# Reusable Snippets

logger = script.get_logger()

def removeallemptyelevationmarkers():
    with revit.Transaction('KCA-Remove all elevation markers'):
        # print('REMOVING ELEVATION MARKERS...\n')
        elevmarkers = DB.FilteredElementCollector(revit.doc)\
                        .OfClass(DB.ElevationMarker)\
                        .WhereElementIsNotElementType()\
                        .ToElements()

        for em in elevmarkers:
            if em.CurrentViewCount == 0:
                # emtype = revit.doc.GetElement(em.GetTypeId())
                # print('ID: {0}\tELEVATION TYPE: {1}'
                #       .format(em.Id,
                #               revit.query.get_name(emtype)))
                try:
                    revit.doc.Delete(em.Id)
                except Exception as e:
                    logger.error('- Failed to delete marker: {} | {}'
                                 .format(em.Id, e))
                    continue

def delete_unused_view_templates(doc):
    """
    Deletes all View Templates that are not assigned to any view.
    Returns number of deleted templates.
    """

    views = FilteredElementCollector(doc)\
        .OfClass(View)\
        .WhereElementIsNotElementType()\
        .ToElements()

    template_ids = set()
    used_template_ids = set()

    # Collect all templates
    for v in views:
        if v.IsTemplate:
            template_ids.add(v.Id)

    # Collect used templates
    for v in views:
        if not v.IsTemplate:
            tid = v.ViewTemplateId
            if tid and tid != ElementId.InvalidElementId:
                used_template_ids.add(tid)

    # Determine unused
    unused_template_ids = list(template_ids - used_template_ids)

    if not unused_template_ids:
        # print("No unused view templates to delete.")
        return 0

    # print("Deleting view templates:",
    #       [doc.GetElement(tid).Name for tid in unused_template_ids])

    # --- DELETE ---
    t = Transaction(doc, "KCA-Delete unused view templates")
    t.Start()

    deleted = 0
    for tid in unused_template_ids:
        try:
            doc.Delete(tid)
            deleted += 1
        except Exception as e:
            print("Failed to delete {}: {}".format(tid, e))

    t.Commit()

    return deleted