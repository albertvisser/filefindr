"""unittests for ./afrift/gui_qt.py
"""
import types
import pytest
from afrift import gui_qt as testee
from mockgui import mockqtwidgets as mockqtw
class MockSelect:
    "stub for main.SelectNames objeect"
    def __init__(self):
        print('called Selectnames.__init__')


class MockResults:
    "stub for main.Results objeect"
    def __init__(self):
        print('called Results.__init__')


class MockAfrift:
    "stub for main.Afrift objeect"
    def __init__(self):
        print('called Afrift.__init__')
        self.gui = MockAfriftGui()


class MockAfriftGui:
    "stub for gui.AfriftGui object"
    def __init__(self):
        print('called AfriftGui.__init__')


class TestAfriftGui:
    """unittest for gui_qt.AfriftGui
    """
    def setup_testobj(self, monkeypatch, capsys):
        """stub for gui_qt.AfriftGui object

        create the object skipping the normal initialization
        intercept messages during creation
        return the object so that other methods can be monkeypatched in the caller
        """
        def mock_init(self, *args):
            """stub
            """
            print('called AfriftGui.__init__ with args', args)
        monkeypatch.setattr(testee.AfriftGui, '__init__', mock_init)
        testobj = testee.AfriftGui()
        testobj.master = MockAfrift()
        assert capsys.readouterr().out == ('called AfriftGui.__init__ with args ()\n'
                                           'called Afrift.__init__\n'
                                           'called AfriftGui.__init__\n')
        return testobj

    def test_init(self, monkeypatch, capsys):
        """unittest for AfriftGui.__init__
        """
        monkeypatch.setattr(testee.qtw, 'QApplication', mockqtw.MockApplication)
        monkeypatch.setattr(testee.qtw.QWidget, '__init__', mockqtw.MockWidget.__init__)
        monkeypatch.setattr(testee.qtw.QWidget, 'setWindowTitle', mockqtw.MockWidget.setWindowTitle)
        monkeypatch.setattr(testee.qtw.QWidget, 'setWindowIcon', mockqtw.MockWidget.setWindowIcon)
        monkeypatch.setattr(testee.gui, 'QIcon', mockqtw.MockIcon)
        master = MockAfrift()
        master.title = 'title'
        master.iconame = 'icon'
        testobj = testee.AfriftGui(master)
        assert capsys.readouterr().out == ("called Afrift.__init__\n"
                                           "called AfriftGui.__init__\n"
                                           "called Application.__init__\n"
                                           "called Widget.__init__\n"
                                           "called Widget.setWindowTitle with arg `title`\n"
                                           "called Icon.__init__ with arg `icon`\n"
                                           "called Widget.setWindowIcon\n")

    def test_init_screen(self, monkeypatch, capsys):
        """unittest for AfriftGui.init_screen
        """
        monkeypatch.setattr(testee.qtw, 'QGridLayout', mockqtw.MockGridLayout)
        monkeypatch.setattr(testee.qtw, 'QVBoxLayout', mockqtw.MockVBoxLayout)
        monkeypatch.setattr(testee.qtw.QWidget, 'setLayout', mockqtw.MockWidget.setLayout)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.init_screen()
        assert testobj.row == -1
        assert isinstance(testobj.grid, testee.qtw.QGridLayout)
        assert capsys.readouterr().out == ("called Grid.__init__\n"
                                           "called VBox.__init__\n"
                                           "called VBox.addLayout with arg MockGridLayout\n"
                                           "called Widget.setLayout with arg MockVBoxLayout\n")

    def test_add_combobox_row(self, monkeypatch, capsys):
        """unittest for AfriftGui.add_combobox_row
        """
        def callback1():
            "dummy callback for reference"
        def callback2():
            "dummy callback for reference"
        monkeypatch.setattr(testee.qtw, 'QHBoxLayout', mockqtw.MockHBoxLayout)
        monkeypatch.setattr(testee.qtw, 'QLabel', mockqtw.MockLabel)
        monkeypatch.setattr(testee.qtw, 'QComboBox', mockqtw.MockComboBox)
        monkeypatch.setattr(testee.qtw, 'QPushButton', mockqtw.MockPushButton)
        monkeypatch.setattr(mockqtw.MockComboBox, 'editTextChanged', {str: mockqtw.MockSignal()})
        assert capsys.readouterr().out == "called Signal.__init__\n"
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
                                          button=('btn', callback1), callback=callback2,
                                          completer='case')
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
                f"called PushButton.__init__ with args ('btn', {testobj}) {{}}\n"
                f"called Signal.connect with args ({callback1},)\n"
                "called HBox.__init__\n"
                "called HBox.addWidget with arg MockComboBox\n"
                "called HBox.addWidget with arg MockPushButton\n"
                "called HBox.addStretch\n"
                "called Grid.addLayout with arg MockHBoxLayout at (1, 1)\n"
                "called ComboBox.completer\n"
                "called Completer.setCaseSensitivity with arg CaseSensitivity.CaseSensitive\n"
                f"called Signal.connect with args ({callback2},)\n")
        testobj.row = 0
        result = testobj.add_combobox_row('labeltext', ['item', 'list'], completer='off')
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
                "called Grid.addWidget with arg MockComboBox at (1, 1)\n"
                "called ComboBox.setCompleter with arg None\n")

    def test_add_checkbox_row(self, monkeypatch, capsys):
        """unittest for AfriftGui.add_checkbox_row
        """
        monkeypatch.setattr(testee.qtw, 'QHBoxLayout', mockqtw.MockHBoxLayout)
        monkeypatch.setattr(testee.qtw, 'QCheckBox', mockqtw.MockCheckBox)
        monkeypatch.setattr(testee.qtw, 'QSpinBox', mockqtw.MockSpinBox)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.row = 0
        testobj.grid = mockqtw.MockGridLayout()
        assert capsys.readouterr().out == "called Grid.__init__\n"
        result = testobj.add_checkbox_row('text')
        assert isinstance(result, testee.qtw.QCheckBox)
        assert testobj.row == 1
        assert capsys.readouterr().out == (
                f"called CheckBox.__init__ with args ('text', {testobj})\n"
                "called Grid.addWidget with arg MockCheckBox at (1, 1)\n")
        testobj.row = 0
        result = testobj.add_checkbox_row('text', toggler='toggle', spinner='spin', indent=4)
        assert isinstance(result[0], testee.qtw.QCheckBox)
        assert isinstance(result[1], testee.qtw.QSpinBox)
        assert testobj.row == 1
        assert capsys.readouterr().out == (
                f"called CheckBox.__init__ with args ('text', {testobj})\n"
                "called CheckBox.toggle\n"
                "called SpinBox.__init__\n"
                "called SpinBox.setValue with arg 's'\n"
                "called SpinBox.setMinimum with arg 'p'\n"
                "called HBox.__init__\n"
                "called HBox.addWidget with arg MockCheckBox\n"
                "called HBox.addWidget with arg MockSpinBox\n"
                "called HBox.addStretch\n"
                "called Grid.addLayout with arg MockHBoxLayout at (1, 1)\n")
        testobj.row = 0
        result = testobj.add_checkbox_row('text', toggler='toggle', indent=4)
        assert isinstance(result, testee.qtw.QCheckBox)
        assert testobj.row == 1
        assert capsys.readouterr().out == (
                f"called CheckBox.__init__ with args ('text', {testobj})\n"
                "called CheckBox.toggle\n"
                "called HBox.__init__\n"
                "called HBox.addSpacing\n"
                "called HBox.addWidget with arg MockCheckBox\n"
                "called HBox.addStretch\n"
                "called Grid.addLayout with arg MockHBoxLayout at (1, 1)\n")
        testobj.row = 0
        result = testobj.add_checkbox_row('letterss', toggler='toggle', indent=4)
        assert isinstance(result, testee.qtw.QCheckBox)
        assert testobj.row == 1
        assert capsys.readouterr().out == (
                f"called CheckBox.__init__ with args ('letterss', {testobj})\n"
                "called CheckBox.toggle\n"
                f"called Signal.connect with args ({testobj.check_casing},)\n"
                "called HBox.__init__\n"
                "called HBox.addSpacing\n"
                "called HBox.addWidget with arg MockCheckBox\n"
                "called HBox.addStretch\n"
                "called Grid.addLayout with arg MockHBoxLayout at (1, 1)\n")

    def test_add_label_to_grid(self, monkeypatch, capsys):
        """unittest for AfriftGui.add_label_to_grid
        """
        monkeypatch.setattr(testee.qtw, 'QHBoxLayout', mockqtw.MockHBoxLayout)
        monkeypatch.setattr(testee.qtw, 'QLabel', mockqtw.MockLabel)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.row = 0
        testobj.grid = mockqtw.MockGridLayout()
        assert capsys.readouterr().out == "called Grid.__init__\n"
        testobj.add_label_to_grid('text', new_row=True)
        assert testobj.row == 1
        assert capsys.readouterr().out == ("called Label.__init__ with args ('text',)\n"
                                           "called Grid.addWidget with arg MockLabel at (1, 0)\n")
        testobj.row = 0
        testobj.add_label_to_grid('text', left_align=True)
        assert testobj.row == 0
        assert capsys.readouterr().out == (
                "called HBox.__init__\n"
                "called Label.__init__ with args ('text',)\n"
                "called HBox.addWidget with arg MockLabel\n"
                "called HBox.addStretch\n"
                "called Grid.addLayout with arg MockHBoxLayout at (0, 1)\n")
        testobj.row = 0
        testobj.add_label_to_grid('text', fullwidth=True)
        assert testobj.row == 1
        assert capsys.readouterr().out == (
                "called Label.__init__ with args ('text',)\n"
                "called Grid.addWidget with arg MockLabel at (1, 0, 1, 2)\n")

    def test_add_listbox_to_grid(self, monkeypatch, capsys):
        """unittest for AfriftGui.add_listbox_to_grid
        """
        monkeypatch.setattr(testee.qtw, 'QListWidget', mockqtw.MockListBox)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.row = 0
        testobj.grid = mockqtw.MockGridLayout()
        assert capsys.readouterr().out == "called Grid.__init__\n"
        testobj.add_listbox_to_grid('text')
        assert capsys.readouterr().out == (
                "called List.__init__\n"
                "called List.insertItems with args (0, text)\n"
                "called Grid.addWidget with arg MockListBox at (1, 0, 1, 2)\n")

    def test_add_buttons(self, monkeypatch, capsys):
        """unittest for AfriftGui.add_buttons
        """
        def callback1():
            "dummy callback for reference"
        def callback2():
            "dummy callback for reference"
        monkeypatch.setattr(testee.qtw, 'QHBoxLayout', mockqtw.MockHBoxLayout)
        monkeypatch.setattr(testee.qtw, 'QPushButton', mockqtw.MockPushButton)
        monkeypatch.setattr(testee.gui, 'QAction', mockqtw.MockAction)
        monkeypatch.setattr(testee.qtw.QWidget, 'addAction', mockqtw.MockWidget.addAction)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.row = 0
        testobj.grid = mockqtw.MockGridLayout()
        assert capsys.readouterr().out == "called Grid.__init__\n"
        testobj.add_buttons((('xxx', callback1, 'aaa'), ('yyy', callback2, 'bbb')))
        assert testobj.row == 1
        assert capsys.readouterr().out == (
                "called HBox.__init__\n"
                "called HBox.addStretch\n"
                f"called PushButton.__init__ with args ('xxx', {testobj}) {{}}\n"
                f"called Signal.connect with args ({callback1},)\n"
                "called HBox.addWidget with arg MockPushButton\n"
                f"called Action.__init__ with args ('xxx', {testobj})\n"
                "called Widget.addAction\n"
                f"called Signal.connect with args ({callback1},)\n"
                "called Action.setShortcut with arg `aaa`\n"
                f"called PushButton.__init__ with args ('yyy', {testobj}) {{}}\n"
                f"called Signal.connect with args ({callback2},)\n"
                "called HBox.addWidget with arg MockPushButton\n"
                f"called Action.__init__ with args ('yyy', {testobj})\n"
                "called Widget.addAction\n"
                f"called Signal.connect with args ({callback2},)\n"
                "called Action.setShortcut with arg `bbb`\n"
                "called HBox.addStretch\n"
                "called Grid.addLayout with arg MockHBoxLayout at (1, 0, 1, 2)\n")
        # testobj.row = 0
        # testobj.add_buttons((), end=True)
        # assert testobj.row == 1
        # assert capsys.readouterr().out == (
        #         "called HBox.__init__\n"
        #         "called HBox.addStretch\n"
        #         "called Grid.addLayout with arg MockHBoxLayout at (1, 0, 1, 2)\n")

    def test_set_focus_to(self, monkeypatch, capsys):
        """unittest for AfriftGui.set_focus_to
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        widget = mockqtw.MockWidget()
        assert capsys.readouterr().out == "called Widget.__init__\n"
        testobj.set_focus_to(widget)
        assert capsys.readouterr().out == "called Widget.setFocus\n"

    def test_get_combobox_value(self, monkeypatch, capsys):
        """unittest for AfriftGui.get_combobox_value
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        cb = mockqtw.MockComboBox()
        assert capsys.readouterr().out == "called ComboBox.__init__\n"
        assert testobj.get_combobox_value(cb) == 'current text'
        assert capsys.readouterr().out == "called ComboBox.currentText\n"

    def test_get_checkbox_value(self, monkeypatch, capsys):
        """unittest for AfriftGui.get_checkbox_value
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        cb = mockqtw.MockCheckBox()
        assert capsys.readouterr().out == "called CheckBox.__init__\n"
        assert not testobj.get_checkbox_value(cb)
        assert capsys.readouterr().out == "called CheckBox.isChecked\n"

    def test_get_spinbox_value(self, monkeypatch, capsys):
        """unittest for AfriftGui.get_spinbox_value
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        sb = mockqtw.MockSpinBox()
        assert capsys.readouterr().out == "called SpinBox.__init__\n"
        assert testobj.get_spinbox_value(sb) == 0
        assert capsys.readouterr().out == "called SpinBox.value\n"

    def test_error(self, monkeypatch, capsys):
        """unittest for AfriftGui.error
        """
        monkeypatch.setattr(testee.qtw.QMessageBox, 'critical', mockqtw.MockMessageBox.critical)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.error('titel', 'message')
        assert capsys.readouterr().out == (
                f"called MessageBox.critical with args `{testobj}` `titel` `message`\n")

    def test_meld(self, monkeypatch, capsys):
        """unittest for AfriftGui.meld
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
        """unittest for AfriftGui.add_item_to_searchlist
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        # testobj.vraag_zoek = mockqtw.MockComboBox()
        combo = mockqtw.MockComboBox()
        assert capsys.readouterr().out == "called ComboBox.__init__\n"
        testobj.add_item_to_searchlist(combo, 'item')
        assert capsys.readouterr().out == ("called ComboBox.insertItem with args (0, item)\n")

    def test_set_waitcursor(self, monkeypatch, capsys):
        """unittest for AfriftGui.set_waitcursor
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

    def test_go(self, monkeypatch, capsys):
        """unittest for AfriftGui.go
        """
        def mock_show():
            print('called AfriftGui.show')
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.app = mockqtw.MockApplication()
        testobj.show = mock_show
        with pytest.raises(SystemExit):
            testobj.go()
        assert capsys.readouterr().out == ("called Application.__init__\n"
                                           "called AfriftGui.show\n"
                                           "called Application.exec\n")

    def test_einde(self, monkeypatch, capsys):
        """unittest for AfriftGui.einde
        """
        def mock_close():
            print('called AfriftGui.close')
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.close = mock_close
        testobj.einde()
        assert capsys.readouterr().out == ("called AfriftGui.close\n")

    def test_check_casing(self, monkeypatch, capsys):
        """unittest for AfriftGui.check_case
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.master.vraag_zoek = mockqtw.MockComboBox()
        assert capsys.readouterr().out == "called ComboBox.__init__\n"
        testobj.check_casing(testee.core.Qt.CheckState.Unchecked)
        assert capsys.readouterr().out == (
                "called ComboBox.completer\n"
                "called Completer.setCaseSensitivity with arg CaseSensitivity.CaseInsensitive\n"
                f"called ComboBox.setCompleter with arg {testobj.master.vraag_zoek.completer()}\n")
        assert capsys.readouterr().out == "called ComboBox.completer\n"
        testobj.check_casing(testee.core.Qt.CheckState.Checked)
        assert capsys.readouterr().out == (
                "called ComboBox.completer\n"
                "called Completer.setCaseSensitivity with arg CaseSensitivity.CaseSensitive\n"
                f"called ComboBox.setCompleter with arg {testobj.master.vraag_zoek.completer()}\n")
        assert capsys.readouterr().out == "called ComboBox.completer\n"

    def test_get_sender_value(self, monkeypatch, capsys):
        """unittest for AfriftGui.get_sender_value
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.get_sender_value('x', 'y') == 'x'

    def test_replace_combobox_items(self, monkeypatch, capsys):
        """unittest for AfriftGui.replace_combobox_items
        """
        cmb = mockqtw.MockComboBox()
        assert capsys.readouterr().out == "called ComboBox.__init__\n"
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.replace_combobox_items(cmb, ['x', 'xx'])
        assert capsys.readouterr().out == (
                "called ComboBox.clear\n"
                "called ComboBox.addItems with arg ['x', 'xx']\n")

    def test_set_checkbox_value(self, monkeypatch, capsys):
        """unittest for AfriftGui.set_checkbox_value
        """
        cb = mockqtw.MockCheckBox()
        assert capsys.readouterr().out == "called CheckBox.__init__\n"
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.set_checkbox_value(cb, True)
        assert capsys.readouterr().out == "called CheckBox.setChecked with arg True\n"

    def test_zoekdir(self, monkeypatch, capsys):
        """unittest for AfriftGui.zoekdir
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
        testobj.parent = MockAfrift()
        testobj.master = MockSelect()
        assert capsys.readouterr().out == ("called SelectNamesGui.__init__ with args ()\n"
                                           "called Afrift.__init__\n"
                                           "called AfriftGui.__init__\n"
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
        parent = MockAfrift()
        master = MockSelect()
        master.title = 'title'
        master.iconame = 'ico'
        testobj = testee.SelectNamesGui(parent, master)
        assert capsys.readouterr().out == ("called Afrift.__init__\n"
                                           "called AfriftGui.__init__\n"
                                           "called Selectnames.__init__\n"
                                           f"called Dialog.__init__ with args {parent.gui} () {{}}\n"
                                           "called Dialog.setWindowTitle with args ('title',)\n"
                                           "called Icon.__init__ with arg `ico`\n"
                                           "called Dialog.setWindowIcon with arg MockIcon\n")

    def test_setup_screen(self, monkeypatch, capsys):
        """unittest for SelectNamesGui.setup_screen
        """
        monkeypatch.setattr(testee.qtw, 'QVBoxLayout', mockqtw.MockVBoxLayout)
        monkeypatch.setattr(testee.qtw.QDialog, 'setLayout', mockqtw.MockDialog.setLayout)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.setup_screen()
        assert isinstance(testobj.vbox, testee.qtw.QVBoxLayout)
        assert capsys.readouterr().out == ("called VBox.__init__\n"
                                           "called Dialog.setLayout with arg MockVBoxLayout\n")

    def test_add_line(self, monkeypatch, capsys):
        """unittest for SelectNamesGui.add_line
        """
        monkeypatch.setattr(testee.qtw, 'QHBoxLayout', mockqtw.MockHBoxLayout)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.vbox = mockqtw.MockVBoxLayout()
        assert capsys.readouterr().out == "called VBox.__init__\n"
        testobj.add_line()
        assert capsys.readouterr().out == ("called HBox.__init__\n"
                                           "called VBox.addLayout with arg MockHBoxLayout\n")

    def test_add_text_to_line(self, monkeypatch, capsys):
        """unittest for SelectNamesGui.add_text_to_line
        """
        monkeypatch.setattr(testee.qtw, 'QLabel', mockqtw.MockLabel)
        testobj = self.setup_testobj(monkeypatch, capsys)
        hbox = mockqtw.MockHBoxLayout()
        assert capsys.readouterr().out == "called HBox.__init__\n"
        testobj.add_text_to_line(hbox, "asdfghj")
        assert capsys.readouterr().out == (
                f"called Label.__init__ with args ('asdfghj', {testobj})\n"
                "called HBox.addWidget with arg MockLabel\n")

    def test_add_checkbox_to_line(self, monkeypatch, capsys):
        """unittest for SelectNamesGui.add_checkbox_to_line
        """
        def callback():
            "empty callback, for reference"
        monkeypatch.setattr(testee.qtw, 'QCheckBox', mockqtw.MockCheckBox)
        testobj = self.setup_testobj(monkeypatch, capsys)
        hbox = mockqtw.MockHBoxLayout()
        assert capsys.readouterr().out == "called HBox.__init__\n"
        testobj.add_checkbox_to_line(hbox, 'check', callback)
        assert capsys.readouterr().out == (
                f"called CheckBox.__init__ with args ('check', {testobj})\n"
                f"called Signal.connect with args ({callback},)\n"
                "called HBox.addSpacing\n"
                "called HBox.addWidget with arg MockCheckBox\n")

    def test_add_button_to_line(self, monkeypatch, capsys):
        """unittest for SelectNamesGui.add_button_to_lines
        """
        def callback():
            "empty callback, for reference"
        monkeypatch.setattr(testee.qtw, 'QPushButton', mockqtw.MockPushButton)
        testobj = self.setup_testobj(monkeypatch, capsys)
        hbox = mockqtw.MockHBoxLayout()
        assert capsys.readouterr().out == "called HBox.__init__\n"
        testobj.add_button_to_line(hbox, 'btn', callback)
        assert capsys.readouterr().out == (
                f"called PushButton.__init__ with args ('btn', {testobj}) {{}}\n"
                f"called Signal.connect with args ({callback},)\n"
                "called HBox.addStretch\n"
                "called HBox.addWidget with arg MockPushButton\n"
                "called HBox.addSpacing\n")

    def test_add_selectionlist(self, monkeypatch, capsys):
        """unittest for SelectNamesGui.add_selectionlist
        """
        monkeypatch.setattr(testee.qtw, 'QFrame', mockqtw.MockFrame)
        monkeypatch.setattr(testee.qtw, 'QVBoxLayout', mockqtw.MockVBoxLayout)
        monkeypatch.setattr(testee.qtw, 'QCheckBox', mockqtw.MockCheckBox)
        monkeypatch.setattr(testee.qtw, 'QHBoxLayout', mockqtw.MockHBoxLayout)
        monkeypatch.setattr(testee.qtw, 'QScrollArea', mockqtw.MockScrollArea)
        testobj = self.setup_testobj(monkeypatch, capsys)
        hbox = mockqtw.MockHBoxLayout()
        assert capsys.readouterr().out == "called HBox.__init__\n"
        testobj.master.do_files = False
        testobj.add_selectionlist(hbox, ['name', 'list'])
        assert capsys.readouterr().out == (
                "called Frame.__init__\n"
                "called VBox.__init__\n"
                f"called CheckBox.__init__ with args ('name', {testobj.frm})\n"
                "called HBox.__init__\n"
                "called HBox.addWidget with arg MockCheckBox\n"
                "called VBox.addLayout with arg MockHBoxLayout\n"
                f"called CheckBox.__init__ with args ('list', {testobj.frm})\n"
                "called HBox.__init__\n"
                "called HBox.addWidget with arg MockCheckBox\n"
                "called VBox.addLayout with arg MockHBoxLayout\n"
                "called Frame.setLayout with arg MockVBoxLayout\n"
                f"called ScrollArea.__init__ with args ({testobj},)\n"
                "called ScrollArea.setWidget with arg `MockFrame`\n"
                "called HBox.addWidget with arg MockScrollArea\n")
        testobj.master.do_files = True
        testobj.add_selectionlist(hbox, [123, 456])
        assert capsys.readouterr().out == (
                "called Frame.__init__\n"
                "called VBox.__init__\n"
                f"called CheckBox.__init__ with args ('123', {testobj.frm})\n"
                "called HBox.__init__\n"
                "called HBox.addWidget with arg MockCheckBox\n"
                "called VBox.addLayout with arg MockHBoxLayout\n"
                f"called CheckBox.__init__ with args ('456', {testobj.frm})\n"
                "called HBox.__init__\n"
                "called HBox.addWidget with arg MockCheckBox\n"
                "called VBox.addLayout with arg MockHBoxLayout\n"
                "called Frame.setLayout with arg MockVBoxLayout\n"
                f"called ScrollArea.__init__ with args ({testobj},)\n"
                "called ScrollArea.setWidget with arg `MockFrame`\n"
                "called HBox.addWidget with arg MockScrollArea\n")

    def test_add_buttons(self, monkeypatch, capsys):
        """unittest for SelectNamesGui.add_buttons
        """
        def callback1():
            "empty callback, for reference"
        def callback2():
            "empty callback, for reference"
        monkeypatch.setattr(testee.qtw, 'QPushButton', mockqtw.MockPushButton)
        testobj = self.setup_testobj(monkeypatch, capsys)
        hbox = mockqtw.MockHBoxLayout()
        assert capsys.readouterr().out == "called HBox.__init__\n"
        testobj.add_buttons(hbox, (('btn1', callback1), ('btn2', callback2)))
        assert capsys.readouterr().out == (
                "called HBox.addStretch\n"
                f"called PushButton.__init__ with args ('btn1', {testobj}) {{}}\n"
                f"called Signal.connect with args ({callback1},)\n"
                "called HBox.addWidget with arg MockPushButton\n"
                f"called PushButton.__init__ with args ('btn2', {testobj}) {{}}\n"
                f"called Signal.connect with args ({callback2},)\n"
                "called HBox.addWidget with arg MockPushButton\n"
                "called HBox.addStretch\n")

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

    def test_cancel(self, monkeypatch, capsys):
        """unittest for SelectNamesGui.cancel
        """
        monkeypatch.setattr(testee.qtw.QDialog, 'reject', mockqtw.MockDialog.reject)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.cancel()
        assert capsys.readouterr().out == "called Dialog.reject\n"

    def test_confirm(self, monkeypatch, capsys):
        """unittest for SelectNamesGui.confirm
        """
        monkeypatch.setattr(testee.qtw.QDialog, 'accept', mockqtw.MockDialog.accept)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.master.do_files = False
        testobj.master.names = {'x': 'xxx', 'w': 'www', 'y': 'yyy'}
        testobj.master.checklist = [mockqtw.MockCheckBox('x'), mockqtw.MockCheckBox('y'),
                                    mockqtw.MockCheckBox('w')]
        testobj.master.checklist[0].setChecked(True)
        testobj.master.checklist[2].setChecked(True)
        assert capsys.readouterr().out == ("called CheckBox.__init__ with args ('x',)\n"
                                           "called CheckBox.__init__ with args ('y',)\n"
                                           "called CheckBox.__init__ with args ('w',)\n"
                                           "called CheckBox.setChecked with arg True\n"
                                           "called CheckBox.setChecked with arg True\n")
        testobj.confirm()
        assert testobj.master.names == ['x', 'w']
        assert capsys.readouterr().out == ("called CheckBox.isChecked\n"
                                           "called CheckBox.text\n"
                                           "called CheckBox.isChecked\n"
                                           "called CheckBox.isChecked\n"
                                           "called CheckBox.text\n"
                                           "called Dialog.accept\n")
        testobj.master.do_files = True
        testobj.master.names = {'x': 'xxx', 'w': 'www', 'y': 'yyy'}
        testobj.master.checklist[2].setChecked(False)
        assert capsys.readouterr().out == "called CheckBox.setChecked with arg False\n"
        testobj.confirm()
        assert testobj.master.names == ['www', 'yyy']
        assert capsys.readouterr().out == ("called CheckBox.isChecked\n"
                                           "called CheckBox.text\n"
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
        testobj.parent = MockAfrift()
        testobj.master = MockResults()
        assert capsys.readouterr().out == ('called ResultsGui.__init__ with args ()\n'
                                           "called Afrift.__init__\n"
                                           "called AfriftGui.__init__\n"
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
        parent = MockAfrift()
        testobj = testee.ResultsGui(parent, master)
        assert testobj.show_result_details
        assert capsys.readouterr().out == ("called Results.__init__\n"
                                           "called Afrift.__init__\n"
                                           "called AfriftGui.__init__\n"
                                           f"called Dialog.__init__ with args {parent.gui} () {{}}\n"
                                           "called Dialog.setWindowTitle with args ('title',)\n"
                                           "called Icon.__init__ with arg `ico`\n"
                                           "called Dialog.setWindowIcon with arg MockIcon\n")

    def test_add_line(self, monkeypatch, capsys):
        """unittest for Results.add_line
        """
        monkeypatch.setattr(testee.qtw, 'QHBoxLayout', mockqtw.MockHBoxLayout)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.vbox = mockqtw.MockVBoxLayout()
        assert capsys.readouterr().out == "called VBox.__init__\n"
        result = testobj.add_line()
        assert isinstance(result, testee.qtw.QHBoxLayout)
        assert capsys.readouterr().out == ("called HBox.__init__\n"
                                           "called VBox.addLayout with arg MockHBoxLayout\n")

    def test_add_text_to_line(self, monkeypatch, capsys):
        """unittest for Results.add_text_to_line
        """
        monkeypatch.setattr(testee.qtw, 'QLabel', mockqtw.MockLabel)
        testobj = self.setup_testobj(monkeypatch, capsys)
        hbox = mockqtw.MockHBoxLayout()
        assert capsys.readouterr().out == "called HBox.__init__\n"
        testobj.add_text_to_line(hbox, 'text')
        assert capsys.readouterr().out == (f"called Label.__init__ with args ('text', {testobj})\n"
                                           "called HBox.addWidget with arg MockLabel\n")

    def test_add_buttons_to_line(self, monkeypatch, capsys):
        """unittest for Results.add_buttons_to_line
        """
        def callback1():
            "dummy function, just for reference"
        def callback2():
            "dummy function, just for reference"
        monkeypatch.setattr(testee.qtw, 'QPushButton', mockqtw.MockPushButton)
        testobj = self.setup_testobj(monkeypatch, capsys)
        hbox = mockqtw.MockHBoxLayout()
        assert capsys.readouterr().out == "called HBox.__init__\n"
        # testobj.add_buttons_to_line(hbox, (), start=True, end=True)
        # assert capsys.readouterr().out == ("called HBox.addStretch\n"
        #                                    "called HBox.addStretch\n")
        testobj.add_buttons_to_line(hbox, (('text1', callback1, True), ('text2', callback2, False)))
        assert capsys.readouterr().out == (
                f"called PushButton.__init__ with args ('text1', {testobj}) {{}}\n"
                f"called Signal.connect with args ({callback1},)\n"
                "called PushButton.setEnabled with arg `True`\n"
                "called HBox.addWidget with arg MockPushButton\n"
                f"called PushButton.__init__ with args ('text2', {testobj}) {{}}\n"
                f"called Signal.connect with args ({callback2},)\n"
                "called PushButton.setEnabled with arg `False`\n"
                "called HBox.addWidget with arg MockPushButton\n")

    def test_add_results_list(self, monkeypatch, capsys):
        """unittest for Results.add_results_list
        """
        def mock_populate(*args):
            print('called ResultsGui.populate_list with args', args[0].__class__, args[1:])
        def mock_goto():
            print('called Results.goto_result')
        def callback1():
            "dummy function, just for reference"
        def callback2():
            "dummy function, just for reference"
        monkeypatch.setattr(testee.qtw, 'QTableWidget', mockqtw.MockTable)
        monkeypatch.setattr(testee.gui, 'QAction', mockqtw.MockAction)
        monkeypatch.setattr(testee.qtw.QDialog, 'addAction', mockqtw.MockDialog.addAction)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.populate_list = mock_populate
        testobj.master.goto_result = mock_goto
        hbox = mockqtw.MockHBoxLayout()
        assert capsys.readouterr().out == "called HBox.__init__\n"
        testobj.add_results_list(hbox, ['xxx', 'yyy'], [], ['item', 'list'])
        assert capsys.readouterr().out == (
                f"called Table.__init__ with args ({testobj},)\n"
                "called Header.__init__\n"
                "called Header.__init__\n"
                "called Table.verticalHeader\n"
                "called Header.setVisible with args 'False'\n"
                "called Table.setGridStyle with arg PenStyle.NoPen\n"
                "called Table.setColumnCount with arg '2'\n"
                "called Table.setHorizontalHeaderLabels with arg '['xxx', 'yyy']'\n"
                "called Table.horizontalHeader\n"
                "called Header.setStretchLastSection with arg True\n"
                "called ResultsGui.populate_list with args"
                " <class 'mockgui.mockqtwidgets.MockTable'> (['item', 'list'],)\n"
                "called Table.resizeColumnsToContents\n"
                "called Signal.connect with args ()\n"
                "called HBox.addWidget with arg MockTable\n")
        testobj.add_results_list(hbox, [], [('text1', 'Ctrl+G', callback1),
                                            ('text2', 'F1', callback2)], ['item', 'list'])
        assert capsys.readouterr().out == (
                f"called Table.__init__ with args ({testobj},)\n"
                "called Header.__init__\n"
                "called Header.__init__\n"
                "called Table.verticalHeader\n"
                "called Header.setVisible with args 'False'\n"
                "called Table.setGridStyle with arg PenStyle.NoPen\n"
                "called Table.setColumnCount with arg '0'\n"
                "called Table.setHorizontalHeaderLabels with arg '[]'\n"
                "called Table.horizontalHeader\n"
                "called Header.setStretchLastSection with arg True\n"
                "called ResultsGui.populate_list with args"
                " <class 'mockgui.mockqtwidgets.MockTable'> (['item', 'list'],)\n"
                "called Table.resizeColumnsToContents\n"
                "called Signal.connect with args ()\n"
                "called HBox.addWidget with arg MockTable\n"
                f"called Action.__init__ with args ('text1', {testobj})\n"
                "called Action.setShortcut with arg `Ctrl+G`\n"
                f"called Signal.connect with args ({callback1},)\n"
                "called Dialog.addAction\n"
                f"called Action.__init__ with args ('text2', {testobj})\n"
                "called Action.setShortcut with arg `F1`\n"
                f"called Signal.connect with args ({callback2},)\n"
                "called Dialog.addAction\n")

    def test_add_checkbox_to_line(self, monkeypatch, capsys):
        """unittest for Results.add_checkbox_to_line
        """
        monkeypatch.setattr(testee.qtw, 'QCheckBox', mockqtw.MockCheckBox)
        testobj = self.setup_testobj(monkeypatch, capsys)
        hbox = mockqtw.MockHBoxLayout()
        assert capsys.readouterr().out == "called HBox.__init__\n"
        result = testobj.add_checkbox_to_line(hbox, 'text', 'value')
        assert isinstance(result, testee.qtw.QCheckBox)
        assert capsys.readouterr().out == (f"called CheckBox.__init__ with args ('text', {testobj})\n"
                                           "called CheckBox.setChecked with arg value\n"
                                           "called HBox.addWidget with arg MockCheckBox\n")

    def test_add_stretch_to_line(self, monkeypatch, capsys):
        """unittest for Results.add_checkbox_to_line
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        hbox = mockqtw.MockHBoxLayout()
        assert capsys.readouterr().out == "called HBox.__init__\n"
        result = testobj.add_stretch_to_line(hbox)
        assert capsys.readouterr().out == "called HBox.addStretch\n"

    def test_disable_widget(self, monkeypatch, capsys):
        """unittest for ResultsGui.disabe_widget
        """
        widget =  mockqtw.MockWidget()
        assert capsys.readouterr().out == "called Widget.__init__\n"
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.disable_widget(widget)
        assert capsys.readouterr().out == "called Widget.setEnabled with arg False\n"

    def test_finalize_display(self, monkeypatch, capsys):
        """unittest for Results.add_finalize_display
        """
        monkeypatch.setattr(testee.qtw.QDialog, 'resize', mockqtw.MockDialog.resize)
        monkeypatch.setattr(testee.qtw.QDialog, 'setLayout', mockqtw.MockDialog.setLayout)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.vbox = mockqtw.MockVBoxLayout()
        assert capsys.readouterr().out == "called VBox.__init__\n"
        testobj.master.parent = types.SimpleNamespace(apptype="single")
        testobj.show_result_details = False
        testobj.master.show_context = False
        testobj.finalize_display()
        assert capsys.readouterr().out == "called Dialog.setLayout with arg MockVBoxLayout\n"
        testobj.master.parent = types.SimpleNamespace(apptype="other")
        testobj.show_result_details = True
        testobj.finalize_display()
        assert capsys.readouterr().out == ("called Dialog.setLayout with arg MockVBoxLayout\n"
                                           "called Dialog.resize with args (724, 488)\n")
        testobj.master.parent = types.SimpleNamespace(apptype="single")
        testobj.master.show_context = True
        testobj.finalize_display()
        assert capsys.readouterr().out == ("called Dialog.setLayout with arg MockVBoxLayout\n"
                                           "called Dialog.resize with args (824, 488)\n")

    def test_populate_list(self, monkeypatch, capsys, expected_output):
        """unittest for ResultsGui.populate_list
        """
        monkeypatch.setattr(testee.qtw, 'QTableWidgetItem', mockqtw.MockTableItem)
        testobj = self.setup_testobj(monkeypatch, capsys)
        lijst = mockqtw.MockTable()
        assert capsys.readouterr().out == ("called Table.__init__ with args ()\n"
                                           "called Header.__init__\n"
                                           "called Header.__init__\n")
        items = ['no results']
        testobj.populate_list(lijst, items)
        assert capsys.readouterr().out == ""
        items = ['results', ['x', 'y', 'z'], ['a', 'b', 'c']]
        testobj.master.show_context = False
        testobj.populate_list(lijst, items)
        assert capsys.readouterr().out == expected_output['populate']
        testobj.master.show_context = True
        testobj.populate_list(lijst, items)
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

    def test_set_header(self, monkeypatch, capsys):
        """unittest for ResultsGui.set_header
        """
        widget = mockqtw.MockLabel()
        assert capsys.readouterr().out == "called Label.__init__\n"
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.set_header(widget, 'text')
        assert capsys.readouterr().out == "called Label.setText with arg `text`\n"

    def test_get_checkbox_value(self, monkeypatch, capsys):
        """unittest for Results._get_checkbox_value
        """
        widget = mockqtw.MockCheckBox()
        assert capsys.readouterr().out == "called CheckBox.__init__\n"
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert not testobj.get_checkbox_value(widget)
        assert capsys.readouterr().out == "called CheckBox.isChecked\n"

    def test_get_savefile(self, monkeypatch, capsys):
        """unittest for ResultsGui.get_savefile
        """
        monkeypatch.setattr(testee.qtw.QFileDialog, 'getSaveFileName',
                            mockqtw.MockFileDialog.getSaveFileName)
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.get_savefile('title', 'dirname', 'fname',
                                    [('.', 'x-files'), ('.y', 'y-files')]) == ""
        assert capsys.readouterr().out == (
                f"called FileDialog.getSaveFileName with args {testobj}"
                " ('title', 'dirname/fname', 'x-files (*.);;y-files (*.y)') {}\n")

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

    def _test_remember_settings(self, monkeypatch, capsys):
        """unittest for ResultsGui.remember_settings
        """
        def mock_write():
            print('called Afrift.write_to_ini')
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.master.parent = types.SimpleNamespace(outopts={}, write_to_ini=mock_write)
        testobj.get_pth = lambda: 'path'
        testobj.get_csv = lambda: 'csv'
        testobj.get_sum = lambda: 'summ'
        testobj.remember_settings()
        assert testobj.master.parent.outopts == {'full_path': 'path', 'as_csv': 'csv',
                                                 'summarize': 'summ'}
        assert capsys.readouterr().out == "called Afrift.write_to_ini\n"

    def test_klaar(self, monkeypatch, capsys):
        """unittest for ResultsGui.klaar
        """
        monkeypatch.setattr(testee.qtw.QDialog, 'done', mockqtw.MockDialog.done)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.klaar()
        assert capsys.readouterr().out == "called Dialog.done with arg `0`\n"


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

@pytest.fixture
def expected_output():
    """output from GUI creation methods
    """
    return {'populate': populate_1, 'populate2': populate_2}
