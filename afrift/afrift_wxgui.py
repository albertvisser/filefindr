"""AFRIFT wxPython versie
"""
import os
import sys
import wx
## import contextlib


class SelectNamesGui(wx.Dialog):
    def __init__(self, parent):
        self.parent = parent
        style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        super().__init__(parent, title=self.title, style=style)
        self.SetIcon(wx.Icon(iconame, wx.BITMAP_TYPE_ICO))

    def setup_screen(self, captions):
        vbox = wx.BoxSizer(wx.VERTICAL)

        txt = wx.StaticText(self, -1, captions['heading'])
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(txt, 0, wx.EXPAND | wx.ALL, 5)
        vbox.Add(hbox, 0)

        self.sel_all = wx.CheckBox(self, label=captions['sel_all'])
        self.Bind(wx.EVT_CHECKBOX, self.select_all, self.sel_all)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.addSpacing(10)
        hbox.addWidget(self.sel_all)

        self.flip_sel = wx.Button(self, label=captions['invert'])
        ## self.Bind(wx.EVT_BUTTON, self.invert_selection, self.flip_sel)
        self.flip_Bind(wx.EVT_BUTTON, self.invert_selection)
        hbox.addStretch()
        hbox.addWidget(self.flip_sel)
        hbox.addSpacing(20)
        vbox.addLayout(hbox)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.frm = wx.CheckListBox(self, -1, choices=self.parent.names)
        self.checklist = self.frm.GetItems()
        hbox.Add(self.frm, 0)
        vbox.Add(hbox, 0)

        b_can = wx.Button(self, label=captions['exit'])
        b_can.Bind(wx.EVT_BUTTON, self.klaar)
        self.SetEscapeId(b_can.GetId())
        b_ok = wx.Button(self, label=captions['execute'])
        b_ok.Bind(wx.EVT_BUTTON, self.klaar)
        self.SetAffirmativeId(b_ok.GetId())
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(b_can, 0)
        hbox.Add(b_ok, 0)
        vbox.Add(hbox, 0, wx.ALIGN_CENTER_HORIZONTAL)

        self.SetAutoLayout(True)
        self.SetSizer(vbox)
        vbox.Fit(self)
        ## vsizer.SetSizeHints(self)
        self.Layout()

    def select_all(self):
        """check or uncheck all boxes
        """
        state = self.sel_all.IsChecked()
        for cb in self.checklist:
            cb.setChecked(state)

    def invert_selection(self):
        """check unchecked and uncheck checked boxes
        """
        for cb in self.checklist:
            cb.setChecked(not cb.isChecked())

    def klaar(self, event):
        "dialoog afsluiten"
        dirs = []
        for checked in self.frm.CheckedStrings:
            print(checked)
            if self.parent.dofiles:
                self.parent.names.remove(checked)
            else:
                dirs.append(checked)
        if not self.parent.dofiles:
            self.parent.names = dirs
        self.EndModal(0)


