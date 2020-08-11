"""AFRIFT wxPython specific classes
"""
import os
import sys
import wx
import wx.lib.mixins.listctrl as listmix
## import contextlib
TXTW = 240
TXTH = 24


class MyListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
    "ListCtrl met mixin voor automatische kolom uitvulling"
    def __init__(self, parent, pos=wx.DefaultPosition, size=wx.DefaultSize, style=0):
        wx.ListCtrl.__init__(self, parent, pos=pos, size=size, style=style)
        listmix.ListCtrlAutoWidthMixin.__init__(self)


class SelectNamesGui(wx.Dialog):
    """dialog for selecting directories/files
    """
    def __init__(self, parent, master):
        self.parent = parent
        self.master = master
        style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        super().__init__(parent.gui, title=self.master.title, style=style)
        self.SetIcon(wx.Icon(master.iconame, wx.BITMAP_TYPE_ICO))

    def setup_screen(self, captions):
        "build widgets"
        vbox = wx.BoxSizer(wx.VERTICAL)

        txt = wx.StaticText(self, -1, captions['heading'])
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(txt, 0, wx.EXPAND | wx.ALL, 5)
        vbox.Add(hbox, 0)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.AddSpacer(10)
        self.sel_all = wx.CheckBox(self, label=captions['sel_all'])
        self.sel_all.Bind(wx.EVT_CHECKBOX, self.select_all)
        hbox.Add(self.sel_all, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 28)

        self.flip_sel = wx.Button(self, size=(-1, TXTH), label=captions['invert'])
        self.flip_sel.Bind(wx.EVT_BUTTON, self.invert_selection)
        # hbox.addStretch()
        hbox.Add(self.flip_sel, 0, wx.ALIGN_RIGHT | wx.RIGHT, 7)
        # hbox.AddSpacer(20)
        vbox.Add(hbox, 0, wx.EXPAND)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.frm = wx.CheckListBox(self, -1, choices=[str(x) for x in self.master.parent.names])
        self.checklist = self.frm.GetItems()
        hbox.Add(self.frm, 0, wx.LEFT | wx.RIGHT, 7)
        vbox.Add(hbox, 0)

        b_can = wx.Button(self, size=(-1, TXTH), label=captions['exit'])
        # b_can.Bind(wx.EVT_BUTTON, self.klaar)
        self.SetEscapeId(b_can.GetId())
        b_ok = wx.Button(self, size=(-1, TXTH), label=captions['execute'])
        b_ok.Bind(wx.EVT_BUTTON, self.klaar)
        #  self.SetAffirmativeId(b_ok.GetId())
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(b_can, 0)
        hbox.Add(b_ok, 0)
        vbox.Add(hbox, 0, wx.ALIGN_CENTER_HORIZONTAL)

        self.SetAutoLayout(True)
        self.SetSizer(vbox)
        vbox.Fit(self)
        ## vsizer.SetSizeHints(self)
        self.Layout()

    def go(self):
        """show the dialog screen
        """
        result = self.ShowModal()
        if result == wx.ID_OK:
            return True
        # elif result == wx.ID_CANCEL:
        return False

    def select_all(self, event):
        """check or uncheck all boxes
        """
        state = self.sel_all.IsChecked()
        for itemindex in range(len(self.checklist)):
            self.frm.Check(itemindex, state)

    def invert_selection(self, event):
        """check unchecked and uncheck checked boxes
        """
        for itemindex in range(len(self.checklist)):
            self.frm.Check(itemindex, not self.frm.IsChecked(itemindex))

    def klaar(self, event):
        "dialoog afsluiten"
        dirs = []
        for checked in self.frm.CheckedStrings:
            if self.master.do_files:
                self.master.names.pop(checked)
            else:
                dirs.append(checked)
        if self.master.do_files:
            self.master.names = [self.master.names[x] for x in sorted(self.master.names.keys())]
        else:
            self.master.names = dirs
        self.EndModal(wx.ID_OK)


