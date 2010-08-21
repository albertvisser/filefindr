"""Gui-onafhankelije code t.b.v. Afrift applicaties

het meeste hiervan bevind zich in een class die als mixin gebruikt wordt"""

import os
import sys
if sys.version.startswith('3'):
    from configparser import SafeConfigParser
else:
    from ConfigParser import SafeConfigParser
HERE = os.path.dirname(__file__)
iconame = os.path.join(HERE,"find.ico")

class ABase(object):
    """
    mixin base class voor de Application classes

    deze class bevat methoden die onafhanelijk zijn van de gekozen
    GUI-toolkit"""

    def __init__(self, parent, apptype="", data=""):
        "attributen die altijd nodig zijn"
        self.parent = parent
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
            self.fnames = [data,]
            self.hier = os.path.dirname(data)
        elif self.apptype == "multi": # data is file met namen om te verwerken
            self.title += " - file list version"
            self.fnames = []
            with open(data) as f_in:
                for line in f_in:
                    line = line.strip()
                    if not self.hier:
                        self.hier = os.path.dirname(line)
                    if line.endswith("\\") or line.endswith("/"):
                        # directory afwandelen en onderliggende files verzamelen
                        pass
                    else:
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
        self.readini()
        self._vervleeg = False
        self._backup = True

    def readini(self):
        "lees ini file (met eerder gebruikte zoekinstellingen)"
        self.inifile = self.hier + "/afriftftc.ini"
        # inlezen mru-gegevens
        self._mruItems["zoek"] = []
        self._mruItems["verv"] = []
        self._mruItems["types"] = []
        self._mruItems["dirs"] = []
        self.p["case"] = False
        self.p["woord"] = False
        self.p["subdirs"] = False
        s = SafeConfigParser()
        s.read(self.inifile)
        if s.has_section("zoek"):
            for i in range(len(s.options("zoek"))):
                ky = ("woord%i"  % (i+1))
                self._mruItems["zoek"].append(s.get("zoek", ky))
        if s.has_section("vervang"):
            for i in range(len(s.options("vervang"))):
                ky = ("woord%i"  % (i+1))
                self._mruItems["verv"].append(s.get("vervang", ky))
        if s.has_section("filetypes"):
            for i in range(len(s.options("filetypes"))):
                ky = ("spec%i"  % (i+1))
                self._mruItems["types"].append(s.get("filetypes", ky))
        if s.has_section("dirs"):
            for i in range(len(s.options("dirs"))):
                ky = ("pad%i"  % (i+1))
                self._mruItems["dirs"].append(s.get("dirs", ky))
        if s.has_section("options"):
            if s.has_option("options", "matchCase"):
                if s.getboolean("options", "matchCase"):
                    self.p["case"] = True
            if s.has_option("options", "matchWords"):
                if s.getboolean("options", "matchWords"):
                    self.p["woord"] = True
            if s.has_option("options", "searchSubdirs"):
                if s.getboolean("options", "searchSubdirs"):
                    self.p["subdirs"] = True
        ## print self._mruItems

    def schrijfini(self):
        """huidige settings toevoegen dan wel vervangen in ini file"""
        ## print self.p
        s = SafeConfigParser()
        ## print "*** schrijfini ***"
        ## print self._mruItems
        for ix, item in enumerate(self._mruItems["zoek"]):
            if ix == 0:
                s.add_section("zoek")
            s.set("zoek", "woord{0}".format(ix + 1), item)
        for ix, item in enumerate(self._mruItems["verv"]):
            if ix == 0:
                s.add_section("vervang")
            s.set("vervang", "woord{0}".format(ix + 1), item)
        for ix, item in enumerate(self._mruItems["types"]):
            if ix == 0:
                s.add_section("filetypes")
            s.set("filetypes", "spec{0}".format(ix + 1), item)
        for ix, item in enumerate(self._mruItems["dirs"]):
            if ix == 0:
                s.add_section("dirs")
            s.set("dirs", "pad{0}".format(ix + 1), item)
        s.add_section("options")
        h = "True" if self.p["case"] else "False"
        s.set("options", "matchCase", h)
        h = "True" if self.p["woord"] else "False"
        s.set("options", "matchWords", h)
        h = "True" if self.p["subdirs"] else "False"
        s.set("options", "searchSubdirs", h)
        with open(self.inifile, "w") as f_out:
            s.write(f_out)

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
