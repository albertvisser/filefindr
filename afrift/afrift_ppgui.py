import os
if os.name == 'ce':
    DESKTOP = False
    import ppygui as gui
else:
    DESKTOP = True
    import ppygui.api as gui
from .findr_files import findr
from afrift_base import iconame, ABase

class MainFrame(gui.CeFrame, ABase):
    "hoofdscherm van de applicatie"

    def __init__(self, **args):
        gui.CeFrame.__init__(self,
            title="Albert's find-replace in files tool - for Total Commander",
            )
        self.sipp = gui.SIPPref(self)
        # self.fnames bevat 1 of meer namen van de te verwerken bestanden
        ABase.__init__(self)
        if 'files' in args:
            self.fnames = args['files']
        if 'apptype' in args:
            self.apptype = args['apptype']
        if 'dir' in args:
            self.curdir = args['dir']
        self.go()

    def go(self):
        """opzetten scherm(variabelen)

        de _-variabelen worden gekopieerd om het vervolg voorlopig niet te veel te hoeven
        aanpassen"""
        ABase.go(self)
        ## self.zoekstr = self._zoekstr
        ## self.vervstr = self._vervstr
        ## self.typestr = self._typestr
        ## self.dirnaam = self._dirnaam
        ## self.case = self._case
        ## self.vervleeg = self._vervleeg
        ## self.word = self._word
        ## self.subdirs = self._subdirs
        ## self.backup = self._backup
        self.toonScherm()

    def toonScherm(self):

        self.lblZoek = gui.Label(self,title="Zoek naar:",)
        self.cmbZoek = gui.Combo(self,choices = self._mruItems["zoek"])
        ## self.cmbZoek.set_text(self.zoekstr)

        self.lblVerv = gui.Label(self,title="Vervang door:")
        self.cmbVerv = gui.Combo(self,choices = self._mruItems["verv"])
        ## self.cmbVerv.set_text(self.vervstr)

        self.cbVervang = gui.Button(self,text="lege vervangtekst = weghalen",
            style="check")
        self.cbCase = gui.Button(self,text="hoofd/kleine letters gelijk",
            style="check")
        self.cbWoord = gui.Button(self,text="hele woorden",
            style="check")

        if self.apptype =="":
            self.lblDir = gui.Label(self,"In directory:")
            self.cmbDir = gui.Combo(self,choices = self._mruItems["dirs"])
            self.btnDir = gui.Button(self,title="Zoek",action=self.zoekdir)
            t = ""
        else:
            t = "van geselecteerde directories \n"

        self.cbSubs = gui.Button(self,text= t + "ook subdirectories doorzoeken    ",
            style="check")

        self.lblTypes = gui.Label(self,title="alleen files van type:")
        self.cmbTypes = gui.Combo(self,choices=self._mruItems["types"])

        if self.apptype == "multi":
            self.lblFiles = gui.Label(self,title="In de volgende files/directories:")
            self.lbFiles = gui.List(self,choices=self.fnames)

        self.btnDoIt = gui.Button(self,text="Uitvoeren",action=self.doit)
        self.btnCancel = gui.Button(self,text="Einde",action=self.einde)

        v0 = gui.VBox((2,2,2,2),spacing=2)
        h0 = gui.HBox() #(2,2,2,2),spacing=2)
        h1 = gui.HBox((2,2,20,2))
        h1.add(self.lblZoek)
        h0.add(h1)
        h0.add(self.cmbZoek)
        v0.add(h0)
        h0 = gui.HBox() #(2,2,2,2),spacing=2)
        h1 = gui.HBox((2,2,3,2))
        h1.add(self.lblVerv)
        h0.add(h1)
        h0.add(self.cmbVerv)
        v0.add(h0)
        h0 = gui.HBox() #(2,2,2,2),spacing=2)
        spcr = gui.Spacer(x=60,y=0)
        h0.add(spcr)
        h0.add(self.cbVervang)
        v0.add(h0)
        h0 = gui.HBox() #(2,2,2,2),spacing=2)
        spcr = gui.Spacer(x=60,y=0)
        h0.add(spcr)
        h0.add(self.cbCase)
        v0.add(h0)
        h0 = gui.HBox() #(2,2,2,2),spacing=2)
        spcr = gui.Spacer(x=60,y=0)
        h0.add(spcr)
        h0.add(self.cbWoord)
        v0.add(h0)
        if self.apptype =="":
            h0 = gui.HBox() #(2,2,2,2),spacing=2)
            h1 = gui.HBox((2,2,13,2))
            h1.add(self.lblDir)
            h0.add(h1)
            h0.add(self.cmbDir)
            h1 = gui.HBox((2,-1,2,-1))
            h1.add(self.btnDir)
            h0.add(h1)
            v0.add(h0)
        h0 = gui.HBox() #(2,2,2,2),spacing=2)
        spcr = gui.Spacer(x=60,y=0)
        h0.add(spcr)
        h0.add(self.cbSubs)
        v0.add(h0)
        h0 = gui.HBox() #(2,2,2,2),spacing=2)
        h0.add(self.lblTypes)
        h0.add(self.cmbTypes)
        v0.add(h0)
        if self.apptype == "multi":
            h0 = gui.HBox() #(2,2,2,2),spacing=2)
            h0.add(self.lblFiles)
            v0.add(h0)
            h0 = gui.HBox() #(2,2,2,2),spacing=2)
            v1 = gui.VBox() #(2,2,2,2),spacing=2)
            v1.add(self.lbFiles)
            h0.add(v1)
            v0.add(h0)
        h0 = gui.HBox() #(2,2,2,2),spacing=2)
        spcr = gui.Spacer(x=60,y=0)
        h0.add(spcr)
        h0.add(self.btnDoIt)
        h0.add(self.btnCancel)
        spcr = gui.Spacer(x=40,y=0)
        h0.add(spcr)
        v0.add(h0)
        self.sizer = v0

    def einde(self,event=None):
        """applicatie afsluiten"""
        self.close()

    def doit(self,event=None):
        """Zoekactie uitvoeren en resultaatscherm tonen"""
        self.toonpad = False
        self.showpath = False

        item = self.cmbZoek.get_text()
        if item == "":
            gui.Message.ok(ft,"Kan niet zoeken zonder zoekargument",icon='error')
            return
        else:
            self.mruZoek.remove(item)
        self.mruZoek.insert(0,item)
        s = s + "zoeken naar " + item
        zoekstr = item

        item = self.cmbVerv.get_text()
        if item == "":
            self.wijzig = False
        else:
            self.wijzig = True
            self.mruVerv.remove(item)
            self.mruVerv.insert(0,item)
            s = s + "\nen vervangen door " + item
        vervstr = item

        ss = ""
        self.matchCase = self.cbCase.checked
        if self.matchCase:
            ss = ss + "case-sensitive"

        self.matchWords = self.cbWoord.checked
        if self.matchWords:
            if ss:
                ss = ss + ", "
            ss = ss + "hele woorden"
        if ss:
            s = s + " (" + ss + ")"

        item = self.cmbTypes.get_text()
        typelijst = ''
        if item != "":
            try:
                self.mruTypes.remove(item)
            except:
                pass
            self.mruTypes.insert(0,item)
            s = s + "\nin bestanden van type " + item
            h = item.split(",")
            h = [x.lstrip().strip() for x in h[:]]
            typelijst = h

        zoekpad = ''
        if self.apptype == "":
            item = self.cmbDir.get_text()
            if item == "":
                gui.Message.ok(ft,"Ik wil wel graag weten in welke directory ik moet (beginnen met) zoeken",icon='error')
                return
            if not os.path.exists(item):
                gui.Message.ok(ft,"De opgegeven directory bestaat niet",icon='error')
                return
            try:
                self.mruDirs.remove(item)
            except:
                pass
            self.mruDirs.insert(0,item)
            s = s + "\nin " + item
            zoekpad = item

        self.searchSubdirs = self.cbSubs.checked
        if self.searchSubdirs:
            s = s + " en onderliggende directories"

        self.schrijfini()

        h = findr(
            zoek=zoekstr,
            vervang=vervstr,
            pad=zoekpad,
            filelist=self.fnames,
            extlist=typelijst,
            subdirs=self.searchSubdirs,
            case=self.matchCase,
            woord=self.matchWords,
            #regexp=True,
            #backup=True
            )

        if self.apptype == "":
            zr = "AFRIFT - Resultaten:"
        else:
            zr = "Afrift for TC - Resultaten"
        if len(h.rpt) == 2:
            gui.Message.ok(zr,"Niks gevonden")
            return
        self.w = gui.ceFrame()
        n = 0
        zr = []
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
                zr.append(r)
                zr.append('    ' + x[i+2:])
            n += 1
        self.results = gui.List(self.w,
            title = self.z,
            choices = zr,
            )
        spcr = gui.Spacer(x=20)
        klaar = gui.Button(self.w,title="Klaar",action=self.einde_w)
        kopie = gui.Button(self.w,title="Copy to File",action=self.kopie)
        self.cbPad = gui.Button(self.w,type='check',
                title="toon directorypad in uitvoer",
#                variable=self.showpath
                )
        v0 = VBox()
        h0 = HBox()
        h0.add(self.results)
        v0.add(h0)
        h0 = HBox()
        h0.add(spcr)
        h0.add(klaar)
        h0.add(kopie)
        h0.add(self.cbPad)
        v0.add(h0)
        self.w.sizer = v0
        #~ w.mainloop()

    def kopie(self,event=None):
        self.showpath = self.cbPad
        f = self.zoekstr.get() + ".txt"
        fn = gui.FileDlg.save(
            title="Resultaat naar bestand kopieren",
            filename=f,
            wildcards={"text files": ".txt","all files": "*"})
        if fn != "":
            fl = file(fn,"w")
            r1 = self.results.get(0, END)
            sw = True
            fl.write("%s\n" % self.z)
            for x in r1:
                if sw:
                    sw = False
                    if self.showpath:
                        h = x
                    else:
                        h = x.split("\\")[-1]
                else:
                    sw = True
                    fl.write("%s %s\n" % (h,x))
            fl.close()

    def zoekdir(self,evt=None):
        oupad = self.dirnaam
        if oupad == "":
            pad = gui.FileDialog.openfolder()
        else:
            pad = gui.FileDialog.openfolder(filename=oupad) #os.path.join(oupad,'*.*'))
        if pad != "":
            self.cmbDir.set_text(pad) #os.path.split(pad)[0]

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
        h = str(self.matchCase)
        s.set("options","matchCase",h)
        h = str(self.matchWords)
        s.set("options","matchWords",h)
        h = str(self.searchSubdirs)
        s.set("options","searchSubdirs",h)
        s.write(file(self.inifile,"w"))

    #~ def quit():
        #~ self.master.quit

def AppSingle(*args):
    print(args)
    app = gui.Application(MainFrame(
        apptype = 'single',
        dir = args[1][:args[1].rfind("\\")],
        files = [args[1],]
        ))
    app.run()

def AppMulti(*args):
    fnames = []
    curdir = ''
    f = open(args[1],"r")
    for line in f:
        if not curdir:
            curdir = line[:line.rfind("\\")]
        if y[:-1] != "\\" and y[:-1] != "/":
            fnames.append(y)
    f.close()
    app = gui.Application(MainFrame(
        apptype = 'multi',
        dir = curdir,
        files = fnames
        ))
    app.run()

def test():
    app = gui.Application(MainFrame())
    app.run()

if __name__ == "__main__":
    test()