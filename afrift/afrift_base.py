"""Gui-onafhankelijke code t.b.v. Afrift applicaties

het meeste hiervan bevind zich in een class die als mixin gebruikt wordt"""

import os
import sys
import pathlib
BASE = pathlib.Path(os.environ['HOME']) / '.afrift'
if not BASE.exists():
    BASE.mkdir()
HERE = os.path.dirname(__file__)
iconame = os.path.join(HERE,"find.ico")
## import pickle
import json
import logging
logging.basicConfig(filename=os.path.join(os.path.dirname(HERE), 'logs',
    'afrift.log'), level=logging.DEBUG, format='%(asctime)s %(message)s')

def log(message):
    if 'DEBUG' in os.environ and os.environ["DEBUG"] != "0":
        logging.info(message)

def get_iniloc():
    here = str(pathlib.Path.cwd()).replace(os.environ['HOME'] + '/', '~').replace(
        '/', '_')
    if here[0] == '_':
        here = here[1:]
    iniloc = BASE / here
    mrufile = iniloc / 'mru_items.json'
    optsfile = iniloc / 'options.json'
    return iniloc, mrufile, optsfile

class ABase(object):
    """
    mixin base class voor de Application classes

    deze class bevat methoden die onafhankelijk zijn van de gekozen
    GUI-toolkit"""

    ## def __init__(self, parent, apptype="", fnaam="", flist=None):
    def __init__(self, apptype="", fnaam="", flist=None):
        """attributen die altijd nodig zijn

        self.pickled geeft aan of bij het op de nieuwe manier (met pickle) lezen
        van de mru-settings gelukt is of niet.
        """
        ## if len(data) > 1:
            ## prognaam, fnaam = data
        ## try:
            ## self.parent = parent
        ## except AttributeError: # ppygui doet dit zelf al
            ## pass
        self.title = "Albert's find-replace in files tool"
        self.fouttitel = self.title + "- fout"
        self.resulttitel = self.title + " - Resultaten"
        self.apptype = apptype
        self.hier = ""
        self._mru_items = {}
        if apptype == "":
            self.fnames = []
            self.hier = os.getcwd()
            if fnaam.startswith('...'):
                pass
            elif fnaam.startswith('..'):
                fnaam = fnaam.replace('..', os.path.dirname(self.hier), 1)
            elif fnaam.startswith('.'):
                fnaam = fnaam.replace('.', self.hier, 1)
            elif fnaam.startswith('~'):
                fnaam = os.path.expanduser(fnaam)
            if fnaam:
                ## if os.path.exists(fnaam) and not os.path.isdir(fnaam):
                    ## fnaam = os.path.dirname(fnaam)
                self.fnames = [fnaam,]
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
        self._keys = ("zoek", "verv", "types", "dirs")
        for key in self._keys:
            self._mru_items[key] = []
        self._optionskey = "options"
        self._sections = ('zoek', 'vervang', 'filetypes', 'dirs')
        self._words = ('woord', 'woord', 'spec', 'pad', )
        self._optkeys = ("case", "woord", "subdirs", "context")
        for key in self._optkeys:
            self.p[key] = False
        self._options = ("matchcase", "matchwords", "searchsubdirs", "showcontext")
        self.readini()
        encfile = BASE / 'fallback_encoding'
        try:
            test = encfile.read_text()
        except FileNotFoundError:
            test = 'latin-1\n'
            encfile.write_text(test)
        self._fallback_encoding = test.strip()
        edfile = BASE / 'open_result'
        try:
            test = edfile.read_text()
        except FileNotFoundError:
            test = '\n'.join(("program = 'SciTE'",
                "file-option = '-open:{}'",
                "line-option = '-goto:{}'",
                ""))
            edfile.write_text(test)
        self._editor_option = [x.split(' = ')[1].strip("'")
            for x in test.strip().split('\n')]
        self._vervleeg = False
        self._backup = True
        self._exit_when_ready = False

    def readini(self):
        """lees ini file (met eerder gebruikte zoekinstellingen)

        geen settings file of niet te lezen dan initieel laten
        """
        loc, mfile, ofile = get_iniloc()
        if loc.exists():
            with mfile.open() as _in:
                self._mru_items = json.load(_in)
            with ofile.open() as _in:
                opts = json.load(_in)
            self.p.update(opts)

    def schrijfini(self):
        """huidige settings toevoegen dan wel vervangen in ini file"""
        loc, mfile, ofile = get_iniloc()
        if not loc.exists():
            loc.mkdir()
        with mfile.open("w") as _out:
            json.dump(self._mru_items, _out, indent=4)
        opts = {key: self.p[key] for key in self._optkeys}
        with ofile.open("w") as _out:
            json.dump(opts, _out, indent=4)

    def checkzoek(self, item):
        "controleer zoekargument"
        if not item:
            mld = "Kan niet zoeken zonder zoekargument"
        else:
            mld = ""
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
        regex, case, words = items
        ss = []
        if regex:
            ss.append("regular expression")
        self.p["regexp"] = regex
        if case:
            ss.append("case-sensitive")
        self.p["case"] = case
        if words:
            ss.append("hele woorden")
        self.p["woord"] = words
        if ss:
            self.s += " ({0})".format(', '.join(ss))
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
            self.p['filelist'] = ''
        return mld

    def checksubs(self, *items):
        "subdirs aangeven"
        subdirs, links, depth = items
        if subdirs:
            self.s += " en onderliggende directories"
        self.p["subdirs"] = subdirs
        self.p["follow_symlinks"] = links
        self.p["maxdepth"] = depth

