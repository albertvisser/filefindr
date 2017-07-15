# -*- coding: utf-8 -*-
"""imports the gui from a toolkit-specific module
so that the starters need not know about which one is used
"""
## from .afrift_ppgui import MainFrame
## from .afrift_tkgui import MainFrame
## from .afrift_tk3gui import MainFrame
## from .afrift_wxgui import MainFrame
## from .afrift_qt4gui import MainFrame
from .afrift_qtgui import MainFrame
MainFrame = MainFrame