class ResultsGui(wx.Dialog):
    """results screen
    """
    def __init__(self, parent, master):
        self.master = master
        style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        super().__init__(parent.gui, title=master.parent.resulttitel, style=style)
        self.SetIcon(wx.Icon(master.iconame, wx.BITMAP_TYPE_ICO))

    def setup_screen(self, captions):
        "build widgets"
        def add_ampersand(text):
            "& teken tussenvoegen t.b.v. accelerator"
            return '&'.join((text[0], text[1:]))
        breedte = 50 if self.master.parent.apptype == "single" else 150  # qt versie
        vsizer = wx.BoxSizer(wx.VERTICAL)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.txt = wx.StaticText(self, label=captions['heading'])
        hsizer.Add(self.txt, 0, wx.EXPAND | wx.ALL, 5)
        vsizer.Add(hsizer, 0, wx.EXPAND)

        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.lijst = MyListCtrl(self, size=(-1, 460), style=wx.LC_REPORT | wx.LC_VRULES)
        self.lijst.InsertColumn(0, self.master.titel)
        self.lijst.SetColumnWidth(0, breedte)
        colno = 1
        if self.master.show_context:
            self.lijst.InsertColumn(1, captions['ctxt'])
            self.lijst.SetColumnWidth(1, 200)
            colno += 1
        self.lijst.InsertColumn(colno, captions['txt'])
        self.lijst.resizeLastColumn(200)
        self.populate_list()

        self.lijst.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.to_result)
        accel_list = []
        menuitem = wx.MenuItem(None, wx.NewId(), captions['hlp'])
        self.Bind(wx.EVT_MENU, self.help, menuitem)
        accel = wx.AcceleratorEntry(cmd=menuitem.GetId())
        ok = accel.FromString('F1')
        if ok:
            accel_list.append(accel)
        menuitem = wx.MenuItem(None, wx.NewId(), captions['rslt'])
        self.Bind(wx.EVT_MENU, self.to_result, menuitem)
        accel = wx.AcceleratorEntry(cmd=menuitem.GetId())
        ok = accel.FromString('Ctrl+G')
        if ok:
            accel_list.append(accel)

        hsizer.Add(self.lijst, 1, wx.EXPAND | wx.ALL, 5)
        vsizer.Add(hsizer, 1, wx.EXPAND)

        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        bsizer = wx.BoxSizer(wx.HORIZONTAL)
        btn = wx.Button(self, wx.ID_CANCEL, size=(-1, TXTH), label=captions['exit'])
        bsizer.Add(btn, 0, wx.ALL, 5)

        if not self.master.label_only:
            btn = wx.Button(self, size=(-1, TXTH), label=captions['rpt'])
            btn.Bind(wx.EVT_BUTTON, self.master.refresh)
            if self.master.parent.p['vervang']:
                btn.Enable(False)
            bsizer.Add(btn, 0, wx.ALL, 5)

            btn = wx.Button(self, size=(-1, TXTH), label=captions['cpy'])
            btn.Bind(wx.EVT_BUTTON, self.master.kopie)
            bsizer.Add(btn, 0, wx.ALL, 5)

            btn = wx.Button(self, size=(-1, TXTH), label=captions['clp'])
            btn.Bind(wx.EVT_BUTTON, self.master.to_clipboard)
            bsizer.Add(btn, 0, wx.ALL, 5)

            gsizer = wx.FlexGridSizer(cols=2, vgap=5, hgap=5)
            gsizer.Add(wx.StaticText(self, label=captions['fmt']), 0,
                       wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 4)

            cb = wx.CheckBox(self, label=add_ampersand(captions['dlm']))
            accel = wx.AcceleratorEntry(cmd=cb.GetId())
            ok = accel.FromString('Alt+O')
            if ok:
                accel_list.append(accel)
            cb.SetValue(self.master.parent.outopts['as_csv'])
            self.cb_delim = cb
            gsizer.Add(cb)

            cb = wx.CheckBox(self, label='&' + captions['pth'])
            accel = wx.AcceleratorEntry(cmd=cb.GetId())
            ok = accel.FromString('Alt+P')
            if ok:
                accel_list.append(accel)
            cb.SetValue(self.master.parent.outopts['full_path'])
            if self.master.parent.apptype == "single":
                cb.Enable(False)
            self.cb_path = cb
            gsizer.Add(cb)

            cb = wx.CheckBox(self, label=add_ampersand(captions['sum']))
            accel = wx.AcceleratorEntry(cmd=cb.GetId())
            ok = accel.FromString('Alt+U')
            if ok:
                accel_list.append(accel)
            cb.SetValue(self.master.parent.outopts['summarize'])
            self.cb_smrz = cb
            gsizer.Add(cb)

            hsizer.Add(bsizer, 0, wx.ALIGN_CENTER_VERTICAL)
            hsizer.Add(gsizer, 0, wx.ALL, 5)
        vsizer.Add(hsizer, 0, wx.ALIGN_CENTER_HORIZONTAL)  # wx.EXPAND)

        if accel_list:
            self.SetAcceleratorTable(wx.AcceleratorTable(accel_list))
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
        for result in self.master.results[1:]:

            col = 0
            indx = self.lijst.InsertItem(sys.maxsize, result[0])
            self.lijst.SetItem(indx, col, result[0])

            if self.master.show_context:
                col += 1
                self.lijst.SetItem(indx, col, result[1])

            col += 1
            self.lijst.SetItem(indx, col, result[-1])

    def clear_contents(self):
        "remove all entries from list"
        self.lijst.DeleteAllItems()

    def go(self):
        """show the dialog screen
        """
        self.ShowModal()

    def breekaf(self, message):
        "show reason and end dialog"
        self.meld(self.parent.resulttitel, message)
        self.EndModal(0)

    def set_header(self, text):
        "set header for list"
        self.txt.SetLabel(text)

    def get_pth(self):
        "get indicator to show path"
        return self.cb_path.GetValue()

    def get_csv(self):
        "get indicator to save as csv"
        return self.cb_delim.GetValue()

    def get_sum(self):
        "get indicator to show as summarized"
        return self.cb_smrz.GetValue()

    def get_savefile(self, fname, ext):
        """callback for button 'Copy to file'
        """
        if ext == '.csv':
            f_filter = 'Comma delimited files (*.csv)|*.csv;;'
        elif ext == '.txt':
            f_filter = 'Text files (*.txt)|*.txt;;'
        fn = ''
        with wx.FileDialog(self, message="Resultaat naar bestand kopieren",
                           defaultDir=str(self.master.parent.hier),
                           defaultFile=fname.join(('searchfor_', ".txt")),
                           wildcard="{}|All files (*.*)|*.*".format(f_filter),
                           style=wx.FD_SAVE) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                fn = dlg.GetPath()
        return fn

    def meld(self, titel, message):
        "show an informational message"
        wx.MessageBox(message, titel, wx.OK | wx.ICON_INFORMATION, self)

    def copy_to_clipboard(self, text):
        """callback for button 'Copy to clipboard'
        """
        do = wx.TextDataObject()
        do.SetText(text)
        clp = wx.Clipboard.Get()
        if clp.Open():
            clp.SetData(do)
            clp.Close()
        else:
            wx.MessageBox("Unable to open the clipboard", "Error")

    def help(self, event):
        """implemented here to swallow event argument
        """
        self.master.help()

    def to_result(self, event):
        """show result in file
        """
        row = self.lijst.GetFirstSelected()
        if row == -1:
            row = 0
        self.master.goto_result(row, -1)

    def remember_settings(self):
        ""
        self.master.parent.outopts['full_path'] = self.get_pth()
        self.master.parent.outopts['as_csv'] = self.get_csv()
        self.master.parent.outopts['summarize'] = self.get_sum()
        self.master.parent.write_to_ini()

    def klaar(self):
        """finish dialog - never called
        """
        self.EndModal(0)


