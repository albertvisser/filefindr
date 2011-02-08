#! /usr/bin/env python3
# -*- coding: latin1 -*-
"""AFRIFT Tkinter versie"""

import os
import sys
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as tkMessageBox
import tkinter.filedialog as tkFileDialog

from findr_files import findr
from afrift_base import iconame, ABase

class Results(tk.Toplevel):
    "Resultatenscherm"

    def __init__(self, parent):
        self.parent = parent
        tk.Toplevel.__init__(self)
        self.title(self.parent.resulttitel)
        ## self.wm_iconbitmap(iconame)

        self.toonpad = tk.IntVar()
        self.showpath = False

        frm = tk.Frame(self)
        frm.pack(fill=tk.X)
        txt = "{0} ({1} items)".format(self.parent.zoekvervang.rpt[0],
            len(self.parent.zoekvervang.rpt)-1)
        tk.Label(frm, text=txt, anchor=tk.W).pack(side=tk.LEFT,
            fill=tk.X, expand=True, padx=5)
        frm = tk.Frame(self)
        frm.pack(fill=tk.BOTH, expand=True)
        self.scrollY = tk.Scrollbar(frm, orient=tk.VERTICAL)
        self.scrollX = tk.Scrollbar(frm, orient=tk.HORIZONTAL)
        if self.parent.apptype == "":
            b = 50
        elif self.parent.apptype == "single":
            b = 10
        elif self.parent.apptype == "multi":
            b = 40
        self.scrollX.config(command=self.list_xview)
        self.scrollX.pack(side=tk.BOTTOM, fill=tk.X)
        frm2 = tk.PanedWindow(frm, orient=tk.HORIZONTAL)
        frm2.pack()
        p2l = tk.Frame(frm2)
        p2l.pack()
        frm2.add(p2l)
        p2r = tk.Frame(frm2)
        p2r.pack()
        frm2.add(p2r)
        self.results = tk.Listbox(p2l, setgrid=tk.YES, width=b,
            takefocus=False,
            yscrollcommand=self.scrollY.set,
            xscrollcommand=self.scrollX.set
            )
        self.results_data = tk.Listbox(p2r, setgrid=tk.YES, width=60,
            takefocus=False,
            yscrollcommand=self.scrollY.set,
            xscrollcommand=self.scrollX.set
            )
        self.kop = self.populate_list()
        self.scrollY.config(command=self.list_yview)
        self.scrollY.pack(side=tk.RIGHT, fill=tk.Y)
        self.results.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.results_data.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        frm2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        frm = tk.Frame(self, height=12)
        frm.pack()
        klaar = tk.Button(frm, text="Klaar", command=self.einde)
        klaar.pack(side=tk.LEFT, padx=5, pady=5)
        klaar.bind("<Return>", self.einde)
        kopie = tk.Button(frm, text="Copy to File", command=self.kopie)
        kopie.pack(side=tk.LEFT, padx=5, pady=5)
        kopie.bind("<Return>", self.kopie)
        self.toonpad.set(int(self.showpath))
        tk.Label(frm, text="", width=2).pack(side=tk.LEFT)
        self.vraagPad = tk.Checkbutton(frm,
            text="toon directorypad in uitvoer",
            variable=self.toonpad
            )
        self.vraagPad.pack(side=tk.LEFT)
        self.bind_all("<Prior>", self.w_pgup)
        self.bind_all("<Next>", self.w_pgdn)
        self.bind_all("<Escape>", self.einde)

    def populate_list(self):
        "resultaten in de listboxes zetten"
        kop = ""
        for ix, item in enumerate(self.parent.zoekvervang.rpt):
            if ix == 0:
                kop = item
            elif item != "":
                where, what = item.split(": ",1)
                if self.parent.apptype == "single":
                    fname, lineno = where.split("r.",1)
                    if ix == 1:
                        kop += " in {0}".format(fname)
                    where = lineno
                self.results.insert(tk.END, where)
                self.results_data.insert(tk.END, what)
        return kop

    def w_pgup(self, event):
        "omhoog bladeren"
        self.results.yview(tk.SCROLL, -1, tk.PAGES)
        self.results_data.yview(tk.SCROLL, -1, tk.PAGES)

    def w_pgdn(self, event):
        "omlaag bladeren"
        self.results.yview(tk.SCROLL, 1, tk.PAGES)
        self.results_data.yview(tk.SCROLL, 1, tk.PAGES)

    def list_yview(self, *args):
        "sync yview voor listboxes"
        self.results.yview(*args)
        self.results_data.yview(*args)

    def list_xview(self, *args):
        "sync xview voor listboxes"
        self.results.xview(*args)
        self.results_data.xview(*args)

    def einde(self, event=None):
        "resultaatscherm afsluiten"
        self.destroy()
        self.parent.master.bind_all("<Escape>", self.parent.einde)
        self.parent.master.unbind_all("<Prior>")
        self.parent.master.unbind_all("<Next>")
        self.parent.master.lift()

    def kopie(self, event=None):
        "resultaten naar bestand kopieren"
        self.showpath = bool(self.toonpad.get())
        f = self.parent.p["zoek"]
        for char in '/\\?%*:|"><.':
            if char in f:
                f = f.replace(char, "~")
        f +=  ".txt"
        fn = tkFileDialog.asksaveasfilename(title="Resultaat naar bestand kopieren",
                                            parent=self,
                                            initialdir=self.parent.hier,
                                            initialfile=f,
                                            defaultextension=".txt",
                                            filetypes=[("text files",".txt"),("all files","*")])
        if fn != "":
            fl = file(fn, "w")
            r1 = self.results.get(0, tk.END)
            r2 = self.results_data.get(0, tk.END)
            fl.write("%s\n" % self.kop)
            for i in range(len(r1)):
                if self.showpath:
                    fl.write("%s %s\n" % (r1[i], r2[i]))
                else:
                    s2 = r1[i].split("\\")
                    fl.write("%s %s\n" % (s2[-1], r2[i]))
            fl.close()

