"""Gui-onafhankelijke code t.b.v. Afrift applicaties

het meeste hiervan bevind zich in een class die als mixin gebruikt wordt"""

import os
import sys
HERE = os.path.dirname(__file__)
iconame = os.path.join(HERE,"find.ico")
import pickle

class ABase(object):
    """
    mixin base class voor de Application classes

    deze class bevat methoden die onafhankelijk zijn van de gekozen
    GUI-toolkit"""

    def __init__(self, parent, apptype="", fnaam="", flist=None):
        """attributen die altijd nodig zijn

        self.pickled geeft aan of bij het op de nieuwe manier (met pickle) lezen
        van de mru-settings gelukt is of niet.
        """
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
        self._mru_items = {}
        if apptype == "":
            self.fnames = []
            self.hier = os.getcwd()
        elif self.apptype == "single": # data is file om te verwerken
            self.title += " - single file version"
            if not fnaam:
                raise ValueError('Need filename for application type "single"')
            self.fnames = [fnaam,]
            self.hier = os.path.dirname(fnaam)
        elif self.apptype == "multi": # data is file met namen om te verwerken
            self.title += " - file list version"
            self.fnames = []
            if fnaam:
                with open(fnaam) as f_in:
                    for line in f_in:
                        line = line.strip()
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
            elif flist:
                self.fnames = flist
            else:
                raise ValueError('Need filename or list of files for application'
                    ' type "multi"')
        else:
            raise ValueError('application type should be empty, "single" or "multi"')
        self.s = ""
        self.p = {}
        if len(self.fnames) > 0:
            self.p["filelist"] = self.fnames
        for ix, name in enumerate(self.fnames):
            if name.endswith("\\") or name.endswith("/"):
                self.fnames[ix] = name[:-1]
        if os.access(self.hier, os.W_OK):
            self._inifile = os.path.join(self.hier, "afrift.ini")
        else:
            self._inifile = os.path.join(os.path.dirname(__file__), "afrift.ini")
        self._keys = ("zoek", "verv", "types", "dirs")
        for key in self._keys:
            self._mru_items[key] = []
        self._optionskey = "options"
        self._sections = ('zoek', 'vervang', 'filetypes', 'dirs')
        self._words = ('woord', 'woord', 'spec', 'pad', )
        self._optkeys = ("case", "woord", "subdirs")
        for key in self._optkeys:
            self.p[key] = False
        self._options = ("matchcase", "matchwords", "searchsubdirs")
        self.pickled = self.readini()
        self._vervleeg = False
        self._backup = True
        self._exit_when_ready = False

    def readini(self):
        """lees ini file (met eerder gebruikte zoekinstellingen)

        geen settings file of niet te lezen dan initieel laten
        """
        pickled = True
        try:
            with open(self._inifile, 'rb') as f_in:
                try:
                    self._mru_items = pickle.load(f_in)
                except pickle.PickleError:
                    pickled = False
                if pickled:
                    for opt in self._optkeys:
                        self.p[opt] = pickle.load(f_in)
        except IOError:
            pass
        return pickled # voor als je wilt terugmelden dat het settings ophalen mislukt is

    def schrijfini(self):
        """huidige settings toevoegen dan wel vervangen in ini file"""
        with open(self._inifile, "wb") as f_out:
            pickle.dump(self._mru_items, f_out, protocol=2)
            for opt in self._optkeys:
                pickle.dump(self.p[opt], f_out, protocol=2)

    def checkzoek(self, item):
        "controleer zoekargument"
        if not item:
            mld = "Kan niet zoeken zonder zoekargument"
        else:
            mld = ""
            print(item, ";", self._mru_items["zoek"])
            print(item in self._mru_items["zoek"])
            try:
                self._mru_items["zoek"].remove(item)
            except ValueError:
                pass
            self._mru_items["zoek"].insert(0, item)
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
                self._mru_items["verv"].remove(vervang)
            except ValueError:
                pass
            self._mru_items["verv"].insert(0, vervang)
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
        if item:
            try:
                self._mru_items["types"].remove(item)
            except ValueError:
                pass
            self._mru_items["types"].insert(0, item)
            self.s += "\nin bestanden van type {0}".format(item)
            h = item.split(",")
            self.p["extlist"] = [x.lstrip().strip() for x in h]
        else:
            self.p["extlist"] = []
        return mld

    def checkpath(self, item):
        "controleer zoekpad"
        if not item:
            mld = ("Ik wil wel graag weten in welke directory ik moet "
                   "(beginnen met) zoeken")
        elif not os.path.exists(item):
            mld = "De opgegeven directory bestaat niet"
        else:
            mld = ""
            try:
                self._mru_items["dirs"].remove(item)
            except ValueError:
                pass
            self._mru_items["dirs"].insert(0, item)
            self.s += "\nin {0}".format(item)
            self.p["pad"] = item
        return mld

    def checksubs(self, *items):
        "subdirs aangeven"
        subdirs, links, depth = items
        if subdirs:
            self.s += " en onderliggende directories"
        self.p["subdirs"] = subdirs
        self.p["follow_symlinks"] = links
        self.p["maxdepth"] = depth

