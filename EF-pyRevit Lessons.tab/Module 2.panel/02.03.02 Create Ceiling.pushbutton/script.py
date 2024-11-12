# -*- coding: utf-8 -*-
__title__   = "Create Ceiling"
__doc__     = """Version = 1.0
Date    = 15.06.2024
________________________________________________________________
Description:

Module 2. Exercise 1
________________________________________________________________
Author: Maximo Cubero"""



# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝
#==================================================
from types import ObjectType
# Regular + Autodesk
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI.Selection import *
# pyRevit
from pyrevit import revit, forms

# .NET Imports (You often need List import)
import clr
clr.AddReference("System")
from System.Collections.Generic import List


# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝
#==================================================
app    = __revit__.Application
uidoc  = __revit__.ActiveUIDocument
doc    = __revit__.ActiveUIDocument.Document #type:Document


# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝
#==================================================

#Homework 2

# Ceiling CreateCeilingAtElevation(Document document, Level level, double elevation)
# {
#    XYZ first = new XYZ(0, 0, 0);
#    XYZ second = new XYZ(20, 0, 0);
#    XYZ third = new XYZ(20, 15, 0);
#    XYZ fourth = new XYZ(0, 15, 0);
#    CurveLoop profile = new CurveLoop();
#    profile.Append(Line.CreateBound(first, second));
#    profile.Append(Line.CreateBound(second, third));
#    profile.Append(Line.CreateBound(third, fourth));
#    profile.Append(Line.CreateBound(fourth, first));
#
#    var ceiling = Ceiling.Create(document, new List<CurveLoop> { profile }, ElementId.InvalidElementId, level.Id);
#    Parameter param = ceiling.get_Parameter(BuiltInParameter.CEILING_HEIGHTABOVELEVEL_PARAM);
#    param.Set(elevation);
#
#    return ceiling;
# }

def CreateCeilingAtElevation(document, _level, elevation):

   first  = XYZ(0, 0, 0)
   second = XYZ(20, 0, 0)
   third  = XYZ(20, 15, 0)
   fourth = XYZ(0, 15, 0)
   profile = CurveLoop()
   profile.Append(Line.CreateBound(first, second))
   profile.Append(Line.CreateBound(second, third))
   profile.Append(Line.CreateBound(third, fourth))
   profile.Append(Line.CreateBound(fourth, first))

   ceiling = Ceiling.Create(document, List[CurveLoop]([profile]), ElementId(-1), _level.Id)
   param = ceiling.get_Parameter(BuiltInParameter.CEILING_HEIGHTABOVELEVEL_PARAM)
   param.Set(elevation)

   return ceiling

level = FilteredElementCollector(doc).OfClass(Level).FirstElement()

t = Transaction(doc, "Create Ceiling")
t.Start()
CreateCeilingAtElevation(doc, level, 10 )
t.Commit()