class ResultsGui(wx.Dialog):
    def __init__(self, parent, root):
        self.root = root
        style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        super().__init__(parent, title=parent.resulttitel, style=style)
        self.SetIcon(wx.Icon(iconame, wx.BITMAP_TYPE_ICO))

    def setup_gui(self, captions):
        if self.root.parent.apptype == "single":
            breedte = 50
        elif self.root.parent.apptype == 'multi':
            breedte = 200
        else:
            breedte = 300
        vsizer = wx.BoxSizer(wx.VERTICAL)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        txt = wx.StaticText(self, label=captions['heading'])

        hsizer.Add(txt, 0, wx.EXPAND | wx.ALL, 5)
        vsizer.Add(hsizer, 0, wx.EXPAND)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.lijst = wx.ListCtrl(self, -1, size=(breedte + 385, 460),
                                 style=wx.LC_REPORT | wx.LC_VRULES)
        self.lijst.InsertColumn(0, self.root.titel)
        self.lijst.SetColumnWidth(0, breedte)
        self.lijst.InsertColumn(1, "Data")
        self.lijst.SetColumnWidth(1, 380)
        self.populate_list()
        vsizer.Add(hsizer, 1, wx.EXPAND)

        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        bsizer = wx.BoxSizer(wx.HORIZONTAL)
        btn = wx.Button(self, wx.ID_CANCEL, label=captions['exit'])
        ## self.Bind(wx.EVT_BUTTON, self.einde,  b2)
        bsizer.Add(btn, 0, wx.ALL, 5)
        btn = wx.Button(self, label=captions['cpy'])
        btn.Bind(wx.EVT_BUTTON, self.kopie)
        bsizer.Add(btn, 0, wx.ALL, 5)
        btn = wx.Button(self, label=captions['clp'])
        btn.Bind(wx.EVT_BUTTON, self.to_clipboard)
        bsizer.Add(btn, 0, wx.ALL, 5)
        cb = wx.CheckBox(self, label=captions['pth'])
        cb.SetValue(False)
        if self.parent.apptype == "single":
            cb.Enable(False)
        self.cb = cb
        bsizer.Add(cb, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        hsizer.Add(bsizer, 0)
        vsizer.Add(hsizer, 0, wx.ALIGN_CENTER_HORIZONTAL)  # wx.EXPAND)

        self.SetAutoLayout(True)
        self.SetSizer(vsizer)
        vsizer.Fit(self)
        ## vsizer.SetSizeHints(self)
        self.Layout()
        self.Show(True)
        self.SetFocus()

    def populate_list(self):
        """copy results to listbox
        """
        for result in self.results[1:]:
            i = self.lijst.InsertItem(sys.maxsize, result[0])
            self.lijst.SetItem(i, 0, result[0])
            # TODO: insert context if present
            self.lijst.SetItem(i, 1, result[-1])

    def get_savefile(self, fname, filter):
        # TODO finish
        # filter komt mee vanwege de csv mogelijkheid
        fn = ''
        with wx.FileDialog(self, message="Resultaat naar bestand kopieren",
                           defaultDir=str(self.root.parent.hier),
                           defaultFile=fname.join(('searchfor_', ".txt")),
                           wildcard="text files (*.txt)|*.txt|all files (*.*)|*.*",
                           style=wx.FD_SAVE) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                fn = dlg.GetPath()
        return fn

    def copy_to_clipboard(self, text):
        # TODO: finish
        toonpad = True if self.cb.IsChecked() else False
        do = wx.TextDataObject()
        do.SetText('\n'.join([str(x) for x in self.get_results(toonpad)]))
        clp = wx.Clipboard.Get()
        if clp.Open():
            clp.SetData(do)
            clp.Close()
        else:
            wx.MessageBox("Unable to open the clipboard", "Error")


class MainFrameGui(wx.Frame):
    def __init__(self, root):
        self.root = root        # verwijzing naar MainFrame - voor als het nodig is
        self.app = wx.App()
        super().__init__(None, title=self.root.title,
                         style=wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)
        self.SetIcon(wx.Icon(root.iconame, wx.BITMAP_TYPE_ICO))

    def setup_screen(self, captions):
        "set up screen for the various modes"
        self.pnl = wx.Panel(self)
        TXTW = 240
        TXTH = 24

        bsizer = wx.BoxSizer(wx.VERTICAL)
        gbsizer = wx.GridBagSizer(4)
        row = 0
        gbsizer.Add(wx.StaticText(self.pnl, label=captions['vraag_zoek']), (row, 0),
                    flag=wx.EXPAND | wx.ALL, border=4)
        self.vraag_zoek = wx.ComboBox(self.pnl, size=(TXTW, TXTH), style=wx.CB_DROPDOWN,
                                      choices=self.root._mru_items["zoek"])
        gbsizer.Add(self.vraag_zoek, (row, 1), flag=wx.ALIGN_CENTER_VERTICAL)
        gbsizer.Add(wx.StaticText(self.pnl, size=(20, -1)), (row, 2))
        row += 1
        vsizer = wx.BoxSizer(wx.VERTICAL)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hbsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.vraag_regex = wx.CheckBox(self.pnl, label=captions['regex'])
        hbsizer.Add(self.vraag_regex, 0)
        hsizer.Add(hbsizer, 0, wx.TOP | wx.BOTTOM, 4)
        vsizer.Add(hsizer, 0, wx.EXPAND)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hbsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.vraag_case = wx.CheckBox(self.pnl, -1, label=captions['case'])
        self.vraag_case.SetValue(bool(self.root.p["case"]))
        hbsizer.Add(self.vraag_case, 0)
        hsizer.Add(hbsizer, 0, wx.TOP | wx.BOTTOM, 4)
        vsizer.Add(hsizer, 0, wx.EXPAND)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hbsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.vraag_woord = wx.CheckBox(self.pnl, label=captions['woord'])
        self.vraag_woord.SetValue(bool(self.root.p["woord"]))
        hbsizer.Add(self.vraag_woord, 0)
        hsizer.Add(hbsizer, 0, wx.TOP | wx.BOTTOM, 4)
        vsizer.Add(hsizer, 0, wx.EXPAND)
        gbsizer.Add(vsizer, (row, 1))

        row += 1
        gbsizer.Add(wx.StaticText(self.pnl, label=captions['vraag_verv']), (row, 0),
                    flag=wx.EXPAND | wx.ALL, border=4)
        self.vraag_verv = wx.ComboBox(self.pnl, size=(TXTW, TXTH), style=wx.CB_DROPDOWN,
                                      choices=self.root._mru_items["verv"])
        gbsizer.Add(self.vraag_verv, (row, 1), flag=wx.ALIGN_CENTER_VERTICAL)
        row += 1
        vsizer = wx.BoxSizer(wx.VERTICAL)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hbsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.check_vervang = wx.CheckBox(self.pnl, label=captions['empty'])
        self.check_vervang.SetValue(self.root._vervleeg)
        hbsizer.Add(self.check_vervang, 0)
        hsizer.Add(hbsizer, 0, wx.TOP | wx.BOTTOM, 4)
        vsizer.Add(hsizer, 0, wx.EXPAND)
        gbsizer.Add(vsizer, (row, 1))

        t = ""
        if self.root.apptype == "":
            row += 1
            gbsizer.Add(wx.StaticText(self.pnl, label=captions['in']), (row, 0),
                        flag=wx.EXPAND | wx.ALL, border=4)
            self.vraag_dir = wx.ComboBox(self.pnl, size=(TXTW, TXTH), style=wx.CB_DROPDOWN,
                                         choices=self.root._mru_items["dirs"])
            hsizer = wx.BoxSizer(wx.HORIZONTAL)
            hsizer.Add(self.vraag_dir, 0, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
            btn = wx.Button(self.pnl, label=captions['zoek'], size=(-1, TXTH))
            btn.Bind(wx.EVT_BUTTON, self.zoekdir)
            hsizer.Add(btn, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 4)
            gbsizer.Add(hsizer, (row, 1), flag=wx.EXPAND | wx.TOP | wx.BOTTOM, border=2)
        elif self.root.apptype == "single":
            row += 1
            gbsizer.Add(wx.StaticText(self.pnl, label=captions['in_s']), (row, 0),
                        flag=wx.EXPAND | wx.ALL, border=4)
            gbsizer.Add(wx.StaticText(self.pnl, label=self.root.fnames[0]), (row, 1),
                        flag=wx.EXPAND | wx.ALL, border=4)
            gbsizer.Add(wx.StaticText(self.pnl, size=(120, -1)), (row, 2),
                        flag=wx.EXPAND | wx.ALL, border=4)
        else:
            t = captions['subs_m']

        if self.root.apptype != "single" or os.path.isdir(self.root.fnames[0]):
            row += 1
            self.vraag_subs = wx.CheckBox(self.pnl, -1, label=t + captions['subs'])
            self.vraag_subs.SetValue(bool(self.root.p["subdirs"]))
            gbsizer.Add(self.vraag_subs, (row, 1), flag=wx.EXPAND | wx.TOP | wx.BOTTOM, border=2)
            row += 1
            hsizer = wx.BoxSizer(wx.HORIZONTAL)
            self.vraag_links = wx.CheckBox(self.pnl, -1, label=captions['link'])
            hsizer.Add(self.vraag_links, 0, wx.ALIGN_CENTER_VERTICAL)  # wx.TOP | wx.BOTTOM, 4)
            self.vraag_diepte = wx.SpinCtrl(self.pnl, -1, min=-1, initial=5, size=(122, TXTH))
            hsizer.Add(self.vraag_diepte, 0, wx.ALIGN_CENTER_VERTICAL)  # , 4)
            gbsizer.Add(hsizer, (row, 1), flag=wx.EXPAND | wx.TOP | wx.BOTTOM, border=2)

        if self.root.apptype != "single" or os.path.isdir(self.root.fnames[0]):
            row += 1
            self.ask_skipdirs = wx.CheckBox(self.pnl, label=captions['skipdirs'])
            gbsizer.Add(self.ask_skipdirs, (row, 1), flag=wx.EXPAND)
            row += 1
            self.ask_skipfiles = wx.CheckBox(self.pnl, label=captions['skipfiles'])
            gbsizer.Add(self.ask_skipfiles, (row, 1), flag=wx.EXPAND)

        if self.root.apptype != "single" or os.path.isdir(self.root.fnames[0]):
            row += 1
            gbsizer.Add(wx.StaticText(self.pnl, label=captions['ftypes']), (row, 0),
                        flag=wx.EXPAND | wx.ALL, border=4)
            self.vraag_types = wx.ComboBox(self.pnl, -1, size=(TXTW, TXTH),
                                           choices=self.root._mru_items["types"],
                                           style=wx.CB_DROPDOWN)
            gbsizer.Add(self.vraag_types, (row, 1), flag=wx.ALIGN_CENTER_VERTICAL)

        if self.root.apptype == "multi":
            row += 1
            gbsizer.Add(wx.StaticText(self.pnl, label=captions['in_m']), (row, 0), (1, 2),
                        flag=wx.EXPAND | wx.LEFT | wx.TOP, border=4)
            row += 1
            self.lb = wx.ListBox(self.pnl, size=(TXTW, -1), choices=self.root.fnames)
            gbsizer.Add(self.lb, (row, 0), (1, 2), flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=4)

        row += 1
        self.vraag_backup = wx.CheckBox(self.pnl, label=captions['backup'])
        self.vraag_backup.SetValue(bool(self.root._backup))
        gbsizer.Add(self.vraag_backup, (row, 1), flag=wx.EXPAND)
        row += 1
        self.vraag_exit = wx.CheckBox(self.pnl, label=captions['exit'])
        self.vraag_exit.SetValue(bool(self.root._exit_when_ready))
        gbsizer.Add(self.vraag_exit, (row, 1), flag=wx.EXPAND)

        row += 1
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.DoIt = wx.Button(self.pnl, -1, size=(-1, TXTH), label="&Uitvoeren")
        self.DoIt.Bind(wx.EVT_BUTTON, self.root.doe)
        hsizer.Add(self.DoIt, 0, wx.EXPAND | wx.ALL, 4)
        ## self.Cancel = wx.Button(self.pnl,  wx.ID_CANCEL, "&Einde") # helpt niet
        self.Cancel = wx.Button(self.pnl, -1, size=(-1, TXTH), label="&Einde")
        self.Cancel.Bind(wx.EVT_BUTTON, self.einde)
        hsizer.Add(self.Cancel, 0, wx.EXPAND | wx.ALL, 4)
        gbsizer.Add(hsizer, (row, 0), (1, 3), flag=wx.ALIGN_BOTTOM | wx.ALIGN_CENTER_HORIZONTAL,
                    border=0)
        bsizer.Add(gbsizer, 0, wx.ALL, 4)

        ## self.pnl.SetAutoLayout(True)
        self.pnl.SetSizer(bsizer)
        bsizer.Fit(self)
        ## bsizer.SetSizeHints(self)

        self.pnl.Layout()
        self.vraag_zoek.SetFocus()
        self.noescape = False
        self.Bind(wx.EVT_KEY_UP, self.on_key_up)
        self.SetFocus()

    def get_searchtext(self):
        return self.vraag_zoek.GetValue()

    def get_replace_args(self):
        return self.vraag_verv.GetValue(), self.check_vervang.GetValue()

    def get_search_attr(self):
        return (self.vraag_regex.GetValue(), self.vraag_case.GetValue(),
                self.vraag_woord.GetValue())

    def get_types_to_search(self):
        return self.vraag_types.GetValue()

    def get_dir_to_search(self):
        return self.vraag_dir.GetValue()

    def get_subdirs_to_search(self):
        return (self.vraag_subs.GetValue(), self.vraag_links.GetValue(),
                self.vraag_diepte.GetValue())

    def get_backup(self):
        return self.vraag_backup.GetValue()

    def get_ignore(self):
        return

    def get_context(self):
        return

    def error(self, titel, message):
        wx.MessageBox(message, titel, wx.OK | wx.ICON_ERROR)

    def meld(self, titel, message):
        wx.MessageBox(message, titel, wx.OK | wx.ICON_INFORMATION)

    def add_item_to_searchlist(self, item):
        ""

    def get_skipdirs(self):
        return self.ask_skipdirs.IsChecked()

    def get_skipfiles(self):
        return self.ask_skipfiles.IsChecked()

    def set_waitcursor(value):
        if value:
            wx.BeginBusyCursor()
        else:
            wx.EndBusyCursor()

    def get_exit(self):
        self.vraag_exit.GetValue()

    def go(self):
        self.Show(True)
        self.app.MainLoop()

    def einde(self, event=None):
        """applicatie afsluiten"""
        self.Close(True)

    def on_key_up(self, ev):
        """event handler voor toetsaanslagen"""
        ## print(ev.GetKeyCode())
        if ev.GetKeyCode() == wx.WXK_ESCAPE:
            if self.noescape:
                self.noescape = False
            else:
                self.einde()
        else:
            ev.Skip()

    def zoekdir(self, event):
        """event handler voor 'zoek in directory'"""
        oupad = self.vraag_dir.GetValue()
        with wx.DirDialog(self, "Choose a directory:", defaultPath=oupad,
                          style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                self.vraag_dir.SetValue(dlg.GetPath())
        # dlg.Destroy()
