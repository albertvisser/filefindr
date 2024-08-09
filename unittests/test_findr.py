"""unittests for ./afrift/findr_files.py
"""
import types
import pytest
from afrift import findr_files as testee


def test_determine_split():
    """unittest for findr_files.determine_split
    """
    assert testee.determine_split('None', 'whatever') == 3
    assert testee.determine_split('py', ['', '', '', 'class', '', '', '', '']) == 5
    assert testee.determine_split('py', ['', '', '', 'class', '', 'docstring', '', '']) == 6
    assert testee.determine_split('py', ['', '', '', 'class', '', 'method', '', '']) == 7
    assert testee.determine_split('py', ['', '', '', 'class', '', 'method', '', 'comment']) == 8
    assert testee.determine_split('py', ['', '', '', 'function', '', '']) == 5
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

# moved to PyRead class
# def test_is_single_line_docstring(monkeypatch, capsys):
#     """unittest for findr_files.is_single_line_docstring
#     """
#     assert not testee.is_single_line_docstring('hello')
#     assert testee.is_single_line_docstring('"hello"')
#     assert not testee.is_single_line_docstring('"hello')
#     assert not testee.is_single_line_docstring('""hello""')
#     assert testee.is_single_line_docstring('"""hello"""')
#     assert not testee.is_single_line_docstring('"""hello')
#     assert testee.is_single_line_docstring("'hello'")
#     assert not testee.is_single_line_docstring("'hello")
#     assert not testee.is_single_line_docstring("''hello''")
#     assert testee.is_single_line_docstring("'''hello'''")
#     assert not testee.is_single_line_docstring("'''hello")


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


def test_read_input_file(tmp_path):
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


