Files in this directory
=======================

__init__.py
    (empty) package indicator
afrift.pyw
    starter for standalone version
    imports afrift_gui.py
afrift_tc.pyw
    starter for TC lijst version
    imports afrift_gui.py
afrift_tc_1.pyw
    starter for TC 1 file version
    imports afrift_gui.py
afrift_tkgui.py
    GUI code Tkinter/Pmw version
    imports Tkinter, Pmw, findr_files, afrift_base
afrift_gui.py
    GUI code wxPython version
    imports wx, findr_files, afrift_base
afrift_ppgui.py
    GUI code PocketPyGUI version
    imports ppygui, findr_files, afrift_base
afrift_qtgui.py
    GUI code PyQT version
    imports PyQT4.QtGui, PyQT4.QtCore, findr_files, afrift_base
afrift_tk3gui.py
    GUI code Tkinter version for Python 3
    imports tkinter, tkinter.ttk, findr_files, afrift_base
afrift_base.py
    (most) GUI-independent code
    imports ConfigParser
findr_files.py
    find/replace routine (class)
    imports re, shutil
