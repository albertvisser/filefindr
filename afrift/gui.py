"""imports the gui code from a toolkit-specific module
so that the other modules don't need to know which one is used
"""
# from .afrift_ppgui import MainFrame
# from .afrift_tkgui import MainFrame
# from .afrift_tk3gui import MainFrame
# from .afrift_qt4gui import MainFrame
from .gui_wx import SelectNamesGui, ResultsGui, MainFrameGui
# from .gui_qt import SelectNamesGui, ResultsGui, MainFrameGui
