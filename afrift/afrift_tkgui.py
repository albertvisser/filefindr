# -*- coding: latin1 -*-
from Tkinter import *
import tkMessageBox
import tkFileDialog
import Pmw
import os
import sys
from ConfigParser import SafeConfigParser
from findr_files import findr
iconame = os.path.join(os.getcwd(),"find.ico")
h = os.path.split(sys.argv[0])
iconame = os.path.join(h[0],"find.ico")

class Application:

    def __init__(self,master,h):
        # self.fnames bevat 1 of meer namen van de te verwerken bestanden
        self.master = master
        self.master.title("Albert's find-replace in files tool")
        self.master.wm_iconbitmap(iconame)
        self.fnames = []
        self.apptype = ''
        self.curdir = os.getcwd()
        self.go()

    def go(self):
        for i in range(len(self.fnames)):
            x = self.fnames[i]
            if x[-1] == "\\":
                self.fnames[i] = x[:-1]
        self.readini()
        self.zoekstr = StringVar()
        self.vervstr = StringVar()
        self.typestr = StringVar()
        self.dirnaam = StringVar()
        self.case = IntVar()
        self.case.set(int(self.matchCase))
        self.vervleeg = IntVar()
        self.vervleeg.set(0)
        self.word = IntVar()
        self.word.set(int(self.matchWords))
        self.subdirs = IntVar()
        self.backup = IntVar()
        self.backup.set(1)
        self.subdirs.set(int(self.searchSubdirs))
        self.toonScherm(self.master)

    def readini(self):
        self.hier = os.getcwd()
        self.inifile = self.hier + "/afriftftc.ini"
        # inlezen mru-gegevens
        self.mruZoek = []
        self.mruVerv = []
        self.mruTypes = []
        self.mruDirs = []
        self.matchCase = False
        self.matchWords = False
        self.searchSubdirs = False
        s = SafeConfigParser()
        s.read(self.inifile)
        if s.has_section("zoek"):
            for i in range(len(s.options("zoek"))):
                ky = ("woord%i"  % (i+1))
                self.mruZoek.append(s.get("zoek",ky))
        if s.has_section("vervang"):
            for i in range(len(s.options("vervang"))):
                ky = ("woord%i"  % (i+1))
                self.mruVerv.append(s.get("vervang",ky))
        if s.has_section("filetypes"):
            for i in range(len(s.options("filetypes"))):
                ky = ("spec%i"  % (i+1))
                self.mruTypes.append(s.get("filetypes",ky))
        if s.has_section("dirs"):
            for i in range(len(s.options("dirs"))):
                ky = ("pad%i"  % (i+1))
                self.mruDirs.append(s.get("dirs",ky))
        if s.has_section("options"):
            if s.has_option("options","matchCase"):
                if s.getboolean("options","matchCase"):
                    self.matchCase = True
            if s.has_option("options","matchWords"):
                if s.getboolean("options","matchWords"):
                    self.matchWords = True
            if s.has_option("options","searchSubdirs"):
                if s.getboolean("options","searchSubdirs"):
                    self.searchSubdirs = True

    def toonScherm(self,master):
        self.master = Frame(master)
        self.master.pack()
        self.fZoek = Frame(self.master)
        self.fZoek.pack(fill=BOTH,expand=True)
        self.vraagZoek = Pmw.ComboBox(self.fZoek,
            scrolledlist_items = self.mruZoek,
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
            scrolledlist_items = self.mruVerv,
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
                scrolledlist_items = self.mruDirs,
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
            scrolledlist_items = self.mruTypes,
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
        self.vraagZoek.invoke()

    def Zoek_pgup(self,event):
        self.vraagZoek.yview(SCROLL,-1,PAGES)

    def Zoek_pgdn(self,event):
        self.vraagZoek.yview(SCROLL,1,PAGES)

    def Verv_dropdown(self,event):
        self.vraagVerv.invoke()

    def einde(self,event):
        self.master.quit()

    def doe(self,event=None):
        s = ""
        p = {}
        self.toonpad = IntVar()
        self.showpath = False

        if self.apptype != "":
            ft = "AFRIFT for TC fout"
        else:
            ft = "AFRIFT fout"

        if self.fnames: # len(self.fnames) > 0:
            p["filelist"] = self.fnames

        item = self.zoekstr.get()
        if not item: # item == "":
            tkMessageBox.showerror(ft,"Kan niet zoeken zonder zoekargument")
            return
        elif item in self.mruZoek:
            self.mruZoek.remove(item)
        self.mruZoek.insert(0,item)
        s += "zoeken naar " + item
        p["zoek"] = item # zoekstring

        item = self.vervstr.get()
        if not item: # item == "":
            if bool(self.vervleeg.get()): # self.vervleeg.get() == 1:
                p["vervang"] = "" # vervangstring
                s += "\nen weggehaald"
        else:
            if item in self.mruVerv:
                self.mruVerv.remove(item)
            self.mruVerv.insert(0,item)
            s += "\nen vervangen door " + item
            p["vervang"] = item # vervangstring

        ss = ""
        self.matchCase = bool(self.case.get())
        if self.matchCase:
            ss += "case-sensitive"
        p["case"] = self.matchCase # case-sensitive ja/nee

        self.matchWords = bool(self.word.get())
        if self.matchWords:
            if ss: # ss != "":
                ss += ", "
            ss += "hele woorden"
        p["woord"] = self.matchWords # woord/woorddeel
        if ss: # ss != "":
            s += " (" + ss + ")"

        item = self.typestr.get()
        if item: # item != "":
            if item in self.mruTypes:
                self.mruTypes.remove(item)
            self.mruTypes.insert(0,item)
            s += "\nin bestanden van type " + item
            h = item.split(",")
            p["extlist"] = [x.lstrip().strip() for x in h[:]] # lijst extensies

        if not self.apptype: # self.apptype == "":
            item = self.dirnaam.get()
            if not item: #item == "":
                tkMessageBox.showerror(ft,"Ik wil wel graag weten in welke directory ik moet (beginnen met) zoeken")
                return
            else:
                if not os.path.exists(item):
                    tkMessageBox.showerror(ft,"De opgegeven directory bestaat niet")
                    return
            if item in self.mruDirs:
                self.mruDirs.remove(item)
            self.mruDirs.insert(0,item)
            s += "\nin " + item
            p["pad"] = item # lijst dirs

        self.searchSubdirs = bool(self.subdirs.get())
        if self.searchSubdirs:
            s += " en onderliggende directories"
        p["subdirs"] = self.searchSubdirs # zoeken in subdirectories

        p["backup"] = bool(self.backup.get()) # backup bij vervangen
        self.schrijfini()
        #~ tkMessageBox.showinfo("En wat gaan we doen?",s)

        h = findr(**p)

        if self.apptype == "":
            zr = "Albert's Find/Replace In Files Tool - Resultaten"
        else:
            zr = "Afrift for TC - Resultaten"
        if len(h.rpt) == 2:
            tkMessageBox.showinfo(zr,"Niks gevonden")
        else:
            self.w = Toplevel()
            self.w.title(zr)
            self.w.wm_iconbitmap(iconame)
            f1 = Frame(self.w)
            f1.pack(fill=X)
            txt = "%s (%i items)" % (h.rpt[0],len(h.rpt)-1)
            Label(f1,text=txt,anchor=W).pack(side=LEFT,fill=X,expand=YES,padx=5)
            f2 = Frame(self.w)
            f2.pack(fill=BOTH,expand=YES)
            self.scrollY = Scrollbar(f2, orient=VERTICAL)
            self.scrollX = Scrollbar(f2, orient=HORIZONTAL)
            if self.apptype == "":
                b = 50
            elif self.apptype == "single":
                b = 10
            elif self.apptype == "multi":
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
            klaar = Button(f3,text="Klaar",command=self.einde_w)
            klaar.pack(side=LEFT,padx=5,pady=5)
            klaar.bind("<Return>",self.w_einde)
            kopie = Button(f3,text="Copy to File",command=self.kopie)
            kopie.pack(side=LEFT,padx=5,pady=5)
            kopie.bind("<Return>",self.w_kopie)
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
            self.w.focus_set()
            self.w.grab_set()
            self.w.wait_window()
            #~ w.mainloop()


    def w_kopie(self,event):
        self.kopie()

    def w_einde(self,event):
        self.einde_w()

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

    def einde_w(self):
        self.w.destroy()
        self.master.bind_all("<Escape>",self.einde)
        self.master.unbind_all("<Prior>")
        self.master.unbind_all("<Next>")
        self.master.lift()

    def kopie(self):
        self.showpath = bool(self.toonpad.get())
        f = self.zoekstr.get().replace('"','@').replace("'",'@') + ".txt"
        fn = tkFileDialog.asksaveasfilename(title="Resultaat naar bestand kopieren",
                                            parent=self.w,
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

    def zoekdir(self):
        oupad = self.dirnaam.get()
        if oupad == "":
            pad = tkFileDialog.askdirectory()
        else:
            pad = tkFileDialog.askdirectory(initialdir=oupad)
        #~ if oupad == "":
            #~ if len(self.mruDirs) > 0:
                #~ oupad = self.mruDirs[0]
            #~ else:
                #~ oupad = self.hier
        #~ if not os.path.exists(oupad):
            #~ oupad = "C:\\"
        #~ pad = tkFileDialog.askdirectory()
        if pad != "":
            self.dirnaam.set(pad)

    def schrijfini(self):
        s = SafeConfigParser()
        if len(self.mruZoek) > 0:
            s.add_section("zoek")
            i = 1
            for x in self.mruZoek:
                s.set("zoek",("woord%i" % i),x)
                i = i + 1
        if len(self.mruVerv) > 0:
            s.add_section("vervang")
            i = 1
            for x in self.mruVerv:
                s.set("vervang",("woord%i" % i),x)
                i = i + 1
        if len(self.mruTypes) > 0:
            s.add_section("filetypes")
            i = 1
            for x in self.mruTypes:
                s.set("filetypes",("spec%i" % i),x)
                i = i + 1
        if len(self.mruDirs):
            s.add_section("dirs")
            i = 1
            for x in self.mruDirs:
                s.set("dirs",("pad%i" % i),x)
                i = i + 1
        s.add_section("options")
        if self.matchCase:
            h = "True"
        else:
            h = "False"
        s.set("options","matchCase",h)
        if self.matchWords:
            h = "True"
        else:
            h = "False"
        s.set("options","matchWords",h)
        if self.searchSubdirs:
            h = "True"
        else:
            h = "False"
        s.set("options","searchSubdirs",h)
        s.write(file(self.inifile,"w"))

    #~ def quit():
        #~ self.master.quit

class Appl_single(Application):

    def __init__(self,master,h):
        # h[0] is dit programma zelf
        # h[1] is de naam van het te verwerken bestandeen bestand waarin de betreffende namen staan
        self.master = master
        self.master.title("Albert's find-replace in files tool - for Total Commander, single file version")
        self.master.wm_iconbitmap(iconame)
        self.fnames = [h[1]]
        t = h[1]
        for x in range(len(t),0,-1):
            if t[x-1] == "\\":
                break
        self.curdir = t[:x-1]
        self.apptype = 'single'
        self.go()

class Appl_multi(Application):

    def __init__(self,master,h):
        # h[0] is dit programma zelf
        # h[1] is de naam van een bestand waarin de betreffende namen staan
        self.master = master
        self.master.title("Albert's find-replace in files tool - for Total Commander")
        self.master.wm_iconbitmap(iconame)
        #~ tkMessageBox.showinfo("AFRIFT for TC onderbroken","Appl_multi - input file: " + h[1])
        self.readh(h[1])
        #~ tkMessageBox.showinfo("AFRIFT for TC onderbroken","Appl_multi - input file gelezen")
        self.apptype = 'multi'
        self.go()

    def readh(self,h):
        # een subdirectory is herkenbaar aan de \ aan het eind
        # het hier te tonen schermpje vraagt alleen om zoek - vervang - case - heel woord
        self.fnames = []
        f = file(h,"r")
        l = f.readlines()
        f.close()
        t = l[0]
        for x in range(len(t),0,-1):
            if t[x-1] == "\\":
                break
        self.curdir = t[:x-1]
        for x in l:
            y = x[:-1]
            if y[:-1] == "\\" or y[:-1] == "/":
                # directory afwandelen en onderliggende files verzamelen
                pass
            else:
                self.fnames.append(y)

def test():
    root = Tk()
    Pmw.initialise(root)
    ## h = Appl_single(root,['afrift_wxgui.py','CMDAE.tmp'])
    ## h = Appl_multi(root,['afrift_wxgui.py','CMDAE.tmp'])
    h = Application(root,("hallo","findr_files.py"))
    root.mainloop()

if __name__ == "__main__":
    test()
