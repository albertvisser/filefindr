"""unittests for ./afrift/gui_qt.py
"""
import types
import pytest
from afrift import gui_qt as testee
from mockgui import mockqtwidgets as mockqtw


selectnames_out = """\
called VBox.__init__
called Label.__init__ with args ('heading', {testobj})
called HBox.__init__
called HBox.addWidget with arg MockLabel
called VBox.addLayout with arg MockHBoxLayout
called CheckBox.__init__ with text 'sel-all'
called Signal.connect with args ({testobj.select_all},)
called HBox.__init__
called HBox.addSpacing
called HBox.addWidget with arg MockCheckBox
called PushButton.__init__ with args ('invert', {testobj}) {{}}
called Signal.connect with args ({testobj.invert_selection},)
called HBox.addStretch
called HBox.addWidget with arg MockPushButton
called HBox.addSpacing
called VBox.addLayout with arg MockHBoxLayout
called Frame.__init__
called VBox.__init__
called CheckBox.__init__ with text 'xxxx'
called HBox.__init__
called HBox.addWidget with arg MockCheckBox
called VBox.addLayout with arg MockHBoxLayout
called CheckBox.__init__ with text 'yyyy'
called HBox.__init__
called HBox.addWidget with arg MockCheckBox
called VBox.addLayout with arg MockHBoxLayout
called Frame.setLayout with arg MockVBoxLayout
called ScrollArea.__init__ with args ({testobj},)
called ScrollArea.setWidget with arg `MockFrame`
called HBox.__init__
called HBox.addWidget with arg MockScrollArea
called VBox.addLayout with arg MockHBoxLayout
called PushButton.__init__ with args ('exit', {testobj}) {{}}
called Signal.connect with args ({testobj.reject},)
called PushButton.__init__ with args ('execute', {testobj}) {{}}
called Signal.connect with args ({testobj.accept},)
called HBox.__init__
called HBox.__init__
called HBox.addStretch
called HBox.addWidget with arg MockPushButton
called HBox.addWidget with arg MockPushButton
called HBox.addStretch
called HBox.addLayout with arg MockHBoxLayout
called VBox.addLayout with arg MockHBoxLayout
called Dialog.setLayout
"""
results_start = """\
called VBox.__init__
called HBox.__init__
called Label.__init__ with args ('head', {testobj})
called HBox.addWidget with arg MockLabel
called HBox.addStretch
called PushButton.__init__ with args ('Go to selected result', {testobj}) {{}}
called Signal.connect with args ({testobj.to_result},)
called HBox.addWidget with arg MockPushButton
called VBox.addLayout with arg MockHBoxLayout
"""
results_dets_1a = """\
called HBox.__init__
called Table.__init__ with args ({testobj},)
called Header.__init__
called Header.__init__
called Table.verticalHeader
called Header.setVisible with args 'False'
called Table.setGridStyle with arg PenStyle.NoPen
"""
results_dets_1b1 = """\
called Table.setColumnCount with arg '2'
called Table.setHorizontalHeaderLabels with arg '('title', 'text')'
"""
results_dets_1b2 = """\
called Table.setColumnCount with arg '3'
called Table.setHorizontalHeaderLabels with arg '('title', 'ctext', 'text')'
"""
results_dets_1c = """\
called Table.horizontalHeader
called Header.setStretchLastSection with arg True
called ResultsGui.populate_list
called Table.resizeColumnsToContents
called Signal.connect with args ()
called Action.__init__ with args ('help', {testobj})
called Action.setShortcut with arg `F1`
called Signal.connect with args ({testobj.master.help},)
called Dialog.addAction
called Action.__init__ with args ('result', {testobj})
called Action.setShortcut with arg `Ctrl+G`
called Signal.connect with args ({testobj.to_result},)
called Dialog.addAction
called HBox.addWidget with arg MockTable
called VBox.addLayout with arg MockHBoxLayout
"""
results_middle = """\
called HBox.__init__
called HBox.addStretch
called PushButton.__init__ with args ('exit', {testobj}) {{}}
called Signal.connect with args ({testobj.klaar},)
called HBox.addWidget with arg MockPushButton
"""
results_dets_2 = """\
called VBox.__init__
called HBox.__init__
called PushButton.__init__ with args ('rept', {testobj}) {{}}
called Signal.connect with args ({testobj.master.refresh},){pvervang}
called HBox.addWidget with arg MockPushButton
called PushButton.__init__ with args ('copy', {testobj}) {{}}
called Signal.connect with args ({testobj.master.kopie},)
called HBox.addWidget with arg MockPushButton
called PushButton.__init__ with args ('clip', {testobj}) {{}}
called Signal.connect with args ({testobj.master.to_clipboard},)
called HBox.addWidget with arg MockPushButton
called HBox.addStretch
called VBox.addLayout with arg MockHBoxLayout
called HBox.__init__
called PushButton.__init__ with args ('alt', {testobj}) {{}}
called Signal.connect with args ({testobj.master.zoek_anders},)
called HBox.addWidget with arg MockPushButton
called PushButton.__init__ with args ('sel', {testobj}) {{}}
called Signal.connect with args ({testobj.master.vervang_in_sel},){pvervang}
called HBox.addWidget with arg MockPushButton
called PushButton.__init__ with args ('all', {testobj}) {{}}
called Signal.connect with args ({testobj.master.vervang_alles},){pvervang}
called HBox.addWidget with arg MockPushButton
called VBox.addLayout with arg MockHBoxLayout
called HBox.addLayout with arg MockVBoxLayout
called Grid.__init__
called Label.__init__ with args ('frmt', {testobj})
called Grid.addWidget with arg MockLabel at (0, 0)
called CheckBox.__init__ with text '&path'
called CheckBox.setChecked with arg True{sfile}
called Grid.addWidget with arg MockCheckBox at (1, 0)
called CheckBox.__init__ with text 'd&elim'
called CheckBox.setChecked with arg True
called Grid.addWidget with arg MockCheckBox at (0, 1)
called CheckBox.__init__ with text 's&umm'
called CheckBox.setChecked with arg True
called Grid.addWidget with arg MockCheckBox at (1, 1)
called HBox.addLayout with arg MockGridLayout
called HBox.addStretch
"""
results_end = """\
called VBox.addLayout with arg MockHBoxLayout
called Dialog.setLayout
"""
results_dets_3 = """\
called Dialog.resize with args (624, 488)
"""
results_dets_3a = """\
called Dialog.resize with args (824, 488)
"""
populate_1 = """\
called Table.insertRow with arg '0'
called Table.setRowHeight with args (0, 18)
called TableItem.__init__ with arg 'x'
called TableItem.setToolTip with arg x
called TableItem.setFlags with arg ItemFlag.ItemIsSelectable|ItemIsEnabled
called Table.setItem with args (0, 0, MockTableItem)
called TableItem.__init__ with arg 'z'
called TableItem.setToolTip with arg z
called TableItem.setFlags with arg ItemFlag.ItemIsSelectable|ItemIsEnabled
called Table.setItem with args (0, 1, MockTableItem)
called Table.insertRow with arg '1'
called Table.setRowHeight with args (1, 18)
called TableItem.__init__ with arg 'a'
called TableItem.setToolTip with arg a
called TableItem.setFlags with arg ItemFlag.ItemIsSelectable|ItemIsEnabled
called Table.setItem with args (1, 0, MockTableItem)
called TableItem.__init__ with arg 'c'
called TableItem.setToolTip with arg c
called TableItem.setFlags with arg ItemFlag.ItemIsSelectable|ItemIsEnabled
called Table.setItem with args (1, 1, MockTableItem)
"""
populate_2 = """\
called Table.insertRow with arg '0'
called Table.setRowHeight with args (0, 18)
called TableItem.__init__ with arg 'x'
called TableItem.setToolTip with arg x
called TableItem.setFlags with arg ItemFlag.ItemIsSelectable|ItemIsEnabled
called Table.setItem with args (0, 0, MockTableItem)
called TableItem.__init__ with arg 'y'
called TableItem.setToolTip with arg y
called TableItem.setFlags with arg ItemFlag.ItemIsSelectable|ItemIsEnabled
called Table.setItem with args (0, 1, MockTableItem)
called TableItem.__init__ with arg 'z'
called TableItem.setToolTip with arg z
called TableItem.setFlags with arg ItemFlag.ItemIsSelectable|ItemIsEnabled
called Table.setItem with args (0, 2, MockTableItem)
called Table.insertRow with arg '1'
called Table.setRowHeight with args (1, 18)
called TableItem.__init__ with arg 'a'
called TableItem.setToolTip with arg a
called TableItem.setFlags with arg ItemFlag.ItemIsSelectable|ItemIsEnabled
called Table.setItem with args (1, 0, MockTableItem)
called TableItem.__init__ with arg 'b'
called TableItem.setToolTip with arg b
called TableItem.setFlags with arg ItemFlag.ItemIsSelectable|ItemIsEnabled
called Table.setItem with args (1, 1, MockTableItem)
called TableItem.__init__ with arg 'c'
called TableItem.setToolTip with arg c
called TableItem.setFlags with arg ItemFlag.ItemIsSelectable|ItemIsEnabled
called Table.setItem with args (1, 2, MockTableItem)
"""
main_start = """\
called Grid.__init__
called MainGui.add_combobox_row with args ('zk', ['x', 'x', 'x']) {{}}
called ComboBox.__init__{zoektxt}
called MainGui.add_checkbox_row with args ('rg', 'rex') {{}}
called CheckBox.__init__
called MainGui.add_checkbox_row with args ('cs', 'bbb') {{}}
called CheckBox.__init__
called MainGui.add_checkbox_row with args ('wrd', 'ccc') {{}}
called CheckBox.__init__
called MainGui.add_combobox_row with args ('verv', ['y', 'y', 'y']) {{}}
called ComboBox.__init__{vervtxt}
called ComboBox.completer
called Completer.setCaseSensitivity with arg CaseSensitivity.CaseSensitive
called MainGui.add_checkbox_row with args ('emp', {testobj.master.always_replace}) {{}}
called CheckBox.__init__
called MainGui.add_checkbox_row with args ('bak', {testobj.master.maak_backups}) {{}}
called CheckBox.__init__
called MainGui.add_checkbox_row with args ('ex', {testobj.master.exit_when_ready}) {{}}
called CheckBox.__init__
"""
main_open = """\
called PushButton.__init__ with args ('zk',) {{}}
called Signal.connect with args ({testobj.zoekdir},)
called MainGui.add_combobox_row with args ('in', ['a', 'b']) {{'initial': '', 'button': {testobj.zoek}}}
called ComboBox.__init__
called ComboBox.setCompleter with arg None
called Signal.connect with args ({testobj.check_loc},)
"""
main_single = """\
called Label.__init__ with args ('ins',)
called Grid.addWidget with arg MockLabel at (0, 0)
called HBox.__init__
called Label.__init__ with args ('qqq',)
called HBox.addWidget with arg MockLabel
called HBox.addStretch
called Grid.addLayout with arg MockHBoxLayout at (0, 1)
"""
main_dir = """\
called MainGui.add_checkbox_row with args ('subs', True) {{}}
"""
main_multi = """\
called Label.__init__ with args ('inm',)
called Grid.addWidget with arg MockLabel at (0, 0, 1, 2)
called List.__init__
called List.insertItems with args (0, ['qqq'])
called Grid.addWidget with arg MockListBox at (1, 0, 1, 2)
called MainGui.add_checkbox_row with args ('submsubs', True) {{}}
"""
main_nonfile = """\
called CheckBox.__init__
called SpinBox.__init__
called SpinBox.setMinimum with arg '-1'
called SpinBox.setValue with arg '5'
called MainGui.add_checkbox_row with args ('lnk',) {{'toggler': 'f_s', 'spinner': {testobj.vraag_diepte}}}
called CheckBox.__init__
called MainGui.add_checkbox_row with args ('skpd', 's_s') {{}}
called CheckBox.__init__
called MainGui.add_checkbox_row with args ('skpf', 's_f') {{}}
called CheckBox.__init__
called MainGui.add_combobox_row with args ('ft', ['1', '2']) {{}}
called ComboBox.__init__{exttext}
"""
main_end = """\
called MainGui.add_checkbox_row with args ('ctx', 'ctx') {{}}
called CheckBox.__init__
called MainGui.add_checkbox_row with args ('ign', 'neg') {{'indent': 22}}
called CheckBox.__init__
called HBox.__init__
called HBox.addStretch
called PushButton.__init__ with args ('ex', {testobj}) {{}}
called Signal.connect with args ({testobj.master.doe},)
called HBox.addWidget with arg MockPushButton
called PushButton.__init__ with args ('end', {testobj}) {{}}
called Signal.connect with args ({testobj.close},)
called HBox.addWidget with arg MockPushButton
called HBox.addStretch
called Grid.addLayout with arg MockHBoxLayout at ({testobj.row}, 0, 1, 2)
called VBox.__init__
called VBox.addLayout with arg MockGridLayout
called Widget.setLayout with arg MockVBoxLayout
called ComboBox.setFocus
"""

