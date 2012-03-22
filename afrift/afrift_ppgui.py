import os
if os.name == 'ce':
    DESKTOP = False
    import ppygui as gui
else:
    DESKTOP = True
    import ppygui.api as gui
from findr_files import findr
from afrift_base import iconame, ABase

class Results(gui.ceFrame):
    """Resultaten scherm"""

    def __init__(self, parent):
        ## self.parent = parent
        gui.ceFrame.__init__(self, title=self.parent.resulttitel)
        self.rlijst = self.populate_list()
        self.results = gui.List(self,
            title = self.rlijst[0],
            choices = [": ".join((x,y)) for x,y in self.rlijst[1:]],
            )
        spcr = gui.Spacer(x=20)
        klaar = gui.Button(self,title="Klaar",action=self.einde)
        kopie = gui.Button(self,title="Copy to File",action=self.kopie)
        self.cbPad = gui.Button(self,type='check',
                title="toon directorypad in uitvoer",
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

    def populate_list(self):
        "resultaten in de listbox zetten"
        res = []
        for ix, line in enumerate(self.parent.zoekvervang.rpt):
            if ix == 0:
                kop = line
            elif line != "":
                where, what = line.split(": ", 1)
                if self.parent.apptype == "single":
                    fname, lineno = where.split("r.", 1)
                    if ix == 1:
                        kop += " in {0}".format(fname)
                    where = lineno
                res.append((where, what))
        res.insert(0, kop)
        return res

    def kopie(self,event=None):
        "callback for button 'Copy to file'"
        toonpad = self.cbPad.checked
        f = self.parent.p["zoek"]
        for char in '/\\?%*:|"><.':
            if char in f:
                f = f.replace(char, "~")
        f +=  ".txt"
        fn = gui.FileDlg.save(
            title="Resultaat naar bestand kopieren",
            filename=f,
            wildcards={"text files": ".txt","all files": "*"})
        if fn != "":
            with open(fn, "w") as f_out:
                f_out.write("{0}\n".format(self.rlijst[0]))
                for r1, r2 in self.rlijst[1:]:
                    if toonpad:
                        f_out.write("{0} {1}\n".format(r1, r2))
                    else:
                        f_out.write("{0} {1}\n".format(r1.split(os.sep)[-1], r2))

    def einde(self,event=None):
        """scherm afsluiten"""
        self.close()

class MainFrame(gui.CeFrame, ABase):
    "hoofdscherm van de applicatie"

    def __init__(self, parent=None, apptype="", fnaam=""):
        ABase.__init__(self, parent, apptype, fnaam)
        gui.CeFrame.__init__(self, title=self.title)
        self.sipp = gui.SIPPref(self)

        self.lblZoek = gui.Label(self,title="Zoek naar:",)
        self.cmbZoek = gui.Combo(self,choices = self._mruItems["zoek"])

        self.lblVerv = gui.Label(self,title="Vervang door:")
        self.cmbVerv = gui.Combo(self,choices = self._mruItems["verv"])

        self.cbVervang = gui.Button(self,text="lege vervangtekst = weghalen",
            style="check")
        self.cbCase = gui.Button(self,text="hoofd/kleine letters gelijk",
            style="check")
        self.cbWoord = gui.Button(self,text="hele woorden",
            style="check")

        t = ""
        if self.apptype =="":
            self.lblDir = gui.Label(self,"In directory:")
            self.cmbDir = gui.Combo(self,choices = self._mruItems["dirs"])
            self.btnDir = gui.Button(self,title="Zoek",action=self.zoekdir)
        elif self.apptype == "single":
            self.lblDirt = gui.Label(self,"In file/directory:")
            self.lblDir = gui.Label(self,self.fnames[0])
        else:
            t = "van geselecteerde directories \n"

        if self.apptype != "single" or os.path.isdir(self.fnames[0]):
            self.cbSubs = gui.Button(self,text= t + "ook subdirectories doorzoeken    ",
                style="check")

            self.lblTypes = gui.Label(self,title="alleen files van type:")
            self.cmbTypes = gui.Combo(self,choices=self._mruItems["types"])

        if self.apptype == "multi":
            self.lblFiles = gui.Label(self,title="In de volgende files/directories:")
            self.lbFiles = gui.List(self,choices=self.fnames)

        self.btnDoIt = gui.Button(self,text="Uitvoeren",action=self.doe)
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
        elif self.apptype == "single":
            h0 = gui.HBox() #(2,2,2,2),spacing=2)
            h1 = gui.HBox((2,2,13,2))
            h1.add(self.lblDirt)
            h0.add(h1)
            h0.add(self.lblDir)
            h1 = gui.HBox((2,-1,2,-1))
            h1.add(self.btnDir)
            h0.add(h1)
            v0.add(h0)
        if self.apptype != "single" or os.path.isdir(self.fnames[0]):
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

    def doe(self,event=None):
        """Zoekactie uitvoeren en resultaatscherm tonen"""
        ## self.toonpad = False
        ## self.showpath = False
            if not self.apptype:
                mld = self.checkpath(self.cmbDir.get_text())
        if not mld:
            self.checksubs(self.cbSubs.checked)

        mld = self.checkzoek(self.cmbZoek.get_text())
        if not mld:
            self.checkverv(self.cmbVerv.get_text(), self.cbVervang.checked)
            self.checkattr(self.cbCase.checked, self.cbWoord.checked)
                b = self.cmbTypes.get_text()
            except AttributeError:
                b = None
            if b:
                self.checktype(b)
            if not self.apptype:
                mld = self.checkpath(self.cmbDir.get_text())
        if not mld:
                self.checksubs(self.cbSubs.checked)
            except AttributeError:

        #-- nog niet toegevoegd in deze interface
        # self.p["backup"] = self.vraagBackup.GetValue()

        if mld:
            gui.Message.ok(self.fouttitel,mld,icon='error')
        self.schrijfini()
        self.zoekvervang = findr(**self.p)
        if len(self.zoekvervang.rpt) == 1:
            gui.Message.ok(self.resulttitel,"Niks gevonden")
        else:
            Results(self)

    def zoekdir(self,evt=None):
        oupad = self.dirnaam
        if oupad == "":
            pad = gui.FileDialog.openfolder()
        else:
            pad = gui.FileDialog.openfolder(filename=oupad) #os.path.join(oupad,'*.*'))
        if pad != "":
            self.cmbDir.set_text(pad) #os.path.split(pad)[0]


def test():
    app = gui.Application(MainFrame())
    ## app = gui.Application(MainFrame(apptype = "single",
        ## fnaam = '/home/albert/filefindr/afrift/afrift_gui.py'))
    ## app = gui.Application(MainFrame(apptype = "multi", fnaam = 'CMDAE.tmp'))
    app.run()

if __name__ == "__main__":
    test()