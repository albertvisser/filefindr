"""Gui-toolkit onafhankelijke code t.b.v. Afrift applicaties

opgezet als classes die de toolkit-dependent code aanroepen als methodes op een attribuut ervan
ze worden geïmporteerd via een aparte module die bepaalt welke toolkit er gebruikt wordt
"""

import os
import collections
import subprocess
import contextlib
import json
import logging
import pathlib
import io
import csv
from .gui import SelectNamesGui, ResultsGui, AfriftGui
from .findr_files import Finder, reformat_result
BASE = pathlib.Path.home() / '.afrift'
BASE.mkdir(exist_ok=True)
HERE = pathlib.Path(__file__).parent  # os.path.dirname(__file__)
LOGFILE = HERE.parent / 'logs' / 'afrift.log'
logging.basicConfig(filename=str(LOGFILE), level=logging.DEBUG, format='%(asctime)s %(message)s')
WANT_LOGGING = 'DEBUG' in os.environ and os.environ["DEBUG"] != "0"
common_path_txt = 'De bestanden staan allemaal in of onder de directory "{}"'
iconame = str(HERE / "find.ico")  # os.path.join(HERE, "find.ico")


def main(args):
    """Entry point for application
    """
    # preliminary actions, earlier in module level code
    if WANT_LOGGING:
        LOGFILE.parent.mkdir(exist_ok=True)
        LOGFILE.touch(exist_ok=True)
    # some screening, then relay the arguments to the application class
    # args['apptype'] = args.pop('appmode')
    if args['output_file']:
        if args['as_csv'] and args['summarize']:
            return "'Output to csv' and 'summarize' is not a sensible combination"
    else:
        for option in ('full_path', 'as_csv', 'summarize'):
            if args.get(option, ''):
                return 'Output options without output destination not allowed'
    # test = args.pop('fname')
    # if len(test) > 1:
    #     args['flist'] = test
    #     args['apptype'] = 'multi'
    # elif test:
    #     args['fnaam'] = test[0]
    try:
        Afrift(**args)
    except ValueError as err:
        return str(err)
    return ''


