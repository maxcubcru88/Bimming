# -*- coding: utf-8 -*-

__title__ = "Power BI\nTemplate"
__doc__ = """Download the Power BI Template.

Author: Máximo Cubero"""

#__helpurl__ = "https://www.bimming.uk"
__min_revit_ver__ = 2021
__max_revit_ver__ = 2025
#__context__ = 'zero-doc'
#__highlight__ = 'new'

from pyrevit import script

url = 'https://github.com/maxcubcru88/Bimming/raw/refs/heads/main/Support%20Files/Bimming-PowerBI-Filter%20Usage%20v1.0.7.pbix'

script.open_url(url)
