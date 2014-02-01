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

+ ``python afrift.pyw`` to call the primary version
+ ``python afrift_multi.pyw <filename>`` to call the version working on multiple files and directories; the argument is the name of a file containing those
+ ``python afrift_single.pyw <filename>`` to call the version working on a single file.

For the single file version, I've tweaked my favourite text editor SciTE to call
it from within the file I'm currently editing.

The multiple file version I've set up to be called on the file(s) and/or directories
I mark in my file manager .

Dependencies
------------

- Python
- wxPython for the current GUI version
- Tkinter, PyQt4 for older GUI versions and Python3 GUI versions
- PocketPyGUI for a PocketPC version
