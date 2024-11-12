# -*- coding: utf-8 -*-
__title__   = "Set Override Graphics"
__doc__     = """Version = 1.0
Date    = 15.06.2024
________________________________________________________________
Description:

Module 2. Exercise 1
________________________________________________________________
Author: Maximo Cubero"""

from types import ObjectType

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝
#==================================================
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

#Homework 1

# public void ElementOverride()
# {
#     Document doc = this.ActiveUIDocument.Document;
#     UIDocument uidoc = this.ActiveUIDocument;
#     ElementId id = uidoc.Selection.PickObject(ObjectType.Element,"Select an element").ElementId;
#     OverrideGraphicSettings ogs = new OverrideGraphicSettings();
#     ogs.SetProjectionLineColor(new Color(0,255,0));
#     using (Transaction t = new Transaction(doc,"Set Element Override"))
#     {
#         t.Start();
#         doc.ActiveView.SetElementOverrides(id, ogs);
#         t.Commit();
#     }
# }

def ElementOverride():

    el_id = uidoc.Selection.PickObject(ObjectType.Element,"Select an element").ElementId
    ogs = OverrideGraphicSettings()
    ogs.SetProjectionLineColor(Color(0,255,0))
    t = Transaction(doc,"Set Element Override")
    t.Start()
    doc.ActiveView.SetElementOverrides(el_id, ogs)
    t.Commit()

ElementOverride()