# -*- coding: UTF-8 -*-
"""Uitvoeren van de find/replace actie

de uitvoering wordt gestuurd door in een dictionary verzamelde parameters"""

from __future__ import print_function
import os
import pathlib
import re
import shutil
import collections
import subprocess
contains_default = 'module level code'
special_chars = ('.', '^', '$', '*', '+', '?', '{', '}', '[', ']', '(', ')', '|', '\\')


def determine_split_none(words):
    """determine word number to split on for regular search
    argument is provided for compatibility with other variants
    """
    return 3


def determine_split_py(words):
    """determine word number to split on for python context sensitive search
    """
    if words[3] == 'class':
        end = 5
        if words[5] == 'method':
            end = 7
    elif words[3] == 'function':
        end = 5
    else:  # if words == 'module':
        end = 6
    return end


determine_split = {None: determine_split_none,  # dispatch table
                   "py": determine_split_py}


def format_result(lines, context_type=None):
    """reformat search results
    """
    start_splitting = False
    old_program_file = old_context = ''
    lines_out = []
    for line in lines:
        line = line.strip()
        if not start_splitting:
            if line:
                lines_out.append(line)
            else:
                start_splitting = True
            continue
        words = line.split()
        program_file = words[0]
        location = ' '.join(words[1:3])

        end = determine_split[context_type](words)
        context = ' '.join(words[3:end]) if end > 3 else ''

        split_on = words[end - 1]
        statement = line.split(split_on, 1)[1]
        source_changed = False
        if program_file != old_program_file:
            source_changed = True
            if old_program_file:
                lines_out.append('')
            old_program_file = program_file
            lines_out.append(program_file)
        if context and context != old_context or source_changed:
            old_context = context
            lines_out.append(context)
        lines_out.append(': '.join((location, statement)))
    return lines_out


def check_single_string(inp):
    """inspect single (doc)string
    """
    test = inp[0]
    while test in ('"', "'"):
        try:
            ix = inp.index(test, 1)
        except IndexError:
            return False
        inp = inp[ix + 1:].strip()
        if not inp:
            return True
        test = inp[0]
    return False


def determine_filetype(entry):
    """Try to discover what kind of file this is and return which context-sensitive search to use
    """
    if entry.suffix in ('.py', '.pyw'):
        return 'py'
    result = subprocess.run(['file', entry], stdout=subprocess.PIPE)
    if 'python' in str(result.stdout.lower()):
        return 'py'
    return ''


def read_input_file(file, fallback_encoding):
    """return contents of the specified file as a list or None if it can't be read
    """
    try:
        with file.open() as f_in:
            return f_in.readlines()
    except UnicodeDecodeError:
        try:
            with file.open("r", encoding=fallback_encoding) as f_in:
                return f_in.readlines()
        except UnicodeDecodeError:
            return None


