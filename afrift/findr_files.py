"""Uitvoeren van de find/replace actie

de uitvoering wordt gestuurd door in een dictionary verzamelde parameters"""

import os
import pathlib
import re
import shutil
import collections
import subprocess
contains_default = 'module level code'
special_chars = ('.', '^', '$', '*', '+', '?', '{', '}', '[', ']', '(', ')', '|', '\\')


def determine_split(content_type, words):
    """determine word number to split on idepending on content type and content
    regular search: always 3
    python context: different for definitions of class, function or method
    """
    if content_type == "py":
        if words[3] == 'class':
            end = 5
            if words[5] == 'method':
                end = 7
        elif words[3] == 'function':
            end = 5
        else:  # if words == 'module':
            end = 6
        return end
    # if content type is None
    return 3


def reformat_result(lines, context_type=None):
    """format search results for showing as "summarized"

    the lines before the first blank line do not take part in the "summarizing"
    """
    old_source_file = old_context = ''
    lines_out = []
    start_splitting = False
    for line in lines:
        line = line.strip()
        if not start_splitting:
            if line:
                lines_out.append(line)
            else:
                start_splitting = True
            continue
        words = line.split()
        source_file = words[0]
        location = ' '.join(words[1:3])

        end = determine_split(context_type, words)
        context = ' '.join(words[3:end]) if end > 3 else ''

        split_on = words[end - 1]
        statement = line.split(split_on, 1)[1]
        source_changed = False
        if source_file != old_source_file:
            source_changed = True
            if old_source_file:
                lines_out.append('')
            old_source_file = source_file
            lines_out.append(source_file)
        if context and context != old_context or source_changed:
            old_context = context
            lines_out.append(context)
        lines_out.append(f'{location}: {statement}')
    return lines_out


def is_single_line_docstring(inp):
    """return True if input is a valid single-line docstring (with correct delimiters)
    """
    test = inp[0]
    while test in ('"', "'"):
        try:
            ix = inp.index(test, 1)
        # het is een syntax error als een single-quote niet wordt afgesloten op dezelfde regel
        # dus hoef ik hier wel naar te kijken?
        # except IndexError:
        except ValueError:
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
    result = subprocess.run(['file', entry], stdout=subprocess.PIPE, check=False)
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
    docstring_delim = ''
    indentpos = prev_lineno = 0
    start_of_code = False
    for ix, line in enumerate(lines):
        if line.strip() == "":
            continue
        lineno = ix + 1
        code = line.lstrip()
        if code.startswith('#') and negeer_docs:
            itemlist.append(((lineno, 0), (lineno, -1), 'comment'))
            if not start_of_code:
                modlevel_start = lineno + 1
            continue
        if code.startswith('#') and line.index(code) < indentpos:
            pass
        else:
            indentpos = line.index(code)
        if negeer_docs:
            if docstring_delim and line.rstrip().endswith(docstring_delim):
                # dit mist de situatie dat er een commentaar volgt na de docstring
                docstring_delim = ''
                # doctring_start is eerder ingesteld
                itemlist.append(((docstring_start, indentpos), (lineno, -1), "docstring"))
                if not start_of_code:
                    modlevel_start = lineno + 1
                continue
            if code.startswith(('"""', "'''")):
                docstring_delim = code[:3]
                docstring_start = lineno
                if line.rstrip().endswith(docstring):
                    docstring = ''
                    itemlist.append(((docstring_start, indentpos), (lineno, -1), "docstring"))
                if not start_of_code:
                    modlevel_start = lineno + 1
                continue
            # het is een syntax error als een single-quote niet wordt afgesloten op dezelfde regel
            # dus is de extra controle wel nodig?
            if code.startswith(('"', "'")) and is_single_line_docstring(code.rstrip()):
                itemlist.append(((lineno, indentpos), (lineno, -1), 'docstring'))
                if not start_of_code:
                    modlevel_start = lineno + 1
                continue
        if not start_of_code:
            start_of_code = True
            itemlist.append(((modlevel_start, 0), (len(lines), -1), contains_default))
        pop_construct(prev_lineno)
        if code.startswith(('def ', 'class ')):
            words = code.split()
            construct = (indentpos, words[0], words[1].split(':')[0].split('(')[0], lineno)
            in_construct.append(construct)
        if '#' in code and negeer_docs:
            pos = code.index('#')
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
                type_ = "method" if construct and construct[-2] == "class" else "function"
            construct.extend([type_, name])
        itemlist.append(((start, 0), (end, -1), " ".join(construct)))
    return sorted(itemlist)


def rgxescape(data):   # only for strings
    """escape special characters in regexes when they are not to be interpreted
    """
    zoek = ''
    for char in data:
        if char in special_chars:
            zoek += "\\"
        zoek += char
    return zoek


