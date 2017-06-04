#! /usr/bin/env python3
import sys
from afrift.afrift_gui import MainFrame
if len(sys.argv) > 1:
    MainFrame(fnaam=sys.argv[1])
else:
    MainFrame()
