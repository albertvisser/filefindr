# -*- coding: UTF-8 -*-
import sys,os
import re
import shutil
from mystuff import splitjoin

class findr(object):
    def __init__(self,**parms):
        self.p = {
            'zoek':'',
            'vervang':'',
            'pad':'',
            'extlist':[],
            'filelist':[],
            'subdirs': False,
            "case": False,
            "woord": False,
            "regexp": False,
            "backup": False
            }
        for x in parms:
            if x in self.p:
                self.p[x] = parms[x]
            else:
                raise TypeError, 'Onbekende optie ' + x
        self.ok = True
        self.rpt = [] # verslag van wat er gebeurd is
        flist = ["G"," opgegeven"]
        if self.p['filelist'] == [] and self.p['pad'] == "":
            self.rpt.append("Fout: geen lijst bestanden en geen directory opgegeven")
        elif self.p['filelist'] != [] and self.p['pad'] != "":
            self.rpt.append("Fout: lijst bestanden én directory opgegeven")
        elif self.p['zoek'] == "":
            self.rpt.append('Fout: geen zoekstring opgegeven')
        if self.rpt:
            self.ok = False
            h = "Zoekactie niet mogelijk:"
        else:
            self.p['wijzig'] = True if self.p['vervang'] else False
            self.extlistUpper = []
            for x in self.p['extlist']:
                self.extlistUpper.append(x.upper())
            # moet hier nog iets mee doen m.h.o.o. woorddelen of niet
            if self.p['case']:
                self.re = re.compile(unicode(self.p['zoek']))
            else:
                self.re = re.compile(unicode(self.p['zoek']),re.IGNORECASE)
            if self.p['pad']:
                self.subdirs(self.p['pad'])
                #~ h = ("in %s" % (self.p['pad']))
                #~ if self.p['subdirs']: h = ("%s en onderliggende directories:" % h)
                #~ self.rpt.insert(0,h)
                h = ("Gezocht naar '%s'" % self.p['zoek'])
                if self.p['wijzig']:
                    h = ("%s en dit vervangen door '%s'" % (h,self.p['vervang']))
                if len(self.p['extlist']) > 0:
                    s = self.p['extlist'][0]
                    if len(self.p['extlist']) > 2:
                        for x in self.p['extlist'][1:-1]:
                            s = ("%s, %s" % (s,x))
                    if len(self.p['extlist']) > 1:
                        s = ("%s en %s" % (s,self.p['extlist'][-1]))
                    h = ("%s in bestanden van type %s" % (h,s))
            else:
                h = ("Gezocht naar '%s'" % self.p['zoek'])
                if self.p['wijzig']:
                    h = ("%s en dit vervangen door '%s' in:" % (h,self.p['vervang']))
                for entry in self.p['filelist']:
                    if not os.path.isdir(entry):
                        d = os.path.splitext(entry)
                        if len(self.p['extlist']) == 0 or d[1].upper() in self.extlistUpper:
                            self.zoek(entry)
                    else:
                        self.subdirs(entry)
                    #~ self.zoek(entry)
        self.rpt.insert(0,h)
        ## self.rpt.append("")

    def subdirs(self,pad):
        for file in os.listdir(pad):
            entry = os.path.join(pad,file)
            if not os.path.isdir(entry):
                h = os.path.splitext(entry)
                ## print h[1].upper(), self.extlistUpper
                if len(self.p['extlist']) == 0 or h[1].upper() in self.extlistUpper:
                    self.zoek(entry)
            else:
                if self.p['subdirs']:
                    self.subdirs(entry)

    def zoek(self,best):
        ## print "----"
        ## print(best)
        z = self.p['zoek']
        f = file(best,"r")
        regels = f.readlines()
        pos = 0
        lines = []
        for x in regels:
            ## print(x[:-1])
            lines.append(pos)
            pos += len(x)
        lines.append(pos)
        data = "".join(regels)
        f.close()
        nw = []
        i = 0
        found = False
        from_line = 0
        last_in_line = 0
        for vind in self.re.finditer(data):
            found = True
            ## print(vind.span())
            for lineno,linestart in enumerate(lines[from_line:]):
                ## print(from_line,lineno,linestart)
                if vind.start() < linestart:
                    if not self.p['wijzig']:
                        in_line = lineno + from_line
                        if in_line != last_in_line:
                            self.rpt.append("%s r. %i: %s" % (best,in_line,
                                regels[in_line - 1][:-1]))
                        last_in_line = in_line
                    from_line = lineno
                    break
        if found and self.p['wijzig']:
            aant, ndata = self.re.subn(unicode(self.p["vervang"]),data)
            self.rpt.append("%s: %s times" % (best,aant))
            if self.p['backup']:
                bestnw = best + ".bak"
                shutil.copyfile(best,bestnw)
            f = file(best,"w")
            f.write(ndata)
            f.close()

def test():
    h = findr(
        zoek="bestand\nwaarin",
        #vervang="voor",
        pad=os.getcwd(),
        #filelist=['test.py.txt',],
        extlist = [".txt",".ini"],
        subdirs=True, # zoeken in subdirectories
        case=True, # case-sensitive ja/nee
        woord=True, # woord/woorddeel
        #regexp=True,  # zoekstring is regexp
        #backup=True
        )
    f = open("whatidid.rpt","w")
    for x in h.rpt:
        f.write("%s\n" % x)
    f.close()
    for x in open("whatidid.rpt"):
        print x


if __name__ == '__main__':
    test()