class Afrift:
    """Hoofdscherm van de applicatie

    deze class bevat methoden die onafhankelijk zijn van de gekozen
    GUI-toolkit
    """
    def __init__(self, **kwargs):
        """attributen die altijd nodig zijn
        """
        log(f'in Afrift.init: cwd is {pathlib.Path.cwd()}')
        log(f'  kwargs is {kwargs}')
        # self.apptype = kwargs.pop('apptype', '')
        # fnaam = kwargs.pop('fnaam', '')
        # flist = kwargs.pop('flist', None)
        fnames = kwargs.pop('fnames', [])
        list_file = kwargs.pop('list_file', '')
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
                               'subdirs': False, 'follow_symlinks': False, 'select_subdirs': False,
                               'select_files': False, 'context': False, 'negeer': False,
                               'dont_save': False, 'no_gui': False,
                               'output_file': False, 'full_path': False, 'as_csv': False,
                               'summarize': False}
        # het idee achter bovenstaande dict is om alle keuzes op het scherm te verzamelen
        # en ze eerst vanuit de opgeslagen waarden en daarna vanuit de
        # opgegeven startup-opties te vullen - zie ook onderstaande captions en read_kwargs()

        # fnpath = pathlib.Path(fnaam).expanduser().resolve()
        # if self.apptype == "" and fnpath.exists() and not fnpath.is_dir():
        #     self.apptype = 'single'

        # self.p = {'filelist': self.get_filename_list(fnaam, fnpath, flist)}
        if fnames:
            if list_file:
                raise ValueError("List-file niet toegestaan bij lijst bestanden")
            self.apptype, filelist = determine_mode_from_input(fnames)
        elif list_file:
            # self.apptype = 'multi'
            self.apptype, filelist = determine_mode_from_input(expand_list_file(list_file))
        else:
            self.apptype, filelist = 'open', []
        self.p = {'filelist': filelist}
        if self.apptype.startswith("single"):
            self.title += " - single file version"
        elif self.apptype == "multi":
            self.title += " - multi-file version"

        self.s = ""
        self.setup_options()
        self.extraopts = collections.defaultdict(lambda: False)
        self.apply_cmdline_options(kwargs)
        self.gui = AfriftGui(self)
        self.setup_screen()
        if self.extraopts['no_gui']:
            self.doe()
        else:
            self.gui.go()

    def get_filename_list(self, fn_orig, fnaam, flist):   # niet meer nodig
        """determine the files to search in
        """
        fnames = []
        if self.apptype == "":
            if fn_orig:
                fnames = [fnaam]
        elif self.apptype == "single":
            if not fn_orig:
                raise ValueError('Need filename for application type "single"')
            fnames = [fnaam]
        elif self.apptype == "multi":
            if fn_orig:
                if fnaam.is_dir():
                    fnames = [fnaam]
                    self.apptype = ''
                else:
                    with fnaam.open() as f_in:
                        for line in f_in:
                            line = line.strip()
                            if line.endswith(("\\", "/")):
                                line = line[:-1]
                            line = pathlib.Path(line).expanduser().resolve()
                            fnames.append(line)
                    if len(fnames) == 1:
                        self.apptype = '' if fnames[0].is_dir() else 'single'
            elif flist:
                fnames = [pathlib.Path(x) for x in flist]
            else:
                raise ValueError('Need filename or list of files for application type "multi"')
        else:
            raise ValueError('application type should be empty, "single" or "multi"')
        if self.apptype == "single":
            self.title += " - single file version"
        elif self.apptype == "multi":
            self.title += " - multi-file version"
        return fnames

    def setup_options(self):
        """update self.p with default and other options
        """
        for key in [x[0] for x in self.save_options_keys]:
            self.p[key] = False

        if self.p['filelist']:
            # if self.apptype == 'single':
            if self.apptype.startswith('single'):
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
            encfile.touch()
            test = 'latin-1\n'
            encfile.write_text(test)
        self.p['fallback_encoding'] = test.strip()

        edfile = BASE / 'open_result'
        try:
            test = edfile.read_text()
        except FileNotFoundError:
            edfile.touch()
            test = "program = 'SciTE'\nfile-option = '-open:{}'\nline-option = '-goto:{}'\n"
            edfile.write_text(test)
        self.editor_option = [x.split(' = ')[1].strip("'")
                              for x in test.strip().split('\n') if x]
        if self.editor_option[0].startswith('['):
            command_list = [x[1:-1] for x in self.editor_option[0][1:-1].split(', ')]
            self.editor_option[0] = command_list
        else:
            self.editor_option[0] = [self.editor_option[0]]

        self.always_replace = False
        self.maak_backups = True
        self.exit_when_ready = False

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
                    self.p[key] = opts.pop(key, '') or self.p[key]

    def apply_cmdline_options(self, cmdline_options):
        """lees settings opties vanuit invoer; override waar opgegeven
        """
        self.p['zoek'] = cmdline_options.pop('search', '')
        test = cmdline_options.pop('replace', None)
        if test is not None:
            self.p['vervang'] = test
            if test == '':
                self.always_replace = True
        self.p["extlist"] = cmdline_options.pop('extensions', '')
        if not self.p["extlist"]:
            self.p["extlist"] = []

        # saved_options alleen toepassen als use-saved is opgegeven?
        self.extraopts['use_saved'] = cmdline_options.pop('use_saved', False)
        if not self.extraopts['use_saved']:
            for key, argname in self.save_options_keys:
                self.p[key] = cmdline_options.pop(argname, self.p.get(key, False))

        for arg in ('regex', 'follow_symlinks', 'select_subdirs', 'select_files',
                    'dont_save', 'no_gui', 'output_file', 'full_path', 'as_csv', 'summarize'):
            if arg in self.outopts:
                self.outopts[arg] = cmdline_options.pop(arg, '') or self.outopts[arg]
            else:
                self.extraopts[arg] = cmdline_options.pop(arg, '')
        self.maak_backups = cmdline_options.pop('backup_originals', '')
        self.exit_when_ready = True   # altijd aan?

    def setup_screen(self):
        "set up display"
        self.gui.init_screen()
        self.vraag_zoek = self.gui.add_combobox_row('Zoek naar:', self.mru_items["zoek"],
                                                    initial=self.p.get("zoek", ''))
        self.vraag_regex = self.gui.add_checkbox_row("regular expression (Python format)",
                                                     self.extraopts['regex'])
        self.vraag_case = self.gui.add_checkbox_row("hoofd/kleine letters gelijk", self.p["case"])
        self.vraag_woord = self.gui.add_checkbox_row("hele woorden", self.p["woord"])

        self.vraag_verv = self.gui.add_combobox_row('Vervang door:', self.mru_items["verv"],
                                                    initial=self.p.get("verv", ''),
                                                    completer='case')
        self.vraag_leeg = self.gui.add_checkbox_row("lege vervangtekst = weghalen",
                                                    self.always_replace)
        self.vraag_backup = self.gui.add_checkbox_row("gewijzigd(e) bestand(en) backuppen",
                                                      self.maak_backups)
        self.vraag_exit = self.gui.add_checkbox_row("direct afsluiten na vervangen",
                                                    self.exit_when_ready)
        # breakpoint()
        if self.apptype == "open":
            initial = str(self.p['filelist'][0]) if self.p['filelist'] else ''
            self.vraag_dir = self.gui.add_combobox_row("In directory:", self.mru_items["dirs"],
                                                       initial=initial,
                                                       button=("&Zoek", self.gui.zoekdir),
                                                       completer='off', callback=self.update_defaults)
        elif self.apptype.startswith("single"):
            self.gui.add_label_to_grid("In file/directory:", new_row=True)
            self.gui.add_label_to_grid(str(self.p['filelist'][0]), left_align=True)
        else:  # if self.apptype == "multi":  - momenteel geen andere mogelijkheid
            self.gui.add_label_to_grid("In de volgende files/directories:", fullwidth=True)
            self.lb = self.gui.add_listbox_to_grid([str(x) for x in self.p['filelist']])
        if self.apptype != "single-file":
            txt = "van geselecteerde directories " if self.apptype == "multi" else ""
            self.vraag_subs = self.gui.add_checkbox_row(txt + "ook subdirectories doorzoeken",
                                                        self.p["subdirs"])
            self.vraag_links, self.vraag_diepte = self.gui.add_checkbox_row(
                "symlinks volgen - max. diepte (-1 is alles):",
                toggler=self.extraopts['follow_symlinks'], spinner=(5, -1))
            self.ask_skipdirs = self.gui.add_checkbox_row(
                "selecteer (sub)directories om over te slaan", self.extraopts['select_subdirs'])
            self.ask_skipfiles = self.gui.add_checkbox_row("selecteer bestanden om over te slaan",
                                                           self.extraopts['select_files'])
            self.vraag_types = self.gui.add_combobox_row("Alleen files van type:",
                                                         self.mru_items["types"],
                                                         initial=self.p.get("extlist", ''))
        self.vraag_context = self.gui.add_checkbox_row(
            "context tonen (waar mogelijk, anders overslaan)", self.p["context"])
        self.vraag_uitsluit = self.gui.add_checkbox_row("commentaren en docstrings negeren",
                                                        self.p["negeer"], indent=22)
        self.gui.add_buttons((('&Uitvoeren', self.doe), ('&Afsluiten', self.gui.einde)))
        self.gui.set_focus_to(self.vraag_zoek)

    def update_defaults(self, *args):
        """update settings using newly chosen location to search from
        """
        txt = self.gui.get_sender_value(*args)
        if os.path.exists(txt) and not txt.endswith(os.path.sep):
            self.read_from_ini(txt)
            self.gui.replace_combobox_items(self.vraag_zoek, self.mru_items["zoek"])
            self.gui.replace_combobox_items(self.vraag_verv, self.mru_items["verv"])
            self.gui.replace_combobox_items(self.vraag_types, self.mru_items["types"])
            self.gui.set_checkbox_value(self.vraag_case, self.p["case"])
            self.gui.set_checkbox_value(self.vraag_woord, self.p["woord"])
            self.gui.set_checkbox_value(self.vraag_subs, self.p["subdirs"])
            self.gui.set_checkbox_value(self.vraag_context, self.p["context"])
            self.gui.set_checkbox_value(self.vraag_uitsluit, self.p["negeer"])

    def doe(self, *args):
        """Zoekactie uitvoeren en resultaatscherm tonen"""
        if message := self.setup_parameters():
            self.gui.error(self.fouttitel, message)
            return

        self.gui.add_item_to_searchlist(self.vraag_zoek, self.p['zoek'])
        if not self.extraopts['dont_save']:
            loc = self.p.get('pad', '') or str(self.p['filelist'][0].parent)
            self.write_to_ini(os.path.abspath(loc))
        self.zoekvervang = Finder(**self.p)
        if self.zoekvervang.rpt:
            self.gui.error(self.fouttitel, self.zoekvervang.rpt[0])
            return
        ok = self.zoekvervang.setup_search()
        if not ok:
            self.gui.meld(self.resulttitel, f'{self.zoekvervang.rpt}\n{self.zoekvervang.errors}')
            return
        if not self.zoekvervang.filenames:
            self.gui.meld(self.resulttitel, "Geen bestanden om te doorzoeken")
            return

        # if (self.apptype != 'single' and self.p['filelist']
        #         and (len(self.p['filelist']) > 1 or self.p['filelist'][0].is_dir())):
        if self.apptype != 'single-file':
            canceled = self.select_search_exclusions_if_requested()
            if canceled:
                return

        self.gui.set_waitcursor(True)
        self.zoekvervang.go()  # do_action()  # search_python=self.p["context"])
        self.gui.set_waitcursor(False)

        self.show_results()

        if ((self.extraopts['no_gui'] and self.extraopts['output_file'])
                or (self.gui.get_checkbox_value(self.vraag_exit)
                    and self.p["vervang"] is not None)):
            self.gui.einde()

    def setup_parameters(self):
        """screen argument checks
        """
        if mld := self.checkzoek(self.gui.get_combobox_value(self.vraag_zoek)):
            return mld
        if mld := self.checkverv(self.gui.get_combobox_value(self.vraag_verv),
                                 self.gui.get_checkbox_value(self.vraag_leeg)):
            return mld
        if mld := self.checkattr(self.gui.get_checkbox_value(self.vraag_regex),
                                 self.gui.get_checkbox_value(self.vraag_case),
                                 self.gui.get_checkbox_value(self.vraag_woord)):
            return mld
        if self.apptype != 'single-file':
            if mld := self.checktype(self.gui.get_combobox_value(self.vraag_types)):
                return mld
        # if not self.apptype.startswith('single'):
        if self.apptype == 'open':
            if mld := self.checkpath(self.gui.get_combobox_value(self.vraag_dir)):
                return mld
        if self.apptype != 'single-file':
            subdirs = self.gui.get_checkbox_value(self.vraag_subs)
            links = self.gui.get_checkbox_value(self.vraag_links)
            depth = self.gui.get_spinbox_value(self.vraag_diepte)
            if subdirs:
                self.s += " en onderliggende directories"
            self.p["subdirs"] = subdirs
            self.p["follow_symlinks"] = links
            self.p["maxdepth"] = depth
        # elif self.apptype == "single" and self.p['filelist'][0].is_symlink():
        elif self.apptype == "single-file" and self.p['filelist'][0].is_symlink():
            self.p["follow_symlinks"] = True
        self.p["backup"] = self.gui.get_checkbox_value(self.vraag_backup)
        self.p["negeer"] = self.gui.get_checkbox_value(self.vraag_uitsluit)
        self.p["context"] = self.gui.get_checkbox_value(self.vraag_context)
        return ''

    def checkzoek(self, item):
        "controleer zoekargument"
        if not item:
            mld = "Kan niet zoeken zonder zoekargument"
        else:
            mld = ""
            with contextlib.suppress(ValueError):
                self.mru_items["zoek"].remove(item)
            self.mru_items["zoek"].insert(0, item)
            self.s += f"zoeken naar {item}"
            self.p["zoek"] = item
        return mld

    def checkverv(self, *items):
        "controleer vervanging"
        mld = ""
        self.p["vervang"] = None
        vervang, leeg = items
        if vervang:
            with contextlib.suppress(ValueError):
                self.mru_items["verv"].remove(vervang)
            self.mru_items["verv"].insert(0, vervang)
            self.s += f"\nen vervangen door {vervang}"
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
            self.s += f" ({', '.join(opts)})"
        return mld

    def checktype(self, item):
        "controleer speciale bestandstypen (extensies)"
        mld = ""
        if item:
            with contextlib.suppress(ValueError):
                self.mru_items["types"].remove(item)
            self.mru_items["types"].insert(0, item)
            self.s += f"\nin bestanden van type {item}"
            exts = item.split(",")
            self.p["extlist"] = [x.lstrip().strip() for x in exts]
        else:
            self.p["extlist"] = []
        return mld

    def checkpath(self, item):
        "controleer zoekpad"
        if not item:
            mld = "Ik wil wel graag weten in welke directory ik moet (beginnen met) zoeken"
        elif not pathlib.Path(item).exists():
            mld = "De opgegeven directory bestaat niet"
        else:
            mld = ""
            with contextlib.suppress(ValueError):
                self.mru_items["dirs"].remove(item)
            self.mru_items["dirs"].insert(0, item)
            self.p['filelist'] = [pathlib.Path(item)]
            self.s += f"\nin {item}"
        return mld

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
        # if self.apptype == 'single':
        if self.apptype == 'single-file':
            result = self.p['filelist'][0]
        elif self.apptype == 'multi':
            test = os.path.commonpath([str(x) for x in self.p['filelist']])
            if os.path.isfile(test):
                result = os.path.dirname(test) + os.sep
            else:
                result = test + os.sep
        else:
            result = str(self.p["filelist"][0]) + os.sep
        return result

    def select_search_exclusions_if_requested(self):
        """present dialogs to skip directories and/or files to search
        """
        skip_dirs = self.gui.get_checkbox_value(self.ask_skipdirs)
        skip_files = self.gui.get_checkbox_value(self.ask_skipfiles)
        go_on = skip_dirs or skip_files  # -> if not(skip_dirs or skip_files):
        canceled = False                 # ->     return False
        while go_on:  # -> while True
            # eerste ronde: toon directories
            if skip_dirs and self.zoekvervang.dirnames:
                self.names = sorted(self.zoekvervang.dirnames)

                result, names = SelectNames(self, files=False).show()
                if not result:
                    canceled = True
                    break

                self.remove_files_in_selected_dirs(names)
                if not skip_files:            # zijn deze twee überhaupt nodig?
                    go_on = False  # -> break
            # tweede ronde: toon de files die overblijven
            if skip_files:
                self.names = sorted(self.zoekvervang.filenames)  # , key=lambda x: str(x))
                result, names = SelectNames(self).show()
                if not result and not skip_dirs:
                    canceled = True
                    break
                if result:
                    self.zoekvervang.filenames = names
                    go_on = False  # -> break - is deze wel nodig?
        return canceled

    def remove_files_in_selected_dirs(self, dirnames):
        """remove files ithat do not need to be searched from the selection
        """
        fnames = self.zoekvervang.filenames[:]
        for entry in fnames:
            for name in dirnames:
                # if str(entry).startswith(name + '/'):
                if str(entry.parent) == name:
                    self.zoekvervang.filenames.remove(entry)
                    break

    def show_results(self):
        """present the result(s) or write to an output file
        """
        if len(self.zoekvervang.rpt) == 1:
            if f_out := self.extraopts['output_file']:
                with f_out:
                    print('No results', file=f_out)
            else:
                # mld = "Niks gevonden" if self.zoekvervang.ok else self.zoekvervang.rpt[0]
                self.gui.meld(self.resulttitel, 'No results')

        else:
            dlg = Results(self, self.determine_common())
            if f_out := self.extraopts['output_file']:
                with f_out:
                    for line in dlg.get_results():
                        print(line, file=f_out)
            else:
                dlg.show()


