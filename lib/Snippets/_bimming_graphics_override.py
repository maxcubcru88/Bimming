# -*- coding: utf-8 -*-

# Imports
#==================================================
import random
import math
from decimal import Decimal, getcontext, ROUND_HALF_UP
from Snippets._bimming_convert import *
from Autodesk.Revit.DB import *
from pyrevit import forms
from collections import defaultdict

# Variables
#==================================================
app   = __revit__.Application
uidoc = __revit__.ActiveUIDocument
doc   = __revit__.ActiveUIDocument.Document #type:Document

# Reusable Snippets

def set_graphics_override_direction(line_weight = -1 ,
                                    color_lines = Color.InvalidColorValue,
                                    color_surfaces = Color.InvalidColorValue,
                                    fill_pattern_id = ElementId.InvalidElementId):
    """Creates and returns an OverrideGraphicSettings object with specified overrides.

    Args:
        line_weight (int, optional): Line weight for projection and cut lines. Defaults to -1 (no override).
        color_lines (Color, optional): Color for projection and cut lines. Defaults to Color.InvalidColorValue.
        color_surfaces (Color, optional): Color for surface and cut patterns. Defaults to Color.InvalidColorValue.
        fill_pattern_id (ElementId, optional): Fill pattern ID for surface and cut patterns. Defaults to ElementId.InvalidElementId.

    Returns:
        OverrideGraphicSettings: The configured override settings object.

    Notes:
        - `Color.InvalidColorValue` means no override for colors.
        - `ElementId.InvalidElementId` means no override for fill patterns.
    """
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

def generate_random_colors(n):
    """Generates a list of random Revit colors.

    Args:
        n (int): The number of colors to generate.

    Returns:
        list[Color]: A list of Revit Color objects with random RGB values.
    """
    colors = []
    for _ in range(n):
        # Generate random RGB values
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)

        # Create Revit Color and add to list
        color = Color(r, g, b)
        colors.append(color)

    return colors


def lighten_color(color, factor=0.2):
    """
    Lightens the given color by increasing its RGB values.

    Args:
        color (Color): Autodesk.Revit.DB.Color object.
        factor (float, optional): Percentage (0 to 1) of how much lighter the color should be.
                                  Default is 0.2 (20% lighter).

    Returns:
        Color: New Autodesk.Revit.DB.Color object with lightened RGB values.
    """
    # Ensure the factor is between 0 and 1
    factor = max(0, min(factor, 1))

    # Extract original RGB values
    r, g, b = color.Red, color.Green, color.Blue

    # Lighten the color by increasing its RGB values proportionally
    new_r = min(int(r + (255 - r) * factor), 255)
    new_g = min(int(g + (255 - g) * factor), 255)
    new_b = min(int(b + (255 - b) * factor), 255)

    # Return the new lightened color
    return Color(new_r, new_g, new_b)