class MainFrameGui(wx.Frame):
    """main screen
    """
    def __init__(self, master):
        self.master = master        # verwijzing naar MainFrame - voor als het nodig is
        self.app = wx.App()
        super().__init__(None, title=self.master.title,
                         style=wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)
        self.SetIcon(wx.Icon(master.iconame, wx.BITMAP_TYPE_ICO))

    def setup_screen(self, captions):
        "set up screen for the various modes"
        self.pnl = wx.Panel(self)

        bsizer = wx.BoxSizer(wx.VERTICAL)
        self.grid = wx.GridBagSizer()
        self.row = -1

        self.vraag_zoek = self.add_combobox_row(captions['vraag_zoek'],
                                                self.master.mru_items['zoek'],
                                                initial=self.master.p.get("zoek", ''))
        self.grid.Add(wx.StaticText(self.pnl, size=(20, -1)), (self.row, 2))

        self.vraag_regex = self.add_checkbox_row(captions['regex'], self.master.extraopts['regex'])
        self.vraag_case = self.add_checkbox_row(captions['case'], self.master.p["case"])
        self.vraag_woord = self.add_checkbox_row(captions['woord'], self.master.p["woord"])

        self.vraag_verv = self.add_combobox_row(captions['vraag_verv'],
                                                self.master.mru_items["verv"],
                                                initial=self.master.p.get("verv", ''))
        self.check_vervang = self.add_checkbox_row(captions['empty'], self.master.always_replace)

        if self.master.apptype == "":
            initial = str(self.master.p['filelist'][0]) if self.master.p['filelist'] else ''
            btn = wx.Button(self.pnl, label=captions['zoek'], size=(-1, TXTH))
            btn.Bind(wx.EVT_BUTTON, self.zoekdir)
            self.vraag_dir = self.add_combobox_row(captions['in'], self.master.mru_items["dirs"],
                                                   initial=initial, control=btn)
            self.vraag_dir.Bind(wx.EVT_TEXT, self.check_loc)

        elif self.master.apptype == "single":
            self.row += 1
            self.grid.Add(wx.StaticText(self.pnl, label=captions['in_s']), (self.row, 0),
                          flag=wx.EXPAND | wx.ALL, border=4)
            self.grid.Add(wx.StaticText(self.pnl, label=str(self.master.p['filelist'][0])),
                          (self.row, 1), flag=wx.EXPAND | wx.ALL, border=4)
        else:  # if self.master.apptype == "multi":
            self.row += 1
            self.grid.Add(wx.StaticText(self.pnl, label=captions['in_m']), (self.row, 0), (1, 2),
                          flag=wx.EXPAND | wx.LEFT | wx.TOP, border=4)
            self.row += 1
            self.lb = wx.ListBox(self.pnl, size=(TXTW, 120),  # -1),
                                 choices=[str(x) for x in self.master.p['filelist']])
            self.grid.Add(self.lb, (self.row, 0), (1, 2), flag=wx.EXPAND | wx.LEFT | wx.RIGHT,
                          border=4)

        if self.master.apptype != "single" or os.path.isdir(self.master.p['filelist'][0]):
            txt = captions['subs_m'] if self.master.apptype == "multi" else ""
            self.vraag_subs = self.add_checkbox_row(txt + captions['subs'], self.master.p["subdirs"])
            # NB flag=wx.EXPAND | wx.TOP | wx.BOTTOM, border=2)
            self.vraag_diepte = wx.SpinCtrl(self.pnl, -1, min=-1, initial=5, size=(122, TXTH))
            self.vraag_links = self.add_checkbox_row(captions['link'], control=self.vraag_diepte)
            self.ask_skipdirs = self.add_checkbox_row(captions['skipdirs'])
            self.ask_skipfiles = self.add_checkbox_row(captions['skipfiles'])
            self.vraag_types = self.add_combobox_row(captions['ftypes'],
                                                     self.master.mru_items["types"])

        self.vraag_context = self.add_checkbox_row(captions['context'], self.master.p['context'])
        self.vraag_negeer = self.add_checkbox_row(captions['negeer'], self.master.p['negeer'],
                                                  indent=22)
        self.vraag_backup = self.add_checkbox_row(captions['backup'], self.master.maak_backups)
        self.vraag_exit = self.add_checkbox_row(captions['exit'], self.master.exit_when_ready)

        self.row += 1
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.DoIt = wx.Button(self.pnl, -1, size=(-1, TXTH), label=captions['exec'])
        self.DoIt.Bind(wx.EVT_BUTTON, self.doe)
        hsizer.Add(self.DoIt, 0, wx.EXPAND | wx.ALL, 4)
        self.Cancel = wx.Button(self.pnl, -1, size=(-1, TXTH), label=captions['end'])
        self.Cancel.Bind(wx.EVT_BUTTON, self.einde)
        hsizer.Add(self.Cancel, 0, wx.EXPAND | wx.ALL, 4)
        self.grid.Add(hsizer, (self.row, 0), (1, 3),
                      flag=wx.ALIGN_BOTTOM | wx.ALIGN_CENTER_HORIZONTAL, border=0)
        bsizer.Add(self.grid, 0, wx.ALL, 4)

        ## self.pnl.SetAutoLayout(True)
        self.pnl.SetSizer(bsizer)
        bsizer.Fit(self)
        ## bsizer.SetSizeHints(self)

        self.pnl.Layout()
        self.vraag_zoek.SetFocus()
        accel_list = []
        menuitem = wx.MenuItem(None, wx.NewId(), 'exec')
        self.Bind(wx.EVT_MENU, self.doe, menuitem)
        accel = wx.AcceleratorEntry(cmd=menuitem.GetId())
        ok = accel.FromString('Return')
        if ok:
            accel_list.append(accel)
        menuitem = wx.MenuItem(None, wx.NewId(), 'end')
        self.Bind(wx.EVT_MENU, self.einde, menuitem)
        accel = wx.AcceleratorEntry(cmd=menuitem.GetId())
        ok = accel.FromString('Escape')
        if ok:
            accel_list.append(accel)
        if accel_list:
            self.SetAcceleratorTable(wx.AcceleratorTable(accel_list))
        self.SetFocus()

    def get_searchtext(self):
        "get value of search field"
        return self.vraag_zoek.GetValue()

    def get_replace_args(self):
        "get value of replace field"
        return self.vraag_verv.GetValue(), self.check_vervang.GetValue()

    def get_search_attr(self):
        "read switches for type of search"
        return (self.vraag_regex.GetValue(), self.vraag_case.GetValue(),
                self.vraag_woord.GetValue())

    def get_types_to_search(self):
        "get filetypes to search"
        return self.vraag_types.GetValue()

    def get_dir_to_search(self):
        "get directory to search"
        return self.vraag_dir.GetValue()

    def get_subdirs_to_search(self):
        "get parameters for search in subdirectories"
        return (self.vraag_subs.GetValue(), self.vraag_links.GetValue(),
                self.vraag_diepte.GetValue())

    def get_backup(self):
        "get backup indicator"
        return self.vraag_backup.GetValue()

    def get_ignore(self):
        "get indicator not to search in comments amd docstrings"
        return self.vraag_negeer.GetValue()

    def get_context(self):
        "get indicator to do context specific search"
        return self.vraag_context.GetValue()

    def error(self, titel, message):
        "show an error message"
        wx.MessageBox(message, titel, wx.OK | wx.ICON_ERROR, self)

    def meld(self, titel, message, additional=None):
        "show an informational message"
        if additional:
            with wx.MessageDialog(self, message, titel, wx.OK | wx.ICON_INFORMATION) as dlg:
                dlg.SetExtendedMessage('\n'.join(additional))
                dlg.ShowModal()
        else:
            wx.MessageBox(message, titel, wx.OK | wx.ICON_INFORMATION, self)

    def add_item_to_searchlist(self, item):
        "add string to list of items searched for"
        self.vraag_zoek.Insert(item, 0)

    def get_skipdirs(self):
        "get indicator to select directories to skip"
        return self.ask_skipdirs.IsChecked()

    def get_skipfiles(self):
        "get indicator to select files to skip"
        return self.ask_skipfiles.IsChecked()

    def doe(self, event):
        """callback implemented here to swallow the event parameter
        """
        self.master.doe()

    def set_waitcursor(self, value):
        """switch back and forth to a "busy" cursor
        """
        if value:
            wx.BeginBusyCursor()
        else:
            wx.EndBusyCursor()

    def get_exit(self):
        "get indicator to exit program when ready"
        return self.vraag_exit.GetValue()

    def go(self):
        "show screen and handle events"
        self.Show(True)
        self.app.MainLoop()

    def einde(self, event=None):
        """applicatie afsluiten"""
        self.Close(True)

    def add_combobox_row(self, label, choices, initial='', control=None):
        "add a line with a combobox on it"
        self.row += 1
        lbl = wx.StaticText(self.pnl, label=label)
        self.grid.Add(lbl, (self.row, 0), flag=wx.EXPAND | wx.ALL, border=4)
        cmb = wx.ComboBox(self.pnl, size=(TXTW, TXTH), style=wx.CB_DROPDOWN, choices=choices)
        cmb.AutoComplete(choices)
        if initial:
            cmb.SetValue(initial)
        if control:
            hsizer = wx.BoxSizer(wx.HORIZONTAL)
            hsizer.Add(cmb, 0, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
            hsizer.Add(control, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 4)
            self.grid.Add(hsizer, (self.row, 1), flag=wx.EXPAND | wx.TOP | wx.BOTTOM, border=2)
        else:
            self.grid.Add(cmb, (self.row, 1), flag=wx.ALIGN_CENTER_VERTICAL)
        return cmb

    def add_checkbox_row(self, labeltext, value=None, indent=0, control=None):
        "add a line with a checkbox on it"
        self.row += 1
        vsizer = wx.BoxSizer(wx.VERTICAL)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hbsizer = wx.BoxSizer(wx.HORIZONTAL)
        cb = wx.CheckBox(self.pnl, label=labeltext)
        if value:
            cb.SetValue(value)
        if control:
            hbsizer.Add(cb, 0, wx.ALIGN_CENTER_VERTICAL)  # wx.TOP | wx.BOTTOM, 4)
            hbsizer.Add(control, 0, wx.ALIGN_CENTER_VERTICAL)  # , 4)
        elif indent:
            hbsizer.Add(cb, 0, wx.LEFT, indent)
        else:
            hbsizer.Add(cb, 0)
        hsizer.Add(hbsizer, 0, wx.TOP | wx.BOTTOM, 4)
        vsizer.Add(hsizer, 0, wx.EXPAND)
        self.grid.Add(vsizer, (self.row, 1), flag=wx.EXPAND)
        return cb

    def check_loc(self, event):
        """update location to get settings from
        """
        txt = event.GetEventObject().GetValue()
        if os.path.exists(txt) and not txt.endswith(os.path.sep):
            self.master.read_from_ini(txt)
            self.vraag_zoek.Clear()
            self.vraag_zoek.AppendItems(self.master.mru_items["zoek"])
            if self.master.mru_items["zoek"]:
                self.vraag_zoek.SetValue(self.master.mru_items["zoek"][0])
            self.vraag_verv.Clear()
            self.vraag_verv.AppendItems(self.master.mru_items["verv"])
            if self.master.mru_items["verv"]:
                self.vraag_verv.SetValue(self.master.mru_items["verv"][0])
            self.vraag_types.Clear()
            self.vraag_types.AppendItems(self.master.mru_items["types"])
            if self.master.mru_items["types"]:
                self.vraag_types.SetValue(self.master.mru_items["types"][0])
            ## self.vraag_dir.Clear()
            ## self.vraag_dir.AppendItems(self.master.mru_items["dirs"])
            self.vraag_case.SetValue(self.master.p["case"])
            self.vraag_woord.SetValue(self.master.p["woord"])
            self.vraag_subs.SetValue(self.master.p["subdirs"])
            self.vraag_context.SetValue(self.master.p["context"])

    def zoekdir(self, event):
        """event handler voor 'zoek in directory'"""
        oupad = self.vraag_dir.GetValue()
        with wx.DirDialog(self, "Choose a directory:", defaultPath=oupad,
                          style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                self.vraag_dir.SetValue(dlg.GetPath())
