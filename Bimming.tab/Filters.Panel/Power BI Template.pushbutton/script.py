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

url = 'https://www.dropbox.com/scl/fi/d2lceh98ylvc407qclahm/Bimming-PowerBi-Template-Filter-Usage-v04.pbix?rlkey=giuch68yqu3kgjejlu4v039xp&dl=1'

script.open_url(url)
