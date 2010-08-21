#! /usr/bin/env python3
# -*- coding: latin1 -*-
"""AFRIFT Tkinter versie"""

import os
import sys
from tkinter import *
from tkinter.ttk import *
from tkinter.scrolledtext import ScrolledText
import tkinter.messagebox as tkMessageBox
import tkinter.filedialog as tkFileDialog
## import Pmw
from findr_files import findr
from afrift_base import iconame, ABase

class Results(Toplevel):
    "Resultatenscherm"

    def __init__(self,iconame,zr,h):
        Toplevel.__init__()
        self.title(self.zr)
        ## self.wm_iconbitmap(iconame)

        self.toonpad = IntVar()
        self.showpath = False

        f1 = Frame(self)
        f1.pack(fill=X)
        txt = "%s (%i items)" % (h.rpt[0],len(h.rpt)-1)
        Label(f1,text=txt,anchor=W).pack(side=LEFT,fill=X,expand=YES,padx=5)
        f2 = Frame(self)
        f2.pack(fill=BOTH,expand=YES)
        self.scrollY = Scrollbar(f2, orient=VERTICAL)
        self.scrollX = Scrollbar(f2, orient=HORIZONTAL)
        if self.apptype == "":
            b = 50
        elif self.apptype == "single":
            b = 10
        elif self.apptype == "multi":
            b = 40
        f2a = PanedWindow(f2)
        f2a.pack()
        p2l = Frame(f2a)
        p2l.pack()
        f2a.add(p2l) # "In file")
        p2r = Frame(f2a)
        pr2.pack()
        f2a.add(p2r) # "Data")
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
        for x in h.rpt:
            if n == 0:
                self.z = x
            else:
                i = x.find(": ")
                r = x[:i]
                if self.apptype == "single":
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
        f3 = Frame(self.w,height=12)
        f3.pack()
        klaar = Button(f3,text="Klaar",command=self.w_einde)
        klaar.pack(side=LEFT,padx=5,pady=5)
        klaar.bind("<Return>",self.w_einde)
        kopie = Button(f3,text="Copy to File",command=self.w_kopie)
        kopie.pack(side=LEFT,padx=5,pady=5)
        kopie.bind("<Return>",self.kopie)
        self.toonpad.set(int(self.showpath))
        Label(f3,text="",width=2).pack(side=LEFT)
        self.vraagPad = Checkbutton(f3,
            text="toon directorypad in uitvoer",
            variable=self.toonpad
            )
        self.vraagPad.pack(side=LEFT)
        self.w.bind_all("<Prior>",self.w_pgup)
        self.w.bind_all("<Next>",self.w_pgdn)
        self.w.bind_all("<Escape>",self.w_einde)

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

    def w_einde(self, event=None):
        self.destroy()
        self.master.bind_all("<Escape>",self.einde)
        self.master.unbind_all("<Prior>")
        self.master.unbind_all("<Next>")
        self.master.lift()

    def w_kopie(self, event=None):
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

