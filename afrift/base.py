"""Gui-toolkit onafhankelijke code t.b.v. Afrift applicaties

opgezet als classes die de toolkit-dependent code aanroepen als methodes op een attribuut ervan
ze worden geïmporteerd via een aparte module die bepaalt welke toolkit er gebruikt wordt
"""

import os
import collections
import subprocess
import json
import logging
import pathlib
from .gui import SelectNamesGui, ResultsGui, MainFrameGui
from .findr_files import Finder, format_result
BASE = pathlib.Path.home() / '.afrift'
if not BASE.exists():
    BASE.mkdir()
HERE = pathlib.Path(__file__).parent  # os.path.dirname(__file__)
LOGFILE = HERE.parent / 'logs' / 'afrift.log'
WANT_LOGGING = 'DEBUG' in os.environ and os.environ["DEBUG"] != "0"
if WANT_LOGGING:
    if not LOGFILE.parent.exists():
        LOGFILE.parent.mkdir()
    if not LOGFILE.exists():
        LOGFILE.touch()
    logging.basicConfig(filename=str(LOGFILE), level=logging.DEBUG,
                        format='%(asctime)s %(message)s')
common_path_txt = 'De bestanden staan allemaal in of onder de directory "{}"'
iconame = str(HERE / "find.ico")  # os.path.join(HERE, "find.ico")


def log(message):
    "output to log"
    if WANT_LOGGING:
        logging.info(message)


def get_iniloc(path=None):
    """determine location & filenames for stored settings
    if given, input should be an absolute path
    """
    path = pathlib.Path(path) if path else pathlib.Path.cwd()
    if path == pathlib.Path.home():
        here = str(path)[1:]
    else:
        try:
            here = '~' + str(path.relative_to(pathlib.Path.home()))
        except ValueError:
            here = str(path.resolve())[1:]
    iniloc = BASE / here.replace('/', '_')
    mrufile = iniloc / 'mru_items.json'
    optsfile = iniloc / 'options.json'
    return iniloc, mrufile, optsfile


class SelectNames():
    """Tussenscherm om te verwerken files te kiezen

    deze class bevat methoden die onafhankelijk zijn van de gekozen
    GUI-toolkit
    """
    def __init__(self, parent, files=True):
        self.do_files = files
        self.parent = parent
        self.title = self.parent.title + " - file list"
        self.iconame = iconame
        if files:
            text = "Selecteer de bestanden die je *niet* wilt verwerken"
            self.names = {str(x): x for x in self.parent.names}
        else:
            text = "Selecteer de directories die je *niet* wilt verwerken"
        self.gui = SelectNamesGui(parent, self)
        captions = {'heading': text, 'sel_all': 'Select/Unselect All', 'invert': 'Invert selection',
                    'exit': "&Terug", 'execute': "&Klaar"}
        self.gui.setup_screen(captions)

    def show(self):
        """show the dialog screen
        """
        return self.gui.go()