class SelectNames:
    """Tussenscherm om te verwerken files te kiezen

    deze class bevat methoden die onafhankelijk zijn van de gekozen GUI-toolkit
    """
    def __init__(self, parent, files=True):
        self.do_files = files
        self.parent = parent
        self.title = self.parent.title + " - file list"
        self.iconame = iconame
        if files:
            headingtext = "Selecteer de bestanden die je *niet* wilt verwerken"
            self.names = {str(x): x for x in self.parent.names}
        else:
            headingtext = "Selecteer de directories die je *niet* wilt verwerken"
            self.names = []
        self.gui = SelectNamesGui(parent, self)
        self.gui.setup_screen()
        line = self.gui.add_line()
        self.gui.add_text_to_line(line, headingtext)
        line = self.gui.add_line()
        self.sel_all = self.gui.add_checkbox_to_line(line, 'Select/Unselect All',
                                                     self.gui.select_all)
        self.flip_sel = self.gui.add_button_to_line(line, 'Invert selection',
                                                    self.gui.invert_selection)
        line = self.gui.add_line()
        self.checklist = self.gui.add_selectionlist(line, [str(x) for x in self.parent.names])
        line = self.gui.add_line()
        self.gui.add_buttons(line, [("&Terug", self.gui.cancel), ("&Klaar", self.gui.confirm)])

    def show(self):
        """show the dialog screen
        """
        return self.gui.go(), self.names


