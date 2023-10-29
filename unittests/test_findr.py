"""unittests for findr routines
"""

import types
import pathlib
import pytest
import afrift.findr_files as findr


def test_determine_split_none():
    assert findr.determine_split_none('whatever') == 3


def test_determine_split_py():
    assert findr.determine_split_py(['', '', '', 'class', '', '']) == 5
    assert findr.determine_split_py(['', '', '', 'class', '', 'method']) == 7
    assert findr.determine_split_py(['', '', '', 'function']) == 5
    assert findr.determine_split_py('whatever') == 6


def test_check_single_string():
    assert not findr.check_single_string('hello')
    assert findr.check_single_string('"hello"')
    assert not findr.check_single_string('""hello""')
    assert findr.check_single_string('"""hello"""')
    assert findr.check_single_string("'hello'")
    assert not findr.check_single_string("''hello''")
    assert findr.check_single_string("'''hello'''")


def test_determine_filetype(monkeypatch):
    def mock_subprocess_pyfile(*args, **kwargs):
        return types.SimpleNamespace(stdout='python')
    def mock_subprocess_nopyfile(*args, **kwargs):
        return types.SimpleNamespace(stdout='pytho')
    assert findr.determine_filetype(pathlib.Path('')) == ''
    assert findr.determine_filetype(pathlib.Path('test')) == ''
    assert findr.determine_filetype(pathlib.Path('test.pu')) == ''
    assert findr.determine_filetype(pathlib.Path('test.py')) == 'py'
    assert findr.determine_filetype(pathlib.Path('test.pyw')) == 'py'
    monkeypatch.setattr(findr.subprocess, 'run', mock_subprocess_pyfile)
    assert findr.determine_filetype(pathlib.Path('')) == 'py'
    monkeypatch.setattr(findr.subprocess, 'run', mock_subprocess_nopyfile)
    assert findr.determine_filetype(pathlib.Path('')) == ''


class TestFinder:
    def test_setup_class(self):
        with pytest.raises(TypeError):
            testobj = findr.Finder(gargl=False)
        testobj = findr.Finder()
        assert not testobj.ok
        assert testobj.rpt == ["Fout: geen lijst bestanden en geen directory opgegeven"]
        testobj = findr.Finder(filelist=['x'], pad='hier')
        assert not testobj.ok
        assert testobj.rpt == ["Fout: lijst bestanden én directory opgegeven"]
        testobj = findr.Finder(pad='hier')
        assert not testobj.ok
        assert testobj.rpt == ['Fout: geen zoekstring opgegeven']
        testobj = findr.Finder(pad='hier', zoek='Vind')
        assert testobj.ok
        assert testobj.p['zoek'] == 'Vind'
        assert testobj.p['vervang'] == ''
        assert testobj.p['wijzig'] is True
        assert testobj.p['extlist'] == []
        assert testobj.extlist_upper == []
        testobj = findr.Finder(pad='hier', zoek='Vind', vervang=None, extlist=['py', '.pyw'])
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

    def test_parse_zoek(self, monkeypatch):
        def mock_init(self, *args):
            self.p = {}
        monkeypatch.setattr(findr.Finder, '__init__', mock_init)
        testobj = findr.Finder()
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
