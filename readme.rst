Find/Replace in Files
=====================

This application is meant to show occurrences of text in files contained in
one or more directories, as well as replacing those with other text.

Primarily it has a front-end in which you can choose the directory
containing the files to work on, but you can also call special versions
that work on a series of files and directories or on a single file.

There are several options to specify the type of search/replace action,
as well as the location(s) and type(s) of the file to process.

The search results are shown in a dialog box and they can also be saved to a file.


Usage
-----

``python(3) start.py`` from the program directory starts up the primary version. There's a host of options you can either select in the gui or enter on the command line. Help is provided through the use of ``argparse`` in the startup script.
The options are retained per directory, so when you specify some you don't have to choose them again for a new search in the same location. 

Originally this tool was intended to work on a directory, but I added some extra modes to make this work with other tools I use: a ``single`` mode makes it work on a single file instead of a directoryand a ``multi`` mode makes it possible to specify multiple files and directories to start from.

The single file version was intended to be called from within my favourite text editor SciTE to use on the current file, and the multiple file version was meant to be called from a graphical file manager after marking the entries to work with, but you can also specify these on the command line.

Use ``toolkit.py`` in the program directory (``afrift``) to define which gui toolkit to use. I didn't think it was useful to make this an option you can specify on startup, so it's in the background.


Dependencies
------------

- Python(3)
- PyQt (5) or wxPython (Phoenix) for the current GUI version


Historic notes
--------------

I used Tkinter for the first GUI version and also for the first Python3 version (the latter is still included but currently unmaintained), and I've also built one using PocketPyGUI for a PocketPC version when I was using a PDA.

For saving previousy entered values between sessions, the previous implementation used *pickle*. The most up-to-date version uses *json* for this.
