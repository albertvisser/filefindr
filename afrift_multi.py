# -*- coding: utf-8 -*-

# als je %L opgeeft in het Parameters veld bij de definitie van een TC button of menu item geeft-ie de
# geselecteerde file- en directorynamen door aan het aangeroepen programma
import sys
from afrift.afrift_gui import MainFrame

if len(sys.argv) > 1:
    MainFrame(apptype="multi", fnaam=sys.argv[1])
else:
    MainFrame(apptype="multi")
