"""AFRIFT wxPython specific classes
"""
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


class AfriftGui(wx.Frame):
    """main screen
    """
    def __init__(self, master):
        self.master = master        # verwijzing naar Afrift - voor als het nodig is
        self.app = wx.App()
        super().__init__(None, title=self.master.title,
                         style=wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)
        self.SetIcon(wx.Icon(master.iconame, wx.BITMAP_TYPE_ICO))

    def init_screen(self):
        "set up screen for the various modes"
        self.pnl = wx.Panel(self)
        self.grid = wx.GridBagSizer()
        self.row = -1

    def add_combobox_row(self, label, choices, initial='', button=None, callback=None, **kwargs):
        "add a line with a combobox on it"
        self.row += 1
        lbl = wx.StaticText(self.pnl, label=label)
        self.grid.Add(lbl, (self.row, 0), flag=wx.EXPAND | wx.ALL, border=4)
        cmb = wx.ComboBox(self.pnl, size=(TXTW, TXTH), style=wx.CB_DROPDOWN, choices=choices)
        cmb.AutoComplete(choices)
        if initial:
            cmb.SetValue(initial)
        if button:
            btn = wx.Button(self.pnl, label=button[0], size=(-1, TXTH))
            btn.Bind(wx.EVT_BUTTON, button[1])
            hsizer = wx.BoxSizer(wx.HORIZONTAL)
            hsizer.Add(cmb, 0, wx.EXPAND)  # | wx.ALIGN_CENTER_VERTICAL)
            hsizer.Add(btn, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 4)
            self.grid.Add(hsizer, (self.row, 1), flag=wx.EXPAND | wx.TOP | wx.BOTTOM, border=2)
        else:
            self.grid.Add(cmb, (self.row, 1), flag=wx.ALIGN_CENTER_VERTICAL)
        if callback:
            cmb.Bind(wx.EVT_TEXT, callback)
        return cmb

    def add_checkbox_row(self, labeltext, value=None, indent=0, spinner=None, **kwargs):
        "add a line with a checkbox on it"
        self.row += 1
        vsizer = wx.BoxSizer(wx.VERTICAL)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hbsizer = wx.BoxSizer(wx.HORIZONTAL)
        cb = wx.CheckBox(self.pnl, label=labeltext)
        if value:
            cb.SetValue(value)
        if spinner:
            hbsizer.Add(cb, 0, wx.ALIGN_CENTER_VERTICAL)  # wx.TOP | wx.BOTTOM, 4)
            sb = wx.SpinCtrl(self.pnl, -1, min=spinner[1], initial=spinner[0], size=(122, TXTH))
            hbsizer.Add(sb, 0, wx.ALIGN_CENTER_VERTICAL)  # , 4)
        elif indent:
            hbsizer.Add(cb, 0, wx.LEFT, indent)
        else:
            hbsizer.Add(cb, 0)
        hsizer.Add(hbsizer, 0, wx.TOP | wx.BOTTOM, 4)
        vsizer.Add(hsizer, 0, wx.EXPAND)
        self.grid.Add(vsizer, (self.row, 1), flag=wx.EXPAND)
        if spinner:
            return cb, sb
        return cb

    def add_label_to_grid(self, text, fullwidth=False, new_row=False, left_align=False):
        "place a label"
        if new_row or fullwidth:
            self.row += 1
        if fullwidth:
            self.grid.Add(wx.StaticText(self.pnl, label=text), (self.row, 0), (1, 2),
                          flag=wx.EXPAND | wx.LEFT | wx.TOP, border=3)
        elif left_align:
            self.grid.Add(wx.StaticText(self.pnl, label=text), (self.row, 1),
                          flag=wx.EXPAND | wx.ALL, border=3)
        else:
            self.grid.Add(wx.StaticText(self.pnl, label=text), (self.row, 0),
                          flag=wx.EXPAND | wx.ALL, border=4)

    def add_listbox_to_grid(self, listitems):
        "place the listbox with the filenames"
        self.row += 1
        lb = wx.ListBox(self.pnl, size=(TXTW, 120), choices=listitems)
        self.grid.Add(lb, (self.row, 0), (1, 2), flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=4)
        return lb

    def add_buttons(self, buttondefs):
        "add the button strip at the bottom"
        self.row += 1
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        accel_list = []
        for ix, bdef in enumerate(buttondefs):
            text, callback = bdef
            btn = wx.Button(self.pnl, -1, size=(-1, TXTH), label=text)
            btn.Bind(wx.EVT_BUTTON, callback)
            hsizer.Add(btn, 0, wx.EXPAND | wx.ALL, 4)
            # menuitem = wx.MenuItem(None, wx.ID_ANY, text)
            menuitem = wx.MenuItem(None, text=text)
            self.Bind(wx.EVT_MENU, callback, menuitem)
            accel = wx.AcceleratorEntry(cmd=menuitem.GetId())
            ok = accel.FromString('Return' if ix == 0 else 'Ctrl+Q') # 'Escape')
            if ok:
                accel_list.append(accel)
        self.grid.Add(hsizer, (self.row, 0), (1, 3),
                      flag=wx.ALIGN_BOTTOM | wx.ALIGN_CENTER_HORIZONTAL, border=0)
        if accel_list:
            self.SetAcceleratorTable(wx.AcceleratorTable(accel_list))

    def set_focus_to(self, widget):
        "determine the input field to start from"
        widget.SetFocus()

    def get_combobox_value(self, cb):
        "return the selected/entered value from a combobox"
        return cb.GetValue()

    def get_checkbox_value(self, cb):
        "return the value from a checkbox"
        return cb.GetValue()

    def get_spinbox_value(self, sb):
        "return the value from a spinbox"
        return sb.GetValue()

    def go(self):
        "show screen and handle events"
        bsizer = wx.BoxSizer(wx.VERTICAL)
        bsizer.Add(self.grid, 0, wx.ALL, 4)
        self.pnl.SetAutoLayout(True)
        self.pnl.SetSizer(bsizer)
        bsizer.Fit(self)
        ## bsizer.SetSizeHints(self)
        self.pnl.Layout()
        self.Show(True)
        self.app.MainLoop()

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

    def add_item_to_searchlist(self, itemlist, item):
        "add string to list of items searched for"
        itemlist.Insert(item, 0)

    def set_waitcursor(self, value):
        """switch back and forth to a "busy" cursor
        """
        if value:
            wx.BeginBusyCursor()
        else:
            wx.EndBusyCursor()

    def einde(self, event=None):
        """applicatie afsluiten"""
        self.Close(True)

    def get_sender_value(self, *args):
        "return the text value from the callback"
        return args[0].GetEventObject().GetValue()

    def replace_combobox_items(self, cmb, itemlist):
        "repopulate a combobox's selection list"
        cmb.Clear()
        cmb.AppendItems(itemlist)
        if itemlist:
            cmb.SetValue(itemlist[0])

    def set_checkbox_value(self, cb, state):
        "set a checkbox's state"
        cb.SetValue(state)

    def zoekdir(self, event):
        """event handler voor 'zoek in directory'"""
        oupad = self.vraag_dir.GetValue()
        with wx.DirDialog(self, "Choose a directory:", defaultPath=oupad,
                          style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                self.vraag_dir.SetValue(dlg.GetPath())


class SelectNamesGui(wx.Dialog):
    """dialog for selecting directories/files
    """
    def __init__(self, parent, master):
        self.parent = parent
        self.master = master
        style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        super().__init__(parent.gui, title=self.master.title, style=style)
        self.SetIcon(wx.Icon(master.iconame, wx.BITMAP_TYPE_ICO))

    def setup_screen(self):
        "build widgets"
        self.vbox = wx.BoxSizer(wx.VERTICAL)

    def add_line(self):
        "start a new screen line"
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.vbox.Add(hbox, 0)
        return hbox

    def add_text_to_line(self, hbox, text):
        "show some fixed text on the current line"
        txt = wx.StaticText(self, label=text)
        hbox.Add(txt, 0, wx.EXPAND | wx.ALL, 5)

    def add_checkbox_to_line(self, hbox, text, callback):
        "show a checkbox on the current line"
        hbox.AddSpacer(10)
        cb = wx.CheckBox(self, label=text)
        cb.Bind(wx.EVT_CHECKBOX, callback)
        hbox.Add(cb, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 28)
        return cb

    def add_button_to_line(self, hbox, text, callback):
        "show a button on the current line"
        button = wx.Button(self, size=(-1, TXTH), label=text)
        button.Bind(wx.EVT_BUTTON, callback)
        # hbox.addStretch()
        hbox.Add(button, 0, wx.RIGHT, 7)
        # hbox.AddSpacer(20)
        return button

    def add_selectionlist(self, hbox, namelist):
        "show the list of names that can be selected"
        self.frm = wx.CheckListBox(self, -1, choices=namelist)
        hbox.Add(self.frm, 0, wx.LEFT | wx.RIGHT, 7)
        return self.frm.GetItems()

    def add_buttons(self, hbox, buttondefs, end=False):
        "add a button strip"
        box = wx.BoxSizer(wx.HORIZONTAL)
        for ix, bdef in enumerate(buttondefs):
            text, callback = bdef
            button = wx.Button(self, size=(-1, TXTH), label=text)
            if ix == 0:
                self.SetEscapeId(button.GetId())
            if ix == 1:
                button.Bind(wx.EVT_BUTTON, callback)
                # self.SetAffirmativeId(b_ok.GetId())
            box.Add(button, 0)
        if end:
            hbox.AddStretchSpacer()
        hbox.Add(box)  # , 0, wx.ALIGN_CENTER_HORIZONTAL)
        # hbox.AddStretchSpacer()

    def go(self):
        """show the dialog screen
        """
        self.SetAutoLayout(True)
        self.SetSizer(self.vbox)
        self.vbox.Fit(self)
        self.Layout()

        result = self.ShowModal()
        if result == wx.ID_OK:
            return True
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

    def cancel(self):
        "dialoog afbreken"
        self.EndModal(wx.ID_CANCEL)

    def confirm(self, event):
        "dialoog afsluiten"
        dirs = []
        for checked in self.frm.GetCheckedStrings():
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
        self.show_result_details = True  # wordt in master.__init__ op juiste waarde gezet
        self.vsizer = wx.BoxSizer(wx.VERTICAL)
        self.accel_list = []

    def add_line(self):
        "add a new line to the display"
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.vsizer.Add(hsizer, 0, wx.EXPAND)
        return hsizer

    def add_text_to_line(self, hsizer, text):
        "add some fixed text to a screen line"
        txt = wx.StaticText(self, label=text)
        hsizer.Add(txt, 0, wx.EXPAND | wx.ALL, 5)
        return txt

    def add_buttons_to_line(self, hsizer, buttondefs):
        "add one or more buttons to a screen line"
        for caption, callback, enable in buttondefs:
            btn = wx.Button(self, size=(-1, TXTH), label=caption)
            btn.Bind(wx.EVT_BUTTON, callback)
            hsizer.Add(btn, 0, wx.ALL, 5)
            btn.Enable(enable)

    def add_results_list(self, hsizer, headers, actiondefs, listitems):
        "add the list with results to a the display and return a reference to it"
        breedte = 50 if self.master.parent.apptype.startswith("single") else 150
        lijst = MyListCtrl(self, size=(breedte + 400, -1), style=wx.LC_REPORT)  #  | wx.LC_VRULES)
        for ix, caption in enumerate(headers):
            lijst.InsertColumn(ix, caption)
            lijst.SetColumnWidth(0, breedte if ix == 0 else 200)
        lijst.resizeLastColumn(200)
        self.populate_list(lijst, listitems)
        lijst.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.to_result)
        hsizer.Add(lijst, 1, wx.EXPAND | wx.ALL, 5)
        for caption, keydef, callback in actiondefs:
            menuitem = wx.MenuItem(None, text=caption)
            self.Bind(wx.EVT_MENU, callback, menuitem)
            accel = wx.AcceleratorEntry(cmd=menuitem.GetId())
            ok = accel.FromString(keydef)
            if ok:
                self.accel_list.append(accel)
        return lijst

    def add_checkbox_to_line(self, hsizer, caption, checkvalue):
        "show another checkbox on the current line and return a reference to it"
        cb = wx.CheckBox(self, label=caption)
        accel = wx.AcceleratorEntry(cmd=cb.GetId())
        ok = accel.FromString('Alt+O')  # uit caption afleiden
        if ok:
            self.accel_list.append(accel)
        cb.SetValue(checkvalue)
        hsizer.Add(cb)
        return cb

    def add_stretch_to_line(self, hsizer):
        "make the widgets align to the opposite side"
        hsizer.AddStretchSpacer()

    def disable_widget(self, widget):
        """make a widget inaccessible
        """
        widget.Enable(False)

    def finalize_display(self):
        "do layout and set window size"
        if self.accel_list:
            self.SetAcceleratorTable(wx.AcceleratorTable(self.accel_list))
        self.SetAutoLayout(True)
        self.SetSizer(self.vsizer)
        self.vsizer.Fit(self)
        # self.vsizer.SetSizeHints(self)
        self.Layout()
        self.Show()
        self.SetFocus()

    def populate_list(self, lijst, listitems):
        """copy results to listbox
        """
        for result in listitems[1:]:
            col = 0
            indx = lijst.InsertItem(sys.maxsize, result[0])
            lijst.SetItem(indx, col, result[0])
            if self.master.show_context:
                col += 1
                lijst.SetItem(indx, col, result[1])
            col += 1
            lijst.SetItem(indx, col, result[-1])

    def clear_contents(self):
        "remove all entries from list"
        self.lijst.DeleteAllItems()

    def go(self):
        """show the dialog screen
        """
        self.ShowModal()

    def set_header(self, widget, text):
        "set header for list"
        widget.SetLabel(text)

    def get_checkbox_value(self, widget):
        "return the state of a checkbox"
        return widget.GetValue()

    def get_savefile(self, title, dirname, fname, exts):
        """callback for button 'Copy to file'
        """
        # if ext == '.csv':
        #     f_filter = 'Comma delimited files (*.csv)|*.csv;;'
        # elif ext == '.txt':
        #     f_filter = 'Text files (*.txt)|*.txt;;'
        # f_filter = f"{f_filter}|All files (*.*)|*.*",
        f_filter = '|'.join([f'{oms} (*{ext})|*{ext}' for ext, oms in exts])
        fn = ''
        with wx.FileDialog(self, message="Resultaat naar bestand kopieren",
                           defaultDir=dirname,
                           defaultFile=fname,  # .join(('searchfor_', ".txt")),
                           wildcard=f_filter,
                           style=wx.FD_SAVE) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                fn = dlg.GetPath()
        return fn

    def meld(self, titel, message):
        "show an informational message"
        wx.MessageBox(message, titel, wx.OK | wx.ICON_INFORMATION, self)

    def get_text_from_user(self, titel, message):
        "pop up a dkialog to get user input"
        text = wx.GetTextFromUser(message, titel, parent=self)
        return text, bool(text)
        # or:
        # with wx.TextEntryDialog(self, titel, message) as dlg:
        #     ok = dlg.SetModal() == wx.ID_OK
        #     text = dlg.GetValue() if ok else None
        # return text, ok

    def get_selection(self):
        "get the selected lines"
        items = []
        texts = []
        item = self.lijst.GetFirstSelected()
        while item != -1:
            items.append(self.lijst.GetItem(item))
            item = self.lijst.GetNextSelected(item)
        texts = [x.GetText() for x in items]
        return texts

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

    def to_result(self, event):
        """show result in file
        """
        row = self.lijst.GetFirstSelected()
        if row == -1:
            self.meld(self.master.parent.resulttitel, 'Select a result first')
            return
        self.master.goto_result(row, -1)

    def klaar(self, event):
        """finish dialog
        """
        self.EndModal(0)
