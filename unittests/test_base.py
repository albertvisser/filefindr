"""unittests for ./afrift/base.py
"""
# import os
import pathlib
import pytest
from afrift import base

class TestMainFrame:
    """unittests for base.MainFrame
    """
    def test_setup_class(self, monkeypatch, capsys):
        """unittest for MainFrame.setup_class
        """
        def mock_get_filename_list(*args):
            """stub
            """
            return ['x', 'y', 'z']
        def mock_get_filename_list_empty(*args):
            """stub
            """
            return []
        def mock_setup_options(*args):
            """stub
            """
            print('called setup_options')
        def mock_apply_cmdline_options_nogui(self, *args):
            """stub
            """
            print('called apply_cmdline_options')
            self.extraopts = {'no_gui': True}
        def mock_apply_cmdline_options(self, *args):
            """stub
            """
            print('called apply_cmdline_options')
            self.extraopts = {'no_gui': False}
        def mock_gui(*args):
            """stub
            """
            print('called gui instantiation')
        def mock_gui_setup_screen(*args):
            """stub
            """
            print('called gui.setup_screen')
        def mock_doe(*args):
            """stub
            """
            print('called doe')
        def mock_gui_go(*args):
            """stub
            """
            print('called gui.go')
        monkeypatch.setattr(base.MainFrame, 'get_filename_list', mock_get_filename_list)
        monkeypatch.setattr(base.MainFrame, 'setup_options', mock_setup_options)
        monkeypatch.setattr(base.MainFrame, 'apply_cmdline_options', mock_apply_cmdline_options)
        monkeypatch.setattr(base.MainFrameGui, '__init__', mock_gui)
        monkeypatch.setattr(base.MainFrameGui, 'setup_screen', mock_gui_setup_screen)
        monkeypatch.setattr(base.MainFrameGui, 'go', mock_gui_go)
        monkeypatch.setattr(base.MainFrame, 'doe', mock_doe)

        testsubj = base.MainFrame()
        assert testsubj.apptype == ''
        assert testsubj.p['filelist'] == ['x', 'y', 'z']
        assert capsys.readouterr().out == ('called setup_options\ncalled apply_cmdline_options\n'
                'called gui instantiation\ncalled gui.setup_screen\ncalled gui.go\n')
        monkeypatch.setattr(base.MainFrame, 'get_filename_list', mock_get_filename_list_empty)
        monkeypatch.setattr(base.MainFrame, 'apply_cmdline_options',
                            mock_apply_cmdline_options_nogui)
        testsubj = base.MainFrame()
        assert testsubj.apptype == ''
        assert testsubj.p['filelist'] == []
        assert capsys.readouterr().out == ('called setup_options\ncalled apply_cmdline_options\n'
                'called gui instantiation\ncalled gui.setup_screen\ncalled doe\n')
        # gemist: r. 310 geen apptype opgegeven en fnaam argument bestaat en is directory

    def test_get_filename_list(self, monkeypatch):
        """unittest for MainFrame.get_filename_list
        """
        def mock_setup_class(*args):
            """stub
            """
            return
        monkeypatch.setattr(base.MainFrame, '__init__', mock_setup_class)
        testsubj = base.MainFrame()
        testsubj.apptype = 'anything'
        with pytest.raises(ValueError):
            testsubj.get_filename_list('', '', '')

        testsubj.apptype = ''
        assert testsubj.get_filename_list('', 'anything', ['x', 'y', 'z']) == []
        assert testsubj.get_filename_list('something', 'anything', ['x', 'y', 'z']) == ['anything']

        testsubj.apptype = 'single'
        testsubj.title = 'x'
        with pytest.raises(ValueError):
            testsubj.get_filename_list('', 'anything', ['x', 'y', 'z'])
        testsubj.title = 'x'
        assert testsubj.get_filename_list('something', 'anything', ['x', 'y', 'z']) == ['anything']
        assert testsubj.title == 'x - single file version'

        testsubj.apptype = 'multi'
        testsubj.title = 'x'
        with pytest.raises(ValueError):
            testsubj.get_filename_list('', '', '')
        testsubj.title = 'x'
        assert testsubj.get_filename_list('', 'anything', ['x', 'y', 'z']) == [pathlib.Path('x'),
                                                                               pathlib.Path('y'),
                                                                               pathlib.Path('z')]
        assert testsubj.title == 'x - multi-file version'
        # de rest moet nog (fn_orig/fnaam = directory, fn_orig/fnaam = file met namen)
        # maar ik weet al dat het werkt dus ik ga even verder met setup_options
        # gemist vogens coverage: 355-364 apptype = multi en 1e argument heeft waarde

    def test_setup_options(self, monkeypatch, capsys):
        """unittest for MainFrame.setup_options
        """
        def mock_read_from_ini(*args):
            """stub
            """
            if len(args) > 1:
                print(f'called read_from_ini with `{args[1]}`')
            else:
                print('called read_from_ini with no args')
        def mock_setup_class(self, *args):
            """stub
            """
            self.save_options_keys = (("case", 'case_sensitive'), ("woord", 'whole_words'),
                                     ("subdirs", 'recursive'), ("context", 'python_context'),
                                     ("negeer", 'ignore_comments'))
        monkeypatch.setattr(base.MainFrame, '__init__', mock_setup_class)
        testsubj = base.MainFrame()

        testsubj.p = {'filelist': []}
        base.BASE = pathlib.Path.home()
        monkeypatch.setattr(base.MainFrame, 'read_from_ini', mock_read_from_ini)
        testsubj.setup_options()
        assert testsubj.p['fallback_encoding'] == 'latin-1'
        assert testsubj.editor_option == ['SciTE', '-open:{}', '-goto:{}']
        # laatste test: [["Scite'\\nfile-option"]]
        assert not testsubj.always_replace
        assert testsubj.maak_backups
        assert not testsubj.exit_when_ready
        assert capsys.readouterr().out == ('called read_from_ini with no args\n')
        (pathlib.Path.home() / 'fallback_encoding').unlink()
        (pathlib.Path.home() / 'open_result').unlink()
        testsubj.p = {'filelist': [pathlib.Path.home() / 'x']}
        testsubj.apptype = ''
        testsubj.setup_options()
        assert capsys.readouterr().out == ('called read_from_ini with `{pathlib.Path.home()}/x`\n')
        testsubj.apptype = 'single'
        testsubj.setup_options()
        assert capsys.readouterr().out == ('called read_from_ini with `{pathlib.Path.home()}`\n')
        testsubj.apptype = 'multi'
        testsubj.p = {'filelist': [pathlib.Path.home() / 'x', pathlib.Path.home() / 'y' / 'x']}
        testsubj.setup_options()
        assert capsys.readouterr().out == ('called read_from_ini with `{pathlib.Path.home()}`\n')
        # volgens coverage niks gemist

    def test_read_from_ini(self, monkeypatch):
        """unittest for MainFrame.read_from_ini
        """
        def mock_get_iniloc(*args):
            """stub
            """
            loc = pathlib.Path.home() / 'testloc'
            return loc, loc / 'mfile', loc / 'ofile'
        def mock_setup_class(*args):
            """stub
            """
            return
        def clear_path(path):
            """stub
            """
            if not path.exists():
                return
            if (path / 'mfile').exists():
                (path / 'mfile').unlink()  # missing_ok=True)
            if (path / 'ofile').exists():
                (path / 'ofile').unlink()  # missing_ok=True)
            path.rmdir()
        monkeypatch.setattr(base.MainFrame, '__init__', mock_setup_class)
        testsubj = base.MainFrame()
        path = pathlib.Path.home() / 'testloc'
        clear_path(path)
        testsubj.mru_items = None
        testsubj.outopts, testsubj.p = {}, {}
        testsubj.save_options_keys = (('tast',),)
        monkeypatch.setattr(base, 'get_iniloc', mock_get_iniloc)
        testsubj.read_from_ini()
        assert testsubj.mru_items is None
        assert testsubj.outopts == {}
        assert testsubj.p == {}
        # setup
        path.mkdir(exist_ok=True)
        (path / 'mfile').write_text("""{"test": []}""")
        (path / 'ofile').write_text("""{"test": true, "tast": "y"}""")
        # test
        testsubj.outopts['test'] = False
        testsubj.read_from_ini()
        assert testsubj.mru_items == {'test': []}
        assert testsubj.outopts == {'test': True}
        assert testsubj.p == {'tast': 'y'}
        # teardown
        clear_path(path)
        # volgens coverage niks gemist

    def test_apply_cmdline_options(self, monkeypatch):
        """unittest for MainFrame.apply_cmdline_options
        """
        def mock_setup_class(self, *args):
            """stub
            """
            self.p = {}
            self.mru_items = {"zoek": [], "verv": [], "types": [], "dirs": []}
            self.save_options_keys = (("case", 'case_sensitive'), ("woord", 'whole_words'),
                                      ("subdirs", 'recursive'), ("context", 'python_context'),
                                      ("negeer", 'ignore_comments'))
            self.outopts = {'full_path': False, 'as_csv': False, 'summarize': False}
            self.extraopts = {}
            self.always_replace = self.maak_backups = self.exit_when_ready = False
        monkeypatch.setattr(base.MainFrame, '__init__', mock_setup_class)
        testsubj = base.MainFrame()
        testsubj.apply_cmdline_options({})
        assert testsubj.p == {'zoek': '', 'extlist': [], 'case': False, 'woord': False,
                              'subdirs': False, 'context': False, 'negeer': False}

        monkeypatch.setattr(base.MainFrame, '__init__', mock_setup_class)
        testsubj = base.MainFrame()
        testsubj.apply_cmdline_options({'search': 'zoek', 'replace': '', 'summarize': True})
        assert testsubj.p == {'zoek': 'zoek', 'vervang': '', 'extlist': [], 'case': False,
                              'woord': False, 'subdirs': False, 'context': False, 'negeer': False}
        assert testsubj.outopts['summarize'] is True
        # volgens coverage niks gemist

    def write_to_ini(self, monkeypatch, capsysy):
        """stub
        """
