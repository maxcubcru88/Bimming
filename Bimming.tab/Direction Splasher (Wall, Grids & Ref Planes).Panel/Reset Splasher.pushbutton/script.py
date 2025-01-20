# -*- coding: utf-8 -*-
__title__ = "Reset\nSplasher"
__doc__ = """Resets graphic overrides for walls, reference planes, and grids in the active view.

Author: Máximo Cubero"""

# IMPORTS
#==================================================
# Regular + Autodesk
from Autodesk.Revit.DB import *

# VARIABLES
#==================================================
doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app   = __revit__.Application

# MAIN
#==================================================

def set_graphics_override_direction(line_weight = -1 ,
                                    color_lines = Color.InvalidColorValue,
                                    color_surfaces = Color.InvalidColorValue,
                                    fill_pattern_id = ElementId.InvalidElementId):

    # Color.InvalidColorValue       -> means no override for the color is set.
    # ElementId.InvalidElementId    -> means no override for the fill pattern is set

    # Create an OverrideGraphicSettings object
    override_settings = OverrideGraphicSettings()

    # Set weight override Ref Planes
    override_settings.SetCutLineWeight(line_weight)
    override_settings.SetProjectionLineWeight(line_weight)

    # Set color override lines
    override_settings.SetProjectionLineColor(color_lines)
    override_settings.SetCutLineColor(color_lines)

    # Set color override surfaces
    override_settings.SetSurfaceBackgroundPatternColor(color_surfaces)
    override_settings.SetSurfaceForegroundPatternColor(color_surfaces)
    override_settings.SetCutBackgroundPatternColor(color_surfaces)
    override_settings.SetCutForegroundPatternColor(color_surfaces)

    override_settings.SetSurfaceBackgroundPatternId(fill_pattern_id)
    override_settings.SetSurfaceForegroundPatternId(fill_pattern_id)
    override_settings.SetCutBackgroundPatternId(fill_pattern_id)
    override_settings.SetCutForegroundPatternId(fill_pattern_id)

    return override_settings

#1️⃣ Select Wall, Grid or Ref Planes

all_walls        = FilteredElementCollector(doc).OfClass(Wall).ToElements()
all_grids        = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Grids).WhereElementIsNotElementType().ToElements()
all_ref_planes   = FilteredElementCollector(doc, doc.ActiveView.Id).OfClass(ReferencePlane).ToElements()

collector = list(all_walls) + list(all_grids) + list(all_ref_planes)

# RESET GRAPHICS FOR ALL THE ELEMENTS

t = Transaction(doc, 'MC-Elements Splasher')
t.Start()

for el in collector:
    settings = set_graphics_override_direction()
    doc.ActiveView.SetElementOverrides(el.Id, settings)

t.Commit()