# -*- coding: utf-8 -*-


# Imports
#==================================================
from Autodesk.Revit.DB import *
from collections import defaultdict

# Variables
#==================================================
app   = __revit__.Application
uidoc = __revit__.ActiveUIDocument
doc   = __revit__.ActiveUIDocument.Document #type:Document

# Functions
#==================================================

from Autodesk.Revit.DB import BuiltInCategory

def collect_all_group_members(doc, group):
    """Recursively collects all members of a detail group, including nested detail groups and filtering for specific categories.

    Args:
        doc (Document): The active Revit document.
        group (Group): The Revit detail group element.

    Returns:
        list: A list of elements in the group, including nested detail groups and specified categories.
    """
    allowed_categories = {
        int(BuiltInCategory.OST_DetailComponents),
        int(BuiltInCategory.OST_Lines),
        int(BuiltInCategory.OST_TextNotes),
        int(BuiltInCategory.OST_InsulationLines),
        int(BuiltInCategory.OST_GenericAnnotation),
        int(BuiltInCategory.OST_RevisionClouds),
        int(BuiltInCategory.OST_IOSDetailGroups)  # Include detail groups
    }

    all_members = []
    group_members = group.GetMemberIds()  # Get direct members of the group

    for member_id in group_members:
        member = doc.GetElement(member_id)

        # Include detail groups and other allowed categories
        if member.Category and member.Category.Id.IntegerValue in allowed_categories:
            all_members.append(member)

        # If the member is a detail group, recurse into it
        if member.Category and member.Category.Id.IntegerValue == int(BuiltInCategory.OST_IOSDetailGroups):
            all_members.extend(collect_all_group_members(doc, member))

    return all_members