class MainFrame(ABase):
    """Hoofdscherm van de applicatie"""

    def __init__(self, parent=None, apptype="", data=""):
        ABase.__init__(self, parent, apptype, data)

        self.zoekstr = tk.StringVar()
        self.zoekstr.set('')
        self.vervstr = tk.StringVar()
        self.vervstr.set('')
        self.typestr = tk.StringVar()
        self.typestr.set('')
        self.dirnaam = tk.StringVar()
        self.dirnaam.set('')
        self.case = tk.IntVar()
        self.case.set(self.p["case"])
        self.vervleeg = tk.IntVar()
        self.vervleeg.set(self._vervleeg)
        self.word = tk.IntVar()
        self.word.set(self.p["woord"])
        self.subdirs = tk.IntVar()
        self.subdirs.set(self.p["subdirs"])
        self.backup = tk.IntVar()
        self.backup.set(self._backup)

        self.parent.title(self.title)
        ## self.parent.wm_iconbitmap("@"+iconame)
        self.master = tk.Frame(self.parent)
        self.master.pack()
        frm = tk.Frame(self.master)
        frm.pack(fill=tk.BOTH, expand=True)
        tk.Label(frm, text = "Zoek naar:", width=17).pack(side=tk.LEFT)
        self.vraagZoek = ttk.Combobox(frm,
            values = self._mruItems["zoek"],
            width = 40,
            textvariable = self.zoekstr,
            )
        self.vraagZoek.pack(side=tk.LEFT, padx=5, pady=5)
        frm = tk.Frame(self.master)
        frm.pack(fill=tk.BOTH, expand=True)
        tk.Label(frm, text = "Vervang door:", width=17).pack(side=tk.LEFT)
        self.vraagVerv = ttk.Combobox(frm,
            values = self._mruItems["verv"],
            width = 40,
            textvariable = self.vervstr,
            )
        self.vraagVerv.pack(side=tk.LEFT, padx=5, pady=5)
        frm = tk.Frame(self.master)
        frm.pack(fill=tk.BOTH, expand=True)
        tk.Label(frm, text="", width=17).pack(side=tk.LEFT)
        self.cVervang = tk.Checkbutton(frm,
            text="lege vervangtekst = weghalen",
            variable=self.vervleeg)
        self.cVervang.pack(side=tk.LEFT)
        frm = tk.Frame(self.master)
        frm.pack(fill=tk.BOTH, expand=True)
        tk.Label(frm, text="", width=17).pack(side=tk.LEFT)
        self.vraagCase = tk.Checkbutton(frm,
            text="hoofd/kleine letters gelijk",
            variable=self.case
            )
        self.vraagCase.pack(side=tk.LEFT)
        frm = tk.Frame(self.master)
        frm.pack(fill=tk.BOTH, expand=True)
        tk.Label(frm, text="", width=17).pack(side=tk.LEFT)
        self.vraagWoord = tk.Checkbutton(frm,
            text="hele woorden",
            variable=self.word
            )
        self.vraagWoord.pack(side=tk.LEFT)
        t = ""
        if self.apptype == "":
            frm = tk.Frame(self.master)
            frm.pack(fill=tk.BOTH, expand=True)
            tk.Label(frm, text="In directory:", width=17).pack(side=tk.LEFT)
            self.vraagDir = ttk.Combobox(frm,
                values = self._mruItems["dirs"],
                width = 40,
                textvariable = self.dirnaam,
                )
            self.vraagDir.pack(side=tk.LEFT, padx=5, pady=5)
            self.Zoek = tk.Button(frm, text="Zoek", command=self.zoekdir)
            self.Zoek.pack(side=tk.LEFT, padx=5)
            tk.Label(frm, text="").pack(side=tk.RIGHT)
        elif self.apptype == "single":
            frm = tk.Frame(self.master)
            frm.pack(fill=tk.BOTH, expand=True)
            tk.Label(frm, text="In file/directory", width=17).pack(side=tk.LEFT)
            tk.Label(frm, text=self.fnames[0]).pack(side=tk.LEFT)
            tk.Label(frm, text="").pack(side=tk.RIGHT)
        else:
            t = "van geselecteerde directories "
        if self.apptype != "single" or os.path.isdir(self.fnames[0]):
            frm = tk.Frame(self.master)
            frm.pack(fill=tk.BOTH, expand=True)
            tk.Label(frm, text="", width=17).pack(side=tk.LEFT)
            self.vraagSubs = tk.Checkbutton(frm,
                text = t + "ook subdirectories doorzoeken    ",
                variable=self.subdirs,
                )
            self.vraagSubs.pack(side=tk.LEFT)
            frm = tk.Frame(self.master)
            frm.pack(fill=tk.BOTH, expand=True)
            tk.Label(frm, text = "alleen files van type:", width=17).pack(side=tk.LEFT)
            self.vraagTypes = ttk.Combobox(frm,
                values = self._mruItems["types"],
                width = 40,
                textvariable = self.typestr,
                )
            self.vraagTypes.pack(side=tk.LEFT, padx=5, pady=5)
        frm = tk.Frame(self.master)
        frm.pack(fill=tk.BOTH, expand=True)
        if self.apptype == "multi":
            sl = tk.Frame(frm)
            sl.pack(fill=tk.BOTH, expand=True)
            tk.Label(sl, text='In de volgende files/directories:').pack(side = tk.LEFT)
            self.lb = tk.ScrolledText(sl,
                    height=12,
                    takefocus=False
            )
            for name in self.names:
                self.lb.insert(tk.END, name)
            self.lb.pack(fill=tk.X, expand=True)
            lt = tk.Frame(frm)
            lt.pack(fill=tk.BOTH, expand=True)
        frm = tk.Frame(self.master)
        frm.pack(fill=tk.BOTH, expand=True)
        tk.Label(frm, text="", width=17).pack(side=tk.LEFT)
        self.vraagBackup = tk.Checkbutton(frm,
            text = "gewijzigde bestanden backuppen",
            variable=self.backup,
            )
        self.vraagBackup.pack(side=tk.LEFT)
        frm = tk.Frame(self.master)
        frm.pack()
        self.DoIt = tk.Button(frm, text="Uitvoeren", command=self.doe)
        self.DoIt.pack(side=tk.LEFT, padx=5, pady=5)
        self.master.bind_all("<Return>", self.doe)
        self.vraagZoek.focus_set()
        self.Cancel = tk.Button(frm, text="Einde", command=self.master.quit)
        self.Cancel.pack(side=tk.LEFT, padx=5, pady=5)
        self.master.bind_all("<Escape>", self.einde)

    def einde(self, event):
        """applicatie afsluiten"""
        self.master.quit()

    def doe(self, event=None):
        """Zoekactie uitvoeren en resultaatscherm tonen"""

        mld = self.checkzoek(self.zoekstr.get())

        if not mld:
            self.checkverv(self.vervstr.get(), self.vervleeg.get())
            self.checkattr(bool(self.case.get()), bool(self.word.get()))
            try:
                item = self.typestr.get()
            except AttributeError:
                b = None
            if item:
                self.checktype(item)
            if not self.apptype:
                mld = self.checkpath(self.dirnaam.get())

        if not mld:
            try:
                self.checksubs(bool(self.subdirs.get()))
            except AttributeError:
                pass

        self.p["backup"] = bool(self.backup.get())

        if mld:
            tkMessageBox.showerror(self.fouttitel, mld)
            return

        self.schrijfini()
        self.zoekvervang = findr(**self.p)

        if len(self.zoekvervang.rpt) == 2:
            tkMessageBox.showinfo(self.resulttitel, "Niks gevonden")
        else:
            w = Results(self)
            w.focus_set()
            w.grab_set()
            w.wait_window()

    def zoekdir(self):
        """event handler voor 'zoek in directory'"""
        oupad = self.dirnaam.get()
        if oupad == "":
            pad = tkFileDialog.askdirectory()
        else:
            pad = tkFileDialog.askdirectory(initialdir=oupad)
        if pad != "":
            self.dirnaam.set(pad)

def test():
    "test routine"
    root = tk.Tk()
    ## MainFrame(root)
    MainFrame(root, "single", '/home/visser/Python/filefindr/afrift/afrift_gui.py')
    ## MainFrame(root, 'multi', 'CMDAE.tmp')
    root.mainloop()

if __name__ == "__main__":
    test()