class CSVTextBuf:
    """Format the search results into columns before outputting
    """
    def __init__(self, apptype, toonpad):
        self.apptype = apptype
        self.toonpad = toonpad
        self.textbuf = io.StringIO()
        self.writer = csv.writer(self.textbuf, dialect='unix')
        self.header = [('Path/file' if toonpad else 'File'), 'Line', 'Context', 'Result']

    def write_line(self, result):
        "write the header if it hasn't been written yet, then write a line of results"
        loc, line = result[0].rsplit(' r. ', 1)
        result[:1] = [loc, line]
        if self.header and len(self.header) > len(result):
            self.header[2:] = self.header[3:]
        # if self.apptype == 'single' and not self.toonpad:
        if self.apptype == 'single-file' and not self.toonpad:
            result = result[1:]
            if self.header:
                self.header = self.header[1:]
        if self.header:
            self.writer.writerow(self.header)
            self.header = None
        self.writer.writerow(result)

    def get_contents_and_close(self):
        "make the buffer contents available and close the buffer"
        result = self.textbuf.getvalue().split("\n")
        self.textbuf.close()
        return result


class Results:
    """Show results on screen

    deze class bevat methoden die onafhankelijk zijn van de gekozen
    GUI-toolkit
    """

    def __init__(self, parent, common_path=''):
        self.parent = parent
        self.common = common_path
        self.show_context = self.parent.p["context"]
        self.results = []
        self.titel = 'Regel' if self.parent.apptype == "single-file" else 'File/Regel'
        self.iconame = iconame
        self.gui = ResultsGui(parent, self)

        if self.parent.p['vervang'] and self.parent.apptype == 'single-file':
            self.show_result_details = False
            aantal = self.parent.zoekvervang.rpt[1].split(None, 1)[1]
            label_txt = self.parent.zoekvervang.rpt[0]
            label_txt = label_txt.replace('vervangen', aantal + ' vervangen')
        else:
            self.show_result_details = True
            itemcount = len(self.parent.zoekvervang.rpt) - 1
            label_txt = f"{self.parent.zoekvervang.rpt[0]} ({itemcount} items)"
            if self.parent.apptype == "multi":
                label_txt += '\n' + common_path_txt.format(self.common.rstrip(os.sep))
        line = self.gui.add_line()
        self.hdr = self.gui.add_text_to_line(line, label_txt)
        self.gui.add_stretch_to_line(line)
        self.gui.add_buttons_to_line(line, (('Go to selected result', self.gui.to_result, True),))
        self.build_list()
        if self.show_result_details:
            line = self.gui.add_line()
            if self.show_context:
                headers = (self.titel, 'Context', 'Tekst')
            else:
                headers = ((self.titel, 'Tekst'))
            actions = (('Help', 'F1', self.help), ('&Goto Result', 'Ctrl+G', self.gui.to_result))
            self.lijst = self.gui.add_results_list(line, headers, actions, self.results)
        line = self.gui.add_line()
        self.gui.add_text_to_line(line, 'Action:')
        self.gui.add_buttons_to_line(line, (("&Klaar", self.gui.klaar, True),))  #  , start=True)
        if self.show_result_details:
            enable = bool(self.parent.p['vervang'])     # FIXME: is dit wel goed?
            self.gui.add_buttons_to_line(line, (("&Repeat Search", self.refresh, enable),
                                         ('&Zoek anders', self.zoek_anders, True),
                                         ('Vervang in &Selectie', self.vervang_in_sel, enable),
                                         ('Vervang &Alles', self.vervang_alles, enable)))
            self.gui.add_stretch_to_line(line)
            line = self.gui.add_line()
            self.gui.add_text_to_line(line, 'Output:')
            self.gui.add_buttons_to_line(line, (("Copy to &File", self.kopie, True),
                                                ("Copy to &Clipboard", self.to_clipboard, True)))
            self.cb_delim = self.gui.add_checkbox_to_line(line, "comma-delimited",
                                                          self.parent.outopts['as_csv'])
            self.cb_smrz = self.gui.add_checkbox_to_line(line, "summarized",
                                                         self.parent.outopts['summarize'])
            self.cb_path = self.gui.add_checkbox_to_line(line, "toon directorypad",
                                                         self.parent.outopts['full_path'])
            self.gui.add_stretch_to_line(line)
            if self.parent.apptype == 'single-file':
                self.gui.disable_widget(self.cb_path)
        self.gui.finalize_display()

    def build_list(self):
        "construct list of results"
        for ix, line in enumerate(self.parent.zoekvervang.rpt):
            if ix == 0:
                kop = line
            elif line != "":
                where, what = line.split(": ", 1)
                if self.parent.apptype == "single-file":
                    where = where.split("r. ", 1)[1] if "r. " in where else ""
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
        """show the screen
        """
        self.gui.go()

    def get_results(self):
        """format output
        """
        toonpad = self.gui.get_checkbox_value(self.cb_path)
        comma = self.gui.get_checkbox_value(self.cb_delim)
        summarize = self.gui.get_checkbox_value(self.cb_smrz)

        text = [f"{self.results[0]}"]
        if self.parent.apptype == "multi" and not toonpad:
            text.append(common_path_txt.format(self.common))
        text.append("")
        if comma:
            textbuf = CSVTextBuf(self.parent.apptype, toonpad)
        for item in self.results[1:]:
            result = list(item)
            if self.parent.apptype == 'single-file':
                result[0] = ' r. ' + result[0]
            if toonpad and (self.parent.apptype == 'multi' or comma):
                result[0] = self.common + result[0]
            if comma:
                textbuf.write_line(result)
            else:
                text.append(" ".join(result).strip())

        if comma:
            text += textbuf.get_contents_and_close()

        if summarize:
            context = 'py' if self.show_context else None
            fname = self.parent.p['filelist'][0]
            if self.parent.apptype == 'single-file':
                text = [f'{fname} {x}' if x else '' for x in text]
            text = reformat_result(text, context)
            if self.parent.apptype == 'single-file' and not toonpad:
                text = [x.replace(str(fname), '', 1).strip() for x in text]

        return text

    def refresh(self, *args, **kwargs):
        """repeat search and show new results
        """
        self.results = []
        self.gui.clear_contents()
        self.parent.zoekvervang.rpt = ["".join(self.parent.zoekvervang.specs)]
        self.parent.gui.set_waitcursor(True)
        self.parent.zoekvervang.go()
        self.parent.gui.set_waitcursor(False)
        if len(self.parent.zoekvervang.rpt) == len(['melding']):
            # self.gui.breekaf(self.messages['nope'], done=False)
            message = f"{self.parent.zoekvervang.rpt[0]}\nNiks gevonden"
            self.gui.meld(self.parent.resulttitel, message)
            return
        if (len(self.parent.zoekvervang.rpt) == len(['melding', 'header'])
                and self.parent.zoekvervang.p['wijzig']):
            count_txt = self.parent.zoekvervang.rpt.pop().split(': ')[-1]
        else:
            count_txt = f'{len(self.parent.zoekvervang.rpt) - 1} items'

        label_txt = ''
        replcount = kwargs.get('replace_count', '')
        if replcount:
            srch = self.parent.zoekvervang.p['zoek']
            repl = kwargs.get('replace_text', '')
            label_txt = f'`{srch}` with `{repl}` replaced {replcount} in lines\n'
        label_txt += f"{self.parent.zoekvervang.rpt[0]} ({count_txt})"
        if self.parent.apptype == "multi":
            label_txt += '\n' + common_path_txt.format(self.common)

        self.gui.set_header(self.hdr, label_txt)
        self.build_list()
        self.gui.populate_list(self.lijst, self.results)

    def check_option_combinations_ok(self):
        """onzinnige combinatie(s) uitsluiten
        """
        if all((self.gui.get_checkbox_value(self.cb_delim),
                self.gui.get_checkbox_value(self.cb_smrz))):
            self.gui.meld('ahem',
                          "Summarize to comma delimited is not a sensible option, request denied")
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
        ext = ('.csv', 'Comma delimited files') if self.gui.get_checkbox_value(self.cb_delim) else ('.txt', 'Text files')
        exts = (ext, ('.*', 'All files'))
        f_nam = f_nam.join(("files-containing-", ext[0]))
        savename = self.gui.get_savefile("Resultaat naar bestand kopiëren",
                                         str(self.parent.hier), f_nam, exts)
        if savename:
            self.remember_settings()
            with open(savename, "w") as f_out:
                for line in self.get_results():
                    f_out.write(line + "\n")

    def to_clipboard(self, *args):
        """callback for button 'Copy to clipboard'
        """
        if self.check_option_combinations_ok():
            self.remember_settings()
            self.gui.copy_to_clipboard('\n'.join(self.get_results()) + '\n')

    def remember_settings(self):
        "save options to configuration"
        self.parent.outopts['full_path'] = self.gui.get_checkbox_value(self.cb_path)
        self.parent.outopts['as_csv'] = self.gui.get_checkbox_value(self.cb_delim)
        self.parent.outopts['summarize'] = self.gui.get_checkbox_value(self.cb_smrz)
        self.parent.write_to_ini()

    def help(self, *args):
        """show instructions
        """
        self.gui.meld('info', "Select a line and doubleclick or press Ctrl-G"
                      " to open the indicated file\nat the indicated line"
                      " (not in single file mode)")

    def goto_result(self, row, col):
        """open the file containing the selected item
        """
        if self.parent.apptype == 'single-file':
            self.gui.meld('ahem', 'Not in single file mode')
            return
        selected = self.results[row + 1]
        target, line = selected[0].split(' r. ')
        target = self.common + target
        prog, fileopt, lineopt = self.parent.editor_option
        # subprocess.run([prog, fileopt.format(target), lineopt.format(line)], check=False)
        subprocess.run(prog + [fileopt.format(target)] + [lineopt.format(line)], check=False)

    def vervang_in_sel(self, *args):
        "achteraf vervangen in geselecteerde regels"
        # bepaal geselecteerde regels
        items = self.gui.get_selection()
        if not items:
            self.gui.meld(self.parent.resulttitel, 'Geen regels geselecteerd om in te vervangen')
            return
        lines_to_replace = [x.split(' r. ') for x in items]
        prompt = f"vervang `{self.parent.p['zoek']}` in geselecteerde regels door:"
        text, ok = self.gui.get_text_from_user(self.parent.resulttitel, prompt)
        if ok:
            replaced = self.parent.zoekvervang.replace_selected(text, lines_to_replace)
            # self.parent.zoekvervang.setup_search() -- is dit nodig als het niet wijzigt?
            self.refresh(replace_text=text, replace_count=replaced)

    def vervang_alles(self, *args):
        "achteraf vervangen in alle regels"
        prompt = f"vervang `{self.parent.p['zoek']}` in alle regels door:"
        text, ok = self.gui.get_text_from_user(self.parent.resulttitel, prompt)
        if ok:
            self.parent.zoekvervang.p['vervang'] = text
            self.parent.zoekvervang.p['wijzig'] = True
            self.parent.zoekvervang.setup_search()
            self.refresh()

    def zoek_anders(self, *args):
        "zoek naar iets anders in dezelfde selectie"
        origzoek = self.parent.zoekvervang.p['zoek']
        text, ok = self.gui.get_text_from_user(self.parent.resulttitel,
                                               'zoek in dezelfde selectie naar:')
        if ok:
            self.parent.zoekvervang.p['zoek'] = text
            self.parent.zoekvervang.setup_search()
            self.refresh()
            self.parent.zoekvervang.p['zoek'] = origzoek
            self.parent.zoekvervang.setup_search()


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


def determine_mode_from_input(fnames):
    """read the input filename(s) and build a search list, setting the appropriate application type
    """
    if len(fnames) == 1:
        fnpath = pathlib.Path(fnames[0]).expanduser().resolve()
        if not fnpath.exists():
            raise ValueError('File does not exist')
        if fnpath.is_dir():
            apptype = 'single-dir'
        else:
            apptype = 'single-file'
        fnames = [fnpath]
    else:
        fnames = [pathlib.Path(x) for x in fnames]
        apptype = 'multi'
    return apptype, fnames


def expand_list_file(fnaam):
    """read the file containing the filenames to search and build a search list
    """
    fnpath = pathlib.Path(fnaam).expanduser().resolve()
    if not fnpath.exists():
        raise ValueError('File does not exist')
    if fnpath.is_dir():
        raise ValueError('List file must not be a directory')
    fnames = []
    with fnpath.open() as f_in:
        for line in f_in:
            line = line.strip()
            if line.endswith(("\\", "/")):
                line = line[:-1]
            line = pathlib.Path(line).expanduser().absolute()
            fnames.append(line)
    return fnames