@pytest.fixture
def expected_output():
    """output from GUI creation methods
    """
    return {'selectnames': selectnames_out, 'results': results_start + results_middle + results_end,
            'results_2': results_start + results_dets_1a + results_dets_1b1 + results_dets_1c
            + results_middle + results_dets_2 + results_end + results_dets_3,
            'results_2a': results_start + results_dets_1a + results_dets_1b2 + results_dets_1c
            + results_middle + results_dets_2 + results_end + results_dets_3a,
            'populate': populate_1, 'populate2': populate_2,
            'base': main_start + main_open + main_dir + main_nonfile + main_end,
            'file': main_start + main_single + main_end,
            'dir': main_start + main_single + main_dir + main_nonfile + main_end,
            'multi': main_start + main_multi + main_nonfile + main_end}

class MockSelect:
    "stub for main.SelectNames objeect"
    def __init__(self):
        print('called Selectnames.__init__')


class MockResults:
    "stub for main.Results objeect"
    def __init__(self):
        print('called Results.__init__')


class MockMain:
    "stub for main.MainFrame objeect"
    def __init__(self):
        print('called MainFrame.__init__')
        self.gui = MockMainGui()


class MockMainGui:
    "stub for gui.MainFrameGui object"
    def __init__(self):
        print('called MainFrameGui.__init__')