class Results():
    """Show results on screen

    deze class bevat methoden die onafhankelijk zijn van de gekozen
    GUI-toolkit
    """
    def __init__(self, parent, common_path=''):
        self.parent = parent
        self.common = common_path
        self.show_context = self.parent.p["context"]
        self.results = []
        self.titel = 'Regel' if self.parent.apptype == "single" else 'File/Regel'
        self.iconame = iconame
        self.gui = ResultsGui(parent, self)

        self.label_only = self.parent.p['vervang'] and self.parent.apptype == 'single'
        if self.label_only:
            aantal = self.parent.zoekvervang.rpt[1].split(None, 1)[1]
            label_txt = self.parent.zoekvervang.rpt[0]
            label_txt = label_txt.replace('vervangen', aantal + ' vervangen')
        else:
            label_txt = "{} ({} items)".format(self.parent.zoekvervang.rpt[0],
                                               len(self.parent.zoekvervang.rpt) - 1)
            if self.parent.apptype == "multi":
                label_txt += '\n' + common_path_txt.format(self.common.rstrip(os.sep))
        captions = {'heading': label_txt, 'ctxt': 'Context', 'txt': 'Tekst', 'hlp': 'Help',
                    'rslt': 'Goto Result', 'exit': "&Klaar", 'rpt': "&Repeat Search",
                    'cpy': "Copy to &File", 'clp': "Copy to &Clipboard", 'fmt': 'Formatteer output:',
                    'pth': "toon directorypad", 'dlm': "comma-delimited", 'sum': "summarized"}
        self.build_list()
        self.gui.setup_screen(captions)

    def build_list(self):
        "construct list of results"
        for ix, line in enumerate(self.parent.zoekvervang.rpt):
            if ix == 0:
                kop = line
            elif line != "":
                where, what = line.split(": ", 1)
                if self.parent.apptype == "single":
                    if "r. " in where:
                        where = where.split("r. ", 1)[1]
                    else:
                        where = ""
                if self.common and self.common != '/':
                    where = where.replace(str(self.common), "")
                if self.show_context:
                    where, rest = where.rsplit(' (', 1)
                    context = rest.split(')')[0]
                    self.results.append((where, context, what))
                else:
                    self.results.append((where, what))
        self.results.insert(0, kop)

    def show(self):
        """show the dialog screen
        """
        self.gui.go()

    def get_results(self):
        """format output
        """
        toonpad = self.gui.get_pth()
        comma = self.gui.get_csv()
        context = self.gui.get_sum()

        text = ["{}".format(self.results[0])]
        if self.parent.apptype == "multi" and not toonpad:
            text.append(common_path_txt.format(self.common))
        text.append("")
        if comma:
            import io
            import csv
            textbuf = io.StringIO()
            writer = csv.writer(textbuf, dialect='unix')
            header = [('Path/file' if toonpad else 'File'), 'Line', 'Context', 'Result']
        for item in self.results[1:]:
            result = list(item)
            if self.parent.apptype == 'single':
                result[0] = ' r. ' + result[0]
            if toonpad and (self.parent.apptype == 'multi' or comma):
                result[0] = self.common + result[0]
            if comma:
                loc, line = result[0].rsplit(' r. ', 1)
                result[:1] = [loc, line]
                if header and len(header) > len(result):
                    header[2:] = header[3:]
                if self.parent.apptype == 'single' and not toonpad:
                    result = result[1:]
                    if header:
                        header = header[1:]
                if header:
                    writer.writerow(header)
                    header = None
                writer.writerow(result)
            else:
                text.append(" ".join(result).strip())

        if comma:
            text += textbuf.getvalue().split("\n")
            textbuf.close()

        if context:
            context = 'py' if self.show_context else None
            if self.parent.apptype == 'single':
                text = ['{} {}'.format(self.parent.p['filelist'][0], x) if x else '' for x in text]
            text = format_result(text, context)
            if self.parent.apptype == 'single' and not toonpad:
                text = [x.replace(str(self.parent.p['filelist'][0]), '', 1).strip() for x in text]

        return text

    def refresh(self, *args):
        """repeat search and show new results
        """
        self.results = []
        self.gui.clear_contents()
        self.parent.zoekvervang.rpt = ["".join(self.parent.zoekvervang.specs)]
        self.parent.gui.set_waitcursor(True)
        self.parent.zoekvervang.go()
        self.parent.gui.set_waitcursor(False)
        if len(self.parent.zoekvervang.rpt) == 1:
            self.gui.breekaf("Niks gevonden")
        label_txt = "{} ({} items)".format(self.parent.zoekvervang.rpt[0],
                                           len(self.parent.zoekvervang.rpt) - 1)
        if self.parent.apptype == "multi":
            label_txt += '\n' + common_path_txt.format(self.common)

        self.gui.set_header(label_txt)
        self.build_list()
        self.gui.populate_list()

    def check_option_combinations_ok(self):
        """onzinnige combinatie(s) uitsluiten
        """
        title, msg = (self.parent.title,
                      "Summarize to comma delimited is not a sensible option, request denied")
        if self.gui.get_sum() and self.gui.get_csv():
            self.gui.meld(title, msg)
            return False
        return True

    def kopie(self, *args):
        """callback for button 'Copy to file'
        """
        if not self.check_option_combinations_ok():
            return
        f_nam = self.parent.p["zoek"]
        for char in '/\\?%*:|"><.':
            if char in f_nam:
                f_nam = f_nam.replace(char, "~")
        if self.gui.get_csv():
            ext = '.csv'
        else:
            ext = '.txt'
        f_nam = f_nam.join(("files-containing-", ext))
        savename = self.gui.get_savefile(f_nam, ext)
        if savename:
            self.gui.remember_settings()
            with open(savename, "w") as f_out:
                for line in self.get_results():
                    f_out.write(line + "\n")

    def help(self):
        """show instructions
        """
        self.gui.meld('info',
                      "Select a line and doubleclick or press Ctrl-G to open the indicated file\n"
                      "at the indicated line (not in single file mode)")

    def to_clipboard(self, *args):
        """callback for button 'Copy to clipboard'
        """
        if self.check_option_combinations_ok():
            self.gui.remember_settings()
            self.gui.copy_to_clipboard('\n'.join(self.get_results()))

    def goto_result(self, row, col):
        """open the file containing the selected item
        """
        if self.parent.apptype == 'single':
            self.gui.meld('ahem', 'Not in single file mode')
            return
        selected = self.results[row + 1]
        target, line = selected[0].split(' r. ')
        target = self.common + target
        prog, fileopt, lineopt = self.parent.editor_option
        subprocess.run([prog, fileopt.format(target), lineopt.format(line)])


