"""Opens the issue tracker on github to report bugs and issues."""
from pyrevit import script
from pyrevit.versionmgr import urls

url = "https://github.com/maxcubcru88/Bimming/issues"
script.open_url(url)
