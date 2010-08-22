#! /usr/bin/env python3
# -*- coding: latin1 -*-
"""AFRIFT Tkinter versie"""

import os
import sys
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.scrolledtext import ScrolledText
import tkinter.messagebox as tkMessageBox
import tkinter.filedialog as tkFileDialog
## import Pmw
from findr_files import findr
from afrift_base import iconame, ABase

class Results(tk.Toplevel):
    "Resultatenscherm"

    def __init__(self, parent):
        self.parent = parent
        tk.Toplevel.__init__(self)
        self.title(self.parent.resulttitel)
        ## self.wm_iconbitmap(iconame)
        rpt = self.parent.zoekvervang.rpt

        self.toonpad = tk.IntVar()
        self.showpath = False

        f1 = tk.Frame(self)
        f1.pack(fill=tk.X)
        txt = "%s (%i items)" % (rpt[0], len(rpt)-1)
        tk.Label(f1, text=txt, anchor=tk.W).pack(side=tk.LEFT,
            fill=tk.X, expand=True, padx=5)
        f2 = tk.Frame(self)
        f2.pack(fill=tk.BOTH, expand=tk.YES)
        self.scrollY = tk.Scrollbar(f2, orient=tk.VERTICAL)
        self.scrollX = tk.Scrollbar(f2, orient=tk.HORIZONTAL)
        if self.parent.apptype == "":
            b = 50
        elif self.parent.apptype == "single":
            b = 10
        elif self.parent.apptype == "multi":
            b = 40
        self.scrollX.config(command=self.list_xview)
        self.scrollX.pack(side=tk.BOTTOM, fill=tk.X)
        f2a = tk.PanedWindow(f2, orient=tk.HORIZONTAL)
        f2a.pack()
        p2l = tk.Frame(f2a)
        p2l.pack()
        f2a.add(p2l) # "In file")
        p2r = tk.Frame(f2a)
        p2r.pack()
        f2a.add(p2r) # "Data")
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
        n = 0
        self.z = " "
        for x in rpt:
            if n == 0:
                self.z = x
            else:
                i = x.find(": ")
                r = x[:i]
                if self.parent.apptype == "single":
                    j = r.find("r.")
                    if n == 1:
                        self.z = self.z + " in " + r[:j]
                    r = r[j:]
                self.results.insert(tk.END, r)
                self.results_data.insert(tk.END, x[i+2:])
            n += 1
        self.scrollY.config(command=self.list_yview)
        self.scrollY.pack(side=tk.RIGHT, fill=tk.Y)
        self.results.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.results_data.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        f2a.pack(side=tk.LEFT, fill=tk.BOTH, expand=True) # fill=tk.BOTH, expand=True)
        ## f2a.setnaturalsize()
        f3 = tk.Frame(self, height=12)
        f3.pack()
        klaar = tk.Button(f3, text="Klaar", command=self.einde)
        klaar.pack(side=tk.LEFT, padx=5, pady=5)
        klaar.bind("<Return>", self.einde)
        kopie = tk.Button(f3, text="Copy to File", command=self.kopie)
        kopie.pack(side=tk.LEFT, padx=5, pady=5)
        kopie.bind("<Return>", self.kopie)
        self.toonpad.set(int(self.showpath))
        tk.Label(f3, text="", width=2).pack(side=tk.LEFT)
        self.vraagPad = tk.Checkbutton(f3,
            text="toon directorypad in uitvoer",
            variable=self.toonpad
            )
        self.vraagPad.pack(side=tk.LEFT)
        self.bind_all("<Prior>", self.w_pgup)
        self.bind_all("<Next>", self.w_pgdn)
        self.bind_all("<Escape>", self.einde)

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
        self.parent.master.bind_all("<Escape>", self.einde)
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
            fl.write("%s\n" % self.z)
            for i in range(len(r1)):
                if self.showpath:
                    fl.write("%s %s\n" % (r1[i], r2[i]))
                else:
                    s2 = r1[i].split("\\")
                    fl.write("%s %s\n" % (s2[-1], r2[i]))
            fl.close()
        ## self.w.focus_set()
        ## self.w.grab_set()
        ## self.w.wait_window()

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
        self.fZoek = tk.Frame(self.master)
        self.fZoek.pack(fill=tk.BOTH, expand=True)
        tk.Label(self.fZoek, text = "Zoek naar:", width=17).pack(side=tk.LEFT)
        self.vraagZoek = ttk.Combobox(self.fZoek,
            values = self._mruItems["zoek"],
            width = 40,
            textvariable = self.zoekstr,
            ## listbox_bg="#ffffff",
            ## labelpos = "wn",
            ## label_anchor=W,
            ## label_justify=LEFT
            )
        self.vraagZoek.pack(side=tk.LEFT, padx=5, pady=5)
        ## self.vraagZoek.bind("<Next>",self.Zoek_dropdown)
        self.fVerv = tk.Frame(self.master)
        self.fVerv.pack(fill=tk.BOTH, expand=True)
        tk.Label(self.fVerv, text = "Vervang door:", width=17).pack(side=tk.LEFT)
        self.vraagVerv = ttk.Combobox(self.fVerv,
            values = self._mruItems["verv"],
            width = 40,
            textvariable = self.vervstr,
            ## listbox_bg="#ffffff",
            ## labelpos = "wn",
            ## label_text = "Vervang door:",
            ## label_width=17,
            ## label_anchor=W,
            ## label_justify=LEFT
            )
        self.vraagVerv.pack(side=tk.LEFT, padx=5, pady=5)
        ## self.vraagVerv.bind("<Next>",self.Verv_dropdown)
        self.fOpt0 = tk.Frame(self.master)
        self.fOpt0.pack(fill=tk.BOTH, expand=True)
        tk.Label(self.fOpt0, text="", width=17).pack(side=tk.LEFT)
        self.cVervang = tk.Checkbutton(self.fOpt0,
            text="lege vervangtekst = weghalen",
            variable=self.vervleeg)
        self.cVervang.pack(side=tk.LEFT)
        self.fOpt1 = tk.Frame(self.master)
        self.fOpt1.pack(fill=tk.BOTH, expand=True)
        tk.Label(self.fOpt1, text="", width=17).pack(side=tk.LEFT)
        self.vraagCase = tk.Checkbutton(self.fOpt1,
            text="hoofd/kleine letters gelijk",
            variable=self.case
            )
        self.vraagCase.pack(side=tk.LEFT)
        self.fOpt2 = tk.Frame(self.master)
        self.fOpt2.pack(fill=tk.BOTH, expand=True)
        tk.Label(self.fOpt2, text="", width=17).pack(side=tk.LEFT)
        self.vraagWoord = tk.Checkbutton(self.fOpt2,
            text="hele woorden",
            variable=self.word
            )
        self.vraagWoord.pack(side=tk.LEFT)
        if self.apptype == "":
            self.fDir = tk.Frame(self.master)
            self.fDir.pack(fill=tk.BOTH, expand=True)
            tk.Label(self.fDir, text="In directory:", width=17).pack(side=tk.LEFT)
            self.vraagDir = ttk.Combobox(self.fDir,
                values = self._mruItems["dirs"],
                ## arrowbutton_takefocus = False,
                width = 40,
                textvariable = self.dirnaam,
                ## listbox_bg="#ffffff",
                ## labelpos = "wn",
                ## label_text = "In directory:",
                ## label_width=17,
                ## label_anchor=W,
                ## label_justify=LEFT
                )
            self.vraagDir.pack(side=tk.LEFT, padx=5, pady=5)
            self.Zoek = tk.Button(self.fDir, text="Zoek", command=self.zoekdir)
            self.Zoek.pack(side=tk.LEFT, padx=5)
            tk.Label(self.fDir, text="").pack(side=tk.RIGHT)
            t = ""
        else:
            t = "van geselecteerde directories "
        self.fOpt3 = tk.Frame(self.master)
        self.fOpt3.pack(fill=tk.BOTH, expand=True)
        tk.Label(self.fOpt3, text="", width=17).pack(side=tk.LEFT)
        self.vraagSubs = tk.Checkbutton(self.fOpt3,
            text = t + "ook subdirectories doorzoeken    ",
            variable=self.subdirs,
            )
        self.vraagSubs.pack(side=tk.LEFT)
        self.fTypes = tk.Frame(self.master)
        self.fTypes.pack(fill=tk.BOTH, expand=True)
        tk.Label(self.fTypes, text = "alleen files van type:", width=17).pack(side=tk.LEFT)
        self.vraagTypes = ttk.Combobox(self.fTypes,
            values = self._mruItems["types"],
            width = 40,
            textvariable = self.typestr,
            ## listbox_bg="#ffffff",
            ## labelpos = "wn",
            ## label_text = "alleen files van type:",
            ## label_width=17,
            ## label_anchor=W,
            ## label_justify=LEFT
            )
        self.vraagTypes.pack(side=tk.LEFT, padx=5, pady=5)
        self.fExe = tk.Frame(self.master)
        self.fExe.pack(fill=tk.BOTH, expand=True)
        if self.apptype == "multi":
            sl = tk.Frame(self.fExe)
            sl.pack(fill=tk.BOTH, expand=True)
            tk.Label(sl, text='In de volgende files/directories:').pack(side = tk.LEFT)
            self.lb = tk.ScrolledText(sl,
                    ## items=self.fnames,
                    ## labelpos='nw',
                    ## label_text='In de volgende files/directories:',
                    ## label_justify=LEFT,
                    height=12,
                    takefocus=False
            )
            for name in self.names:
                self.lb.insert(tk.END, name)
            self.lb.pack(fill=tk.X, expand=True)
            ## self.lb.bind("<Prior>",self.Zoek_pgup)
            ## self.lb.bind("<Next>",self.Zoek_pgdn)
            lt = tk.Frame(self.fExe)
            lt.pack(fill=tk.BOTH, expand=True)
        self.fOpt4 = tk.Frame(self.fExe)
        self.fOpt4.pack(fill=tk.BOTH, expand=True)
        tk.Label(self.fOpt4, text="", width=17).pack(side=tk.LEFT)
        self.vraagBackup = tk.Checkbutton(self.fOpt4,
            text = "gewijzigde bestanden backuppen",
            variable=self.backup,
            )
        self.vraagBackup.pack(side=tk.LEFT)
        sf = tk.Frame(self.fExe)
        sf.pack()
        self.DoIt = tk.Button(sf, text="Uitvoeren", command=self.doe)
        self.DoIt.pack(side=tk.LEFT, padx=5, pady=5)
        #~ self.DoIt.bind("<Return>",self.doe)
        self.master.bind_all("<Return>", self.doe)
        self.vraagZoek.focus_set()
        self.Cancel = tk.Button(sf, text="Einde", command=self.master.quit)
        self.Cancel.pack(side=tk.LEFT, padx=5, pady=5)
        #~ self.Cancel.bind("<Return>", self.einde)
        self.master.bind_all("<Escape>", self.einde)

    ## def Zoek_dropdown(self,event):
        ## "event handler voor openen zoek-Combobox dropdown"
        ## self.vraagZoek.invoke()

    ## def Zoek_pgup(self,event):
        ## "event handler voor terugbladeren in zoek-Combobox dropdown"
        ## self.vraagZoek.yview(SCROLL,-1,PAGES)

    ## def Zoek_pgdn(self,event):
        ## "event handler voor doorbladeren in zoek-Combobox dropdown"
        ## self.vraagZoek.yview(SCROLL,1,PAGES)

    ## def Verv_dropdown(self,event):
        ## "event handler voor openen vervang-Combobox dropdown"
        ## self.vraagVerv.invoke()

    def einde(self, event):
        """applicatie afsluiten"""
        self.master.quit()

    def doe(self, event=None):
        """Zoekactie uitvoeren en resultaatscherm tonen"""

        mld = self.checkzoek(self.zoekstr.get())

        if not mld:
            self.checkverv(self.vervstr.get(), self.vervleeg.get())
            self.checkattr(bool(self.case.get()), bool(self.word.get()))
            item = self.typestr.get()
            if item:
                self.checktype(item)
            if not self.apptype:
                mld = self.checkpath(self.dirnaam.get())

        if not mld:
            self.checksubs(bool(self.subdirs.get()))

        self.p["backup"] = bool(self.backup.get()) # backup bij vervangen

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
            #~ w.mainloop()

    def zoekdir(self):
        """event handler voor 'zoek in directory'"""
        oupad = self.dirnaam.get()
        if oupad == "":
            pad = tkFileDialog.askdirectory()
        else:
            pad = tkFileDialog.askdirectory(initialdir=oupad)
        if pad != "":
            self.dirnaam.set(pad)


    #~ def quit():
        #~ self.master.quit

def test():
    "test routine"
    root = tk.Tk()
    ## MainFrame(root)
    MainFrame(root, "single", '/home/visser/Python/filefindr/afrift/afrift_gui.py')
    ## MainFrame(root, 'multi', 'CMDAE.tmp')
    root.mainloop()

if __name__ == "__main__":
    test()
