# -*- coding: UTF-8 -*-
"""AFRIFT wxPython versie   - currently unmaintained
"""
import os
import sys
import wx
import contextlib
## from findr_files import Finder        # !! swap with next statement before testing
from findr_files_py2 import Finder # !! swap with previous statement before committing
from afrift_base import iconame, ABase, HERE

class SelectNames(wx.Dialog):
    """Tussenscherm om te verwerken files te kiezen"""

    def __init__(self, parent, ID,
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
            files=True):
        self.dofiles = files
        self.parent = parent
        self.results = []
        title = self.parent.title + " - file list"
        wx.Dialog.__init__(self, parent, ID, title, style = style)
        self.SetIcon(wx.Icon(iconame, wx.BITMAP_TYPE_ICO))
        vbox = wx.BoxSizer(wx.VERTICAL)

        if files:
            text = "Selecteer de bestanden die je *niet* wilt verwerken"
        else:
            text = "Selecteer de directories die je *niet* wilt verwerken"
        txt = wx.StaticText(self, -1, text)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(txt, 0, wx.EXPAND | wx.ALL, 5)
        vbox.Add(hbox, 0)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.frm = wx.CheckListBox(self, -1, choices=self.parent.names)
        hbox.Add(self.frm, 0)
        vbox.Add(hbox, 0)

        id_ = wx.NewId()
        b1 = wx.Button(self, id_, "&Klaar")
        ## self.Bind(wx.EVT_BUTTON, self.klaar, b1)
        b1.Bind(wx.EVT_BUTTON, self.klaar)
        self.SetAffirmativeId(id_)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(b1, 0)
        vbox.Add(hbox, 0, wx.ALIGN_CENTER_HORIZONTAL)

        self.SetAutoLayout(True)
        self.SetSizer(vbox)
        vbox.Fit(self)
        ## vsizer.SetSizeHints(self)
        self.Layout()

    def klaar(self, event):
        "dialoog afsluiten"
        dirs = []
        for checked in self.frm.CheckedStrings:
            print(checked)
            if self.dofiles:
                self.parent.names.remove(checked)
            else:
                dirs.append(checked)
        if not self.dofiles:
            self.parent.names = dirs
        self.EndModal(0)

