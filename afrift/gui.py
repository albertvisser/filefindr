"""imports the gui code from a toolkit-specific module
so that the other modules don't need to know which one is used
"""
from .toolkit import toolkit
if toolkit == 'qt':
    from .gui_qt import SelectNamesGui, ResultsGui, MainFrameGui
elif toolkit == 'wx':
    from .gui_wx import SelectNamesGui, ResultsGui, MainFrameGui
