"""unittests for ./afrift/base.py
"""
import types
import pathlib
import pytest
from afrift import base as testee


class MockMainFrame:
    "stub for main.MainFrame"
    def __init__(self):
        print('called MainFrame.__init__ ')


class MockResultsGui:
    "stub for gui.ResultsGui"
    # def __init__(self, parent, master):
    def __init__(self, *args):
        print('called ResultsGui.__init__ with args', args)
    def setup_screen(self, captions):
        print(f"called ResultsGui.setup_screen with arg {captions}")
    def go(self):
        print('called ResultsGui.go')
    def meld(self, *args):
        print('called ResultsGui.meld with args', args)
    def remember_settings(self):
        print('called ResultsGui.remember_settings')
    def copy_to_clipboard(self, arg):
        print(f"called ResultsGui.copy_to_clipboard with arg '{arg}'")


class MockSelectNamesGui:
    "stub for gui.SelectnamesGui"
    def __init__(self, *args):
        print('called SelectNamesGui with args', args)
    def setup_screen(self, arg):
        print(f"called SelectNamesGui.setup_screen with arg '{arg}'")
    def go(self):
        print("called SelectNamesGui.go")
        return 'gone'


def test_main(monkeypatch, capsys, tmp_path):
    """unittest for base.main
    """
    def mock_mkdir(*args, **kwargs):
        print('called pathlib.Path.mkdir with args', args, kwargs)
    def mock_touch(*args, **kwargs):
        print('called pathlib.Path.touch with args', args, kwargs)
    def mock_mainframe(*args, **kwargs):
        print('called MainFrame with args', args, kwargs)
    def mock_mainframe_2(*args, **kwargs):
        print('called MainFrame with args', args, kwargs)
        raise ValueError('message')
    with pytest.raises(TypeError) as exc:
        testee.main()
    assert str(exc.value) == "main() missing 1 required positional argument: 'args'"
    monkeypatch.setattr(testee.pathlib.Path, 'mkdir', mock_mkdir)
    monkeypatch.setattr(testee.pathlib.Path, 'touch', mock_touch)
    monkeypatch.setattr(testee, 'MainFrame', mock_mainframe)
    mock_logfile = tmp_path / 'logs' / 'afrift.log'
    monkeypatch.setattr(testee, 'LOGFILE', mock_logfile)
    monkeypatch.setattr(testee, 'WANT_LOGGING', True)
    assert testee.main({'appmode': 'xx', 'fname': ['yy'], 'output_file': ''}) == ''
    assert capsys.readouterr().out == (
            f"called pathlib.Path.mkdir with args ({mock_logfile.parent!r},) {{'exist_ok': True}}\n"
            f"called pathlib.Path.touch with args ({mock_logfile!r},) {{'exist_ok': True}}\n"
            "called MainFrame with args () {'output_file': '', 'apptype': 'xx', 'fnaam': 'yy'}\n")

    monkeypatch.setattr(testee, 'WANT_LOGGING', False)
    assert testee.main({'appmode': 'xx', 'fname': ['yy', 'zz'], 'output_file': ''}) == ''
    assert capsys.readouterr().out == (
            "called MainFrame with args"
            " () {'output_file': '', 'apptype': 'multi', 'flist': ['yy', 'zz']}\n")

    assert testee.main({'appmode': 'xx', 'fname': ['yy'], 'output_file': '', 'full_path': 'zz'}) == (
            "Output options without output destination not allowed")
    assert capsys.readouterr().out == ''
    assert testee.main({'appmode': 'xx', 'fname': ['yy'], 'output_file': '', 'as_csv': True}) == (
            "Output options without output destination not allowed")
    assert capsys.readouterr().out == ''
    assert testee.main({'appmode': 'xx', 'fname': ['yy'], 'output_file': '', 'summarize': True}) == (
            "Output options without output destination not allowed")
    assert capsys.readouterr().out == ''
    assert testee.main({'appmode': 'xx', 'fname': ['yy'], 'output_file': 'zz', 'as_csv': True,
                        'summarize': True}) == (
            "'Output to csv' and 'summarize' is not a sensible combination")
    assert capsys.readouterr().out == ''

    monkeypatch.setattr(testee, 'MainFrame', mock_mainframe_2)
    assert testee.main({'appmode': 'xx', 'fname': ['yy'], 'output_file': ''}) == 'message'
    assert capsys.readouterr().out == (
            "called MainFrame with args () {'output_file': '', 'apptype': 'xx', 'fnaam': 'yy'}\n")


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
            "stub for base.MainFrame"
            pass
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
        assert capsys.readouterr().out == "called SelectNamesGui with args ()\n"
        return testobj

    def test_init(self, monkeypatch, capsys):
        """unittest for SelectNames.__init__
        """
        class MockParent:
            "stub for base.MainFrame"
            pass
        monkeypatch.setattr(testee, 'iconame', 'find.ico')
        monkeypatch.setattr(testee, 'SelectNamesGui', MockSelectNamesGui)
        parent = MockParent()
        parent.title = 'app title'
        parent.names = [testee.pathlib.Path('xx'), testee.pathlib.Path('yy')]
        testobj = testee.SelectNames(parent)
        assert testobj.do_files
        assert testobj.parent == parent
        assert testobj.title == 'app title - file list'
        assert testobj.iconame == 'find.ico'
        assert testobj.names == {'xx': testee.pathlib.Path('xx'), 'yy': testee.pathlib.Path('yy')}
        assert capsys.readouterr().out == (
                f"called SelectNamesGui with args ({parent}, {testobj})\n"
                "called SelectNamesGui.setup_screen with arg"
                " '{'heading': 'Selecteer de bestanden die je *niet* wilt verwerken',"
                " 'sel_all': 'Select/Unselect All', 'invert': 'Invert selection',"
                " 'exit': '&Terug', 'execute': '&Klaar'}'\n")

        testobj = testee.SelectNames(parent, files=False)
        assert not testobj.do_files
        assert testobj.parent == parent
        assert testobj.title == 'app title - file list'
        assert testobj.iconame == 'find.ico'
        assert not hasattr(testobj, 'names')
        assert capsys.readouterr().out == (
                f"called SelectNamesGui with args ({parent}, {testobj})\n"
                "called SelectNamesGui.setup_screen with arg"
                " '{'heading': 'Selecteer de directories die je *niet* wilt verwerken',"
                " 'sel_all': 'Select/Unselect All', 'invert': 'Invert selection',"
                " 'exit': '&Terug', 'execute': '&Klaar'}'\n")

    def test_show(self, monkeypatch, capsys):
        """unittest for SelectNames.show
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.names = ['x', 'y']
        testobj.show()
        assert capsys.readouterr().out == "called SelectNamesGui.go\n"


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
        parent = MockMainFrame()
        parent.p = {}
        parent.zoekvervang = types.SimpleNamespace()
        testobj = testee.Results(parent)
        assert capsys.readouterr().out == ("called MainFrame.__init__ \n"
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
        parent = MockMainFrame()
        assert capsys.readouterr().out == "called MainFrame.__init__ \n"
        parent.p = {'context': True, 'vervang': None}
        parent.apptype = ''
        parent.zoekvervang = types.SimpleNamespace(rpt=['gezocht en/of vervangen', 'namelijk 2'])
        monkeypatch.setattr(testee.Results, 'captions', {})
        monkeypatch.setattr(testee.Results, 'build_list', mock_build)
        monkeypatch.setattr(testee, 'ResultsGui', MockResultsGui)
        testobj = testee.Results(parent)
        assert testobj.parent == parent
        assert testobj.common == ''
        assert testobj.show_context
        assert testobj.results == []
        assert testobj.titel == 'File/Regel'
        assert isinstance(testobj.gui, testee.ResultsGui)
        assert testobj.show_result_details
        assert capsys.readouterr().out == (
                f"called ResultsGui.__init__ with args ({parent}, {testobj})\n"
                "called TestResults.build_list\n"
                "called ResultsGui.setup_screen with arg"
                " {'heading': 'gezocht en/of vervangen (1 items)'}\n")
        parent.p['vervang'] = 'xx'
        parent.apptype = 'single'
        testobj = testee.Results(parent)
        assert testobj.titel == 'Regel'
        assert not testobj.show_result_details
        assert capsys.readouterr().out == (
                f"called ResultsGui.__init__ with args ({parent}, {testobj})\n"
                "called TestResults.build_list\n"
                "called ResultsGui.setup_screen with arg"
                " {'heading': 'gezocht en/of 2 vervangen'}\n")
        parent.apptype = 'multi'
        testobj = testee.Results(parent)
        assert testobj.titel == 'File/Regel'
        assert testobj.show_result_details
        assert capsys.readouterr().out == (
                f"called ResultsGui.__init__ with args ({parent}, {testobj})\n"
                "called TestResults.build_list\n"
                "called ResultsGui.setup_screen with arg"
                " {'heading': 'gezocht en/of vervangen (1 items)\\n"
                'De bestanden staan allemaal in of onder de directory ""\'}\n')

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
        testobj.parent.zoekvervang.rpt = ['xxx', '', "path_to/file r. i: text"]
        testobj.build_list()
        assert testobj.results == ['xxx', ('path_to/file r. i', 'text')]

        testobj.results = []
        testobj.parent.apptype = 'single'
        testobj.build_list()
        assert testobj.results == ['xxx', ('i', 'text')]

        testobj.results = []
        testobj.parent.apptype = ''
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

    def _test_get_results(self, monkeypatch, capsys):
        """unittest for Results.get_results
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.get_results() == "expected_result"
        assert capsys.readouterr().out == ("")

    def _test_refresh(self, monkeypatch, capsys):
        """unittest for Results.refresh
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.refresh(*args, **kwargs) == "expected_result"
        assert capsys.readouterr().out == ("")

    def test_check_option_combinations_ok(self, monkeypatch, capsys):
        """unittest for Results.check_option_combinations_ok
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.gui.get_sum = lambda: True
        testobj.gui.get_csv = lambda: False
        assert testobj.check_option_combinations_ok()
        assert capsys.readouterr().out == ""
        testobj.gui.get_sum = lambda: False
        testobj.gui.get_csv = lambda: True
        assert testobj.check_option_combinations_ok()
        assert capsys.readouterr().out == ""
        testobj.gui.get_sum = lambda: True
        testobj.gui.get_csv = lambda: True
        assert not testobj.check_option_combinations_ok()
        assert capsys.readouterr().out == (
                f"""called ResultsGui.meld with args ('ahem', '{testobj.messages["sum2csv"]}')\n""")

    def test_kopie(self, monkeypatch, capsys, tmp_path):
        """unittest for Results.kopie
        """
        mock_savefile = tmp_path / 'savefile'
        def mock_get_savefile(*args):
            print('called ResultsGui.get_savefile with args', args)
            return ''
        def mock_get_savefile_2(*args):
            print('called ResultsGui.get_savefile with args', args)
            return str(mock_savefile)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.parent.p['zoek'] = 'xyz/\\?%*:|"><.123'
        testobj.get_results = lambda: ['heading', 'data']
        testobj.check_option_combinations_ok = lambda: False
        testobj.gui.get_savefile = mock_get_savefile
        testobj.gui.get_csv = lambda: True
        testobj.kopie()
        assert capsys.readouterr().out == ""
        testobj.check_option_combinations_ok = lambda: True
        testobj.kopie()
        assert not mock_savefile.exists()
        assert capsys.readouterr().out == ("called ResultsGui.get_savefile with args"
                                           " ('files-containing-xyz~~~~~~~~~~~123.csv', '.csv')\n")
        testobj.gui.get_csv = lambda: False
        testobj.gui.get_savefile = mock_get_savefile_2
        testobj.kopie()
        assert mock_savefile.read_text() == "heading\ndata\n"
        assert capsys.readouterr().out == ("called ResultsGui.get_savefile with args"
                                           " ('files-containing-xyz~~~~~~~~~~~123.txt', '.txt')\n"
                                           "called ResultsGui.remember_settings\n")

    def test_help(self, monkeypatch, capsys):
        """unittest for Results.help
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.messages = {'help': 'Help!'}
        testobj.help()
        assert capsys.readouterr().out == "called ResultsGui.meld with args ('info', 'Help!')\n"

    def test_to_clipboard(self, monkeypatch, capsys):
        """unittest for Results.to_clipboard
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.get_results = lambda: ['heading', 'data']
        testobj.check_option_combinations_ok = lambda: False
        testobj.to_clipboard()
        assert capsys.readouterr().out == ""
        testobj.check_option_combinations_ok = lambda: True
        testobj.to_clipboard()
        assert capsys.readouterr().out == (
                "called ResultsGui.remember_settings\n"
                "called ResultsGui.copy_to_clipboard with arg 'heading\ndata\n'\n")

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
        testobj.parent.apptype = 'single'
        testobj.goto_result(0, 5)
        assert capsys.readouterr().out == "called ResultsGui.meld with args ('ahem', 'no go')\n"
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
                "called ResultsGui.meld with args ('Results', 'No items')\n")
        testobj.gui.get_selection = mock_get_sel_2
        testobj.vervang_in_sel()
        assert capsys.readouterr().out == (
                "called ResultsGui.get_selection\n"
                "called ResultsGui.get_text_from_user with args ('Results', 'findr xxx in sel')\n")
        testobj.gui.get_text_from_user = mock_get_text_2
        testobj.vervang_in_sel()
        assert capsys.readouterr().out == (
                "called ResultsGui.get_selection\n"
                "called ResultsGui.get_text_from_user with args ('Results', 'findr xxx in sel')\n"
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
                "called ResultsGui.get_text_from_user with args ('Results', 'findr xxx')\n")
        testobj.gui.get_text_from_user = mock_get_text_2
        testobj.vervang_alles()
        assert capsys.readouterr().out == (
                "called ResultsGui.get_text_from_user with args ('Results', 'findr xxx')\n"
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
                "called ResultsGui.get_text_from_user with args ('Results', 'new search')\n")
        testobj.gui.get_text_from_user = mock_get_text_2
        testobj.zoek_anders()
        assert capsys.readouterr().out == (
                "called ResultsGui.get_text_from_user with args ('Results', 'new search')\n"
                "called Findr.setup_search\n"
                "Findr.p['zoek'] = yyy\n"
                "called Results.refresh with args {}\n"
                "called Findr.setup_search\n"
                "Findr.p['zoek'] = xxx\n")


