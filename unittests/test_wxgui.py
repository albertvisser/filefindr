"""unittests for ./afrift/gui_wx.py
"""
import types
from afrift import gui_wx as testee
from mockgui import mockwxwidgets as mockwx


class TestMyListCtrl:
    """unittests for gui_wx.MyListCtrl
    """
    def setup_testobj(self, monkeypatch, capsys):
        """stub for gui_wx.MyListCtrl object

        create the object skipping the normal initialization
        intercept messages during creation
        return the object so that other methods can be monkeypatched in the caller
        """
        def mock_init(self, *args):
            """stub
            """
            print('called MyListCtrl.__init__ with args', args)
        monkeypatch.setattr(testee.MyListCtrl, '__init__', mock_init)
        testobj = testee.MyListCtrl()
        assert capsys.readouterr().out == 'called MyListCtrl.__init__ with args ()\n'
        return testobj

    def test_init(self, monkeypatch, capsys):
        """unittest for MyListCtrl.__init__
        """
        monkeypatch.setattr(testee.wx.ListCtrl, '__init__', mockwx.MockListCtrl.__init__)
        monkeypatch.setattr(testee.listmix.ListCtrlAutoWidthMixin, '__init__',
                            mockwx.MockListCtrlAutoWidthMixin.__init__)
        parent = 'parent'
        testobj = testee.MyListCtrl(parent)
        assert capsys.readouterr().out == (
                "called ListCtrl.__init__ with args"
                " ('parent',) {'pos': wx.Point(-1, -1), 'size': wx.Size(-1, -1), 'style': 0}\n"
                "called ListCtrlAutoWidthMixin.__init__ with args () {}\n")
        testobj = testee.MyListCtrl(parent, pos="pos", size="size", style="style")
        assert capsys.readouterr().out == (
                "called ListCtrl.__init__ with args"
                " ('parent',) {'pos': 'pos', 'size': 'size', 'style': 'style'}\n"
                "called ListCtrlAutoWidthMixin.__init__ with args () {}\n")