class TestPyRead:
    """unittests for findr_files.PyRead
    """
    def setup_testobj(self, monkeypatch, capsys):
        """testdouble for findr_files.PyRead object

        create the object skipping the normal initialization
        intercept messages during creation
        return the object so that other methods can be monkeypatched in the caller
        """
        def mock_init(self):
            """stub
            """
            print('called PyRead.__init__')
        monkeypatch.setattr(testee.PyRead, '__init__', mock_init)
        testobj = testee.PyRead()
        assert capsys.readouterr().out == 'called PyRead.__init__\n'
        return testobj

    def test_init(self, monkeypatch, capsys):
        """unittest for PyRead.__init__
        """
        def mock_read(*args):
            print('called read_input_file with args', args)
            return []
        def mock_read_2(*args):
            print('called read_input_file with args', args)
            return ['xxx\n']
        monkeypatch.setattr(testee, 'read_input_file', mock_read)
        with pytest.raises(EOFError) as exc:
            testee.PyRead('testfile')
        assert str(exc.value) == 'No lines in file'
        assert capsys.readouterr().out == (
                "called read_input_file with args ('testfile', 'latin-1')\n")

        monkeypatch.setattr(testee, 'read_input_file', mock_read_2)
        testobj = testee.PyRead('testfile')
        assert testobj.lines == ['xxx\n']
        assert not testobj.negeer_docs
        assert testobj.itemlist == []
        assert testobj.modlevel_start == 1
        assert testobj.constructs == []
        assert testobj.in_construct == []
        assert testobj.docstring == ''
        assert testobj.docstring_start == 0
        assert testobj.docstring_delim == ''
        assert testobj.indentpos == 0
        assert testobj.prev_lineno == 0
        assert not testobj.start_of_code
        assert capsys.readouterr().out == (
                "called read_input_file with args ('testfile', 'latin-1')\n")

        testobj = testee.PyRead('testfile', 'qqq', True)
        assert testobj.lines == ['xxx\n']
        assert testobj.negeer_docs
        assert testobj.itemlist == []
        assert testobj.modlevel_start == 1
        assert testobj.constructs == []
        assert testobj.in_construct == []
        assert testobj.docstring == ''
        assert testobj.docstring_start == 0
        assert testobj.docstring_delim == ''
        assert testobj.indentpos == 0
        assert testobj.prev_lineno == 0
        assert not testobj.start_of_code
        assert capsys.readouterr().out == (
                "called read_input_file with args ('testfile', 'qqq')\n")

    def test_go(self, monkeypatch, capsys):
        """unittest for PyRead.go
        """
        def mock_process():
            print('called PyRead.process_codelines')
        def mock_build():
            print('called PyRead.build_contexts')
        def mock_filter():
            print('called PyRead.filter_comments')
            return ['xxx', 'yyy']
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.itemlist = ['yyy', 'xxx']
        testobj.process_codelines = mock_process
        testobj.build_contexts = mock_build
        testobj.filter_comments = mock_filter
        assert testobj.go() == ['xxx', 'yyy']
        assert capsys.readouterr().out == ("called PyRead.process_codelines\n"
                                           # "called PyRead.build_contexts\n"
                                           # "called PyRead.filter_comments\n")
                                           "called PyRead.build_contexts\n")

    def test_process_codelines(self, monkeypatch, capsys):
        """unittest for PyRead.process_codelines
        """
        def mock_analyze(*args):
            print('called PyRead.analyze_line with args', args)
            return args[1]
        def mock_pop(lineno):
            print(f"called PyRead.pop_construct with arg {lineno}")
        def mock_build(*args, **kwargs):
            print("called PyRead.build_comment_context with args", args, kwargs)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.analyze_line = mock_analyze
        testobj.pop_construct = mock_pop
        testobj.build_comment_context = mock_build
        testobj.lines = []
        testobj.prev_lineno = 1
        testobj.in_construct = []
        testobj.process_codelines()
        assert testobj.indentpos == 0
        assert capsys.readouterr().out == "called PyRead.pop_construct with arg 0\n"
        testobj.lines = ['']
        testobj.process_codelines()
        assert testobj.indentpos == 0
        assert capsys.readouterr().out == ("called PyRead.analyze_line with args (1, '')\n"
                                           "called PyRead.pop_construct with arg 0\n")
        testobj.lines = ['   xxxx', 'yyyy # zzz']
        # testobj.itemlist = []
        testobj.process_codelines()
        assert testobj.indentpos == 0
        # assert testobj.itemlist == [((2, 5), (2, -1), 'comment')]
        assert capsys.readouterr().out == (
            "called PyRead.analyze_line with args (1, '   xxxx')\n"
            "called PyRead.pop_construct with arg 1\n"
            "called PyRead.analyze_line with args (2, 'yyyy # zzz')\n"
            "called PyRead.pop_construct with arg 1\n"
            "called PyRead.build_comment_context with args (2, 2, 5) {'context_type': 'comment'}\n"
            "called PyRead.pop_construct with arg 1\n")
        # testobj.itemlist = []
        testobj.in_construct = []
        testobj.lines = ['def myfunction(arg1, arg2):', 'class MyClass: # a class']
        testobj.process_codelines()
        assert testobj.indentpos == 0
        # assert testobj.itemlist == [((2, 15), (2, -1), 'comment')]
        assert capsys.readouterr().out == (
            "called PyRead.analyze_line with args (1, 'def myfunction(arg1, arg2):')\n"
            "called PyRead.pop_construct with arg 2\n"
            "called PyRead.analyze_line with args (2, 'class MyClass: # a class')\n"
            "called PyRead.pop_construct with arg 1\n"
            "called PyRead.build_comment_context with args (2, 2, 15) {'context_type': 'comment'}\n"
            "called PyRead.pop_construct with arg 1\n")

    def test_build_contexts(self, monkeypatch, capsys):
        """unittest for PyRead.build_contexts
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.itemlist = []
        testobj.constructs = [(('', 'import', 'os', 1, 1),)]
        testobj.build_contexts()
        assert testobj.itemlist == [((1, 0), (1, -1), 'import os'),]
        testobj.itemlist = []
        testobj.constructs = [(('', 'class', 'TestClass', ''), ('', 'def', 'testmethod', 1, 2)),
                              (('', 'def', 'testfunction', 3, 4),)]
        testobj.build_contexts()
        assert testobj.itemlist == [((2, 0), (2, -1), 'class TestClass method testmethod'),
                                    ((4, 0), (4, -1), 'function testfunction')]

    def test_filter_comments(self, monkeypatch, capsys):
        """unittest for PyRead.filter_comments
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.itemlist = []
        assert testobj.filter_comments() == []
        testobj.itemlist = [(3, 4, 'xxx'), (1, 2, 'docstring'), (5, 5, 'comment')]
        testobj.negeer_docs = True
        assert testobj.filter_comments() == [(3, 4, 'xxx')]
        testobj.negeer_docs = False
        assert testobj.filter_comments() == [(1, 2, 'docstring'), (3, 4, 'xxx'), (5, 5, 'comment', )]

    def test_analyze_line(self, monkeypatch, capsys):
        """unittest for PyRead.analyze_line
        """
        def mock_add(*args):
            print('called PyRead.add_context with args', args)
        def mock_build(*args, **kwargs):
            print("called PyRead.build_comment_context with args", args, kwargs)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.add_context = mock_add
        testobj.build_comment_context = mock_build
        testobj.docstring_delim = ''
        testobj.itemlist = []
        testobj.modlevel_start = 1
        testobj.lines = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        testobj.start_of_code = True
        assert testobj.analyze_line(10, '    xxxx yyyy zzzz') == 'xxxx yyyy zzzz'
        assert testobj.indentpos == 4

        testobj.start_of_code = False
        assert testobj.analyze_line(10, '    xxxx yyyy zzzz') == 'xxxx yyyy zzzz'
        assert testobj.indentpos == 4
        assert testobj.start_of_code
        assert testobj.itemlist == [((1, 0), (9, -1), 'module level code')]

        testobj.docstring_delim = 'xxx'
        testobj.docstring_start = 3
        assert testobj.analyze_line(5, '    last line of docstring xxx') == ''
        assert testobj.docstring_delim == ''
        assert testobj.modlevel_start == 1
        assert capsys.readouterr().out == (
                "called PyRead.build_comment_context with args (3, 5, 4) {'advance_lineno': 5}\n")

        testobj.docstring_delim = 'xxx'
        assert testobj.analyze_line(5, '    xxx # is not the end of this line') == ''
        assert testobj.modlevel_start == 1
        assert capsys.readouterr().out == (
            "called PyRead.build_comment_context with args (3, 5, 4) {'advance_lineno': 5}\n"
            "called PyRead.build_comment_context with args (5, 5, 8) {'context_type': 'comment'}\n")
        # commentaar op zelfde regel als docstring eind-delimiter, niet erg waarschijnlijk

        testobj.docstring_delim = 'xxx'
        assert testobj.analyze_line(5, '    xxx is not the end of this line') == (
                'is not the end of this line')
        assert testobj.modlevel_start == 1
        assert capsys.readouterr().out == (
                "called PyRead.build_comment_context with args (3, 5, 4) {'advance_lineno': 5}\n")
        # tekst op zelfde regel als einde-docstring, kan eigenlijk niet (syntax error bij uitvoeren)

        testobj.docstring_delim = ''
        # testobj.itemlist = []
        assert testobj.analyze_line(5, '   # this is a comment') == ''
        assert testobj.modlevel_start == 1
        assert capsys.readouterr().out == (
            "called PyRead.build_comment_context with args (5, 5, 3) {'context_type': 'comment'}\n")

        testobj.start_of_code = False
        testobj.docstring_start = 0
        assert testobj.analyze_line(5, '   """complete docstring"""') == ''
        assert testobj.docstring_delim == ''
        assert testobj.docstring_start == 5
        # assert testobj.itemlist == [((5, 3), (5, -1), 'docstring')]
        assert testobj.modlevel_start == 6
        assert capsys.readouterr().out == (
                'called PyRead.build_comment_context with args (5, 5, 3) {}\n')

        testobj.itemlist = []
        testobj.modlevel_start = 1
        testobj.docstring_start = 0
        assert testobj.analyze_line(5, '   """start of a docstring') == ''
        assert testobj.docstring_delim == '"""'
        assert testobj.docstring_start == 5
        assert testobj.itemlist == []
        assert testobj.modlevel_start == 6
        assert capsys.readouterr().out == ''

        testobj.docstring_delim = ''
        testobj.docstring_start = 0
        testobj.modlevel_start = 1
        assert testobj.analyze_line(5, '   "complete docstring"') == ''
        assert testobj.docstring_delim == ''
        assert testobj.docstring_start == 0
        assert testobj.itemlist == []
        assert testobj.modlevel_start == 1
        assert capsys.readouterr().out == (
                "called PyRead.build_comment_context with args (5, 5, 3) {'advance_lineno': 5}\n")

    def test_build_comment_context(self, monkeypatch, capsys):
        """unittest for PyRead.build_comment_context
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.in_construct = [(0, 'def', 'functienaam', 9)]
        testobj.itemlist = []
        testobj.start_of_code = True
        testobj.modlevel_start = 5
        testobj.build_comment_context(1, 2)
        assert testobj.itemlist == [((1, 0), (2, -1), 'function functienaam docstring')]
        assert testobj.modlevel_start == 5
        testobj.in_construct = [(0, 'class', 'classnaam', 9)]
        testobj.itemlist = []
        testobj.start_of_code = False
        testobj.modlevel_start = 5
        testobj.build_comment_context(1, 2, 3, 4, 'comment', 1)
        assert testobj.itemlist == [((1, 3), (2, 4), 'class classnaam comment')]
        assert testobj.modlevel_start == 2
        testobj.in_construct = [(0, 'def', 'functienaam', 9), (4, 'def', 'functienaam', 11)]
        testobj.itemlist = []
        testobj.start_of_code = True
        testobj.modlevel_start = 5
        testobj.build_comment_context(1, 2, advance_lineno=0)
        assert testobj.itemlist == [((1, 0), (2, -1),
                                     'function functienaam function functienaam docstring')]
        assert testobj.modlevel_start == 5
        testobj.in_construct = [(0, 'class', 'classnaam', 9), (4, 'def', 'methodnaam', 11)]
        testobj.itemlist = []
        testobj.start_of_code = False
        testobj.modlevel_start = 5
        testobj.build_comment_context(1, 2)
        assert testobj.itemlist == [((1, 0), (2, -1),
                                     'class classnaam method methodnaam docstring')]
        assert testobj.modlevel_start == 5
        testobj.in_construct = [(0, 'class', 'classnaam', 9), (4, 'def', 'methodnaam', 11),
                               (12, 'def', 'functienaam', 13)]
        testobj.itemlist = []
        testobj.start_of_code = False
        testobj.modlevel_start = 5
        testobj.build_comment_context(1, 2)
        assert testobj.itemlist == [((1, 0), (2, -1), 'class classnaam method methodnaam'
                                     ' function functienaam docstring')]
        assert testobj.modlevel_start == 5
        testobj.in_construct = [(0, 'class', 'classnaam', 9), (4, 'def', 'methodnaam', 11),
                               (12, 'class', 'classnaam', 13), (16, 'def', 'methodnaam', 16)]
        testobj.itemlist = []
        testobj.start_of_code = False
        testobj.modlevel_start = 5
        testobj.build_comment_context(1, 2)
        assert testobj.itemlist == [((1, 0), (2, -1), 'class classnaam method methodnaam'
                                     ' class classnaam method methodnaam docstring')]
        assert testobj.modlevel_start == 5

    def test_add_context(self, monkeypatch, capsys):
        """unittest for PyRead.add_context
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.itemlist = []
        testobj.start_of_code = False
        testobj.modlevel_start = 1
        testobj.add_context('xxx', 15)
        assert testobj.itemlist == ['xxx']
        assert testobj.modlevel_start == 16
        testobj.itemlist = []
        testobj.start_of_code = True
        testobj.modlevel_start = 1
        testobj.add_context('xxx', 15)
        assert testobj.itemlist == ['xxx']
        assert testobj.modlevel_start == 1

    def test_is_single_line_docstring(self, monkeypatch, capsys):
        """unittest for PyRead.is_single_line_docstring
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert not testobj.is_single_line_docstring('hello')
        assert testobj.is_single_line_docstring('"hello"')
        assert not testobj.is_single_line_docstring('"hello')
        assert not testobj.is_single_line_docstring('""hello""')
        assert testobj.is_single_line_docstring('"""hello"""')
        assert not testobj.is_single_line_docstring('"""hello')
        assert testobj.is_single_line_docstring("'hello'")
        assert not testobj.is_single_line_docstring("'hello")
        assert not testobj.is_single_line_docstring("''hello''")
        assert testobj.is_single_line_docstring("'''hello'''")
        assert not testobj.is_single_line_docstring("'''hello")

    def test_pop_construct(self, monkeypatch, capsys):
        """unittest for PyRead.pop_construct
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.constructs = []
        testobj.in_construct = [(0, 'def', 'functienaam', 9)]
        testobj.indentpos = 0
        testobj.pop_construct('another line')
        assert testobj.constructs == [[[0, 'def', 'functienaam', 9, 'another line']]]
        assert testobj.in_construct == []

        testobj.constructs = []
        testobj.in_construct = [(0, 'def', 'functienaam', 9)]
        testobj.indentpos = 1
        testobj.pop_construct('another line')
        assert testobj.constructs == []
        assert testobj.in_construct == [(0, 'def', 'functienaam', 9)]

        testobj.constructs = []
        testobj.in_construct = [(0, 'def', 'functienaam', 9), (4, 'def', 'functienaam', 11)]
        testobj.indentpos = 0
        testobj.pop_construct('another line')
        assert testobj.constructs == [[(0, 'def', 'functienaam', 9),
                                       [4, 'def', 'functienaam', 11, 'another line']],
                                      [[0, 'def', 'functienaam', 9, 'another line']]]
        assert testobj.in_construct == []

        testobj.constructs = []
        testobj.in_construct = [(0, 'def', 'functienaam', 9), (4, 'def', 'functienaam', 11)]
        testobj.indentpos = 4
        testobj.pop_construct('another line')
        assert testobj.constructs == [[(0, 'def', 'functienaam', 9),
                                       [4, 'def', 'functienaam', 11, 'another line']]]
        assert testobj.in_construct == [(0, 'def', 'functienaam', 9)]

        testobj.constructs = []
        testobj.in_construct = [(0, 'def', 'functienaam', 9), (4, 'def', 'functienaam', 11)]
        testobj.indentpos = 5
        testobj.pop_construct('another line')
        assert testobj.constructs == []
        assert testobj.in_construct == [(0, 'def', 'functienaam', 9), (4, 'def', 'functienaam', 11)]

        testobj.constructs = []
        testobj.in_construct = [(0, 'class', 'classnaam', 9), (4, 'def', 'methodnaam', 11)]
        testobj.indentpos = 0
        testobj.pop_construct('another line')
        assert testobj.constructs == [[(0, 'class', 'classnaam', 9),
                                       [4, 'def', 'methodnaam', 11, 'another line']],
                                      [[0, 'class', 'classnaam', 9, 'another line']]]
        assert testobj.in_construct == []

        testobj.constructs = []
        testobj.in_construct = [(0, 'class', 'classnaam', 9), (4, 'def', 'methodnaam', 11)]
        testobj.indentpos = 4
        testobj.pop_construct('another line')
        assert testobj.constructs == [[(0, 'class', 'classnaam', 9),
                                       [4, 'def', 'methodnaam', 11, 'another line']]]
        assert testobj.in_construct == [(0, 'class', 'classnaam', 9)]

        testobj.constructs = []
        testobj.in_construct = [(0, 'class', 'classnaam', 9), (4, 'def', 'methodnaam', 11)]
        testobj.indentpos = 5
        testobj.pop_construct('another line')
        assert testobj.constructs == []
        assert testobj.in_construct == [(0, 'class', 'classnaam', 9), (4, 'def', 'methodnaam', 11)]

        testobj.constructs = []
        testobj.in_construct = [(0, 'class', 'classnaam', 9), (4, 'def', 'methodnaam', 11),
                               (12, 'def', 'functienaam', 13)]
        testobj.indentpos = 0
        testobj.pop_construct('another line')
        assert testobj.constructs == [[(0, 'class', 'classnaam', 9), (4, 'def', 'methodnaam', 11),
                                       [12, 'def', 'functienaam', 13, 'another line']],
                                      [(0, 'class', 'classnaam', 9),
                                       [4, 'def', 'methodnaam', 11, 'another line']],
                                      [[0, 'class', 'classnaam', 9, 'another line']]]
        assert testobj.in_construct == []

        testobj.constructs = []
        testobj.in_construct = [(0, 'class', 'classnaam', 9), (4, 'def', 'methodnaam', 11),
                               (12, 'def', 'functienaam', 13)]
        testobj.indentpos = 4
        testobj.pop_construct('another line')
        assert testobj.constructs == [[(0, 'class', 'classnaam', 9), (4, 'def', 'methodnaam', 11),
                                       [12, 'def', 'functienaam', 13, 'another line']],
                                      [(0, 'class', 'classnaam', 9),
                                       [4, 'def', 'methodnaam', 11, 'another line']]]
        assert testobj.in_construct == [(0, 'class', 'classnaam', 9)]

        testobj.constructs = []
        testobj.in_construct = [(0, 'class', 'classnaam', 9), (4, 'def', 'methodnaam', 11),
                               (12, 'def', 'functienaam', 13)]
        testobj.indentpos = 8
        testobj.pop_construct('another line')
        assert testobj.constructs == [[(0, 'class', 'classnaam', 9), (4, 'def', 'methodnaam', 11),
                                       [12, 'def', 'functienaam', 13, 'another line']]]
        assert testobj.in_construct == [(0, 'class', 'classnaam', 9), (4, 'def', 'methodnaam', 11)]

        testobj.constructs = []
        testobj.in_construct = [(0, 'class', 'classnaam', 9), (4, 'def', 'methodnaam', 11),
                               (12, 'def', 'functienaam', 13)]
        testobj.indentpos = 12
        testobj.pop_construct('another line')
        assert testobj.constructs == [[(0, 'class', 'classnaam', 9), (4, 'def', 'methodnaam', 11),
                                       [12, 'def', 'functienaam', 13, 'another line']]]
        assert testobj.in_construct == [(0, 'class', 'classnaam', 9), (4, 'def', 'methodnaam', 11)]

        testobj.constructs = []
        testobj.in_construct = [(0, 'class', 'classnaam', 9), (4, 'def', 'methodnaam', 11),
                               (12, 'def', 'functienaam', 13)]
        testobj.indentpos = 13
        testobj.pop_construct('another line')
        assert testobj.constructs == []
        assert testobj.in_construct == [(0, 'class', 'classnaam', 9), (4, 'def', 'methodnaam', 11),
                                        (12, 'def', 'functienaam', 13)]

        testobj.constructs = []
        testobj.in_construct = [(0, 'class', 'classnaam', 9), (4, 'def', 'methodnaam', 11),
                               (12, 'class', 'classnaam', 13), (16, 'def', 'methodnaam', 16)]
        testobj.indentpos = 0
        testobj.pop_construct('another line')
        assert testobj.constructs == [[(0, 'class', 'classnaam', 9), (4, 'def', 'methodnaam', 11),
                                       (12, 'class', 'classnaam', 13),
                                       [16, 'def', 'methodnaam', 16, 'another line']],
                                      [(0, 'class', 'classnaam', 9), (4, 'def', 'methodnaam', 11),
                                       [12, 'class', 'classnaam', 13, 'another line']],
                                      [(0, 'class', 'classnaam', 9),
                                       [4, 'def', 'methodnaam', 11, 'another line']],
                                      [[0, 'class', 'classnaam', 9, 'another line']]]
        assert testobj.in_construct == []

        testobj.constructs = []
        testobj.in_construct = [(0, 'class', 'classnaam', 9), (4, 'def', 'methodnaam', 11),
                               (12, 'class', 'classnaam', 13), (16, 'def', 'methodnaam', 16)]
        testobj.indentpos = 4
        testobj.pop_construct('another line')
        assert testobj.constructs == [[(0, 'class', 'classnaam', 9), (4, 'def', 'methodnaam', 11),
                                       (12, 'class', 'classnaam', 13),
                                       [16, 'def', 'methodnaam', 16, 'another line']],
                                      [(0, 'class', 'classnaam', 9), (4, 'def', 'methodnaam', 11),
                                       [12, 'class', 'classnaam', 13, 'another line']],
                                      [(0, 'class', 'classnaam', 9),
                                       [4, 'def', 'methodnaam', 11, 'another line']]]
        assert testobj.in_construct == [(0, 'class', 'classnaam', 9)]

        testobj.constructs = []
        testobj.in_construct = [(0, 'class', 'classnaam', 9), (4, 'def', 'methodnaam', 11),
                               (12, 'class', 'classnaam', 13), (16, 'def', 'methodnaam', 16)]
        testobj.indentpos = 8
        testobj.pop_construct('another line')
        assert testobj.constructs == [[(0, 'class', 'classnaam', 9), (4, 'def', 'methodnaam', 11),
                                       (12, 'class', 'classnaam', 13),
                                       [16, 'def', 'methodnaam', 16, 'another line']],
                                      [(0, 'class', 'classnaam', 9), (4, 'def', 'methodnaam', 11),
                                       [12, 'class', 'classnaam', 13, 'another line']]]
        assert testobj.in_construct == [(0, 'class', 'classnaam', 9), (4, 'def', 'methodnaam', 11)]

        testobj.constructs = []
        testobj.in_construct = [(0, 'class', 'classnaam', 9), (4, 'def', 'methodnaam', 11),
                               (12, 'class', 'classnaam', 13), (16, 'def', 'methodnaam', 16)]
        testobj.indentpos = 12
        testobj.pop_construct('another line')
        assert testobj.constructs == [[(0, 'class', 'classnaam', 9), (4, 'def', 'methodnaam', 11),
                                       (12, 'class', 'classnaam', 13),
                                       [16, 'def', 'methodnaam', 16, 'another line']],
                                      [(0, 'class', 'classnaam', 9), (4, 'def', 'methodnaam', 11),
                                       [12, 'class', 'classnaam', 13, 'another line']]]
        assert testobj.in_construct == [(0, 'class', 'classnaam', 9), (4, 'def', 'methodnaam', 11)]

        testobj.constructs = []
        testobj.in_construct = [(0, 'class', 'classnaam', 9), (4, 'def', 'methodnaam', 11),
                               (12, 'class', 'classnaam', 13), (16, 'def', 'methodnaam', 16)]
        testobj.indentpos = 16
        testobj.pop_construct('another line')
        assert testobj.constructs == [[(0, 'class', 'classnaam', 9), (4, 'def', 'methodnaam', 11),
                                       (12, 'class', 'classnaam', 13),
                                       [16, 'def', 'methodnaam', 16, 'another line']]]
        assert testobj.in_construct == [(0, 'class', 'classnaam', 9), (4, 'def', 'methodnaam', 11),
                                        (12, 'class', 'classnaam', 13)]

        testobj.constructs = []
        testobj.in_construct = [(0, 'class', 'classnaam', 9), (4, 'def', 'methodnaam', 11),
                               (12, 'class', 'classnaam', 13), (16, 'def', 'methodnaam', 16)]
        testobj.indentpos = 17
        testobj.pop_construct('another line')
        assert testobj.constructs == []
        assert testobj.in_construct == [(0, 'class', 'classnaam', 9), (4, 'def', 'methodnaam', 11),
                                        (12, 'class', 'classnaam', 13), (16, 'def', 'methodnaam', 16)]


def test_rgxescape():
    "unittest for findr_files.rgxescape"
    assert testee.rgxescape(r'`1234567890-=') == r'`1234567890-='
    assert testee.rgxescape(r'~!@#$%^&*()_+') == r'~!@#\$%\^&\*\(\)_\+'
    assert testee.rgxescape(r'qwertyuiop[]\ ') == r'qwertyuiop\[\]\\ '
    assert testee.rgxescape(r'QWERTYUIOP{}|') == r'QWERTYUIOP\{\}\|'
    assert testee.rgxescape(r"asdfghjkl;'") == r"asdfghjkl;'"
    assert testee.rgxescape(r'ASDFGHJKL:"') == r'ASDFGHJKL:"'
    assert testee.rgxescape(r'zxcvbnm,./') == r'zxcvbnm,\./'
    assert testee.rgxescape(r'ZXCVBNM<>?') == r'ZXCVBNM<>\?'


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

    def test_init(self):
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
        testobj = testee.Finder(zoek='Vind', vervang=None, filelist=['xx'])
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

    def test_subdirs(self, monkeypatch, capsys, tmp_path):
        """unittest for Finder.subdirs
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.p['maxdepth'] = -1
        testobj.p['follow_symlinks'] = False
        testobj.p['extlist'] = []
        testobj.p['subdirs'] = False
        testobj.dirnames = set()
        testobj.filenames = []
        assert testobj.subdirs('/lost+found') == ""  # PermissionError
        assert testobj.dirnames == {'/lost+found'}
        assert testobj.filenames == []

        testpath = tmp_path / 'testfile'
        testobj.dirnames = set()
        testobj.filenames = []
        assert testobj.subdirs(testpath) == f"File not found: {tmp_path}/testfile"
        assert testobj.dirnames == set()
        assert testobj.filenames == []

        testpath.touch()
        testobj.dirnames = set()
        testobj.filenames = []
        assert testobj.subdirs(testpath) == ""   # NotADirectoryError
        assert testobj.dirnames == set()
        assert testobj.filenames == [testpath]

        testpath = tmp_path / 'testdir'
        testpath.mkdir()
        testobj.dirnames = set()
        testobj.filenames = []
        assert testobj.subdirs(testpath) == ""
        assert testobj.dirnames == {f'{tmp_path}/testdir'}
        assert testobj.filenames == []

        testobj.p['extlist'] = ['py']
        testobj.p['maxdepth'] = 2
        testobj.p['follow_symlinks'] = True
        testobj.p['subdirs'] = True
        testobj.extlist_upper = ['.PY']
        (testpath / 'testfile.py').touch()
        (testpath / 'testfile.c').touch()
        (testpath / 'testfile').symlink_to(tmp_path / 'testfile.py')
        (testpath / 'subdir').mkdir()
        (testpath / 'subdir' / 'testfile.py').touch()
        (testpath / 'subdir' / 'subdir').mkdir()
        (testpath / 'subdir' / 'subdir' / 'testfile.py').touch()
        testobj.dirnames = set()
        testobj.filenames = []
        assert testobj.subdirs(testpath) == ""
        assert testobj.dirnames == {f'{tmp_path}/testdir',
                                    f'{tmp_path}/testdir/subdir',
                                    f'{tmp_path}/testdir/subdir/subdir'}
        assert testobj.filenames == [tmp_path / 'testdir' / 'testfile.py',
                                     tmp_path / 'testdir' / 'subdir' / 'testfile.py']

        testobj.p['extlist'] = []
        testobj.p['maxdepth'] = 3
        testobj.dirnames = set()
        testobj.filenames = []
        assert testobj.subdirs(testpath) == ""
        assert testobj.dirnames == {f'{tmp_path}/testdir',
                                    f'{tmp_path}/testdir/subdir',
                                    f'{tmp_path}/testdir/subdir/subdir'}
        assert testobj.filenames == [tmp_path / 'testdir' / 'testfile.py',
                                     tmp_path / 'testdir' / 'testfile.c',
                                     # waarom niet ook testfile (als zijnde een symlink) ?
                                     tmp_path / 'testdir' / 'subdir' / 'testfile.py',
                                     tmp_path / 'testdir' / 'subdir' / 'subdir' / 'testfile.py']

        testobj.p['follow_symlinks'] = False
        testobj.dirnames = set()
        testobj.filenames = []
        assert testobj.subdirs(testpath) == ""
        assert testobj.dirnames == {f'{tmp_path}/testdir',
                                    f'{tmp_path}/testdir/subdir',
                                    f'{tmp_path}/testdir/subdir/subdir'}
        assert testobj.filenames == [tmp_path / 'testdir' / 'testfile.py',
                                     tmp_path / 'testdir' / 'testfile.c',
                                     tmp_path / 'testdir' / 'subdir' / 'testfile.py',
                                     tmp_path / 'testdir' / 'subdir' / 'subdir' / 'testfile.py']

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

    def test_build_regexes(self, monkeypatch, capsys):
        """unittest for Finder.build_regexes
        """
        def mock_parse():
            print('called Finder.parse_zoekstring')
            return ['xxx', 'yyy'], ['zzz'], ['qqq']
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.p = {'zoek': 'xyz', 'case': False, 'regexp': True, 'wijzig': True}
        testobj.use_complex = not (testobj.p['regexp'] or testobj.p['wijzig'])
        assert testobj.build_regexes() == (
                [testee.re.compile('xyz', testee.re.IGNORECASE | testee.re.MULTILINE)], "")
        assert capsys.readouterr().out == ""
        testobj.p = {'zoek': 'xyz', 'case': True, 'regexp': True, 'wijzig': False}
        testobj.use_complex = not (testobj.p['regexp'] or testobj.p['wijzig'])
        assert testobj.build_regexes() == ([testee.re.compile('xyz', testee.re.MULTILINE)], "")
        assert capsys.readouterr().out == ""
        testobj.p = {'zoek': 'xyz', 'case': True, 'regexp': False, 'wijzig': True}
        testobj.use_complex = not (testobj.p['regexp'] or testobj.p['wijzig'])
        assert testobj.build_regexes() == ([testee.re.compile('xyz', testee.re.MULTILINE)], "")
        assert capsys.readouterr().out == ""
        testobj.parse_zoekstring = mock_parse
        testobj.p = {'zoek': 'xyz', 'case': True, 'regexp': False, 'wijzig': False}
        testobj.use_complex = not (testobj.p['regexp'] or testobj.p['wijzig'])
        assert testobj.build_regexes() == ([testee.re.compile('xxx|yyy', testee.re.MULTILINE),
                                            testee.re.compile('zzz', testee.re.MULTILINE)],
                                           testee.re.compile('qqq', testee.re.MULTILINE))
        assert capsys.readouterr().out == ("called Finder.parse_zoekstring\n")

    def test_parse_zoekstring(self, monkeypatch, capsys):
        """unittest for Finder.parse_zoek
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.p['zoek'] = ''
        assert testobj.parse_zoekstring() == ([], [], [])
        testobj.p['zoek'] = 'test'
        assert testobj.parse_zoekstring() == (['test'], [], [])
        testobj.p['zoek'] = '"test"'
        assert testobj.parse_zoekstring() == (['test'], [], [])
        testobj.p['zoek'] = "'test'"
        assert testobj.parse_zoekstring() == (['test'], [], [])
        testobj.p['zoek'] = "'test, text'"
        assert testobj.parse_zoekstring() == (['test, text'], [], [])
        testobj.p['zoek'] = "'test', 'text'"
        assert testobj.parse_zoekstring() == (['test', 'text'], [], [])
        testobj.p['zoek'] = "'test' + 'text'"
        assert testobj.parse_zoekstring() == (['test'], ['text'], [])
        testobj.p['zoek'] = "'test' - 'text'"
        assert testobj.parse_zoekstring() == (['test'], [], ['text'])
        testobj.p['zoek'] = "'test', 'text' - 'xxxx', 'yyyy' + 'aaaa', 'bbbb'"
        assert testobj.parse_zoekstring() == (['test', 'text', 'yyyy', 'bbbb'], ['aaaa'], ['xxxx'])
        testobj.p['zoek'] = "'test', 'text' - 'xxxx' - 'yyyy' + 'aaaa' + 'bbbb'"
        assert testobj.parse_zoekstring() == (['test', 'text'], ['aaaa', 'bbbb'], ['xxxx', 'yyyy'])

    def test_go(self, monkeypatch, capsys):
        """unittest for Finder.go
        """
        def mock_zoek(naam):
            print(f"called Finder.zoek with arg '{naam}'")
        def mock_add():
            print("called Finder.add_context_to_search_results")
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.zoek = mock_zoek
        testobj.add_context_to_search_results = mock_add
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
                                           "called Finder.add_context_to_search_results\n")

    def test_zoek(self, monkeypatch, capsys):
        """unittest for Finder.zoek
        """
        def mock_read(*args):
            print('called read_input_file with args', args)
            return None
        def mock_read_2(*args):
            print('called read_input_file with args', args)
            return []
        def mock_read_3(*args):
            print('called read_input_file with args', args)
            return ['some\n', 'test   \n', 'data lines\n']
        def mock_complex(*args):
            print("called Finder.complex_search with args", args)
            return []
        def mock_complex_2(*args):
            print("called Finder.complex_search with args", args)
            return [1, 2]
        def mock_old(*args):
            print("called Finder.old_rgx_search with args", args)
            return False
        def mock_old_2(*args):
            print("called Finder.old_rgx_search with args", args)
            return True
        def mock_replace(*args):
            print("called Finder.replace_and_report with args", args)
        monkeypatch.setattr(testee, 'read_input_file', mock_read)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.complex_search = mock_complex
        testobj.old_rgx_search = mock_old
        testobj.replace_and_report = mock_replace
        testobj.rpt = []
        testobj.p = {'fallback_encoding': 'xxx', 'wijzig': False}
        testobj.use_complex = True
        testobj.zoek('testfile')
        assert testobj.rpt == ['testfile: overgeslagen, waarschijnlijk geen tekstbestand']
        assert capsys.readouterr().out == "called read_input_file with args ('testfile', 'xxx')\n"

        testobj.rpt = []
        monkeypatch.setattr(testee, 'read_input_file', mock_read_2)
        testobj.zoek('testfile')
        assert testobj.rpt == []
        assert capsys.readouterr().out == (
                "called read_input_file with args ('testfile', 'xxx')\n"
                "called Finder.complex_search with args ([], [0])\n")

        testobj.rpt = []
        monkeypatch.setattr(testee, 'read_input_file', mock_read_3)
        testobj.zoek('testfile')
        assert testobj.rpt == []
        assert capsys.readouterr().out == (
                "called read_input_file with args ('testfile', 'xxx')\n"
                "called Finder.complex_search with args"
                " (['some\\n', 'test   \\n', 'data lines\\n'], [0, 5, 13, 24])\n")

        testobj.rpt = []
        testobj.complex_search = mock_complex_2
        testobj.zoek('testfile')
        assert testobj.rpt == ['testfile r. 1: some', 'testfile r. 2: test']
        assert capsys.readouterr().out == (
                "called read_input_file with args ('testfile', 'xxx')\n"
                "called Finder.complex_search with args"
                " (['some\\n', 'test   \\n', 'data lines\\n'], [0, 5, 13, 24])\n")

        testobj.rpt = []
        testobj.use_complex = False
        monkeypatch.setattr(testee, 'read_input_file', mock_read_2)
        testobj.zoek('testfile')
        assert testobj.rpt == []
        assert capsys.readouterr().out == (
                "called read_input_file with args ('testfile', 'xxx')\n"
                "called Finder.old_rgx_search with args ([], [0], 'testfile')\n")

        testobj.rpt = []
        monkeypatch.setattr(testee, 'read_input_file', mock_read_3)
        testobj.zoek('testfile')
        assert testobj.rpt == []
        assert capsys.readouterr().out == (
                "called read_input_file with args ('testfile', 'xxx')\n"
                "called Finder.old_rgx_search with args"
                " (['some\\n', 'test   \\n', 'data lines\\n'], [0, 5, 13, 24], 'testfile')\n")

        testobj.rpt = []
        testobj.old_rgx_search = mock_old_2
        testobj.zoek('testfile')
        assert testobj.rpt == []
        assert capsys.readouterr().out == (
                "called read_input_file with args ('testfile', 'xxx')\n"
                "called Finder.old_rgx_search with args"
                " (['some\\n', 'test   \\n', 'data lines\\n'], [0, 5, 13, 24], 'testfile')\n")

        testobj.rpt = []
        testobj.p['wijzig'] = True
        testobj.zoek('testfile')
        assert testobj.rpt == []
        assert capsys.readouterr().out == (
                "called read_input_file with args ('testfile', 'xxx')\n"
                "called Finder.old_rgx_search with args"
                " (['some\\n', 'test   \\n', 'data lines\\n'], [0, 5, 13, 24], 'testfile')\n"
                "called Finder.replace_and_report with args"
                " (['some\\n', 'test   \\n', 'data lines\\n'], 'testfile')\n")

    def test_add_context_to_search_results(self, monkeypatch, capsys):
        """unittest for Finder.add_context_to_search_results
        """
        def mock_type(entry):
            print(f"called determine_filetype for '{entry}'")
            if str(entry).endswith('.py'):
                return 'py'
            return ''
        class MockPyRead:
            """stub for PyRead object
            """
            def __init__(self, *args):
                print('called PyRead.__init__ with args', args)
            def go(self):
                print('called PyRead.go')
                return ['']
        counter = 0
        def mock_context(*args):
            nonlocal counter
            print('called Finder.determine_context_from_locations with args', args)
            counter += 1
            if counter == 1:
                return ''
            if counter == 2:
                return 'comment'
            if counter == 3:
                return 'docstring'
            if counter == 4:
                return 'ignore'
            return 'somewhere in the code'
        monkeypatch.setattr(testee, 'determine_filetype', mock_type)
        # monkeypatch.setattr(testee, 'pyread', mock_pyread)
        monkeypatch.setattr(testee, 'PyRead', MockPyRead)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.p = {'fallback_encoding': 'uuu', 'negeer': False}
        testobj.filenames = [testee.pathlib.Path('testfile'), testee.pathlib.Path('testfile.py')]
        testobj.rpt = ['cannot be split', 'testfile r. 3', 'testfile.py r. 1 xxx',
                       'testfile.py r. 1: xxx', 'testfile.py r. 2: xxx', 'testfile.py r. 3: xxx',
                       'testfile.py r. 4: xxx', 'testfile.py r. 5: xxx']
        testobj.determine_context_from_locations = mock_context
        testobj.add_context_to_search_results()
        assert testobj.rpt == ['cannot be split', 'testfile.py r. 1 xxx',
                               'testfile.py r. 1 (): xxx', 'testfile.py r. 2 (comment): xxx',
                               'testfile.py r. 3 (docstring): xxx',
                               'testfile.py r. 5 (somewhere in the code): xxx']
        assert capsys.readouterr().out == (
                "called determine_filetype for 'testfile'\n"
                "called determine_filetype for 'testfile.py'\n"
                # "called pyread with args ('testfile.py', 'uuu', False)\n"
                "called PyRead.__init__ with args (PosixPath('testfile.py'), 'uuu')\n"
                "called PyRead.go\n"
                "called Finder.determine_context_from_locations with args ('1', 'xxx', [''])\n"
                "called Finder.determine_context_from_locations with args ('2', 'xxx', [''])\n"
                "called Finder.determine_context_from_locations with args ('3', 'xxx', [''])\n"
                "called Finder.determine_context_from_locations with args ('4', 'xxx', [''])\n"
                "called Finder.determine_context_from_locations with args ('5', 'xxx', [''])\n")
        counter = 0
        testobj.p['negeer'] = True
        testobj.rpt = ['cannot be split', 'testfile r. 3', 'testfile.py r. 1 xxx',
                       'testfile.py r. 1: xxx', 'testfile.py r. 2: xxx', 'testfile.py r. 3: xxx',
                       'testfile.py r. 4: xxx']
        testobj.add_context_to_search_results()
        assert testobj.rpt == ['cannot be split', 'testfile.py r. 1 xxx',
                               'testfile.py r. 1 (): xxx']
        assert capsys.readouterr().out == (
                "called determine_filetype for 'testfile'\n"
                "called determine_filetype for 'testfile.py'\n"
                # "called pyread with args ('testfile.py', 'uuu', True)\n"
                "called PyRead.__init__ with args (PosixPath('testfile.py'), 'uuu')\n"
                "called PyRead.go\n"
                "called Finder.determine_context_from_locations with args ('1', 'xxx', [''])\n"
                "called Finder.determine_context_from_locations with args ('2', 'xxx', [''])\n"
                "called Finder.determine_context_from_locations with args ('3', 'xxx', [''])\n"
                "called Finder.determine_context_from_locations with args ('4', 'xxx', [''])\n")

    def test_determine_context_from_locations(self, monkeypatch, capsys):
        """unittest for Finder.determine_context_from_locations
        """
        def mock_find(locs):
            print(f'called Finder.find_smallest_context with arg {locs}')
            return locs[0][2][2]
        monkeypatch.setattr(testee, 'default_location', 'xxx')
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.p = {'zoek': 'Arg'}
        testobj.find_smallest_context = mock_find
        locations = [((0, 0), (5, -1), 'yyy'),
                     ((8, 8), (12, -1), 'comment'),
                     ((15, 4), (30, -1), 'zzz')]
        assert testobj.determine_context_from_locations(4, 'ARG', locations) == "yyy"
        assert capsys.readouterr().out == ("called Finder.find_smallest_context with arg"
                                           " [((4, 1), (1, 2), ((0, 0), (5, 3), 'yyy'))]\n")
        assert testobj.determine_context_from_locations(8, '        gargl', locations) == "comment"
        assert capsys.readouterr().out == ("called Finder.find_smallest_context with arg"
                                           " [((0, 4), (2, 3), ((8, 8), (12, 13), 'comment'))]\n")
        assert testobj.determine_context_from_locations(9, '        gargl', locations) == "comment"
        assert capsys.readouterr().out == ("called Finder.find_smallest_context with arg"
                                           " [((1, 3), (2, 3), ((8, 8), (12, 13), 'comment'))]\n")
        # assert testobj.determine_context_from_locations(12, 'gargl', locations) == ""
        # assert capsys.readouterr().out == ""
        # assert testobj.determine_context_from_locations(13, 'gargl', locations) == ""
        # assert capsys.readouterr().out == ""
        # assert testobj.determine_context_from_locations(15, 'oaRG', locations) == ""
        # assert capsys.readouterr().out == ""
        # assert testobj.determine_context_from_locations(16, 'oaRG', locations) == ""
        # assert capsys.readouterr().out == ""

    def test_find_smallest_context(self, monkeypatch, capsys):
        """unittest for Finder.find_smallest_context
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        locs = [((5, 5), (12, 29), ((46, 0), (56, 41), 'comment')),
                ((5, 6), (12, 29), ((46, 0), (57, 41), 'comment')),
                ((5, 2), (12, 29), ((45, 0), (53, 41), 'function test_splitjoin'))]
        assert testobj.find_smallest_context(locs) == 'function test_splitjoin'

    def test_complex_search(self, monkeypatch, capsys):
        """unittest for Finder.complex_search
        """
        class MockMatch:
            """stub for re.match result
            """
            def __init__(self, seq):
                self._seq = seq
            def start(self):
                return self._seq
        class MockRgx:
            """stub for re.compile result
            """
            def __init__(self, zoek):
                self._zoek = zoek
            def __repr__(self):
                return f"<Rgx '{self._zoek}'>"
            def finditer(self, find):
                if self._zoek == "find":
                    return MockMatch(1), MockMatch(7), MockMatch(13)
                if self._zoek == "find also":
                    return MockMatch(1), MockMatch(13), MockMatch(19)
                if self._zoek == "ignore":
                    return MockMatch(1), MockMatch(7)

        testobj = self.setup_testobj(monkeypatch, capsys)
        lines = ['test data', 'to search through', 'for stuff']
        linestarts = (0, 1, 5, 12, 20)

        testobj.rgx = []
        testobj.ignore = None
        assert testobj.complex_search(lines, linestarts) == []
        assert capsys.readouterr().out == ""
        # assert capsys.readouterr().out == ("found_in_lines: []\n"
        #                                    "found_in_lines: []\n"
        #                                    "lines_found: defaultdict(<class 'set'>, {})\n"
        #                                    "all_searches: set()\n")

        testobj.rgx = [MockRgx('find')]
        assert testobj.complex_search(lines, linestarts) == [2, 3, 4]
        assert capsys.readouterr().out == ""
        # assert capsys.readouterr().out == (
        #         "found_in_lines: [(1, 0), (7, 0), (13, 0)]\n"
        #         "found_in_lines: [(1, 0), (7, 0), (13, 0)]\n"
        #         "itemstart, number: 1 0\n"
        #         "ix, linestart: 0 0\nix, linestart: 1 1\nix, linestart: 2 5\n"
        #         "itemstart ligt vóór linestart => gevonden in regel 2\n"
        #         "itemstart, number: 7 0\n"
        #         "ix, linestart: 0 5\nix, linestart: 1 12\n"
        #         "itemstart ligt vóór linestart => gevonden in regel 3\n"
        #         "itemstart, number: 13 0\n"
        #         "ix, linestart: 0 1\nix, linestart: 1 5\nix, linestart: 2 12\nix, linestart: 3 20\n"
        #         "itemstart ligt vóór linestart => gevonden in regel 4\n"
        #         "lines_found: defaultdict(<class 'set'>, {2: {0}, 3: {0}, 4: {0}})\n"
        #         "all_searches: {0}\n"
        #         "in_line, values: 2 {0}\n"
        #         "in_line, values: 3 {0}\n"
        #         "in_line, values: 4 {0}\n")

        testobj.ignore = MockRgx('ignore')
        assert testobj.complex_search(lines, linestarts) == [4]
        assert capsys.readouterr().out == ""
        # assert capsys.readouterr().out == (
        #         "found_in_lines: [(1, 0), (7, 0), (13, 0)]\n"
        #         "found_in_lines: [(1, 0), (7, 0), (13, 0), (1, -1), (7, -1)]\n"
        #         "itemstart, number: 1 -1\n"
        #         "ix, linestart: 0 0\nix, linestart: 1 1\nix, linestart: 2 5\n"
        #         "itemstart ligt vóór linestart => gevonden in regel 2\n"
        #         "itemstart, number: 1 0\n"
        #         "ix, linestart: 0 5\n"
        #         "itemstart ligt vóór linestart => gevonden in regel 2\n"
        #         "itemstart, number: 7 -1\n"
        #         "ix, linestart: 0 0\nix, linestart: 1 1\nix, linestart: 2 5\nix, linestart: 3 12\n"
        #         "itemstart ligt vóór linestart => gevonden in regel 3\n"
        #         "itemstart, number: 7 0\n"
        #         "ix, linestart: 0 12\n"
        #         "itemstart ligt vóór linestart => gevonden in regel 3\n"
        #         "itemstart, number: 13 0\n"
        #         "ix, linestart: 0 0\nix, linestart: 1 1\nix, linestart: 2 5\nix, linestart: 3 12\n"
        #         "ix, linestart: 4 20\n"
        #         "itemstart ligt vóór linestart => gevonden in regel 4\n"
        #         "lines_found: defaultdict(<class 'set'>, {2: {0, -1}, 3: {0, -1}, 4: {0}})\n"
        #         "all_searches: {0}\n"
        #         "in_line, values: 2 {0, -1}\n"
        #         "in_line, values: 3 {0, -1}\n"
        #         "in_line, values: 4 {0}\n")

        testobj.rgx = [MockRgx('find'), MockRgx('find also')]
        testobj.ignore = None
        assert testobj.complex_search(lines, linestarts) == [2, 4]
        assert capsys.readouterr().out == ""
        # assert capsys.readouterr().out == (
        #         "found_in_lines: [(1, 0), (7, 0), (13, 0), (1, 1), (13, 1), (19, 1)]\n"
        #         "found_in_lines: [(1, 0), (7, 0), (13, 0), (1, 1), (13, 1), (19, 1)]\n"
        #         "itemstart, number: 1 0\n"
        #         "ix, linestart: 0 0\nix, linestart: 1 1\nix, linestart: 2 5\n"
        #         "itemstart ligt vóór linestart => gevonden in regel 2\n"
        #         "itemstart, number: 1 1\n"
        #         "ix, linestart: 0 5\n"
        #         "itemstart ligt vóór linestart => gevonden in regel 2\n"
        #         "itemstart, number: 7 0\n"
        #         "ix, linestart: 0 0\nix, linestart: 1 1\nix, linestart: 2 5\nix, linestart: 3 12\n"
        #         "itemstart ligt vóór linestart => gevonden in regel 3\n"
        #         "itemstart, number: 13 0\n"
        #         "ix, linestart: 0 12\nix, linestart: 1 20\n"
        #         "itemstart ligt vóór linestart => gevonden in regel 4\n"
        #         "itemstart, number: 13 1\n"
        #         "ix, linestart: 0 1\nix, linestart: 1 5\nix, linestart: 2 12\nix, linestart: 3 20\n"
        #         "itemstart ligt vóór linestart => gevonden in regel 4\n"
        #         "itemstart, number: 19 1\nix, linestart: 0 12\nix, linestart: 1 20\n"
        #         "itemstart ligt vóór linestart => gevonden in regel 4\n"
        #         "lines_found: defaultdict(<class 'set'>, {2: {0, 1}, 3: {0}, 4: {0, 1}})\n"
        #         "all_searches: {0, 1}\n"
        #         "in_line, values: 2 {0, 1}\n"
        #         "in_line, values: 3 {0}\nnot all searches satisfied\n"
        #         "in_line, values: 4 {0, 1}\n")

        testobj.rgx = [MockRgx('find'), MockRgx('find also')]
        testobj.ignore = MockRgx('ignore')
        assert testobj.complex_search(lines, linestarts) == [4]
        assert capsys.readouterr().out == ""
        # assert capsys.readouterr().out == (
        #        "found_in_lines: [(1, 0), (7, 0), (13, 0), (1, 1), (13, 1), (19, 1)]\n"
        #        "found_in_lines: [(1, 0), (7, 0), (13, 0), (1, 1), (13, 1), (19, 1),"
        #        " (1, -1), (7, -1)]\n"
        #        "itemstart, number: 1 -1\n"
        #        "ix, linestart: 0 0\nix, linestart: 1 1\nix, linestart: 2 5\n"
        #        "itemstart ligt vóór linestart => gevonden in regel 2\n"
        #        "itemstart, number: 1 0\n"
        #        "ix, linestart: 0 5\n"
        #        "itemstart ligt vóór linestart => gevonden in regel 2\n"
        #        "itemstart, number: 1 1\n"
        #        "ix, linestart: 0 0\nix, linestart: 1 1\nix, linestart: 2 5\n"
        #        "itemstart ligt vóór linestart => gevonden in regel 2\n"
        #        "itemstart, number: 7 -1\n"
        #        "ix, linestart: 0 5\nix, linestart: 1 12\n"
        #        "itemstart ligt vóór linestart => gevonden in regel 3\n"
        #        "itemstart, number: 7 0\n"
        #        "ix, linestart: 0 1\nix, linestart: 1 5\nix, linestart: 2 12\n"
        #        "itemstart ligt vóór linestart => gevonden in regel 3\n"
        #        "itemstart, number: 13 0\n"
        #        "ix, linestart: 0 5\nix, linestart: 1 12\nix, linestart: 2 20\n"
        #        "itemstart ligt vóór linestart => gevonden in regel 4\n"
        #        "itemstart, number: 13 1\n"
        #        "ix, linestart: 0 5\nix, linestart: 1 12\nix, linestart: 2 20\n"
        #        "itemstart ligt vóór linestart => gevonden in regel 4\n"
        #        "itemstart, number: 19 1\n"
        #        "ix, linestart: 0 5\nix, linestart: 1 12\nix, linestart: 2 20\n"
        #        "itemstart ligt vóór linestart => gevonden in regel 4\n"
        #        "lines_found: defaultdict(<class 'set'>, {2: {0, 1, -1}, 3: {0, -1}, 4: {0, 1}})\n"
        #        "all_searches: {0, 1}\n"
        #        "in_line, values: 2 {0, 1, -1}\n"
        #        "in_line, values: 3 {0, -1}\n"
        #        "in_line, values: 4 {0, 1}\n")

    def test_old_rgx_search(self, monkeypatch, capsys):
        """unittest for Finder.old_rgx_search
        """
        class MockMatch:
            """stub for re.match result
            """
            def __init__(self, start):
                self._start = start
            def start(self):
                return self._start
        class MockRegex:
            """stub for re.compile result
            """
            def finditer(self, arg):
                print(f"called regex.finditer with arg '{arg}'")
                return []
        class MockRegex2:
            """stub for re.compile result
            """
            def finditer(self, arg):
                print(f"called regex.finditer with arg '{arg}'")
                return [MockMatch(4), MockMatch(18)]
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.rpt = []
        testobj.p = {'wijzig': False}
        testobj.rgx = MockRegex()
        assert not testobj.old_rgx_search(['test', 'data', 'lines'], [0, 5, 12, 20], 'testfile')
        assert testobj.rpt == []
        assert capsys.readouterr().out == "called regex.finditer with arg 'testdatalines'\n"

        testobj.rgx = MockRegex2()
        assert testobj.old_rgx_search(['test', 'data', 'lines'], [0, 5, 12, 20], 'testfile')
        assert testobj.rpt == ['testfile r. 1: test', 'testfile r. 3: lines']
        assert capsys.readouterr().out == "called regex.finditer with arg 'testdatalines'\n"

        testobj.rpt = []
        testobj.p = {'wijzig': True}
        assert testobj.old_rgx_search(['test', 'data', 'lines'], [0, 5, 12, 20], 'testfile')
        assert testobj.rpt == []
        assert capsys.readouterr().out == "called regex.finditer with arg 'testdatalines'\n"

    def test_replace_and_report(self, monkeypatch, capsys, tmp_path):
        """unittest for Finder.replace_and_report
        """
        class MockRegex:
            """stub for re.compile result
            """
            def subn(self, *args):
                print('called regex.subn with args', args)
                return 'ndata', 5
        def mock_backup(fname):
            print(f"called Finder.backup_if_needed with arg '{fname}'")
        filename = tmp_path / 'testfile'
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.backup_if_needed = mock_backup
        testobj.p = {'vervang': 'yyy'}
        testobj.rpt = []
        testobj.rgx = MockRegex()
        testobj.replace_and_report('data', filename)
        assert testobj.rpt == [f"{filename}: 5 keer"]
        assert filename.read_text() == 'ndata'
        assert capsys.readouterr().out == (
                f"called regex.subn with args ('yyy', 'data')\n"
                f"called Finder.backup_if_needed with arg '{filename}'\n")

    def test_replace_selected(self, monkeypatch, capsys, tmp_path):
        """unittest for Finder.replace_selected
        """
        def mock_backup(name):
            print(f"called Finder.backup_if_needed with arg '{name}'")
        file0 = tmp_path / 'single_file'
        file1 = tmp_path / 'file1'
        file2 = tmp_path / 'file2'
        file0.write_text('aaxxxbb\nccc\nxxx xxx\nyyy\n')
        file1.write_text('2xaaxxxbb\nxxx xxx\nccc\nyyy\n')
        file2.write_text('ccc\nyyy\nxxxaabb\nxxx xxx\n')
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.backup_if_needed = mock_backup

        testobj.p = {'zoek': 'xxx', 'filelist': [str(file0)]}
        lines_to_replace = [[1], [3]]
        assert testobj.replace_selected('yyy', lines_to_replace) == len(lines_to_replace)
        assert file0.read_text() == "aayyybb\nccc\nyyy yyy\nyyy\n"
        assert capsys.readouterr().out == (
                f"called Finder.backup_if_needed with arg '{file0}'\n")

        testobj.p = {'zoek': 'xxx', 'filelist': [str(tmp_path / 'file1'), str(tmp_path / 'file2')]}
        lines_to_replace = [[str(file1), 1], [str(file1), 2], [str(file2), 3], [str(file2), 4]]
        assert testobj.replace_selected('yyy', lines_to_replace) == len(lines_to_replace)
        assert file1.read_text() == "2xaayyybb\nyyy yyy\nccc\nyyy\n"
        assert file2.read_text() == "ccc\nyyy\nyyyaabb\nyyy yyy\n"
        assert capsys.readouterr().out == (
                f"called Finder.backup_if_needed with arg '{file1}'\n"
                f"called Finder.backup_if_needed with arg '{file2}'\n")

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
