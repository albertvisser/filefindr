# -*- coding: latin1 -*-
# als je %L opgeeft in het Parameters veld bij de definitie van een TC button of menu item geeft-ie de
# geselecteerde file- en directorynamen door aan het aangeroepen programma
import sys
from afrift_gui import MainFrame

MainFrame(apptype="Single",data=sys.argv)

## import sys
## h = sys.argv
## h = ("hallo","findr_files.py")

## from Tkinter import *
## import Pmw
## from afrift_gui import Appl_single
## root = Tk()
## Pmw.initialise(root)
## app = Appl_single(root,h)
## root.mainloop()

## import wx
## from afrift_wxgui import Appl_single
## app = wx.PySimpleApp()
## h = Appl_single(None,h)
## app.MainLoop()

## from afrift_ppgui import AppSingle
## app = AppSingle(*h)
