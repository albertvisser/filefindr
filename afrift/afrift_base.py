"""Gui-onafhankelije code t.b.v. Afrift applicaties

het meeste hiervan bevind zich in een class die als mixin gebruikt wordt"""

import os
import sys
try:
    from configobj import ConfigObj
except ImportError:
    sys.exit('configobj waarschijnlijk niet geinstalleerd')
HERE = os.path.dirname(__file__)
iconame = os.path.join(HERE,"find.ico")

class ABase(object):
    """
    mixin base class voor de Application classes

    deze class bevat methoden die onafhanelijk zijn van de gekozen
    GUI-toolkit"""

    def __init__(self, parent, apptype="", fnaam=""):
        "attributen die altijd nodig zijn"
        ## if len(data) > 1:
            ## prognaam, fnaam = data
        try:
            self.parent = parent
        except AttributeError: # ppygui doet dit zelf al
            pass
        self.title = "Albert's find-replace in files tool"
        self.fouttitel = self.title + "- fout"
        self.resulttitel = self.title + " - Resultaten"
        self.apptype = apptype
        self.hier = ""
        self._mruItems = {}
        if apptype == "":
            self.fnames = []
            self.hier = os.getcwd()
        elif self.apptype == "single": # data is file om te verwerken
            self.title += " - single file version"
            self.fnames = [fnaam,]
            self.hier = os.path.dirname(fnaam)
        elif self.apptype == "multi": # data is file met namen om te verwerken
            self.title += " - file list version"
            self.fnames = []
            with open(fnaam) as f_in:
                for line in f_in:
                    ## line = line.strip()
                    if not self.hier:
                        if line.endswith("\\") or line.endswith("/"):
                            line = line[:-1]
                        self.hier = os.path.dirname(line)
                    ## if line.endswith("\\") or line.endswith("/"):
                        ## # directory afwandelen en onderliggende files verzamelen
                        ## pass
                    ## else:
                        ## self.fnames.append(line)
                    self.fnames.append(line)
        else:
            raise ValueError('application type should be empty, "single" or "multi"')
        self.s = ""
        self.p = {}
        if len(self.fnames) > 0:
            self.p["filelist"] = self.fnames
        for ix, name in enumerate(self.fnames):
            if name.endswith("\\") or name.endswith("/"):
                self.fnames[ix] = name[:-1]
        self._inifile = os.path.join(self.hier, "afrift.ini")
        self._keys = ("zoek", "verv", "types", "dirs")
        self._optionskey = "options"
        self._sections = ('zoek', 'vervang', 'filetypes', 'dirs')
        self._words = ('woord', 'woord', 'spec', 'pad', )
        self._optkeys = ("case", "woord", "subdirs")
        self._options = ("matchcase", "matchwords", "searchsubdirs")
        self.readini()
        self._vervleeg = False
        self._backup = True

    def readini(self):
        "lees ini file (met eerder gebruikte zoekinstellingen)"
        for key in self._keys:
            self._mruItems[key] = []
        for key in self._optkeys:
            self.p[key] = False
        conf = ConfigObj(self._inifile)
        for ix, sect in enumerate(self._keys):
            if self._sections[ix] in conf:
                for nr, item in enumerate(conf[self._sections[ix]]):
                    ky = "".join((self._words[ix],str(nr + 1)))
                    self._mruItems[sect].append(conf[self._sections[ix]][ky])
        if self._optionskey in conf:
            for ix, opt in enumerate(self._options):
                if opt in conf[self._optionskey]:
                    if conf[self._optionskey].as_bool(opt):
                        self.p[self._optkeys[ix]] = True

    def schrijfini(self):
        """huidige settings toevoegen dan wel vervangen in ini file"""
        conf = ConfigObj()
        conf.filename = self._inifile
        for ix, sect in enumerate(self._sections):
            for nr, item in enumerate(self._mruItems[self._keys[ix]]):
                if nr == 0:
                    conf[sect] = {}
                ky = "".join((self._words[ix],str(nr + 1)))
                conf[sect][ky] = item
        for ix, opt in enumerate(self._options):
            if ix == 0:
                conf[self._optionskey] = {}
            h = "True" if self.p[self._optkeys[ix]] else "False"
            conf[self._optionskey][opt] = h
        conf.write()

    def checkzoek(self, item):
        "controleer zoekargument"
        if not item:
            mld = "Kan niet zoeken zonder zoekargument"
        else:
            mld = ""
            try:
                self._mruItems["zoek"].remove(item)
            except ValueError:
                pass
            self._mruItems["zoek"].insert(0, item)
            self.s += "zoeken naar {0}".format(item)
            self.p["zoek"] = item
        return mld

    def checkverv(self, *items):
        "controleer vervanging"
        mld = ""
        self.p["vervang"] = None
        vervang, leeg = items
        if vervang:
            try:
                self._mruItems["verv"].remove(vervang)
            except ValueError:
                pass
            self._mruItems["verv"].insert(0, vervang)
            self.s = "\nen vervangen door {0}".format(vervang)
            self.p["vervang"] = vervang
        elif leeg:
            self.s += "\nen weggehaald"
            self.p["vervang"] = ""
        return mld

    def checkattr(self, *items):
        "controleer extra opties"
        mld = ""
        case, words = items
        ss = ""
        if case:
            ss = "case-sensitive"
        self.p["case"] = case
        if words:
            if ss:
                ss += ", "
            ss += "hele woorden"
        self.p["woord"] = words
        if ss:
            self.s += " ({0})".format(ss)
        return mld

    def checktype(self, item):
        "controleer speciale bestandstypen (extensies)"
        mld = ""
        try:
            self._mruItems["types"].remove(item)
        except ValueError:
            pass
        self._mruItems["types"].insert(0, item)
        self.s += "\nin bestanden van type {0}".format(item)
        h = item.split(",")
        self.p["extlist"] = [x.lstrip().strip() for x in h]
        return mld

    def checkpath(self, item):
        "controleer zoekpad"
        if not item:
            mld = "Ik wil wel graag weten in welke directory ik moet (beginnen met) zoeken"
        elif not os.path.exists(item):
            mld = "De opgegeven directory bestaat niet"
        else:
            mld = ""
            try:
                self._mruItems["dirs"].remove(item)
            except ValueError:
                pass
            self._mruItems["dirs"].insert(0, item)
            self.s += "\nin {0}".format(item)
            self.p["pad"] = item
        return mld

    def checksubs(self, item):
        "subdirs aangeven"
        if item:
            self.s += " en onderliggende directories"
        self.p["subdirs"] = item
