"""unittests for ./afrift/findr_files.py
"""
import types
import pytest
from afrift import findr_files as testee


def test_determine_split(monkeypatch, capsys):
    """unittest for findr_files.determine_split
    """
    assert testee.determine_split('None', 'whatever') == 3
    assert testee.determine_split('py', ['', '', '', 'class', '', '']) == 5
    assert testee.determine_split('py', ['', '', '', 'class', '', 'method']) == 7
    assert testee.determine_split('py', ['', '', '', 'function']) == 5
    assert testee.determine_split('py', 'whatever') == 6


def test_reformat_result(monkeypatch, capsys):
    """unittest for findr_files.format_result
    """
    def mock_determine(content_type, wordlist):
        print(f"called determine_split_none with args ('{content_type}', {wordlist})")
        if content_type == 'py':
            return 4
        return 3
    monkeypatch.setattr(testee, 'determine_split', mock_determine)
    assert testee.reformat_result([]) == []
    lines = ['no reformatting', 'before (first) blank line', '',
             'xx r. 1 qqqqq', 'xx r. 2 rrrrr', 'yy r. 3 ssss', 'zz r. 4 tttt', 'zz r. 5 uuuuu']
    assert testee.reformat_result(lines) == ['no reformatting', 'before (first) blank line',
                                             'xx', '',
                                             'r. 1:  qqqqq', 'r. 2:  rrrrr', '',
                                             'yy', '',
                                             'r. 3:  ssss', '',
                                             'zz', '',
                                             'r. 4:  tttt', 'r. 5:  uuuuu']
    assert capsys.readouterr().out == (
            "called determine_split_none with args ('None', ['xx', 'r.', '1', 'qqqqq'])\n"
            "called determine_split_none with args ('None', ['xx', 'r.', '2', 'rrrrr'])\n"
            "called determine_split_none with args ('None', ['yy', 'r.', '3', 'ssss'])\n"
            "called determine_split_none with args ('None', ['zz', 'r.', '4', 'tttt'])\n"
            "called determine_split_none with args ('None', ['zz', 'r.', '5', 'uuuuu'])\n")
    lines = ['', 'xx r. 1 aaaaa qqqqq', 'xx r. 2 aaaaa rrrrr', 'xx r. 3 bbbbb sssss',
             'yy r. 4 bbbbb ttttt', 'yy r. 5 ccccc uuuuu']
    # breakpoint()
    assert testee.reformat_result(lines, 'py') == ['xx',
                                                   'aaaaa', 'r. 1:  qqqqq', 'r. 2:  rrrrr',
                                                   'bbbbb', 'r. 3:  sssss', '',
                                                   'yy',
                                                   'bbbbb', 'r. 4:  ttttt',
                                                   'ccccc', 'r. 5:  uuuuu']
    assert capsys.readouterr().out == (
            "called determine_split_none with args ('py', ['xx', 'r.', '1', 'aaaaa', 'qqqqq'])\n"
            "called determine_split_none with args ('py', ['xx', 'r.', '2', 'aaaaa', 'rrrrr'])\n"
            "called determine_split_none with args ('py', ['xx', 'r.', '3', 'bbbbb', 'sssss'])\n"
            "called determine_split_none with args ('py', ['yy', 'r.', '4', 'bbbbb', 'ttttt'])\n"
            "called determine_split_none with args ('py', ['yy', 'r.', '5', 'ccccc', 'uuuuu'])\n")


def test_is_single_line_docstring(monkeypatch, capsys):
    """unittest for findr_files.is_single_line_docstring
    """
    assert not testee.is_single_line_docstring('hello')
    assert testee.is_single_line_docstring('"hello"')
    assert not testee.is_single_line_docstring('"hello')
    assert not testee.is_single_line_docstring('""hello""')
    assert testee.is_single_line_docstring('"""hello"""')
    assert not testee.is_single_line_docstring('"""hello')
    assert testee.is_single_line_docstring("'hello'")
    assert not testee.is_single_line_docstring("'hello")
    assert not testee.is_single_line_docstring("''hello''")
    assert testee.is_single_line_docstring("'''hello'''")
    assert not testee.is_single_line_docstring("'''hello")


