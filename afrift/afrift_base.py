"""Gui-onafhankelijke code t.b.v. Afrift applicaties

het meeste hiervan bevind zich in een class die als mixin gebruikt wordt"""

import os
import collections
import json
import logging
import pathlib
BASE = pathlib.Path.home() / '.afrift'
if not BASE.exists():
    BASE.mkdir()
HERE = pathlib.Path(__file__).parent  # os.path.dirname(__file__)
iconame = str(HERE / "find.ico")  # os.path.join(HERE, "find.ico")
logging.basicConfig(
    filename=str(HERE.parent / 'logs' / 'afrift.log'),
    level=logging.DEBUG,
    format='%(asctime)s %(message)s')


def log(message):
    "output to log"
    if 'DEBUG' in os.environ and os.environ["DEBUG"] != "0":
        logging.info(message)


def get_iniloc(path=None):
    """determine location & filenames for stored settings
    """
    path = pathlib.Path(path) if path else pathlib.Path.cwd()
    if path == pathlib.Path.home():
        here = str(path)[1:]
    else:
        try:
            here = '~' + str(path.relative_to(pathlib.Path.home()))
        except ValueError:
            here = str(path)[1:]
    iniloc = BASE / here.replace('/', '_')
    log('in get_iniloc: iniloc={}'.format(iniloc))
    mrufile = iniloc / 'mru_items.json'
    optsfile = iniloc / 'options.json'
    return iniloc, mrufile, optsfile


class ABase(object):
    """
    mixin base class voor de Application classes

    deze class bevat methoden die onafhankelijk zijn van de gekozen
    GUI-toolkit"""

    def __init__(self, **kwargs):
        """attributen die altijd nodig zijn

        self.pickled geeft aan of bij het op de nieuwe manier (met pickle) lezen
        van de mru-settings gelukt is of niet.
        """
        log('in init van mixin: cwd is {}'.format(os.getcwd()))
        log('kwargs is {}'.format(kwargs))
        apptype = kwargs.pop('apptype', '')
        fnaam = kwargs.pop('fnaam', '')
        flist = kwargs.pop('flist', None)
        self.title = "Albert's find-replace in files tool"
        self.fouttitel = self.title + "- fout"
        self.resulttitel = self.title + " - Resultaten"
        self.apptype = apptype
        self.hier = ""
        self._mru_items = {}
        if self.apptype == "" and os.path.exists(fnaam) and not os.path.isdir(fnaam):
            self.apptype = 'single'
        if self.apptype == "":
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
                self.fnames = [fnaam]
        elif self.apptype == "single":
            self.title += " - single file version"
            if not fnaam:
                raise ValueError('Need filename for application type "single"')
            self.fnames = [fnaam]
            self.hier = os.path.dirname(fnaam)
        elif self.apptype == "multi":
            self.title += " - file list version"
            self.fnames = []
            if fnaam:
                try:
                    with open(fnaam) as f_in:
                        for line in f_in:
                            line = line.strip()
                            if not self.hier:
                                if line.endswith("\\") or line.endswith("/"):
                                    line = line[:-1]
                                self.hier = os.path.dirname(line)
                            self.fnames.append(line)
                except IsADirectoryError:
                    self.fnames = [fnaam]
            elif flist:
                self.fnames = flist
            else:
                raise ValueError('Need filename or list of files for application '
                                 'type "multi"')
        else:
            raise ValueError('application type should be empty, "single" or "multi"')
        self.s = ""
        self.p = {'filelist': []}
        if len(self.fnames) > 0:
            self.p["filelist"] = self.fnames
        for ix, name in enumerate(self.fnames):
            if name.endswith("\\") or name.endswith("/"):
                name = name[:-1]
            self.fnames[ix] = os.path.abspath(name)
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
        if self.p['filelist']:
            if self.apptype == 'single':
                self.readini(pathlib.Path(self.p['filelist'][0]).parent)
            elif self.apptype == 'multi':
                self.readini(os.path.commonpath(self.p['filelist']))
            else:
                self.readini(self.p['filelist'][0])
        else:
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
        self.editor_option = [x.split(' = ')[1].strip("'")
                              for x in test.strip().split('\n')]
        self._vervleeg = False
        self._backup = True
        self._exit_when_ready = False
        self.extraopts = collections.defaultdict(lambda: False)
        self.read_kwargs(kwargs)

    def readini(self, path=None):
        """lees ini file (met eerder gebruikte zoekinstellingen)

        geen settings file of niet te lezen dan initieel laten
        """
        loc, mfile, ofile = get_iniloc(path)
        log('in readini: {}, {}, {}'.format(loc, mfile, ofile))
        if loc.exists():
            log('reading files')
            with mfile.open() as _in:
                self._mru_items = json.load(_in)
            with ofile.open() as _in:
                opts = json.load(_in)
            self.p.update(opts)

    def read_kwargs(self, kwargs):
        """lees settings opties vanuit invoer; override waar opgegeven
        """
        self.p['zoek'] = kwargs.pop('search', '')
        test = kwargs.pop('replace', None)
        if test is not None:
            self.p['vervang'] = test
            if test == '':
                self._vervleeg = True
        self.p["extlist"] = kwargs.pop('extensions', '')
        if self.p["extlist"] is None:
            self.p["extlist"] = []
        for arg in ('regex',
                    'follow_symlinks',
                    'select_subdirs',
                    'select_files',
                    'use_saved',
                    'dont_save',
                    'no_gui',
                    'output_file'):
            self.extraopts[arg] = kwargs.pop(arg)
        if not self.extraopts['use_saved']:
            for arg, key in (('case_sensitive', "case"),
                             ('whole_words', "woord"),
                             ('recursive', "subdirs"),
                             ('python_context', "context"), ):
                self.p[key] = kwargs.pop(arg)
        self._backup = kwargs.pop('backup_originals')
        self._exit_when_ready = True

    def schrijfini(self, path=None):
        """huidige settings toevoegen dan wel vervangen in ini file"""
        loc, mfile, ofile = get_iniloc(path)
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
        opts = []
        if regex:
            opts.append("regular expression")
        self.p["regexp"] = regex
        if case:
            opts.append("case-sensitive")
        self.p["case"] = case
        if words:
            opts.append("hele woorden")
        self.p["woord"] = words
        if opts:
            self.s += " ({})".format(', '.join(opts))
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
            exts = item.split(",")
            self.p["extlist"] = [x.lstrip().strip() for x in exts]
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
