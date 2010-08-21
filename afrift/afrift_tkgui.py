#! /usr/bin/env python
# -*- coding: latin1 -*-
"""AFRIFT Tkinter versie"""

import os
import sys
if sys.version.startswith("3"):
    from tkinter import *
else:
    from Tkinter import *
import tkMessageBox
import tkFileDialog
import Pmw
from findr_files import findr
from afrift_base import iconame, ABase

class Results(Toplevel):
    "Resultatenscherm"

    def __init__(self,parent):
        self.parent = parent
        Toplevel.__init__(self)
        self.title(self.parent.resulttitel)
        ## self.wm_iconbitmap(iconame)
        rpt = self.parent.zoekvervang.rpt

        self.toonpad = IntVar()
        self.showpath = False

        f1 = Frame(self)
        f1.pack(fill=X)
        txt = "%s (%i items)" % (rpt[0],len(rpt)-1)
        Label(f1,text=txt,anchor=W).pack(side=LEFT,fill=X,expand=YES,padx=5)
        f2 = Frame(self)
        f2.pack(fill=BOTH,expand=YES)
        self.scrollY = Scrollbar(f2, orient=VERTICAL)
        self.scrollX = Scrollbar(f2, orient=HORIZONTAL)
        if self.parent.apptype == "":
            b = 50
        elif self.parent.apptype == "single":
            b = 10
        elif self.parent.apptype == "multi":
            b = 40
        f2a = Pmw.PanedWidget(f2,orient='horizontal',)
        p2l = f2a.add("In file")
        p2r = f2a.add("Data")
        self.results = Listbox(p2l, setgrid=YES,width=b,
            takefocus=False,
            yscrollcommand=self.scrollY.set,
            xscrollcommand=self.scrollX.set
            )
        self.results_data = Listbox(p2r, setgrid=YES,width=60,
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
                self.results.insert(END,r)
                self.results_data.insert(END,x[i+2:])
            n += 1
        self.scrollY.config(command=self.list_yview)
        self.scrollY.pack(side=RIGHT, fill=Y)
        self.scrollX.config(command=self.list_xview)
        self.scrollX.pack(side=BOTTOM, fill=X)
        self.results.pack(side=LEFT, fill=BOTH, expand=1)
        self.results_data.pack(side=LEFT, fill=BOTH, expand=1)
        f2a.pack(side=LEFT, fill=BOTH, expand=1) # fill=BOTH,expand=YES)
        f2a.setnaturalsize()
        f3 = Frame(self,height=12)
        f3.pack()
        klaar = Button(f3,text="Klaar",command=self.einde)
        klaar.pack(side=LEFT,padx=5,pady=5)
        klaar.bind("<Return>",self.einde)
        kopie = Button(f3,text="Copy to File",command=self.kopie)
        kopie.pack(side=LEFT,padx=5,pady=5)
        kopie.bind("<Return>",self.kopie)
        self.toonpad.set(int(self.showpath))
        Label(f3,text="",width=2).pack(side=LEFT)
        self.vraagPad = Checkbutton(f3,
            text="toon directorypad in uitvoer",
            variable=self.toonpad
            )
        self.vraagPad.pack(side=LEFT)
        self.bind_all("<Prior>",self.w_pgup)
        self.bind_all("<Next>",self.w_pgdn)
        self.bind_all("<Escape>",self.einde)

    def w_pgup(self,event):
        self.results.yview(SCROLL,-1,PAGES)
        self.results_data.yview(SCROLL,-1,PAGES)

    def w_pgdn(self,event):
        self.results.yview(SCROLL,1,PAGES)
        self.results_data.yview(SCROLL,1,PAGES)

    def list_yview(self, *args):
        apply(self.results.yview, args)
        apply(self.results_data.yview, args)

    def list_xview(self, *args):
        apply(self.results.xview, args)
        apply(self.results_data.xview, args)

    def einde(self, event=None):
        self.destroy()
        self.parent.master.bind_all("<Escape>",self.parent.einde)
        self.parent.master.unbind_all("<Prior>")
        self.parent.master.unbind_all("<Next>")
        self.parent.master.lift()

    def kopie(self, event=None):
        self.showpath = bool(self.toonpad.get())
        f = self.zoekstr.get().replace('"','@').replace("'",'@') + ".txt"
        fn = tkFileDialog.asksaveasfilename(title="Resultaat naar bestand kopieren",
                                            parent=self,
                                            initialdir=self.curdir,
                                            initialfile=f,
                                            defaultextension=".txt",
                                            filetypes=[("text files",".txt"),("all files","*")])
        if fn != "":
            fl = file(fn,"w")
            r1 = self.results.get(0, END)
            r2 = self.results_data.get(0, END)
            fl.write("%s\n" % self.z)
            for i in range(len(r1)):
                if self.showpath:
                    fl.write("%s %s\n" % (r1[i],r2[i]))
                else:
                    s2 = r1[i].split("\\")
                    fl.write("%s %s\n" % (s2[-1],r2[i]))
            fl.close()
        self.w.focus_set()
        self.w.grab_set()
        self.w.wait_window()

class MainFrame(ABase):
    """Hoofdscherm van de applicatie"""

    def __init__(self, parent=None, apptype="", data=""):
        ABase.__init__(self, parent, apptype, data)

        self.zoekstr = StringVar()
        self.zoekstr.set('')
        self.vervstr = StringVar()
        self.vervstr.set('')
        self.typestr = StringVar()
        self.typestr.set('')
        self.dirnaam = StringVar()
        self.dirnaam.set('')
        self.case = IntVar()
        self.case.set(self.p["case"])
        self.vervleeg = IntVar()
        self.vervleeg.set(self._vervleeg)
        self.word = IntVar()
        self.word.set(self.p["woord"])
        self.subdirs = IntVar()
        self.subdirs.set(self.p["subdirs"])
        self.backup = IntVar()
        self.backup.set(self._backup)

        self.parent.title(self.title)
        ## self.parent.wm_iconbitmap("@"+iconame)
        self.master = Frame(self.parent)
        self.master.pack()
        self.fZoek = Frame(self.master)
        self.fZoek.pack(fill=BOTH,expand=True)
        self.vraagZoek = Pmw.ComboBox(self.fZoek,
            scrolledlist_items = self._mruItems["zoek"],
            arrowbutton_takefocus = False,
            entry_width = 40,
            entry_textvariable = self.zoekstr,
            listbox_bg="#ffffff",
            labelpos = "wn",
            label_text = "Zoek naar:",
            label_width=17,
            label_anchor=W,
            label_justify=LEFT)
        self.vraagZoek.pack(side=LEFT,padx=5,pady=5)
        self.vraagZoek.bind("<Next>",self.Zoek_dropdown)
        self.fVerv = Frame(self.master)
        self.fVerv.pack(fill=BOTH,expand=True)
        self.vraagVerv = Pmw.ComboBox(self.fVerv,
            scrolledlist_items = self._mruItems["verv"],
            arrowbutton_takefocus = False,
            entry_width = 40,
            entry_textvariable = self.vervstr,
            listbox_bg="#ffffff",
            labelpos = "wn",
            label_text = "Vervang door:",
            label_width=17,
            label_anchor=W,
            label_justify=LEFT)
        self.vraagVerv.pack(side=LEFT,padx=5,pady=5)
        self.vraagVerv.bind("<Next>",self.Verv_dropdown)
        self.fOpt0 = Frame(self.master)
        self.fOpt0.pack(fill=BOTH,expand=True)
        Label(self.fOpt0,text="",width=17).pack(side=LEFT)
        self.cVervang = Checkbutton(self.fOpt0,
            text="lege vervangtekst = weghalen",
            variable=self.vervleeg)
        self.cVervang.pack(side=LEFT)
        self.fOpt1 = Frame(self.master)
        self.fOpt1.pack(fill=BOTH,expand=True)
        Label(self.fOpt1,text="",width=17).pack(side=LEFT)
        self.vraagCase = Checkbutton(self.fOpt1,
            text="hoofd/kleine letters gelijk",
            variable=self.case
            )
        self.vraagCase.pack(side=LEFT)
        self.fOpt2 = Frame(self.master)
        self.fOpt2.pack(fill=BOTH,expand=True)
        Label(self.fOpt2,text="",width=17).pack(side=LEFT)
        self.vraagWoord = Checkbutton(self.fOpt2,
            text="hele woorden",
            variable=self.word
            )
        self.vraagWoord.pack(side=LEFT)
        if self.apptype =="":
            self.fDir = Frame(self.master)
            self.fDir.pack(fill=BOTH,expand=True)
            self.vraagDir = Pmw.ComboBox(self.fDir,
                scrolledlist_items = self._mruItems["dirs"],
                arrowbutton_takefocus = False,
                entry_width = 40,
                entry_textvariable = self.dirnaam,
                listbox_bg="#ffffff",
                labelpos = "wn",
                label_text = "In directory:",
                label_width=17,
                label_anchor=W,
                label_justify=LEFT)
            self.vraagDir.pack(side=LEFT,padx=5,pady=5)
            self.Zoek = Button(self.fDir,text="Zoek",command=self.zoekdir)
            self.Zoek.pack(side=LEFT,padx=5)
            Label(self.fDir,text="").pack(side=RIGHT)
            t = ""
        else:
            t = "van geselecteerde directories "
        self.fOpt3 = Frame(self.master)
        self.fOpt3.pack(fill=BOTH,expand=True)
        Label(self.fOpt3,text="",width=17).pack(side=LEFT)
        self.vraagSubs = Checkbutton(self.fOpt3,
            text = t + "ook subdirectories doorzoeken    ",
            variable=self.subdirs,
            )
        self.vraagSubs.pack(side=LEFT)
        self.fTypes = Frame(self.master)
        self.fTypes.pack(fill=BOTH,expand=True)
        self.vraagTypes = Pmw.ComboBox(self.fTypes,
            scrolledlist_items = self._mruItems["types"],
            arrowbutton_takefocus = False,
            entry_width = 40,
            entry_textvariable = self.typestr,
            listbox_bg="#ffffff",
            labelpos = "wn",
            label_text = "alleen files van type:",
            label_width=17,
            label_anchor=W,
            label_justify=LEFT)
        self.vraagTypes.pack(side=LEFT,padx=5,pady=5)
        self.fExe = Frame(self.master)
        self.fExe.pack(fill=BOTH,expand=True)
        if self.apptype == "multi":
            sl = Frame(self.fExe)
            sl.pack(fill=BOTH,expand=True)
            self.lb = Pmw.ScrolledListBox(sl,
                    items=self.fnames,
                    labelpos='nw',
                    label_text='In de volgende files/directories:',
                    label_justify=LEFT,
                    listbox_height=12,
                    listbox_takefocus=False
            )
            self.lb.pack(fill=X,expand=True)
            self.lb.bind("<Prior>",self.Zoek_pgup)
            self.lb.bind("<Next>",self.Zoek_pgdn)
            lt = Frame(self.fExe)
            lt.pack(fill=BOTH,expand=True)
            #~ Label(lt,text='N.B.: geselecteerde directories worden (nog) niet meegenomen',anchor=W).pack()
        self.fOpt4 = Frame(self.fExe)
        self.fOpt4.pack(fill=BOTH,expand=True)
        Label(self.fOpt4,text="",width=17).pack(side=LEFT)
        self.vraagBackup = Checkbutton(self.fOpt4,
            text = "gewijzigde bestanden backuppen",
            variable=self.backup,
            )
        self.vraagBackup.pack(side=LEFT)
        sf = Frame(self.fExe)
        sf.pack()
        self.DoIt = Button(sf,text="Uitvoeren",command=self.doe)
        self.DoIt.pack(side=LEFT,padx=5,pady=5)
        #~ self.DoIt.bind("<Return>",self.doe)
        self.master.bind_all("<Return>",self.doe)
        self.vraagZoek.component('entry').focus_set()
        self.Cancel = Button(sf,text="Einde",command=self.master.quit)
        self.Cancel.pack(side=LEFT,padx=5,pady=5)
        #~ self.Cancel.bind("<Return>",self.einde)
        self.master.bind_all("<Escape>",self.einde)

    def Zoek_dropdown(self,event):
        "event handler voor openen zoek-combobox dropdown"
        self.vraagZoek.invoke()

    def Zoek_pgup(self,event):
        "event handler voor terugbladeren in zoek-combobox dropdown"
        self.vraagZoek.yview(SCROLL,-1,PAGES)

    def Zoek_pgdn(self,event):
        "event handler voor doorbladeren in zoek-combobox dropdown"
        self.vraagZoek.yview(SCROLL,1,PAGES)

    def Verv_dropdown(self,event):
        "event handler voor openen vervang-combobox dropdown"
        self.vraagVerv.invoke()

    def einde(self,event):
        """applicatie afsluiten"""
        self.master.quit()

    def doe(self,event=None):
        """Zoekactie uitvoeren en resultaatscherm tonen"""

        mld = self.checkzoek(self.zoekstr.get())

        if not mld:
            self.checkverv(self.vervstr.get(),self.vervleeg.get())
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
            tkMessageBox.showerror(self.fouttitel,mld)
            return

        self.schrijfini()
        self.zoekvervang = findr(**self.p)

        if len(self.zoekvervang.rpt) == 2:
            tkMessageBox.showinfo(self.resulttitel,"Niks gevonden")
        else:
            self.w = Results(self)
            self.w.focus_set()
            self.w.grab_set()
            self.w.wait_window()
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
    root = Tk()
    Pmw.initialise(root)
    ## h = MainFrame(root)
    h = MainFrame(root, 'single', '/home/visser/Python/filefindr/afrift/afrift_gui.py')
    ## h = MainFrame(root, 'multi', 'CMDAE.tmp')
    root.mainloop()

if __name__ == "__main__":
    test()