class Results(wx.Dialog):
    """Resultaten scherm"""

    def __init__(
            self, parent, ID, title,
            ## size=wx.DefaultSize, pos=wx.DefaultPosition,
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
            ):
        self.parent = parent
        self.results = []
        if self.parent.apptype == "": # breedte linkerkolom
            breedte, titel = 300, 'File/Regel'
        elif self.parent.apptype == "single":
            breedte, titel = 50, 'Regel'
        elif self.parent.apptype == "multi":
            breedte, titel = 200, 'File/Regel'
        wx.Dialog.__init__(self, parent, ID, title, style = style)
        self.SetIcon(wx.Icon(iconame, wx.BITMAP_TYPE_ICO))

        #pnl = wx.Panel(self,-1)
        txt = wx.StaticText(self, -1, "{0} ({1} items)".format(
            self.parent.zoekvervang.rpt[0], len(self.parent.zoekvervang.rpt)-1))
        self.lijst = wx.ListCtrl(self, -1, size = (breedte + 385, 160),
            style = wx.LC_REPORT | wx.LC_VRULES,
            )
        self.lijst.InsertColumn(0, titel)
        self.lijst.SetColumnWidth(0, breedte)
        self.lijst.InsertColumn(1, "Data")
        self.lijst.SetColumnWidth(1, 380)
        self.populate_list()

        b2 = wx.Button(self, wx.ID_CANCEL, "&Klaar")
        ## self.Bind(wx.EVT_BUTTON, self.einde,  b2)
        b1 = wx.Button(self, -1, "&Copy to File")
        self.Bind(wx.EVT_BUTTON, self.kopie, b1)
        b3 = wx.Button(self, -1, "Copy to &Clipboard")
        self.Bind(wx.EVT_BUTTON, self.to_clipboard, b3)
        cb = wx.CheckBox(self, -1, label="toon directorypad in uitvoer")
        cb.SetValue(False)
        if self.parent.apptype == "single":
            cb.Enable(False)
        self.cb = cb

        vsizer = wx.BoxSizer(wx.VERTICAL)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(txt, 0, wx.EXPAND | wx.ALL, 5)
        vsizer.Add(hsizer, 0, wx.EXPAND)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(self.lijst, 1, wx.EXPAND | wx.ALL)
        vsizer.Add(hsizer, 1, wx.EXPAND)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        bsizer = wx.BoxSizer(wx.HORIZONTAL)
        bsizer.Add(b1, 0, wx.ALL, 5)
        bsizer.Add(b3, 0, wx.ALL, 5)
        bsizer.Add(b2, 0, wx.ALL, 5)
        bsizer.Add(cb, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        hsizer.Add(bsizer, 0)
        vsizer.Add(hsizer, 0, wx.ALIGN_CENTER_HORIZONTAL) # wx.EXPAND)

        self.SetAutoLayout(True)
        self.SetSizer(vsizer)
        vsizer.Fit(self)
        ## vsizer.SetSizeHints(self)
        self.Layout()
        self.Show(True)
        self.SetFocus()

    def populate_list(self):
        "resultaten in de listbox zetten"
        for ix, line in enumerate(self.parent.zoekvervang.rpt):
            if ix == 0:
                kop = line
            elif line != "":
                where, what = line.split(": ", 1)
                ## try:
                fname, lineno = where.rsplit("r. ", 1)
                ## except ValueError:
                    ## pass
                ## else:
                if self.parent.apptype == "single":
                    if ix == 1:
                        kop += " in {0}".format(fname)
                    where = lineno
                elif not self.parent.apptype:
                    where = where.replace(self.parent.p['pad'], '')[1:]
                i = self.lijst.InsertStringItem(sys.maxsize, where)
                self.lijst.SetStringItem(i, 0, where)
                try:
                    self.lijst.SetStringItem(i, 1, what)
                except UnicodeDecodeError as e:
                    self.lijst.SetStringItem(i, 1, ">> {0} <<".format(e))
                self.results.append((where, what))
        self.results.insert(0, kop)

    def get_results(self, toonpad):
        """apply switch to show complete path to results
        """
        text = ["{0}".format(self.results[0])]
        for r1, r2 in self.results[1:]:
            if toonpad:
                text.append("{0} {1}".format(r1, r2))
            else:
                text.append("{0} {1}".format(r1.split(os.sep)[-1], r2))
        return text

    def kopie(self, event=None):
        "callback for button 'Copy to file'"
        toonpad = self.cb.GetValue()
        f = self.parent.p["zoek"]
        for char in '/\\?%*:|"><.':
            if char in f:
                f = f.replace(char, "~")
        dlg = wx.FileDialog(self,
            message = "Resultaat naar bestand kopieren",
            defaultDir = self.parent.hier,
            defaultFile = f.join(('searchfor_', ".txt")),
            wildcard = "text files (*.txt)|*.txt|all files (*.*)|*.*",
            style = wx.SAVE
            )
        if dlg.ShowModal() == wx.ID_OK:
            fn = dlg.GetPath()
            with open(fn, "w") as f_out:
                for line in self.get_results(toonpad):
                    f_out.write(line + "\n")
        dlg.Destroy()

    def to_clipboard(self, event=None):
        """callback for button 'Copy to clipboard'
        """
        toonpad = True if self.cb.IsChecked() else False
        do = wx.TextDataObject()
        do.SetText('\n'.join([str(x) for x in self.get_results(toonpad)]))
        clp = wx.Clipboard.Get()
        if clp.Open():
            clp.SetData(do)
            clp.Close()
        else:
            wx.MessageBox("Unable to open the clipboard", "Error")

class MainFrame(wx.Frame, ABase):
    """Hoofdscherm van de applicatie"""

    def __init__(self, parent=None, apptype="", fnaam=""):
        app = wx.PySimpleApp(redirect=True, filename=os.path.join(
            os.path.dirname(HERE), 'logs', "afrift_wx.log"))
        ABase.__init__(self, parent, apptype, fnaam)
        wx.Frame.__init__(self, parent, wx.ID_ANY, self.title,
            style=wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE
            )
        self.setupscreen()
        app.MainLoop()

    def setupscreen(self):
        self.SetTitle(self.title)
        self.SetIcon(wx.Icon(iconame, wx.BITMAP_TYPE_ICO))
        self.pnl = wx.Panel(self, -1)

        TXTW = 200

        ## box = wx.StaticBox(self.pnl, -1)
        t1 = wx.StaticText(self.pnl, -1, "Zoek naar:")
        c1 = wx.ComboBox(self.pnl, -1, size=(TXTW, -1),
            choices=self._mru_items["zoek"],
            style=wx.CB_DROPDOWN
            )
        self.vraagZoek = c1

        t2 = wx.StaticText(self.pnl, -1, "Vervang door:")
        c2 = wx.ComboBox(self.pnl, -1, size=(TXTW, -1),
            choices=self._mru_items["verv"],
            style=wx.CB_DROPDOWN
            )
        self.vraagVerv = c2

        c3a = wx.CheckBox(self.pnl, -1, label="regular expression (Python format)")
        self.vraag_regex = c3a
        c3 = wx.CheckBox(self.pnl, -1, label="lege vervangtekst = weghalen")
        c3.SetValue(self._vervleeg)
        self.cVervang = c3
        c4 = wx.CheckBox(self.pnl, -1, label="hoofd/kleine letters gelijk")
        c4.SetValue(self.p["case"])
        self.vraagCase = c4
        c5 = wx.CheckBox(self.pnl, -1, label="hele woorden")
        c5.SetValue(self.p["woord"])
        self.vraagWoord = c5

        t = ""
        if self.apptype == "":
            t6 =  wx.StaticText(self.pnl, -1, "In directory:")
            c6 = wx.ComboBox(self.pnl, -1, size=(TXTW, -1),
                choices=self._mru_items["dirs"],
                style=wx.CB_DROPDOWN
                )
            self.vraagDir = c6
            self.Zoek = wx.Button(self.pnl, -1, label="&Zoek")
            self.Bind(wx.EVT_BUTTON, self.zoekdir, self.Zoek)
        elif self.apptype == "single":
            t6t = wx.StaticText(self.pnl, -1, "In file/directory:")
            t6 =  wx.StaticText(self.pnl, -1, self.fnames[0])
            t6b = wx.StaticText(self.pnl, -1, "", size = (120,-1))
        else:
            t = "van geselecteerde directories "

        if self.apptype != "single" or os.path.isdir(self.fnames[0]):
            c7 = wx.CheckBox(self.pnl, -1,
                label = t + "ook subdirectories doorzoeken",
                )
            c7.SetValue(self.p["subdirs"])
            self.vraagSubs = c7
            c7a = wx.CheckBox(self.pnl, -1, label="symlinks volgen")
            self.vraag_links = c7a
            t7b = wx.StaticText(self.pnl, -1, label =
                "    max. diepte (-1 is alles): ")
            c7b = wx.SpinCtrl(self.pnl, -1, size=(50, -1), min=-1, initial=5)
            self.vraag_diepte = c7b

            t8 =  wx.StaticText(self.pnl, -1, "alleen files van type:")
            c8 = wx.ComboBox(self.pnl, -1, size=(TXTW, -1),
                choices=self._mru_items["types"],
                style=wx.CB_DROPDOWN
                )
            self.vraagTypes = c8

        if self.apptype == "multi":
            t9 = wx.StaticText(self.pnl, -1, "In de volgende files/directories:")
            c9 = wx.ListBox(self.pnl, -1, size=(TXTW, -1), choices=self.fnames)
            self.lb = c9

        if self.apptype != "single" or os.path.isdir(self.fnames[0]):
            self.ask_skipdirs = wx.CheckBox(self.pnl, -1,
                label="selecteer (sub)directories om over te slaan")
            self.ask_skipfiles = wx.CheckBox(self.pnl, -1,
                label="selecteer bestanden om over te slaan")

        ## t10 =  wx.StaticText(self.pnl, -1,"", size=wid)
        c10 = wx.CheckBox(self.pnl, -1, label="gewijzigde bestanden backuppen")
        c10.SetValue(self._backup)
        self.vraagBackup = c10
        c11 = wx.CheckBox(self.pnl, -1, label="direct afsluiten na vervangen")
        c11.SetValue(self._exit_when_ready)
        self.vraag_exit = c11

        self.DoIt = wx.Button(self.pnl, -1, label="&Uitvoeren")
        self.Bind(wx.EVT_BUTTON, self.doe, self.DoIt)
        ## self.Cancel = wx.Button(self.pnl,  wx.ID_CANCEL, "&Einde") # helpt niet
        self.Cancel = wx.Button(self.pnl, -1, label="&Einde")
        self.Bind(wx.EVT_BUTTON, self.einde, self.Cancel)

        bsizer = wx.BoxSizer(wx.VERTICAL)
        gbsizer = wx.GridBagSizer(4)
        row = 0
        gbsizer.Add(t1, (row, 0), flag=wx.EXPAND | wx.ALL, border=4)
        gbsizer.Add(c1, (row, 1), flag=wx.ALIGN_CENTER_VERTICAL)
        gbsizer.Add(wx.StaticText(self.pnl, -1,"", size=(20, -1)), (row, 2))
        row += 1
        gbsizer.Add(t2, (row, 0), flag=wx.EXPAND | wx.ALL, border=4)
        gbsizer.Add(c2, (row, 1), flag=wx.ALIGN_CENTER_VERTICAL)
        row += 1
        vsizer = wx.BoxSizer(wx.VERTICAL)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hbsizer = wx.BoxSizer(wx.HORIZONTAL)
        hbsizer.Add(c3a, 0)
        hsizer.Add(hbsizer, 0, wx.TOP | wx.BOTTOM, 4)
        vsizer.Add(hsizer, 0, wx.EXPAND)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hbsizer = wx.BoxSizer(wx.HORIZONTAL)
        hbsizer.Add(c3, 0)
        hsizer.Add(hbsizer, 0, wx.TOP | wx.BOTTOM, 4)
        vsizer.Add(hsizer, 0, wx.EXPAND)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hbsizer = wx.BoxSizer(wx.HORIZONTAL)
        hbsizer.Add(c4, 0)
        hsizer.Add(hbsizer, 0, wx.TOP | wx.BOTTOM, 4)
        vsizer.Add(hsizer, 0, wx.EXPAND)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hbsizer = wx.BoxSizer(wx.HORIZONTAL)
        hbsizer.Add(c5, 0)
        hsizer.Add(hbsizer, 0, wx.TOP | wx.BOTTOM, 4)
        vsizer.Add(hsizer, 0, wx.EXPAND)
        gbsizer.Add(vsizer, (row, 1)) #,(1, 2))
        if self.apptype == "":
            row += 1
            gbsizer.Add(t6, (row, 0), flag=wx.EXPAND | wx.ALL, border=4)
            hsizer = wx.BoxSizer(wx.HORIZONTAL)
            hsizer.Add(c6, 0, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
            hsizer.Add(self.Zoek, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 4 )
            gbsizer.Add(hsizer, (row, 1), flag=wx.EXPAND | wx.TOP | wx.BOTTOM,
                border=2)
        elif self.apptype == "single":
            row += 1
            gbsizer.Add(t6t, (row, 0), flag=wx.EXPAND | wx.ALL, border=4)
            gbsizer.Add(t6, (row, 1), flag=wx.EXPAND | wx.ALL, border=4)
            gbsizer.Add(t6b, (row,2), flag=wx.EXPAND | wx.ALL, border=4)
        if self.apptype != "single" or os.path.isdir(self.fnames[0]):
            row += 1
            gbsizer.Add(c7, (row, 1), flag=wx.EXPAND | wx.TOP | wx.BOTTOM, border=2)
            row += 1
            hsizer = wx.BoxSizer(wx.HORIZONTAL)
            hsizer.Add(c7a, 0, wx.ALIGN_CENTER_VERTICAL) # wx.TOP | wx.BOTTOM, 4)
            hsizer.Add(t7b, 0, wx.ALIGN_CENTER_VERTICAL) # wx.TOP | wx.BOTTOM, 4)
            hsizer.Add(c7b, 0, wx.ALIGN_CENTER_VERTICAL) #, 4)
            gbsizer.Add(hsizer, (row, 1), flag=wx.EXPAND | wx.TOP | wx.BOTTOM,
                border=2)
            row += 1
            gbsizer.Add(t8, (row, 0), flag=wx.EXPAND | wx.ALL, border=4)
            gbsizer.Add(c8, (row, 1), flag=wx.ALIGN_CENTER_VERTICAL)
        if self.apptype == "multi":
            row += 1
            gbsizer.Add(t9, (row, 0), (1, 2),
                flag=wx.EXPAND | wx.LEFT | wx.TOP, border=4)
            row += 1
            gbsizer.Add(c9, (row, 0), (1, 2),
                flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=4)
        if self.apptype != "single" or os.path.isdir(self.fnames[0]):
            row += 1
            gbsizer.Add(self.ask_skipdirs, (row, 1), flag=wx.EXPAND)
            row += 1
            gbsizer.Add(self.ask_skipfiles, (row, 1), flag=wx.EXPAND)
        row += 1
        gbsizer.Add(c10, (row, 1), flag = wx.EXPAND)
        row += 1
        gbsizer.Add(c11, (row, 1), flag = wx.EXPAND)
        row += 1
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(self.DoIt, 0, wx.EXPAND | wx.ALL, 4)
        hsizer.Add(self.Cancel, 0, wx.EXPAND | wx.ALL, 4)
        gbsizer.Add(hsizer, (row, 0), (1, 3), flag = wx.ALIGN_BOTTOM | wx.ALIGN_CENTER_HORIZONTAL,
            border=0)
        bsizer.Add(gbsizer, 0, wx.ALL, 4)

        ## self.pnl.SetAutoLayout(True)
        self.pnl.SetSizer(bsizer)
        bsizer.Fit(self)
        ## bsizer.SetSizeHints(self)

        self.pnl.Layout()
        self.vraagZoek.SetFocus()
        self.noescape = False
        self.Bind(wx.EVT_KEY_UP, self.on_key_up)
        ## for win in self.GetChildren():
            ## self.Bind(wx.EVT_KEY_UP,self.on_key_up,win)
        self.Show(True)
        self.SetFocus()

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

    def doe(self, event=None):
        """Invoer controleren, indien ok zoekactie uitvoeren en resultaatscherm tonen"""
        mld = self.checkzoek(self.vraagZoek.GetValue())
        if not mld:
            self.checkverv(self.vraagVerv.GetValue(), self.cVervang.GetValue())
            self.checkattr(self.vraag_regex.GetValue(), self.vraagCase.GetValue(),
                self.vraagWoord.GetValue())
            try:
                b = self.vraagTypes.GetValue()
            except AttributeError:
                b = None
            if b:
                self.checktype(b)
            if not self.apptype:
                mld = self.checkpath(self.vraagDir.GetValue())
        if not mld:
            try:
                self.checksubs(self.vraagSubs.GetValue(),
                    self.vraag_links.GetValue(), self.vraag_diepte.GetValue())
            except AttributeError:
                pass
        self.p["backup"] = self.vraagBackup.GetValue()
        self.p["fallback_encoding"] = self._fallback_encoding

        if mld:
            dlg = wx.MessageDialog(self, mld, self.fouttitel, wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # TODO: find out why json.dump doesn't work in Py 2 and fix it
        ## self.schrijfini()
        print "\ninitializing zoekvervang class"
        self.zoekvervang = Finder(**self.p)
        if not self.zoekvervang.filenames:
            dlg = wx.MessageDialog(self, "Geen bestanden gevonden", self.resulttitel,
                wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return

        if self.apptype == "single" or (
                len(self.fnames) == 1 and os.path.isfile(self.fnames[0])):
            pass
        else:
            ## print(self.skipdirs_overslaan, self.skipfiles_overslaan)
            if self.ask_skipdirs.IsChecked():
                # eerste ronde: toon directories
                if self.zoekvervang.dirnames:
                    self.names = sorted(self.zoekvervang.dirnames)
                    dlg = SelectNames(self, -1, files=False)
                    dlg.ShowModal()
                    dlg.Destroy()
                    # tweede ronde: toon de files die overblijven
                    fnames = self.zoekvervang.filenames[:]
                    for name in self.names:
                        for fname in fnames:
                            if fname.startswith(name + '/'):
                                self.zoekvervang.filenames.remove(fname)
            if self.ask_skipfiles.IsChecked():
                self.names = self.zoekvervang.filenames
                dlg = SelectNames(self, -1)
                dlg.ShowModal()
                dlg.Destroy()
                self.zoekvervang.filenames = self.names

        self.zoekvervang.do_action()

        self.noescape = True
        if len(self.zoekvervang.rpt) == 1:
            txt = "Niks gevonden" if self.zoekvervang.ok else self.zoekvervang.rpt[0]
            dlg = wx.MessageDialog(self, txt, self.resulttitel,
                wx.OK | wx.ICON_INFORMATION)
        else:
            dlg = Results(self, -1, self.resulttitel)
        dlg.ShowModal()
        dlg.Destroy()
        if self.vraag_exit.GetValue() and self.p["vervang"] is not None:
            self.einde()

    def zoekdir(self, event):
        """event handler voor 'zoek in directory'"""
        oupad = self.vraagDir.GetValue()
        dlg = wx.DirDialog(self, "Choose a directory:",
            defaultPath = oupad,
            style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST
            )
        if dlg.ShowModal() == wx.ID_OK:
            self.vraagDir.SetValue(dlg.GetPath())
        dlg.Destroy()

if __name__ == "__main__":
    MainFrame()
