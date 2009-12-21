# -*- coding: latin1 -*-

# als je %L opgeeft in het Parameters veld bij de definitie van een TC button of menu item geeft-ie de
# geselecteerde file- en directorynamen door aan het aangeroepen programma
import sys
from afrift_gui import MainFrame

MainFrame(apptype="Multi",data=sys.argv)
## import sys
## h = sys.argv

## from Tkinter import *
## import Pmw
## from afrift_gui import Appl_multi
## root = Tk()
## Pmw.initialise(root)
## app = Appl_multi(root,h)
## root.mainloop()

## import wx
## from afrift_wxgui import Appl_multi
## app = wx.PySimpleApp()
## h = Appl_multi(root,h)
## app.MainLoop()

## from afrift_ppgui import AppMulti
## app = AppMulti(*h)