class TestSelectNamesGui:
    """unittest for gui_qt.SelectNamesGui
    """
    def setup_testobj(self, monkeypatch, capsys):
        """stub for gui_qt.SelectNamesGui object

        create the object skipping the normal initialization
        intercept messages during creation
        return the object so that other methods can be monkeypatched in the caller
        """
        def mock_init(self, *args):
            """stub
            """
            print('called SelectNamesGui.__init__ with args', args)
        monkeypatch.setattr(testee.SelectNamesGui, '__init__', mock_init)
        testobj = testee.SelectNamesGui()
        testobj.parent = MockMain()
        testobj.master = MockSelect()
        assert capsys.readouterr().out == ("called SelectNamesGui.__init__ with args ()\n"
                                           "called MainFrame.__init__\n"
                                           "called MainFrameGui.__init__\n"
                                           "called Selectnames.__init__\n")
        return testobj

    def test_init(self, monkeypatch, capsys):
        """unittest for SelectNamesGui.__init__
        """
        def mock_set(self, arg):
            print(f"called Dialog.setWindowIcon with arg {type(arg).__name__}")
        monkeypatch.setattr(testee.qtw.QDialog, '__init__', mockqtw.MockDialog.__init__)
        monkeypatch.setattr(testee.qtw.QDialog, 'setWindowTitle', mockqtw.MockDialog.setWindowTitle)
        monkeypatch.setattr(testee.qtw.QDialog, 'setWindowIcon', mock_set)
        monkeypatch.setattr(testee.gui, 'QIcon', mockqtw.MockIcon)
        parent = MockMain()
        master = MockSelect()
        master.title = 'title'
        master.iconame = 'ico'
        testobj = testee.SelectNamesGui(parent, master)
        assert capsys.readouterr().out == ("called MainFrame.__init__\n"
                                           "called MainFrameGui.__init__\n"
                                           "called Selectnames.__init__\n"
                                           f"called Dialog.__init__ with args {parent.gui} () {{}}\n"
                                           "called Dialog.setWindowTitle with args ('title',)\n"
                                           "called Icon.__init__ with arg `ico`\n"
                                           "called Dialog.setWindowIcon with arg MockIcon\n")

    def test_setup_screen(self, monkeypatch, capsys, expected_output):
        """unittest for SelectNamesGui.setup_screen
        """
        class MockFile:
            "stub"
            def __init__(self, arg):
                self._name = arg
            def __str__(self):
                return self._name
        monkeypatch.setattr(testee.qtw, 'QVBoxLayout', mockqtw.MockVBoxLayout)
        monkeypatch.setattr(testee.qtw, 'QHBoxLayout', mockqtw.MockHBoxLayout)
        monkeypatch.setattr(testee.qtw, 'QFrame', mockqtw.MockFrame)
        monkeypatch.setattr(testee.qtw, 'QLabel', mockqtw.MockLabel)
        monkeypatch.setattr(testee.qtw, 'QPushButton', mockqtw.MockPushButton)
        monkeypatch.setattr(testee.qtw, 'QCheckBox', mockqtw.MockCheckBox)
        monkeypatch.setattr(testee.qtw, 'QScrollArea', mockqtw.MockScrollArea)
        monkeypatch.setattr(testee.qtw.QDialog, 'setLayout', mockqtw.MockDialog.setLayout)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.master.parent = testobj.parent
        testobj.master.parent.names = ['xxxx', 'yyyy']
        testobj.master.do_files = False
        testobj.select_all = lambda: 'dummy'
        testobj.invert_selection = lambda: 'dummy'
        captions = {'heading': 'heading', 'sel_all': 'sel-all', 'invert': 'invert', 'exit': 'exit',
                    'execute': 'execute'}
        testobj.setup_screen(captions)
        assert isinstance(testobj.sel_all, testee.qtw.QCheckBox)
        assert isinstance(testobj.flip_sel, testee.qtw.QPushButton)
        assert len(testobj.checklist) == 2
        assert isinstance(testobj.checklist[0], testee.qtw.QCheckBox)
        assert isinstance(testobj.checklist[1], testee.qtw.QCheckBox)
        assert capsys.readouterr().out == expected_output['selectnames'].format(testobj=testobj)
        testobj.master.parent.names = [MockFile('xxxx'), MockFile('yyyy')]
        testobj.master.do_files = True
        testobj.setup_screen(captions)
        assert isinstance(testobj.sel_all, testee.qtw.QCheckBox)
        assert isinstance(testobj.flip_sel, testee.qtw.QPushButton)
        assert len(testobj.checklist) == 2
        assert isinstance(testobj.checklist[0], testee.qtw.QCheckBox)
        assert isinstance(testobj.checklist[1], testee.qtw.QCheckBox)
        assert capsys.readouterr().out == expected_output['selectnames'].format(testobj=testobj)

    def test_go(self, monkeypatch, capsys):
        """unittest for SelectNamesGui.go
        """
        def mock_exec():
            print('called Dialog.exec')
            return testee.qtw.QDialog.DialogCode.Accepted
        monkeypatch.setattr(testee.qtw.QDialog, 'exec', mockqtw.MockDialog.exec)
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert not testobj.go()
        assert capsys.readouterr().out == "called Dialog.exec\n"
        testobj.exec = mock_exec
        assert testobj.go()
        assert capsys.readouterr().out == "called Dialog.exec\n"

    def test_select_all(self, monkeypatch, capsys):
        """unittest for SelectNamesGui.select_all
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.sel_all = mockqtw.MockCheckBox()
        testobj.checklist = [mockqtw.MockCheckBox(), mockqtw.MockCheckBox()]
        assert capsys.readouterr().out == ("called CheckBox.__init__\ncalled CheckBox.__init__\n"
                                           "called CheckBox.__init__\n")
        testobj.select_all()
        assert capsys.readouterr().out == ("called CheckBox.isChecked\n"
                                           "called CheckBox.setChecked with arg False\n"
                                           "called CheckBox.setChecked with arg False\n")
        for item in testobj.checklist:
            assert not item.isChecked()

    def test_select_all_2(self, monkeypatch, capsys):
        """unittest for SelectNamesGui.select_all
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.sel_all = mockqtw.MockCheckBox()
        testobj.checklist = [mockqtw.MockCheckBox(), mockqtw.MockCheckBox()]
        testobj.sel_all.setChecked(True)
        assert capsys.readouterr().out == ("called CheckBox.__init__\ncalled CheckBox.__init__\n"
                                           "called CheckBox.__init__\n"
                                           "called CheckBox.setChecked with arg True\n")
        testobj.select_all()
        assert capsys.readouterr().out == ("called CheckBox.isChecked\n"
                                           "called CheckBox.setChecked with arg True\n"
                                           "called CheckBox.setChecked with arg True\n")
        for item in testobj.checklist:
            assert item.isChecked()

    def test_invert_selection(self, monkeypatch, capsys):
        """unittest for SelectNamesGui.invert_selection
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.checklist = [mockqtw.MockCheckBox(), mockqtw.MockCheckBox()]
        testobj.checklist[0].setChecked(True)
        assert capsys.readouterr().out == ("called CheckBox.__init__\ncalled CheckBox.__init__\n"
                                           "called CheckBox.setChecked with arg True\n")
        testobj.invert_selection()
        assert capsys.readouterr().out == ("called CheckBox.isChecked\n"
                                           "called CheckBox.setChecked with arg False\n"
                                           "called CheckBox.isChecked\n"
                                           "called CheckBox.setChecked with arg True\n")
        assert not testobj.checklist[0].isChecked()
        assert testobj.checklist[1].isChecked()

    def test_accept(self, monkeypatch, capsys):
        """unittest for SelectNamesGui.accept
        """
        monkeypatch.setattr(testee.qtw.QDialog, 'accept', mockqtw.MockDialog.accept)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.master.do_files = False
        testobj.master.names = {'x': 'xxx', 'w': 'www', 'y': 'yyy'}
        testobj.checklist = [mockqtw.MockCheckBox('x'), mockqtw.MockCheckBox('y'),
                             mockqtw.MockCheckBox('w')]
        testobj.checklist[0].setChecked(True)
        testobj.checklist[2].setChecked(True)
        assert capsys.readouterr().out == ("called CheckBox.__init__ with text 'x'\n"
                                           "called CheckBox.__init__ with text 'y'\n"
                                           "called CheckBox.__init__ with text 'w'\n"
                                           "called CheckBox.setChecked with arg True\n"
                                           "called CheckBox.setChecked with arg True\n")
        testobj.accept()
        assert testobj.master.names == ['x', 'w']
        assert capsys.readouterr().out == ("called CheckBox.isChecked\n"
                                           "called CheckBox.isChecked\n"
                                           "called CheckBox.isChecked\n"
                                           "called Dialog.accept\n")
        testobj.master.do_files = True
        testobj.master.names = {'x': 'xxx', 'w': 'www', 'y': 'yyy'}
        testobj.checklist[2].setChecked(False)
        assert capsys.readouterr().out == "called CheckBox.setChecked with arg False\n"
        testobj.accept()
        assert testobj.master.names == ['www', 'yyy']
        assert capsys.readouterr().out == ("called CheckBox.isChecked\n"
                                           "called CheckBox.isChecked\n"
                                           "called CheckBox.isChecked\n"
                                           "called Dialog.accept\n")


class TestResultsGui:
    """unittest for gui_qt.ResultsGui
    """
    def setup_testobj(self, monkeypatch, capsys):
        """stub for gui_qt.ResultsGui object

        create the object skipping the normal initialization
        intercept messages during creation
        return the object so that other methods can be monkeypatched in the caller
        """
        def mock_init(self, *args):
            """stub
            """
            print('called ResultsGui.__init__ with args', args)
        monkeypatch.setattr(testee.ResultsGui, '__init__', mock_init)
        testobj = testee.ResultsGui()
        testobj.parent = MockMain()
        testobj.master = MockResults()
        assert capsys.readouterr().out == ('called ResultsGui.__init__ with args ()\n'
                                           "called MainFrame.__init__\n"
                                           "called MainFrameGui.__init__\n"
                                           "called Results.__init__\n")
        return testobj

    def test_init(self, monkeypatch, capsys):
        """unittest for ResultsGui.__init__
        """
        def mock_set(self, arg):
            print(f"called Dialog.setWindowIcon with arg {type(arg).__name__}")
        monkeypatch.setattr(testee.qtw.QDialog, '__init__', mockqtw.MockDialog.__init__)
        monkeypatch.setattr(testee.qtw.QDialog, 'setWindowTitle', mockqtw.MockDialog.setWindowTitle)
        monkeypatch.setattr(testee.qtw.QDialog, 'setWindowIcon', mock_set)
        monkeypatch.setattr(testee.gui, 'QIcon', mockqtw.MockIcon)
        master = MockResults()
        master.parent = types.SimpleNamespace(resulttitel='title')
        master.iconame = 'ico'
        parent = MockMain()
        testobj = testee.ResultsGui(parent, master)
        assert testobj.show_result_details
        assert capsys.readouterr().out == ("called Results.__init__\n"
                                           "called MainFrame.__init__\n"
                                           "called MainFrameGui.__init__\n"
                                           f"called Dialog.__init__ with args {parent.gui} () {{}}\n"
                                           "called Dialog.setWindowTitle with args ('title',)\n"
                                           "called Icon.__init__ with arg `ico`\n"
                                           "called Dialog.setWindowIcon with arg MockIcon\n")

    def test_setup_screen(self, monkeypatch, capsys, expected_output):
        """unittest for ResultsGui.setup_screen
        """
        def mock_populate():
            print('called ResultsGui.populate_list')
        monkeypatch.setattr(testee.qtw, 'QVBoxLayout', mockqtw.MockVBoxLayout)
        monkeypatch.setattr(testee.qtw, 'QHBoxLayout', mockqtw.MockHBoxLayout)
        monkeypatch.setattr(testee.qtw, 'QGridLayout', mockqtw.MockGridLayout)
        monkeypatch.setattr(testee.qtw, 'QLabel', mockqtw.MockLabel)
        monkeypatch.setattr(testee.qtw, 'QPushButton', mockqtw.MockPushButton)
        monkeypatch.setattr(testee.qtw, 'QCheckBox', mockqtw.MockCheckBox)
        monkeypatch.setattr(testee.qtw, 'QTableWidget', mockqtw.MockTable)
        monkeypatch.setattr(testee.gui, 'QAction', mockqtw.MockAction)
        monkeypatch.setattr(testee.qtw.QDialog, 'addAction', mockqtw.MockDialog.addAction)
        monkeypatch.setattr(testee.qtw.QDialog, 'resize', mockqtw.MockDialog.resize)
        monkeypatch.setattr(testee.qtw.QDialog, 'setLayout', mockqtw.MockDialog.setLayout)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.master.parent = types.SimpleNamespace(apptype="single",
                                                      outopts={'full_path': True, 'as_csv': True,
                                                               'summarize': True},
                                                      p={'vervang': ''})
        testobj.master.titel = 'title'
        testobj.klaar = lambda: 'klaar'
        testobj.populate_list = mock_populate
        testobj.master.goto_result = lambda: 'goto'
        testobj.master.help = lambda: 'help'
        testobj.to_result = lambda: 'to_result'
        testobj.master.refresh = lambda: 'refresh'
        testobj.master.kopie = lambda: 'kopie'
        testobj.master.to_clipboard = lambda: 'to_clipboard'
        testobj.master.zoek_anders = lambda: 'zoek_anders'
        testobj.master.vervang_in_sel = lambda: 'vervang_in_sel'
        testobj.master.vervang_alles = lambda: 'vervang_alles'
        testobj.show_result_details = False
        captions = {'heading': 'head', 'ctxt': 'ctext', 'txt': 'text', 'hlp': 'help',
                    'rslt': 'result', 'exit': 'exit',
                    'rpt': 'rept', 'cpy': 'copy', 'clp': 'clip', 'alt': 'alt', 'sel': 'sel',
                    'all': 'all', 'fmt': 'frmt', 'pth': 'path', 'dlm': 'delim', 'sum': 'summ'}
        testobj.setup_screen(captions)
        assert isinstance(testobj.txt, testee.qtw.QLabel)
        assert capsys.readouterr().out == expected_output['results'].format(testobj=testobj,
                                                                            pvervang='',
                                                                            sfile='')
        testobj.show_result_details = True
        testobj.master.show_context = False
        testobj.setup_screen(captions)
        assert isinstance(testobj.txt, testee.qtw.QLabel)
        assert capsys.readouterr().out == expected_output['results_2'].format(testobj=testobj,
                                                                            pvervang='',
                                                                            sfile='')
        testobj.master.show_context = True
        testobj.master.parent.p['vervang'] = 'x'
        testobj.master.parent.apptype = 'single-file'
        testobj.setup_screen(captions)
        assert isinstance(testobj.txt, testee.qtw.QLabel)
        assert capsys.readouterr().out == expected_output['results_2a'].format(
                testobj=testobj, pvervang='\ncalled PushButton.setEnabled with arg `False`',
                sfile='\ncalled CheckBox.setEnabled with arg False')

    def test_populate_list(self, monkeypatch, capsys, expected_output):
        """unittest for ResultsGui.populate_list
        """
        monkeypatch.setattr(testee.qtw, 'QTableWidgetItem', mockqtw.MockTableItem)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.lijst = mockqtw.MockTable()
        assert capsys.readouterr().out == ("called Table.__init__ with args ()\n"
                                           "called Header.__init__\n"
                                           "called Header.__init__\n")
        testobj.master.results = ['no results']
        testobj.populate_list()
        assert capsys.readouterr().out == ""
        testobj.master.results = ['results', ['x', 'y', 'z'], ['a', 'b', 'c']]
        testobj.master.show_context = False
        testobj.populate_list()
        assert capsys.readouterr().out == expected_output['populate']
        testobj.master.show_context = True
        testobj.populate_list()
        assert capsys.readouterr().out == expected_output['populate2']

    def test_clear_contents(self, monkeypatch, capsys):
        """unittest for ResultsGui.clear_contents
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.lijst = mockqtw.MockTable()
        assert capsys.readouterr().out == ("called Table.__init__ with args ()\n"
                                           "called Header.__init__\n"
                                           "called Header.__init__\n")
        testobj.clear_contents()
        assert capsys.readouterr().out == "called Table.clearContents\n"

    def test_go(self, monkeypatch, capsys):
        """unittest for ResultsGui.go
        """
        monkeypatch.setattr(testee.qtw.QDialog, 'exec', mockqtw.MockDialog.exec)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.go()
        assert capsys.readouterr().out == "called Dialog.exec\n"

    def test_breekaf(self, monkeypatch, capsys):
        """unittest for ResultsGui.breekaf
        """
        def mock_meld(*args):
            print('called Results.meld with args', args)
        monkeypatch.setattr(testee.qtw.QDialog, 'done', mockqtw.MockDialog.done)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.master.parent = types.SimpleNamespace(resulttitel='results')
        testobj.meld = mock_meld
        testobj.breekaf('message')
        assert capsys.readouterr().out == ("called Results.meld with args ('results', 'message')\n"
                                           "called Dialog.done with arg `0`\n")
        testobj.breekaf('message', False)
        assert capsys.readouterr().out == "called Results.meld with args ('results', 'message')\n"

    def test_set_header(self, monkeypatch, capsys):
        """unittest for ResultsGui.set_header
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.txt = mockqtw.MockLabel()
        assert capsys.readouterr().out == "called Label.__init__\n"
        testobj.set_header('text')
        assert capsys.readouterr().out == "called Label.setText with arg `text`\n"

    def test_get_pth(self, monkeypatch, capsys):
        """unittest for ResultsGui.get_pth
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.cb_path = mockqtw.MockCheckBox()
        assert capsys.readouterr().out == "called CheckBox.__init__\n"
        assert not testobj.get_pth()
        assert capsys.readouterr().out == "called CheckBox.isChecked\n"
        testobj.cb_path.setChecked(True)
        assert capsys.readouterr().out == "called CheckBox.setChecked with arg True\n"
        assert testobj.get_pth()
        assert capsys.readouterr().out == "called CheckBox.isChecked\n"

    def test_get_csv(self, monkeypatch, capsys):
        """unittest for ResultsGui.get_csv
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.cb_delim = mockqtw.MockCheckBox()
        assert capsys.readouterr().out == "called CheckBox.__init__\n"
        assert not testobj.get_csv()
        assert capsys.readouterr().out == "called CheckBox.isChecked\n"
        testobj.cb_delim.setChecked(True)
        assert capsys.readouterr().out == "called CheckBox.setChecked with arg True\n"
        assert testobj.get_csv()
        assert capsys.readouterr().out == "called CheckBox.isChecked\n"

    def test_get_sum(self, monkeypatch, capsys):
        """unittest for ResultsGui.get_sum
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.cb_smrz = mockqtw.MockCheckBox()
        assert capsys.readouterr().out == "called CheckBox.__init__\n"
        assert not testobj.get_sum()
        assert capsys.readouterr().out == "called CheckBox.isChecked\n"
        testobj.cb_smrz.setChecked(True)
        assert capsys.readouterr().out == "called CheckBox.setChecked with arg True\n"
        assert testobj.get_sum()
        assert capsys.readouterr().out == "called CheckBox.isChecked\n"

    def test_get_savefile(self, monkeypatch, capsys, tmp_path):
        """unittest for ResultsGui.get_savefile
        """
        monkeypatch.setattr(testee.qtw.QFileDialog, 'getSaveFileName',
                            mockqtw.MockFileDialog.getSaveFileName)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.master.parent = types.SimpleNamespace(hier=tmp_path)
        assert testobj.get_savefile('fname', '.csv') == ""
        assert capsys.readouterr().out == (
                f"called FileDialog.getSaveFileName with args {testobj}"
                f" ('Resultaat naar bestand kopieren', '{tmp_path}/fname',"
                " 'Comma delimited files (*.csv);;All files (*.*)') {}\n")
        assert testobj.get_savefile('fname', '.txt') == ""
        assert capsys.readouterr().out == (
                f"called FileDialog.getSaveFileName with args {testobj}"
                f" ('Resultaat naar bestand kopieren', '{tmp_path}/fname',"
                " 'Text files (*.txt);;All files (*.*)') {}\n")
        # assert testobj.get_savefile('fname', 'whatever') == "expected_result"
        # dit gaat fout (hoort zo, maar wil ik dit netjes afhandelen?)

    def test_meld(self, monkeypatch, capsys):
        """unittest for ResultsGui.meld
        """
        monkeypatch.setattr(testee.qtw.QMessageBox, 'information',
                            mockqtw.MockMessageBox.information)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.meld('title', 'message')
        assert capsys.readouterr().out == (
                f"called MessageBox.information with args `{testobj}` `title` `message`\n")

    def test_get_text_from_user(self, monkeypatch, capsys):
        """unittest for ResultsGui.get_text_from_user
        """
        monkeypatch.setattr(testee.qtw.QInputDialog, 'getText',
                            mockqtw.MockInputDialog.getText)
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.get_text_from_user('title', 'prompt') == ('', False)
        assert capsys.readouterr().out == (
                f"called InputDialog.getText with args {testobj} ('title', 'prompt') {{}}\n")

    def test_get_selection(self, monkeypatch, capsys):
        """unittest for ResultsGui.get_selection
        """
        def mock_selected():
            print('called Table.selectedItems')
            return [types.SimpleNamespace(row=lambda: 1), types.SimpleNamespace(row=lambda: 2)]
        def mock_item(x, y):
            print(f"called Table.item with args ({x}, {y})")
            if x == 1:
                return types.SimpleNamespace(text=lambda: 'xxx')
            if x == 2:
                return types.SimpleNamespace(text=lambda: 'yyy')
            return types.SimpleNamespace(text='zzz')
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.lijst = mockqtw.MockTable()
        assert capsys.readouterr().out == ("called Table.__init__ with args ()\n"
                                           "called Header.__init__\n"
                                           "called Header.__init__\n")
        testobj.lijst.item = mock_item
        assert testobj.get_selection() == []
        assert capsys.readouterr().out == ("called Table.selectedItems\n")
        testobj.lijst.selectedItems = mock_selected
        assert testobj.get_selection() == ['xxx', 'yyy']
        assert capsys.readouterr().out == ("called Table.selectedItems\n"
                                           "called Table.item with args (1, 0)\n"
                                           "called Table.item with args (2, 0)\n")

    def test_copy_to_clipboard(self, monkeypatch, capsys):
        """unittest for ResultsGui.copy_to_clipboard
        """
        monkeypatch.setattr(testee.qtw, 'QApplication', mockqtw.MockApplication)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.copy_to_clipboard('text')
        assert capsys.readouterr().out == ("called Application.clipboard\n"
                                           "called ClipBoard.__init__\n"
                                           "called Clipboard.setText with arg 'text'\n")

    def test_to_result(self, monkeypatch, capsys):
        """unittest for ResultsGui.to_result
        """
        def mock_goto(*args):
            print("called Results.goto_result with args", args)
        def mock_col():
            print("called Table.currentColumn")
            return -1
        def mock_row():
            print("called Table.currentRow")
            return -1
        def mock_meld(*args):
            print('called Results.meld with args', args)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.meld = mock_meld
        testobj.lijst = mockqtw.MockTable()
        testobj.master.parent = types.SimpleNamespace(resulttitel='xxx')
        assert capsys.readouterr().out == ("called Table.__init__ with args ()\n"
                                           "called Header.__init__\n"
                                           "called Header.__init__\n")
        testobj.master.goto_result = mock_goto
        testobj.to_result()
        assert capsys.readouterr().out == ("called Table.currentRow\n"
                                           "called Table.currentColumn\n"
                                           "called Results.goto_result with args (2, 1)\n")
        testobj.lijst.currentRow = mock_row
        testobj.to_result()
        assert capsys.readouterr().out == ("called Table.currentRow\n"
                                           "called Table.currentColumn\n"
                                           "called Results.meld with args ('xxx',"
                                           " 'Select a result first')\n")
        testobj.lijst = mockqtw.MockTable()
        assert capsys.readouterr().out == ("called Table.__init__ with args ()\n"
                                           "called Header.__init__\n"
                                           "called Header.__init__\n")
        testobj.lijst.currentColumn = mock_col
        testobj.to_result()
        assert capsys.readouterr().out == ("called Table.currentRow\n"
                                           "called Table.currentColumn\n"
                                           "called Results.meld with args ('xxx',"
                                           " 'Select a result first')\n")


    def test_remember_settings(self, monkeypatch, capsys):
        """unittest for ResultsGui.remember_settings
        """
        def mock_write():
            print('called MainFrame.write_to_ini')
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.master.parent = types.SimpleNamespace(outopts={}, write_to_ini=mock_write)
        testobj.get_pth = lambda: 'path'
        testobj.get_csv = lambda: 'csv'
        testobj.get_sum = lambda: 'summ'
        testobj.remember_settings()
        assert testobj.master.parent.outopts == {'full_path': 'path', 'as_csv': 'csv',
                                                 'summarize': 'summ'}
        assert capsys.readouterr().out == "called MainFrame.write_to_ini\n"

    def test_klaar(self, monkeypatch, capsys):
        """unittest for ResultsGui.klaar
        """
        monkeypatch.setattr(testee.qtw.QDialog, 'done', mockqtw.MockDialog.done)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.klaar()
        assert capsys.readouterr().out == "called Dialog.done with arg `0`\n"