class TestMainFrame:
    """unittest for base.MainFrame
    """
    def setup_testobj(self, monkeypatch, capsys):
        """stub for base.MainFrame object

        create the object skipping the normal initialization
        intercept messages during creation
        return the object so that other methods can be monkeypatched in the caller
        """
        def mock_init(self, *args):
            """stub
            """
            print('called MainFrame.__init__ with args', args)
        monkeypatch.setattr(testee.MainFrame, '__init__', mock_init)
        testobj = testee.MainFrame()
        assert capsys.readouterr().out == 'called MainFrame.__init__ with args ()\n'
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
        """unittest for MainFrame.__init__
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
        monkeypatch.setattr(testee.MainFrame, 'get_filename_list', mock_get_filename_list)
        monkeypatch.setattr(testee.MainFrame, 'setup_options', mock_setup_options)
        monkeypatch.setattr(testee.MainFrame, 'apply_cmdline_options', mock_apply_cmdline_options)
        monkeypatch.setattr(testee.MainFrameGui, '__init__', mock_gui)
        monkeypatch.setattr(testee.MainFrameGui, 'setup_screen', mock_gui_setup_screen)
        monkeypatch.setattr(testee.MainFrameGui, 'go', mock_gui_go)
        monkeypatch.setattr(testee.MainFrame, 'doe', mock_doe)

        testobj = testee.MainFrame()
        assert testobj.apptype == ''
        assert testobj.p['filelist'] == ['x', 'y', 'z']
        assert capsys.readouterr().out == ('called setup_options\ncalled apply_cmdline_options\n'
                'called gui instantiation\ncalled gui.setup_screen\ncalled gui.go\n')
        monkeypatch.setattr(testee.MainFrame, 'get_filename_list', mock_get_filename_list_empty)
        monkeypatch.setattr(testee.MainFrame, 'apply_cmdline_options',
                            mock_apply_cmdline_options_nogui)
        testobj = testee.MainFrame()
        assert testobj.apptype == ''
        assert testobj.p['filelist'] == []
        assert capsys.readouterr().out == ('called setup_options\ncalled apply_cmdline_options\n'
                'called gui instantiation\ncalled gui.setup_screen\ncalled doe\n')
        # gemist: r. 310 geen apptype opgegeven en fnaam argument bestaat en is directory

    def test_get_filename_list(self, monkeypatch, capsys):
        """unittest for MainFrame.get_filename_list
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
        # de rest moet nog (fn_orig/fnaam = directory, fn_orig/fnaam = file met namen)
        # maar ik weet al dat het werkt dus ik ga even verder met setup_options
        # gemist vogens coverage: 355-364 apptype = multi en 1e argument heeft waarde

    def test_setup_options(self, monkeypatch, capsys, tmp_path):
        """unittest for MainFrame.setup_options
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

    def _test_read_from_ini(self, monkeypatch, capsys):
        """unittest for MainFrame.read_from_ini
        """
        loc = testee.pathlib.Path('loc')
        mfile = loc / 'mru'
        ofile = loc / 'opts'
        def mock_get(arg):
            print(f"called get_iniloc with arg '{arg}'")
            return loc, mfile, ofile
        def mock_open(arg):
            print(f"called path.open with arg '{arg}'")
            return str(arg)
        # hoe laat ik deze ook weer als contextmanager werken?
        # bv return open(str(arg)) maar dan moet dat wel een bestaand file zijn
        def mock_load(arg):
            print(f"called json.load with arg '{arg}'")
            if loc == 'ofile':
                return {'x': 'y'}
            return {'mru': 'items'}
        monkeypatch.setattr(testee, 'get_iniloc', mock_get)
        monkeypatch.setattr(testee.pathlib.Path, 'open', mock_open)
        monkeypatch.setattr(testee.json, 'load', mock_load)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.outopts = {}
        testobj.mru_items = {}
        testobj.save_options_keys = {}
        testobj.p = {}
        monkeypatch.setattr(testee.pathlib.Path, 'exists', lambda *x: False)
        testobj.read_from_ini()
        assert capsys.readouterr().out == ("called get_iniloc with arg 'None'\n")
        monkeypatch.setattr(testee.pathlib.Path, 'exists', lambda *x: True)
        # breakpoint()
        testobj.read_from_ini(path='xx')
        assert capsys.readouterr().out == ("")

    def test_apply_cmdline_options(self, monkeypatch, capsys):
        """unittest for MainFrame.apply_cmdline_options
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.apply_cmdline_options({})
        assert testobj.p == {'zoek': '', 'extlist': [], 'case': False, 'woord': False,
                             'subdirs': False, 'context': False, 'negeer': False}

        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.apply_cmdline_options({'search': 'zoek', 'replace': '', 'summarize': True})
        assert testobj.p == {'zoek': 'zoek', 'vervang': '', 'extlist': [], 'case': False,
                             'woord': False, 'subdirs': False, 'context': False, 'negeer': False}
        assert testobj.outopts['summarize'] is True

    def _test_write_to_ini(self, monkeypatch, capsys):
        """unittest for MainFrame.write_to_ini
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.write_to_ini(path=None) == "expected_result"
        assert capsys.readouterr().out == ("")

    def test_determine_common(self, monkeypatch, capsys):
        """unittest for MainFrame.determine_common
        """
        def mock_commonpath(*args):
            print('called os.path.commonpath with args', args)
            return 'qqq'
        def mock_isfile(arg):
            print(f"called os.path.isfile with arg '{arg}')")
            return 'aaa/bbb'
        monkeypatch.setattr(testee.os.path, 'commonpath', mock_commonpath)
        monkeypatch.setattr(testee.os.path, 'isfile', lambda *x: False)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.p = {'filelist': [testee.pathlib.Path('xxx'), testee.pathlib.Path('yyy')],
                     'pad': testee.pathlib.Path('zzz')}
        testobj.apptype = ''
        assert testobj.determine_common() == f"zzz{testee.os.sep}"
        assert capsys.readouterr().out == ""
        testobj.apptype = 'single'
        assert testobj.determine_common() == testee.pathlib.PosixPath("xxx")
        assert capsys.readouterr().out == ""
        return
        testobj.apptype = 'multi'
        # breakpoint()
        assert testobj.determine_common() == "xxx"
        assert capsys.readouterr().out == ""
        monkeypatch.setattr(testee.os.path, 'isfile', lambda *x: True)
        assert testobj.determine_common() == "xxx"
        assert capsys.readouterr().out == ""

    def test_checkzoek(self, monkeypatch, capsys):
        """unittest for MainFrame.checkzoek
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
        """unittest for MainFrame.checkverv
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.mru_items = {'verv': ['xxx', 'yyy']}
        testobj.s = 'zz'
        testobj.p = {}
        assert testobj.checkverv(['', '']) == ""
        assert testobj.mru_items['verv'] == ['xxx', 'yyy']
        assert testobj.s == 'zz'
        assert testobj.p['vervang'] is None

        testobj.mru_items = {'verv': ['xxx', 'yyy']}
        testobj.s = 'zz'
        testobj.p = {}
        assert testobj.checkverv(['text', False]) == ""
        assert testobj.mru_items['verv'] == ['text', 'xxx', 'yyy']
        assert testobj.s == 'zz\nen vervangen door text'
        assert testobj.p['vervang'] == 'text'

        testobj.mru_items = {'verv': ['xxx', 'yyy']}
        testobj.s = 'zz'
        testobj.p = {}
        assert testobj.checkverv(['xxx', False]) == ""
        assert testobj.mru_items['verv'] == ['xxx', 'yyy']
        assert testobj.s == 'zz\nen vervangen door xxx'
        assert testobj.p['vervang'] == 'xxx'

        testobj.mru_items = {'verv': ['xxx', 'yyy']}
        testobj.s = 'zz'
        testobj.p = {}
        assert testobj.checkverv(['', True]) == ""
        assert testobj.mru_items['verv'] == ['xxx', 'yyy']
        assert testobj.s == 'zz\nen weggehaald'
        assert testobj.p['vervang'] == ''

    def test_checkattr(self, monkeypatch, capsys):
        """unittest for MainFrame.checkattr
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.s = 'zz'
        testobj.p = {}
        assert testobj.checkattr(['xx', False, False]) == ""
        assert testobj.s == 'zz (regular expression)'
        assert testobj.p == {'regexp': 'xx', 'case': False, 'woord': False}
        testobj.s = 'zz'
        testobj.p = {}
        assert testobj.checkattr(['', True, True]) == ""
        assert testobj.s == 'zz (case-sensitive, hele woorden)'
        assert testobj.p == {'regexp': '', 'case': True, 'woord': True}

    def test_checktype(self, monkeypatch, capsys):
        """unittest for MainFrame.checktype
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
        """unittest for MainFrame.checkpath
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
        assert testobj.s == 'xx\nin /home'
        assert testobj.p['pad'] == testee.pathlib.PosixPath('/home')
        assert testobj.p['filelist'] == ''

    def test_checksubs(self, monkeypatch, capsys):
        """unittest for MainFrame.checksubs
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.s = 'zz'
        testobj.p = {}
        testobj.checksubs(['x', 'y', 'z'])
        assert testobj.p == {"subdirs": 'x', "follow_symlinks": 'y', "maxdepth": 'z'}
        assert testobj.s == 'zz en onderliggende directories'
        testobj.s = 'zz'
        testobj.p = {}
        testobj.checksubs(['', '', ''])
        assert testobj.p == {"subdirs": '', "follow_symlinks": '', "maxdepth": ''}
        assert testobj.s == 'zz'

    def _test_doe(self, monkeypatch, capsys):
        """unittest for MainFrame.doe
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.doe() == "expected_result"
        assert capsys.readouterr().out == ("")