class TestAfriftGui:
    """unittests for gui_wx.AfriftGui
    """
    def setup_testobj(self, monkeypatch, capsys):
        """stub for gui_wx.AfriftGui object

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
        assert capsys.readouterr().out == 'called AfriftGui.__init__ with args ()\n'
        return testobj

    def test_init(self, monkeypatch, capsys):
        """unittest for AfriftGui.__init__
        """
        monkeypatch.setattr(testee.wx.Frame, '__init__', mockwx.MockFrame.__init__)
        monkeypatch.setattr(testee.wx.Frame, 'SetIcon', mockwx.MockFrame.SetIcon)
        monkeypatch.setattr(testee.wx, 'Icon', mockwx.MockIcon)
        master = types.SimpleNamespace(title='xxx', iconame='yyy')
        testobj = testee.AfriftGui(master)
        assert testobj.master == master
        assert isinstance(testobj.app, testee.wx.App)
        assert capsys.readouterr().out == (
                "called frame.__init__ with args (None,) {'title': 'xxx', 'style': 541072960}\n"
                "called Icon.__init__ with args ('yyy', 3)\n"
                "called Frame.SetIcon with args (Icon created from 'yyy',)\n")

    def test_init_screen(self, monkeypatch, capsys):
        """unittest for AfriftGui.init_screen
        """
        monkeypatch.setattr(testee.wx, 'Panel', mockwx.MockPanel)
        monkeypatch.setattr(testee.wx, 'GridBagSizer', mockwx.MockGridSizer)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.init_screen()
        assert isinstance(testobj.pnl, testee.wx.Panel)
        assert isinstance(testobj.grid, testee.wx.GridBagSizer)
        assert testobj.row == -1
        assert capsys.readouterr().out == (f"called Panel.__init__ with args ({testobj},) {{}}\n"
                                           "called GridSizer.__init__ with args () {}\n")

    def test_add_combobox_row(self, monkeypatch, capsys):
        """unittest for AfriftGui.add_combobox_row
        """
        def callback1():
            "dummy function, just for reference"
        def callback2():
            "dummy function, just for reference"
        monkeypatch.setattr(testee.wx, 'StaticText', mockwx.MockStaticText)
        monkeypatch.setattr(testee.wx, 'ComboBox', mockwx.MockComboBox)
        monkeypatch.setattr(testee.wx, 'Button', mockwx.MockButton)
        monkeypatch.setattr(testee.wx, 'BoxSizer', mockwx.MockBoxSizer)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.grid = mockwx.MockGridSizer()
        testobj.pnl = mockwx.MockPanel()
        assert capsys.readouterr().out == ("called GridSizer.__init__ with args () {}\n"
                                           "called Panel.__init__ with args () {}\n")
        testobj.row = 0
        result = testobj.add_combobox_row('label', ['choi', 'ces'])
        assert testobj.row == 1
        assert isinstance(result, testee.wx.ComboBox)
        assert capsys.readouterr().out == (
                f"called StaticText.__init__ with args ({testobj.pnl},) {{'label': 'label'}}\n"
                "called GridSizer.Add with args <item> ((1, 0),) {'flag': 8432, 'border': 4}\n"
                f"called ComboBox.__init__ with args ({testobj.pnl},)"
                " {'size': (240, 24), 'style': 32, 'choices': ['choi', 'ces']}\n"
                "called combobox.AutoComplete with args (['choi', 'ces'],)\n"
                "called GridSizer.Add with args <item> ((1, 1),) {'flag': 2048}\n")
        testobj.row = 0
        result = testobj.add_combobox_row('label', ['choi', 'ces'], initial='xxx',
                                          button=('btn', callback1), callback=callback2)
        assert testobj.row == 1
        assert isinstance(result, testee.wx.ComboBox)
        assert capsys.readouterr().out == (
                f"called StaticText.__init__ with args ({testobj.pnl},) {{'label': 'label'}}\n"
                "called GridSizer.Add with args <item> ((1, 0),) {'flag': 8432, 'border': 4}\n"
                f"called ComboBox.__init__ with args ({testobj.pnl},)"
                " {'size': (240, 24), 'style': 32, 'choices': ['choi', 'ces']}\n"
                "called combobox.AutoComplete with args (['choi', 'ces'],)\n"
                "called combobox.SetValue with args ('xxx',)\n"
                f"called Button.__init__ with args ({testobj.pnl},)"
                " {'label': 'btn', 'size': (-1, 24)}\n"
                f"called Button.Bind with args ({testee.wx.EVT_BUTTON}, {callback1}) {{}}\n"
                "called BoxSizer.__init__ with args (4,)\n"
                "called hori sizer.Add with args <item> (0, 8192)\n"
                "called hori sizer.Add with args <item> (0, 8240, 4)\n"
                "called GridSizer.Add with args <item> ((1, 1),) {'flag': 8384, 'border': 2}\n"
                f"called ComboBox.Bind with args ({testee.wx.EVT_TEXT}, {callback2}) {{}}\n")

    def test_add_checkbox_row(self, monkeypatch, capsys):
        """unittest for AfriftGui.add_checkbox_row
        """
        monkeypatch.setattr(testee.wx, 'CheckBox', mockwx.MockCheckBox)
        monkeypatch.setattr(testee.wx, 'SpinCtrl', mockwx.MockSpinCtrl)
        monkeypatch.setattr(testee.wx, 'BoxSizer', mockwx.MockBoxSizer)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.row = 0
        testobj.grid = mockwx.MockGridSizer()
        testobj.pnl = mockwx.MockPanel()
        assert capsys.readouterr().out == ("called GridSizer.__init__ with args () {}\n"
                                           "called Panel.__init__ with args () {}\n")
        result = testobj.add_checkbox_row('labeltext')
        assert testobj.row == 1
        assert isinstance(result, testee.wx.CheckBox)
        assert capsys.readouterr().out == (
                "called BoxSizer.__init__ with args (8,)\n"
                "called BoxSizer.__init__ with args (4,)\n"
                "called BoxSizer.__init__ with args (4,)\n"
                f"called CheckBox.__init__ with args ({testobj.pnl},) {{'label': 'labeltext'}}\n"
                "called hori sizer.Add with args <item> (0,)\n"
                "called hori sizer.Add with args <item> (0, 192, 4)\n"
                "called vert sizer.Add with args <item> (0, 8192)\n"
                "called GridSizer.Add with args <item> ((1, 1),) {'flag': 8192}\n")
        testobj.row = 0
        assert testobj.add_checkbox_row('labeltext', value='xxx', indent=10)
        assert isinstance(result, testee.wx.CheckBox)
        assert capsys.readouterr().out == (
                "called BoxSizer.__init__ with args (8,)\n"
                "called BoxSizer.__init__ with args (4,)\n"
                "called BoxSizer.__init__ with args (4,)\n"
                f"called CheckBox.__init__ with args ({testobj.pnl},) {{'label': 'labeltext'}}\n"
                "called checkbox.SetValue with args ('xxx',)\n"
                "called hori sizer.Add with args <item> (0, 16, 10)\n"
                "called hori sizer.Add with args <item> (0, 192, 4)\n"
                "called vert sizer.Add with args <item> (0, 8192)\n"
                "called GridSizer.Add with args <item> ((1, 1),) {'flag': 8192}\n")
        testobj.row = 0
        result = testobj.add_checkbox_row('labeltext', spinner=(5, 1))
        assert isinstance(result[0], testee.wx.CheckBox)
        assert isinstance(result[1], testee.wx.SpinCtrl)
        assert capsys.readouterr().out == (
                "called BoxSizer.__init__ with args (8,)\n"
                "called BoxSizer.__init__ with args (4,)\n"
                "called BoxSizer.__init__ with args (4,)\n"
                f"called CheckBox.__init__ with args ({testobj.pnl},) {{'label': 'labeltext'}}\n"
                "called hori sizer.Add with args <item> (0, 2048)\n"
                f"called SpinCtrl.__init__ with args ({testobj.pnl}, -1)"
                " {'min': 1, 'initial': 5, 'size': (122, 24)}\n"
                "called hori sizer.Add with args <item> (0, 2048)\n"
                "called hori sizer.Add with args <item> (0, 192, 4)\n"
                "called vert sizer.Add with args <item> (0, 8192)\n"
                "called GridSizer.Add with args <item> ((1, 1),) {'flag': 8192}\n")

    def test_add_label_to_grid(self, monkeypatch, capsys):
        """unittest for AfriftGui.add_label_to_grid
        """
        monkeypatch.setattr(testee.wx, 'StaticText', mockwx.MockStaticText)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.grid = mockwx.MockGridSizer()
        testobj.pnl = mockwx.MockPanel()
        assert capsys.readouterr().out == ("called GridSizer.__init__ with args () {}\n"
                                           "called Panel.__init__ with args () {}\n")
        testobj.row = 0
        testobj.add_label_to_grid('text')
        assert testobj.row == 1
        assert capsys.readouterr().out == (
                f"called StaticText.__init__ with args ({testobj.pnl},) {{'label': 'text'}}\n"
                "called GridSizer.Add with args <item> ((1, 0),) {'flag': 8432, 'border': 4}\n")
        testobj.row = 0
        testobj.add_label_to_grid('text', fullwidth=True)
        assert testobj.row == 1
        assert capsys.readouterr().out == (
            f"called StaticText.__init__ with args ({testobj.pnl},) {{'label': 'text'}}\n"
            "called GridSizer.Add with args <item> ((1, -1), (1, 2)) {'flag': 8272, 'border': 3}\n")
        testobj.row = 0
        testobj.add_label_to_grid('text', left_align=True)
        assert testobj.row == 1
        assert capsys.readouterr().out == (
                f"called StaticText.__init__ with args ({testobj.pnl},) {{'label': 'text'}}\n"
                "called GridSizer.Add with args <item> ((1, -1),) {'flag': 8432, 'border': 3}\n")

    def test_add_listbox_to_grid(self, monkeypatch, capsys):
        """unittest for AfriftGui.add_listbox_to_grid
        """
        monkeypatch.setattr(testee.wx, 'ListBox', mockwx.MockListBox)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.grid = mockwx.MockGridSizer()
        testobj.pnl = mockwx.MockPanel()
        assert capsys.readouterr().out == ("called GridSizer.__init__ with args () {}\n"
                                           "called Panel.__init__ with args () {}\n")
        testobj.row = 0
        result = testobj.add_listbox_to_grid(['list', 'items'])
        assert testobj.row == 1
        assert isinstance(result, testee.wx.ListBox)
        assert capsys.readouterr().out == (
            f"called ListBox.__init__ with args ({testobj.pnl},)"
            " {'size': (240, 120), 'choices': ['list', 'items']}\n"
            "called GridSizer.Add with args <item> ((1, 0), (1, 2)) {'flag': 8240, 'border': 4}\n")

    def test_add_buttons(self, monkeypatch, capsys):
        """unittest for AfriftGui.add_buttons
        """
        def callback1():
            "dummy function, just for reference"
        def callback2():
            "dummy function, just for reference"
        def mock_fromstring(self, *args):
            print('called AcceleratorEntry.FromString with args', args)
            return False
        monkeypatch.setattr(testee.wx, 'BoxSizer', mockwx.MockBoxSizer)
        monkeypatch.setattr(testee.wx, 'Button', mockwx.MockButton)
        monkeypatch.setattr(testee.wx, 'MenuItem', mockwx.MockMenuItem)
        monkeypatch.setattr(testee.wx, 'AcceleratorEntry', mockwx.MockAcceleratorEntry)
        monkeypatch.setattr(testee.wx, 'AcceleratorTable', mockwx.MockAcceleratorTable)
        monkeypatch.setattr(testee.wx.Frame, 'Bind', mockwx.MockFrame.Bind)
        monkeypatch.setattr(testee.wx.Frame, 'SetAcceleratorTable',
                            mockwx.MockFrame.SetAcceleratorTable)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.grid = mockwx.MockGridSizer()
        testobj.pnl = mockwx.MockPanel()
        assert capsys.readouterr().out == ("called GridSizer.__init__ with args () {}\n"
                                           "called Panel.__init__ with args () {}\n")
        testobj.row = 0
        testobj.add_buttons([])
        assert testobj.row == 1
        assert capsys.readouterr().out == (
            "called BoxSizer.__init__ with args (4,)\n"
            "called GridSizer.Add with args <item> ((1, 0), (1, 3)) {'flag': 1280, 'border': 0}\n")
        testobj.row = 0
        testobj.add_buttons([('btn1', callback1), ('btn2', callback2)])
        assert testobj.row == 1
        assert capsys.readouterr().out == (
                "called BoxSizer.__init__ with args (4,)\n"
                f"called Button.__init__ with args ({testobj.pnl}, -1)"
                " {'size': (-1, 24), 'label': 'btn1'}\n"
                f"called Button.Bind with args ({testee.wx.EVT_BUTTON}, {callback1}) {{}}\n"
                "called hori sizer.Add with args <item> (0, 8432, 4)\n"
                "called MenuItem.__init__ with args (None,) {'text': 'btn1'}\n"
                f"called Frame.Bind with args ({testee.wx.EVT_MENU}, {callback1})\n"
                "called menuitem.GetId\n"
                "called AcceleratorEntry.__init__ with args () {'cmd': 'NewID'}\n"
                "called AcceleratorEntry.FromString with args ('Return',)\n"
                f"called Button.__init__ with args ({testobj.pnl}, -1)"
                " {'size': (-1, 24), 'label': 'btn2'}\n"
                f"called Button.Bind with args ({testee.wx.EVT_BUTTON}, {callback2}) {{}}\n"
                "called hori sizer.Add with args <item> (0, 8432, 4)\n"
                "called MenuItem.__init__ with args (None,) {'text': 'btn2'}\n"
                f"called Frame.Bind with args ({testee.wx.EVT_MENU}, {callback2})\n"
                "called menuitem.GetId\n"
                "called AcceleratorEntry.__init__ with args () {'cmd': 'NewID'}\n"
                "called AcceleratorEntry.FromString with args ('Escape',)\n"
                "called GridSizer.Add with args"
                " <item> ((1, 0), (1, 3)) {'flag': 1280, 'border': 0}\n"
                "called AcceleratorTable.__init__ with 2 AcceleratorEntries\n"
                "called Frame.SetAcceleratorTable\n")
        monkeypatch.setattr(testee.wx.AcceleratorEntry, 'FromString', mock_fromstring)
        testobj.row = 0
        testobj.add_buttons([('btn1', callback1), ('btn2', callback2)])
        assert testobj.row == 1
        assert capsys.readouterr().out == (
                "called BoxSizer.__init__ with args (4,)\n"
                f"called Button.__init__ with args ({testobj.pnl}, -1)"
                " {'size': (-1, 24), 'label': 'btn1'}\n"
                f"called Button.Bind with args ({testee.wx.EVT_BUTTON}, {callback1}) {{}}\n"
                "called hori sizer.Add with args <item> (0, 8432, 4)\n"
                "called MenuItem.__init__ with args (None,) {'text': 'btn1'}\n"
                f"called Frame.Bind with args ({testee.wx.EVT_MENU}, {callback1})\n"
                "called menuitem.GetId\n"
                "called AcceleratorEntry.__init__ with args () {'cmd': 'NewID'}\n"
                "called AcceleratorEntry.FromString with args ('Return',)\n"
                f"called Button.__init__ with args ({testobj.pnl}, -1)"
                " {'size': (-1, 24), 'label': 'btn2'}\n"
                f"called Button.Bind with args ({testee.wx.EVT_BUTTON}, {callback2}) {{}}\n"
                "called hori sizer.Add with args <item> (0, 8432, 4)\n"
                "called MenuItem.__init__ with args (None,) {'text': 'btn2'}\n"
                f"called Frame.Bind with args ({testee.wx.EVT_MENU}, {callback2})\n"
                "called menuitem.GetId\n"
                "called AcceleratorEntry.__init__ with args () {'cmd': 'NewID'}\n"
                "called AcceleratorEntry.FromString with args ('Escape',)\n"
                "called GridSizer.Add with args"
                " <item> ((1, 0), (1, 3)) {'flag': 1280, 'border': 0}\n")

    def test_set_focus_to(self, monkeypatch, capsys):
        """unittest for AfriftGui.set_focus_to
        """
        widget = mockwx.MockControl()
        assert capsys.readouterr().out == "called Control.__init__\n"
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.set_focus_to(widget)
        assert capsys.readouterr().out == "called Control.SetFocus\n"

    def test_get_combobox_value(self, monkeypatch, capsys):
        """unittest for AfriftGui.get_combobox_value
        """
        cb = mockwx.MockComboBox()
        assert capsys.readouterr().out == "called ComboBox.__init__ with args () {}\n"
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.get_combobox_value(cb) == "value from combobox"
        assert capsys.readouterr().out == "called combobox.GetValue\n"

    def test_get_checkbox_value(self, monkeypatch, capsys):
        """unittest for AfriftGui.get_checkbox_value
        """
        cb = mockwx.MockCheckBox()
        assert capsys.readouterr().out == "called CheckBox.__init__ with args () {}\n"
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.get_checkbox_value(cb) == "value from checkbox"
        assert capsys.readouterr().out == "called checkbox.GetValue\n"

    def test_get_spinbox_value(self, monkeypatch, capsys):
        """unittest for AfriftGui.get_spinbox_value
        """
        sb = mockwx.MockSpinCtrl()
        assert capsys.readouterr().out == "called SpinCtrl.__init__ with args () {}\n"
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.get_spinbox_value(sb) == "value from spinctrl"
        assert capsys.readouterr().out == "called SpinCtrl.GetValue\n"

    def test_go(self, monkeypatch, capsys):
        """unittest for AfriftGui.go
        """
        def mock_show(*args):
            print('called Frame.Showi with args', args)
        def mock_mainloop():
            print('called Frame.MainLoop')
        monkeypatch.setattr(testee.wx, 'BoxSizer', mockwx.MockBoxSizer)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.Show = mock_show
        testobj.app = types.SimpleNamespace(MainLoop=mock_mainloop)
        testobj.grid = mockwx.MockGridSizer()
        testobj.pnl = mockwx.MockPanel()
        assert capsys.readouterr().out == ("called GridSizer.__init__ with args () {}\n"
                                           "called Panel.__init__ with args () {}\n")
        testobj.go()
        assert capsys.readouterr().out == ("called BoxSizer.__init__ with args (8,)\nc"
                                           "alled vert sizer.Add with args <item> (0, 240, 4)\n"
                                           "called Panel.SetAutoLayout with args (True,)\n"
                                           "called Panel.SetSizer with args (vert sizer,)\n"
                                           f"called vert sizer.Fit with args ({testobj},)\n"
                                           "called Panel.Layout with args ()\n"
                                           "called Frame.Showi with args (True,)\n"
                                           "called Frame.MainLoop\n")

    def test_error(self, monkeypatch, capsys):
        """unittest for AfriftGui.error
        """
        monkeypatch.setattr(testee.wx, 'MessageBox', mockwx.mock_messagebox)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.error('titel', 'message')
        assert capsys.readouterr().out == (
                f"called wx.MessageBox with args ('message', 'titel', 516, {testobj})\n")

    def test_meld(self, monkeypatch, capsys):
        """unittest for AfriftGui.meld
        """
        monkeypatch.setattr(testee.wx, 'MessageBox', mockwx.mock_messagebox)
        monkeypatch.setattr(testee.wx, 'MessageDialog', mockwx.MockMessageDialog)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.meld('titel', 'message')
        assert capsys.readouterr().out == (
                f"called wx.MessageBox with args ('message', 'titel', 2052, {testobj})\n")
        testobj.meld('titel', 'message', additional=['addit', 'ional'])
        assert capsys.readouterr().out == (
                "called MessageDialog.__init__ with args"
                f" ({testobj}, 'message', 'titel', 2052) {{}}\n"
                "called MessageDialog.SetExtendedMessage with args ('addit\\nional',)\n"
                "called MessageDialog.ShowModal\n")

    def test_add_item_to_searchlist(self, monkeypatch, capsys):
        """unittest for AfriftGui.add_item_to_searchlist
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        listbox = mockwx.MockListBox()
        testobj.add_item_to_searchlist(listbox, 'item')
        assert capsys.readouterr().out == ("called ListBox.__init__ with args () {}\n"
                                           "called listbox.Insert with args ('item', 0)\n")

    def test_set_waitcursor(self, monkeypatch, capsys):
        """unittest for AfriftGui.set_waitcursor
        """
        def mock_begin():
            print('called wx.BeginBusyCursor')
        def mock_end():
            print('called wx.EndBusyCursor')
        monkeypatch.setattr(testee.wx, 'BeginBusyCursor', mock_begin)
        monkeypatch.setattr(testee.wx, 'EndBusyCursor', mock_end)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.set_waitcursor(True)
        assert capsys.readouterr().out == ("called wx.BeginBusyCursor\n")
        testobj.set_waitcursor(False)
        assert capsys.readouterr().out == ("called wx.EndBusyCursor\n")

    def test_einde(self, monkeypatch, capsys):
        """unittest for AfriftGui.einde
        """
        def mock_close(arg):
            print(f'called AfriftGui.Close with arg {arg}')
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.Close = mock_close
        testobj.einde(event=None)
        assert capsys.readouterr().out == ("called AfriftGui.Close with arg True\n")

    def test_get_sender_value(self, monkeypatch, capsys):
        """unittest for AfriftGui.get_sender_value
        """
        def mock_get():
            print('called Widget.GetValue')
            return 'xxx'
        def mock_getobj():
            print('called Event.GetEventObject')
            return types.SimpleNamespace(GetValue=mock_get)
        testobj = self.setup_testobj(monkeypatch, capsys)
        event = types.SimpleNamespace(GetEventObject=mock_getobj)
        assert testobj.get_sender_value(event) == 'xxx'
        assert capsys.readouterr().out == ("called Event.GetEventObject\n"
                                           "called Widget.GetValue\n")

    def test_replace_combobox_items(self, monkeypatch, capsys):
        """unittest for AfriftGui.replace_combobox_items
        """
        cmb = mockwx.MockComboBox()
        assert capsys.readouterr().out == "called ComboBox.__init__ with args () {}\n"
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.replace_combobox_items(cmb, [])
        assert capsys.readouterr().out == (
                "called combobox.clear\n"
                "called combobox.AppendItems with args ([],)\n")
        testobj.replace_combobox_items(cmb, ['x', 'y'])
        assert capsys.readouterr().out == (
                "called combobox.clear\n"
                "called combobox.AppendItems with args (['x', 'y'],)\n"
                "called combobox.SetValue with args ('x',)\n")

    def test_set_checkbox_value(self, monkeypatch, capsys):
        """unittest for AfriftGui.set_checkbox_value
        """
        cb = mockwx.MockCheckBox()
        assert capsys.readouterr().out == "called CheckBox.__init__ with args () {}\n"
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.set_checkbox_value(cb, 'value')
        assert capsys.readouterr().out == "called checkbox.SetValue with args ('value',)\n"

    def test_zoekdir(self, monkeypatch, capsys):
        """unittest for AfriftGui.zoekdir
        """
        def mock_show(self):
            print('called DirDialog.ShowModal')
            return testee.wx.ID_CANCEL
        monkeypatch.setattr(testee.wx, 'DirDialog', mockwx.MockDirDialog)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.vraag_dir = mockwx.MockComboBox()
        assert capsys.readouterr().out == "called ComboBox.__init__ with args () {}\n"
        testobj.zoekdir('event')
        assert capsys.readouterr().out == (
            "called combobox.GetValue\n"
            "called DirDialog.__init__ with args ('Choose a directory:',)"
            " {'defaultPath': 'value from combobox', 'style': 536877632}\n"
            "called DirDialog.ShowModal\n"
            "called DirDialog.GetPath\n"
            "called combobox.SetValue with args ('dirname',)\n")
        monkeypatch.setattr(testee.wx.DirDialog, 'ShowModal', mock_show)
        testobj.zoekdir('event')
        assert capsys.readouterr().out == (
            "called combobox.GetValue\n"
            "called DirDialog.__init__ with args ('Choose a directory:',)"
            " {'defaultPath': 'value from combobox', 'style': 536877632}\n"
            "called DirDialog.ShowModal\n")