class MainFrame():
    """Hoofdscherm van de applicatie

    deze class bevat methoden die onafhankelijk zijn van de gekozen
    GUI-toolkit
    """
    def __init__(self, **kwargs):
        """attributen die altijd nodig zijn
        """
        log('in MainFrame.init: cwd is {}'.format(pathlib.Path.cwd()))
        log('  kwargs is {}'.format(kwargs))
        self.apptype = kwargs.pop('apptype', '')
        fnaam = kwargs.pop('fnaam', '')
        flist = kwargs.pop('flist', None)
        self.title = "Albert's find-replace in files tool"
        self.iconame = iconame
        self.fouttitel = self.title + "- fout"
        self.resulttitel = self.title + " - Resultaten"
        # self.apptype = apptype
        self.hier = pathlib.Path.cwd()  # os.getcwd()
        self.mru_items = {"zoek": [], "verv": [], "types": [], "dirs": []}
        self.save_options_keys = (("case", 'case_sensitive'), ("woord", 'whole_words'),
                                 ("subdirs", 'recursive'), ("context", 'python_context'),
                                 ("negeer", 'ignore_comments'))
        self.outopts = {'full_path': False, 'as_csv': False, 'summarize': False}
        self.screen_choices = {'regex': False, 'case': False, 'woord': False,
                               'subdirs': False,'follow_symlinks': False, 'select_subdirs': False,
                               'select_files': False, 'context': False, 'negeer': False,
                               'dont_save': False, 'no_gui': False,
                               'output_file': False, 'full_path': False, 'as_csv': False,
                               'summarize': False}
        # het idee achter bovenstaande dict is om alle keuzes op het scherm te verzamelen
        # en ze eerst vanuit de opgeslagen waarden en daarna vanuit de
        # opgegeven startup-opties te vullen - zie ook onderstaande captions en read_kwargs()

        fnpath = pathlib.Path(fnaam).expanduser().resolve()
        if self.apptype == "" and fnpath.exists() and not fnpath.is_dir():
            self.apptype = 'single'

        fnames = self.get_filename_list(fnaam, fnpath, flist)
        self.s = ""
        self.p = {'filelist': []}
        if fnames:
            self.p["filelist"] = fnames
        self.cmdline_options = kwargs  # remember which options come from the command line
        self.setup_options()
        self.gui = MainFrameGui(self)
        captions = {'vraag_zoek': 'Zoek naar:', 'regex': "regular expression (Python format)",
                    'case': "hoofd/kleine letters gelijk", 'woord': "hele woorden",
                    'vraag_verv': 'Vervang door:', 'empty': "lege vervangtekst = weghalen",
                    'zoek': "&Zoek", 'in': "In directory:", 'in_s': "In file/directory:",
                    'in_m': "In de volgende files/directories:",
                    'subs_m': "van geselecteerde directories ",
                    'subs': "ook subdirectories doorzoeken",
                    'link': "symlinks volgen - max. diepte (-1 is alles):",
                    'skipdirs': "selecteer (sub)directories om over te slaan",
                    'skipfiles': "selecteer bestanden om over te slaan",
                    'ftypes': "Alleen files van type:",
                    'context': "context tonen (waar mogelijk, anders overslaan)",
                    'negeer': "commentaren en docstrings negeren",
                    'backup': "gewijzigd(e) bestand(en) backuppen",
                    'exit': "direct afsluiten na vervangen", 'exec': '&Uitvoeren',
                    'end': '&Einde'}
        self.gui.setup_screen(captions)
        if self.extraopts['no_gui']:
            self.doe()
        else:
            self.gui.go()

    def get_filename_list(self, fn_orig, fnaam, flist):
        fnames = []
        if self.apptype == "":
            if fn_orig:
                fnames = [fnaam]
        elif self.apptype == "single":
            self.title += " - single file version"
            if not fn_orig:
                raise ValueError('Need filename for application type "single"')
            fnames = [fnaam]
        elif self.apptype == "multi":
            self.title += " - multi-file version"
            if fn_orig:
                if fnaam.is_dir():
                    fnames = [fnaam]
                else:
                    with fnaam.open() as f_in:
                        for line in f_in:
                            line = line.strip()
                            if line.endswith("\\") or line.endswith("/"):
                                line = line[:-1]
                            line = pathlib.Path(line).expanduser().resolve()
                            fnames.append(line)
            elif flist:
                fnames = [pathlib.Path(x) for x in flist]
            else:
                raise ValueError('Need filename or list of files for application '
                                 'type "multi"')
        else:
            raise ValueError('application type should be empty, "single" or "multi"')
        return fnames

    def setup_options(self):
        if self.p['filelist']:
            if self.apptype == 'single':
                self.read_from_ini(self.p['filelist'][0].parent)
            elif self.apptype == 'multi':
                test = os.path.commonpath([str(x) for x in self.p['filelist']])
                self.read_from_ini(os.path.abspath(test))
            else:
                self.read_from_ini(self.p['filelist'][0])
        else:
            self.read_from_ini()

        encfile = BASE / 'fallback_encoding'
        try:
            test = encfile.read_text()
        except FileNotFoundError:
            test = 'latin-1\n'
            encfile.write_text(test)
        self.p['fallback_encoding'] = test.strip()

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

        self.always_replace = False
        self.maak_backups = True
        self.exit_when_ready = False
        self.extraopts = collections.defaultdict(lambda: False)
        self.apply_cmdline_options()

    def read_from_ini(self, path=None):
        """lees ini file (met eerder gebruikte zoekinstellingen)

        als geen settings file of niet te lezen dan initieel laten
        """
        loc, mfile, ofile = get_iniloc(path)
        if loc.exists():
            with mfile.open() as _in:
                self.mru_items = json.load(_in)
            with ofile.open() as _in:
                opts = json.load(_in)
                for key, value in self.outopts.items():
                    self.outopts[key] = opts.pop(key, '') or value
                for key in [x[0] for x in self.save_options_keys]:
                    self.p[key] = opts.pop(key, '') or value

    def apply_cmdline_options(self):
        """lees settings opties vanuit invoer; override waar opgegeven
        """
        self.p['zoek'] = self.cmdline_options.pop('search', '')
        test = self.cmdline_options.pop('replace', None)
        if test is not None:
            self.p['vervang'] = test
            if test == '':
                self.always_replace = True
        self.p["extlist"] = self.cmdline_options.pop('extensions', '')
        if not self.p["extlist"]:
            self.p["extlist"] = []

        # saved_options alleen toepassen als use-saved is opgegeven?
        self.extraopts['use_saved'] = self.cmdline_options.pop('use_saved', False)
        if not self.extraopts['use_saved']:
            for key, argname in self.save_options_keys:
                self.p[key] = self.cmdline_options.pop(argname, self.p.get(key, False))

        for arg in ('regex', 'follow_symlinks', 'select_subdirs', 'select_files',
                    'dont_save', 'no_gui', 'output_file', 'full_path', 'as_csv', 'summarize'):
            if arg in self.outopts:
                self.outopts[arg] = self.cmdline_options.pop(arg, '') or self.outopts[arg]
            else:
                self.extraopts[arg] = self.cmdline_options.pop(arg, '')
        self.maak_backups = self.cmdline_options.pop('backup_originals', '')
        self.exit_when_ready = True   # altijd aan?

    def write_to_ini(self, path=None):
        """huidige settings toevoegen dan wel vervangen in ini file

        indien opgegeven op de cmdline, dan niet onthouden (zie self.cmdline_options)
        """
        if self.extraopts['dont_save']:
            return
        loc, mfile, ofile = get_iniloc(path)
        if not loc.exists():
            loc.mkdir()
        with mfile.open("w") as _out:
            json.dump(self.mru_items, _out, indent=4)
        opts = {key: self.p[key] for key, argname in self.save_options_keys}
        opts.update(self.outopts)
        with ofile.open("w") as _out:
            json.dump(opts, _out, indent=4)

    def determine_common(self):
        """determine common part of filenames
        """
        if self.apptype == 'single':
            test = self.p['filelist'][0]
        elif self.apptype == 'multi':
            test = os.path.commonpath([str(x) for x in self.p['filelist']])
            ## if test in self.p['filelist']:
                ## pass
            ## else:
                ## while test and not os.path.exists(test):
                    ## test = test[:-1]
            # make sure common part is a directory
            if os.path.isfile(test):
                test = os.path.dirname(test) + os.sep
            else:
                test += os.sep
        else:
            test = str(self.p["pad"]) + os.sep
        return test

    def checkzoek(self, item):
        "controleer zoekargument"
        if not item:
            mld = "Kan niet zoeken zonder zoekargument"
        else:
            mld = ""
            try:
                self.mru_items["zoek"].remove(item)
            except ValueError:
                pass
            self.mru_items["zoek"].insert(0, item)
            self.s += "zoeken naar {0}".format(item)
            self.p["zoek"] = item
        return mld

    def checkverv(self, items):
        "controleer vervanging"
        mld = ""
        self.p["vervang"] = None
        vervang, leeg = items
        if vervang:
            try:
                self.mru_items["verv"].remove(vervang)
            except ValueError:
                pass
            self.mru_items["verv"].insert(0, vervang)
            self.s = "\nen vervangen door {0}".format(vervang)
            self.p["vervang"] = vervang
        elif leeg:
            self.s += "\nen weggehaald"
            self.p["vervang"] = ""
        return mld

    def checkattr(self, items):
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
                self.mru_items["types"].remove(item)
            except ValueError:
                pass
            self.mru_items["types"].insert(0, item)
            self.s += "\nin bestanden van type {0}".format(item)
            exts = item.split(",")
            self.p["extlist"] = [x.lstrip().strip() for x in exts]
        else:
            self.p["extlist"] = []
        return mld

    def checkpath(self, item):
        "controleer zoekpad"
        test = pathlib.Path(item)
        if not item:
            mld = ("Ik wil wel graag weten in welke directory ik moet "
                   "(beginnen met) zoeken")
        elif not test.exists():  # pathlib.Path(item).exists():
            mld = "De opgegeven directory bestaat niet"
        else:
            mld = ""
            try:
                self.mru_items["dirs"].remove(item)
            except ValueError:
                pass
            self.mru_items["dirs"].insert(0, item)
            self.s += "\nin {0}".format(item)
            self.p["pad"] = test  # item
            self.p['filelist'] = ''
        return mld

    def checksubs(self, items):
        "subdirs aangeven"
        subdirs, links, depth = items
        if subdirs:
            self.s += " en onderliggende directories"
        self.p["subdirs"] = subdirs
        self.p["follow_symlinks"] = links
        self.p["maxdepth"] = depth

    def doe(self):
        """Zoekactie uitvoeren en resultaatscherm tonen"""
        item = self.gui.get_searchtext()
        mld = self.checkzoek(item)
        if not mld:
            self.checkverv(self.gui.get_replace_args())
            self.checkattr(self.gui.get_search_attr())
            # volgens qt versie
            if self.apptype != "single" or self.p['filelist'][0].is_dir():
                self.checktype(self.gui.get_types_to_search())
            # volgens wx versie
            # try:
            #     typelist = self.gui.get_types_to_search()
            # except AttributeError:
            #     typelist = None
            # if typelist:
            #     self.checktype(typelist)
            if not self.apptype:
                mld = self.checkpath(self.gui.get_dir_to_search())
        if not mld:
            # volgens qt versie
            if self.apptype != "single" or self.p['filelist'][0].is_dir():
                self.checksubs(self.gui.get_subdirs_to_search())
            elif self.apptype == "single" and self.p['filelist'][0].is_symlink():
                self.p["follow_symlinks"] = True
            # volgens wx versie
            # try:
            #     self.checksubs(self.gui.get_subdirs_to_search())
            # except aAttributeError:
            #     pass
        self.p["backup"] = self.gui.get_backup()
        self.p["negeer"] = self.gui.get_ignore()
        self.p["context"] = self.gui.get_context()

        if mld:
            self.gui.error(self.fouttitel, mld)
            return

        self.gui.add_item_to_searchlist(item)
        if not self.extraopts['dont_save']:
            loc = self.p.get('pad', '') or str(self.p['filelist'][0].parent)
            self.write_to_ini(os.path.abspath(loc))
        self.zoekvervang = Finder(**self.p)

        if not self.zoekvervang.ok:
            self.gui.meld(self.resulttitel, '\n'.join(self.zoekvervang.rpt),
                          self.zoekvervang.errors)
            return

        if not self.zoekvervang.filenames:
            self.gui.meld(self.resulttitel, "Geen bestanden gevonden")
            return

        common_part = self.determine_common()
        if self.apptype == "single" or (
                len(self.p['filelist']) == 1 and self.p['filelist'][0].is_file()):
            pass
        else:
            skip_dirs = self.gui.get_skipdirs()
            skip_files = self.gui.get_skipfiles()
            go_on = skip_dirs or skip_files
            canceled = False
            while go_on:
                if skip_dirs:
                    # eerste ronde: toon directories
                    if self.zoekvervang.dirnames:
                        self.names = sorted(self.zoekvervang.dirnames)

                        result = SelectNames(self, files=False).show()
                        if not result:
                            canceled = True
                            break

                        fnames = self.zoekvervang.filenames[:]
                        for entry in fnames:
                            for name in self.names:
                                # if str(entry).startswith(name + '/'):
                                if entry.parent == name:
                                    self.zoekvervang.filenames.remove(entry)
                                    break
                        if not skip_files:
                            go_on = False
                if skip_files:
                    # tweede ronde: toon de files die overblijven
                    self.names = sorted(self.zoekvervang.filenames)  # , key=lambda x: str(x))
                    result = SelectNames(self).show()
                    if not result and not skip_dirs:
                        canceled = True
                        break
                    elif result:
                        self.zoekvervang.filenames = self.names
                        go_on = False

            if canceled:
                return

        self.gui.set_waitcursor(True)
        self.zoekvervang.go()  # do_action()  # search_python=self.p["context"])
        self.gui.set_waitcursor(False)

        self.noescape = True    # wx versie: switch tbv afsluiten dialoog met Escape
        if len(self.zoekvervang.rpt) == 1:
            if self.extraopts['output_file']:
                print('No results')
            else:
                mld = "Niks gevonden" if self.zoekvervang.ok else self.zoekvervang.rpt[0]
                self.gui.meld(self.resulttitel, mld)
        else:
            dlg = Results(self, common_part)

            if self.extraopts['output_file']:
                with self.extraopts['output_file'] as f_out:
                    for line in dlg.get_results():
                        f_out.write(line + "\n")
            else:
                dlg.show()

        if (self.extraopts['no_gui'] and self.extraopts['output_file']) or (
                self.gui.get_exit() and self.p["vervang"] is not None):
            self.gui.einde()
