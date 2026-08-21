# -*- coding: utf-8 -*-
__title__   = "Toggle\nTheme"
__doc__     = """Switches the Revit UI between Light and Dark theme.

Requires Revit 2024 or newer (UIThemeManager API was introduced in 2024).

Author: Maximo Cubero"""

__min_revit_ver__ = 2021
__max_revit_ver__ = 2026

# IMPORTS
#==================================================
import clr
from traceback import print_tb
clr.AddReference('System')
from pyrevit import forms
from Autodesk.Revit.UI import UIThemeManager, UITheme
from Snippets._bimcore_convert import *

# MAIN
#==================================================
if rvt_year < 2024:
    forms.alert(msg="Theme switching requires Revit 2024 or newer.", exitscript=True)

if UIThemeManager.CurrentTheme == UITheme.Dark:
    UIThemeManager.CurrentTheme = UITheme.Light
else:
    UIThemeManager.CurrentTheme = UITheme.Dark