class TestSelectNamesGui:
    """unittests for gui_wx.SelectNamesGui
    """
    def setup_testobj(self, monkeypatch, capsys):
        """stub for gui_wx.SelectNamesGui object

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
        assert capsys.readouterr().out == 'called SelectNamesGui.__init__ with args ()\n'
        return testobj

    def test_init(self, monkeypatch, capsys):
        """unittest for SelectNamesGui.__init__
        """
        monkeypatch.setattr(testee.wx.Dialog, '__init__', mockwx.MockDialog.__init__)
        monkeypatch.setattr(testee.wx.Dialog, 'SetIcon', mockwx.MockDialog.SetIcon)
        monkeypatch.setattr(testee.wx, 'Icon', mockwx.MockIcon)
        parent = types.SimpleNamespace(gui='AfriftGui')
        master = types.SimpleNamespace(title='title', iconame="icon")
        testobj = testee.SelectNamesGui(parent, master)
        assert capsys.readouterr().out == (
                "called Dialog.__init__ with args () {'title': 'title', 'style': 536877120}\n"
                "called Icon.__init__ with args ('icon', 3)\n"
                "called Dialog.SetIcon with args (Icon created from 'icon',)\n")

    def test_setup_screen(self, monkeypatch, capsys):
        """unittest for SelectNamesGui.setup_screen
        """
        monkeypatch.setattr(testee.wx, 'BoxSizer', mockwx.MockBoxSizer)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.setup_screen()
        assert isinstance(testobj.vbox, testee.wx.BoxSizer)
        assert capsys.readouterr().out == "called BoxSizer.__init__ with args (8,)\n"

    def test_add_line(self, monkeypatch, capsys):
        """unittest for SelectNamesGui.add_line
        """
        monkeypatch.setattr(testee.wx, 'BoxSizer', mockwx.MockBoxSizer)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.vbox = mockwx.MockBoxSizer(testee.wx.VERTICAL)
        assert capsys.readouterr().out == "called BoxSizer.__init__ with args (8,)\n"
        result = testobj.add_line()
        assert isinstance(result, testee.wx.BoxSizer)
        assert capsys.readouterr().out == ("called BoxSizer.__init__ with args (4,)\n"
                                           "called vert sizer.Add with args <item> (0,)\n")

    def test_add_text_to_line(self, monkeypatch, capsys):
        """unittest for SelectNamesGui.add_text_to_line
        """
        monkeypatch.setattr(testee.wx, 'StaticText', mockwx.MockStaticText)
        hbox = mockwx.MockBoxSizer(testee.wx.HORIZONTAL)
        assert capsys.readouterr().out == "called BoxSizer.__init__ with args (4,)\n"
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.add_text_to_line(hbox, 'text')
        assert capsys.readouterr().out == (
                f"called StaticText.__init__ with args ({testobj},) {{'label': 'text'}}\n"
                "called hori sizer.Add with args <item> (0, 8432, 5)\n")

    def test_add_checkbox_to_line(self, monkeypatch, capsys):
        """unittest for SelectNamesGui.add_checkbox_to_line
        """
        def callback():
            "dummy function, just for reference"
        monkeypatch.setattr(testee.wx, 'CheckBox', mockwx.MockCheckBox)
        hbox = mockwx.MockBoxSizer(testee.wx.HORIZONTAL)
        assert capsys.readouterr().out == "called BoxSizer.__init__ with args (4,)\n"
        testobj = self.setup_testobj(monkeypatch, capsys)
        result = testobj.add_checkbox_to_line(hbox, 'text', callback)
        assert isinstance(result, testee.wx.CheckBox)
        assert capsys.readouterr().out == (
                "called hori sizer.AddSpacer with args (10,)\n"
                f"called CheckBox.__init__ with args ({testobj},) {{'label': 'text'}}\n"
                f"called CheckBox.Bind with args ({testee.wx.EVT_CHECKBOX}, {callback}) {{}}\n"
                "called hori sizer.Add with args <item> (0, 2080, 28)\n")

    def test_add_button_to_line(self, monkeypatch, capsys):
        """unittest for SelectNamesGui.add_button_to_line
        """
        def callback():
            "dummy function, just for reference"
        monkeypatch.setattr(testee.wx, 'Button', mockwx.MockButton)
        testobj = self.setup_testobj(monkeypatch, capsys)
        hbox = mockwx.MockBoxSizer(testee.wx.HORIZONTAL)
        assert capsys.readouterr().out == "called BoxSizer.__init__ with args (4,)\n"
        result = testobj.add_button_to_line(hbox, 'text', callback)
        assert isinstance(result, testee.wx.Button)
        assert capsys.readouterr().out == (
                "called Button.__init__ with args"
                f" ({testobj},) {{'size': (-1, 24), 'label': 'text'}}\n"
                f"called Button.Bind with args ({testee.wx.EVT_BUTTON}, {callback}) {{}}\n"
                "called hori sizer.Add with args <item> (0, 544, 7)\n")

    def test_add_selectionlist(self, monkeypatch, capsys):
        """unittest for SelectNamesGui.add_selectionlist
        """
        monkeypatch.setattr(testee.wx, 'CheckListBox', mockwx.MockCheckListBox)
        testobj = self.setup_testobj(monkeypatch, capsys)
        hbox = mockwx.MockBoxSizer(testee.wx.HORIZONTAL)
        assert capsys.readouterr().out == "called BoxSizer.__init__ with args (4,)\n"
        assert testobj.add_selectionlist(hbox, 'namelist') == ['item', 'list']
        assert capsys.readouterr().out == (
                f"called CheckListBox.__init__ with args ({testobj}, -1) {{'choices': 'namelist'}}\n"
                "called hori sizer.Add with args <item> (0, 48, 7)\n"
                "called CheckListBox.GetItems\n")

    def test_add_buttons(self, monkeypatch, capsys):
        """unittest for SelectNamesGui.add_buttons
        """
        def callback1():
            "dummy function, just for reference"
        def callback2():
            "dummy function, just for reference"
        monkeypatch.setattr(testee.wx, 'BoxSizer', mockwx.MockBoxSizer)
        monkeypatch.setattr(testee.wx, 'Button', mockwx.MockButton)
        monkeypatch.setattr(testee.wx.Dialog, 'SetEscapeId', mockwx.MockDialog.SetEscapeId)
        testobj = self.setup_testobj(monkeypatch, capsys)
        hbox = mockwx.MockBoxSizer(testee.wx.HORIZONTAL)
        assert capsys.readouterr().out == "called BoxSizer.__init__ with args (4,)\n"
        testobj.add_buttons(hbox, [('btn1', callback1), ('btn2', callback2)])
        assert capsys.readouterr().out == (
                "called BoxSizer.__init__ with args (4,)\n"
                "called Button.__init__ with args"
                f" ({testobj},) {{'size': (-1, 24), 'label': 'btn1'}}\n"
                "called Button.GetId\n"
                "called dialog.SetEscapeId with args ('id',)\n"
                "called hori sizer.Add with args <item> (0,)\n"
                "called Button.__init__ with args"
                f" ({testobj},) {{'size': (-1, 24), 'label': 'btn2'}}\n"
                f"called Button.Bind with args ({testee.wx.EVT_BUTTON}, {callback2}) {{}}\n"
                "called hori sizer.Add with args <item> (0,)\n"
                "called hori sizer.Add with args <item> (0, 256)\n")

    def test_go(self, monkeypatch, capsys):
        """unittest for SelectNamesGui.go
        """
        def mock_show(self):
            print('called Dialog.ShowModal')
            return testee.wx.ID_CANCEL
        monkeypatch.setattr(testee.wx.Dialog, 'SetAutoLayout', mockwx.MockDialog.SetAutoLayout)
        monkeypatch.setattr(testee.wx.Dialog, 'SetSizer', mockwx.MockDialog.SetSizer)
        monkeypatch.setattr(testee.wx.Dialog, 'Layout', mockwx.MockDialog.Layout)
        monkeypatch.setattr(testee.wx.Dialog, 'ShowModal', mockwx.MockDialog.ShowModal)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.vbox = mockwx.MockBoxSizer(testee.wx.VERTICAL)
        assert capsys.readouterr().out == "called BoxSizer.__init__ with args (8,)\n"
        assert testobj.go()
        assert capsys.readouterr().out == (
                "called dialog.SetAutoLayout with args (True,)\n"
                "called dialog.SetSizer with args (vert sizer,)\n"
                f"called vert sizer.Fit with args ({testobj},)\n"
                "called dialog.Layout with args ()\n"
                "called Dialog.ShowModal\n")
        monkeypatch.setattr(testee.wx.Dialog, 'ShowModal', mock_show)
        assert not testobj.go()
        assert capsys.readouterr().out == (
                "called dialog.SetAutoLayout with args (True,)\n"
                "called dialog.SetSizer with args (vert sizer,)\n"
                f"called vert sizer.Fit with args ({testobj},)\n"
                "called dialog.Layout with args ()\n"
                "called Dialog.ShowModal\n")

    def test_select_all(self, monkeypatch, capsys):
        """unittest for SelectNamesGui.select_all
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.sel_all = mockwx.MockCheckBox()
        testobj.frm = mockwx.MockCheckListBox()
        testobj.checklist = ['x', 'y']
        testobj.select_all('event')
        assert capsys.readouterr().out == (
                "called CheckBox.__init__ with args () {}\n"
                "called CheckListBox.__init__ with args () {}\n"
                "called checkbox.IsChecked\n"
                "called CheckListBox.Check with args (0, 'value from checkbox')\n"
                "called CheckListBox.Check with args (1, 'value from checkbox')\n")

    def test_invert_selection(self, monkeypatch, capsys):
        """unittest for SelectNamesGui.invert_selection
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.frm = mockwx.MockCheckListBox()
        testobj.checklist = ['x', 'y']
        testobj.invert_selection('event')
        assert capsys.readouterr().out == ("called CheckListBox.__init__ with args () {}\n"
                                           "called CheckListBox.IsChecked with arg 0\n"
                                           "called CheckListBox.Check with args (0, False)\n"
                                           "called CheckListBox.IsChecked with arg 1\n"
                                           "called CheckListBox.Check with args (1, False)\n")

    def test_cancel(self, monkeypatch, capsys):
        """unittest for SelectNamesGui.cancel
        """
        monkeypatch.setattr(testee.wx.Dialog, 'EndModal', mockwx.MockDialog.EndModal)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.cancel()
        assert capsys.readouterr().out == (
                f"called Dialog.EndModal with arg {testee.wx.ID_CANCEL}\n")

    def test_confirm(self, monkeypatch, capsys):
        """unittest for SelectNamesGui.confirm
        """
        monkeypatch.setattr(testee.wx.Dialog, 'EndModal', mockwx.MockDialog.EndModal)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.master = types.SimpleNamespace()
        testobj.frm = mockwx.MockCheckListBox()
        assert capsys.readouterr().out == "called CheckListBox.__init__ with args () {}\n"
        testobj.master.do_files = False
        testobj.master.names = {'x': 'xxx', 'w': 'www', 'y': 'yyy'}
        testobj.confirm('event')
        assert testobj.master.names == ['checked', 'strings']
        assert capsys.readouterr().out == ("called CheckListBox.GetCheckedStrings\n"
                                           "called Dialog.EndModal with arg 5100\n")
        testobj.master.do_files = True
        testobj.master.names = {'x': 'xxx', 'w': 'www', 'checked': 'yyy', 'strings': 'qqq'}
        testobj.confirm('event')
        assert testobj.master.names == ['www', 'xxx']
        assert capsys.readouterr().out == ("called CheckListBox.GetCheckedStrings\n"
                                           "called Dialog.EndModal with arg 5100\n")


class TestResultsGui:
    """unittests for gui_wx.ResultsGui
    """
    def setup_testobj(self, monkeypatch, capsys):
        """stub for gui_wx.ResultsGui object

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
        assert capsys.readouterr().out == 'called ResultsGui.__init__ with args ()\n'
        return testobj

    def test_init(self, monkeypatch, capsys):
        """unittest for ResultsGui.__init__
        """
        monkeypatch.setattr(testee.wx.Dialog, '__init__', mockwx.MockDialog.__init__)
        monkeypatch.setattr(testee.wx.Dialog, 'SetIcon', mockwx.MockDialog.SetIcon)
        monkeypatch.setattr(testee.wx, 'Icon', mockwx.MockIcon)
        monkeypatch.setattr(testee.wx, 'BoxSizer', mockwx.MockBoxSizer)
        master = types.SimpleNamespace(parent=types.SimpleNamespace(resulttitel='titel'),
                                       iconame='icon')
        parent = types.SimpleNamespace(gui="ResultsGui")
        testobj = testee.ResultsGui(parent, master)
        assert testobj.show_result_details
        assert isinstance(testobj.vsizer, testee.wx.BoxSizer)
        assert testobj.accel_list == []
        assert capsys.readouterr().out == (
                "called Dialog.__init__ with args () {'title': 'titel', 'style': 536877120}\n"
                "called Icon.__init__ with args ('icon', 3)\n"
                "called Dialog.SetIcon with args (Icon created from 'icon',)\n"
                "called BoxSizer.__init__ with args (8,)\n")

    def test_add_line(self, monkeypatch, capsys):
        """unittest for ResultsGui.add_line
        """
        monkeypatch.setattr(testee.wx, 'BoxSizer', mockwx.MockBoxSizer)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.vsizer = mockwx.MockBoxSizer(testee.wx.VERTICAL)
        assert capsys.readouterr().out == "called BoxSizer.__init__ with args (8,)\n"
        result = testobj.add_line()
        assert isinstance(result, testee.wx.BoxSizer)
        assert capsys.readouterr().out == ("called BoxSizer.__init__ with args (4,)\n"
                                           "called vert sizer.Add with args <item> (0, 8192)\n")

    def test_add_text_to_line(self, monkeypatch, capsys):
        """unittest for ResultsGui.add_text_to_line
        """
        monkeypatch.setattr(testee.wx, 'StaticText', mockwx.MockStaticText)
        hsizer = mockwx.MockBoxSizer(testee.wx.HORIZONTAL)
        assert capsys.readouterr().out == "called BoxSizer.__init__ with args (4,)\n"
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.add_text_to_line(hsizer, 'text')
        assert capsys.readouterr().out == (
                f"called StaticText.__init__ with args ({testobj},) {{'label': 'text'}}\n"
                "called hori sizer.Add with args <item> (0, 8432, 5)\n")

    def test_add_buttons_to_line(self, monkeypatch, capsys):
        """unittest for ResultsGui.add_buttons_to_line
        """
        def callback1():
            "dummy function, just for reference"
        def callback2():
            "dummy function, just for reference"
        monkeypatch.setattr(testee.wx, 'Button', mockwx.MockButton)
        testobj = self.setup_testobj(monkeypatch, capsys)
        hsizer = mockwx.MockBoxSizer(testee.wx.HORIZONTAL)
        assert capsys.readouterr().out == "called BoxSizer.__init__ with args (4,)\n"
        testobj.add_buttons_to_line(hsizer, (('btn1', callback1, True), ('btn2', callback2, False)))
        assert capsys.readouterr().out == (
                "called Button.__init__ with args"
                f" ({testobj},) {{'size': (-1, 24), 'label': 'btn1'}}\n"
                f"called Button.Bind with args ({testee.wx.EVT_BUTTON}, {callback1}) {{}}\n"
                "called hori sizer.Add with args <item> (0, 240, 5)\n"
                "called Button.Enable with arg True\n"
                "called Button.__init__ with args"
                f" ({testobj},) {{'size': (-1, 24), 'label': 'btn2'}}\n"
                f"called Button.Bind with args ({testee.wx.EVT_BUTTON}, {callback2}) {{}}\n"
                "called hori sizer.Add with args <item> (0, 240, 5)\n"
                "called Button.Enable with arg False\n")
        testobj.add_buttons_to_line(hsizer, (), start=True)
        assert capsys.readouterr().out == ""
        testobj.add_buttons_to_line(hsizer, (), end=True)
        assert capsys.readouterr().out == "called hori sizer.AddStretchSpacer\n"

    def test_add_results_list(self, monkeypatch, capsys):
        """unittest for ResultsGui.add_results_list
        """
        def mock_populate(*args):
            print('called MyListCtrl.populate_list with args', args[0].__class__, args[1:])
        def mock_result():
            "empty callback, just for reference"
        def callback1():
            "dummy function, just for reference"
        def callback2():
            "dummy function, just for reference"
        def mock_fromstring(self, *args):
            print('called AcceleratorEntry.FromString with args', args)
            return False
        monkeypatch.setattr(testee, 'MyListCtrl', mockwx.MockListCtrl)
        monkeypatch.setattr(testee.wx, 'MenuItem', mockwx.MockMenuItem)
        monkeypatch.setattr(testee.wx, 'AcceleratorEntry', mockwx.MockAcceleratorEntry)
        monkeypatch.setattr(testee.wx.Dialog, 'Bind', mockwx.MockDialog.Bind)
        hsizer = mockwx.MockBoxSizer(testee.wx.HORIZONTAL)
        assert capsys.readouterr().out == "called BoxSizer.__init__ with args (4,)\n"
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.master = types.SimpleNamespace(parent=types.SimpleNamespace(apptype='xxx'))
        testobj.populate_list = mock_populate
        testobj.to_result = mock_result
        testobj.accel_list = []
        testobj.add_results_list(hsizer, [], [], ['item', 'list'])
        assert testobj.accel_list == []
        assert capsys.readouterr().out == (
                "called ListCtrl.__init__ with args"
                f" ({testobj},) {{'size': (-1, 460), 'style': 33}}\n"
                "called ListCtrl.resizeLastColumn with args (200,)\n"
                "called MyListCtrl.populate_list with args"
                " <class 'mockgui.mockwxwidgets.MockListCtrl'> (['item', 'list'],)\n"
                "called ListCtrl.Bind with args"
                f" ({testee.wx.EVT_LIST_ITEM_ACTIVATED}, {testobj.to_result})\n"
                "called hori sizer.Add with args <item> (1, 8432, 5)\n")
        testobj.add_results_list(hsizer, ['head', 'ers'], (('txt1', 'key1', callback1),
                                                           ('txt2', 'key2', callback2)),
                                 ['item', 'list'])
        assert len(testobj.accel_list) == 2
        assert isinstance(testobj.accel_list[0], testee.wx.AcceleratorEntry)
        assert isinstance(testobj.accel_list[1], testee.wx.AcceleratorEntry)
        assert capsys.readouterr().out == (
                f"called ListCtrl.__init__ with args ({testobj},)"
                " {'size': (-1, 460), 'style': 33}\n"
                "called ListCtrl.InsertColumn with args (0, 'head')\n"
                "called ListCtrl.SetColumnWidth with args (0, 200)\n"
                "called ListCtrl.InsertColumn with args (1, 'ers')\n"
                "called ListCtrl.SetColumnWidth with args (0, 150)\n"
                "called ListCtrl.resizeLastColumn with args (200,)\n"
                "called MyListCtrl.populate_list with args"
                " <class 'mockgui.mockwxwidgets.MockListCtrl'> (['item', 'list'],)\n"
                "called ListCtrl.Bind with args"
                f" ({testee.wx.EVT_LIST_ITEM_ACTIVATED}, {testobj.to_result})\n"
                "called hori sizer.Add with args <item> (1, 8432, 5)\n"
                "called MenuItem.__init__ with args (None,) {'label': 'txt1'}\n"
                f"called dialog.Bind with args ({testee.wx.EVT_MENU}, {callback1})\n"
                "called menuitem.GetId\n"
                "called AcceleratorEntry.__init__ with args () {'cmd': 'NewID'}\n"
                "called AcceleratorEntry.FromString with args ('key1',)\n"
                "called MenuItem.__init__ with args (None,) {'label': 'txt2'}\n"
                f"called dialog.Bind with args ({testee.wx.EVT_MENU}, {callback2})\n"
                "called menuitem.GetId\n"
                "called AcceleratorEntry.__init__ with args () {'cmd': 'NewID'}\n"
                "called AcceleratorEntry.FromString with args ('key2',)\n")
        monkeypatch.setattr(testee.wx.AcceleratorEntry, 'FromString', mock_fromstring)
        testobj.accel_list = []
        testobj.add_results_list(hsizer, ['head', 'er', 's'], (('txt1', 'key1', callback1),
                                                               ('txt2', 'key2', callback2)),
                                 ['item', 'list'])
        assert testobj.accel_list == []
        assert capsys.readouterr().out == (
                f"called ListCtrl.__init__ with args ({testobj},)"
                " {'size': (-1, 460), 'style': 33}\n"
                "called ListCtrl.InsertColumn with args (0, 'head')\n"
                "called ListCtrl.SetColumnWidth with args (0, 200)\n"
                "called ListCtrl.InsertColumn with args (1, 'er')\n"
                "called ListCtrl.SetColumnWidth with args (0, 150)\n"
                "called ListCtrl.InsertColumn with args (2, 's')\n"
                "called ListCtrl.SetColumnWidth with args (0, 200)\n"
                "called ListCtrl.resizeLastColumn with args (200,)\n"
                "called MyListCtrl.populate_list with args"
                " <class 'mockgui.mockwxwidgets.MockListCtrl'> (['item', 'list'],)\n"
                "called ListCtrl.Bind with args"
                f" ({testee.wx.EVT_LIST_ITEM_ACTIVATED}, {testobj.to_result})\n"
                "called hori sizer.Add with args <item> (1, 8432, 5)\n"
                "called MenuItem.__init__ with args (None,) {'label': 'txt1'}\n"
                f"called dialog.Bind with args ({testee.wx.EVT_MENU}, {callback1})\n"
                "called menuitem.GetId\n"
                "called AcceleratorEntry.__init__ with args () {'cmd': 'NewID'}\n"
                "called AcceleratorEntry.FromString with args ('key1',)\n"
                "called MenuItem.__init__ with args (None,) {'label': 'txt2'}\n"
                f"called dialog.Bind with args ({testee.wx.EVT_MENU}, {callback2})\n"
                "called menuitem.GetId\n"
                "called AcceleratorEntry.__init__ with args () {'cmd': 'NewID'}\n"
                "called AcceleratorEntry.FromString with args ('key2',)\n")

    def test_add_checkbox_to_line(self, monkeypatch, capsys):
        """unittest for ResultsGui.add_checkbox_to_line
        """
        def mock_fromstring(self, *args):
            print('called AcceleratorEntry.FromString with args', args)
            return False
        monkeypatch.setattr(testee.wx, 'CheckBox', mockwx.MockCheckBox)
        monkeypatch.setattr(testee.wx, 'AcceleratorEntry', mockwx.MockAcceleratorEntry)
        hsizer = mockwx.MockBoxSizer(testee.wx.HORIZONTAL)
        assert capsys.readouterr().out == "called BoxSizer.__init__ with args (4,)\n"
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.accel_list = []
        result = testobj.add_checkbox_to_line(hsizer, 'text', 'checkvalue')
        assert isinstance(result, testee.wx.CheckBox)
        assert len(testobj.accel_list) == 1
        assert isinstance(testobj.accel_list[0], testee.wx.AcceleratorEntry)
        assert capsys.readouterr().out == (
                f"called CheckBox.__init__ with args ({testobj},) {{'label': 'text'}}\n"
                "called CheckBox.GetId\n"
                "called AcceleratorEntry.__init__ with args () {'cmd': 'id'}\n"
                "called AcceleratorEntry.FromString with args ('Alt+O',)\n"
                "called checkbox.SetValue with args ('checkvalue',)\n"
                "called hori sizer.Add with args <item> ()\n")
        testobj.accel_list = []
        monkeypatch.setattr(testee.wx.AcceleratorEntry, 'FromString', mock_fromstring)
        result = testobj.add_checkbox_to_line(hsizer, 'text', 'checkvalue')
        assert isinstance(result, testee.wx.CheckBox)
        assert capsys.readouterr().out == (
                f"called CheckBox.__init__ with args ({testobj},) {{'label': 'text'}}\n"
                "called CheckBox.GetId\n"
                "called AcceleratorEntry.__init__ with args () {'cmd': 'id'}\n"
                "called AcceleratorEntry.FromString with args ('Alt+O',)\n"
                "called checkbox.SetValue with args ('checkvalue',)\n"
                "called hori sizer.Add with args <item> ()\n")

    def test_disable_widget(self, monkeypatch, capsys):
        """unittest for ResultsGui.disabe_widget
        """
        widget =  mockwx.MockControl()
        assert capsys.readouterr().out == "called Control.__init__\n"
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.disable_widget(widget)
        assert capsys.readouterr().out == "called Control.Enable with arg False\n"

    def test_finalize_display(self, monkeypatch, capsys):
        """unittest for ResultsGui.finalize_display
        """
        monkeypatch.setattr(testee.wx.Dialog, 'SetAutoLayout', mockwx.MockDialog.SetAutoLayout)
        monkeypatch.setattr(testee.wx.Dialog, 'SetSizer', mockwx.MockDialog.SetSizer)
        monkeypatch.setattr(testee.wx.Dialog, 'Layout', mockwx.MockDialog.Layout)
        monkeypatch.setattr(testee.wx.Dialog, 'Show', mockwx.MockDialog.Show)
        monkeypatch.setattr(testee.wx.Dialog, 'SetFocus', mockwx.MockDialog.SetFocus)
        monkeypatch.setattr(testee.wx.Dialog, 'SetAcceleratorTable',
                            mockwx.MockDialog.SetAcceleratorTable)
        monkeypatch.setattr(testee.wx, 'AcceleratorTable', mockwx.MockAcceleratorTable)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.vsizer = mockwx.MockBoxSizer(testee.wx.VERTICAL)
        assert capsys.readouterr().out == "called BoxSizer.__init__ with args (8,)\n"
        testobj.accel_list = []
        testobj.finalize_display()
        assert capsys.readouterr().out == ("called dialog.SetAutoLayout with args (True,)\n"
                                           "called dialog.SetSizer with args (vert sizer,)\n"
                                           f"called vert sizer.Fit with args ({testobj},)\n"
                                           "called dialog.Layout with args ()\n"
                                           "called Dialog.Show\ncalled dialog.SetFocus\n")
        testobj.accel_list = ['accel', 'list']
        testobj.finalize_display()
        assert capsys.readouterr().out == (
                "called AcceleratorTable.__init__ with 2 AcceleratorEntries\n"
                "called dialog.SetAcceleratorTable\n"
                "called dialog.SetAutoLayout with args (True,)\n"
                "called dialog.SetSizer with args (vert sizer,)\n"
                f"called vert sizer.Fit with args ({testobj},)\n"
                "called dialog.Layout with args ()\n"
                "called Dialog.Show\ncalled dialog.SetFocus\n")

    def test_populate_list(self, monkeypatch, capsys):
        """unittest for ResultsGui.populate_list
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.master = types.SimpleNamespace(show_context=False)
        lijst = mockwx.MockListCtrl()
        assert capsys.readouterr().out == ("called ListCtrl.__init__ with args () {}\n")
        items = ['title']
        testobj.populate_list(lijst, items)
        assert capsys.readouterr().out == ("")
        items = ['title', ('line1', 'context1', 'text1'), ('line2', 'context2', 'text2')]
        testobj.populate_list(lijst, items)
        assert capsys.readouterr().out == (
                "called ListCtrl.InsertItem with args (9223372036854775807, 'line1')\n"
                "called ListCtrl.SetItem with args ('itemindex', 0, 'line1')\n"
                "called ListCtrl.SetItem with args ('itemindex', 1, 'text1')\n"
                "called ListCtrl.InsertItem with args (9223372036854775807, 'line2')\n"
                "called ListCtrl.SetItem with args ('itemindex', 0, 'line2')\n"
                "called ListCtrl.SetItem with args ('itemindex', 1, 'text2')\n")
        testobj.master.show_context = True
        testobj.populate_list(lijst, items)
        assert capsys.readouterr().out == (
                "called ListCtrl.InsertItem with args (9223372036854775807, 'line1')\n"
                "called ListCtrl.SetItem with args ('itemindex', 0, 'line1')\n"
                "called ListCtrl.SetItem with args ('itemindex', 1, 'context1')\n"
                "called ListCtrl.SetItem with args ('itemindex', 2, 'text1')\n"
                "called ListCtrl.InsertItem with args (9223372036854775807, 'line2')\n"
                "called ListCtrl.SetItem with args ('itemindex', 0, 'line2')\n"
                "called ListCtrl.SetItem with args ('itemindex', 1, 'context2')\n"
                "called ListCtrl.SetItem with args ('itemindex', 2, 'text2')\n")

    def test_clear_contents(self, monkeypatch, capsys):
        """unittest for ResultsGui.clear_contents
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.lijst = mockwx.MockListCtrl()
        assert capsys.readouterr().out == "called ListCtrl.__init__ with args () {}\n"
        testobj.clear_contents()
        assert capsys.readouterr().out == "called ListCtrl.DeleteAllItems with args ()\n"

    def test_go(self, monkeypatch, capsys):
        """unittest for ResultsGui.go
        """
        monkeypatch.setattr(testee.wx.Dialog, 'ShowModal', mockwx.MockDialog.ShowModal)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.go()
        assert capsys.readouterr().out == "called Dialog.ShowModal\n"

    def test_set_header(self, monkeypatch, capsys):
        """unittest for ResultsGui.set_header
        """
        widget = mockwx.MockStaticText()
        assert capsys.readouterr().out == "called StaticText.__init__ with args () {}\n"
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.set_header(widget, 'text')
        assert capsys.readouterr().out == "called StaticText.SetLabel with args ('text',) {}\n"

    def test_get_checkbox_value(self, monkeypatch, capsys):
        """unittest for ResultsGui.get_checkbox_value
        """
        widget = mockwx.MockCheckBox()
        assert capsys.readouterr().out == "called CheckBox.__init__ with args () {}\n"
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.get_checkbox_value(widget) == "value from checkbox"
        assert capsys.readouterr().out == ("called checkbox.GetValue\n")

    def test_get_savefile(self, monkeypatch, capsys):
        """unittest for ResultsGui.get_savefile
        """
        def mock_show(self):
            print('called FileDialog.ShowModal')
            return testee.wx.ID_CANCEL
        monkeypatch.setattr(testee.wx, 'FileDialog', mockwx.MockFileDialog)
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.get_savefile('title', 'dirname', 'fname', ()) == "dirname/filename"
        assert capsys.readouterr().out == (
                "called FileDialog.__init__ with args"
                " () {'message': 'Resultaat naar bestand kopieren',"
                " 'defaultDir': 'dirname', 'defaultFile': 'fname', 'wildcard': '', 'style': 2}\n"
                "called FileDialog.ShowModal\n"
                "called FileDialog.GetPath\n")
        monkeypatch.setattr(mockwx.MockFileDialog, 'ShowModal', mock_show)
        result = testobj.get_savefile('title', 'dirname', 'fname', (('x', 'xx'), ('y', 'yy')))
        assert result == ""
        assert capsys.readouterr().out == (
                "called FileDialog.__init__ with args"
                " () {'message': 'Resultaat naar bestand kopieren', 'defaultDir': 'dirname',"
                " 'defaultFile': 'fname', 'wildcard': 'xx (*x)|*x|yy (*y)|*y', 'style': 2}\n"
                "called FileDialog.ShowModal\n")

    def test_meld(self, monkeypatch, capsys):
        """unittest for ResultsGui.meld
        """
        monkeypatch.setattr(testee.wx, 'MessageBox', mockwx.mock_messagebox)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.meld('titel', 'message')
        assert capsys.readouterr().out == (
                f"called wx.MessageBox with args ('message', 'titel', 2052, {testobj})\n")

    def test_get_text_from_user(self, monkeypatch, capsys):
        """unittest for ResultsGui.get_text_from_user
        """
        monkeypatch.setattr(testee.wx, 'GetTextFromUser', mockwx.mock_get_text_from_user)
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.get_text_from_user('titel', 'message') == ("", False)
        assert capsys.readouterr().out == (
            f"called wx.GetTextFromUser with args ('message', 'titel') {{'parent': {testobj}}}\n")
        monkeypatch.setattr(testee.wx, 'GetTextFromUser', mockwx.mock_get_text_from_user_2)
        assert testobj.get_text_from_user('titel', 'message') == ("text from user", True)
        assert capsys.readouterr().out == (
            f"called wx.GetTextFromUser with args ('message', 'titel') {{'parent': {testobj}}}\n")

    def test_get_selection(self, monkeypatch, capsys):
        """unittest for ResultsGui.get_selection
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.lijst = mockwx.MockListCtrl()
        assert capsys.readouterr().out == "called ListCtrl.__init__ with args () {}\n"
        assert testobj.get_selection() == []
        assert capsys.readouterr().out == ("called ListCtrl.getFirstSelected\n")
        monkeypatch.setattr(mockwx.MockListCtrl, 'GetFirstSelected',
                            mockwx.MockListCtrl.GetFirstSelected_2)
        assert testobj.get_selection() == ['first item', 'next item']
        assert capsys.readouterr().out == ("called ListCtrl.getFirstSelected\n"
                                           "called ListCtrl.GetItem with args (first item,)\n"
                                           "called ListCtrl.getNextSelected\n"
                                           "called ListCtrl.GetItem with args (next item,)\n"
                                           "called ListCtrl.getNextSelected\n")

    def test_copy_to_clipboard(self, monkeypatch, capsys):
        """unittest for ResultsGui.copy_to_clipboard
        """
        def mock_open(self):
            print('called ClipBoard.Open')
            return False
        monkeypatch.setattr(testee.wx, 'TextDataObject', mockwx.MockTextDataObject)
        monkeypatch.setattr(testee.wx, 'Clipboard', mockwx.MockClipboard)
        monkeypatch.setattr(testee.wx, 'MessageBox', mockwx.mock_messagebox)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.copy_to_clipboard('text')
        assert capsys.readouterr().out == ("called TextDataObject.__init__\n"
                                           "called TextDataObject.SetText with arg 'text'\n"
                                           "called Clipboard.Get\n"
                                           "called Clipboard.Open\n"
                                           "called Clipboard.SetData with arg 'text'\n"
                                           "called Clipboard.Close\n")
        monkeypatch.setattr(mockwx.MockClipboard, 'Open', mock_open)
        testobj.copy_to_clipboard('text')
        assert capsys.readouterr().out == (
                "called TextDataObject.__init__\n"
                "called TextDataObject.SetText with arg 'text'\n"
                "called Clipboard.Get\ncalled ClipBoard.Open\n"
                "called wx.MessageBox with args ('Unable to open the clipboard', 'Error')\n")

    def test_to_result(self, monkeypatch, capsys):
        """unittest for ResultsGui.to_result
        """
        def mock_meld(*args):
            print('called Results.meld with args', args)
        def mock_goto(*args):
            print('called Afrift.goto_result with args', args)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.lijst = mockwx.MockListCtrl()
        assert capsys.readouterr().out == "called ListCtrl.__init__ with args () {}\n"
        testobj.meld = mock_meld
        testobj.master = types.SimpleNamespace(parent=types.SimpleNamespace(resulttitel='xxx'),
                                               goto_result=mock_goto)
        testobj.to_result('event')
        assert capsys.readouterr().out == (
                "called ListCtrl.getFirstSelected\n"
                "called Results.meld with args ('xxx', 'Select a result first')\n")
        monkeypatch.setattr(mockwx.MockListCtrl, 'GetFirstSelected',
                            mockwx.MockListCtrl.GetFirstSelected_2)
        testobj.to_result('event')
        assert capsys.readouterr().out == ("called ListCtrl.getFirstSelected\n"
                                           "called Afrift.goto_result with args (first item, -1)\n")

    def test_klaar(self, monkeypatch, capsys):
        """unittest for ResultsGui.klaar
        """
        monkeypatch.setattr(testee.wx.Dialog, 'EndModal', mockwx.MockDialog.EndModal)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.klaar()
        assert capsys.readouterr().out == ("called Dialog.EndModal with arg 0\n")