class Application(ABase):
    """Hoofdscherm van de applicatie"""

    def __init__(self,master,h):
        # self.fnames bevat 1 of meer namen van de te verwerken bestanden
        self.master = master
        self.master.title("Albert's find-replace in files tool")
        ## self.master.wm_iconbitmap("@"+iconame)
        ABase.__init__(self)
        self.go()

    def go(self):
        """opzetten scherm(variabelen)

        de _-variabelen worden gekopieerd naar Tkinter classes"""
        ABase.go(self)
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
        self.toonScherm(self.master)

    def toonScherm(self,master):
        """scherm opbouwen en tonen"""
        self.master = Frame(master)
        self.master.pack()
        self.fZoek = Frame(self.master)
        self.fZoek.pack(fill=BOTH,expand=True)
        Label(self.fZoek, text = "Zoek naar:", width=17).pack(side=LEFT)
        self.vraagZoek = Combobox(self.fZoek,
            values = self._mruItems["zoek"],
            width = 40,
            textvariable = self.zoekstr,
            ## listbox_bg="#ffffff",
            ## labelpos = "wn",
            ## label_anchor=W,
            ## label_justify=LEFT
            )
        self.vraagZoek.pack(side=LEFT,padx=5,pady=5)
        ## self.vraagZoek.bind("<Next>",self.Zoek_dropdown)
        self.fVerv = Frame(self.master)
        self.fVerv.pack(fill=BOTH,expand=True)
        Label(self.fVerv, text = "Vervang door:", width=17).pack(side=LEFT)
        self.vraagVerv = Combobox(self.fVerv,
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
        self.vraagVerv.pack(side=LEFT,padx=5,pady=5)
        ## self.vraagVerv.bind("<Next>",self.Verv_dropdown)
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
            Label(self.fDir, text = "In directory:", width=17).pack(side = LEFT)
            self.vraagDir = Combobox(self.fDir,
                values = self._mruItems["subdirs"],
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
        Label(self.fTypes,text = "alleen files van type:",width=17).pack(side=LEFT)
        self.vraagTypes = Combobox(self.fTypes,
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
        self.vraagTypes.pack(side=LEFT,padx=5,pady=5)
        self.fExe = Frame(self.master)
        self.fExe.pack(fill=BOTH,expand=True)
        if self.apptype == "multi":
            sl = Frame(self.fExe)
            sl.pack(fill=BOTH,expand=True)
            Label(sl, text='In de volgende files/directories:').pack(side = LEFT)
            self.lb = ScrolledText(sl,
                    ## items=self.fnames,
                    ## labelpos='nw',
                    ## label_text='In de volgende files/directories:',
                    ## label_justify=LEFT,
                    height=12,
                    takefocus=False
            )
            for name in self.names:
                self.lb.insert(END, name)
            self.lb.pack(fill=X,expand=True)
            ## self.lb.bind("<Prior>",self.Zoek_pgup)
            ## self.lb.bind("<Next>",self.Zoek_pgdn)
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
        self.vraagZoek.focus_set()
        self.Cancel = Button(sf,text="Einde",command=self.master.quit)
        self.Cancel.pack(side=LEFT,padx=5,pady=5)
        #~ self.Cancel.bind("<Return>",self.einde)
        self.master.bind_all("<Escape>",self.einde)

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

    def einde(self,event):
        """applicatie afsluiten"""
        self.master.quit()

    def doe(self,event=None):
        """Zoekactie uitvoeren en resultaatscherm tonen"""

        mld = self.checkzoek(self.zoekstr.get())

        if not mld:
            self.checkverv(self.vervstr.get(),self.vervleeg.get())
            self.checkattr(bool(self.case.get(), bool(self.word.get())))
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
        zoekvervang = findr(**p)

        if len(zoekvervang.rpt) == 2:
            tkMessageBox.showinfo(self.resulttitel,"Niks gevonden")
        else:
            self.w = Results(iconame, self.resulttitel, zoekvervang)
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

class Appl_single(Application):
    "Versie voor aansturing met 1 specifiek bestand om in te zoeken"

    def __init__(self,master,h):
        """
        h[0] is dit programma zelf
        h[1] is de naam van het te verwerken bestand
        """
        self.master = master
        self.master.title("Albert's find-replace in files tool - for Total Commander, single file version")
        ## self.master.wm_iconbitmap(iconame)
        ABase.__init__(self,"single",h[1])
        self.go()

class Appl_multi(Application):
    "Versie voor aansturing mmet lijst bestanden en/of directories om in te zoeken"

    def __init__(self,master,h):
        """
        # h[0] is dit programma zelf
        # h[1] is de naam van een bestand waarin de betreffende namen staan
        """
        self.master = master
        self.master.title("Albert's find-replace in files tool - for Total Commander")
        ## self.master.wm_iconbitmap(iconame)
        ABase.__init__(self,"multi",h[1])
        self.go()

def test():
    root = Tk()
    h = Appl_single(root,['afrift_tk3gui.py','afrift_tk3gui.py'])
    ## h = Appl_multi(root,['afrift_tk3gui.py','CMDAE.tmp'])
    ## h = Application(root,("hallo","findr_files.py"))
    root.mainloop()

if __name__ == "__main__":
    test()