def pyread(file, fallback_encoding='latin-1', negeer_docs=False):
    """context-aware search in Python files

    this routine procduces a list of contexts
    """
    def pop_construct(last_line):
        """if needed, add construct(s) to list
        """
        while in_construct and indentpos <= in_construct[-1][0]:
            construct = list(in_construct.pop())
            construct.append(last_line)
            constructs.append(in_construct + [construct])
    lines = read_input_file(file, fallback_encoding)
    if lines is None:
        return lines
    itemlist = []
    modlevel_start = 1
    constructs = []
    in_construct = []
    docstring = ''
    docstring_start = 0
    indentpos = prev_lineno = 0
    start_of_code = False
    for ix, line in enumerate(lines):
        if line.strip() == "":
            continue
        lineno = ix + 1
        test = line.lstrip()
        if test.startswith('#') and negeer_docs:
            itemlist.append(((lineno, 0), (lineno, -1), 'comment'))
            if not start_of_code:
                modlevel_start = lineno + 1
            continue
        elif test.startswith('#') and line.index(test) < indentpos:
            pass
        else:
            indentpos = line.index(test)
        if negeer_docs:
            if docstring and line.rstrip().endswith(docstring):
                docstring = ''
                itemlist.append(((docstring_start, indentpos), (lineno, -1), "docstring"))
                if not start_of_code:
                    modlevel_start = lineno + 1
                continue
            if test.startswith('"""') or test.startswith("'''"):
                docstring = test[:3]
                docstring_start = lineno
                if line.rstrip().endswith(docstring):
                    docstring = ''
                    itemlist.append(((docstring_start, indentpos), (lineno, -1), "docstring"))
                if not start_of_code:
                    modlevel_start = lineno + 1
                continue
            if test.startswith('"') or test.startswith("'"):
                if check_single_string(test.rstrip()):
                    itemlist.append(((lineno, indentpos), (lineno, -1), 'docstring'))
                    if not start_of_code:
                        modlevel_start = lineno + 1
                    continue
        if not start_of_code:
            start_of_code = True
            itemlist.append(((modlevel_start, 0), (len(lines), -1), contains_default))
        pop_construct(prev_lineno)
        if test.startswith('def ') or test.startswith('class '):
            words = test.split()
            construct = (indentpos, words[0], words[1].split(':')[0].split('(')[0], lineno)
            in_construct.append(construct)
        if '#' in test and negeer_docs:
            pos = test.index('#')
            itemlist.append(((lineno, pos), (lineno, -1), 'comment'))
        prev_lineno = lineno
    indentpos = 0
    pop_construct(prev_lineno - 1)
    for item in constructs:
        _, _, _, start, end = item[-1]
        construct = []
        for part in item:
            type_, name = part[1:3]
            if type_ == "def":
                if construct and construct[-2] == "class":
                    type_ = "method"
                else:
                    type_ = "function"
            construct.extend([type_, name])
        itemlist.append(((start, 0), (end, -1), " ".join(construct)))
    return sorted(itemlist)