def test_determine_filetype(monkeypatch, capsys):
    """unittest for findr_files.determine_filetype
    """
    def mock_subprocess_pyfile(*args, **kwargs):
        """stub
        """
        print('called subprocess.run with args', args, kwargs)
        return types.SimpleNamespace(stdout='python')
    def mock_subprocess_nopyfile(*args, **kwargs):
        """stub
        """
        print('called subprocess.run with args', args, kwargs)
        return types.SimpleNamespace(stdout='pytho')
    assert testee.determine_filetype(testee.pathlib.Path('')) == ''
    assert testee.determine_filetype(testee.pathlib.Path('test')) == ''
    assert testee.determine_filetype(testee.pathlib.Path('test.pu')) == ''
    assert testee.determine_filetype(testee.pathlib.Path('test.py')) == 'py'
    assert testee.determine_filetype(testee.pathlib.Path('test.pyw')) == 'py'
    monkeypatch.setattr(testee.subprocess, 'run', mock_subprocess_pyfile)
    assert testee.determine_filetype(testee.pathlib.Path('')) == 'py'
    assert capsys.readouterr().out == (
            "called subprocess.run with args"
            " (['file', PosixPath('.')],) {'stdout': -1, 'check': False}\n")
    monkeypatch.setattr(testee.subprocess, 'run', mock_subprocess_nopyfile)
    assert testee.determine_filetype(testee.pathlib.Path('')) == ''
    assert capsys.readouterr().out == (
            "called subprocess.run with args"
            " (['file', PosixPath('.')],) {'stdout': -1, 'check': False}\n")


def test_read_input_file(monkeypatch, capsys, tmp_path):
    """unittest for findr_files.read_input_file
    """
    fname = 'findr_results'
    as_utf = tmp_path / f'{fname}_unicode'
    as_utf.write_text('thïs\nis\nsøme\ntëxt\n', encoding='utf-8')
    as_latin = tmp_path / f'{fname}_latin'
    as_latin.write_text('thïs\nis\nsøme\ntëxt\n', encoding='latin-1')
    # assert testee.get_file(as_utf) == ['is\n', 'some\n', 'this\n', 'tëxt\n']
    # assert testee.get_file(as_latin) == ['is\n', 'some\n', 'this\n', 'tëxt\n']
    assert testee.read_input_file(as_utf, '') == ['thïs\n', 'is\n', 'søme\n', 'tëxt\n']
    assert testee.read_input_file(as_latin, 'latin-1') == ['thïs\n', 'is\n', 'søme\n', 'tëxt\n']
    assert testee.read_input_file(as_latin, 'utf-32') is None


