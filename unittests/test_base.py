"""unittests for ./afrift/base.py
"""
import types
import pathlib
import pytest
from afrift import base as testee


class MockAfrift:
    "stub for main.Afrift"
    def __init__(self):
        print('called Afrift.__init__ ')
        self.gui = types.SimpleNamespace()


class MockResultsGui:
    "stub for gui.ResultsGui"
    # def __init__(self, parent, master):
    def __init__(self, *args):
        print('called ResultsGui.__init__ with args', args)
    # def setup_screen(self, captions):
    #     print(f"called ResultsGui.setup_screen with arg {captions}")
    def add_line(self):
        print('called ResultsGui.add_line')
        return 'line'
    def add_text_to_line(self, *args):
        print('called ResultsGui.add_text_to_line with args', args)
        return 'textfield'
    def add_buttons_to_line(self, *args, **kwargs):
        print('called ResultsGui.add_buttons_to_line with args', args, kwargs)
    def add_results_list(self, *args):
        print('called ResultsGui.add_results_list with args', args)
        return 'resultslist'
    def add_list_actions(self, *args):
        print('called ResultsGui.add_list_actions with args', args)
    def add_checkbox_to_line(self, *args):
        print('called ResultsGui.add_checkbox_to_line with args', args)
        return 'checkbox'
    def disable_widget(self, widget):
        print(f'called ResultsGui.disable_widget with arg {widget}')
    def finalize_display(self):
        print('called ResultsGui.finalize_display')
    def populate_list(self, *args):
        print('called ResultsGui.populate_list with args', args)
    def clear_contents(self):
        print('called ResultsGui.clear_contents')
    def go(self):
        print('called ResultsGui.go')
    # def set_header(self, text):
    #     print(f"called ResultsGui.set_header with arg '{text}'")
    def set_header(self, *args):
        print('called ResultsGui.set_header with args', args)
    def get_checkbox_value(self, *args):
        print('called ResultsGui.get_checkbox_value with args', args)
        return False
    def get_savefile(self, *args):
        print('called ResultsGui.get_savefile with args', args)
        return ''
    def meld(self, *args):
        print('called ResultsGui.meld with args', args)
    def get_text_from_user(self, *args):
        print('called ResultsGui.get_text_from_user with args', args)
        return ''
    def get_selection(self, *args):
        print('called ResultsGui.get_selection with args', args)
        return []
    def copy_to_clipboard(self, arg):
        print(f"called ResultsGui.copy_to_clipboard with arg '{arg}'")
    def to_result(self):
        print('called ResultsGui.to_result')
    def klaar(self, *args, **kwargs):
        print('called ResultsGui.klaar with args', args, kwargs)


class MockSelectNamesGui:
    "stub for gui.SelectnamesGui"
    def __init__(self, *args):
        print('called SelectNamesGui.__init__ with args', args)
    def setup_screen(self):
        print('called SelectNamesGui.setup_screen')
    def add_line(self):
        print('called SelectNamesGui.add_line')
        return 'line'
    def add_text_to_line(self, *args):
        print("called SelectNamesGui.add_text_to_line with args", args)
    def add_checkbox_to_line(self, *args):
        print("called SelectNamesGui.add_checkbox_to_line with args", args)
        return 'checkbox'
    def add_button_to_line(self, *args):
        print("called SelectNamesGui.add_button_to_line with args", args)
        return 'button'
    def add_selectionlist(self, *args):
        print("called SelectNamesGui.add_selectionlist with args", args)
        return 'selectionlist'
    def add_buttons(self, *args):
        print("called SelectNamesGui.add_buttons with args", args)
    def go(self):
        print("called SelectNamesGui.go")
        return 'gone'
    def select_all(self):
        "dummy callback, for refenrence"
    def invert_selection(self):
        "dummy callback, for refenrence"
    def cancel(self):
        "dummy callback, for refenrence"
    def confirm(self):
        "dummy callback, for refenrence"


def test_main(monkeypatch, capsys, tmp_path):
    """unittest for base.main
    """
    def mock_mkdir(*args, **kwargs):
        print('called pathlib.Path.mkdir with args', args, kwargs)
    def mock_touch(*args, **kwargs):
        print('called pathlib.Path.touch with args', args, kwargs)
    def mock_mainframe(*args, **kwargs):
        print('called Afrift with args', args, kwargs)
    def mock_mainframe_2(*args, **kwargs):
        print('called Afrift with args', args, kwargs)
        raise ValueError('message')
    with pytest.raises(TypeError) as exc:
        testee.main()
    assert str(exc.value) == "main() missing 1 required positional argument: 'args'"
    monkeypatch.setattr(testee.pathlib.Path, 'mkdir', mock_mkdir)
    monkeypatch.setattr(testee.pathlib.Path, 'touch', mock_touch)
    monkeypatch.setattr(testee, 'Afrift', mock_mainframe)
    mock_logfile = tmp_path / 'logs' / 'afrift.log'
    monkeypatch.setattr(testee, 'LOGFILE', mock_logfile)
    monkeypatch.setattr(testee, 'WANT_LOGGING', True)
    assert testee.main({'x': 'xx', 'output_file': ''}) == ''
    assert capsys.readouterr().out == (
            f"called pathlib.Path.mkdir with args ({mock_logfile.parent!r},) {{'exist_ok': True}}\n"
            f"called pathlib.Path.touch with args ({mock_logfile!r},) {{'exist_ok': True}}\n"
            "called Afrift with args () {'x': 'xx', 'output_file': ''}\n")

    monkeypatch.setattr(testee, 'WANT_LOGGING', False)
    assert testee.main({'x': 'xx', 'output_file': ''}) == ''
    assert capsys.readouterr().out == (
            "called Afrift with args () {'x': 'xx', 'output_file': ''}\n")

    assert testee.main({'output_file': '', 'full_path': 'zz'}) == (
            "Output options without output destination not allowed")
    assert capsys.readouterr().out == ''
    assert testee.main({'output_file': '', 'as_csv': True}) == (
            "Output options without output destination not allowed")
    assert capsys.readouterr().out == ''
    assert testee.main({'output_file': '', 'summarize': True}) == (
            "Output options without output destination not allowed")
    assert capsys.readouterr().out == ''
    assert testee.main({'output_file': 'zz', 'as_csv': True, 'summarize': True}) == (
            "'Output to csv' and 'summarize' is not a sensible combination")
    assert capsys.readouterr().out == ''
    assert testee.main({'output_file': 'zz', 'as_csv': False, 'summarize': True}) == ''
    assert capsys.readouterr().out == (
            "called Afrift with args () {'output_file': 'zz', 'as_csv': False,"
            " 'summarize': True}\n")
    assert testee.main({'output_file': 'zz', 'as_csv': True, 'summarize': False}) == ''
    assert capsys.readouterr().out == (
            "called Afrift with args () {'output_file': 'zz', 'as_csv': True,"
            " 'summarize': False}\n")

    monkeypatch.setattr(testee, 'Afrift', mock_mainframe_2)
    assert testee.main({'appmode': 'xx', 'fname': ['yy'], 'output_file': ''}) == 'message'
    assert capsys.readouterr().out == (
            "called Afrift with args () {'appmode': 'xx', 'fname': ['yy'], 'output_file': ''}\n")


def test_log(monkeypatch, capsys):
    """unittest for base.log
    """
    def mock_info(arg):
        print(f"called logging.info with arg '{arg}`")
    monkeypatch.setattr(testee.logging, 'info', mock_info)
    monkeypatch.setattr(testee, 'WANT_LOGGING', False)
    testee.log('message')
    assert capsys.readouterr().out == ""
    monkeypatch.setattr(testee, 'WANT_LOGGING', True)
    testee.log('message')
    assert capsys.readouterr().out == ("called logging.info with arg 'message`\n")


def test_get_iniloc(monkeypatch, tmp_path):
    """unittest for base.get_iniloc
    """
    def mock_cwd(*args):
        return testee.pathlib.Path('here')
    def mock_home(*args):
        return testee.pathlib.Path('/home')
    def mock_resolve(*args):
        return testee.pathlib.Path(f'/resolved/{args[0]}')
    monkeypatch.setattr(testee.pathlib.Path, 'cwd', mock_cwd)
    monkeypatch.setattr(testee.pathlib.Path, 'home', mock_home)
    monkeypatch.setattr(testee.pathlib.Path, 'resolve', mock_resolve)
    mockbase = tmp_path / 'afrift'
    monkeypatch.setattr(testee, 'BASE', mockbase)
    expected = mockbase / 'resolved_here'
    assert testee.get_iniloc() == (expected, expected / 'mru_items.json', expected / 'options.json')
    expected = mockbase / 'home'
    assert testee.get_iniloc(mock_home()) == (expected, expected / 'mru_items.json',
                                              expected / 'options.json')
    expected = mockbase / '~somewhere'
    assert testee.get_iniloc(mock_home() / 'somewhere') == (expected, expected / 'mru_items.json',
                                                            expected / 'options.json')
    expected = mockbase / 'resolved_somewhere'
    assert testee.get_iniloc('/somewhere') == (expected, expected / 'mru_items.json',
                                               expected / 'options.json')
    expected = mockbase / 'resolved_somewhere'
    assert testee.get_iniloc('somewhere') == (expected, expected / 'mru_items.json',
                                              expected / 'options.json')


def test_determine_mode_from_input(tmp_path):
    """unittest for determine_mode_from_input
    """
    with pytest.raises(ValueError) as err:
        testee.determine_mode_from_input(['filename'])
    assert str(err.value) == 'File does not exist'
    (tmp_path / 'testdir').mkdir()
    (tmp_path / 'testfile').touch()
    origdir = testee.os.getcwd()
    testee.os.chdir(tmp_path)
    assert testee.determine_mode_from_input(['testdir']) == (
            'single-dir', [tmp_path / 'testdir'])
    assert testee.determine_mode_from_input(['testfile']) == (
            'single-file', [tmp_path / 'testfile'])
    assert testee.determine_mode_from_input(['testfile1', 'testfile2']) == (
            'multi', [testee.pathlib.Path('testfile1'), testee.pathlib.Path('testfile2')])
    testee.os.chdir(origdir)


def test_expand_list_file(tmp_path):
    """unittest for expand_list_file
    """
    with pytest.raises(ValueError) as err:
        testee.expand_list_file('filename')
    assert str(err.value) == 'File does not exist'
    (tmp_path / 'testdir').mkdir()
    # (tmp_path / 'testfile').touch()
    (tmp_path / 'testfile').write_text('testfile1\ntestdir1/\ntestfile2  \ntestdir2\\\ntestfile3')

    origdir = testee.os.getcwd()
    testee.os.chdir(tmp_path)
    with pytest.raises(ValueError) as err:
        testee.expand_list_file('testdir')
    assert str(err.value) == 'List file must not be a directory'
    assert testee.expand_list_file('testfile') == [tmp_path / 'testfile1',
                                                   tmp_path / 'testdir1',
                                                   tmp_path / 'testfile2',
                                                   tmp_path / 'testdir2',
                                                   tmp_path / 'testfile3']
    testee.os.chdir(origdir)


