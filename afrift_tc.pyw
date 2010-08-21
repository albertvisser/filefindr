#! /usr/bin/env python 

# als je %L opgeeft in het Parameters veld bij de definitie van een TC button of menu item geeft-ie de
# geselecteerde file- en directorynamen door aan het aangeroepen programma
import sys
from afrift.afrift_gui import MainFrame

MainFrame(apptype="Multi",data=sys.argv)
