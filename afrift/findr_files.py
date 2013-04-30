# -*- coding: UTF-8 -*-
"""Uitvoeren van de find/replace actie

de uitvoering wordt gestuurd door in een dictionary verzamelde parameters"""

import sys
import os
import re
import shutil

class Finder(object):
    "interpreteren van de parameters en aansturen van de zoek/vervang routine"
    def __init__(self, **parms):
        ## print parms
        self.p = {
            'zoek': '',
            'vervang': '',
            'pad': '',
            'extlist': [],
            'filelist': [],
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
                raise TypeError('Onbekende optie ' + x)
        ## print self.p
        ## sys.exit()
        self.ok = True
        self.rpt = [] # verslag van wat er gebeurd is
        if not self.p['filelist'] and not self.p['pad']:
            self.rpt.append("Fout: geen lijst bestanden en geen directory opgegeven")
        elif self.p['filelist'] and self.p['pad']:
            self.rpt.append("Fout: lijst bestanden én directory opgegeven")
        elif not self.p['zoek']:
            self.rpt.append('Fout: geen zoekstring opgegeven')
        if self.rpt:
            self.ok = False
            specs = "Zoekactie niet mogelijk"
        else:
            self.p['wijzig'] = True if self.p['vervang'] is not None else False
            self.extlistUpper = []
            for x in self.p['extlist']:
                if not x.startswith("."):
                    x = "." + x
                self.extlistUpper.append(x.upper())
            # moet hier nog iets mee doen m.h.o.o. woorddelen of niet
            zoek = ''
            for ch in self.p['zoek']:
                if ch in ('.', '^','$','*','+','?','{','}','[',']','(',')','|','\\'):
                    zoek += "\\"
                zoek += ch
            if self.p['case']:
                if sys.version.startswith("3"):
                    self.re = re.compile(str(zoek))
                else:
                    self.re = re.compile(unicode(zoek))
            else:
                if sys.version.startswith("3"):
                    self.re = re.compile(str(zoek), re.IGNORECASE)
                else:
                    self.re = re.compile(unicode(zoek), re.IGNORECASE)
            specs = ["Gezocht naar '{0}'".format(self.p['zoek'])]
            if self.p['wijzig']:
                specs.append(" en dit vervangen door '{0}'".format(self.p['vervang']))
            if self.p['extlist']:
                if len(self.p['extlist']) > 1:
                     s = " en ".join((", ".join(self.p['extlist'][:-1]),
                                                self.p['extlist'][-1]))
                else:
                     s = self.p['extlist'][0]
                specs.append(" in bestanden van type {0}".format(s))
            if self.p['pad']:
                specs.append(" in {0}".format(self.p['pad']))
                self.subdirs(self.p['pad'])
            else:
                if len(self.p['filelist']) == 1:
                    specs.append(" in {0}".format(self.p['filelist'][0]))
                else:
                    specs.append(" in opgegeven bestanden/directories")
                for entry in self.p['filelist']:
                    if not os.path.isdir(entry):
                        d, ext = os.path.splitext(entry)
                        if ext.upper() in self.extlistUpper or not self.p['extlist']:
                            self.zoek(entry)
                    else:
                        self.subdirs(entry)
                    #~ self.zoek(entry)
            if self.p['subdirs']:
                specs.append(" en onderliggende directories")
            self.rpt.insert(0, "".join(specs))
        ## self.rpt.append("")

    def subdirs(self, pad):
        "recursieve routine voor zoek/vervang in subdirectories"
        for fname in os.listdir(pad):
            entry = os.path.join(pad, fname)
            ## print("zoeken in ",entry,sep = " ")
            if not os.path.isdir(entry):
                h, ext = os.path.splitext(entry)
                if len(self.p['extlist']) == 0 or ext.upper() in self.extlistUpper:
                    self.zoek(entry)
            else:
                if self.p['subdirs']:
                    self.subdirs(entry)

    def zoek(self, best):
        "het daadwerkelijk uitvoeren van de zoek/vervang actie op een bepaald bestand"
        print("----")
        print(best)
        pos = 0
        lines = []
        regels = []
        msg = ""
        with open(best, "r", encoding="latin-1") as f_in: # truc om niet-utf tekstfiles toch te kunnen lezen
            ## try:
                for x in f_in:
                    lines.append(pos)
                    x = x.rstrip() + os.linesep
                    ## x = " " + x
                    ## if x[0] == chr(13):
                        ## x = x[1:]
                    regels.append(x)
                    pos += len(x)
            ## except UnicodeDecodeError:
                ## self.rpt.append("{}: overgeslagen, waarschijnlijk geen tekst"
                    ## "bestand".format(best))
        lines.append(pos)
        data = "".join(regels)
        found = False
        from_line = 0
        last_in_line = 0
        for vind in self.re.finditer(data):
            found = True
            ## print(vind, vind.span(), sep = " ")
            for lineno, linestart in enumerate(lines[from_line:]):
                ## print(from_line,lineno,linestart)
                if vind.start() < linestart:
                    if not self.p['wijzig']:
                        in_line = lineno + from_line
                        if in_line != last_in_line:
                            self.rpt.append("{0} r. {1}: {2}".format(
                                best, in_line, regels[in_line - 1]))
                        last_in_line = in_line
                    from_line = lineno
                    break
        if found and self.p['wijzig']:
            ndata, aant = self.re.subn(unicode(self.p["vervang"]), data)
            self.rpt.append("%s: %s times" % (best, aant))
            if self.p['backup']:
                bestnw = best + ".bak"
                shutil.copyfile(best, bestnw)
            with open(best,"w") as f_out:
                f_out.write(ndata)

def test():
    "test routine"
    import logging
    logging.basicConfig(filename='whatidid.rpt')
    logger = logging.getLogger(__name__)
    h = Finder(
        zoek="logging",
        vervang=None, # "voor",
        pad='/home/albert',
        #filelist=['test.py.txt',],
        extlist = ['py'], # [".txt",".ini"],
        subdirs=True, # zoeken in subdirectories
        ## case=True, # case-sensitive ja/nee
        woord=True, # woord/woorddeel
        #regexp=True,  # zoekstring is regexp
        #backup=True
        )
    for x in h.rpt:
        logger.info("%s\n" % x)

if __name__ == '__main__':
    test()