class TestAfrift:
    """unittest for base.Afrift
    """
    def setup_testobj(self, monkeypatch, capsys):
        """stub for base.Afrift object

        create the object skipping the normal initialization
        intercept messages during creation
        return the object so that other methods can be monkeypatched in the caller
        """
        def mock_init(self, *args):
            """stub
            """
            print('called Afrift.__init__ with args', args)
        monkeypatch.setattr(testee.Afrift, '__init__', mock_init)
        testobj = testee.Afrift()
        assert capsys.readouterr().out == 'called Afrift.__init__ with args ()\n'
        testobj.p = {}
        testobj.mru_items = {"zoek": [], "verv": [], "types": [], "dirs": []}
        testobj.save_options_keys = (("case", 'case_sensitive'), ("woord", 'whole_words'),
                                    ("subdirs", 'recursive'), ("context", 'python_context'),
                                    ("negeer", 'ignore_comments'))
        testobj.outopts = {'full_path': False, 'as_csv': False, 'summarize': False}
        testobj.extraopts = {}
        testobj.always_replace = testobj.maak_backups = testobj.exit_when_ready = False
        return testobj

    def test_init(self, monkeypatch, capsys):
        """unittest for Afrift.__init__
        """
        def mock_setup_options(*args):
            """stub
            """
            print('called setup_options')
        def mock_determine(arg):
            """stub
            """
            print(f'called determine_mode_from_input with arg {arg}')
            if arg == 'expanded list-file':
                return 'multi', ['yyy', 'zzz']
            return 'single-file', ['xxx']
        def mock_expand(filename):
            print(f"called expand_list_file with arg '{filename}'")
            return 'expanded list-file'
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
            print('called AfriftGui.__init__')
        def mock_setup_screen(*args):
            """stub
            """
            print('called Afrift.setup_screen')
        def mock_doe(*args):
            """stub
            """
            print('called Afrift.doe')
        def mock_gui_go(*args):
            """stub
            """
            print('called AfriftGui.go')
        monkeypatch.setattr(testee.Afrift, 'setup_options', mock_setup_options)
        monkeypatch.setattr(testee, 'determine_mode_from_input', mock_determine)
        monkeypatch.setattr(testee, 'expand_list_file', mock_expand)
        monkeypatch.setattr(testee.Afrift, 'apply_cmdline_options', mock_apply_cmdline_options)
        monkeypatch.setattr(testee.Afrift, 'setup_screen', mock_setup_screen)
        monkeypatch.setattr(testee.Afrift, 'doe', mock_doe)
        monkeypatch.setattr(testee.AfriftGui, '__init__', mock_gui)
        monkeypatch.setattr(testee.AfriftGui, 'go', mock_gui_go)

        testobj = testee.Afrift()
        assert testobj.apptype == 'open'
        assert testobj.p['filelist'] == []
        assert capsys.readouterr().out == ('called setup_options\n'
                                           'called apply_cmdline_options\n'
                                           'called AfriftGui.__init__\n'
                                           'called Afrift.setup_screen\n'
                                           'called AfriftGui.go\n')

        monkeypatch.setattr(testee.Afrift, 'apply_cmdline_options',
                            mock_apply_cmdline_options_nogui)
        testobj = testee.Afrift()
        assert testobj.apptype == 'open'
        assert testobj.p['filelist'] == []
        assert capsys.readouterr().out == ('called setup_options\n'
                                           'called apply_cmdline_options\n'
                                           'called AfriftGui.__init__\n'
                                           'called Afrift.setup_screen\n'
                                           'called Afrift.doe\n')

        testobj = testee.Afrift(fnames=['xxx', 'yyy'])
        assert testobj.apptype == 'single-file'
        assert testobj.p['filelist'] == ['xxx']
        assert capsys.readouterr().out == (
                "called determine_mode_from_input with arg ['xxx', 'yyy']\n"
                'called setup_options\n'
                'called apply_cmdline_options\n'
                'called AfriftGui.__init__\n'
                'called Afrift.setup_screen\n'
                'called Afrift.doe\n')

        with pytest.raises(ValueError) as exc:
            testobj = testee.Afrift(fnames=['xxx', 'yyy'], list_file='zzz')
        assert str(exc.value) == 'List-file niet toegestaan bij lijst bestanden'

        testobj = testee.Afrift(list_file='zzz')
        assert testobj.apptype == 'multi'
        assert testobj.p['filelist'] == ['yyy', 'zzz']
        assert capsys.readouterr().out == (
                "called expand_list_file with arg 'zzz'\n"
                "called determine_mode_from_input with arg expanded list-file\n"
                'called setup_options\n'
                'called apply_cmdline_options\n'
                'called AfriftGui.__init__\n'
                'called Afrift.setup_screen\n'
                'called Afrift.doe\n')

    def test_get_filename_list(self, monkeypatch, capsys, tmp_path):
        """unittest for Afrift.get_filename_list
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        # assert testobj.get_filename_list(fn_orig, fnaam, flist) == "expected_result"
        # assert capsys.readouterr().out == ("")
        testobj.apptype = 'anything'
        with pytest.raises(ValueError):
            testobj.get_filename_list('', '', '')

        testobj.apptype = ''
        assert testobj.get_filename_list('', 'anything', ['x', 'y', 'z']) == []
        assert testobj.get_filename_list('something', 'anything', ['x', 'y', 'z']) == ['anything']

        testobj.apptype = 'single'
        testobj.title = 'x'
        with pytest.raises(ValueError):
            testobj.get_filename_list('', 'anything', ['x', 'y', 'z'])
        testobj.title = 'x'
        assert testobj.get_filename_list('something', 'anything', ['x', 'y', 'z']) == ['anything']
        assert testobj.title == 'x - single file version'

        testobj.apptype = 'multi'
        testobj.title = 'x'
        with pytest.raises(ValueError):
            testobj.get_filename_list('', '', '')
        testobj.title = 'x'
        assert testobj.get_filename_list('', 'anything', ['x', 'y', 'z']) == [pathlib.Path('x'),
                                                                              pathlib.Path('y'),
                                                                              pathlib.Path('z')]
        assert testobj.title == 'x - multi-file version'

        fnaam = tmp_path / 'testdir'
        fnaam.mkdir()
        assert testobj.get_filename_list('something', fnaam, ['x', 'y', 'z']) == [fnaam]
        assert testobj.title == 'x - multi-file version'
        assert testobj.apptype == ''

        testobj.title = 'x'
        testobj.apptype = 'multi'
        fnaam = tmp_path / 'testfile'
        fnaam.write_text('path1')
        monkeypatch.setattr(testee.pathlib.Path, 'is_dir', lambda x: False)
        assert testobj.get_filename_list('something', fnaam, ['x', 'y', 'z']) == [
                testee.HERE.parent / 'path1']
        assert testobj.title == 'x - single file version'
        assert testobj.apptype == 'single'

        count = 0
        def mock_is_dir(self):
            nonlocal count
            count += 1
            if count == 1:
                return False
            return True
        testobj.title = 'x'
        testobj.apptype = 'multi'
        monkeypatch.setattr(testee.pathlib.Path, 'is_dir', mock_is_dir)
        assert testobj.get_filename_list('something', fnaam, ['x', 'y', 'z']) == [
                testee.HERE.parent / 'path1']
        assert testobj.title == 'x'
        assert testobj.apptype == ''

        testobj.title = 'x'
        testobj.apptype = 'multi'
        fnaam.write_text('path1\npath2\\\npath3/')
        monkeypatch.setattr(testee.pathlib.Path, 'is_dir', lambda x: False)
        assert testobj.get_filename_list('something', fnaam, ['x', 'y', 'z']) == [
                testee.HERE.parent / 'path1',
                testee.HERE.parent / 'path2',
                testee.HERE.parent / 'path3']
        assert testobj.title == 'x - multi-file version'
        assert testobj.apptype == 'multi'

    def test_setup_options(self, monkeypatch, capsys, tmp_path):
        """unittest for Afrift.setup_options
        """
        def mock_read_from_ini(*args):
            """stub
            """
            print('called read_from_ini with args', args)
        mockbase = tmp_path / '.filefindr'
        mockbase.mkdir(exist_ok=True)
        monkeypatch.setattr(testee, 'BASE', mockbase)
        testobj = self.setup_testobj(monkeypatch, capsys)
        # assert testobj.setup_options() == "expected_result"
        # assert capsys.readouterr().out == ("")
        testobj.p = {'filelist': []}
        testobj.read_from_ini = mock_read_from_ini
        testobj.setup_options()
        assert testobj.p['fallback_encoding'] == 'latin-1'
        assert testobj.editor_option == [['SciTE'], '-open:{}', '-goto:{}']
        assert not testobj.always_replace
        assert testobj.maak_backups
        assert not testobj.exit_when_ready
        assert capsys.readouterr().out == ('called read_from_ini with args ()\n')

        (mockbase / 'open_result').write_text(
                "program = ['gnome-terminal', '--profile', 'Code Editor Shell', '--', 'vim']\n"
                "file-option = '{}'\n"
                "line-option = '+{}'\n")
        testobj.setup_options()
        assert testobj.editor_option == [['gnome-terminal', '--profile', 'Code Editor Shell',
                                          '--', 'vim'], '{}', '+{}']
        assert not testobj.always_replace
        assert testobj.maak_backups
        assert not testobj.exit_when_ready
        assert capsys.readouterr().out == ('called read_from_ini with args ()\n')

        testobj.p = {'filelist': [pathlib.Path.home() / 'x']}
        testobj.apptype = ''
        testobj.setup_options()
        assert capsys.readouterr().out == (
                "called read_from_ini with args (PosixPath('/home/albert/x'),)\n")
        testobj.apptype = 'single'
        testobj.setup_options()
        assert capsys.readouterr().out == (
                "called read_from_ini with args (PosixPath('/home/albert'),)\n")
        testobj.apptype = 'multi'
        testobj.p = {'filelist': [pathlib.Path.home() / 'x', pathlib.Path.home() / 'y' / 'x']}
        testobj.setup_options()
        assert capsys.readouterr().out == (
                "called read_from_ini with args ('/home/albert',)\n")

    def test_read_from_ini(self, monkeypatch, capsys, tmp_path):
        """unittest for Afrift.read_from_ini
        """
        loc = tmp_path
        mfile = loc / 'mru'
        mfile.write_text('entry1\nentry2')
        ofile = loc / 'opts'
        ofile.write_text('option1=xxx\noption2=yyy')
        def mock_get(arg):
            print(f"called get_iniloc with arg '{arg}'")
            return loc, mfile, ofile
        def mock_load(arg):
            print(f"called json.load with arg '{arg}'")
            if arg.name == str(ofile):
                return {'x': True, 'y': True, 'b': True}
            return {'q': ['q1', 'q2'], 'r': ['r1', 'r2']}
        monkeypatch.setattr(testee, 'get_iniloc', mock_get)
        monkeypatch.setattr(testee.json, 'load', mock_load)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.outopts = {'a': True, 'b': False}
        testobj.mru_items = {}
        testobj.save_options_keys = (('x', 'x_desc'), ('y', 'y_desc'))
        testobj.p = {'x': False}
        monkeypatch.setattr(testee.pathlib.Path, 'exists', lambda *x: False)
        testobj.read_from_ini()
        assert capsys.readouterr().out == ("called get_iniloc with arg 'None'\n")
        monkeypatch.setattr(testee.pathlib.Path, 'exists', lambda *x: True)
        testobj.read_from_ini(path='xx')
        assert testobj.mru_items == {'q': ['q1', 'q2'], 'r': ['r1', 'r2']}
        assert testobj.outopts == {'a': True, 'b': True}
        assert testobj.p == {'x': True, 'y': True}
        assert capsys.readouterr().out == (
                "called get_iniloc with arg 'xx'\n"
                f"called json.load with arg '<_io.TextIOWrapper name='{mfile}' mode='r'"
                " encoding='UTF-8'>'\n"
                f"called json.load with arg '<_io.TextIOWrapper name='{ofile}' mode='r'"
                " encoding='UTF-8'>'\n")

    def test_apply_cmdline_options(self, monkeypatch, capsys):
        """unittest for Afrift.apply_cmdline_options
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.apply_cmdline_options({})
        assert testobj.p == {'zoek': '', 'extlist': [], 'case': False, 'woord': False,
                             'subdirs': False, 'context': False, 'negeer': False}
        assert testobj.extraopts == {'use_saved': False, 'regex': '', 'follow_symlinks': '',
                                     'select_subdirs': '', 'select_files': '', 'dont_save': '',
                                     'no_gui': '', 'output_file': ''}
        assert testobj.outopts == {'full_path': False, 'as_csv': False, 'summarize': False}
        assert not testobj.always_replace
        assert testobj.maak_backups == ''
        assert testobj.exit_when_ready

        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.apply_cmdline_options({'search': 'zoek', 'replace': 'verv', 'extensions': ['x'],
                                       'use_saved': True})
        assert testobj.p == {'zoek': 'zoek', 'vervang': 'verv', 'extlist': ['x']}
        assert testobj.extraopts == {'use_saved': True, 'regex': '', 'follow_symlinks': '',
                                     'select_subdirs': '', 'select_files': '', 'dont_save': '',
                                     'no_gui': '', 'output_file': ''}
        assert testobj.outopts == {'full_path': False, 'as_csv': False, 'summarize': False}
        assert not testobj.always_replace
        assert testobj.maak_backups == ''
        assert testobj.exit_when_ready

        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.apply_cmdline_options({'search': 'zoek', 'replace': '', 'summarize': True})
        assert testobj.p == {'zoek': 'zoek', 'vervang': '', 'extlist': [], 'case': False,
                             'woord': False, 'subdirs': False, 'context': False, 'negeer': False}
        # assert testobj.outopts['summarize']
        assert testobj.extraopts == {'use_saved': False, 'regex': '', 'follow_symlinks': '',
                                     'select_subdirs': '', 'select_files': '', 'dont_save': '',
                                     'no_gui': '', 'output_file': ''}
        assert testobj.outopts == {'full_path': False, 'as_csv': False, 'summarize': True}
        assert testobj.always_replace
        assert testobj.maak_backups == ''
        assert testobj.exit_when_ready

    def test_setup_screen(self, monkeypatch, capsys):
        """unittest for Afrift.setup_screen
        """
        class MockGui:
            def init_screen(self):
                print('called AfriftGui.init_screen')
            def add_combobox_row(self, *args, **kwargs):
                print('called AfriftGui.add_combobox_row with args', args, kwargs)
                return 'combobox'
            def add_checkbox_row(self, *args, **kwargs):
                print('called AfriftGui.add_checkbox_row with args', args, kwargs)
                if 'spinner' in kwargs:
                    return 'checkbox', 'spinbox'
                return 'checkbox'
            def add_label_to_grid(self, *args, **kwargs):
                print('called AfriftGui.add_label_to_grid with args', args, kwargs)
            def add_listbox_to_grid(self, *args, **kwargs):
                print('called AfriftGui.add_label_to_grid with args', args, kwargs)
                return 'listbox'
            def add_buttons(self, arg):
                print('called AfriftGui.add_buttons with arg', arg)
            def set_focus_to(self, arg):
                print(f'called AfriftGui.set_focus_to with arg {arg}')
            def zoekdir(self):
                "empty callback for reference"
            def check_loc(self):
                "empty callback for reference"
            def einde(self):
                "empty callback for reference"
        def mock_doe(self):
            "empty callback for reference"
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.gui = MockGui()
        testobj.mru_items = {'zoek': ['mru', 'zoek'], 'verv': ['mru', 'verv'],
                             'dirs': ['mru', 'dirs'], 'types': ['mru', 'types']}
        testobj.extraopts = {'regex': 'rgx', 'follow_symlinks': 'flw', 'select_subdirs': 'sls',
                             'select_files': 'slf'}
        testobj.p = {'woord': 'x', 'case': 'cs', 'filelist': [], 'subdirs': 'sub', 'context': 'ctx',
                     'negeer': 'ign'}
        testobj.always_replace = 'rpl'
        testobj.maak_backups = 'bak'
        testobj.exit_when_ready = 'xit'
        testobj.doe = mock_doe
        testobj.apptype = 'open'
        testobj.setup_screen()
        assert testobj.vraag_zoek == 'combobox'
        assert testobj.vraag_regex == 'checkbox'
        assert testobj.vraag_case == 'checkbox'
        assert testobj.vraag_woord == 'checkbox'
        assert testobj.vraag_verv == 'combobox'
        assert testobj.vraag_leeg == 'checkbox'
        assert testobj.vraag_backup == 'checkbox'
        assert testobj.vraag_exit == 'checkbox'
        assert testobj.vraag_dir == 'combobox'
        assert testobj.vraag_subs == 'checkbox'
        assert testobj.vraag_links == 'checkbox'
        assert testobj.vraag_diepte == 'spinbox'
        assert testobj.ask_skipdirs == 'checkbox'
        assert testobj.ask_skipfiles == 'checkbox'
        assert testobj.vraag_types == 'combobox'
        assert testobj.vraag_context == 'checkbox'
        assert testobj.vraag_uitsluit == 'checkbox'
        assert capsys.readouterr().out == (
                "called AfriftGui.init_screen\n"
                "called AfriftGui.add_combobox_row with args"
                " ('Zoek naar:', ['mru', 'zoek']) {'initial': ''}\n"
                "called AfriftGui.add_checkbox_row with args"
                " ('regular expression (Python format)', 'rgx') {}\n"
                "called AfriftGui.add_checkbox_row with args"
                " ('hoofd/kleine letters gelijk', 'cs') {}\n"
                "called AfriftGui.add_checkbox_row with args ('hele woorden', 'x') {}\n"
                "called AfriftGui.add_combobox_row with args"
                " ('Vervang door:', ['mru', 'verv']) {'initial': '', 'completer': 'case'}\n"
                "called AfriftGui.add_checkbox_row with args"
                " ('lege vervangtekst = weghalen', 'rpl') {}\n"
                "called AfriftGui.add_checkbox_row with args"
                " ('gewijzigd(e) bestand(en) backuppen', 'bak') {}\n"
                "called AfriftGui.add_checkbox_row with args"
                " ('direct afsluiten na vervangen', 'xit') {}\n"
                "called AfriftGui.add_combobox_row with args"
                " ('In directory:', ['mru', 'dirs']) {'initial': '',"
                f" 'button': ('&Zoek', {testobj.gui.zoekdir}), 'completer': 'off',"
                f" 'callback': {testobj.update_defaults}}}\n"
                "called AfriftGui.add_checkbox_row with args"
                " ('ook subdirectories doorzoeken', 'sub') {}\n"
                "called AfriftGui.add_checkbox_row with args"
                " ('symlinks volgen - max. diepte (-1 is alles):',)"
                " {'toggler': 'flw', 'spinner': (5, -1)}\n"
                "called AfriftGui.add_checkbox_row with args"
                " ('selecteer (sub)directories om over te slaan', 'sls') {}\n"
                "called AfriftGui.add_checkbox_row with args"
                " ('selecteer bestanden om over te slaan', 'slf') {}\n"
                "called AfriftGui.add_combobox_row with args"
                " ('Alleen files van type:', ['mru', 'types']) {'initial': ''}\n"
                "called AfriftGui.add_checkbox_row with args"
                " ('context tonen (waar mogelijk, anders overslaan)', 'ctx') {}\n"
                "called AfriftGui.add_checkbox_row with args"
                " ('commentaren en docstrings negeren', 'ign') {'indent': 22}\n"
                "called AfriftGui.add_buttons with arg"
                f" (('&Uitvoeren', {testobj.doe}), ('&Afsluiten', {testobj.gui.einde}))\n"
                "called AfriftGui.set_focus_to with arg combobox\n")
        testobj.p['filelist'] = [testee.pathlib.Path('file')]
        testobj.setup_screen()
        assert testobj.vraag_zoek == 'combobox'
        assert testobj.vraag_regex == 'checkbox'
        assert testobj.vraag_case == 'checkbox'
        assert testobj.vraag_woord == 'checkbox'
        assert testobj.vraag_verv == 'combobox'
        assert testobj.vraag_leeg == 'checkbox'
        assert testobj.vraag_backup == 'checkbox'
        assert testobj.vraag_exit == 'checkbox'
        assert testobj.vraag_dir == 'combobox'
        assert testobj.vraag_subs == 'checkbox'
        assert testobj.vraag_links == 'checkbox'
        assert testobj.vraag_diepte == 'spinbox'
        assert testobj.ask_skipdirs == 'checkbox'
        assert testobj.ask_skipfiles == 'checkbox'
        assert testobj.vraag_types == 'combobox'
        assert testobj.vraag_context == 'checkbox'
        assert testobj.vraag_uitsluit == 'checkbox'
        assert capsys.readouterr().out == (
                "called AfriftGui.init_screen\n"
                "called AfriftGui.add_combobox_row with args"
                " ('Zoek naar:', ['mru', 'zoek']) {'initial': ''}\n"
                "called AfriftGui.add_checkbox_row with args"
                " ('regular expression (Python format)', 'rgx') {}\n"
                "called AfriftGui.add_checkbox_row with args"
                " ('hoofd/kleine letters gelijk', 'cs') {}\n"
                "called AfriftGui.add_checkbox_row with args ('hele woorden', 'x') {}\n"
                "called AfriftGui.add_combobox_row with args"
                " ('Vervang door:', ['mru', 'verv']) {'initial': '', 'completer': 'case'}\n"
                "called AfriftGui.add_checkbox_row with args"
                " ('lege vervangtekst = weghalen', 'rpl') {}\n"
                "called AfriftGui.add_checkbox_row with args"
                " ('gewijzigd(e) bestand(en) backuppen', 'bak') {}\n"
                "called AfriftGui.add_checkbox_row with args"
                " ('direct afsluiten na vervangen', 'xit') {}\n"
                "called AfriftGui.add_combobox_row with args"
                " ('In directory:', ['mru', 'dirs']) {'initial': 'file',"
                f" 'button': ('&Zoek', {testobj.gui.zoekdir}), 'completer': 'off',"
                f" 'callback': {testobj.update_defaults}}}\n"
                "called AfriftGui.add_checkbox_row with args"
                " ('ook subdirectories doorzoeken', 'sub') {}\n"
                "called AfriftGui.add_checkbox_row with args"
                " ('symlinks volgen - max. diepte (-1 is alles):',)"
                " {'toggler': 'flw', 'spinner': (5, -1)}\n"
                "called AfriftGui.add_checkbox_row with args"
                " ('selecteer (sub)directories om over te slaan', 'sls') {}\n"
                "called AfriftGui.add_checkbox_row with args"
                " ('selecteer bestanden om over te slaan', 'slf') {}\n"
                "called AfriftGui.add_combobox_row with args"
                " ('Alleen files van type:', ['mru', 'types']) {'initial': ''}\n"
                "called AfriftGui.add_checkbox_row with args"
                " ('context tonen (waar mogelijk, anders overslaan)', 'ctx') {}\n"
                "called AfriftGui.add_checkbox_row with args"
                " ('commentaren en docstrings negeren', 'ign') {'indent': 22}\n"
                "called AfriftGui.add_buttons with arg"
                f" (('&Uitvoeren', {testobj.doe}), ('&Afsluiten', {testobj.gui.einde}))\n"
                "called AfriftGui.set_focus_to with arg combobox\n")
        testobj.apptype = 'single-file'
        testobj.setup_screen()
        assert testobj.vraag_zoek == 'combobox'
        assert testobj.vraag_regex == 'checkbox'
        assert testobj.vraag_case == 'checkbox'
        assert testobj.vraag_woord == 'checkbox'
        assert testobj.vraag_verv == 'combobox'
        assert testobj.vraag_leeg == 'checkbox'
        assert testobj.vraag_backup == 'checkbox'
        assert testobj.vraag_exit == 'checkbox'
        assert testobj.vraag_context == 'checkbox'
        assert testobj.vraag_uitsluit == 'checkbox'
        assert capsys.readouterr().out == (
                "called AfriftGui.init_screen\n"
                "called AfriftGui.add_combobox_row with args"
                " ('Zoek naar:', ['mru', 'zoek']) {'initial': ''}\n"
                "called AfriftGui.add_checkbox_row with args"
                " ('regular expression (Python format)', 'rgx') {}\n"
                "called AfriftGui.add_checkbox_row with args"
                " ('hoofd/kleine letters gelijk', 'cs') {}\n"
                "called AfriftGui.add_checkbox_row with args ('hele woorden', 'x') {}\n"
                "called AfriftGui.add_combobox_row with args"
                " ('Vervang door:', ['mru', 'verv']) {'initial': '', 'completer': 'case'}\n"
                "called AfriftGui.add_checkbox_row with args"
                " ('lege vervangtekst = weghalen', 'rpl') {}\n"
                "called AfriftGui.add_checkbox_row with args"
                " ('gewijzigd(e) bestand(en) backuppen', 'bak') {}\n"
                "called AfriftGui.add_checkbox_row with args"
                " ('direct afsluiten na vervangen', 'xit') {}\n"
                "called AfriftGui.add_label_to_grid with args"
                " ('In file/directory:',) {'new_row': True}\n"
                "called AfriftGui.add_label_to_grid with args ('file',) {'left_align': True}\n"
                "called AfriftGui.add_checkbox_row with args"
                " ('context tonen (waar mogelijk, anders overslaan)', 'ctx') {}\n"
                "called AfriftGui.add_checkbox_row with args"
                " ('commentaren en docstrings negeren', 'ign') {'indent': 22}\n"
                "called AfriftGui.add_buttons with arg"
                f" (('&Uitvoeren', {testobj.doe}), ('&Afsluiten', {testobj.gui.einde}))\n"
                "called AfriftGui.set_focus_to with arg combobox\n")
        testobj.p = {'woord': 'wrd', 'case': 'cs', 'verv': 'vrv',
                     'filelist': ['file', pathlib.Path('list')],
                     'subdirs': 'sub', 'extlist': ['ext', 'list'], 'context': 'ctx', 'negeer': 'ign'}
        testobj.apptype = 'single-dir'
        testobj.setup_screen()
        assert testobj.vraag_zoek == 'combobox'
        assert testobj.vraag_regex == 'checkbox'
        assert testobj.vraag_case == 'checkbox'
        assert testobj.vraag_woord == 'checkbox'
        assert testobj.vraag_verv == 'combobox'
        assert testobj.vraag_leeg == 'checkbox'
        assert testobj.vraag_backup == 'checkbox'
        assert testobj.vraag_exit == 'checkbox'
        assert testobj.vraag_subs == 'checkbox'
        assert testobj.vraag_links == 'checkbox'
        assert testobj.vraag_diepte == 'spinbox'
        assert testobj.ask_skipdirs == 'checkbox'
        assert testobj.ask_skipfiles == 'checkbox'
        assert testobj.vraag_types == 'combobox'
        assert testobj.vraag_context == 'checkbox'
        assert testobj.vraag_uitsluit == 'checkbox'
        assert capsys.readouterr().out == (
                "called AfriftGui.init_screen\n"
                "called AfriftGui.add_combobox_row with args"
                " ('Zoek naar:', ['mru', 'zoek']) {'initial': ''}\n"
                "called AfriftGui.add_checkbox_row with args"
                " ('regular expression (Python format)', 'rgx') {}\n"
                "called AfriftGui.add_checkbox_row with args"
                " ('hoofd/kleine letters gelijk', 'cs') {}\n"
                "called AfriftGui.add_checkbox_row with args ('hele woorden', 'wrd') {}\n"
                "called AfriftGui.add_combobox_row with args"
                " ('Vervang door:', ['mru', 'verv']) {'initial': 'vrv', 'completer': 'case'}\n"
                "called AfriftGui.add_checkbox_row with args"
                " ('lege vervangtekst = weghalen', 'rpl') {}\n"
                "called AfriftGui.add_checkbox_row with args"
                " ('gewijzigd(e) bestand(en) backuppen', 'bak') {}\n"
                "called AfriftGui.add_checkbox_row with args"
                " ('direct afsluiten na vervangen', 'xit') {}\n"
                "called AfriftGui.add_label_to_grid with args"
                " ('In file/directory:',) {'new_row': True}\n"
                "called AfriftGui.add_label_to_grid with args ('file',) {'left_align': True}\n"
                "called AfriftGui.add_checkbox_row with args"
                " ('ook subdirectories doorzoeken', 'sub') {}\n"
                "called AfriftGui.add_checkbox_row with args"
                " ('symlinks volgen - max. diepte (-1 is alles):',)"
                " {'toggler': 'flw', 'spinner': (5, -1)}\n"
                "called AfriftGui.add_checkbox_row with args"
                " ('selecteer (sub)directories om over te slaan', 'sls') {}\n"
                "called AfriftGui.add_checkbox_row with args"
                " ('selecteer bestanden om over te slaan', 'slf') {}\n"
                "called AfriftGui.add_combobox_row with args"
                " ('Alleen files van type:', ['mru', 'types']) {'initial': ['ext', 'list']}\n"
                "called AfriftGui.add_checkbox_row with args"
                " ('context tonen (waar mogelijk, anders overslaan)', 'ctx') {}\n"
                "called AfriftGui.add_checkbox_row with args"
                " ('commentaren en docstrings negeren', 'ign') {'indent': 22}\n"
                "called AfriftGui.add_buttons with arg"
                f" (('&Uitvoeren', {testobj.doe}), ('&Afsluiten', {testobj.gui.einde}))\n"
                "called AfriftGui.set_focus_to with arg combobox\n")
        testobj.apptype = 'multi'
        testobj.setup_screen()
        assert testobj.vraag_zoek == 'combobox'
        assert testobj.vraag_regex == 'checkbox'
        assert testobj.vraag_case == 'checkbox'
        assert testobj.vraag_woord == 'checkbox'
        assert testobj.vraag_verv == 'combobox'
        assert testobj.vraag_leeg == 'checkbox'
        assert testobj.vraag_backup == 'checkbox'
        assert testobj.vraag_exit == 'checkbox'
        assert testobj.lb == 'listbox'
        assert testobj.vraag_subs == 'checkbox'
        assert testobj.vraag_links == 'checkbox'
        assert testobj.vraag_diepte == 'spinbox'
        assert testobj.ask_skipdirs == 'checkbox'
        assert testobj.ask_skipfiles == 'checkbox'
        assert testobj.vraag_types == 'combobox'
        assert testobj.vraag_context == 'checkbox'
        assert testobj.vraag_uitsluit == 'checkbox'
        assert capsys.readouterr().out == (
                "called AfriftGui.init_screen\n"
                "called AfriftGui.add_combobox_row with args"
                " ('Zoek naar:', ['mru', 'zoek']) {'initial': ''}\n"
                "called AfriftGui.add_checkbox_row with args"
                " ('regular expression (Python format)', 'rgx') {}\n"
                "called AfriftGui.add_checkbox_row with args"
                " ('hoofd/kleine letters gelijk', 'cs') {}\n"
                "called AfriftGui.add_checkbox_row with args ('hele woorden', 'wrd') {}\n"
                "called AfriftGui.add_combobox_row with args"
                " ('Vervang door:', ['mru', 'verv']) {'initial': 'vrv', 'completer': 'case'}\n"
                "called AfriftGui.add_checkbox_row with args"
                " ('lege vervangtekst = weghalen', 'rpl') {}\n"
                "called AfriftGui.add_checkbox_row with args"
                " ('gewijzigd(e) bestand(en) backuppen', 'bak') {}\n"
                "called AfriftGui.add_checkbox_row with args"
                " ('direct afsluiten na vervangen', 'xit') {}\n"
                "called AfriftGui.add_label_to_grid with args"
                " ('In de volgende files/directories:',) {'fullwidth': True}\n"
                "called AfriftGui.add_label_to_grid with args (['file', 'list'],) {}\n"
                "called AfriftGui.add_checkbox_row with args"
                " ('van geselecteerde directories ook subdirectories doorzoeken', 'sub') {}\n"
                "called AfriftGui.add_checkbox_row with args"
                " ('symlinks volgen - max. diepte (-1 is alles):',)"
                " {'toggler': 'flw', 'spinner': (5, -1)}\n"
                "called AfriftGui.add_checkbox_row with args"
                " ('selecteer (sub)directories om over te slaan', 'sls') {}\n"
                "called AfriftGui.add_checkbox_row with args"
                " ('selecteer bestanden om over te slaan', 'slf') {}\n"
                "called AfriftGui.add_combobox_row with args"
                " ('Alleen files van type:', ['mru', 'types']) {'initial': ['ext', 'list']}\n"
                "called AfriftGui.add_checkbox_row with args"
                " ('context tonen (waar mogelijk, anders overslaan)', 'ctx') {}\n"
                "called AfriftGui.add_checkbox_row with args"
                " ('commentaren en docstrings negeren', 'ign') {'indent': 22}\n"
                "called AfriftGui.add_buttons with arg"
                f" (('&Uitvoeren', {testobj.doe}), ('&Afsluiten', {testobj.gui.einde}))\n"
                "called AfriftGui.set_focus_to with arg combobox\n")

    def test_update_defaults(self, monkeypatch, capsys, tmp_path):
        """unittest for AfriftGui.update_defaults
        """
        class MockGui:
            def get_sender_value(self):
                print('called AfriftGui.get_sender_value')
                return sender_value
            def replace_combobox_items(self, *args):
                print('called AfriftGui.replace_combobox_items wth args', args)
            def set_checkbox_value(self, *args):
                print('called AfriftGui.set_checkbox_value wth args', args)
        def mock_read(arg):
            print(f"called Afrift.read_from_ini with arg '{arg}'")
        sender_value = f'{tmp_path}/xxx{testee.os.path.sep}'
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.gui = MockGui()
        testobj.mru_items = {'zoek': ['mru', 'zoek'], 'verv': ['mru', 'verv'],
                             'types': ['mru', 'types']}
        testobj.p = {'woord': 'x', 'case': 'cs', 'subdirs': 'sub', 'context': 'ctx',
                     'negeer': 'ign'}
        testobj.read_from_ini = mock_read
        testobj.vraag_zoek = 'vraag_zoek'
        testobj.vraag_verv = 'vraag_verv'
        testobj.vraag_types = 'vraag_types'
        testobj.vraag_case = 'vraag_case'
        testobj.vraag_woord = 'vraag_woord'
        testobj.vraag_subs = 'vraag_subdirs'
        testobj.vraag_context = 'vraag_context'
        testobj.vraag_uitsluit = 'vraag_negeer'
        testobj.update_defaults()
        assert capsys.readouterr().out == "called AfriftGui.get_sender_value\n"
        (tmp_path / 'xxx').mkdir()
        testobj.update_defaults()
        assert capsys.readouterr().out == "called AfriftGui.get_sender_value\n"
        (tmp_path / 'xxx').rmdir()
        sender_value = str(tmp_path / 'xxx')
        testobj.update_defaults()
        assert capsys.readouterr().out == "called AfriftGui.get_sender_value\n"
        (tmp_path / 'xxx').touch()
        testobj.update_defaults()
        assert capsys.readouterr().out == (
            "called AfriftGui.get_sender_value\n"
            f"called Afrift.read_from_ini with arg '{tmp_path / 'xxx'}'\n"
            "called AfriftGui.replace_combobox_items wth args ('vraag_zoek', ['mru', 'zoek'])\n"
            "called AfriftGui.replace_combobox_items wth args ('vraag_verv', ['mru', 'verv'])\n"
            "called AfriftGui.replace_combobox_items wth args ('vraag_types', ['mru', 'types'])\n"
            "called AfriftGui.set_checkbox_value wth args ('vraag_case', 'cs')\n"
            "called AfriftGui.set_checkbox_value wth args ('vraag_woord', 'x')\n"
            "called AfriftGui.set_checkbox_value wth args ('vraag_subdirs', 'sub')\n"
            "called AfriftGui.set_checkbox_value wth args ('vraag_context', 'ctx')\n"
            "called AfriftGui.set_checkbox_value wth args ('vraag_negeer', 'ign')\n")

    def test_doe(self, monkeypatch, capsys, tmp_path):
        """unittest for Afrift.doe
        """
        class MockGui:
            """stub
            """
            def error(self, *args):
                print('called AfriftGui.error with args', args)
            def meld(self, *args):
                print('called AfriftGui.meld with args', args)
            def add_item_to_searchlist(self, *args):
                print('called AfriftGui.add_item_to_searchlist with args', args)
            def set_waitcursor(self, value):
                print(f'called AfriftGui.set_waitcursor with arg {value}')
            def get_checkbox_value(self, *args):
                print('called AfriftGui.get_checkbox_value with args', args)
                return False
            def get_checkbox_value_2(self, *args):
                print('called AfriftGui.get_checkbox_value with args', args)
                return True
            def get_exit(self):
                print('called AfriftGui.get_exit')
                return False
            def einde(self):
                print('called AfriftGui.einde')
        class MockFinder:
            """stub
            """
            filenames = []
            errors = ''

            def __init__(self, **kwargs):
                print('called Finder.__init__ with args', kwargs)
                self.rpt = ['init fout']
            def setup_search(self):
                print('called Finder.setup_search')
                self.rpt = 'header'
                self.errors = 'message'
                return False
            def go(self):
                print('called Finder.go')
        def mockfinder_init_2(self, **kwargs):
            print('called Finder.__init__ with args', kwargs)
            self.rpt = []
        def mockfinder_setup_search_2(self):
            print('called Finder.setup_search')
            self.rpt = 'header'
            return True
        def mockfinder_setup_search_3(self):
            print('called Finder.setup_search')
            self.rpt = 'header'
            self.filenames = ['xxxxx']
            return True
        def mock_setup():
            print('called Afrift.setup_parameters')
            return 'xxx'
        def mock_setup_2():
            print('called Afrift.setup_parameters')
            return ''
        def mock_write(arg):
            print(f'called Afrift.write_to_ini with arg {arg}')
        def mock_select():
            print('called Afrift.select_search_exclusions_if_requested')
            return True
        def mock_select_2():
            print('called Afrift.select_search_exclusions_if_requested')
            return False
        def mock_show():
            print('called Afrift.show_results')
        monkeypatch.setattr(testee, 'Finder', MockFinder)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.gui = MockGui()
        testobj.write_to_ini = mock_write
        testobj.select_search_exclusions_if_requested = mock_select
        testobj.show_results = mock_show
        testobj.vraag_zoek = 'vraag_zoek'
        testobj.vraag_exit = 'vraag_exit'
        testobj.fouttitel = 'error:'
        testobj.resulttitel = 'results:'
        testobj.p = {'zoek': 'find_me', 'vervang': None}
        testobj.setup_parameters = mock_setup
        testobj.doe()
        assert capsys.readouterr().out == ("called Afrift.setup_parameters\n"
                                           "called AfriftGui.error with args ('error:', 'xxx')\n")

        testobj.setup_parameters = mock_setup_2
        testobj.extraopts['dont_save'] = True
        testobj.doe()
        assert capsys.readouterr().out == (
                "called Afrift.setup_parameters\n"
                "called AfriftGui.add_item_to_searchlist with args ('vraag_zoek', 'find_me')\n"
                "called Finder.__init__ with args {'zoek': 'find_me', 'vervang': None}\n"
                "called AfriftGui.error with args ('error:', 'init fout')\n")

        MockFinder.__init__ = mockfinder_init_2
        testobj.doe()
        assert capsys.readouterr().out == (
                "called Afrift.setup_parameters\n"
                "called AfriftGui.add_item_to_searchlist with args ('vraag_zoek', 'find_me')\n"
                "called Finder.__init__ with args {'zoek': 'find_me', 'vervang': None}\n"
                "called Finder.setup_search\n"
                "called AfriftGui.meld with args ('results:', 'header\\nmessage')\n")

        MockFinder.setup_search = mockfinder_setup_search_2
        testobj.extraopts['dont_save'] = False
        testobj.p['filelist'] = [tmp_path]
        # breakpoint()
        testobj.doe()
        assert capsys.readouterr().out == (
                "called Afrift.setup_parameters\n"
                "called AfriftGui.add_item_to_searchlist with args ('vraag_zoek', 'find_me')\n"
                f"called Afrift.write_to_ini with arg {tmp_path.parent}\n"
                "called Finder.__init__ with args"
                f" {{'zoek': 'find_me', 'vervang': None, 'filelist': [{tmp_path!r}]}}\n"
                "called Finder.setup_search\n"
                "called AfriftGui.meld with args ('results:', 'Geen bestanden om te doorzoeken')\n")

        MockFinder.setup_search = mockfinder_setup_search_3
        testobj.p['pad'] = 'xxx'
        testobj.apptype = 'single-file'
        testobj.extraopts['no_gui'] = False
        testobj.doe()
        assert capsys.readouterr().out == (
            "called Afrift.setup_parameters\n"
            "called AfriftGui.add_item_to_searchlist with args ('vraag_zoek', 'find_me')\n"
            f"called Afrift.write_to_ini with arg {testee.HERE.parent}/xxx\n"
            "called Finder.__init__ with args"
            f" {{'zoek': 'find_me', 'vervang': None, 'filelist': [{tmp_path!r}], 'pad': 'xxx'}}\n"
            "called Finder.setup_search\n"
            "called AfriftGui.set_waitcursor with arg True\n"
            "called Finder.go\n"
            "called AfriftGui.set_waitcursor with arg False\n"
            "called Afrift.show_results\n"
            "called AfriftGui.get_checkbox_value with args ('vraag_exit',)\n")
        testobj.apptype = 'not single-file'
        testobj.doe()
        assert capsys.readouterr().out == (
            "called Afrift.setup_parameters\n"
            "called AfriftGui.add_item_to_searchlist with args ('vraag_zoek', 'find_me')\n"
            f"called Afrift.write_to_ini with arg {testee.HERE.parent}/xxx\n"
            "called Finder.__init__ with args"
            f" {{'zoek': 'find_me', 'vervang': None, 'filelist': [{tmp_path!r}], 'pad': 'xxx'}}\n"
            "called Finder.setup_search\n"
            "called Afrift.select_search_exclusions_if_requested\n")

        testobj.p.pop('pad')
        testobj.extraopts['dont_save'] = True
        testobj.select_search_exclusions_if_requested = mock_select_2
        testobj.extraopts['output_file'] = 'ofile'
        testobj.doe()
        assert capsys.readouterr().out == (
                "called Afrift.setup_parameters\n"
                "called AfriftGui.add_item_to_searchlist with args ('vraag_zoek', 'find_me')\n"
                "called Finder.__init__ with args"
                f" {{'zoek': 'find_me', 'vervang': None, 'filelist': {testobj.p['filelist']}}}\n"
                "called Finder.setup_search\n"
                "called Afrift.select_search_exclusions_if_requested\n"
                "called AfriftGui.set_waitcursor with arg True\n"
                "called Finder.go\n"
                "called AfriftGui.set_waitcursor with arg False\n"
                "called Afrift.show_results\n"
                "called AfriftGui.get_checkbox_value with args ('vraag_exit',)\n")

        testobj.extraopts['no_gui'] = True
        testobj.extraopts['output_file'] = ''
        testobj.doe()
        assert capsys.readouterr().out == (
                "called Afrift.setup_parameters\n"
                "called AfriftGui.add_item_to_searchlist with args ('vraag_zoek', 'find_me')\n"
                "called Finder.__init__ with args"
                f" {{'zoek': 'find_me', 'vervang': None, 'filelist': {testobj.p['filelist']}}}\n"
                "called Finder.setup_search\n"
                "called Afrift.select_search_exclusions_if_requested\n"
                "called AfriftGui.set_waitcursor with arg True\n"
                "called Finder.go\n"
                "called AfriftGui.set_waitcursor with arg False\n"
                "called Afrift.show_results\n"
                "called AfriftGui.get_checkbox_value with args ('vraag_exit',)\n")

        testobj.extraopts['output_file'] = 'ofile'
        testobj.doe()
        assert capsys.readouterr().out == (
                "called Afrift.setup_parameters\n"
                "called AfriftGui.add_item_to_searchlist with args ('vraag_zoek', 'find_me')\n"
                "called Finder.__init__ with args"
                f" {{'zoek': 'find_me', 'vervang': None, 'filelist': {testobj.p['filelist']}}}\n"
                "called Finder.setup_search\n"
                "called Afrift.select_search_exclusions_if_requested\n"
                "called AfriftGui.set_waitcursor with arg True\n"
                "called Finder.go\n"
                "called AfriftGui.set_waitcursor with arg False\n"
                "called Afrift.show_results\n"
                "called AfriftGui.einde\n")

        testobj.extraopts['no_gui'] = False
        testobj.extraopts['output_file'] = ''
        testobj.p['vervang'] = ''
        testobj.doe()
        assert capsys.readouterr().out == (
                "called Afrift.setup_parameters\n"
                "called AfriftGui.add_item_to_searchlist with args ('vraag_zoek', 'find_me')\n"
                "called Finder.__init__ with args"
                f" {{'zoek': 'find_me', 'vervang': '', 'filelist': {testobj.p['filelist']}}}\n"
                "called Finder.setup_search\n"
                "called Afrift.select_search_exclusions_if_requested\n"
                "called AfriftGui.set_waitcursor with arg True\n"
                "called Finder.go\n"
                "called AfriftGui.set_waitcursor with arg False\n"
                "called Afrift.show_results\n"
                "called AfriftGui.get_checkbox_value with args ('vraag_exit',)\n")

        monkeypatch.setattr(MockGui, 'get_checkbox_value', MockGui.get_checkbox_value_2)
        testobj.p['vervang'] = None
        testobj.doe()
        assert capsys.readouterr().out == (
                "called Afrift.setup_parameters\n"
                "called AfriftGui.add_item_to_searchlist with args ('vraag_zoek', 'find_me')\n"
                "called Finder.__init__ with args"
                f" {{'zoek': 'find_me', 'vervang': None, 'filelist': {testobj.p['filelist']}}}\n"
                "called Finder.setup_search\n"
                "called Afrift.select_search_exclusions_if_requested\n"
                "called AfriftGui.set_waitcursor with arg True\n"
                "called Finder.go\n"
                "called AfriftGui.set_waitcursor with arg False\n"
                "called Afrift.show_results\n"
                "called AfriftGui.get_checkbox_value with args ('vraag_exit',)\n")

        testobj.p['vervang'] = ''
        testobj.doe()
        assert capsys.readouterr().out == (
                "called Afrift.setup_parameters\n"
                "called AfriftGui.add_item_to_searchlist with args ('vraag_zoek', 'find_me')\n"
                "called Finder.__init__ with args"
                f" {{'zoek': 'find_me', 'vervang': '', 'filelist': {testobj.p['filelist']}}}\n"
                "called Finder.setup_search\n"
                "called Afrift.select_search_exclusions_if_requested\n"
                "called AfriftGui.set_waitcursor with arg True\n"
                "called Finder.go\n"
                "called AfriftGui.set_waitcursor with arg False\n"
                "called Afrift.show_results\n"
                "called AfriftGui.get_checkbox_value with args ('vraag_exit',)\n"
                "called AfriftGui.einde\n")

    def test_setup_parameters(self, monkeypatch, capsys):
        """unittest for Afrift.setup_parameters
        """
        class MockGui:
            """stub
            """
            # def get_searchtext(self):
            #     print("called AfriftGui.get_searchtext")
            #     return 'find'
            # def get_replace_args(self):
            #     print('called AfriftGui.get_replace_args')
            #     return 'replace'
            # def get_search_attr(self):
            #     print('called AfriftGui.get_search_attr')
            #     return 'attr'
            # def get_types_to_search(self):
            #     print('called AfriftGui.get_types_to_search')
            #     return 'types'
            # def get_dir_to_search(self):
            #     print('called AfriftGui.get_dir_to_search')
            #     return 'dir'
            # def get_subdirs_to_search(self):
            #     print('called AfriftGui.get_subdirs_to_search')
            #     return True, True, 5
            # def get_backup(self):
            #     print('called AfriftGui.get_backup')
            #     return True
            # def get_ignore(self):
            #     print('called AfriftGui.get_ignore')
            #     return True
            # def get_context(self):
            #     print('called AfriftGui.get_context')
            #     return True
            def get_combobox_value(self, arg):
                print(f'called AfriftGui.get_combobox_value with arg {arg}')
                return 'xxx'
            def get_checkbox_value(self, arg):
                print(f'called AfriftGui.get_checkbox_value with arg {arg}')
                return True
            def get_spinbox_value(self, arg):
                print(f'called AfriftGui.get_spinbox_value with arg {arg}')
                return 2
        def mock_checkzoek(arg):
            print(f'called Afrift.checkzoek with arg {arg}')
            return 'message from checkzoek'
        def mock_checkzoek_2(arg):
            print(f'called Afrift.checkzoek with arg {arg}')
            return ''
        def mock_checkverv(*args):
            print('called Afrift.checkverv with args', args)
            return 'message from checkverv'
        def mock_checkverv_2(*args):
            print('called Afrift.checkverv with args', args)
            return ''
        def mock_checkattr(*args):
            print('called Afrift.checkattr with args', args)
            return 'message from checkattr'
        def mock_checkattr_2(*args):
            print('called Afrift.checkattr with args', args)
            return ''
        def mock_checktype(arg):
            print(f'called Afrift.checktype with arg {arg}')
            return 'message from checktype'
        def mock_checktype_2(arg):
            print(f'called Afrift.checktype with arg {arg}')
            return ''
        def mock_checkpath(arg):
            print(f'called Afrift.checkpath with arg {arg}')
            return 'message from checkpath'
        def mock_checkpath_2(arg):
            print(f'called Afrift.checkpath with arg {arg}')
            return ''
        def mock_get(self, arg):
            print(f'called AfriftGui.get_checkbox_value with arg {arg}')
            if arg == 'vraag_subs':
                return False
            return True
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.checkzoek = mock_checkzoek
        testobj.checkverv = mock_checkverv
        testobj.checkattr = mock_checkattr
        testobj.checktype = mock_checktype
        testobj.checkpath = mock_checkpath
        testobj.gui = MockGui()
        testobj.s = 'zz'
        testobj.p = {}
        testobj.vraag_zoek = 'vraag_zoek'
        testobj.vraag_verv = 'vraag_verv'
        testobj.vraag_leeg = 'vraag_leeg'
        testobj.vraag_regex = 'vraag_regex'
        testobj.vraag_case = 'vraag_case'
        testobj.vraag_woord = 'vraag_woord'
        testobj.vraag_types = 'vraag_types'
        testobj.vraag_dir = 'vraag_dir'
        testobj.vraag_subs = 'vraag_subs'
        testobj.vraag_leeg = 'vraag_leeg'
        testobj.vraag_links = 'vraag_links'
        testobj.vraag_diepte = 'vraag_diepte'
        testobj.vraag_backup = 'vraag_backup'
        testobj.vraag_uitsluit = 'vraag_uitsluit'
        testobj.vraag_context = 'vraag_context'
        assert testobj.setup_parameters() == 'message from checkzoek'
        assert testobj.p == {}
        assert testobj.s == 'zz'
        assert capsys.readouterr().out == (
                "called AfriftGui.get_combobox_value with arg vraag_zoek\n"
                "called Afrift.checkzoek with arg xxx\n")

        testobj.checkzoek = mock_checkzoek_2
        testobj.s = 'zz'
        testobj.p = {}
        assert testobj.setup_parameters() == 'message from checkverv'
        assert testobj.p == {}
        assert testobj.s == 'zz'
        assert capsys.readouterr().out == (
                "called AfriftGui.get_combobox_value with arg vraag_zoek\n"
                "called Afrift.checkzoek with arg xxx\n"
                "called AfriftGui.get_combobox_value with arg vraag_verv\n"
                "called AfriftGui.get_checkbox_value with arg vraag_leeg\n"
                "called Afrift.checkverv with args ('xxx', True)\n")
        testobj.checkverv = mock_checkverv_2
        testobj.s = 'zz'
        testobj.p = {}
        assert testobj.setup_parameters() == 'message from checkattr'
        assert testobj.p == {}
        assert testobj.s == 'zz'
        assert capsys.readouterr().out == (
                "called AfriftGui.get_combobox_value with arg vraag_zoek\n"
                "called Afrift.checkzoek with arg xxx\n"
                "called AfriftGui.get_combobox_value with arg vraag_verv\n"
                "called AfriftGui.get_checkbox_value with arg vraag_leeg\n"
                "called Afrift.checkverv with args ('xxx', True)\n"
                "called AfriftGui.get_checkbox_value with arg vraag_regex\n"
                "called AfriftGui.get_checkbox_value with arg vraag_case\n"
                "called AfriftGui.get_checkbox_value with arg vraag_woord\n"
                "called Afrift.checkattr with args (True, True, True)\n")
        testobj.checkattr = mock_checkattr_2
        testobj.apptype = 'not single'
        testobj.s = 'zz'
        testobj.p = {'filelist': ['xx']}
        assert testobj.setup_parameters() == 'message from checktype'
        assert testobj.p == {'filelist': ['xx']}
        assert testobj.s == 'zz'
        assert capsys.readouterr().out == (
                "called AfriftGui.get_combobox_value with arg vraag_zoek\n"
                "called Afrift.checkzoek with arg xxx\n"
                "called AfriftGui.get_combobox_value with arg vraag_verv\n"
                "called AfriftGui.get_checkbox_value with arg vraag_leeg\n"
                "called Afrift.checkverv with args ('xxx', True)\n"
                "called AfriftGui.get_checkbox_value with arg vraag_regex\n"
                "called AfriftGui.get_checkbox_value with arg vraag_case\n"
                "called AfriftGui.get_checkbox_value with arg vraag_woord\n"
                "called Afrift.checkattr with args (True, True, True)\n"
                "called AfriftGui.get_combobox_value with arg vraag_types\n"
                "called Afrift.checktype with arg xxx\n")
        testobj.checktype = mock_checktype_2
        testobj.s = 'zz'
        testobj.p = {'filelist': ['xx']}
        testobj.apptype = 'open'
        assert testobj.setup_parameters() == 'message from checkpath'
        assert testobj.p == {'filelist': ['xx']}
        assert testobj.s == 'zz'
        assert capsys.readouterr().out == (
                "called AfriftGui.get_combobox_value with arg vraag_zoek\n"
                "called Afrift.checkzoek with arg xxx\n"
                "called AfriftGui.get_combobox_value with arg vraag_verv\n"
                "called AfriftGui.get_checkbox_value with arg vraag_leeg\n"
                "called Afrift.checkverv with args ('xxx', True)\n"
                "called AfriftGui.get_checkbox_value with arg vraag_regex\n"
                "called AfriftGui.get_checkbox_value with arg vraag_case\n"
                "called AfriftGui.get_checkbox_value with arg vraag_woord\n"
                "called Afrift.checkattr with args (True, True, True)\n"
                "called AfriftGui.get_combobox_value with arg vraag_types\n"
                "called Afrift.checktype with arg xxx\n"
                "called AfriftGui.get_combobox_value with arg vraag_dir\n"
                "called Afrift.checkpath with arg xxx\n")
        testobj.checkpath = mock_checkpath_2
        testobj.s = 'zz'
        testobj.apptype = 'open'  # 'not single'
        testobj.p = {'filelist': ['xx']}
        assert testobj.setup_parameters() == ''
        assert testobj.p == {'filelist': ['xx'],
                             'subdirs': True, 'follow_symlinks': True, 'maxdepth': 2,
                             'backup': True, 'negeer': True, 'context': True}
        assert testobj.s == 'zz en onderliggende directories'
        assert capsys.readouterr().out == (
                "called AfriftGui.get_combobox_value with arg vraag_zoek\n"
                "called Afrift.checkzoek with arg xxx\n"
                "called AfriftGui.get_combobox_value with arg vraag_verv\n"
                "called AfriftGui.get_checkbox_value with arg vraag_leeg\n"
                "called Afrift.checkverv with args ('xxx', True)\n"
                "called AfriftGui.get_checkbox_value with arg vraag_regex\n"
                "called AfriftGui.get_checkbox_value with arg vraag_case\n"
                "called AfriftGui.get_checkbox_value with arg vraag_woord\n"
                "called Afrift.checkattr with args (True, True, True)\n"
                "called AfriftGui.get_combobox_value with arg vraag_types\n"
                "called Afrift.checktype with arg xxx\n"
                "called AfriftGui.get_combobox_value with arg vraag_dir\n"
                "called Afrift.checkpath with arg xxx\n"
                "called AfriftGui.get_checkbox_value with arg vraag_subs\n"
                "called AfriftGui.get_checkbox_value with arg vraag_links\n"
                "called AfriftGui.get_spinbox_value with arg vraag_diepte\n"
                "called AfriftGui.get_checkbox_value with arg vraag_backup\n"
                "called AfriftGui.get_checkbox_value with arg vraag_uitsluit\n"
                "called AfriftGui.get_checkbox_value with arg vraag_context\n")
        monkeypatch.setattr(testee.pathlib.Path, 'is_symlink', lambda x: False)
        testobj.s = 'zz'
        testobj.apptype = 'single-file'
        testobj.p = {'filelist': [testee.pathlib.Path('xx')]}
        assert testobj.setup_parameters() == ''
        assert testobj.p == {'filelist': [testee.pathlib.Path('xx')],
                             # 'subdirs': True, 'follow_symlinks': True, 'maxdepth': 2,
                             'backup': True, 'negeer': True, 'context': True}
        assert testobj.s == 'zz'
        assert capsys.readouterr().out == (
                "called AfriftGui.get_combobox_value with arg vraag_zoek\n"
                "called Afrift.checkzoek with arg xxx\n"
                "called AfriftGui.get_combobox_value with arg vraag_verv\n"
                "called AfriftGui.get_checkbox_value with arg vraag_leeg\n"
                "called Afrift.checkverv with args ('xxx', True)\n"
                "called AfriftGui.get_checkbox_value with arg vraag_regex\n"
                "called AfriftGui.get_checkbox_value with arg vraag_case\n"
                "called AfriftGui.get_checkbox_value with arg vraag_woord\n"
                "called Afrift.checkattr with args (True, True, True)\n"
                # "called AfriftGui.get_combobox_value with arg vraag_types\n"
                # "called Afrift.checktype with arg xxx\n"
                # "called AfriftGui.get_combobox_value with arg vraag_dir\n"
                # "called Afrift.checkpath with arg xxx\n"
                # "called AfriftGui.get_checkbox_value with arg vraag_subs\n"
                # "called AfriftGui.get_checkbox_value with arg vraag_links\n"
                # "called AfriftGui.get_spinbox_value with arg vraag_diepte\n"
                "called AfriftGui.get_checkbox_value with arg vraag_backup\n"
                "called AfriftGui.get_checkbox_value with arg vraag_uitsluit\n"
                "called AfriftGui.get_checkbox_value with arg vraag_context\n")
        monkeypatch.setattr(testee.pathlib.Path, 'is_symlink', lambda x: True)
        testobj.p = {'filelist': [testee.pathlib.Path('xx')]}
        assert testobj.setup_parameters() == ''
        assert testobj.p == {'filelist': [testee.pathlib.Path('xx')], 'follow_symlinks': True,
                             'backup': True, 'negeer': True, 'context': True}
        assert testobj.s == 'zz'
        assert capsys.readouterr().out == (
                "called AfriftGui.get_combobox_value with arg vraag_zoek\n"
                "called Afrift.checkzoek with arg xxx\n"
                "called AfriftGui.get_combobox_value with arg vraag_verv\n"
                "called AfriftGui.get_checkbox_value with arg vraag_leeg\n"
                "called Afrift.checkverv with args ('xxx', True)\n"
                "called AfriftGui.get_checkbox_value with arg vraag_regex\n"
                "called AfriftGui.get_checkbox_value with arg vraag_case\n"
                "called AfriftGui.get_checkbox_value with arg vraag_woord\n"
                "called Afrift.checkattr with args (True, True, True)\n"
                # "called AfriftGui.get_combobox_value with arg vraag_types\n"
                # "called Afrift.checktype with arg xxx\n"
                # "called AfriftGui.get_combobox_value with arg vraag_dir\n"
                # "called Afrift.checkpath with arg xxx\n"
                # "called AfriftGui.get_checkbox_value with arg vraag_subs\n"
                # "called AfriftGui.get_checkbox_value with arg vraag_links\n"
                # "called AfriftGui.get_spinbox_value with arg vraag_diepte\n"
                "called AfriftGui.get_checkbox_value with arg vraag_backup\n"
                "called AfriftGui.get_checkbox_value with arg vraag_uitsluit\n"
                "called AfriftGui.get_checkbox_value with arg vraag_context\n")
        monkeypatch.setattr(MockGui, 'get_checkbox_value', mock_get)
        testobj.apptype = 'single'
        testobj.s = 'zz'
        testobj.p = {}
        assert testobj.setup_parameters() == ''
        assert testobj.p == {'subdirs': False, 'follow_symlinks': True, 'maxdepth': 2,
                             'backup': True, 'negeer': True, 'context': True}
        assert testobj.s == 'zz'
        assert capsys.readouterr().out == (
                "called AfriftGui.get_combobox_value with arg vraag_zoek\n"
                "called Afrift.checkzoek with arg xxx\n"
                "called AfriftGui.get_combobox_value with arg vraag_verv\n"
                "called AfriftGui.get_checkbox_value with arg vraag_leeg\n"
                "called Afrift.checkverv with args ('xxx', True)\n"
                "called AfriftGui.get_checkbox_value with arg vraag_regex\n"
                "called AfriftGui.get_checkbox_value with arg vraag_case\n"
                "called AfriftGui.get_checkbox_value with arg vraag_woord\n"
                "called Afrift.checkattr with args (True, True, True)\n"
                "called AfriftGui.get_combobox_value with arg vraag_types\n"
                "called Afrift.checktype with arg xxx\n"
                # "called AfriftGui.get_combobox_value with arg vraag_dir\n"
                # "called Afrift.checkpath with arg xxx\n"
                "called AfriftGui.get_checkbox_value with arg vraag_subs\n"
                "called AfriftGui.get_checkbox_value with arg vraag_links\n"
                "called AfriftGui.get_spinbox_value with arg vraag_diepte\n"
                "called AfriftGui.get_checkbox_value with arg vraag_backup\n"
                "called AfriftGui.get_checkbox_value with arg vraag_uitsluit\n"
                "called AfriftGui.get_checkbox_value with arg vraag_context\n")

    def test_checkzoek(self, monkeypatch, capsys):
        """unittest for Afrift.checkzoek
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.mru_items = {'zoek': ['xxx', 'yyy']}
        testobj.s = 'zz'
        testobj.p = {}
        assert testobj.checkzoek('') == "Kan niet zoeken zonder zoekargument"

        assert testobj.checkzoek('text') == ""
        assert testobj.mru_items['zoek'] == ['text', 'xxx', 'yyy']
        assert testobj.s == 'zzzoeken naar text'
        assert testobj.p['zoek'] == 'text'

        testobj.mru_items = {'zoek': ['xxx', 'yyy']}
        testobj.s = 'zz'
        testobj.p = {}
        assert testobj.checkzoek('xxx') == ""
        assert testobj.mru_items['zoek'] == ['xxx', 'yyy']
        assert testobj.s == 'zzzoeken naar xxx'
        assert testobj.p['zoek'] == 'xxx'

    def test_checkverv(self, monkeypatch, capsys):
        """unittest for Afrift.checkverv
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.mru_items = {'verv': ['xxx', 'yyy']}
        testobj.s = 'zz'
        testobj.p = {}
        assert testobj.checkverv('', '') == ""
        assert testobj.mru_items['verv'] == ['xxx', 'yyy']
        assert testobj.s == 'zz'
        assert testobj.p['vervang'] is None

        testobj.mru_items = {'verv': ['xxx', 'yyy']}
        testobj.s = 'zz'
        testobj.p = {}
        assert testobj.checkverv('text', False) == ""
        assert testobj.mru_items['verv'] == ['text', 'xxx', 'yyy']
        assert testobj.s == 'zz\nen vervangen door text'
        assert testobj.p['vervang'] == 'text'

        testobj.mru_items = {'verv': ['xxx', 'yyy']}
        testobj.s = 'zz'
        testobj.p = {}
        assert testobj.checkverv('xxx', False) == ""
        assert testobj.mru_items['verv'] == ['xxx', 'yyy']
        assert testobj.s == 'zz\nen vervangen door xxx'
        assert testobj.p['vervang'] == 'xxx'

        testobj.mru_items = {'verv': ['xxx', 'yyy']}
        testobj.s = 'zz'
        testobj.p = {}
        assert testobj.checkverv('', True) == ""
        assert testobj.mru_items['verv'] == ['xxx', 'yyy']
        assert testobj.s == 'zz\nen weggehaald'
        assert testobj.p['vervang'] == ''

    def test_checkattr(self, monkeypatch, capsys):
        """unittest for Afrift.checkattr
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.s = 'zz'
        testobj.p = {}
        assert testobj.checkattr('', False, False) == ""
        assert testobj.s == 'zz'
        assert testobj.p == {'regexp': '', 'case': False, 'woord': False}
        testobj.p = {}
        assert testobj.checkattr('xx', False, False) == ""
        assert testobj.s == 'zz (regular expression)'
        assert testobj.p == {'regexp': 'xx', 'case': False, 'woord': False}
        testobj.s = 'zz'
        testobj.p = {}
        assert testobj.checkattr('', True, True) == ""
        assert testobj.s == 'zz (case-sensitive, hele woorden)'
        assert testobj.p == {'regexp': '', 'case': True, 'woord': True}

    def test_checktype(self, monkeypatch, capsys):
        """unittest for Afrift.checktype
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.mru_items = {'types': ['x', 'y']}
        testobj.s = 'zz'
        testobj.p = {}
        assert testobj.checktype('') == ""
        assert testobj.mru_items['types'] == ['x', 'y']
        assert testobj.s == 'zz'
        assert testobj.p['extlist'] == []

        testobj.mru_items = {'types': ['x', 'y']}
        testobj.s = 'zz'
        testobj.p = {}
        assert testobj.checktype('x') == ""
        assert testobj.mru_items['types'] == ['x', 'y']
        assert testobj.s == 'zz\nin bestanden van type x'
        assert testobj.p['extlist'] == ['x']

        testobj.mru_items = {'types': ['x', 'y']}
        testobj.s = 'zz'
        testobj.p = {}
        assert testobj.checktype('a , b, c') == ""
        assert testobj.mru_items['types'] == ['a , b, c', 'x', 'y']
        assert testobj.s == 'zz\nin bestanden van type a , b, c'
        assert testobj.p['extlist'] == ['a', 'b', 'c']

    def test_checkpath(self, monkeypatch, capsys):
        """unittest for Afrift.checkpath
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.checkpath('') == (
                "Ik wil wel graag weten in welke directory ik moet (beginnen met) zoeken")
        assert testobj.checkpath('xxx') == "De opgegeven directory bestaat niet"

        testobj.mru_items = {'dirs': ['']}
        testobj.s = 'xx'
        testobj.p = {}
        assert testobj.checkpath('/home') == ""
        assert testobj.mru_items['dirs'] == ['/home', '']
        assert testobj.p['filelist'] == [pathlib.Path('/home')]
        assert testobj.s == 'xx\nin /home'

    def test_write_to_ini(self, monkeypatch, capsys, tmp_path):
        """unittest for Afrift.write_to_ini
        """
        loc = tmp_path / 'test'
        mfile = loc / 'mru'
        ofile = loc / 'opts'
        def mock_get(arg):
            print(f"called get_iniloc with arg '{arg}'")
            return loc, mfile, ofile
        def mock_dump(*args, **kwargs):
            print('called json.dump with args', args, kwargs)
        monkeypatch.setattr(testee, 'get_iniloc', mock_get)
        monkeypatch.setattr(testee.json, 'dump', mock_dump)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.mru_items = {'q': ['q1', 'q2'], 'r': ['r1', 'r2']}
        testobj.save_options_keys = (('x', 'x_desc'), ('y', 'y_desc'))
        testobj.p = {'x': False, 'y': True}
        testobj.outopts = {'a': True, 'b': False}
        testobj.extraopts = {'dont_save': True}
        monkeypatch.setattr(testee.pathlib.Path, 'exists', lambda *x: False)
        testobj.write_to_ini()
        assert capsys.readouterr().out == ""
        testobj.extraopts = {'dont_save': False}
        testobj.write_to_ini()
        assert capsys.readouterr().out == (
                "called get_iniloc with arg 'None'\n"
                "called json.dump with args ({'q': ['q1', 'q2'], 'r': ['r1', 'r2']},"
                f" <_io.TextIOWrapper name='{mfile}' mode='w' encoding='UTF-8'>) {{'indent': 4}}\n"
                "called json.dump with args ({'x': False, 'y': True, 'a': True, 'b': False},"
                f" <_io.TextIOWrapper name='{ofile}' mode='w' encoding='UTF-8'>) {{'indent': 4}}\n")
        monkeypatch.setattr(testee.pathlib.Path, 'exists', lambda *x: True)
        testobj.write_to_ini(path='xx')
        assert capsys.readouterr().out == (
                "called get_iniloc with arg 'xx'\n"
                "called json.dump with args ({'q': ['q1', 'q2'], 'r': ['r1', 'r2']},"
                f" <_io.TextIOWrapper name='{mfile}' mode='w' encoding='UTF-8'>) {{'indent': 4}}\n"
                "called json.dump with args ({'x': False, 'y': True, 'a': True, 'b': False},"
                f" <_io.TextIOWrapper name='{ofile}' mode='w' encoding='UTF-8'>) {{'indent': 4}}\n")

    def test_determine_common(self, monkeypatch, capsys):
        """unittest for Afrift.determine_common
        """
        orig_commonpath = testee.os.path.commonpath
        def mock_commonpath(*args):
            print('called os.path.commonpath with args', args)
            monkeypatch.setattr(testee.os.path, 'commonpath', orig_commonpath)
            return 'qqq'
        def mock_commonpath_2(*args):
            print('called os.path.commonpath with args', args)
            monkeypatch.setattr(testee.os.path, 'commonpath', orig_commonpath)
            return 'ppp/qqq'
        def mock_isfile(arg):
            print(f"called os.path.isfile with arg '{arg}')")
            return False
        def mock_isfile_2(arg):
            print(f"called os.path.isfile with arg '{arg}')")
            return True
        monkeypatch.setattr(testee.os.path, 'commonpath', mock_commonpath)
        monkeypatch.setattr(testee.os.path, 'isfile', mock_isfile)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.p = {'filelist': [testee.pathlib.Path('xxx'), testee.pathlib.Path('yyy')]}
                     # 'pad': testee.pathlib.Path('zzz')}
        testobj.apptype = ''
        assert testobj.determine_common() == f"xxx{testee.os.sep}"
        assert capsys.readouterr().out == ""
        testobj.apptype = 'single-file'
        assert testobj.determine_common() == testee.pathlib.PosixPath("xxx")
        assert capsys.readouterr().out == ""
        testobj.apptype = 'single-dir'
        assert testobj.determine_common() == "xxx/"
        assert capsys.readouterr().out == ""
        testobj.apptype = 'multi'
        assert testobj.determine_common() == "qqq/"
        assert capsys.readouterr().out == ("called os.path.commonpath with args (['xxx', 'yyy'],)\n"
                                           "called os.path.isfile with arg 'qqq')\n")
        monkeypatch.setattr(testee.os.path, 'commonpath', mock_commonpath_2)
        monkeypatch.setattr(testee.os.path, 'isfile', mock_isfile_2)
        assert testobj.determine_common() == "ppp/"
        assert capsys.readouterr().out == ("called os.path.commonpath with args (['xxx', 'yyy'],)\n"
                                           "called os.path.isfile with arg 'ppp/qqq')\n")

    def test_select_search_exclusions_if_requested(self, monkeypatch, capsys):
        """unittest for Afrift.select_search_exclusions_if_requested
        """
        class MockSelectNames:
            """stub
            """
            def __init__(self, *args, **kwargs):
                print('called Selectnames.__init__ with args', args, kwargs)
                self.do_files = kwargs.get('files', True)
            def show(self):
                print('called Selectnames.show')
                return False, []
            def show_2(self):
                print('called Selectnames.show')
                return True, ['aaa', 'bbb']
            def show_3(self):
                nonlocal showcounter
                print('called Selectnames.show')
                if not self.do_files:
                    return True, ['aaa', 'bbb']
                showcounter += 1
                if showcounter == 1:
                    return False, []
                return True, ['aaa', 'bbb']
        def mock_remove(names):
            print(f'called Afrift.remove_files_in_selected_dirs with arg {names}')
        def mock_get(arg):
            print(f'called AfriftGui.get_checkbox_value with arg {arg}')
            return False
        def mock_get_2(arg):
            print(f'called AfriftGui.get_checkbox_value with arg {arg}')
            if arg == 'ask_skipdirs':
                return True
            return False
        def mock_get_3(arg):
            print(f'called AfriftGui.get_checkbox_value with arg {arg}')
            if arg == 'ask_skipdirs':
                return False
            return True
        def mock_get_4(arg):
            print(f'called AfriftGui.get_checkbox_value with arg {arg}')
            return True
        monkeypatch.setattr(testee, 'SelectNames', MockSelectNames)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.remove_files_in_selected_dirs = mock_remove
        testobj.zoekvervang = types.SimpleNamespace(dirnames=[], filenames=[])
        testobj.ask_skipdirs = 'ask_skipdirs'
        testobj.ask_skipfiles = 'ask_skipfiles'
        testobj.gui = types.SimpleNamespace(get_checkbox_value=mock_get)
        assert not testobj.select_search_exclusions_if_requested()
        assert capsys.readouterr().out == (
                "called AfriftGui.get_checkbox_value with arg ask_skipdirs\n"
                "called AfriftGui.get_checkbox_value with arg ask_skipfiles\n")

        testobj.zoekvervang.dirnames = ['xxx', 'yyy']
        testobj.gui.get_checkbox_value = mock_get_2
        assert testobj.select_search_exclusions_if_requested()
        assert testobj.zoekvervang.filenames == []
        assert capsys.readouterr().out == (
                "called AfriftGui.get_checkbox_value with arg ask_skipdirs\n"
                "called AfriftGui.get_checkbox_value with arg ask_skipfiles\n"
                f"called Selectnames.__init__ with args ({testobj},) {{'files': False}}\n"
                "called Selectnames.show\n")

        testobj.zoekvervang.dirnames = ['xxx', 'yyy']
        testobj.zoekvervang.filenames = ['aaa', 'bbb', 'ccc', 'ddd']
        testobj.gui.get_checkbox_value = mock_get_3
        assert testobj.select_search_exclusions_if_requested()
        assert testobj.zoekvervang.filenames == ['aaa', 'bbb', 'ccc', 'ddd']
        assert capsys.readouterr().out == (
                "called AfriftGui.get_checkbox_value with arg ask_skipdirs\n"
                "called AfriftGui.get_checkbox_value with arg ask_skipfiles\n"
                f"called Selectnames.__init__ with args ({testobj},) {{}}\n"
                "called Selectnames.show\n")

        monkeypatch.setattr(MockSelectNames, 'show', MockSelectNames.show_2)
        monkeypatch.setattr(testee, 'SelectNames', MockSelectNames)
        testobj.zoekvervang.dirnames = ['xxx', 'yyy']
        testobj.zoekvervang.filenames = []
        testobj.gui.get_checkbox_value = mock_get_2
        assert not testobj.select_search_exclusions_if_requested()
        assert capsys.readouterr().out == (
                "called AfriftGui.get_checkbox_value with arg ask_skipdirs\n"
                "called AfriftGui.get_checkbox_value with arg ask_skipfiles\n"
                f"called Selectnames.__init__ with args ({testobj},) {{'files': False}}\n"
                "called Selectnames.show\n"
                "called Afrift.remove_files_in_selected_dirs with arg ['aaa', 'bbb']\n")

        testobj.zoekvervang.dirnames = ['xxx', 'yyy']
        testobj.zoekvervang.filenames = ['aaa', 'bbb', 'ccc', 'ddd']
        testobj.gui.get_checkbox_value = mock_get_3
        assert not testobj.select_search_exclusions_if_requested()
        assert testobj.zoekvervang.filenames == ['aaa', 'bbb']
        assert capsys.readouterr().out == (
                "called AfriftGui.get_checkbox_value with arg ask_skipdirs\n"
                "called AfriftGui.get_checkbox_value with arg ask_skipfiles\n"
                f"called Selectnames.__init__ with args ({testobj},) {{}}\n"
                "called Selectnames.show\n")

        testobj.zoekvervang.dirnames = ['xxx', 'yyy']
        testobj.zoekvervang.filenames = ['aaa', 'bbb', 'ccc', 'ddd']
        testobj.gui.get_checkbox_value = mock_get_4

        showcounter = 0
        monkeypatch.setattr(MockSelectNames, 'show', MockSelectNames.show_3)
        assert not testobj.select_search_exclusions_if_requested()
        assert testobj.zoekvervang.filenames == ['aaa', 'bbb']
        assert capsys.readouterr().out == (
                "called AfriftGui.get_checkbox_value with arg ask_skipdirs\n"
                "called AfriftGui.get_checkbox_value with arg ask_skipfiles\n"
                f"called Selectnames.__init__ with args ({testobj},) {{'files': False}}\n"
                "called Selectnames.show\n"
                "called Afrift.remove_files_in_selected_dirs with arg ['aaa', 'bbb']\n"
                f"called Selectnames.__init__ with args ({testobj},) {{}}\n"
                "called Selectnames.show\n"
                f"called Selectnames.__init__ with args ({testobj},) {{'files': False}}\n"
                "called Selectnames.show\n"
                "called Afrift.remove_files_in_selected_dirs with arg ['aaa', 'bbb']\n"
                f"called Selectnames.__init__ with args ({testobj},) {{}}\n"
                "called Selectnames.show\n")

    def test_remove_files_in_selected_dirs(self, monkeypatch, capsys):
        """unittest for Afrift.remove_files_in_selected_dirs
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.zoekvervang = types.SimpleNamespace(filenames=[testee.pathlib.Path('aaa/xxx'),
                                                               testee.pathlib.Path('aaa/yyy'),
                                                               testee.pathlib.Path('bbb/xxx'),
                                                               testee.pathlib.Path('bbb/yyy'),
                                                               testee.pathlib.Path('ccc/xxx'),
                                                               testee.pathlib.Path('ccc/yyy')])
        testobj.remove_files_in_selected_dirs(['aaa', 'ccc'])
        assert testobj.zoekvervang.filenames == [testee.pathlib.Path('bbb/xxx'),
                                                 testee.pathlib.Path('bbb/yyy')]

    def test_show_results(self, monkeypatch, capsys, tmp_path):
        """unittest for Afrift.show_results
        """
        class MockResults:
            """stub
            """
            def __init__(self, *args):
                print('called Results.__init__ with args', args)
            def get_results(self):
                print('called Results.get_results')
                return ['xx', 'yy']
            def show(self):
                print('called Results.show')
        def mock_determine():
            print('called Afrift.determine_common')
            return 'common_root'
        def mock_meld(*args):
            print('called AfriftGui.meld with args', args)
        outfilename = tmp_path / 'show_results.txt'
        monkeypatch.setattr(testee, 'Results', MockResults)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.determine_common = mock_determine
        testobj.gui = types.SimpleNamespace(meld=mock_meld)
        testobj.resulttitel = 'showing results'
        testobj.zoekvervang = types.SimpleNamespace(rpt=['1 regel'])
        testobj.zoekvervang.ok = True
        testobj.extraopts['output_file'] = None
        testobj.show_results()
        assert capsys.readouterr().out == (
                "called AfriftGui.meld with args ('showing results', 'No results')\n")

        testobj.zoekvervang.ok = False
        testobj.show_results()
        assert capsys.readouterr().out == (
                "called AfriftGui.meld with args ('showing results', 'No results')\n")

        testobj.extraopts['output_file'] = outfilename.open('w')
        testobj.show_results()
        assert outfilename.read_text() == 'No results\n'
        assert capsys.readouterr().out == ''

        testobj.zoekvervang.rpt = ['header', 'result line']
        testobj.extraopts['output_file'] = None
        testobj.show_results()
        assert capsys.readouterr().out == (
                "called Afrift.determine_common\n"
                f"called Results.__init__ with args ({testobj}, 'common_root')\n"
                "called Results.show\n")

        testobj.extraopts['output_file'] = outfilename.open('w')
        testobj.show_results()
        assert outfilename.read_text() == 'xx\nyy\n'
        assert capsys.readouterr().out == (
                "called Afrift.determine_common\n"
                f"called Results.__init__ with args ({testobj}, 'common_root')\n"
                "called Results.get_results\n")


