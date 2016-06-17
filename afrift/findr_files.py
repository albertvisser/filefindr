# -*- coding: UTF-8 -*-
"""Uitvoeren van de find/replace actie

de uitvoering wordt gestuurd door in een dictionary verzamelde parameters"""

from __future__ import print_function
import sys
import os
import re
import shutil
import collections
contains_default = 'module level code'

def pyread(fname):
    with open(fname) as f_in:
        lines = f_in.readlines()
    constructs = []
    in_construct = []
    indentpos = 0
    for ix, line in enumerate(lines):
        if line.strip() == "":
            continue
        lineno = ix + 1
        test = line.lstrip()
        indentpos = line.index(test)
        while in_construct and indentpos <= in_construct[-1][0]:
            construct = list(in_construct.pop())
            construct.append(prev_lineno)
            constructs.append(in_construct + [construct])
        if test.startswith('def ') or test.startswith('class '):
            words = test.split()
            construct = (indentpos, words[0],
                words[1].split(':')[0].split('(')[0], lineno)
            in_construct.append(construct)
        prev_lineno = lineno
    indentpos = 0
    while in_construct and indentpos <= in_construct[-1][0]:
        construct = list(in_construct.pop())
        construct.append(prev_lineno)
        constructs.append(in_construct + [construct])
    itemlist = [(1, len(lines), contains_default)]
    for item in constructs:
        _, _, _, start, end = item[-1]
        construct = []
        in_class = in_method = False
        for part in item:
            type_, name = part[1:3]
            if type_ == "def":
                if construct and construct[-2] == "class":
                    type_ = "method"
                else:
                    type_ = "function"
            construct.extend([type_, name])
        itemlist.append((start, end, " ".join(construct)))
    return sorted(itemlist)