class Finder():
    """interpreteren van de parameters en aansturen van de zoek/vervang routine
    """
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
            "backup": False,
            "follow_symlinks": False,
            "maxdepth": 5,
            "fallback_encoding": 'ascii',
            "context": False,
            "negeer": False, }
        for x in parms:
            if x in self.p:
                self.p[x] = parms[x]
            else:
                raise TypeError('Onbekende optie ' + x)
        ## print('On creating Finder instance:', self.p)
        self.ok = True
        self.errors = []
        self.rpt = []  # oorspronkelijk: verslag van wat er gebeurd is
        self.use_complex = True
        self.rgx, self.ignore = '', ''
        if not self.p['filelist'] and not self.p['pad']:
            self.rpt.append("Fout: geen lijst bestanden en geen directory opgegeven")
        elif self.p['filelist'] and self.p['pad']:
            self.rpt.append("Fout: lijst bestanden én directory opgegeven")
        elif not self.p['zoek']:
            self.rpt.append('Fout: geen zoekstring opgegeven')
        if self.rpt:
            self.ok = False
            return
        self.p['wijzig'] = True if self.p['vervang'] is not None else False
        self.extlist_upper = []
        for x in self.p['extlist']:
            if not x.startswith("."):
                x = "." + x
            self.extlist_upper.append(x.upper())
        # self.setup_search()

    def setup_search(self):
        """instellen variabelen t.b.v. zoekactie en output
        """
        # moet hier nog iets mee doen m.h.o.o. woorddelen of niet
        if self.p['wijzig'] or self.p['regexp']:
            self.use_complex = False
            self.rgx = self.build_regexp_simple()
        else:
            self.rgx, self.ignore = self.build_regexes()
        specs = ["Gezocht naar '{}'".format(self.p['zoek'])]
        if self.p['wijzig']:
            specs.append(" en dit vervangen door '{}'".format(self.p['vervang']))
        if self.p['extlist']:
            if len(self.p['extlist']) > 1:
                typs = " en ".join((", ".join(self.p['extlist'][:-1]),
                                    self.p['extlist'][-1]))
            else:
                typs = self.p['extlist'][0]
            specs.append(" in bestanden van type {}".format(typs))
        self.filenames = []
        self.dirnames = set()
        if self.p['pad']:
            specs.append(" in {}".format(self.p['pad']))
            self.subdirs(self.p['pad'])
        else:
            if len(self.p['filelist']) == 1:
                specs.append(" in {}".format(self.p['filelist'][0]))
            else:
                specs.append(" in opgegeven bestanden/directories")
            for entry in self.p['filelist']:
                ## self.subdirs(entry, is_list=False)
                mld = self.subdirs(entry)
                if mld:
                    self.errors.append(mld)
        if self.p['subdirs']:
            specs.append(" en evt. onderliggende directories")
        self.rpt.insert(0, "".join(specs))
        self.specs = specs
        if self.errors:
            self.rpt.append("Zoekactie niet mogelijk")
            self.ok = False

    ## def subdirs(self, pad, is_list=True, level=0):
    def subdirs(self, pad, level=0):
        """recursieve routine voor zoek/vervang in subdirectories
        samenstellen lijst met te verwerken bestanden

        als is_list = False dan wordt van de doorgegeven naam eerst een list
        gemaakt. Daardoor hebben we altijd een iterable met directorynamen.
        Deze parameter lijkt een probleem te veroorzaken als in multi mode een
        lijst wordt opgegeven (via self.p['filelist']) met directorynamen erin
        (misschien is dat recent veranderd) daarom is deze verwijderd en is de
        except NotADirectoryError toegevoegd
        """
        path = pad
        try:
            test = path.name
        except AttributeError:
            path = pathlib.Path(pad)
        else:
            pad = str(path)
        if path.is_dir():
            self.dirnames.add(pad)

        if self.p["maxdepth"] != -1:
            level += 1
            if level > self.p["maxdepth"]:
                return ''
        ## if is_list:
        try:
            _list = (fname for fname in os.scandir(pad))
        except NotADirectoryError:
            _list = [path]
        except PermissionError:
            _list = []
        except FileNotFoundError:
            return 'File not found: {}'.format(path.resolve())
        ## else:
            ## _list = (pad,)
        for entry in _list:
            if entry.is_dir():
                if self.p['subdirs']:
                    self.subdirs(entry.path, level=level)
            elif entry.is_symlink() and not self.p['follow_symlinks']:
                pass
            else:
                try:
                    ext = entry.suffix
                except AttributeError:
                    entry = pathlib.Path(entry.path)
                    ext = entry.suffix
                if self.p['extlist'] == [] or ext.upper() in self.extlist_upper:
                    self.filenames.append(entry)
        return ''

    def build_regexp_simple(self):
        """build the search regexp(s)
        this original version returns one compiled expression
        """
        zoek = ''
        for char in self.p['zoek']:
            if not self.p['regexp']:
                if char in special_chars:
                    zoek += "\\"
            zoek += char
        flags = re.MULTILINE
        if not self.p['case']:
            flags |= re.IGNORECASE
        return re.compile(str(zoek), flags)

    def build_regexes(self):
        """build the search regexp(s)
        this version makes a complex search possible by looking for special
        separators

        returns a list of re's to look for and a re of strings to ignore"""
        def escape(data):   # only for strings
            """escape special characters when they are not to be interpreted
            """
            zoek = ''
            for char in data:
                if char in special_chars:
                    zoek += "\\"
                zoek += char
            return zoek

        negeer = ''
        flags = re.MULTILINE
        if not self.p['case']:
            flags |= re.IGNORECASE
        if self.p['regexp'] or self.p['wijzig']:  # in these cases: always take literally
            zoek = [re.compile(escape(self.p['zoek']), flags)]
        else:
            zoek_naar, zoek_ook, zoek_niet = self.parse_zoek()
            zoek = [re.compile('|'.join([escape(x) for x in zoek_naar]), flags)]
            zoek += [re.compile(escape(x), flags) for x in zoek_ook]
            if zoek_niet:
                negeer = re.compile('|'.join([escape(x) for x in zoek_niet]), flags)
        return zoek, negeer

    def parse_zoek(self):
        """
            levert drie lists op:
            - een lijst met frasen waarvan er tenminste één moet voorkomen
            - een lijst met frasen die daarnaast ook moeten voorkomen
            - een lijst met frasen die niet mag voorkomen
        """
        def add_to_matches():
            """add phrase to the correct phrase list
            """
            nonlocal zoekitem, also_required, forbidden
            ## print('add_to_matches called with zoekitem', zoekitem, also_required)
            zoekitem = zoekitem.strip()
            if not zoekitem:
                return
            if also_required:
                required_matches.append(zoekitem)
            elif forbidden:
                forbidden_matches.append(zoekitem)
            else:
                possible_matches.append(zoekitem)
            zoekitem = ''
            also_required = forbidden = False
        in_quotes = also_required = forbidden = False
        zoekitem = ''
        possible_matches = []
        required_matches = []
        forbidden_matches = []
        for char in self.p['zoek']:
            if char == '"':
                if in_quotes:
                    add_to_matches()
                in_quotes = not in_quotes
            elif char == ',' and not in_quotes:
                add_to_matches()
            elif char == '+' and not in_quotes:
                add_to_matches()
                also_required = True
            elif char == '-' and not in_quotes:
                add_to_matches()
                forbidden = True
            else:
                zoekitem += char
        add_to_matches()
        return possible_matches, required_matches, forbidden_matches

    def go(self):  # do_action(self)  # , search_python=False):
        """start the search
        """
        for entry in self.filenames:
            self.zoek(entry)
        if not self.p['context']:  # search_python:
            return
        results, self.rpt = self.rpt, []
        locations = {}
        for entry in self.filenames:
            ftype = determine_filetype(entry)
            if ftype == 'py':
                locations[str(entry)] = pyread(entry, self.p['fallback_encoding'], self.p['negeer'])
            else:
                locations[str(entry)] = []
        for item in results:
            test = item.split(' r. ', 1)
            if len(test) == 1:
                self.rpt.append(item)
                continue
            best = test[0]
            if not locations[best]:
                continue
            test = test[1].split(': ', 1)
            if len(test) == 1:
                self.rpt.append(item)
                continue
            lineno, text = test
            contains = contains_default
            for loc in locations[best]:
                lineno = int(lineno)
                if loc[0][0] < lineno <= loc[1][0]:
                    old_contains = contains
                    contains = loc[2]
                    if contains == 'comment':
                        where = text.upper().find(self.p['zoek'].upper())
                        if where < loc[0][1]:
                            contains = old_contains
                if loc[0][0] > lineno:
                    break
            if self.p['negeer'] and contains in ('comment', 'docstring'):
                continue
            if contains != 'ignore':
                self.rpt.append('{} r. {} ({}): {}'.format(best, lineno, contains, text))

    def zoek(self, best):
        "het daadwerkelijk uitvoeren van de zoek/vervang actie op een bepaald bestand"
        pos, lines, regels = 0, [], []
        msg = ""
        try_again = False
        with best.open("r") as f_in:
            try:
                for x in f_in:
                    lines.append(pos)
                    x = x.rstrip() + os.linesep
                    regels.append(x)
                    pos += len(x)
            except UnicodeDecodeError:
                try_again = True
        if try_again:
            pos, lines, regels = 0, [], []
            with best.open("r", encoding=self.p['fallback_encoding']) as f_in:
                try:
                    for x in f_in:
                        lines.append(pos)
                        x = x.rstrip() + os.linesep
                        regels.append(x)
                        pos += len(x)
                except UnicodeDecodeError:
                    msg = best + ": overgeslagen, waarschijnlijk geen tekstbestand"
        if msg:
            self.rpt.append(msg)
            return
        lines.append(pos)
        data = "".join(regels)
        found = False
        from_line = 0
        last_in_line = 0
        if self.use_complex:
            result_list = self.complex_search(data, lines)
            for lineno in result_list:
                found = True
                self.rpt.append("{} r. {}: {}".format(
                    best, lineno, regels[lineno - 1].rstrip()))
            return

        # gebruik de oude manier van zoeken bij vervangen of bij regexp zoekstring
        result_list = self.rgx.finditer(data)
        for vind in result_list:
            found = True
            ## print(vind, vind.span(), sep = " ")
            for lineno, linestart in enumerate(lines[from_line:]):
                ## print(from_line,lineno,linestart)
                if vind.start() < linestart:
                    if not self.p['wijzig']:
                        in_line = lineno + from_line
                        if in_line != last_in_line:
                            self.rpt.append("{0} r. {1}: {2}".format(
                                best, in_line, regels[in_line - 1].rstrip()))
                        last_in_line = in_line
                    from_line = lineno
                    break
        if found and self.p['wijzig']:
            ndata, aant = self.rgx.subn(self.p["vervang"], data)
            best_s = str(best)
            self.rpt.append("%s: %s keer" % (best_s, aant))
            self.backup_if_needed(best_s)
            with best.open("w") as f_out:
                f_out.write(ndata)

    def complex_search(self, data, lines):
        """extended serch using phrases we want to find and phrases we don't want to find
        """
        # maak een lijst van alle locaties waar een string gevonden is
        # (plus de index van de  regexp die er bij hoort)
        found_in_lines = []
        for ix, rgx in enumerate(self.rgx):
            new_lines = [(x.start(), ix) for x in rgx.finditer(data)]
            found_in_lines += new_lines

        # vul de lijst aan met alle locaties waar gevonden is wat we niet willen vinden
        # (gemarkeerd met index -1)
        if self.ignore:
            donotwant = [(x.start(), -1) for x in self.ignore.finditer(data)]
            found_in_lines += donotwant

        # loop de lijst langs om hiervan een dictionary te maken op regelnummer
        # met alle regexp indexen waar deze bij gevonden is
        # zodat we kunnen zien welke we wel en niet willen hebben
        lines_found = collections.defaultdict(set)
        from_line = 0  # houdt bij vanaf welke regel het zin heeft om de inhoud te controleren
        for itemstart, number in sorted(found_in_lines):
            for lineno, linestart in enumerate(lines[from_line:]):
                if itemstart < linestart:
                    in_line = lineno + from_line    # bereken het actuele regelnummer
                    from_line = lineno
                    break
            lines_found[in_line].add(number)

        # uitfilteren welke regel niet in alle zoekacties voorkomt of juist weggelaten met worden
        all_searches = set(range(len(self.rgx)))
        lines_left_over = []
        for line, values in lines_found.items():
            if -1 in values:
                continue
            if values == all_searches:
                lines_left_over.append(line)
        lines_left_over.sort()
        return lines_left_over

    def replace_selected(self, text, lines_to_replace):
        "achteraf vervangen in geselecteerde regels"
        replaced = 0
        single_mode = len(lines_to_replace[0]) == 1
        file_to_replace = ''
        for line in sorted(lines_to_replace):
            if single_mode:
                filename, lineno = str(self.p['filelist'][0]), line[0]
            else:
                filename, lineno = line
            lineno = int(lineno) - 1
            if filename != file_to_replace:
                if file_to_replace:
                    self.backup_if_needed(file_to_replace)
                    with open(file_to_replace, 'w') as out:
                        out.writelines(lines)
                file_to_replace = filename
                with open(file_to_replace) as in_:
                    lines = in_.readlines()
            oldline = lines[lineno]
            lines[lineno] = lines[lineno].replace(self.p['zoek'], text)
            if lines[lineno] != oldline:
                replaced += 1
        self.backup_if_needed(file_to_replace)
        with open(file_to_replace, 'w') as out:
            out.writelines(lines)
        return replaced

    def backup_if_needed(self, fname):
        "make backup if required"
        if self.p['backup']:
            bestnw = fname + ".bak"
            shutil.copyfile(fname, bestnw)