class TestSelectNames:
    """unittest for base.SelectNames
    """
    def setup_testobj(self, monkeypatch, capsys):
        """stub for base.SelectNames object

        create the object skipping the normal initialization
        intercept messages during creation
        return the object so that other methods can be monkeypatched in the caller
        """
        class MockParent:
            "stub for base.Afrift"
        def mock_init(self, *args):
            """stub
            """
            print('called SelectNames.__init__ with args', args)
        parent = MockParent()
        monkeypatch.setattr(testee.SelectNames, '__init__', mock_init)
        testobj = testee.SelectNames(parent)
        assert capsys.readouterr().out == f"called SelectNames.__init__ with args ({parent},)\n"
        testobj.parent = parent
        testobj.gui = MockSelectNamesGui()
        assert capsys.readouterr().out == "called SelectNamesGui.__init__ with args ()\n"
        return testobj

    def test_init(self, monkeypatch, capsys):
        """unittest for SelectNames.__init__
        """
        monkeypatch.setattr(testee, 'iconame', 'find.ico')
        monkeypatch.setattr(testee, 'SelectNamesGui', MockSelectNamesGui)
        parent = types.SimpleNamespace(title='app title')
        parent.names = [testee.pathlib.Path('xx'), testee.pathlib.Path('yy')]
        testobj = testee.SelectNames(parent)
        assert testobj.do_files
        assert testobj.parent == parent
        assert testobj.title == 'app title - file list'
        assert testobj.iconame == 'find.ico'
        assert testobj.names == {'xx': testee.pathlib.Path('xx'), 'yy': testee.pathlib.Path('yy')}
        assert capsys.readouterr().out == (
                f"called SelectNamesGui.__init__ with args ({parent}, {testobj})\n"
                "called SelectNamesGui.setup_screen\n"
                "called SelectNamesGui.add_line\n"
                "called SelectNamesGui.add_text_to_line with args"
                " ('line', 'Selecteer de bestanden die je *niet* wilt verwerken')\n"
                "called SelectNamesGui.add_line\n"
                "called SelectNamesGui.add_checkbox_to_line with args"
                f" ('line', 'Select/Unselect All', {testobj.gui.select_all})\n"
                "called SelectNamesGui.add_button_to_line with args"
                f" ('line', 'Invert selection', {testobj.gui.invert_selection})\n"
                "called SelectNamesGui.add_line\n"
                "called SelectNamesGui.add_selectionlist with args ('line', ['xx', 'yy'])\n"
                "called SelectNamesGui.add_line\n"
                "called SelectNamesGui.add_buttons with args ('line',"
                f" [('&Terug', {testobj.gui.cancel}), ('&Klaar', {testobj.gui.confirm})])\n")

        testobj = testee.SelectNames(parent, files=False)
        assert not testobj.do_files
        assert testobj.parent == parent
        assert testobj.title == 'app title - file list'
        assert testobj.iconame == 'find.ico'
        assert testobj.names == []
        assert capsys.readouterr().out == (
                f"called SelectNamesGui.__init__ with args ({parent}, {testobj})\n"
                "called SelectNamesGui.setup_screen\n"
                "called SelectNamesGui.add_line\n"
                "called SelectNamesGui.add_text_to_line with args"
                " ('line', 'Selecteer de directories die je *niet* wilt verwerken')\n"
                "called SelectNamesGui.add_line\n"
                "called SelectNamesGui.add_checkbox_to_line with args"
                f" ('line', 'Select/Unselect All', {testobj.gui.select_all})\n"
                "called SelectNamesGui.add_button_to_line with args"
                f" ('line', 'Invert selection', {testobj.gui.invert_selection})\n"
                "called SelectNamesGui.add_line\n"
                "called SelectNamesGui.add_selectionlist with args ('line', ['xx', 'yy'])\n"
                "called SelectNamesGui.add_line\n"
                "called SelectNamesGui.add_buttons with args ('line',"
                f" [('&Terug', {testobj.gui.cancel}), ('&Klaar', {testobj.gui.confirm})])\n")

    def test_show(self, monkeypatch, capsys):
        """unittest for SelectNames.show
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.names = ['x', 'y']
        testobj.show()
        assert capsys.readouterr().out == "called SelectNamesGui.go\n"


class TestCSVTextBuf:
    """unittest for base.CSVTextBuf
    """
    def setup_testobj(self, monkeypatch, capsys):
        """stub for base.CSVTextBuf object

        create the object skipping the normal initialization
        intercept messages during creation
        return the object so that other methods can be monkeypatched in the caller
        """
        def mock_init(self, *args):
            print('called CSVTextBuf.__init__ with args', args)
        monkeypatch.setattr(testee.CSVTextBuf, '__init__', mock_init)
        testobj = testee.CSVTextBuf()
        assert capsys.readouterr().out == 'called CSVTextBuf.__init__ with args ()\n'
        return testobj

    def test_init(self, monkeypatch, capsys):
        """unittest for CSVTextBuf.__init__
        """
        class MockWriter:
            """stub
            """
            def __init__(self, *args, **kwargs):
                print('called csv.writer with args', args, kwargs)
        def mock_writer(*args, **kwargs):
            return MockWriter(*args, **kwargs)
        monkeypatch.setattr(testee.csv, 'writer', mock_writer)
        testobj = testee.CSVTextBuf('apptype', False)
        assert testobj.apptype == 'apptype'
        assert not testobj.toonpad
        assert isinstance(testobj.textbuf, testee.io.StringIO)
        assert isinstance(testobj.writer, MockWriter)
        assert testobj.header == ['File', 'Line', 'Context', 'Result']
        assert capsys.readouterr().out == (
                f"called csv.writer with args ({testobj.textbuf},) {{'dialect': 'unix'}}\n")

        testobj = testee.CSVTextBuf('apptype', True)
        assert testobj.apptype == 'apptype'
        assert testobj.toonpad
        assert isinstance(testobj.textbuf, testee.io.StringIO)
        assert isinstance(testobj.writer, MockWriter)
        assert testobj.header == ['Path/file', 'Line', 'Context', 'Result']
        assert capsys.readouterr().out == (
                f"called csv.writer with args ({testobj.textbuf},) {{'dialect': 'unix'}}\n")

    def test_write_line(self, monkeypatch, capsys):
        """unittest for CSVTextBuf.write_line
        """
        class MockWriter:
            """stub
            """
            def writerow(self, arg):
                print(f'called csv.writer.writerow with arg {arg}')
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.header = ['aa', 'bb', 'xx', 'yy', 'zz']
        testobj.writer = MockWriter()
        testobj.toonpad = False
        testobj.apptype = ''
        testobj.write_line(['p r. q', 'r', 's', 't'])
        assert capsys.readouterr().out == (
                "called csv.writer.writerow with arg ['aa', 'bb', 'xx', 'yy', 'zz']\n"
                "called csv.writer.writerow with arg ['p', 'q', 'r', 's', 't']\n")

        testobj.header = ['aa', 'bb', 'xx', 'yy', 'zz']
        testobj.writer = MockWriter()
        testobj.toonpad = False
        testobj.apptype = 'single-file'
        testobj.write_line(['p r. q', 'r', 's'])
        assert capsys.readouterr().out == (
                "called csv.writer.writerow with arg ['bb', 'yy', 'zz']\n"
                "called csv.writer.writerow with arg ['q', 'r', 's']\n")

        testobj.header = None
        testobj.writer = MockWriter()
        testobj.toonpad = False
        testobj.apptype = 'single-file'
        testobj.write_line(['p r. q', 'r', 's'])
        assert capsys.readouterr().out == "called csv.writer.writerow with arg ['q', 'r', 's']\n"

        testobj.header = ['aa', 'bb', 'xx', 'yy', 'zz']
        testobj.writer = MockWriter()
        testobj.toonpad = True
        testobj.apptype = 'single-file'
        testobj.write_line(['p r. q', 'r', 's'])
        assert capsys.readouterr().out == (
                "called csv.writer.writerow with arg ['aa', 'bb', 'yy', 'zz']\n"
                "called csv.writer.writerow with arg ['p', 'q', 'r', 's']\n")

        testobj.header = None
        testobj.writer = MockWriter()
        testobj.toonpad = True
        testobj.apptype = 'single-file'
        testobj.write_line(['p r. q', 'r', 's'])
        assert capsys.readouterr().out == (
                "called csv.writer.writerow with arg ['p', 'q', 'r', 's']\n")

    def test_get_contents_and_close(self, monkeypatch, capsys):
        """unittest for CSVTextBuf.get_contents_and_close
        """
        class MockBuf:
            """stub
            """
            def getvalue(self):
                print('called textbuf.getValue')
                return 'aaa\nbbb\nccc'
            def close(self):
                print('called textbuf.close')
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.textbuf = MockBuf()
        assert testobj.get_contents_and_close() == ['aaa', 'bbb', 'ccc']
        assert capsys.readouterr().out == ("called textbuf.getValue\n"
                                           "called textbuf.close\n")


class TestResults:
    """unittest for base.Results
    """
    def setup_testobj(self, monkeypatch, capsys):
        """stub for base.Results object

        create the object skipping the normal initialization
        intercept messages during creation
        return the object so that other methods can be monkeypatched in the caller
        """
        def mock_init(self, *args):
            """stub
            """
            print('called Results.__init__ with args', args)
        monkeypatch.setattr(testee.Results, '__init__', mock_init)
        parent = MockAfrift()
        parent.p = {}
        parent.zoekvervang = types.SimpleNamespace()
        testobj = testee.Results(parent)
        assert capsys.readouterr().out == ("called Afrift.__init__ \n"
                                           f'called Results.__init__ with args ({parent},)\n')
        testobj.parent = parent
        testobj.gui = MockResultsGui(parent, self)
        assert capsys.readouterr().out == (
                f'called ResultsGui.__init__ with args ({parent}, {self})\n')
        testobj.results = []
        return testobj

    def test_init(self, monkeypatch, capsys):
        """unittest for Results.__init__
        """
        def mock_build(self):
            print('called TestResults.build_list')
        parent = MockAfrift()
        assert capsys.readouterr().out == "called Afrift.__init__ \n"

        parent.p = {'context': True, 'vervang': 'xxx'}
        parent.apptype = 'single-file'
        parent.zoekvervang = types.SimpleNamespace(rpt=['gezocht en/of vervangen', 'namelijk 2'])
        parent.outopts = {'as_csv': 'csv', 'summarize': 'sum', 'full_path': 'pth'}
        monkeypatch.setattr(testee.Results, 'build_list', mock_build)
        monkeypatch.setattr(testee, 'ResultsGui', MockResultsGui)
        testobj = testee.Results(parent)
        assert testobj.parent == parent
        assert testobj.common == ''
        assert testobj.show_context
        assert testobj.results == []
        assert testobj.titel == 'Regel'
        assert isinstance(testobj.gui, testee.ResultsGui)
        assert capsys.readouterr().out == (
                f"called ResultsGui.__init__ with args ({parent}, {testobj})\n"
                "called ResultsGui.add_line\n"
                "called ResultsGui.add_text_to_line with args"
                " ('line', 'gezocht en/of 2 vervangen')\n"
                "called ResultsGui.add_buttons_to_line with args ('line',"
                f" (('Go to selected result', {testobj.gui.to_result}, True),)) {{'end': True}}\n"
                "called TestResults.build_list\n"
                "called ResultsGui.add_line\n"
                "called ResultsGui.add_buttons_to_line with args"
                f" ('line', (('&Klaar', {testobj.gui.klaar}, True),)) {{}}\n"
                "called ResultsGui.finalize_display\n")
        parent.p['vervang'] = ''
        testobj = testee.Results(parent)
        assert testobj.parent == parent
        assert testobj.common == ''
        assert testobj.show_context
        assert testobj.results == []
        assert testobj.titel == 'Regel'
        assert isinstance(testobj.gui, testee.ResultsGui)
        assert capsys.readouterr().out == (
            f"called ResultsGui.__init__ with args ({parent}, {testobj})\n"
            "called ResultsGui.add_line\n"
            "called ResultsGui.add_text_to_line with args"
            " ('line', 'gezocht en/of vervangen (1 items)')\n"
            "called ResultsGui.add_buttons_to_line with args ('line',"
            f" (('Go to selected result', {testobj.gui.to_result}, True),)) {{'end': True}}\n"
            "called TestResults.build_list\n"
            "called ResultsGui.add_line\n"
            "called ResultsGui.add_results_list with args"
            f" ('line', ('Regel', 'Context', 'Tekst'), (('Help', 'F1', {testobj.help})"
            f", ('&Goto Result', 'Ctrl+G', {testobj.gui.to_result})), [])\n"
            "called ResultsGui.add_line\n"
            "called ResultsGui.add_buttons_to_line with args ('line',"
            f" (('&Klaar', {testobj.gui.klaar}, True),)) {{}}\n"
            "called ResultsGui.add_buttons_to_line with args ('line',"
            f" (('&Repeat Search', {testobj.refresh}, False),"
            f" ('&Zoek anders', {testobj.zoek_anders}, True),"
            f" ('Vervang in &Selectie', {testobj.vervang_in_sel}, False),"
            f" ('Vervang &Alles', {testobj.vervang_alles}, False))) {{}}\n"
            "called ResultsGui.add_line\n"
            "called ResultsGui.add_text_to_line with args ('line', 'Output:')\n"
            "called ResultsGui.add_buttons_to_line with args ('line',"
            f" (('Copy to &File', {testobj.kopie}, True),"
            f" ('Copy to &Clipboard', {testobj.to_clipboard}, True))) {{}}\n"
            "called ResultsGui.add_checkbox_to_line with args ('line', 'comma-delimited', 'csv')\n"
            "called ResultsGui.add_checkbox_to_line with args ('line', 'summarized', 'sum')\n"
            "called ResultsGui.add_checkbox_to_line with args ('line', 'toon directorypad', 'pth')\n"
            "called ResultsGui.disable_widget with arg checkbox\n"
            "called ResultsGui.finalize_display\n")
        parent.p['vervang'] = 'xx'
        parent.apptype = 'xxx'
        testobj = testee.Results(parent)
        assert testobj.titel == 'File/Regel'
        assert capsys.readouterr().out == (
            f"called ResultsGui.__init__ with args ({parent}, {testobj})\n"
            "called ResultsGui.add_line\n"
            "called ResultsGui.add_text_to_line with args"
            " ('line', 'gezocht en/of vervangen (1 items)')\n"
            "called ResultsGui.add_buttons_to_line with args ('line',"
            f" (('Go to selected result', {testobj.gui.to_result}, True),)) {{'end': True}}\n"
            "called TestResults.build_list\n"
            "called ResultsGui.add_line\n"
            "called ResultsGui.add_results_list with args"
            f" ('line', ('File/Regel', 'Context', 'Tekst'), (('Help', 'F1', {testobj.help})"
            f", ('&Goto Result', 'Ctrl+G', {testobj.gui.to_result})), [])\n"
            "called ResultsGui.add_line\n"
            "called ResultsGui.add_buttons_to_line with args ('line',"
            f" (('&Klaar', {testobj.gui.klaar}, True),)) {{}}\n"
            "called ResultsGui.add_buttons_to_line with args ('line',"
            f" (('&Repeat Search', {testobj.refresh}, True),"
            f" ('&Zoek anders', {testobj.zoek_anders}, True),"
            f" ('Vervang in &Selectie', {testobj.vervang_in_sel}, True),"
            f" ('Vervang &Alles', {testobj.vervang_alles}, True))) {{}}\n"
            "called ResultsGui.add_line\n"
            "called ResultsGui.add_text_to_line with args ('line', 'Output:')\n"
            "called ResultsGui.add_buttons_to_line with args ('line',"
            f" (('Copy to &File', {testobj.kopie}, True),"
            f" ('Copy to &Clipboard', {testobj.to_clipboard}, True))) {{}}\n"
            "called ResultsGui.add_checkbox_to_line with args ('line', 'comma-delimited', 'csv')\n"
            "called ResultsGui.add_checkbox_to_line with args ('line', 'summarized', 'sum')\n"
            "called ResultsGui.add_checkbox_to_line with args ('line', 'toon directorypad', 'pth')\n"
            "called ResultsGui.finalize_display\n")

        parent.apptype = 'multi'
        parent.p['context'] = False
        testobj = testee.Results(parent, "path/")
        assert testobj.titel == 'File/Regel'
        assert capsys.readouterr().out == (
            f"called ResultsGui.__init__ with args ({parent}, {testobj})\n"
            "called ResultsGui.add_line\n"
            "called ResultsGui.add_text_to_line with args"
            " ('line', 'gezocht en/of vervangen (1 items)\\n"
            'De bestanden staan allemaal in of onder de directory "path"\')\n'
            "called ResultsGui.add_buttons_to_line with args ('line',"
            f" (('Go to selected result', {testobj.gui.to_result}, True),)) {{'end': True}}\n"
            "called TestResults.build_list\n"
            "called ResultsGui.add_line\n"
            "called ResultsGui.add_results_list with args"
            f" ('line', ('File/Regel', 'Tekst'), (('Help', 'F1', {testobj.help})"
            f", ('&Goto Result', 'Ctrl+G', {testobj.gui.to_result})), [])\n"
            "called ResultsGui.add_line\n"
            "called ResultsGui.add_buttons_to_line with args ('line',"
            f" (('&Klaar', {testobj.gui.klaar}, True),)) {{}}\n"
            "called ResultsGui.add_buttons_to_line with args ('line',"
            f" (('&Repeat Search', {testobj.refresh}, True),"
            f" ('&Zoek anders', {testobj.zoek_anders}, True),"
            f" ('Vervang in &Selectie', {testobj.vervang_in_sel}, True),"
            f" ('Vervang &Alles', {testobj.vervang_alles}, True))) {{}}\n"
            "called ResultsGui.add_line\n"
            "called ResultsGui.add_text_to_line with args ('line', 'Output:')\n"
            "called ResultsGui.add_buttons_to_line with args ('line',"
            f" (('Copy to &File', {testobj.kopie}, True),"
            f" ('Copy to &Clipboard', {testobj.to_clipboard}, True))) {{}}\n"
            "called ResultsGui.add_checkbox_to_line with args ('line', 'comma-delimited', 'csv')\n"
            "called ResultsGui.add_checkbox_to_line with args ('line', 'summarized', 'sum')\n"
            "called ResultsGui.add_checkbox_to_line with args ('line', 'toon directorypad', 'pth')\n"
            "called ResultsGui.finalize_display\n")

    def test_build_list(self, monkeypatch, capsys):
        """unittest for Results.build_list
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.parent.apptype = ''
        testobj.common = ""
        testobj.show_context = False
        testobj.parent.zoekvervang.rpt = []
        with pytest.raises(UnboundLocalError) as err:
            testobj.build_list()
        assert str(err.value).startswith("cannot access local variable 'kop'")
        assert capsys.readouterr().out == ("")

        testobj.parent.zoekvervang.rpt = ['xxx', '', "path_to/file r. i: text"]
        testobj.build_list()
        assert testobj.results == ['xxx', ('path_to/file r. i', 'text')]
        assert capsys.readouterr().out == ("")

        testobj.results = []
        testobj.parent.apptype = 'single-file'
        testobj.build_list()
        assert testobj.results == ['xxx', ('i', 'text')]

        testobj.results = []
        testobj.parent.apptype = 'qqq'
        testobj.common = pathlib.Path('path_to')
        testobj.build_list()
        assert testobj.results == ['xxx', ('/file r. i', 'text')]

        testobj.results = []
        testobj.common = '/'
        testobj.build_list()
        assert testobj.results == ['xxx', ('path_to/file r. i', 'text')]

        testobj.parent.zoekvervang.rpt = ['xxx', '', "path_to/file r. j (in method): text"]
        testobj.results = []
        testobj.show_context = True
        testobj.build_list()
        assert testobj.results == ['xxx', ('path_to/file r. j', 'in method', 'text')]

    def test_show(self, monkeypatch, capsys):
        """unittest for Results.show
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.show()
        assert capsys.readouterr().out == ("called ResultsGui.go\n")

    def test_get_results(self, monkeypatch, capsys):
        """unittest for Results.get_results
        """
        class MockTextBuf:
            """stub
            """
            def __init__(self, *args):
                print('called CSVTextBuf.__init__ with args', args)
            def write_line(self, arg):
                print(f"called CSVTextBuf.write_line with arg '{arg}'")
            def get_contents_and_close(self):
                print("called CSVTextBuf.get_contents_and_close")
                return ['textbuf', 'contents']
        def mock_reformat(text, context):
            print(f"called reformat_result with args ({text}, {context})")
            return text
        def mock_get(*args):
            print('called ResultsGui.get_checkbox_value with args', args)
            return args[0] != 'cb_path'
        def mock_get_2(*args):
            print('called ResultsGui.get_checkbox_value with args', args)
            return args[0] != 'cb_delim'
        def mock_get_3(*args):
            print('called ResultsGui.get_checkbox_value with args', args)
            return True
        def mock_get_4(*args):
            print('called ResultsGui.get_checkbox_value with args', args)
            return args[0] == 'cb_smrz'

        monkeypatch.setattr(testee, 'common_path_txt', 'where: {}')
        monkeypatch.setattr(testee, 'CSVTextBuf', MockTextBuf)
        monkeypatch.setattr(testee, 'reformat_result', mock_reformat)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.common = 'here'
        testobj.results = ['first line', ('second', 'line')]
        testobj.show_context = False
        testobj.parent.p = {'filelist': ['filename']}
        testobj.cb_path = 'cb_path'
        testobj.cb_delim = 'cb_delim'
        testobj.cb_smrz = 'cb_smrz'

        testobj.parent.apptype = 'multi'
        assert testobj.get_results() == ["first line", 'where: here', '', 'second line']
        assert capsys.readouterr().out == (
                "called ResultsGui.get_checkbox_value with args ('cb_path',)\n"
                "called ResultsGui.get_checkbox_value with args ('cb_delim',)\n"
                "called ResultsGui.get_checkbox_value with args ('cb_smrz',)\n")

        testobj.parent.apptype = 'single-file'
        assert testobj.get_results() == ["first line", '', 'r. second line']
        assert capsys.readouterr().out == (
                "called ResultsGui.get_checkbox_value with args ('cb_path',)\n"
                "called ResultsGui.get_checkbox_value with args ('cb_delim',)\n"
                "called ResultsGui.get_checkbox_value with args ('cb_smrz',)\n")

        testobj.gui.get_checkbox_value = mock_get
        testobj.show_context = True
        testobj.results = ['first line', ('sec r. ond', 'line')]
        testobj.parent.apptype = 'qqq'
        assert testobj.get_results() == ["first line", '', 'textbuf', 'contents']
        assert capsys.readouterr().out == (
                "called ResultsGui.get_checkbox_value with args ('cb_path',)\n"
                "called ResultsGui.get_checkbox_value with args ('cb_delim',)\n"
                "called ResultsGui.get_checkbox_value with args ('cb_smrz',)\n"
                "called CSVTextBuf.__init__ with args ('qqq', False)\n"
                "called CSVTextBuf.write_line with arg '['sec r. ond', 'line']'\n"
                "called CSVTextBuf.get_contents_and_close\n"
                "called reformat_result with args (['first line', '', 'textbuf', 'contents'], py)\n")

        testobj.gui.get_checkbox_value = mock_get_2
        assert testobj.get_results() == ["first line", '', 'sec r. ond line']
        assert capsys.readouterr().out == (
                "called ResultsGui.get_checkbox_value with args ('cb_path',)\n"
                "called ResultsGui.get_checkbox_value with args ('cb_delim',)\n"
                "called ResultsGui.get_checkbox_value with args ('cb_smrz',)\n"
                "called reformat_result with args (['first line', '', 'sec r. ond line'], py)\n")

        testobj.gui.get_checkbox_value = mock_get_3
        assert testobj.get_results() == ["first line", '', 'textbuf', 'contents']
        assert capsys.readouterr().out == (
                "called ResultsGui.get_checkbox_value with args ('cb_path',)\n"
                "called ResultsGui.get_checkbox_value with args ('cb_delim',)\n"
                "called ResultsGui.get_checkbox_value with args ('cb_smrz',)\n"
                "called CSVTextBuf.__init__ with args ('qqq', True)\n"
                "called CSVTextBuf.write_line with arg '['heresec r. ond', 'line']'\n"
                "called CSVTextBuf.get_contents_and_close\n"
                "called reformat_result with args (['first line', '', 'textbuf', 'contents'], py)\n")

        testobj.gui.get_checkbox_value = mock_get_2
        testobj.parent.apptype = 'multi'
        assert testobj.get_results() == ["first line", '', 'heresec r. ond line']
        assert capsys.readouterr().out == (
                "called ResultsGui.get_checkbox_value with args ('cb_path',)\n"
                "called ResultsGui.get_checkbox_value with args ('cb_delim',)\n"
                "called ResultsGui.get_checkbox_value with args ('cb_smrz',)\n"
                "called reformat_result with args (['first line', '', 'heresec r. ond line'], py)\n")

        testobj.parent.apptype = 'single-file'
        assert testobj.get_results() == ["filename first line", '', 'filename r. sec r. ond line']
        assert capsys.readouterr().out == (
                "called ResultsGui.get_checkbox_value with args ('cb_path',)\n"
                "called ResultsGui.get_checkbox_value with args ('cb_delim',)\n"
                "called ResultsGui.get_checkbox_value with args ('cb_smrz',)\n"
                "called reformat_result with args"
                " (['filename first line', '', 'filename r. sec r. ond line'], py)\n")

        testobj.gui.get_checkbox_value = mock_get_4
        assert testobj.get_results() == ["first line", '', 'r. sec r. ond line']
        assert capsys.readouterr().out == (
                "called ResultsGui.get_checkbox_value with args ('cb_path',)\n"
                "called ResultsGui.get_checkbox_value with args ('cb_delim',)\n"
                "called ResultsGui.get_checkbox_value with args ('cb_smrz',)\n"
                "called reformat_result with args"
                " (['filename first line', '', 'filename r. sec r. ond line'], py)\n")

    def test_refresh(self, monkeypatch, capsys):
        """unittest for Results.refresh
        """
        class MockFindr:
            """stub"""
            def go(self):
                print('called Findr.go')
                self.rpt = ['just a header']
        def mock_setcursor(value):
            print(f'called AfriftGui.set_waitcursor with arg {value}')
        def mock_go_2(self):
            print('called Findr.go')
            self.rpt = ['header', 'number: replace message']
        def mock_go_3(self):
            print('called Findr.go')
            self.rpt = ['header', 'line 1', 'line 2']
        def mock_build():
            print('called TestResults.build_list')
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.messages = {'nope': 'nope'}
        testobj.parent.gui.set_waitcursor = mock_setcursor
        testobj.parent.zoekvervang = MockFindr()
        testobj.parent.zoekvervang.specs = ['aa', 'bb']
        testobj.parent.zoekvervang.p = {'zoek': 'a needle', 'wijzig': False, }
        testobj.parent.resulttitel = 'xxx'
        testobj.build_list = mock_build
        testobj.lijst = 'results_list'
        testobj.hdr = 'textfield'
        testobj.common = 'root'
        testobj.common_path_txt = 'in {}'
        testobj.parent.apptype = ''

        testobj.refresh()
        assert capsys.readouterr().out == (
                "called ResultsGui.clear_contents\n"
                "called AfriftGui.set_waitcursor with arg True\n"
                "called Findr.go\n"
                "called AfriftGui.set_waitcursor with arg False\n"
                "called ResultsGui.meld with args ('xxx', 'just a header\\nNiks gevonden')\n")

        monkeypatch.setattr(MockFindr, 'go', mock_go_2)
        testobj.refresh()
        assert capsys.readouterr().out == (
                "called ResultsGui.clear_contents\n"
                "called AfriftGui.set_waitcursor with arg True\n"
                "called Findr.go\n"
                "called AfriftGui.set_waitcursor with arg False\n"
                "called ResultsGui.set_header with args ('textfield', 'header (1 items)')\n"
                "called TestResults.build_list\n"
                "called ResultsGui.populate_list with args ('results_list', [])\n")

        testobj.parent.zoekvervang.p['wijzig'] = True
        testobj.refresh()
        assert capsys.readouterr().out == (
                "called ResultsGui.clear_contents\n"
                "called AfriftGui.set_waitcursor with arg True\n"
                "called Findr.go\n"
                "called AfriftGui.set_waitcursor with arg False\n"
                "called ResultsGui.set_header with args ('textfield', 'header (replace message)')\n"
                "called TestResults.build_list\n"
                "called ResultsGui.populate_list with args ('results_list', [])\n")

        monkeypatch.setattr(MockFindr, 'go', mock_go_3)
        testobj.refresh()
        assert capsys.readouterr().out == (
                "called ResultsGui.clear_contents\n"
                "called AfriftGui.set_waitcursor with arg True\n"
                "called Findr.go\n"
                "called AfriftGui.set_waitcursor with arg False\n"
                "called ResultsGui.set_header with args ('textfield', 'header (2 items)')\n"
                "called TestResults.build_list\n"
                "called ResultsGui.populate_list with args ('results_list', [])\n")

        testobj.parent.apptype = 'multi'
        testobj.refresh()
        assert capsys.readouterr().out == (
                "called ResultsGui.clear_contents\n"
                "called AfriftGui.set_waitcursor with arg True\n"
                "called Findr.go\n"
                "called AfriftGui.set_waitcursor with arg False\n"
                "called ResultsGui.set_header with args ('textfield', 'header (2 items)\\n"
                'De bestanden staan allemaal in of onder de directory "root"\')\n'
                "called TestResults.build_list\n"
                "called ResultsGui.populate_list with args ('results_list', [])\n")

        testobj.parent.apptype = 'single'
        testobj.refresh(replace_count=10, replace_text='a pointy stick')
        assert capsys.readouterr().out == (
                "called ResultsGui.clear_contents\n"
                "called AfriftGui.set_waitcursor with arg True\n"
                "called Findr.go\n"
                "called AfriftGui.set_waitcursor with arg False\n"
                "called ResultsGui.set_header with args ('textfield',"
                " '`a needle` with `a pointy stick` replaced 10 in lines\\nheader (2 items)')\n"
                "called TestResults.build_list\n"
                "called ResultsGui.populate_list with args ('results_list', [])\n")

    def test_check_option_combinations_ok(self, monkeypatch, capsys):
        """unittest for Results.check_option_combinations_ok
        """
        def mock_get(*args):
            print('called ResultsGui.get_checkbox_value with args', args)
            return args[0] == 'cb_smrz'
        def mock_get_2(*args):
            print('called ResultsGui.get_checkbox_value with args', args)
            return args[0] == 'cb_delim '
        def mock_get_3(*args):
            print('called ResultsGui.get_checkbox_value with args', args)
            return True
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.cb_delim = 'cbdelim'
        testobj.cb_smrz = 'cb_smrz'
        testobj.gui.get_checkbox_value = mock_get
        assert testobj.check_option_combinations_ok()
        assert capsys.readouterr().out == (
                "called ResultsGui.get_checkbox_value with args ('cbdelim',)\n"
                "called ResultsGui.get_checkbox_value with args ('cb_smrz',)\n")
        testobj.gui.get_checkbox_value = mock_get_2
        assert testobj.check_option_combinations_ok()
        assert capsys.readouterr().out == (
                "called ResultsGui.get_checkbox_value with args ('cbdelim',)\n"
                "called ResultsGui.get_checkbox_value with args ('cb_smrz',)\n")
        testobj.gui.get_checkbox_value = mock_get_3
        assert not testobj.check_option_combinations_ok()
        assert capsys.readouterr().out == (
                "called ResultsGui.get_checkbox_value with args ('cbdelim',)\n"
                "called ResultsGui.get_checkbox_value with args ('cb_smrz',)\n"
                "called ResultsGui.meld with args ('ahem',"
                " 'Summarize to comma delimited is not a sensible option, request denied')\n""")

    def test_kopie(self, monkeypatch, capsys, tmp_path):
        """unittest for Results.kopie
        """
        mock_savefile = tmp_path / 'savefile'
        def mock_get_savefile(*args):
            print('called ResultsGui.get_savefile with args', args)
            return str(mock_savefile)
        def mock_get_savefile_2(*args):
            print('called ResultsGui.get_savefile with args', args)
            return ''
        def mock_get(*args):
            print('called ResultsGui.get_checkbox_value with args', args)
            return True
        def mock_check():
            print('called Results.check_option_combinations_ok')
            return True
        def mock_check_2():
            print('called Results.check_option_combinations_ok')
            return False
        def mock_remember():
            print('called Results.remember_settings')
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.parent.p['zoek'] = 'xyz/\\?%*:|"><.123'
        testobj.parent.hier = 'hier'
        testobj.cb_delim = 'cbdelim'
        testobj.get_results = lambda: ['heading', 'data']
        testobj.check_option_combinations_ok = mock_check
        testobj.remember_settings = mock_remember

        testobj.gui.get_savefile = mock_get_savefile
        testobj.kopie()
        assert mock_savefile.exists()
        assert mock_savefile.read_text() == "heading\ndata\n"
        assert capsys.readouterr().out == (
                "called Results.check_option_combinations_ok\n"
                "called ResultsGui.get_checkbox_value with args ('cbdelim',)\n"
                "called ResultsGui.get_savefile with args"
                " ('Resultaat naar bestand kopiëren', 'hier',"
                " 'files-containing-xyz~~~~~~~~~~~123.txt',"
                " (('.txt', 'Text files'), ('.*', 'All files')))\n"
                "called Results.remember_settings\n")
        mock_savefile.unlink()
        testobj.parent.p['zoek'] = 'xyzabc123'
        testobj.kopie()
        assert mock_savefile.exists()
        assert mock_savefile.read_text() == "heading\ndata\n"
        assert capsys.readouterr().out == (
                "called Results.check_option_combinations_ok\n"
                "called ResultsGui.get_checkbox_value with args ('cbdelim',)\n"
                "called ResultsGui.get_savefile with args"
                " ('Resultaat naar bestand kopiëren', 'hier',"
                " 'files-containing-xyzabc123.txt',"
                " (('.txt', 'Text files'), ('.*', 'All files')))\n"
                "called Results.remember_settings\n")
        mock_savefile.unlink()
        testobj.gui.get_checkbox_value = mock_get
        testobj.check_option_combinations_ok = mock_check_2
        testobj.gui.get_savefile = mock_get_savefile_2
        testobj.kopie()
        assert not mock_savefile.exists()
        assert capsys.readouterr().out == "called Results.check_option_combinations_ok\n"
        testobj.check_option_combinations_ok = mock_check
        testobj.kopie()
        assert not mock_savefile.exists()
        assert capsys.readouterr().out == (
                "called Results.check_option_combinations_ok\n"
                "called ResultsGui.get_checkbox_value with args ('cbdelim',)\n"
                "called ResultsGui.get_savefile with args"
                " ('Resultaat naar bestand kopiëren', 'hier',"
                " 'files-containing-xyzabc123.csv',"
                " (('.csv', 'Comma delimited files'), ('.*', 'All files')))\n")

    def test_help(self, monkeypatch, capsys):
        """unittest for Results.help
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.help()
        assert capsys.readouterr().out == ("called ResultsGui.meld with args ('info',"
                                           " 'Select a line and doubleclick or press Ctrl-G"
                                           " to open the indicated file\\nat the indicated"
                                           " line (not in single file mode)')\n")

    def test_to_clipboard(self, monkeypatch, capsys):
        """unittest for Results.to_clipboard
        """
        def mock_remember():
            print('called Results.remember_settings')
        def mock_check():
            print('called Results.check_option_combinations_ok')
            return False
        def mock_check_2():
            print('called Results.check_option_combinations_ok')
            return True
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.get_results = lambda: ['heading', 'data']
        testobj.remember_settings = mock_remember
        testobj.check_option_combinations_ok = mock_check
        testobj.to_clipboard()
        assert capsys.readouterr().out == "called Results.check_option_combinations_ok\n"
        testobj.check_option_combinations_ok = mock_check_2
        testobj.to_clipboard()
        assert capsys.readouterr().out == (
                "called Results.check_option_combinations_ok\n"
                "called Results.remember_settings\n"
                "called ResultsGui.copy_to_clipboard with arg 'heading\ndata\n'\n")

    def test_remember_settings(self, monkeypatch, capsys):
        """unittest for Results.remember_settings
        """
        def mock_write():
            print('called Afrift.write_to_ini')
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.parent.outopts = {}
        testobj.cb_path = 'cbpath'
        testobj.cb_delim = 'cbdelim'
        testobj.cb_smrz = 'cbsmrz'
        testobj.parent.write_to_ini = mock_write
        testobj.remember_settings()
        assert testobj.parent.outopts == {'full_path': False, 'as_csv': False, 'summarize': False}
        assert capsys.readouterr().out == (
                "called ResultsGui.get_checkbox_value with args ('cbpath',)\n"
                "called ResultsGui.get_checkbox_value with args ('cbdelim',)\n"
                "called ResultsGui.get_checkbox_value with args ('cbsmrz',)\n"
                "called Afrift.write_to_ini\n")

    def test_goto_result(self, monkeypatch, capsys):
        """unittest for Results.goto_result
        """
        def mock_run(*args, **kwargs):
            print('called subprocess.run with args', args, kwargs)
        monkeypatch.setattr(testee.subprocess, 'run', mock_run)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.messages = {'goto': 'no go'}
        testobj.results = ['heading', ('filename r. n', 'xxx')]
        testobj.common = 'pathname/'
        testobj.parent.editor_option = [['editor'], 'open-file {}', 'at-position {}']
        testobj.parent.apptype = 'single-file'
        testobj.goto_result(0, 5)
        assert capsys.readouterr().out == ("called ResultsGui.meld with args"
                                           " ('ahem', 'Not in single file mode')\n")
        testobj.parent.apptype = ''
        testobj.goto_result(0, 5)
        assert capsys.readouterr().out == (
                "called subprocess.run with args"
                " (['editor', 'open-file pathname/filename', 'at-position n'],) {'check': False}\n")

    def test_vervang_in_sel(self, monkeypatch, capsys):
        """unittest for Results.vervang_in_sel
        """
        def mock_get_sel():
            print('called ResultsGui.get_selection')
            return []
        def mock_get_sel_2():
            print('called ResultsGui.get_selection')
            return ['file r. x']
        def mock_get_text(*args):
            print('called ResultsGui.get_text_from_user with args', args)
            return '', False
        def mock_get_text_2(*args):
            print('called ResultsGui.get_text_from_user with args', args)
            return 'yyy', True
        def mock_replace(*args):
            print('called Findr.replace_selected with args', args)
            return 5
        def mock_refresh(**kwargs):
            print('called Results.refresh with args', kwargs)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.messages = {'replsel': 'findr {} in sel', 'noitems': 'No items'}
        testobj.parent.p = {'zoek': 'xxx'}
        testobj.parent.resulttitel = 'Results'
        testobj.parent.zoekvervang.replace_selected = mock_replace
        testobj.gui.get_selection = mock_get_sel
        testobj.gui.get_text_from_user = mock_get_text
        testobj.refresh = mock_refresh
        testobj.vervang_in_sel()
        assert capsys.readouterr().out == (
                "called ResultsGui.get_selection\n"
                "called ResultsGui.meld with args"
                " ('Results', 'Geen regels geselecteerd om in te vervangen')\n")
        testobj.gui.get_selection = mock_get_sel_2
        testobj.vervang_in_sel()
        assert capsys.readouterr().out == (
                "called ResultsGui.get_selection\n"
                "called ResultsGui.get_text_from_user with args"
                " ('Results', 'vervang `xxx` in geselecteerde regels door:')\n")
        testobj.gui.get_text_from_user = mock_get_text_2
        testobj.vervang_in_sel()
        assert capsys.readouterr().out == (
                "called ResultsGui.get_selection\n"
                "called ResultsGui.get_text_from_user with args"
                " ('Results', 'vervang `xxx` in geselecteerde regels door:')\n"
                "called Findr.replace_selected with args ('yyy', [['file', 'x']])\n"
                "called Results.refresh with args {'replace_text': 'yyy', 'replace_count': 5}\n")

    def test_vervang_alles(self, monkeypatch, capsys):
        """unittest for Results.vervang_alles
        """
        def mock_get_text(*args):
            print('called ResultsGui.get_text_from_user with args', args)
            return '', False
        def mock_get_text_2(*args):
            print('called ResultsGui.get_text_from_user with args', args)
            return 'xxx', True
        def mock_setup():
            print('called Findr.setup_search')
        def mock_refresh(**kwargs):
            print('called Results.refresh with args', kwargs)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.messages = {'replall': 'findr {}'}
        testobj.parent.p = {'zoek': 'xxx'}
        testobj.parent.resulttitel = 'Results'
        testobj.parent.zoekvervang.p = testobj.parent.p
        testobj.parent.zoekvervang.setup_search = mock_setup
        testobj.refresh = mock_refresh
        testobj.gui.get_text_from_user = mock_get_text
        testobj.vervang_alles()
        assert capsys.readouterr().out == (
                "called ResultsGui.get_text_from_user with args"
                " ('Results', 'vervang `xxx` in alle regels door:')\n")
        testobj.gui.get_text_from_user = mock_get_text_2
        testobj.vervang_alles()
        assert capsys.readouterr().out == (
                "called ResultsGui.get_text_from_user with args"
                " ('Results', 'vervang `xxx` in alle regels door:')\n"
                "called Findr.setup_search\n"
                "called Results.refresh with args {}\n")

    def test_zoek_anders(self, monkeypatch, capsys):
        """unittest for Results.zoek_anders
        """
        def mock_get_text(*args):
            print('called ResultsGui.get_text_from_user with args', args)
            return '', False
        def mock_get_text_2(*args):
            print('called ResultsGui.get_text_from_user with args', args)
            return 'yyy', True
        def mock_refresh(**kwargs):
            print('called Results.refresh with args', kwargs)
        class MockFindr:
            "stub for findr.Finder"
            p = {}
            def setup_search(self):
                print('called Findr.setup_search')
                print("Findr.p['zoek'] =", self.p['zoek'])
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.messages = {'other': 'new search'}
        testobj.parent.p = {'zoek': 'xxx'}
        testobj.parent.resulttitel = 'Results'
        testobj.parent.zoekvervang = MockFindr()
        testobj.parent.zoekvervang.p = testobj.parent.p
        testobj.refresh = mock_refresh
        testobj.gui.get_text_from_user = mock_get_text
        testobj.zoek_anders()
        assert capsys.readouterr().out == (
                "called ResultsGui.get_text_from_user with args"
                " ('Results', 'zoek in dezelfde selectie naar:')\n")
        testobj.gui.get_text_from_user = mock_get_text_2
        testobj.zoek_anders()
        assert capsys.readouterr().out == (
                "called ResultsGui.get_text_from_user with args"
                " ('Results', 'zoek in dezelfde selectie naar:')\n"
                "called Findr.setup_search\n"
                "Findr.p['zoek'] = yyy\n"
                "called Results.refresh with args {}\n"
                "called Findr.setup_search\n"
                "Findr.p['zoek'] = xxx\n")