def _test_pyread(monkeypatch, capsys):
    """unittest for findr_files.pyread
    """
    assert testee.pyread(file, fallback_encoding='latin-1', negeer_docs=False) == "expected_result"

    def _test_pop_construct(self, monkeypatch, capsys):
        """unittest for .pop_construct
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.pop_construct(last_line) == "expected_result"
        assert capsys.readouterr().out == ("")


class TestFinder:
    """unittest for findr_files.Finder
    """
    def setup_testobj(self, monkeypatch, capsys):
        """stub for findr_files.Finder object

        create the object skipping the normal initialization
        intercept messages during creation
        return the object so that other methods can be monkeypatched in the caller
        """
        def mock_init(self):
            """stub
            """
            print('called Finder.__init__')
        monkeypatch.setattr(testee.Finder, '__init__', mock_init)
        testobj = testee.Finder()
        assert capsys.readouterr().out == 'called Finder.__init__\n'
        testobj.p = {}
        return testobj

    def test_init(self, monkeypatch, capsys):
        """unittest for Finder.__init__
        """
        with pytest.raises(TypeError):
            testobj = testee.Finder(gargl=False)
        with pytest.raises(ValueError) as exc:
            testobj = testee.Finder()
        assert str(exc.value) == 'Geen zoekstring opgegeven'
        with pytest.raises(ValueError) as exc:
            testobj = testee.Finder(zoek='Vind')
        assert str(exc.value) == 'Geen zoeklocatie opgegeven'
        with pytest.raises(ValueError) as exc:
            testobj = testee.Finder(filelist=[])
        assert str(exc.value) == 'Geen zoekstring opgegeven'
        testobj = testee.Finder(zoek='Vind', filelist=[''])
        assert testobj.p['zoek'] == 'Vind'
        assert testobj.p['vervang'] is None
        assert not testobj.p['wijzig']
        assert testobj.p['extlist'] == []
        assert testobj.extlist_upper == []
        testobj = testee.Finder(zoek='Vind', vervang=None, filelist= ['xx'])
        assert testobj.p['zoek'] == 'Vind'
        assert testobj.p['vervang'] is None
        assert not testobj.p['wijzig']
        assert testobj.p['extlist'] == []
        assert testobj.extlist_upper == []
        testobj = testee.Finder(zoek='Vind', vervang='', filelist=['xx'])
        assert testobj.p['zoek'] == 'Vind'
        assert testobj.p['vervang'] == ''
        assert testobj.p['wijzig'] is True
        assert testobj.p['extlist'] == []
        assert testobj.extlist_upper == []
        testobj = testee.Finder(zoek='Vind', vervang='Vond', filelist=['xx'], extlist=['py', '.pyw'])
        assert testobj.p['zoek'] == 'Vind'
        assert testobj.p['vervang'] == 'Vond'
        assert testobj.p['wijzig'] is True
        assert testobj.p['extlist'] == ['py', '.pyw']
        assert testobj.extlist_upper == ['.PY', '.PYW']

    def test_setup_search(self, monkeypatch, capsys):
        """unittest for Finder.setup_search
        """
        def mock_build_simple():
            print('called Finder.build_regexp_simple')
            return 'simple_regex'
        def mock_build():
            print('called Finder.build_regexes')
            return 'find_regex', 'ignore_regex'
        def mock_subdirs(name):
            print(f"called Finder.subdirs with arg '{name}'")
            return []
        def mock_subdirs_2(name):
            print(f"called Finder.subdirs with arg '{name}'")
            return '???'
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.build_regexp_simple = mock_build_simple
        testobj.build_regexes = mock_build
        testobj.subdirs = mock_subdirs
        testobj.rpt = ['---']
        testobj.errors = []
        testobj.use_complex = True
        testobj.rgx = testobj.ignore = ''
        testobj.p['zoek'] = 'findstr'
        testobj.p['wijzig'] = False
        testobj.p['regexp'] = True
        testobj.p['extlist'] = ['xx']
        testobj.p['filelist'] = ['single file']
        testobj.p['subdirs'] = False
        assert testobj.setup_search()
        assert not testobj.use_complex
        assert testobj.rgx == 'simple_regex'
        assert testobj.ignore == ''
        # assert self.filenames == []   # niet zo interessant hier omdat deze in
        # assert self.dirnames == {}    # subdirs() aangevuld worden ipv in setup_search()
        assert testobj.errors == []
        assert testobj.rpt == ["Gezocht naar 'findstr' in bestanden van type xx in single file",
                               '---']
        assert capsys.readouterr().out == ("called Finder.build_regexp_simple\n"
                                           "called Finder.subdirs with arg 'single file'\n")
        testobj.rpt = ['---']
        testobj.errors = []
        testobj.use_complex = True
        testobj.rgx = testobj.ignore = ''
        testobj.p['zoek'] = 'findstr'
        testobj.p['vervang'] = 'replstr'
        testobj.p['wijzig'] = True
        testobj.p['regexp'] = False
        testobj.p['extlist'] = []
        testobj.p['filelist'] = ['a file', 'another file']
        testobj.p['subdirs'] = False
        assert testobj.setup_search()
        assert not testobj.use_complex
        assert testobj.rgx == 'simple_regex'
        assert testobj.ignore == ''
        assert testobj.errors == []
        assert testobj.rpt == ["Gezocht naar 'findstr' en dit vervangen door 'replstr'"
                               " in opgegeven bestanden/directories", '---']
        assert capsys.readouterr().out == ("called Finder.build_regexp_simple\n"
                                           "called Finder.subdirs with arg 'a file'\n"
                                           "called Finder.subdirs with arg 'another file'\n")
        testobj.subdirs = mock_subdirs_2
        testobj.rpt = ['---']
        testobj.errors = []
        testobj.use_complex = True
        testobj.rgx = testobj.ignore = ''
        testobj.p['zoek'] = 'findstr'
        testobj.p['wijzig'] = False
        testobj.p['regexp'] = False
        testobj.p['extlist'] = ['xx', 'yy', 'zz']
        testobj.p['filelist'] = ['a directory']
        testobj.p['subdirs'] = True
        assert not testobj.setup_search()
        assert testobj.use_complex
        assert testobj.rgx == 'find_regex'
        assert testobj.ignore == 'ignore_regex'
        assert testobj.errors == ['???']
        assert testobj.rpt == ["Gezocht naar 'findstr' in bestanden van type xx, yy en zz"
                               " in a directory en evt. onderliggende directories", '---',
                               "Zoekactie niet mogelijk"]
        assert capsys.readouterr().out == ("called Finder.build_regexes\n"
                                           "called Finder.subdirs with arg 'a directory'\n")

    def _test_subdirs(self, monkeypatch, capsys):
        """unittest for Finder.subdirs
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.subdirs(pad, level=0) == "expected_result"
        assert capsys.readouterr().out == ("")

    def test_build_regexp_simple(self, monkeypatch, capsys):
        """unittest for Finder.build_regexp_simple
        """
        def mock_compile(*args):
            return f'called re.compile with args {args}'
        monkeypatch.setattr(testee, 'special_chars', '!')
        monkeypatch.setattr(testee.re, 'compile', mock_compile)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.p['zoek'] = 'xy!z'
        testobj.p['case'] = False
        testobj.p['regexp'] = False
        flags_multi = testee.re.MULTILINE
        flags_both = testee.re.MULTILINE | testee.re.IGNORECASE
        assert testobj.build_regexp_simple() == (
                f"called re.compile with args ('xy\\\\!z', {flags_both})")
        testobj.p['case'] = False
        testobj.p['regexp'] = True
        assert testobj.build_regexp_simple() == (
                f"called re.compile with args ('xy!z', {flags_both})")
        testobj.p['case'] = True
        testobj.p['regexp'] = False
        assert testobj.build_regexp_simple() == (
                f"called re.compile with args ('xy\\\\!z', {flags_multi})")

    def _test_build_regexes(self, monkeypatch, capsys):
        """unittest for Finder.build_regexes
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.build_regexes() == "expected_result"
        assert capsys.readouterr().out == ("")

    def _test_parse_zoek(self, monkeypatch, capsys):
        """unittest for Finder.parse_zoek
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.p['zoek'] = 'test'
        assert testobj.parse_zoek() == (['test'], [], [])  # te testen methode
        # missing coverage:
        # 406     add_to_matches: zoekitem is falsey
        # 408     add_to_matches: also_requires is truthy
        # 410     add_to_matches: forbidden is truthy
        # 422-424 self.p['zoek'] contains "
        # 426     self.p['zoek'] contains , not inside quotes
        # 428-429 self.p['zoek'] contains + not inside quotes
        # 431-432 self.p['zoek'] contains - not inside quotes

    def test_go(self, monkeypatch, capsys):
        """unittest for Finder.go
        """
        def mock_zoek(naam):
            print(f"called Finder.zoek with arg '{naam}'")
        def mock_add():
            print("called Finder.add_context")
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.zoek = mock_zoek
        testobj.add_context = mock_add
        testobj.filenames = ['xxx']
        testobj.p["context"] = False
        testobj.go()
        assert capsys.readouterr().out == ("called Finder.zoek with arg 'xxx'\n")
        testobj.filenames = ['xxx', 'yyy', 'zzz']
        testobj.p["context"] = True
        testobj.go()
        assert capsys.readouterr().out == ("called Finder.zoek with arg 'xxx'\n"
                                           "called Finder.zoek with arg 'yyy'\n"
                                           "called Finder.zoek with arg 'zzz'\n"
                                           "called Finder.add_context\n")

    def _test_zoek(self, monkeypatch, capsys):
        """unittest for Finder.zoek
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.zoek(best) == "expected_result"
        assert capsys.readouterr().out == ("")

    def _test_complex_search(self, monkeypatch, capsys):
        """unittest for Finder.complex_search
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.complex_search(data, lines) == "expected_result"
        assert capsys.readouterr().out == ("")

    def _test_replace_selected(self, monkeypatch, capsys):
        """unittest for Finder.replace_selected
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.replace_selected(text, lines_to_replace) == "expected_result"
        assert capsys.readouterr().out == ("")

    def test_backup_if_needed(self, monkeypatch, capsys):
        """unittest for Finder.backup_if_needed
        """
        def mock_copy(*args):
            print('called shutil.copyfile with args', args)
        monkeypatch.setattr(testee.shutil, 'copyfile', mock_copy)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.p['backup'] = False
        testobj.backup_if_needed('filename')
        assert capsys.readouterr().out == ""
        testobj.p['backup'] = True
        testobj.backup_if_needed('filename')
        assert capsys.readouterr().out == (
                "called shutil.copyfile with args ('filename', 'filename.bak')\n")