class Finder(object):
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
        self.use_complex = True
        self.re, self.ignore = '', ''
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
            if self.p['wijzig'] or self.p['regexp']:
                self.use_complex = False
                self.re = self.build_regexp_simple()
            else:
                self.re, self.ignore = self.build_regexes()
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
            self.filenames = []
            self.dirnames = set()
            if self.p['pad']:
                specs.append(" in {0}".format(self.p['pad']))
                self.subdirs(self.p['pad'])
            else:
                if len(self.p['filelist']) == 1:
                    specs.append(" in {0}".format(self.p['filelist'][0]))
                else:
                    specs.append(" in opgegeven bestanden/directories")
                for entry in self.p['filelist']:
                    self.subdirs(entry, is_list=False)
                    ## if os.path.isdir(entry):
                        ## self.subdirs(entry)
                    ## elif os.path.islink(entry) and not self.p['follow_symlinks']:
                        ## pass
                    ## else:
                        ## d, ext = os.path.splitext(entry)
                        ## if ext.upper() in self.extlistUpper or not self.p['extlist']:
                            ## self.zoek(entry)
                    #~ self.zoek(entry)
            if self.p['subdirs']:
                specs.append(" en onderliggende directories")
            self.rpt.insert(0, "".join(specs))
            self.specs = specs
        ## self.rpt.append("")

    def subdirs(self, pad, is_list=True, level=0):
        """recursieve routine voor zoek/vervang in subdirectories
        samenstellen lijst met te verwerken bestanden

        als is_list = False dan wordt van de doorgegeven naam eerst een list
        gemaakt. Daardoor hebben we altijd een iterable met directorynamen.
        """
        if os.path.isdir(pad):
            self.dirnames.add(pad)
        if self.p["maxdepth"] != -1:
            level += 1
            if level > self.p["maxdepth"]:
                return
        if is_list:
            try:
                _list = (os.path.join(pad, fname) for fname in os.listdir(pad))
            except PermissionError:
                _list = []
        else:
            _list = (pad,)
        for entry in _list:
            if os.path.isdir(entry):
                if self.p['subdirs']:
                    self.subdirs(entry, level=level)
            elif os.path.islink(entry) and not self.p['follow_symlinks']:
                pass
            else:
                h, ext = os.path.splitext(entry)
                if len(self.p['extlist']) == 0 or ext.upper() in self.extlistUpper:
                    self.filenames.append(entry)

    def build_regexp_simple(self):
        """build the search regexp(s)
        this original version returns one compiled expression
        """
        zoek = ''
        for ch in self.p['zoek']:
            if not self.p['regexp']:
                if ch in ('.', '^','$','*','+','?','{','}','[',']','(',')','|',
                            '\\'):
                    zoek += "\\"
            zoek += ch
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
            for ch in data:
                if ch in ('.', '^','$','*','+','?','{','}','[',']','(',')','|',
                        '\\'):
                    zoek += "\\"
                zoek += ch
            return zoek

        negeer = ''
        flags = re.MULTILINE
        if not self.p['case']:
            flags |= re.IGNORECASE
        if self.p['regexp'] or self.p['wijzig']: # in these cases: always take literally
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
        in_quotes = also_required = forbidden = False
        zoekitem = ''
        possible_matches = []
        required_matches = []
        forbidden_matches = []
        def add_to_matches():
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
                forbidden=True
            else:
                zoekitem += char
        add_to_matches()
        return possible_matches, required_matches, forbidden_matches

    def do_action(self, search_python=False):
        for name in self.filenames:
            self.zoek(name)
        if not search_python: return
        results, self.rpt = self.rpt, []
        locations = {}
        for name in self.filenames:
            locations[name] = pyread(name)
        for item in results:
            test = item.split(' r. ', 1)
            if len(test) == 1:
                self.rpt.append(item)
                continue
            best = test[0]
            test = test[1].split(': ', 1)
            if len(test) == 1:
                self.rpt.append(item)
                continue
            lineno, text = test
            contains = contains_default
            for loc in locations[best]:
                lineno = int(lineno)
                if loc[0] < lineno <= loc[1]:
                    contains = loc[2]
                if loc[0] > lineno:
                    break
            self.rpt.append('{} r. {} ({}): {}'.format(best, lineno, contains, text))

    def zoek(self, best):
        "het daadwerkelijk uitvoeren van de zoek/vervang actie op een bepaald bestand"
        pos, lines, regels = 0, [], []
        msg = ""
        try_again = False
        with open(best, "r") as f_in:
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
            with open(best, "r", encoding=self.p['fallback_encoding']) as f_in:
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
                self.rpt.append("{0} r. {1}: {2}".format(best, lineno,
                    regels[lineno - 1].rstrip()))
            return

        # gebruik de oude manier van zoeken bij vervangen of bij regexp zoekstring
        result_list = self.re.finditer(data)
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
            ndata, aant = self.re.subn(self.p["vervang"], data)
            self.rpt.append("%s: %s times" % (best, aant))
            if self.p['backup']:
                bestnw = best + ".bak"
                shutil.copyfile(best, bestnw)
            with open(best,"w") as f_out:
                f_out.write(ndata)

    def complex_search(self, data, lines):
        # maak een lijst van alle locaties waar een string gevonden is
        # (plus de index van de  regexp die er bij hoort)
        found_in_lines = []
        for ix, re_ in enumerate(self.re):
            new_lines = [(x.start(), ix) for x in re_.finditer(data)]
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
        from_line = 0 # houdt bij vanaf welke regel het zin heeft om de inhoud te controleren
        for itemstart, number in sorted(found_in_lines):
            for lineno, linestart in enumerate(lines[from_line:]):
                if itemstart < linestart:
                    in_line = lineno + from_line    #  bereken het actuele regelnummer
                    from_line = lineno
                    break
            lines_found[in_line].add(number)

        # uitfilteren welke regel niet in alle zoekacties voorkomt of juist weggelaten met worden
        all_searches = set(range(len(self.re)))
        lines_left_over = []
        for line, values in lines_found.items():
            if -1 in values: continue
            if values == all_searches:
                lines_left_over.append(line)
        lines_left_over.sort()
        return lines_left_over
