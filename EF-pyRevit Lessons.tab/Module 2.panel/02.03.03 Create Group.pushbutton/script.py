# -*- coding: utf-8 -*-
__title__   = "Create Group"
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

#Homework 3

# public void MakeGroup(Document document)
# {
#     Group group = null;
#     UIDocument uidoc = new UIDocument(document);
#     ICollection<ElementId> selectedIds = uidoc.Selection.GetElementIds();
#
#     if (selectedIds.Count > 0)
#     {
#         // Group all selected elements
#         group = document.Create.NewGroup(selectedIds);
#         // Initially, the group has a generic name, such as Group 1\. It can be modified by changing the name of the group type as follows:
#         // Change the default group name to a new name "MyGroup"
#         group.GroupType.Name = "MyGroup";
#     }
# }

def MakeGroup(document):

   #group = null
   selectedIds = uidoc.Selection.GetElementIds()

   if (selectedIds.Count > 0):

      # Group all selected elements
      group = document.Create.NewGroup(selectedIds)
      # Initially, the group has a generic name, such as Group 1.
      # It can be modified by changing the name of the group type as follows:
      # Change the default group name to a new name "MyGroup"
      group.GroupType.Name = "MyGroup"

t = Transaction(doc, "Make Group")
t.Start()
MakeGroup(doc)
t.Commit()