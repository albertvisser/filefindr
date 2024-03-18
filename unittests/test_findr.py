"""unittests for ./afrift/findr_files.py
"""
import types
import pytest
from afrift import findr_files as testee


def test_determine_split_none(monkeypatch, capsys):
    """unittest for findr_files.determine_split_none
    """
    assert testee.determine_split_none('whatever') == 3


def test_determine_split_py(monkeypatch, capsys):
    """unittest for findr_files.determine_split_py
    """
    assert testee.determine_split_py(['', '', '', 'class', '', '']) == 5
    assert testee.determine_split_py(['', '', '', 'class', '', 'method']) == 7
    assert testee.determine_split_py(['', '', '', 'function']) == 5
    assert testee.determine_split_py('whatever') == 6


def _test_format_result(monkeypatch, capsys):
    """unittest for findr_files.format_result
    """
    assert testee.format_result(lines, context_type=None) == "expected_result"


def test_check_single_string(monkeypatch, capsys):
    """unittest for findr_files.check_single_string
    """
    assert not testee.check_single_string('hello')
    assert testee.check_single_string('"hello"')
    assert not testee.check_single_string('""hello""')
    assert testee.check_single_string('"""hello"""')
    assert testee.check_single_string("'hello'")
    assert not testee.check_single_string("''hello''")
    assert testee.check_single_string("'''hello'''")


def test_determine_filetype(monkeypatch, capsys):
    """unittest for findr_files.determine_filetype
    """
    def mock_subprocess_pyfile(*args, **kwargs):
        """stub
        """
        return types.SimpleNamespace(stdout='python')
    def mock_subprocess_nopyfile(*args, **kwargs):
        """stub
        """
        return types.SimpleNamespace(stdout='pytho')
    assert testee.determine_filetype(testee.pathlib.Path('')) == ''
    assert testee.determine_filetype(testee.pathlib.Path('test')) == ''
    assert testee.determine_filetype(testee.pathlib.Path('test.pu')) == ''
    assert testee.determine_filetype(testee.pathlib.Path('test.py')) == 'py'
    assert testee.determine_filetype(testee.pathlib.Path('test.pyw')) == 'py'
    monkeypatch.setattr(testee.subprocess, 'run', mock_subprocess_pyfile)
    assert testee.determine_filetype(testee.pathlib.Path('')) == 'py'
    monkeypatch.setattr(testee.subprocess, 'run', mock_subprocess_nopyfile)
    assert testee.determine_filetype(testee.pathlib.Path('')) == ''


def _test_read_input_file(monkeypatch, capsys):
    """unittest for findr_files.read_input_file
    """
    assert testee.read_input_file(file, fallback_encoding) == "expected_result"


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
        testobj = testee.Finder()
        assert not testobj.ok
        assert testobj.rpt == ["Fout: geen lijst bestanden en geen directory opgegeven"]
        testobj = testee.Finder(filelist=['x'], pad='hier')
        assert not testobj.ok
        assert testobj.rpt == ["Fout: lijst bestanden én directory opgegeven"]
        testobj = testee.Finder(pad='hier')
        assert not testobj.ok
        assert testobj.rpt == ['Fout: geen zoekstring opgegeven']
        testobj = testee.Finder(pad='hier', zoek='Vind')
        assert testobj.ok
        assert testobj.p['zoek'] == 'Vind'
        assert testobj.p['vervang'] == ''
        assert testobj.p['wijzig'] is True
        assert testobj.p['extlist'] == []
        assert testobj.extlist_upper == []
        testobj = testee.Finder(pad='hier', zoek='Vind', vervang=None, extlist=['py', '.pyw'])
        assert testobj.ok
        assert testobj.p['zoek'] == 'Vind'
        assert testobj.p['vervang'] is None
        assert testobj.p['wijzig'] is False
        assert testobj.p['extlist'] == ['py', '.pyw']
        assert testobj.extlist_upper == ['.PY', '.PYW']
        # etcetera, nu hier even niet mee bezig
        # missing coverage:
        # 269     self.p['extlist'] is truthy and len(self.p['extlist'] <= 1
        # 277-285 self.p['pad'] is falsey
        # 287     self.p['subdirs'] is truthy
        # 291-292 self errors is truthy

    def _test_setup_search(self, monkeypatch, capsys):
        """unittest for Finder.setup_search
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.setup_search() == "expected_result"
        assert capsys.readouterr().out == ("")

    def _test_subdirs(self, monkeypatch, capsys):
        """unittest for Finder.subdirs
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.subdirs(pad, level=0) == "expected_result"
        assert capsys.readouterr().out == ("")

    def _test_build_regexp_simple(self, monkeypatch, capsys):
        """unittest for Finder.build_regexp_simple
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.build_regexp_simple() == "expected_result"
        assert capsys.readouterr().out == ("")

    def _test_build_regexes(self, monkeypatch, capsys):
        """unittest for Finder.build_regexes
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.build_regexes() == "expected_result"
        assert capsys.readouterr().out == ("")

    def test_parse_zoek(self, monkeypatch, capsys):
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

    def _test_go(self, monkeypatch, capsys):
        """unittest for Finder.go
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.go() == "expected_result"
        assert capsys.readouterr().out == ("")

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

    def _test_backup_if_needed(self, monkeypatch, capsys):
        """unittest for Finder.backup_if_needed
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.backup_if_needed(fname) == "expected_result"
        assert capsys.readouterr().out == ("")
