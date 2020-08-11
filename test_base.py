"""unittests for gui independent code
"""
import os
import pathlib
import pytest
import afrift.base as base

class TestMainFrame:
    def test_setup_class(self, monkeypatch, capsys):
        def mock_get_filename_list(*args):
            return ['x', 'y', 'z']
        def mock_get_filename_list_empty(*args):
            return []
        def mock_setup_options(self, *args):
            print('called setup_options')
            self.extraopts = {'no_gui': False}
        def mock_setup_options_nogui(self, *args):
            print('called setup_options')
            self.extraopts = {'no_gui': True}
        def mock_gui(*args):
            print('called gui instantiation')
        def mock_gui_setup_screen(*args):
            print('called gui.setup_screen')
        def mock_doe(*args):
            print('called doe')
        def mock_gui_go(*args):
            print('called gui.go')
        monkeypatch.setattr(base.MainFrame, 'get_filename_list', mock_get_filename_list)
        monkeypatch.setattr(base.MainFrame, 'setup_options', mock_setup_options)
        monkeypatch.setattr(base.MainFrameGui, '__init__', mock_gui)
        monkeypatch.setattr(base.MainFrameGui, 'setup_screen', mock_gui_setup_screen)
        monkeypatch.setattr(base.MainFrameGui, 'go', mock_gui_go)
        monkeypatch.setattr(base.MainFrame, 'doe', mock_doe)

        testsubj = base.MainFrame()
        assert testsubj.apptype == ''
        assert testsubj.p['filelist'] == ['x', 'y', 'z']
        assert capsys.readouterr().out == ('called setup_options\ncalled gui instantiation\n'
                                           'called gui.setup_screen\ncalled gui.go\n')
        monkeypatch.setattr(base.MainFrame, 'get_filename_list', mock_get_filename_list_empty)
        monkeypatch.setattr(base.MainFrame, 'setup_options', mock_setup_options_nogui)
        testsubj = base.MainFrame()
        assert testsubj.apptype == ''
        assert testsubj.p['filelist'] == []
        assert capsys.readouterr().out == ('called setup_options\ncalled gui instantiation\n'
                                           'called gui.setup_screen\ncalled doe\n')

    def test_get_filename_list(self, monkeypatch):
        def mock_setup_class(*args):
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

    def test_setup_options(self, monkeypatch, capsys):
        def mock_read_from_ini(*args):
            if len(args) > 1:
                print('called read_from_ini with `{}`'.format(args[1]))
            else:
                print('called read_from_ini with no args')
        def mock_apply_cmdline_options(*args):
            print('called apply_cmdline_options')
        def mock_setup_class(*args):
            return
        monkeypatch.setattr(base.MainFrame, '__init__', mock_setup_class)
        testsubj = base.MainFrame()

        testsubj.p = {'filelist': []}
        base.BASE = pathlib.Path.home()
        monkeypatch.setattr(base.MainFrame, 'read_from_ini', mock_read_from_ini)
        monkeypatch.setattr(base.MainFrame, 'apply_cmdline_options', mock_apply_cmdline_options)
        testsubj.setup_options()
        assert testsubj.p['fallback_encoding'] == 'latin-1'
        assert testsubj.editor_option == ['SciTE', '-open:{}', '-goto:{}']
        assert not testsubj.always_replace
        assert testsubj.maak_backups
        assert not testsubj.exit_when_ready
        assert capsys.readouterr().out == ('called read_from_ini with no args\n'
                                           'called apply_cmdline_options\n')
        (pathlib.Path.home() / 'fallback_encoding').unlink()
        (pathlib.Path.home() / 'open_result').unlink()
        testsubj.p = {'filelist': 'x'}
        base.BASE = pathlib.Path.home() / '.afrift'

    def test_read_from_ini(self, monkeypatch, capsys):
        def mock_get_iniloc(*args):
            loc = pathlib.Path.home() / 'testloc'
            return loc, loc / 'mfile', loc / 'ofile'
        def mock_setup_class(*args):
            return
        monkeypatch.setattr(base.MainFrame, '__init__', mock_setup_class)
        testsubj = base.MainFrame()
        testsubj.mru_items = None
        testsubj.outopts = testsubj.p = {}
        monkeypatch.setattr(base, 'get_iniloc', mock_get_iniloc)
        testsubj.read_from_ini()
        assert testsubj.mru_items == None
        assert testsubj.outopts == {}
        assert testsubj.p == {}
        # setup
        path = pathlib.Path.home() / 'testloc'
        path.mkdir(exist_ok=True)
        (path / 'mfile').write_text("""{"test": []}""")
        (path / 'ofile').write_text("""{"test": true, "tast": "y"}""")
        testsubj.outopts['test'] = False
        testsubj.save_options_keys = ('tast',)
        #test
        testsubj.read_from_ini()
        assert testsubj.mru_items == {'test': []}
        assert testsubj.outopts == {'test': True}
        assert testsubj.p == {'tast': 'y'}
        # teardown
        (path / mfile).unlink()
        (path / ofile).unlink()
        path.rmdir()


    def apply_cmdline_options(self, monkeypatch, capsys):
        def mock_setup_class(*args):
            return
        monkeypatch.setattr(base.MainFrame, '__init__', mock_setup_class)
        testsubj = base.MainFrame()
        testsubj.p = {}
        testsubj.outopts = testsubj.extraopts = {}
        testsubj.cmdline_options = {}
        testsubj.always_replace = testsubj.maak_backups = testsubj.exit_when_ready = False
        testsubj.apply_cmdline_options()
        assert testsubj.p == {'zoek': '', 'extlist': []}

    def write_to_ini(self, monkeypatch, capsysy):
        pass
