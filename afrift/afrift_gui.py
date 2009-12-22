# -*- coding: UTF-8 -*-

import wx
#import tkMessageBox
#import tkFileDialog
#import Pmw
import os
import sys
from ConfigParser import SafeConfigParser
from findr_files import findr
iconame = os.path.join(os.getcwd(),"find.ico")
h = os.path.split(sys.argv[0])
iconame = os.path.join(h[0],"find.ico")

class Results(wx.Dialog):
    def __init__(
            self, parent, ID, title,
            ## size=wx.DefaultSize, pos=wx.DefaultPosition,
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
            rpt = None
            ):
        self.parent = parent
        if self.parent.apptype == "": # breedte linkerkolom
            b = 300
            t = 'File/Regel'
        elif self.parent.apptype == "single":
            b = 50
            t = 'Regel'
        elif self.parent.apptype == "multi":
            b = 200
            t = 'File/Regel'
        wx.Dialog.__init__(self, parent, ID, title,
            style = style)
        self.SetIcon(wx.Icon(iconame,wx.BITMAP_TYPE_ICO))

        #pnl = wx.Panel(self,-1)
        txt = wx.StaticText(self,-1,"%s (%i items)" % (rpt[0],len(rpt)-1))
        lijst = wx.ListCtrl(self,-1,
            size = (b + 385,160),
            style=wx.LC_REPORT
            | wx.LC_VRULES,
            )
        lijst.InsertColumn(0,t)
        lijst.SetColumnWidth(0,b)
        lijst.InsertColumn(1,"Data")
        lijst.SetColumnWidth(1,380)
        n = 0
        self.z = " "
        self.results = []
        for x in rpt:
            ## print x
            if n == 0:
                self.z = x
            elif x != "":
                r,s = x.split(": ",1)
                if self.parent.apptype == "single":
                    j = r.find("r.")
                    if n == 1:
                        self.z = self.z + " in " + r[:j]
                    r = r[j:]
                i = lijst.InsertStringItem(sys.maxsize,r)
                lijst.SetStringItem(i,0,r)
                lijst.SetStringItem(i,1,s)
                self.results.append((r,s))
            n += 1

        b1 = wx.Button(self, wx.ID_CANCEL, "Klaar")
        ## self.Bind(wx.EVT_BUTTON,self.einde,b1)
        b2 = wx.Button(self, -1, "Copy to File")
        self.Bind(wx.EVT_BUTTON,self.kopie,b2)
        cb = wx.CheckBox(self,-1,label="toon directorypad in uitvoer")
        cb.SetValue(False)
        self.cb = cb

        vsizer = wx.BoxSizer(wx.VERTICAL)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(txt,0,wx.EXPAND | wx.ALL, 5)
        vsizer.Add(hsizer,0,wx.EXPAND)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(lijst,1,wx.EXPAND | wx.ALL)
        vsizer.Add(hsizer,1,wx.EXPAND)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        bsizer = wx.BoxSizer(wx.HORIZONTAL)
        bsizer.Add(b1,0, wx.ALL, 5)
        bsizer.Add(b2,0, wx.ALL, 5)
        bsizer.Add(cb,0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        hsizer.Add(bsizer,0)
        vsizer.Add(hsizer,0,wx.ALIGN_CENTER_HORIZONTAL) # wx.EXPAND)

        self.SetAutoLayout(True)
        self.SetSizer(vsizer)
        vsizer.Fit(self)
        ## vsizer.SetSizeHints(self)
        self.Layout()
        self.Show(True)

    def kopie(self,event=None):
        toonpad = self.cb.GetValue()
        f = self.parent.zoekstr + ".txt"
        dlg = wx.FileDialog(self,
            message="Resultaat naar bestand kopieren",
            defaultDir=self.parent.curdir,
            defaultFile=f,
            wildcard="text files (*.txt)|*.txt|all files (*.*)|*.*",
            style=wx.SAVE
            )
        if dlg.ShowModal() == wx.ID_OK:
            fn = dlg.GetPath()
            fl = file(fn,"w")
            fl.write("%s\n" % self.z)
            for r1,r2 in self.results:
                if toonpad:
                    fl.write("%s %s\n" % (r1,r2))
                else:
                    fl.write("%s %s\n" % (r1.split("\\")[-1],r2))
            fl.close()
        dlg.Destroy()

    def einde(self,event=None):
        self.w.destroy()

class Application(wx.Frame):
    def __init__(self,parent,id):
        # self.fnames bevat 1 of meer namen van de te verwerken bestanden
        self.parent = parent
        self.title = "Albert's find-replace in files tool"
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
        self.zoekstr = ''
        self.vervstr = ''
        self.typestr = ''
        self.dirnaam = ''
        self.case = int(self.matchCase)
        self.vervleeg = 0
        self.word = int(self.matchWords)
        self.subdirs = int(self.searchSubdirs)
        self.backup = 1
        self.toonScherm()

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

    def toonScherm(self):
        parent = self.parent
        wx.Frame.__init__(self,parent,wx.ID_ANY,self.title,
            style=wx.DEFAULT_FRAME_STYLE|wx.NO_FULL_REPAINT_ON_RESIZE
            )
        self.SetTitle(self.title)
        self.SetIcon(wx.Icon(iconame,wx.BITMAP_TYPE_ICO))
        self.pnl = wx.Panel(self,-1)
        wid = wx.Size(100,-1)
        TXTW = 200

        box = wx.StaticBox(self.pnl,-1)
        t1 = wx.StaticText(self.pnl,-1,"Zoek naar:")
        c1 = wx.ComboBox(self.pnl,-1,size=(TXTW,-1),
            value=self.zoekstr,
            choices=self.mruZoek,
            style=wx.CB_DROPDOWN
            )
        self.vraagZoek = c1

        t2 = wx.StaticText(self.pnl,-1,"Vervang door:")
        c2 = wx.ComboBox(self.pnl,-1,size=(TXTW,-1),
            value=self.vervstr,
            choices=self.mruVerv,
            style=wx.CB_DROPDOWN
            )
        self.vraagVerv = c2

        c3 = wx.CheckBox(self.pnl,-1,label="lege vervangtekst = weghalen")
        c3.SetValue(self.vervleeg)
        self.cVervang = c3
        c4 = wx.CheckBox(self.pnl,-1,label="hoofd/kleine letters gelijk")
        c4.SetValue(self.case)
        self.vraagCase = c4
        c5 = wx.CheckBox(self.pnl,-1,label="hele woorden")
        c5.SetValue(self.word)
        self.vraagWoord = c5

        if self.apptype =="":
            t6 =  wx.StaticText(self.pnl,-1,"In directory:")
            c6 = wx.ComboBox(self.pnl,-1,size=(TXTW,-1),
                value=self.dirnaam,
                choices=self.mruDirs,
                style=wx.CB_DROPDOWN
                )
            self.vraagDir = c6
            self.Zoek = wx.Button(self.pnl,-1,label="&Zoek")
            self.Bind(wx.EVT_BUTTON,self.zoekdir,self.Zoek)
            t = ""
        else:
            t = "van geselecteerde directories "

        c7 = wx.CheckBox(self.pnl,-1,
            label = t + "ook subdirectories doorzoeken",
            )
        c7.SetValue(self.subdirs)
        self.vraagSubs = c7

        t8 =  wx.StaticText(self.pnl,-1,"alleen files van type:")
        c8 = wx.ComboBox(self.pnl,-1,size=(TXTW,-1),
            value=self.typestr,
            choices=self.mruTypes,
            style=wx.CB_DROPDOWN
            )
        self.vraagTypes = c8

        if self.apptype == "multi":
            t9 = wx.StaticText(self.pnl,-1,"In de volgende files/directories:")
            c9 = wx.ListBox(self.pnl,-1,size=(TXTW,-1),choices=self.fnames)
            self.lb = c9

        ## t10 =  wx.StaticText(self.pnl,-1,"",size=wid)
        c10 = wx.CheckBox(self.pnl,-1,label="gewijzigde bestanden backuppen")
        c10.SetValue(self.backup)
        self.vraagBackup = c10

        self.DoIt = wx.Button(self.pnl,-1,label="&Uitvoeren")
        self.Bind(wx.EVT_BUTTON,self.doe,self.DoIt)
        ## self.Cancel = wx.Button(self.pnl, wx.ID_CANCEL, "&Einde") # helpt niet
        self.Cancel = wx.Button(self.pnl,-1,label="&Einde")
        self.Bind(wx.EVT_BUTTON,self.einde,self.Cancel)

        bsizer = wx.BoxSizer(wx.VERTICAL)
        gbsizer = wx.GridBagSizer(4)
        row = 0
        gbsizer.Add(t1,(row,0), flag=wx.EXPAND | wx.ALL, border=4)
        gbsizer.Add(c1,(row,1), flag=wx.ALIGN_CENTER_VERTICAL)
        row += 1
        gbsizer.Add(t2,(row,0), flag=wx.EXPAND | wx.ALL, border=4)
        gbsizer.Add(c2,(row,1), flag=wx.ALIGN_CENTER_VERTICAL)
        row += 1
        vsizer = wx.BoxSizer(wx.VERTICAL)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hbsizer= wx.BoxSizer(wx.HORIZONTAL)
        hbsizer.Add(c3,0)
        hsizer.Add(hbsizer, 0,wx.TOP | wx.BOTTOM,4)
        vsizer.Add(hsizer,0,wx.EXPAND)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hbsizer= wx.BoxSizer(wx.HORIZONTAL)
        hbsizer.Add(c4,0)
        hsizer.Add(hbsizer, 0,wx.TOP | wx.BOTTOM,4)
        vsizer.Add(hsizer,0,wx.EXPAND)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hbsizer= wx.BoxSizer(wx.HORIZONTAL)
        hbsizer.Add(c5,0)
        hsizer.Add(hbsizer, 0,wx.TOP | wx.BOTTOM,4)
        vsizer.Add(hsizer,0,wx.EXPAND)
        gbsizer.Add(vsizer,(row,1)) #,(1,2))
        if self.apptype == "":
            row += 1
            gbsizer.Add(t6,(row,0), flag=wx.EXPAND | wx.ALL, border=4)
            gbsizer.Add(c6,(row,1), flag=wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
            gbsizer.Add(self.Zoek,(row,2), flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=4 )
        row += 1
        gbsizer.Add(c7,(row,1), flag=wx.EXPAND | wx.TOP | wx.BOTTOM,border=2)
        row += 1
        gbsizer.Add(t8,(row,0), flag=wx.EXPAND | wx.ALL, border=4)
        gbsizer.Add(c8,(row,1), flag=wx.ALIGN_CENTER_VERTICAL)
        if self.apptype == "multi":
            row += 1
            gbsizer.Add(t9,(row,0), (1,2), flag=wx.EXPAND | wx.LEFT | wx.TOP,border=4)
            row += 1
            gbsizer.Add(c9,(row,0), (1,2), flag=wx.EXPAND | wx.LEFT | wx.RIGHT,border=4)
        row += 1
        gbsizer.Add(c10,(row,1), flag = wx.EXPAND )
        row += 1
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(self.DoIt,0,wx.EXPAND | wx.ALL,4)
        hsizer.Add(self.Cancel,0,wx.EXPAND | wx.ALL,4)
        gbsizer.Add(hsizer,(row,0),(1,3), flag = wx.ALIGN_BOTTOM | wx.ALIGN_CENTER_HORIZONTAL, border=0)
        bsizer.Add(gbsizer,0, wx.ALL, 4)

        ## self.pnl.SetAutoLayout(True)
        self.pnl.SetSizer(bsizer)
        bsizer.Fit(self)
        ## bsizer.SetSizeHints(self)

        self.pnl.Layout()
        self.vraagZoek.SetFocus()
        #~ self.master.bind_all("<Escape>",self.einde)
        ## self.Bind(wx.EVT_KEY_UP,self.on_key_up)
        ## for win in self.GetChildren():
            ## self.Bind(wx.EVT_KEY_UP,self.on_key_up,win)
        self.Show(True)

    def einde(self,event):
        self.Close(True)

    def on_key_up(self,ev):
        print(ev.GetKeyCode())
        if ev.GetKeyCode() == wx.WXK_ESCAPE:
            self.einde()
        ev.Skip()

    def doe(self,event=None):
        self.zoekstr = self.vraagZoek.GetValue()
        self.vervstr = self.vraagVerv.GetValue()
        self.vervleeg = self.cVervang.GetValue()
        self.matchCase = self.vraagCase.GetValue()
        self.matchWords = self.vraagWoord.GetValue()
        if self.apptype == "":
            self.dirnaam = self.vraagDir.GetValue()
        self.searchSubdirs = self.vraagSubs.GetValue()
        self.typestr = self.vraagTypes.GetValue()
        self.backup = self.vraagBackup.GetValue()

        s = ""
        p = {}
        ft = "AFRIFT for TC fout" if self.apptype else "AFRIFT fout"
        mld = ""
        if len(self.fnames) > 0:
            p["filelist"] = self.fnames

        if not self.zoekstr:
            mld = "Kan niet zoeken zonder zoekargument"
        else:
            if self.zoekstr in self.mruZoek:
                self.mruZoek.remove(self.zoekstr)
            self.mruZoek.insert(0,self.zoekstr)
            s += "zoeken naar " + self.zoekstr
            p["zoek"] = self.zoekstr # zoekstring

        if not mld:
            if not self.vervstr:
                if self.vervleeg:
                    p["vervang"] = "" # vervangstring
                    s += "\nen weggehaald"
            else:
                if self.vervstr in self.mruVerv:
                    self.mruVerv.remove(self.vervstr)
                self.mruVerv.insert(0,self.vervstr)
                s = "\nen vervangen door " .join((s,self.vervstr))
                p["vervang"] = self.vervstr # vervangstring

        if not mld:
            ss = ""
            if self.matchCase:
                ss = "case-sensitive"
            p["case"] = self.matchCase # case-sensitive ja/nee

            if self.matchWords:
                ss = "".join((ss,",","hele woorden")) if ss \
                    else "".join((ss,"hele woorden"))
            p["woord"] =self.matchWords # woord/woorddeel
            s = "".join((s," (",ss,")")) if ss else s

        if not mld and self.typestr:
            if self.typestr in self.mruTypes:
                self.mruTypes.remove(self.typestr)
            self.mruTypes.insert(0,self.typestr)
            s = "\nin bestanden van type ".join((s,self.typestr))
            h = self.typestr.split(",")
            p["extlist"] = [x.lstrip().strip() for x in h[:]] # lijst extensies

        if not mld and not self.apptype: # te doorzoeken directory
            if not self.dirnaam:
                mld = "Ik wil wel graag weten in welke directory ik moet (beginnen met) zoeken"
            elif not os.path.exists(self.dirnaam):
                mld = "De opgegeven directory bestaat niet"
            else:
                if self.dirnaam in self.mruDirs:
                    self.mruDirs.remove(self.dirnaam)
                self.mruDirs.insert(0,self.dirnaam)
                s = "\nin ".join((s,self.dirnaam))
                p["pad"] = self.dirnaam # lijst dirs

        if not mld:
            if self.searchSubdirs:
                s += " en onderliggende directories"
            p["subdirs"] = self.searchSubdirs
            p["backup"] = self.backup

        if mld: # foutmelding geven en afbreken
            dlg = wx.MessageDialog(self,mld,ft,wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return

        self.schrijfini()
        h = findr(**p)
        if self.apptype:
            zr = "Afrift for TC - Resultaten"
        else:
            zr = "Albert's Find/Replace In Files Tool - Resultaten"
        if len(h.rpt) == 1:
            dlg = wx.MessageDialog(self,"Niks gevonden",zr,
                wx.OK | wx.ICON_INFORMATION)
        else:
            dlg = Results(self,-1,zr,rpt = h.rpt)
        dlg.ShowModal()
        dlg.Destroy()

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
    def zoekdir(self,event):
        oupad = self.vraagDir.GetValue()
        #~ if oupad == "":
            #~ if len(self.mruDirs) > 0:
                #~ oupad = self.mruDirs[0]
            #~ else:
                #~ oupad = self.hier
        #~ if not os.path.exists(oupad):
            #~ oupad = "C:\\"
        #~ pad = tkFileDialog.askdirectory()
        dlg = wx.DirDialog(self, "Choose a directory:",
            defaultPath = oupad,
            style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST
            )
        if dlg.ShowModal() == wx.ID_OK:
            self.vraagDir.SetValue(dlg.GetPath())
        dlg.Destroy()

class Appl_single(Application):
    def __init__(self,parent,h):
        # h[0] is dit programma zelf
        # h[1] is de naam van het te verwerken bestandeen bestand waarin de betreffende namen staan
        self.parent = parent
        self.title = "Albert's find-replace in files tool - for Total Commander, single file version"
        ## self.SetTitle(self.title)
        ## self.SetIcon(wx.Icon(iconame,wx.BITMAP_TYPE_ICO))
        self.fnames = [h[1]]
        t = h[1]
        for x in range(len(t),0,-1):
            if t[x-1] == "\\":
                break
        self.curdir = t[:x-1]
        self.apptype = 'single'
        self.go()

class Appl_multi(Application):
    def __init__(self,parent,h):
        # h[0] is dit programma zelf
        # h[1] is de naam van een bestand waarin de betreffende namen staan
        self.parent = parent
        self.title = "Albert's find-replace in files tool - for Total Commander"
        ## self.SetTitle(self.title)
        ## self.SetIcon(wx.Icon(iconame,wx.BITMAP_TYPE_ICO))
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


def MainFrame(apptype=None, data=None):
    app = wx.PySimpleApp(redirect=True,filename="afrift.log")
    if apptype == "Multi":
        h = Appl_multi(None, data)
    elif apptype == "Single":
        h = Appl_single(None, data)
    else:
        h = Application(None, -1)
    app.MainLoop()

def test():
    MainFrame()
    ## MainFrame(apptype="Multi",data=['afrift_wxgui.py','CMDAE.tmp'])
    ## MainFrame(apptype="Single",data=['afrift_wxgui.py','CMDAE.tmp'])

if __name__ == "__main__":
    test()
