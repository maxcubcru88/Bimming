# -*- coding: utf-8 -*-


# Imports
#==================================================
from Autodesk.Revit.DB import *

# Variables
#==================================================
app   = __revit__.Application
uidoc = __revit__.ActiveUIDocument
doc   = __revit__.ActiveUIDocument.Document #type:Document

rvt_year = int(app.VersionNumber)

# Functions
#==================================================

def convert_internal_units(value, get_internal = True, units='mm'):
    #type: (float, bool, str) -> float
    """Function to convert Internal units to meters or vice versa.
    :param value:        Value to convert
    :param get_internal: True to get internal units, False to get Milimeters
    :param units:        Select desired Units: ['m', 'm2', 'cm', 'mm']
    :return:             Length in Internal units or Milimeters."""

    if rvt_year >= 2021:
        from Autodesk.Revit.DB import UnitTypeId
        if   units == 'm' : units = UnitTypeId.Meters
        elif units == "m2": units = UnitTypeId.SquareMeters
        elif units == 'cm': units = UnitTypeId.Centimeters
        elif units == "mm": units = UnitTypeId.Millimeters
        elif units == "degrees": units = UnitTypeId.Degrees
    else:
        from Autodesk.Revit.DB import DisplayUnitType
        if   units == 'm' : units = DisplayUnitType.DUT_METERS
        elif units == "m2": units = DisplayUnitType.DUT_SQUARE_METERS
        elif units == "cm": units = DisplayUnitType.DUT_CENTIMETERS
        elif units == "mm": units = DisplayUnitType.DUT_MILLIMETERS

    if get_internal:
        return UnitUtils.ConvertToInternalUnits(value, units)
    return UnitUtils.ConvertFromInternalUnits(value, units)