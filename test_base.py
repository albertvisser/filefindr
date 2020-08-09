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

    def setup_options(self, monkeypatch, capsys):
        pass





