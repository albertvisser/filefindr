# -*- coding: utf-8 -*-
"""imports the gui from a toolkit-specific module
so that the starters need not know about which one is used
"""
## import sys
## import os
## sys.path.insert(0, os.path.dirname(__file__))
## import afrift_qtgui
from .afrift_qtgui import MainFrame
MainFrame = MainFrame

def test():
    "test routine"
    win = MainFrame()
    ## MainFrame(apptype = "single", fnaam = '/home/albert/filefindr/afrift/afrift_gui.py')
    ## win = MainFrame(apptype="multi", fnaam = 'CMDAE.tmp')

if __name__ == "__main__":
    test()