class TestMainFrameGui:
    """unittest for gui_qt.MainFrameGui
    """
    def setup_testobj(self, monkeypatch, capsys):
        """stub for gui_qt.MainFrameGui object

        create the object skipping the normal initialization
        intercept messages during creation
        return the object so that other methods can be monkeypatched in the caller
        """
        def mock_init(self, *args):
            """stub
            """
            print('called MainFrameGui.__init__ with args', args)
        monkeypatch.setattr(testee.MainFrameGui, '__init__', mock_init)
        testobj = testee.MainFrameGui()
        testobj.master = MockMain()
        assert capsys.readouterr().out == ('called MainFrameGui.__init__ with args ()\n'
                                           'called MainFrame.__init__\n'
                                           'called MainFrameGui.__init__\n')
        return testobj

    def test_init(self, monkeypatch, capsys):
        """unittest for MainFrameGui.__init__
        """
        monkeypatch.setattr(testee.qtw, 'QApplication', mockqtw.MockApplication)
        monkeypatch.setattr(testee.qtw.QWidget, '__init__', mockqtw.MockWidget.__init__)
        monkeypatch.setattr(testee.qtw.QWidget, 'setWindowTitle', mockqtw.MockWidget.setWindowTitle)
        monkeypatch.setattr(testee.qtw.QWidget, 'setWindowIcon', mockqtw.MockWidget.setWindowIcon)
        monkeypatch.setattr(testee.gui, 'QIcon', mockqtw.MockIcon)
        master = MockMain()
        master.title = 'title'
        master.iconame = 'icon'
        testobj = testee.MainFrameGui(master)
        assert capsys.readouterr().out == ("called MainFrame.__init__\n"
                                           "called MainFrameGui.__init__\n"
                                           "called Application.__init__\n"
                                           "called Widget.__init__\n"
                                           "called Widget.setWindowTitle with arg `title`\n"
                                           "called Icon.__init__ with arg `icon`\n"
                                           "called Widget.setWindowIcon\n")

    def test_setup_screen(self, monkeypatch, capsys, expected_output):
        """unittest for MainFrameGui.setup_screen
        """
        def mock_check(*args, **kwargs):
            print('called MainGui.add_checkbox_row with args', args, kwargs)
            return mockqtw.MockCheckBox()
        def mock_combo(*args, **kwargs):
            print('called MainGui.add_combobox_row with args', args, kwargs)
            return mockqtw.MockComboBox()
        monkeypatch.setattr(testee.qtw, 'QGridLayout', mockqtw.MockGridLayout)
        monkeypatch.setattr(testee.qtw, 'QVBoxLayout', mockqtw.MockVBoxLayout)
        monkeypatch.setattr(testee.qtw, 'QHBoxLayout', mockqtw.MockHBoxLayout)
        monkeypatch.setattr(testee.qtw, 'QLabel', mockqtw.MockLabel)
        monkeypatch.setattr(testee.qtw, 'QSpinBox', mockqtw.MockSpinBox)
        monkeypatch.setattr(testee.qtw, 'QListWidget', mockqtw.MockListBox)
        monkeypatch.setattr(testee.qtw, 'QPushButton', mockqtw.MockPushButton)
        monkeypatch.setattr(mockqtw.MockComboBox, 'editTextChanged', {str: mockqtw.MockSignal()})
        monkeypatch.setattr(testee.qtw.QWidget, 'setLayout', mockqtw.MockWidget.setLayout)
        assert capsys.readouterr().out == "called Signal.__init__\n"
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.add_combobox_row = mock_combo
        testobj.add_checkbox_row = mock_check
        testobj.master.always_replace = lambda: 'replace'
        testobj.master.maak_backups = lambda: 'backup'
        testobj.master.exit_when_ready = lambda: 'exit'
        testobj.master.doe = lambda: 'doe'
        testobj.zoekdir = lambda: 'zoekdir'
        testobj.zoek = lambda: 'zoek'
        testobj.check_loc = lambda: 'check'
        testobj.close = lambda: 'close'
        testobj.master.apptype = 'open'
        testobj.master.mru_items = {'zoek': ['x', 'x', 'x'], 'verv': ['y', 'y', 'y'],
                                    'dirs': ['a', 'b'], 'types': ['1', '2']}
        testobj.master.p = {'zoek': 'xxx', 'regex': 'aaa', 'case': 'bbb', 'woord': 'ccc',
                            'verv': 'yyy', 'filelist': [], 'subdirs': True,
                            'extlist': ['x1', 'x2'], 'context': 'ctx', 'negeer': 'neg'}
        testobj.master.extraopts = {'regex': 'rex', 'case': 'case', 'woord': 'word',
                                    'follow_symlinks': 'f_s', 'select_subdirs': 's_s',
                                    'select_files': 's_f'}
        captions = {'vraag_zoek': 'zk', 'regex': 'rg', 'case': 'cs', 'woord': 'wrd',
                    'vraag_verv': 'verv', 'empty': 'emp', 'backup': 'bak', 'exit': 'ex',
                    'zoek': 'zk', 'in': 'in', 'in_s': 'ins',
                    'in_m': 'inm', 'subs_m': 'subm',
                    'subs': 'subs', 'link': 'lnk', 'skipdirs': 'skpd',
                    'skipfiles': 'skpf',
                    'ftypes': 'ft', 'context': 'ctx', 'negeer': 'ign', 'exec': 'ex',
                    'end': 'end'}
        testobj.setup_screen(captions)
        assert isinstance(testobj.grid, testee.qtw.QGridLayout)
        assert testobj.row == 0  # wordt opgehoogd in subroutine
        assert isinstance(testobj.vraag_zoek, mockqtw.MockComboBox)
        assert isinstance(testobj.vraag_regex, mockqtw.MockCheckBox)
        assert isinstance(testobj.vraag_case, mockqtw.MockCheckBox)
        assert isinstance(testobj.vraag_woord, mockqtw.MockCheckBox)
        assert isinstance(testobj.vraag_verv, mockqtw.MockComboBox)
        assert isinstance(testobj.vraag_leeg, mockqtw.MockCheckBox)
        assert isinstance(testobj.vraag_backup, mockqtw.MockCheckBox)
        assert isinstance(testobj.vraag_exit, mockqtw.MockCheckBox)
        assert isinstance(testobj.zoek, testee.qtw.QPushButton)
        assert isinstance(testobj.vraag_dir, mockqtw.MockComboBox)
        assert isinstance(testobj.vraag_subs, mockqtw.MockCheckBox)
        assert isinstance(testobj.vraag_diepte, testee.qtw.QSpinBox)
        assert isinstance(testobj.vraag_links, mockqtw.MockCheckBox)
        assert isinstance(testobj.ask_skipdirs, mockqtw.MockCheckBox)
        assert isinstance(testobj.ask_skipfiles, mockqtw.MockCheckBox)
        assert isinstance(testobj.vraag_types, mockqtw.MockComboBox)
        assert isinstance(testobj.vraag_context, mockqtw.MockCheckBox)
        assert isinstance(testobj.vraag_uitsluit, mockqtw.MockCheckBox)
        assert isinstance(testobj.b_doit, testee.qtw.QPushButton)
        assert isinstance(testobj.b_cancel, testee.qtw.QPushButton)
        assert capsys.readouterr().out == expected_output['base'].format(
                testobj=testobj,
                zoektxt="\ncalled ComboBox.setEditText with arg `xxx`",
                vervtxt="\ncalled ComboBox.setEditText with arg `yyy`",
                exttext="\ncalled ComboBox.setEditText with arg `['x1', 'x2']`")
        testobj.master.apptype = 'single-file'
        testobj.master.p['zoek'] = []
        testobj.master.p['verv'] = []
        testobj.master.p['extlist'] = []
        testobj.master.p['filelist'] = ['qqq']
        testobj.setup_screen(captions)
        assert isinstance(testobj.grid, testee.qtw.QGridLayout)
        assert testobj.row == 1
        assert isinstance(testobj.vraag_zoek, mockqtw.MockComboBox)
        assert isinstance(testobj.vraag_regex, mockqtw.MockCheckBox)
        assert isinstance(testobj.vraag_case, mockqtw.MockCheckBox)
        assert isinstance(testobj.vraag_woord, mockqtw.MockCheckBox)
        assert isinstance(testobj.vraag_verv, mockqtw.MockComboBox)
        assert isinstance(testobj.vraag_leeg, mockqtw.MockCheckBox)
        assert isinstance(testobj.vraag_backup, mockqtw.MockCheckBox)
        assert isinstance(testobj.vraag_exit, mockqtw.MockCheckBox)
        assert isinstance(testobj.vraag_context, mockqtw.MockCheckBox)
        assert isinstance(testobj.vraag_uitsluit, mockqtw.MockCheckBox)
        assert isinstance(testobj.b_doit, testee.qtw.QPushButton)
        assert isinstance(testobj.b_cancel, testee.qtw.QPushButton)
        assert capsys.readouterr().out == expected_output['file'].format(
                testobj=testobj,
                zoektxt="",
                vervtxt="",
                exttext="")
        testobj.master.apptype = 'single-dir'
        testobj.setup_screen(captions)
        assert isinstance(testobj.grid, testee.qtw.QGridLayout)
        assert testobj.row == 1
        assert isinstance(testobj.vraag_zoek, mockqtw.MockComboBox)
        assert isinstance(testobj.vraag_regex, mockqtw.MockCheckBox)
        assert isinstance(testobj.vraag_case, mockqtw.MockCheckBox)
        assert isinstance(testobj.vraag_woord, mockqtw.MockCheckBox)
        assert isinstance(testobj.vraag_verv, mockqtw.MockComboBox)
        assert isinstance(testobj.vraag_leeg, mockqtw.MockCheckBox)
        assert isinstance(testobj.vraag_backup, mockqtw.MockCheckBox)
        assert isinstance(testobj.vraag_exit, mockqtw.MockCheckBox)
        assert isinstance(testobj.vraag_subs, mockqtw.MockCheckBox)
        assert isinstance(testobj.vraag_diepte, testee.qtw.QSpinBox)
        assert isinstance(testobj.vraag_links, mockqtw.MockCheckBox)
        assert isinstance(testobj.ask_skipdirs, mockqtw.MockCheckBox)
        assert isinstance(testobj.ask_skipfiles, mockqtw.MockCheckBox)
        assert isinstance(testobj.vraag_types, mockqtw.MockComboBox)
        assert isinstance(testobj.vraag_context, mockqtw.MockCheckBox)
        assert isinstance(testobj.vraag_uitsluit, mockqtw.MockCheckBox)
        assert isinstance(testobj.b_doit, testee.qtw.QPushButton)
        assert isinstance(testobj.b_cancel, testee.qtw.QPushButton)
        assert capsys.readouterr().out == expected_output['dir'].format(
                testobj=testobj,
                zoektxt="",
                vervtxt="",
                exttext="")
        testobj.master.apptype = 'multi'
        testobj.setup_screen(captions)
        assert isinstance(testobj.grid, testee.qtw.QGridLayout)
        assert testobj.row == 2
        assert isinstance(testobj.vraag_zoek, mockqtw.MockComboBox)
        assert isinstance(testobj.vraag_regex, mockqtw.MockCheckBox)
        assert isinstance(testobj.vraag_case, mockqtw.MockCheckBox)
        assert isinstance(testobj.vraag_woord, mockqtw.MockCheckBox)
        assert isinstance(testobj.vraag_verv, mockqtw.MockComboBox)
        assert isinstance(testobj.vraag_leeg, mockqtw.MockCheckBox)
        assert isinstance(testobj.vraag_backup, mockqtw.MockCheckBox)
        assert isinstance(testobj.vraag_exit, mockqtw.MockCheckBox)
        assert isinstance(testobj.lb, testee.qtw.QListWidget)
        assert isinstance(testobj.vraag_subs, mockqtw.MockCheckBox)
        assert isinstance(testobj.vraag_diepte, testee.qtw.QSpinBox)
        assert isinstance(testobj.vraag_links, mockqtw.MockCheckBox)
        assert isinstance(testobj.ask_skipdirs, mockqtw.MockCheckBox)
        assert isinstance(testobj.ask_skipfiles, mockqtw.MockCheckBox)
        assert isinstance(testobj.vraag_types, mockqtw.MockComboBox)
        assert isinstance(testobj.vraag_context, mockqtw.MockCheckBox)
        assert isinstance(testobj.vraag_uitsluit, mockqtw.MockCheckBox)
        assert isinstance(testobj.b_doit, testee.qtw.QPushButton)
        assert isinstance(testobj.b_cancel, testee.qtw.QPushButton)
        assert capsys.readouterr().out == expected_output['multi'].format(
                testobj=testobj,
                zoektxt="",
                vervtxt="",
                exttext="")

    def test_get_searchtext(self, monkeypatch, capsys):
        """unittest for MainFrameGui.get_searchtext
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.vraag_zoek = mockqtw.MockComboBox()
        assert capsys.readouterr().out == "called ComboBox.__init__\n"
        assert testobj.get_searchtext() == "current text"
        assert capsys.readouterr().out == ("called ComboBox.currentText\n")

    def test_get_replace_args(self, monkeypatch, capsys):
        """unittest for MainFrameGui.get_replace_args
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.vraag_verv = mockqtw.MockComboBox()
        testobj.vraag_leeg = mockqtw.MockCheckBox()
        assert capsys.readouterr().out == "called ComboBox.__init__\ncalled CheckBox.__init__\n"
        assert testobj.get_replace_args() == ('current text', False)
        assert capsys.readouterr().out == ("called ComboBox.currentText\n"
                                           "called CheckBox.isChecked\n")

    def test_get_search_attr(self, monkeypatch, capsys):
        """unittest for MainFrameGui.get_search_attr
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.vraag_regex = mockqtw.MockCheckBox()
        testobj.vraag_case = mockqtw.MockCheckBox()
        testobj.vraag_woord = mockqtw.MockCheckBox()
        assert capsys.readouterr().out == ("called CheckBox.__init__\ncalled CheckBox.__init__\n"
                                           "called CheckBox.__init__\n")
        assert testobj.get_search_attr() == (False, False, False)
        assert capsys.readouterr().out == ("called CheckBox.isChecked\n"
                                           "called CheckBox.isChecked\n"
                                           "called CheckBox.isChecked\n")

    def test_get_types_to_search(self, monkeypatch, capsys):
        """unittest for MainFrameGui.get_types_to_search
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.vraag_types = mockqtw.MockComboBox()
        assert capsys.readouterr().out == "called ComboBox.__init__\n"
        assert testobj.get_types_to_search() == "current text"
        assert capsys.readouterr().out == "called ComboBox.currentText\n"

    def test_get_dir_to_search(self, monkeypatch, capsys):
        """unittest for MainFrameGui.get_dir_to_search
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.vraag_dir = mockqtw.MockComboBox()
        assert capsys.readouterr().out == "called ComboBox.__init__\n"
        assert testobj.get_dir_to_search() == "current text"
        assert capsys.readouterr().out == ("called ComboBox.currentText\n")

    def test_get_subdirs_to_search(self, monkeypatch, capsys):
        """unittest for MainFrameGui.get_subdirs_to_search
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.vraag_subs = mockqtw.MockCheckBox()
        testobj.vraag_links = mockqtw.MockCheckBox()
        testobj.vraag_diepte = mockqtw.MockSpinBox()
        assert capsys.readouterr().out == ("called CheckBox.__init__\ncalled CheckBox.__init__\n"
                                           "called SpinBox.__init__\n")
        assert testobj.get_subdirs_to_search() == (False, False, 0)
        assert capsys.readouterr().out == ("called CheckBox.isChecked\n"
                                           "called CheckBox.isChecked\n"
                                           "called SpinBox.value\n")

    def test_get_backup(self, monkeypatch, capsys):
        """unittest for MainFrameGui.get_backup
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.vraag_backup = mockqtw.MockCheckBox()
        assert capsys.readouterr().out == "called CheckBox.__init__\n"
        assert not testobj.get_backup()
        assert capsys.readouterr().out == "called CheckBox.isChecked\n"

    def test_get_ignore(self, monkeypatch, capsys):
        """unittest for MainFrameGui.get_ignore
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.vraag_uitsluit = mockqtw.MockCheckBox()
        assert capsys.readouterr().out == "called CheckBox.__init__\n"
        assert not testobj.get_ignore()
        assert capsys.readouterr().out == "called CheckBox.isChecked\n"

    def test_get_context(self, monkeypatch, capsys):
        """unittest for MainFrameGui.get_context
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.vraag_context = mockqtw.MockCheckBox()
        assert capsys.readouterr().out == "called CheckBox.__init__\n"
        assert not testobj.get_context()
        assert capsys.readouterr().out == "called CheckBox.isChecked\n"

    def test_error(self, monkeypatch, capsys):
        """unittest for MainFrameGui.error
        """
        monkeypatch.setattr(testee.qtw.QMessageBox, 'critical', mockqtw.MockMessageBox.critical)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.error('titel', 'message')
        assert capsys.readouterr().out == (
                f"called MessageBox.critical with args `{testobj}` `titel` `message`\n")

    def test_meld(self, monkeypatch, capsys):
        """unittest for MainFrameGui.meld
        """
        monkeypatch.setattr(testee.qtw, 'QMessageBox', mockqtw.MockMessageBox)
        # monkeypatch.setattr(testee.qtw.QMessageBox, 'critical', mockqtw.MockMessageBox.critical)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.meld('titel', 'message')
        assert capsys.readouterr().out == (
                f"called MessageBox.information with args `{testobj}` `titel` `message`\n")
        testobj.meld('titel', 'message', additional='xxx')
        assert capsys.readouterr().out == (
                "called MessageBox.__init__ with args"
                f" (2, 'titel', 'message', 1) {{'parent': {testobj}}}\n"
                "called MessageBox.setDetailedText with arg `x\nx\nx`\n"
                "called MessageBox.exec\ncalled MessageBox.close\n")

    def test_add_item_to_searchlist(self, monkeypatch, capsys):
        """unittest for MainFrameGui.add_item_to_searchlist
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.vraag_zoek = mockqtw.MockComboBox()
        assert capsys.readouterr().out == "called ComboBox.__init__\n"
        testobj.add_item_to_searchlist('item')
        assert capsys.readouterr().out == ("called ComboBox.insertItem with args (0, item)\n")

    def test_get_skipdirs(self, monkeypatch, capsys):
        """unittest for MainFrameGui.get_skipdirs
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.ask_skipdirs = mockqtw.MockCheckBox()
        assert capsys.readouterr().out == "called CheckBox.__init__\n"
        assert not testobj.get_skipdirs()
        assert capsys.readouterr().out == "called CheckBox.isChecked\n"

    def test_get_skipfiles(self, monkeypatch, capsys):
        """unittest for MainFrameGui.get_skipfiles
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.ask_skipfiles = mockqtw.MockCheckBox()
        assert capsys.readouterr().out == "called CheckBox.__init__\n"
        assert not testobj.get_skipfiles()
        assert capsys.readouterr().out == "called CheckBox.isChecked\n"

    def test_set_waitcursor(self, monkeypatch, capsys):
        """unittest for MainFrameGui.set_waitcursor
        """
        monkeypatch.setattr(testee.gui, 'QCursor', mockqtw.MockCursor)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.app = mockqtw.MockApplication()
        assert capsys.readouterr().out == "called Application.__init__\n"
        testobj.set_waitcursor(False)
        assert capsys.readouterr().out == "called Application.restoreOverrideCursor\n"
        testobj.set_waitcursor(True)
        assert capsys.readouterr().out == (
                "called Cursor.__init__ with arg CursorShape.WaitCursor\n"
                "called Application.setOverrideCursor with arg MockCursor\n")

    def test_get_exit(self, monkeypatch, capsys):
        """unittest for MainFrameGui.get_exit
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.vraag_exit = mockqtw.MockCheckBox()
        assert capsys.readouterr().out == "called CheckBox.__init__\n"
        testobj.get_exit()
        assert capsys.readouterr().out == "called CheckBox.isChecked\n"

    def test_go(self, monkeypatch, capsys):
        """unittest for MainFrameGui.go
        """
        def mock_show():
            print('called MainGui.show')
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.app = mockqtw.MockApplication()
        testobj.show = mock_show
        with pytest.raises(SystemExit):
            testobj.go()
        assert capsys.readouterr().out == ("called Application.__init__\n"
                                           "called MainGui.show\n"
                                           "called Application.exec\n")

    def test_einde(self, monkeypatch, capsys):
        """unittest for MainFrameGui.einde
        """
        def mock_close():
            print('called MainGui.close')
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.close = mock_close
        testobj.einde()
        assert capsys.readouterr().out == ("called MainGui.close\n")

    def test_add_combobox_row(self, monkeypatch, capsys):
        """unittest for MainFrameGui.add_combobox_row
        """
        monkeypatch.setattr(testee.qtw, 'QComboBox', mockqtw.MockComboBox)
        monkeypatch.setattr(testee.qtw, 'QLabel', mockqtw.MockLabel)
        monkeypatch.setattr(testee.qtw, 'QHBoxLayout', mockqtw.MockHBoxLayout)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.row = 0
        testobj.grid = mockqtw.MockGridLayout()
        assert capsys.readouterr().out == "called Grid.__init__\n"
        result = testobj.add_combobox_row('labeltext', ['item', 'list'])
        assert isinstance(result, testee.qtw.QComboBox)
        assert testobj.row == 1
        assert capsys.readouterr().out == (
                "called Label.__init__ with args ('labeltext',)\n"
                "called Grid.addWidget with arg MockLabel at (1, 0)\n"
                "called ComboBox.__init__\n"
                "called ComboBox.setMaximumWidth with arg `200`\n"
                "called ComboBox.setMinimumWidth with arg `200`\n"
                "called ComboBox.insertItems with args (0, ['item', 'list'])\n"
                "called ComboBox.setEditable with arg `True`\n"
                "called ComboBox.clearEditText\n"
                "called Grid.addWidget with arg MockComboBox at (1, 1)\n")
        testobj.row = 0
        result = testobj.add_combobox_row('labeltext', ['item', 'list'], initial='xx',
                                          button='yy')
        assert isinstance(result, testee.qtw.QComboBox)
        assert testobj.row == 1
        assert capsys.readouterr().out == (
                "called Label.__init__ with args ('labeltext',)\n"
                "called Grid.addWidget with arg MockLabel at (1, 0)\n"
                "called ComboBox.__init__\n"
                "called ComboBox.setMaximumWidth with arg `200`\n"
                "called ComboBox.setMinimumWidth with arg `200`\n"
                "called ComboBox.insertItems with args (0, ['item', 'list'])\n"
                "called ComboBox.setEditable with arg `True`\n"
                "called ComboBox.clearEditText\n"
                "called ComboBox.setEditText with arg `xx`\n"
                "called HBox.__init__\n"
                "called HBox.addWidget with arg MockComboBox\n"
                "called HBox.addWidget with arg str\n"
                "called HBox.addStretch\n"
                "called Grid.addLayout with arg MockHBoxLayout at (1, 1)\n")

    def test_add_checkbox_row(self, monkeypatch, capsys):
        """unittest for MainFrameGui.add_checkbox_row
        """
        monkeypatch.setattr(testee.qtw, 'QCheckBox', mockqtw.MockCheckBox)
        monkeypatch.setattr(testee.qtw, 'QHBoxLayout', mockqtw.MockHBoxLayout)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.row = 0
        testobj.grid = mockqtw.MockGridLayout()
        assert capsys.readouterr().out == "called Grid.__init__\n"
        result = testobj.add_checkbox_row('text')
        assert isinstance(result, testee.qtw.QCheckBox)
        assert testobj.row == 1
        assert capsys.readouterr().out == (
                "called CheckBox.__init__ with text 'text'\n"
                "called Grid.addWidget with arg MockCheckBox at (1, 1)\n")
        testobj.row = 0
        result = testobj.add_checkbox_row('text', toggler='toggle', spinner='spin', indent=4)
        assert isinstance(result, testee.qtw.QCheckBox)
        assert testobj.row == 1
        assert capsys.readouterr().out == (
                "called CheckBox.__init__ with text 'text'\n"
                "called CheckBox.toggle\n"
                "called HBox.__init__\n"
                "called HBox.addWidget with arg MockCheckBox\n"
                "called HBox.addWidget with arg str\n"
                "called HBox.addStretch\n"
                "called Grid.addLayout with arg MockHBoxLayout at (1, 1)\n")
        testobj.row = 0
        result = testobj.add_checkbox_row('text', toggler='toggle', indent=4)
        assert isinstance(result, testee.qtw.QCheckBox)
        assert testobj.row == 1
        assert capsys.readouterr().out == (
                "called CheckBox.__init__ with text 'text'\n"
                "called CheckBox.toggle\n"
                "called HBox.__init__\n"
                "called HBox.addSpacing\n"
                "called HBox.addWidget with arg MockCheckBox\n"
                "called HBox.addStretch\n"
                "called Grid.addLayout with arg MockHBoxLayout at (1, 1)\n")

    def test_check_case(self, monkeypatch, capsys):
        """unittest for MainFrameGui.check_case
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.vraag_zoek = mockqtw.MockComboBox()
        assert capsys.readouterr().out == "called ComboBox.__init__\n"
        testobj.check_case(testee.core.Qt.CheckState.Unchecked)
        assert capsys.readouterr().out == ("called ComboBox.setAutoCompletionCaseSensitivity"
                                           " with arg CaseSensitivity.CaseInsensitive\n")
        testobj.check_case(testee.core.Qt.CheckState.Checked)
        assert capsys.readouterr().out == ("called ComboBox.setAutoCompletionCaseSensitivity"
                                           " with arg CaseSensitivity.CaseSensitive\n")

    def test_check_loc(self, monkeypatch, capsys, tmp_path):
        """unittest for MainFrameGui.check_loc
        """
        def mock_read(arg):
            print(f'called MainWindow.read_from_ini with arg {arg}')
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.master.read_from_ini = mock_read
        testobj.master.mru_items = {'zoek': ['x', 'xx'], 'verv': ['y', 'yy'], 'types': ['z', 'zz']}
        testobj.master.p = {'case': True, 'woord': False, 'subdirs': True, 'context': False}
        testobj.vraag_zoek = mockqtw.MockComboBox()
        testobj.vraag_verv = mockqtw.MockComboBox()
        testobj.vraag_types = mockqtw.MockComboBox()
        testobj.vraag_case = mockqtw.MockCheckBox()
        testobj.vraag_woord = mockqtw.MockCheckBox()
        testobj.vraag_subs = mockqtw.MockCheckBox()
        testobj.vraag_context = mockqtw.MockCheckBox()
        assert capsys.readouterr().out == ("called ComboBox.__init__\ncalled ComboBox.__init__\n"
                                           "called ComboBox.__init__\ncalled CheckBox.__init__\n"
                                           "called CheckBox.__init__\ncalled CheckBox.__init__\n"
                                           "called CheckBox.__init__\n")
        testfile = tmp_path / 'testfile'
        txt = str(testfile)
        testobj.check_loc(txt)
        assert capsys.readouterr().out == ""
        testfile.touch()
        testobj.check_loc(txt)
        assert capsys.readouterr().out == (
                f"called MainWindow.read_from_ini with arg {testfile}\n"
                "called ComboBox.clear\n"
                "called ComboBox.addItems with arg ['x', 'xx']\n"
                "called ComboBox.clear\n"
                "called ComboBox.addItems with arg ['y', 'yy']\n"
                "called ComboBox.clear\n"
                "called ComboBox.addItems with arg ['z', 'zz']\n"
                "called CheckBox.setChecked with arg True\n"
                "called CheckBox.setChecked with arg False\n"
                "called CheckBox.setChecked with arg True\n"
                "called CheckBox.setChecked with arg False\n")
        testfile.unlink()
        testfile.mkdir()
        txt = str(testfile) + '/'
        testobj.check_loc(txt)
        assert capsys.readouterr().out == ""

    def test_keyPressEvent(self, monkeypatch, capsys):
        """unittest for MainFrameGui.keyPressEvent
        """
        def mock_close():
            print('called MainGui.close')
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.close = mock_close
        event = mockqtw.MockEvent(key=None)
        testobj.keyPressEvent(event)
        assert capsys.readouterr().out == ""
        event = mockqtw.MockEvent(key=testee.core.Qt.Key.Key_Escape)
        testobj.keyPressEvent(event)
        assert capsys.readouterr().out == "called MainGui.close\n"

    def test_zoekdir(self, monkeypatch, capsys):
        """unittest for MainFrameGui.zoekdir
        """
        def mock_get(*args, **kwargs):
            print('called FileDialog.getExistingDirectory with args', args, kwargs)
            return 'xxx'
        monkeypatch.setattr(testee.qtw.QFileDialog, 'getExistingDirectory',
                            mockqtw.MockFileDialog.getExistingDirectory)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.vraag_dir = mockqtw.MockComboBox()
        assert capsys.readouterr().out == "called ComboBox.__init__\n"
        testobj.zoekdir()
        assert capsys.readouterr().out == (
                "called ComboBox.currentText\n"
                "called FileDialog.getExistingDirectory with args"
                f" {testobj} ('Choose a directory:', 'current text') {{}}\n")
        monkeypatch.setattr(testee.qtw.QFileDialog, 'getExistingDirectory', mock_get)
        testobj.zoekdir()
        assert capsys.readouterr().out == (
                "called ComboBox.currentText\n"
                "called FileDialog.getExistingDirectory with args"
                f" ({testobj}, 'Choose a directory:', 'current text') {{}}\n"
                "called ComboBox.setEditText with arg `xxx`\n")
