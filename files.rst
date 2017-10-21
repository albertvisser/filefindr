Files in this directory
=======================

.hgignore
    Mercurial ignore list
LICENSE
    MIT license
files.rst
    this list
mystuff.py
    some self written functions originally intended for general use, to be included
    in site-packages
readme.rst
    application notes
start.py
    application command line interface

afrift\
__init__.py
    (empty) package indicator
afrift\afrift_base.py
    (most) GUI-independent code
    imports configobj
afrift\afrift_gui.py
    script that chooses one of the gui toolkit versions
    imports from one of the following afrift_$$.py modules
afrift\afrift_ppgui.py
    GUI code PocketPyGUI version
    imports ppygui, findr_files, afrift_base
afrift\afrift_qt4gui.py
    GUI code PyQT4 version
    imports PyQT4.QtGui, PyQT4.QtCore, findr_files, afrift_base
afrift\afrift_qtgui.py
    GUI code PyQT5 version (currently used in afrift_gui.py)
    imports PyQT5.QtWidgets, PyQT5.QtGui, PyQT5.QtCore, findr_files, afrift_base
afrift\afrift_tk3gui.py
    GUI code Tkinter version for Python 3
    imports tkinter, tkinter.ttk, findr_files, afrift_base
afrift\afrift_tkgui.py
    GUI code Tkinter/Pmw version
    imports Tkinter, Pmw, findr_files, afrift_base
afrift\afrift_wxgui.py
    GUI code wxPython version
    imports wx, findr_files, afrift_base
afrift\find.ico
    icon for the application I found somewhere
afrift\findr_files.py
    the actual workhorse: find/replace routine (class)
    imports re, shutil, collections

test\
afrift.args
    sample search items list (files), used by test_afrift_base.py
sample.txt
    sample search arguments list, used by test_findr_files.py
test_afrift_base.py
    unit tests for the gui independent parts
test_findr_files.py
    unit tests for the file finder class
