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
        self.gui = types.SimpleNamespace()


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
    def clear_contents(self):
        print('called ResultsGui.clear_contents')
    def breekaf(self, *args, **kwargs):
        print('called ResultsGui.breekaf with args', args, kwargs)
    def set_header(self, text):
        print(f"called ResultsGui.set_header with arg '{text}'")
    def populate_list(self):
        print('called ResultsGui.populate_list')


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
    assert testee.main({'x': 'xx', 'output_file': ''}) == ''
    assert capsys.readouterr().out == (
            f"called pathlib.Path.mkdir with args ({mock_logfile.parent!r},) {{'exist_ok': True}}\n"
            f"called pathlib.Path.touch with args ({mock_logfile!r},) {{'exist_ok': True}}\n"
            "called MainFrame with args () {'x': 'xx', 'output_file': ''}\n")

    monkeypatch.setattr(testee, 'WANT_LOGGING', False)
    assert testee.main({'x': 'xx', 'output_file': ''}) == ''
    assert capsys.readouterr().out == (
            "called MainFrame with args () {'x': 'xx', 'output_file': ''}\n")

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

    monkeypatch.setattr(testee, 'MainFrame', mock_mainframe_2)
    assert testee.main({'appmode': 'xx', 'fname': ['yy'], 'output_file': ''}) == 'message'
    assert capsys.readouterr().out == (
            "called MainFrame with args () {'appmode': 'xx', 'fname': ['yy'], 'output_file': ''}\n")


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

        parent.p = {'context': True, 'vervang': 'xxx'}
        parent.apptype = 'single-file'
        parent.zoekvervang = types.SimpleNamespace(rpt=['gezocht en/of vervangen', 'namelijk 2'])
        monkeypatch.setattr(testee.Results, 'captions', {})
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
                "called TestResults.build_list\n"
                "called ResultsGui.setup_screen with arg"
                " {'heading': 'gezocht en/of 2 vervangen'}\n")

        parent.p['vervang'] = 'xx'
        parent.apptype = 'xxx'
        testobj = testee.Results(parent)
        assert testobj.titel == 'File/Regel'
        assert capsys.readouterr().out == (
                f"called ResultsGui.__init__ with args ({parent}, {testobj})\n"
                "called TestResults.build_list\n"
                "called ResultsGui.setup_screen with arg"
                " {'heading': 'gezocht en/of vervangen (1 items)'}\n")

        parent.apptype = 'multi'
        testobj = testee.Results(parent)
        assert testobj.titel == 'File/Regel'
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

        monkeypatch.setattr(testee, 'common_path_txt', 'where: {}')
        monkeypatch.setattr(testee, 'CSVTextBuf', MockTextBuf)
        monkeypatch.setattr(testee, 'reformat_result', mock_reformat)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.common = 'here'
        testobj.results = ['first line', ('second', 'line')]
        testobj.show_context = False
        testobj.parent.p = {'filelist': ['filename']}

        testobj.gui.get_pth = lambda: False
        testobj.gui.get_csv = lambda: False
        testobj.gui.get_sum = lambda: False
        testobj.parent.apptype = 'multi'
        assert testobj.get_results() == ["first line", 'where: here', '', 'second line']
        assert capsys.readouterr().out == ("")

        testobj.gui.get_pth = lambda: False
        testobj.gui.get_csv = lambda: False
        testobj.gui.get_sum = lambda: False
        testobj.parent.apptype = 'single-file'
        assert testobj.get_results() == ["first line", '', 'r. second line']
        assert capsys.readouterr().out == ("")

        testobj.show_context = True
        testobj.results = ['first line', ('sec r. ond', 'line')]
        testobj.gui.get_pth = lambda: False
        testobj.gui.get_csv = lambda: True
        testobj.gui.get_sum = lambda: True
        testobj.parent.apptype = 'qqq'
        assert testobj.get_results() == ["first line", '', 'textbuf', 'contents']
        assert capsys.readouterr().out == (
                "called CSVTextBuf.__init__ with args ('qqq', False)\n"
                "called CSVTextBuf.write_line with arg '['sec r. ond', 'line']'\n"
                "called CSVTextBuf.get_contents_and_close\n"
                "called reformat_result with args (['first line', '', 'textbuf', 'contents'], py)\n")

        testobj.gui.get_pth = lambda: True
        testobj.gui.get_csv = lambda: False
        testobj.gui.get_sum = lambda: True
        assert testobj.get_results() == ["first line", '', 'sec r. ond line']
        assert capsys.readouterr().out == (
                "called reformat_result with args (['first line', '', 'sec r. ond line'], py)\n")

        testobj.gui.get_pth = lambda: True
        testobj.gui.get_csv = lambda: True
        testobj.gui.get_sum = lambda: True
        assert testobj.get_results() == ["first line", '', 'textbuf', 'contents']
        assert capsys.readouterr().out == (
                "called CSVTextBuf.__init__ with args ('qqq', True)\n"
                "called CSVTextBuf.write_line with arg '['heresec r. ond', 'line']'\n"
                "called CSVTextBuf.get_contents_and_close\n"
                "called reformat_result with args (['first line', '', 'textbuf', 'contents'], py)\n")

        testobj.gui.get_pth = lambda: True
        testobj.gui.get_csv = lambda: False
        testobj.gui.get_sum = lambda: True
        testobj.parent.apptype = 'multi'
        assert testobj.get_results() == ["first line", '', 'heresec r. ond line']
        assert capsys.readouterr().out == (
                "called reformat_result with args (['first line', '', 'heresec r. ond line'], py)\n")

        testobj.gui.get_pth = lambda: True
        testobj.gui.get_csv = lambda: False
        testobj.gui.get_sum = lambda: True
        testobj.parent.apptype = 'single-file'
        assert testobj.get_results() == ["filename first line", '', 'filename r. sec r. ond line']
        assert capsys.readouterr().out == (
                "called reformat_result with args"
                " (['filename first line', '', 'filename r. sec r. ond line'], py)\n")

        testobj.gui.get_pth = lambda: False
        testobj.gui.get_csv = lambda: False
        testobj.gui.get_sum = lambda: True
        testobj.parent.apptype = 'single-file'
        assert testobj.get_results() == ["first line", '', 'r. sec r. ond line']
        assert capsys.readouterr().out == (
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
            print(f'called MainGui.set_waitcursor with arg {value}')
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
        testobj.build_list = mock_build
        testobj.common = 'root'
        testobj.common_path_txt = 'in {}'
        testobj.parent.apptype = ''

        testobj.refresh()
        assert capsys.readouterr().out == (
                "called ResultsGui.clear_contents\n"
                "called MainGui.set_waitcursor with arg True\n"
                "called Findr.go\n"
                "called MainGui.set_waitcursor with arg False\n"
                "called ResultsGui.breekaf with args ('just a header\\nnope',) {'done': False}\n")

        monkeypatch.setattr(MockFindr, 'go', mock_go_2)
        testobj.refresh()
        assert capsys.readouterr().out == (
                "called ResultsGui.clear_contents\n"
                "called MainGui.set_waitcursor with arg True\n"
                "called Findr.go\n"
                "called MainGui.set_waitcursor with arg False\n"
                "called ResultsGui.set_header with arg 'header (1 items)'\n"
                "called TestResults.build_list\n"
                "called ResultsGui.populate_list\n")

        testobj.parent.zoekvervang.p['wijzig'] = True
        testobj.refresh()
        assert capsys.readouterr().out == (
                "called ResultsGui.clear_contents\n"
                "called MainGui.set_waitcursor with arg True\n"
                "called Findr.go\n"
                "called MainGui.set_waitcursor with arg False\n"
                "called ResultsGui.set_header with arg 'header (replace message)'\n"
                "called TestResults.build_list\n"
                "called ResultsGui.populate_list\n")

        monkeypatch.setattr(MockFindr, 'go', mock_go_3)
        testobj.refresh()
        assert capsys.readouterr().out == (
                "called ResultsGui.clear_contents\n"
                "called MainGui.set_waitcursor with arg True\n"
                "called Findr.go\n"
                "called MainGui.set_waitcursor with arg False\n"
                "called ResultsGui.set_header with arg 'header (2 items)'\n"
                "called TestResults.build_list\n"
                "called ResultsGui.populate_list\n")

        testobj.parent.apptype = 'multi'
        testobj.refresh()
        assert capsys.readouterr().out == (
                "called ResultsGui.clear_contents\n"
                "called MainGui.set_waitcursor with arg True\n"
                "called Findr.go\n"
                "called MainGui.set_waitcursor with arg False\n"
                "called ResultsGui.set_header with arg 'header (2 items)\n"
                'De bestanden staan allemaal in of onder de directory "root"\'\n'
                "called TestResults.build_list\n"
                "called ResultsGui.populate_list\n")

        testobj.parent.apptype = 'single'
        testobj.refresh(replace_count=10, replace_text='a pointy stick')
        assert capsys.readouterr().out == (
                "called ResultsGui.clear_contents\n"
                "called MainGui.set_waitcursor with arg True\n"
                "called Findr.go\n"
                "called MainGui.set_waitcursor with arg False\n"
                "called ResultsGui.set_header with arg"
                " '`a needle` with `a pointy stick` replaced 10 in lines\nheader (2 items)'\n"
                "called TestResults.build_list\n"
                "called ResultsGui.populate_list\n")

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
        testobj.parent.apptype = 'single-file'
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
        monkeypatch.setattr(testee.MainFrame, 'setup_options', mock_setup_options)
        monkeypatch.setattr(testee, 'determine_mode_from_input', mock_determine)
        monkeypatch.setattr(testee, 'expand_list_file', mock_expand)
        monkeypatch.setattr(testee.MainFrame, 'apply_cmdline_options', mock_apply_cmdline_options)
        monkeypatch.setattr(testee.MainFrameGui, '__init__', mock_gui)
        monkeypatch.setattr(testee.MainFrameGui, 'setup_screen', mock_gui_setup_screen)
        monkeypatch.setattr(testee.MainFrameGui, 'go', mock_gui_go)
        monkeypatch.setattr(testee.MainFrame, 'doe', mock_doe)

        testobj = testee.MainFrame()
        assert testobj.apptype == 'open'
        assert testobj.p['filelist'] == []
        assert capsys.readouterr().out == ('called setup_options\n'
                                           'called apply_cmdline_options\n'
                                           'called gui instantiation\n'
                                           'called gui.setup_screen\n'
                                           'called gui.go\n')

        monkeypatch.setattr(testee.MainFrame, 'apply_cmdline_options',
                            mock_apply_cmdline_options_nogui)
        testobj = testee.MainFrame()
        assert testobj.apptype == 'open'
        assert testobj.p['filelist'] == []
        assert capsys.readouterr().out == ('called setup_options\n'
                                           'called apply_cmdline_options\n'
                                           'called gui instantiation\n'
                                           'called gui.setup_screen\n'
                                           'called doe\n')

        testobj = testee.MainFrame(fnames=['xxx', 'yyy'])
        assert testobj.apptype == 'single-file'
        assert testobj.p['filelist'] == ['xxx']
        assert capsys.readouterr().out == (
                "called determine_mode_from_input with arg ['xxx', 'yyy']\n"
                'called setup_options\n'
                'called apply_cmdline_options\n'
                'called gui instantiation\n'
                'called gui.setup_screen\n'
                'called doe\n')

        with pytest.raises(ValueError) as exc:
            testobj = testee.MainFrame(fnames=['xxx', 'yyy'], list_file='zzz')
        assert str(exc.value) == 'List-file niet toegestaan bij lijst bestanden'

        testobj = testee.MainFrame(list_file='zzz')
        assert testobj.apptype == 'multi'
        assert testobj.p['filelist'] == ['yyy', 'zzz']
        assert capsys.readouterr().out == (
                "called expand_list_file with arg 'zzz'\n"
                "called determine_mode_from_input with arg expanded list-file\n"
                'called setup_options\n'
                'called apply_cmdline_options\n'
                'called gui instantiation\n'
                'called gui.setup_screen\n'
                'called doe\n')

    def test_get_filename_list(self, monkeypatch, capsys, tmp_path):
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

    def test_read_from_ini(self, monkeypatch, capsys, tmp_path):
        """unittest for MainFrame.read_from_ini
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

    def test_write_to_ini(self, monkeypatch, capsys, tmp_path):
        """unittest for MainFrame.write_to_ini
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
        """unittest for MainFrame.determine_common
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

    def test_setup_parameters(self, monkeypatch, capsys):
        """unittest for MainFrame.setup_parameters
        """
        class MockGui:
            """stub
            """
            def get_searchtext(self):
                print("called MainGui.get_searchtext")
                return 'find'
            def get_replace_args(self):
                print('called MainGui.get_replace_args')
                return 'replace'
            def get_search_attr(self):
                print('called MainGui.get_search_attr')
                return 'attr'
            def get_types_to_search(self):
                print('called MainGui.get_types_to_search')
                return 'types'
            def get_dir_to_search(self):
                print('called MainGui.get_dir_to_search')
                return 'dir'
            def get_subdirs_to_search(self):
                print('called MainGui.get_subdirs_to_search')
                return True, True, 5
            def get_backup(self):
                print('called MainGui.get_backup')
                return True
            def get_ignore(self):
                print('called MainGui.get_ignore')
                return True
            def get_context(self):
                print('called MainGui.get_context')
                return True
        def mock_checkzoek(arg):
            print(f'called MainWindow.checkzoek with arg {arg}')
            return 'message from checkzoek'
        def mock_checkzoek_2(arg):
            print(f'called MainWindow.checkzoek with arg {arg}')
            return ''
        def mock_checkverv(arg):
            print(f'called MainWindow.checkverv with arg {arg}')
            return 'message from checkverv'
        def mock_checkverv_2(arg):
            print(f'called MainWindow.checkverv with arg {arg}')
            return ''
        def mock_checkattr(arg):
            print(f'called MainWindow.checkattr with arg {arg}')
            return 'message from checkattr'
        def mock_checkattr_2(arg):
            print(f'called MainWindow.checkattr with arg {arg}')
            return ''
        def mock_checktype(arg):
            print(f'called MainWindow.checktype with arg {arg}')
            return 'message from checktype'
        def mock_checktype_2(arg):
            print(f'called MainWindow.checktype with arg {arg}')
            return ''
        def mock_checkpath(arg):
            print(f'called MainWindow.checkpath with arg {arg}')
            return 'message from checkpath'
        def mock_checkpath_2(arg):
            print(f'called MainWindow.checkpath with arg {arg}')
            return ''
        def mock_get_subdirs():
            print('called MainGui.get_subdirs_to_search')
            return False, False, 0
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.checkzoek = mock_checkzoek
        testobj.checkverv = mock_checkverv
        testobj.checkattr = mock_checkattr
        testobj.checktype = mock_checktype
        testobj.checkpath = mock_checkpath
        testobj.gui = MockGui()
        testobj.s = 'zz'
        testobj.p = {}
        assert testobj.setup_parameters() == 'message from checkzoek'
        assert testobj.p == {}
        assert testobj.s == 'zz'
        assert capsys.readouterr().out == ("called MainGui.get_searchtext\n"
                                           "called MainWindow.checkzoek with arg find\n")

        testobj.checkzoek = mock_checkzoek_2
        testobj.s = 'zz'
        testobj.p = {}
        assert testobj.setup_parameters() == 'message from checkverv'
        assert testobj.p == {}
        assert testobj.s == 'zz'
        assert capsys.readouterr().out == ("called MainGui.get_searchtext\n"
                                           "called MainWindow.checkzoek with arg find\n"
                                           "called MainGui.get_replace_args\n"
                                           "called MainWindow.checkverv with arg replace\n")

        testobj.checkverv = mock_checkverv_2
        testobj.s = 'zz'
        testobj.p = {}
        assert testobj.setup_parameters() == 'message from checkattr'
        assert testobj.p == {}
        assert testobj.s == 'zz'
        assert capsys.readouterr().out == ("called MainGui.get_searchtext\n"
                                           "called MainWindow.checkzoek with arg find\n"
                                           "called MainGui.get_replace_args\n"
                                           "called MainWindow.checkverv with arg replace\n"
                                           "called MainGui.get_search_attr\n"
                                           "called MainWindow.checkattr with arg attr\n")

        testobj.checkattr = mock_checkattr_2
        testobj.apptype = 'not single'
        testobj.s = 'zz'
        testobj.p = {'filelist': ['xx']}
        assert testobj.setup_parameters() == 'message from checktype'
        assert testobj.p == {'filelist': ['xx']}
        assert testobj.s == 'zz'
        assert capsys.readouterr().out == ("called MainGui.get_searchtext\n"
                                           "called MainWindow.checkzoek with arg find\n"
                                           "called MainGui.get_replace_args\n"
                                           "called MainWindow.checkverv with arg replace\n"
                                           "called MainGui.get_search_attr\n"
                                           "called MainWindow.checkattr with arg attr\n"
                                           "called MainGui.get_types_to_search\n"
                                           "called MainWindow.checktype with arg types\n")

        testobj.checktype = mock_checktype_2
        testobj.s = 'zz'
        testobj.p = {'filelist': ['xx']}
        testobj.apptype = 'open'
        assert testobj.setup_parameters() == 'message from checkpath'
        assert testobj.p == {'filelist': ['xx']}
        assert testobj.s == 'zz'
        assert capsys.readouterr().out == ("called MainGui.get_searchtext\n"
                                           "called MainWindow.checkzoek with arg find\n"
                                           "called MainGui.get_replace_args\n"
                                           "called MainWindow.checkverv with arg replace\n"
                                           "called MainGui.get_search_attr\n"
                                           "called MainWindow.checkattr with arg attr\n"
                                           "called MainGui.get_types_to_search\n"
                                           "called MainWindow.checktype with arg types\n"
                                           "called MainGui.get_dir_to_search\n"
                                           "called MainWindow.checkpath with arg dir\n")

        testobj.checkpath = mock_checkpath_2
        testobj.s = 'zz'
        testobj.apptype = 'not single'
        testobj.p = {'filelist': ['xx']}
        assert testobj.setup_parameters() == ''
        assert testobj.p == {'filelist': ['xx'],
                             'subdirs': True, 'follow_symlinks': True, 'maxdepth': 5,
                             'backup': True, 'negeer': True, 'context': True}
        assert testobj.s == 'zz en onderliggende directories'
        assert capsys.readouterr().out == ("called MainGui.get_searchtext\n"
                                           "called MainWindow.checkzoek with arg find\n"
                                           "called MainGui.get_replace_args\n"
                                           "called MainWindow.checkverv with arg replace\n"
                                           "called MainGui.get_search_attr\n"
                                           "called MainWindow.checkattr with arg attr\n"
                                           "called MainGui.get_types_to_search\n"
                                           "called MainWindow.checktype with arg types\n"
                                           "called MainGui.get_subdirs_to_search\n"
                                           "called MainGui.get_backup\n"
                                           "called MainGui.get_ignore\n"
                                           "called MainGui.get_context\n")

        testobj.gui.get_subdirs_to_search = mock_get_subdirs
        testobj.s = 'zz'
        testobj.apptype = 'not single'
        testobj.p = {'filelist': ['xx']}
        assert testobj.setup_parameters() == ''
        assert testobj.p == {'filelist': ['xx'],
                             'subdirs': False, 'follow_symlinks': False, 'maxdepth': 0,
                             'backup': True, 'negeer': True, 'context': True}
        assert testobj.s == 'zz'
        assert capsys.readouterr().out == ("called MainGui.get_searchtext\n"
                                           "called MainWindow.checkzoek with arg find\n"
                                           "called MainGui.get_replace_args\n"
                                           "called MainWindow.checkverv with arg replace\n"
                                           "called MainGui.get_search_attr\n"
                                           "called MainWindow.checkattr with arg attr\n"
                                           "called MainGui.get_types_to_search\n"
                                           "called MainWindow.checktype with arg types\n"
                                           "called MainGui.get_subdirs_to_search\n"
                                           "called MainGui.get_backup\n"
                                           "called MainGui.get_ignore\n"
                                           "called MainGui.get_context\n")

        testobj.apptype = 'single'
        testobj.s = 'zz'
        testobj.p = {}
        assert testobj.setup_parameters() == ''
        assert testobj.p == {'subdirs': False, 'follow_symlinks': False, 'maxdepth': 0,
                             'backup': True, 'negeer': True, 'context': True}
        assert testobj.s == 'zz'
        assert capsys.readouterr().out == ("called MainGui.get_searchtext\n"
                                           "called MainWindow.checkzoek with arg find\n"
                                           "called MainGui.get_replace_args\n"
                                           "called MainWindow.checkverv with arg replace\n"
                                           "called MainGui.get_search_attr\n"
                                           "called MainWindow.checkattr with arg attr\n"
                                           "called MainGui.get_types_to_search\n"
                                           "called MainWindow.checktype with arg types\n"
                                           "called MainGui.get_subdirs_to_search\n"
                                           "called MainGui.get_backup\n"
                                           "called MainGui.get_ignore\n"
                                           "called MainGui.get_context\n")

        testobj.apptype = 'single-file'
        testobj.s = 'zz'
        testobj.p = {'filelist': [testee.pathlib.Path('/tmp')], 'follow_symlinks': False}
        assert testobj.setup_parameters() == ''
        assert testobj.p == {'filelist': [testee.pathlib.Path('/tmp')],
                             'follow_symlinks': False,
                             'backup': True, 'negeer': True, 'context': True}
        assert testobj.s == 'zz'
        assert capsys.readouterr().out == ("called MainGui.get_searchtext\n"
                                           "called MainWindow.checkzoek with arg find\n"
                                           "called MainGui.get_replace_args\n"
                                           "called MainWindow.checkverv with arg replace\n"
                                           "called MainGui.get_search_attr\n"
                                           "called MainWindow.checkattr with arg attr\n"
                                           "called MainGui.get_backup\n"
                                           "called MainGui.get_ignore\n"
                                           "called MainGui.get_context\n")

        monkeypatch.setattr(testee.pathlib.Path, 'is_symlink', lambda x: True)
        testobj.apptype = 'single-file'
        testobj.s = 'zz'
        testobj.p = {'filelist': [testee.pathlib.Path('/tmp')], 'follow_symlinks': False}
        assert testobj.setup_parameters() == ''
        assert testobj.p == {'filelist': [testee.pathlib.Path('/tmp')],
                             'follow_symlinks': True,
                             'backup': True, 'negeer': True, 'context': True}
        assert testobj.s == 'zz'
        assert capsys.readouterr().out == ("called MainGui.get_searchtext\n"
                                           "called MainWindow.checkzoek with arg find\n"
                                           "called MainGui.get_replace_args\n"
                                           "called MainWindow.checkverv with arg replace\n"
                                           "called MainGui.get_search_attr\n"
                                           "called MainWindow.checkattr with arg attr\n"
                                           "called MainGui.get_backup\n"
                                           "called MainGui.get_ignore\n"
                                           "called MainGui.get_context\n")

    def test_show_results(self, monkeypatch, capsys, tmp_path):
        """unittest for MainFrame.show_results
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
            print('called MainWindow.determine_common')
            return 'common_root'
        def mock_meld(*args):
            print('called MainGui.meld with args', args)
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
                "called MainGui.meld with args ('showing results', 'No results')\n")

        testobj.zoekvervang.ok = False
        testobj.show_results()
        assert capsys.readouterr().out == (
                "called MainGui.meld with args ('showing results', 'No results')\n")

        testobj.extraopts['output_file'] = outfilename.open('w')
        testobj.show_results()
        assert outfilename.read_text() == 'No results\n'
        assert capsys.readouterr().out == ''

        testobj.zoekvervang.rpt = ['header', 'result line']
        testobj.extraopts['output_file'] = None
        testobj.show_results()
        assert capsys.readouterr().out == (
                "called MainWindow.determine_common\n"
                f"called Results.__init__ with args ({testobj}, 'common_root')\n"
                "called Results.show\n")

        testobj.extraopts['output_file'] = outfilename.open('w')
        testobj.show_results()
        assert outfilename.read_text() == 'xx\nyy\n'
        assert capsys.readouterr().out == (
                "called MainWindow.determine_common\n"
                f"called Results.__init__ with args ({testobj}, 'common_root')\n"
                "called Results.get_results\n")

    def test_select_search_exclusions_if_requested(self, monkeypatch, capsys):
        """unittest for MainFrame.select_search_exclusions_if_requested
        """
        class MockSelectNames:
            """stub
            """
            def __init__(self, *args, **kwargs):
                print('called Selectnames.__init__ with args', args, kwargs)
            def show(self):
                print('called Selectnames.show')
                return False, []
            def show_2(self):
                print('called Selectnames.show')
                return True, ['aaa', 'bbb']
        def mock_remove(names):
            print(f'called MainWindow.remove_files_in_selected_directories with arg {names}')
        monkeypatch.setattr(testee, 'SelectNames', MockSelectNames)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.remove_files_in_selected_directories = mock_remove
        testobj.zoekvervang = types.SimpleNamespace(dirnames=[], filenames=[])
        testobj.gui = types.SimpleNamespace(get_skipdirs=lambda: False,
                                            get_skipfiles=lambda: False)
        assert not testobj.select_search_exclusions_if_requested()
        assert capsys.readouterr().out == ("")

        testobj.zoekvervang.dirnames = ['xxx', 'yyy']
        testobj.gui = types.SimpleNamespace(get_skipdirs=lambda: True,
                                            get_skipfiles=lambda: False)
        assert testobj.select_search_exclusions_if_requested()
        assert testobj.zoekvervang.filenames == []
        assert capsys.readouterr().out == (
                f"called Selectnames.__init__ with args ({testobj},) {{'files': False}}\n"
                "called Selectnames.show\n")

        testobj.zoekvervang.dirnames = ['xxx', 'yyy']
        testobj.zoekvervang.filenames = ['aaa', 'bbb', 'ccc', 'ddd']
        testobj.gui = types.SimpleNamespace(get_skipdirs=lambda: False,
                                            get_skipfiles=lambda: True)
        assert testobj.select_search_exclusions_if_requested()
        assert testobj.zoekvervang.filenames == ['aaa', 'bbb', 'ccc', 'ddd']
        assert capsys.readouterr().out == (
                f"called Selectnames.__init__ with args ({testobj},) {{}}\n"
                "called Selectnames.show\n")

        monkeypatch.setattr(MockSelectNames, 'show', MockSelectNames.show_2)
        monkeypatch.setattr(testee, 'SelectNames', MockSelectNames)
        testobj.zoekvervang.dirnames = ['xxx', 'yyy']
        testobj.zoekvervang.filenames = []
        testobj.gui = types.SimpleNamespace(get_skipdirs=lambda: True,
                                            get_skipfiles=lambda: False)
        assert not testobj.select_search_exclusions_if_requested()
        assert capsys.readouterr().out == (
                f"called Selectnames.__init__ with args ({testobj},) {{'files': False}}\n"
                "called Selectnames.show\n")

        testobj.zoekvervang.dirnames = ['xxx', 'yyy']
        testobj.zoekvervang.filenames = ['aaa', 'bbb', 'ccc', 'ddd']
        testobj.gui = types.SimpleNamespace(get_skipdirs=lambda: False,
                                            get_skipfiles=lambda: True)
        assert not testobj.select_search_exclusions_if_requested()
        assert testobj.zoekvervang.filenames == ['aaa', 'bbb']
        assert capsys.readouterr().out == (
                f"called Selectnames.__init__ with args ({testobj},) {{}}\n"
                "called Selectnames.show\n")

    def test_remove_files_in_selected_dirs(self, monkeypatch, capsys):
        """unittest for MainFrame.remove_files_in_selected_dirs
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

    def test_doe(self, monkeypatch, capsys, tmp_path):
        """unittest for MainFrame.doe
        """
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
            print('called MainWindow.setup_parameters')
            return 'xxx'
        def mock_setup_2():
            print('called MainWindow.setup_parameters')
            return ''
        def mock_write(arg):
            print(f'called MainWindow.write_to_ini with arg {arg}')
        def mock_select():
            print('called MainWindow.select_search_exclusions_if_requested')
            return True
        def mock_select_2():
            print('called MainWindow.select_search_exclusions_if_requested')
            return False
        def mock_show():
            print('called MainWindow.show_results')
        class MockGui:
            """stub
            """
            def error(self, *args):
                print('called MainGui.error with args', args)
            def meld(self, *args):
                print('called MainGui.meld with args', args)
            def add_item_to_searchlist(self, arg):
                print(f'called MainGui.add_item_to_searchlist with arg {arg}')
            def set_waitcursor(self, value):
                print(f'called MainGui.set_waitcursor with arg {value}')
            def get_exit(self):
                print('called MainGui.get_exit')
                return False
            def einde(self):
                print('called MainGui.einde')
        monkeypatch.setattr(testee, 'Finder', MockFinder)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.gui = MockGui()
        testobj.write_to_ini = mock_write
        testobj.select_search_exclusions_if_requested = mock_select
        testobj.show_results = mock_show
        testobj.fouttitel = 'error:'
        testobj.resulttitel = 'results:'
        testobj.p = {'zoek': 'find_me', 'vervang': None}
        testobj.setup_parameters = mock_setup
        testobj.doe()
        assert capsys.readouterr().out == ("called MainWindow.setup_parameters\n"
                                           "called MainGui.error with args ('error:', 'xxx')\n")

        testobj.setup_parameters = mock_setup_2
        testobj.extraopts['dont_save'] = True
        testobj.doe()
        assert capsys.readouterr().out == (
                "called MainWindow.setup_parameters\n"
                "called MainGui.add_item_to_searchlist with arg find_me\n"
                "called Finder.__init__ with args {'zoek': 'find_me', 'vervang': None}\n"
                "called MainGui.error with args ('error:', 'init fout')\n")

        MockFinder.__init__ = mockfinder_init_2
        testobj.doe()
        assert capsys.readouterr().out == (
                "called MainWindow.setup_parameters\n"
                "called MainGui.add_item_to_searchlist with arg find_me\n"
                "called Finder.__init__ with args {'zoek': 'find_me', 'vervang': None}\n"
                "called Finder.setup_search\n"
                "called MainGui.meld with args ('results:', 'header\\nmessage')\n")

        MockFinder.setup_search = mockfinder_setup_search_2
        testobj.extraopts['dont_save'] = False
        testobj.p['filelist'] = [tmp_path]
        # breakpoint()
        testobj.doe()
        assert capsys.readouterr().out == (
                "called MainWindow.setup_parameters\n"
                "called MainGui.add_item_to_searchlist with arg find_me\n"
                f"called MainWindow.write_to_ini with arg {tmp_path.parent}\n"
                "called Finder.__init__ with args"
                f" {{'zoek': 'find_me', 'vervang': None, 'filelist': [{tmp_path!r}]}}\n"
                "called Finder.setup_search\n"
                "called MainGui.meld with args ('results:', 'Geen bestanden om te doorzoeken')\n")

        MockFinder.setup_search = mockfinder_setup_search_3
        testobj.p['pad'] = 'xxx'
        testobj.apptype = 'not single-file'
        testobj.doe()
        assert capsys.readouterr().out == (
            "called MainWindow.setup_parameters\n"
            "called MainGui.add_item_to_searchlist with arg find_me\n"
            f"called MainWindow.write_to_ini with arg {testee.HERE.parent}/xxx\n"
            "called Finder.__init__ with args"
            f" {{'zoek': 'find_me', 'vervang': None, 'filelist': [{tmp_path!r}], 'pad': 'xxx'}}\n"
            "called Finder.setup_search\n"
            "called MainWindow.select_search_exclusions_if_requested\n")

        testobj.p.pop('pad')
        testobj.extraopts['dont_save'] = True
        testobj.select_search_exclusions_if_requested = mock_select_2
        testobj.extraopts['no_gui'] = False
        testobj.extraopts['output_file'] = 'ofile'
        testobj.doe()
        assert capsys.readouterr().out == (
                "called MainWindow.setup_parameters\n"
                "called MainGui.add_item_to_searchlist with arg find_me\n"
                "called Finder.__init__ with args"
                f" {{'zoek': 'find_me', 'vervang': None, 'filelist': {testobj.p['filelist']}}}\n"
                "called Finder.setup_search\n"
                "called MainWindow.select_search_exclusions_if_requested\n"
                "called MainGui.set_waitcursor with arg True\n"
                "called Finder.go\n"
                "called MainGui.set_waitcursor with arg False\n"
                "called MainWindow.show_results\n"
                "called MainGui.get_exit\n")

        testobj.extraopts['no_gui'] = True
        testobj.extraopts['output_file'] = ''
        testobj.doe()
        assert capsys.readouterr().out == (
                "called MainWindow.setup_parameters\n"
                "called MainGui.add_item_to_searchlist with arg find_me\n"
                "called Finder.__init__ with args"
                f" {{'zoek': 'find_me', 'vervang': None, 'filelist': {testobj.p['filelist']}}}\n"
                "called Finder.setup_search\n"
                "called MainWindow.select_search_exclusions_if_requested\n"
                "called MainGui.set_waitcursor with arg True\n"
                "called Finder.go\n"
                "called MainGui.set_waitcursor with arg False\n"
                "called MainWindow.show_results\n"
                "called MainGui.get_exit\n")

        testobj.extraopts['output_file'] = 'ofile'
        testobj.doe()
        assert capsys.readouterr().out == (
                "called MainWindow.setup_parameters\n"
                "called MainGui.add_item_to_searchlist with arg find_me\n"
                "called Finder.__init__ with args"
                f" {{'zoek': 'find_me', 'vervang': None, 'filelist': {testobj.p['filelist']}}}\n"
                "called Finder.setup_search\n"
                "called MainWindow.select_search_exclusions_if_requested\n"
                "called MainGui.set_waitcursor with arg True\n"
                "called Finder.go\n"
                "called MainGui.set_waitcursor with arg False\n"
                "called MainWindow.show_results\n"
                "called MainGui.einde\n")

        testobj.extraopts['no_gui'] = False
        testobj.extraopts['output_file'] = ''
        testobj.p['vervang'] = ''
        testobj.doe()
        assert capsys.readouterr().out == (
                "called MainWindow.setup_parameters\n"
                "called MainGui.add_item_to_searchlist with arg find_me\n"
                "called Finder.__init__ with args"
                f" {{'zoek': 'find_me', 'vervang': '', 'filelist': {testobj.p['filelist']}}}\n"
                "called Finder.setup_search\n"
                "called MainWindow.select_search_exclusions_if_requested\n"
                "called MainGui.set_waitcursor with arg True\n"
                "called Finder.go\n"
                "called MainGui.set_waitcursor with arg False\n"
                "called MainWindow.show_results\n"
                "called MainGui.get_exit\n")

        testobj.gui.get_exit = lambda: True
        testobj.p['vervang'] = None
        testobj.doe()
        assert capsys.readouterr().out == (
                "called MainWindow.setup_parameters\n"
                "called MainGui.add_item_to_searchlist with arg find_me\n"
                "called Finder.__init__ with args"
                f" {{'zoek': 'find_me', 'vervang': None, 'filelist': {testobj.p['filelist']}}}\n"
                "called Finder.setup_search\n"
                "called MainWindow.select_search_exclusions_if_requested\n"
                "called MainGui.set_waitcursor with arg True\n"
                "called Finder.go\n"
                "called MainGui.set_waitcursor with arg False\n"
                "called MainWindow.show_results\n")

        testobj.p['vervang'] = ''
        testobj.doe()
        assert capsys.readouterr().out == (
                "called MainWindow.setup_parameters\n"
                "called MainGui.add_item_to_searchlist with arg find_me\n"
                "called Finder.__init__ with args"
                f" {{'zoek': 'find_me', 'vervang': '', 'filelist': {testobj.p['filelist']}}}\n"
                "called Finder.setup_search\n"
                "called MainWindow.select_search_exclusions_if_requested\n"
                "called MainGui.set_waitcursor with arg True\n"
                "called Finder.go\n"
                "called MainGui.set_waitcursor with arg False\n"
                "called MainWindow.show_results\n"
                "called MainGui.einde\n")