class Finder:
    """interpreteren van de parameters en aansturen van de zoek/vervang routine
    """
    def __init__(self, **parms):
        self.p = {
            'zoek': '',
            'vervang': None,
            # 'pad': '',
            'filelist': [],
            'extlist': [],
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
        for name, value in parms.items():
            if name in self.p:
                self.p[name] = value
            else:
                raise TypeError('Onbekende optie ' + name)
        # self.ok = True
        self.errors = []
        self.rpt = []
        self.use_complex = True
        self.rgx, self.ignore = '', ''
        if not self.p['zoek']:
            raise ValueError('Geen zoekstring opgegeven')
        if not self.p['filelist']:
            raise ValueError('Geen zoeklocatie opgegeven')
        self.p['wijzig'] = self.p['vervang'] is not None
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
        ok = True
        if self.p['wijzig'] or self.p['regexp']:
            self.use_complex = False
            self.rgx = self.build_regexp_simple()
        else:
            self.rgx, self.ignore = self.build_regexes()
        specs = [f"Gezocht naar '{self.p['zoek']}'"]
        if self.p['wijzig']:
            specs.append(f" en dit vervangen door '{self.p['vervang']}'")
        if self.p['extlist']:
            if len(self.p['extlist']) > 1:
                types = " en ".join((", ".join(self.p['extlist'][:-1]), self.p['extlist'][-1]))
            else:
                types = self.p['extlist'][0]
            specs.append(f" in bestanden van type {types}")
        self.filenames = []
        self.dirnames = set()
        # if self.p['pad']:
        #     specs.append(f" in {self.p['pad']}")
        #     self.subdirs(self.p['pad'])
        # else:
        if len(self.p['filelist']) == 1:
            specs.append(f" in {self.p['filelist'][0]}")
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
            ok = False
        return ok

    ## def subdirs(self, pad, is_list=True, level=0):
    def subdirs(self, pad, level=0):
        """recursieve routine voor zoek/vervang in subdirectories

        samenstellen lijst met te verwerken bestanden
        """
        path = pad
        # try:
        #     test = path.name
        # except AttributeError:
        if not hasattr(path, 'name'):
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
            return f'File not found: {path.resolve()}'
        ## else:
            ## _list = (pad,)
        for entry in _list:
            if entry.is_symlink() and not self.p['follow_symlinks']:
                continue
            if entry.is_file():
                try:
                    ext = entry.suffix
                except AttributeError:
                    entry = pathlib.Path(entry.path)
                    ext = entry.suffix
                if self.p['extlist'] == [] or ext.upper() in self.extlist_upper:
                    self.filenames.append(entry)
            elif self.p['subdirs']:
                self.subdirs(entry.path, level=level)
        return ''

    def build_regexp_simple(self):
        """build the search regexp(s)
        this original version returns one compiled expression
        """
        zoek = ''
        for char in self.p['zoek']:
            if not self.p['regexp'] and char in special_chars:
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

        returns a list of re's to look for and a re of strings to Iignore"""

        negeer = ''
        flags = re.MULTILINE
        if not self.p['case']:
            flags |= re.IGNORECASE
        if self.use_complex:
            zoek_naar, zoek_ook, zoek_niet = self.parse_zoekstring()
            zoek = [re.compile('|'.join([rgxescape(x) for x in zoek_naar]), flags)]
            zoek += [re.compile(rgxescape(x), flags) for x in zoek_ook]
            if zoek_niet:
                negeer = re.compile('|'.join([rgxescape(x) for x in zoek_niet]), flags)
        else:
            # self.p['regexp'] or self.p['wijzig']:  # in these cases: always take literally
            zoek = [re.compile(rgxescape(self.p['zoek']), flags)]
        return zoek, negeer

    def parse_zoekstring(self):
        """
        Analyseer zoekstring met het oog op speciale zoekacties waarbij
        - zoekstrings omgeven worden met "
        - een , aangeeft dat de volgende string ook voor mag komen
        - een + aangeeft dat een volgende string ook voor MOET komen
        - een - aangeeft dat een volgende string NIET voor mag komen

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
        for char in self.p['zoek'].replace("'", '"'):
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

    def go(self):
        """start the search
        """
        for entry in self.filenames:
            self.zoek(entry)
        if self.p['context']:
            self.add_context_to_search_results()

    def zoek(self, best):
        "daadwerkelijk uitvoeren van de zoek/vervang actie op een bepaald bestand"
        lines = read_input_file(best, self.p['fallback_encoding'])
        if lines is None:
            self.rpt.append(f"{best}: overgeslagen, waarschijnlijk geen tekstbestand")
            return
        pos, linestarts, linedata = 0, [], []
        for line in lines:
            linestarts.append(pos)
            linedata.append(line.rstrip() + os.linesep)
            pos += len(line)
        linestarts.append(pos)
        if self.use_complex:
            result_list = self.complex_search(lines, linestarts)
            for lineno in result_list:
                self.rpt.append(f"{best} r. {lineno}: {lines[lineno - 1].rstrip()}")
        else:
            # gebruik de oude manier van zoeken bij vervangen of bij regexp zoekstring
            found = self.old_rgx_search(lines, linestarts, best)
            if found and self.p['wijzig']:
                self.replace_and_report(lines, best)

    def add_context_to_search_results(self):
        """determine locations and add into search results
        """
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
            contains = self.determine_context_from_locations(lineno, text, locations[best])
            if self.p['negeer'] and contains in ('comment', 'docstring'):
                continue
            if contains != 'ignore':
                self.rpt.append(f'{best} r. {lineno} ({contains}): {text}')

    def determine_context_from_locations(self, lineno, text, locations):
        """determine which "location" to add into search result
        """
        contains = contains_default
        for loc in locations:
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
        return contains

    def complex_search(self, lines, linestarts):
        """extended search using phrases we want to find and phrases we don't want to find
        """
        data = "".join(lines)
        # maak een lijst van alle locaties waar een string gevonden is
        # (plus de index van de  regexp die er bij hoort)
        found_in_lines = []
        for ix, rgx in enumerate(self.rgx):
            new_lines = [(x.start(), ix) for x in rgx.finditer(data)]
            found_in_lines += new_lines
        print('found_in_lines:', found_in_lines)

        # vul de lijst aan met alle locaties waar gevonden is wat we niet willen vinden
        # (gemarkeerd met index -1)
        if self.ignore:
            donotwant = [(x.start(), -1) for x in self.ignore.finditer(data)]
            found_in_lines += donotwant
        print('found_in_lines:', found_in_lines)

        # loop de lijst langs om hiervan een dictionary te maken op regelnummer
        # met alle regexp indexen waar deze bij gevonden is
        # zodat we kunnen zien welke we wel en niet willen hebben
        lines_found = collections.defaultdict(set)
        from_line = 0  # houdt bij vanaf welke regel het zin heeft om de inhoud te controleren
        for itemstart, number in sorted(found_in_lines):
            print('itemstart, number:', itemstart, number)
            for ix, linestart in enumerate(linestarts[from_line:]):
                print('ix, linestart:', ix, linestart)
                if itemstart < linestart:
                    in_line = ix + from_line    # bereken het actuele regelnummer
                    print('itemstart ligt vóór linestart => gevonden in regel', in_line)
                    from_line = ix
                    break
            lines_found[in_line].add(number)
        print('lines_found:', lines_found)

        # uitfilteren welke regel niet in alle zoekacties voorkomt of juist weggelaten met worden
        all_searches = set(range(len(self.rgx)))
        print('all_searches:', all_searches)
        lines_left_over = []
        for in_line, searches in lines_found.items():
            print('in_line, values:', in_line, searches)
            if -1 in searches:
                continue
            if searches == all_searches:
                lines_left_over.append(in_line)
            else:
                print('not all searches satisfied')
        lines_left_over.sort()
        return lines_left_over

    def old_rgx_search(self, lines, linestarts, best):
        """search via regex and format results for output
        """
        found = False
        from_line = 0
        last_in_line = 0
        result_list = self.rgx.finditer("".join(lines))
        for vind in result_list:
            found = True
            for lineno, linestart in enumerate(linestarts[from_line:]):
                if vind.start() < linestart:
                    if not self.p['wijzig']:
                        in_line = lineno + from_line
                        if in_line != last_in_line:
                            self.rpt.append(f"{best} r. {in_line}: {lines[in_line - 1].rstrip()}")
                        last_in_line = in_line
                    from_line = lineno
                    break
        return found

    def replace_and_report(self, lines, best):
        """replace via regex
        """
        ndata, aant = self.rgx.subn(self.p["vervang"], "".join(lines))
        best_s = str(best)
        self.rpt.append(f"{best_s}: {aant} keer")
        self.backup_if_needed(best_s)
        with best.open("w") as f_out:
            f_out.write(ndata)

    def replace_selected(self, text, lines_to_replace):
        "achteraf vervangen in geselecteerde regels"
        def determine_filename_lineno(line):
            if single_mode:
                filename, lineno = str(self.p['filelist'][0]), line[0]
            else:
                filename, lineno = line
            lineno = int(lineno) - 1
            return filename, lineno
        def write_replacement(file_to_replace, lines):
            "write back modifications"
            if file_to_replace:
                self.backup_if_needed(file_to_replace)
                with open(file_to_replace, 'w') as out:
                    out.writelines(lines)
        replaced = 0
        single_mode = len(lines_to_replace[0]) == 1
        file_to_replace, lines = '', []
        for line in sorted(lines_to_replace):
            filename, lineno = determine_filename_lineno(line)
            if filename != file_to_replace:
                write_replacement(file_to_replace, lines)
                file_to_replace = filename
                with open(file_to_replace) as in_:
                    lines = in_.readlines()
            oldline = lines[lineno]
            lines[lineno] = lines[lineno].replace(self.p['zoek'], text)
            if lines[lineno] != oldline:
                replaced += 1
        write_replacement(file_to_replace, lines)
        return replaced

    def backup_if_needed(self, fname):
        "make backup if required"
        if self.p['backup']:
            bestnw = fname + ".bak"
            shutil.copyfile(fname, bestnw)
