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
afrift_gui.py
    GUI code wxPython version
    imports wx, ConfigParser, findr_files
afrift_ppgui.py
    GUI code PocketPyGUI version
    imports ppygui, configparser, findr_files
afrift_tkgui.py
    GUI code Tkinter/Pmw version
    imports Tkinter, Pmw, ConfigParser, findr_files
findr_files.py
    find/replace routine (class)
    imports re, shutil, mystuff
mystuff.py
    general purpose routines and userdefined exceptions
    to be placed in site-packages
