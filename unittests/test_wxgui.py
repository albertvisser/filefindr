"""unittests for ./afrift/gui_wx.py
"""
from afrift import gui_wx as testee


class TestMyListCtrl:
    """unittest for gui_wx.MyListCtrl
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

    def _test_init(self, monkeypatch, capsys):
        """unittest for MyListCtrl.__init__
        """
        testobj = testee.MyListCtrl(parent, pos=wx.DefaultPosition, size=wx.DefaultSize, style=0)
        assert capsys.readouterr().out == ("")


class TestSelectNamesGui:
    """unittest for gui_wx.SelectNamesGui
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

    def _test_init(self, monkeypatch, capsys):
        """unittest for SelectNamesGui.__init__
        """
        testobj = testee.SelectNamesGui(parent, master)
        assert capsys.readouterr().out == ("")

    def _test_setup_screen(self, monkeypatch, capsys):
        """unittest for SelectNamesGui.setup_screen
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.setup_screen(captions) == "expected_result"
        assert capsys.readouterr().out == ("")

    def _test_go(self, monkeypatch, capsys):
        """unittest for SelectNamesGui.go
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.go() == "expected_result"
        assert capsys.readouterr().out == ("")

    def _test_select_all(self, monkeypatch, capsys):
        """unittest for SelectNamesGui.select_all
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.select_all(event) == "expected_result"
        assert capsys.readouterr().out == ("")

    def _test_invert_selection(self, monkeypatch, capsys):
        """unittest for SelectNamesGui.invert_selection
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.invert_selection(event) == "expected_result"
        assert capsys.readouterr().out == ("")

    def _test_klaar(self, monkeypatch, capsys):
        """unittest for SelectNamesGui.klaar
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.klaar(event) == "expected_result"
        assert capsys.readouterr().out == ("")


class TestResultsGui:
    """unittest for gui_wx.ResultsGui
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

    def _test_init(self, monkeypatch, capsys):
        """unittest for ResultsGui.__init__
        """
        testobj = testee.ResultsGui(parent, master)
        assert capsys.readouterr().out == ("")

    def _test_setup_screen(self, monkeypatch, capsys):
        """unittest for ResultsGui.setup_screen
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.setup_screen(captions) == "expected_result"
        assert capsys.readouterr().out == ("")

    def _test_populate_list(self, monkeypatch, capsys):
        """unittest for ResultsGui.populate_list
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.populate_list() == "expected_result"
        assert capsys.readouterr().out == ("")

    def _test_clear_contents(self, monkeypatch, capsys):
        """unittest for ResultsGui.clear_contents
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.clear_contents() == "expected_result"
        assert capsys.readouterr().out == ("")

    def _test_go(self, monkeypatch, capsys):
        """unittest for ResultsGui.go
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.go() == "expected_result"
        assert capsys.readouterr().out == ("")

    def _test_breekaf(self, monkeypatch, capsys):
        """unittest for ResultsGui.breekaf
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.breekaf(message, done=True) == "expected_result"
        assert capsys.readouterr().out == ("")

    def _test_set_header(self, monkeypatch, capsys):
        """unittest for ResultsGui.set_header
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.set_header(text) == "expected_result"
        assert capsys.readouterr().out == ("")

    def _test_get_pth(self, monkeypatch, capsys):
        """unittest for ResultsGui.get_pth
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.get_pth() == "expected_result"
        assert capsys.readouterr().out == ("")

    def _test_get_csv(self, monkeypatch, capsys):
        """unittest for ResultsGui.get_csv
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.get_csv() == "expected_result"
        assert capsys.readouterr().out == ("")

    def _test_get_sum(self, monkeypatch, capsys):
        """unittest for ResultsGui.get_sum
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.get_sum() == "expected_result"
        assert capsys.readouterr().out == ("")

    def _test_get_savefile(self, monkeypatch, capsys):
        """unittest for ResultsGui.get_savefile
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.get_savefile(fname, ext) == "expected_result"
        assert capsys.readouterr().out == ("")

    def _test_meld(self, monkeypatch, capsys):
        """unittest for ResultsGui.meld
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.meld(titel, message) == "expected_result"
        assert capsys.readouterr().out == ("")

    def _test_get_text_from_user(self, monkeypatch, capsys):
        """unittest for ResultsGui.get_text_from_user
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.get_text_from_user(titel, message) == "expected_result"
        assert capsys.readouterr().out == ("")

    def _test_get_selection(self, monkeypatch, capsys):
        """unittest for ResultsGui.get_selection
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.get_selection() == "expected_result"
        assert capsys.readouterr().out == ("")

    def _test_copy_to_clipboard(self, monkeypatch, capsys):
        """unittest for ResultsGui.copy_to_clipboard
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.copy_to_clipboard(text) == "expected_result"
        assert capsys.readouterr().out == ("")

    def _test_help(self, monkeypatch, capsys):
        """unittest for ResultsGui.help
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.help(event) == "expected_result"
        assert capsys.readouterr().out == ("")

    def _test_to_result(self, monkeypatch, capsys):
        """unittest for ResultsGui.to_result
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.to_result(event) == "expected_result"
        assert capsys.readouterr().out == ("")

    def _test_remember_settings(self, monkeypatch, capsys):
        """unittest for ResultsGui.remember_settings
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.remember_settings() == "expected_result"
        assert capsys.readouterr().out == ("")

    def _test_klaar(self, monkeypatch, capsys):
        """unittest for ResultsGui.klaar
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.klaar() == "expected_result"
        assert capsys.readouterr().out == ("")


class TestMainFrameGui:
    """unittest for gui_wx.MainFrameGui
    """
    def setup_testobj(self, monkeypatch, capsys):
        """stub for gui_wx.MainFrameGui object

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
        assert capsys.readouterr().out == 'called MainFrameGui.__init__ with args ()\n'
        return testobj

    def _test_init(self, monkeypatch, capsys):
        """unittest for MainFrameGui.__init__
        """
        testobj = testee.MainFrameGui(master)
        assert capsys.readouterr().out == ("")

    def _test_setup_screen(self, monkeypatch, capsys):
        """unittest for MainFrameGui.setup_screen
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.setup_screen(captions) == "expected_result"
        assert capsys.readouterr().out == ("")

    def _test_get_searchtext(self, monkeypatch, capsys):
        """unittest for MainFrameGui.get_searchtext
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.get_searchtext() == "expected_result"
        assert capsys.readouterr().out == ("")

    def _test_get_replace_args(self, monkeypatch, capsys):
        """unittest for MainFrameGui.get_replace_args
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.get_replace_args() == "expected_result"
        assert capsys.readouterr().out == ("")

    def _test_get_search_attr(self, monkeypatch, capsys):
        """unittest for MainFrameGui.get_search_attr
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.get_search_attr() == "expected_result"
        assert capsys.readouterr().out == ("")

    def _test_get_types_to_search(self, monkeypatch, capsys):
        """unittest for MainFrameGui.get_types_to_search
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.get_types_to_search() == "expected_result"
        assert capsys.readouterr().out == ("")

    def _test_get_dir_to_search(self, monkeypatch, capsys):
        """unittest for MainFrameGui.get_dir_to_search
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.get_dir_to_search() == "expected_result"
        assert capsys.readouterr().out == ("")

    def _test_get_subdirs_to_search(self, monkeypatch, capsys):
        """unittest for MainFrameGui.get_subdirs_to_search
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.get_subdirs_to_search() == "expected_result"
        assert capsys.readouterr().out == ("")

    def _test_get_backup(self, monkeypatch, capsys):
        """unittest for MainFrameGui.get_backup
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.get_backup() == "expected_result"
        assert capsys.readouterr().out == ("")

    def _test_get_ignore(self, monkeypatch, capsys):
        """unittest for MainFrameGui.get_ignore
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.get_ignore() == "expected_result"
        assert capsys.readouterr().out == ("")

    def _test_get_context(self, monkeypatch, capsys):
        """unittest for MainFrameGui.get_context
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.get_context() == "expected_result"
        assert capsys.readouterr().out == ("")

    def _test_error(self, monkeypatch, capsys):
        """unittest for MainFrameGui.error
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.error(titel, message) == "expected_result"
        assert capsys.readouterr().out == ("")

    def _test_meld(self, monkeypatch, capsys):
        """unittest for MainFrameGui.meld
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.meld(titel, message, additional=None) == "expected_result"
        assert capsys.readouterr().out == ("")

    def _test_add_item_to_searchlist(self, monkeypatch, capsys):
        """unittest for MainFrameGui.add_item_to_searchlist
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.add_item_to_searchlist(item) == "expected_result"
        assert capsys.readouterr().out == ("")

    def _test_get_skipdirs(self, monkeypatch, capsys):
        """unittest for MainFrameGui.get_skipdirs
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.get_skipdirs() == "expected_result"
        assert capsys.readouterr().out == ("")

    def _test_get_skipfiles(self, monkeypatch, capsys):
        """unittest for MainFrameGui.get_skipfiles
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.get_skipfiles() == "expected_result"
        assert capsys.readouterr().out == ("")

    def _test_doe(self, monkeypatch, capsys):
        """unittest for MainFrameGui.doe
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.doe(event) == "expected_result"
        assert capsys.readouterr().out == ("")

    def _test_set_waitcursor(self, monkeypatch, capsys):
        """unittest for MainFrameGui.set_waitcursor
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.set_waitcursor(value) == "expected_result"
        assert capsys.readouterr().out == ("")

    def _test_get_exit(self, monkeypatch, capsys):
        """unittest for MainFrameGui.get_exit
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.get_exit() == "expected_result"
        assert capsys.readouterr().out == ("")

    def _test_go(self, monkeypatch, capsys):
        """unittest for MainFrameGui.go
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.go() == "expected_result"
        assert capsys.readouterr().out == ("")

    def _test_einde(self, monkeypatch, capsys):
        """unittest for MainFrameGui.einde
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.einde(event=None) == "expected_result"
        assert capsys.readouterr().out == ("")

    def _test_add_combobox_row(self, monkeypatch, capsys):
        """unittest for MainFrameGui.add_combobox_row
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.add_combobox_row(label, choices, initial='', control=None) == "expected_result"
        assert capsys.readouterr().out == ("")

    def _test_add_checkbox_row(self, monkeypatch, capsys):
        """unittest for MainFrameGui.add_checkbox_row
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.add_checkbox_row(labeltext, value=None, indent=0, control=None) == "expected_result"
        assert capsys.readouterr().out == ("")

    def _test_check_loc(self, monkeypatch, capsys):
        """unittest for MainFrameGui.check_loc
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.check_loc(event) == "expected_result"
        assert capsys.readouterr().out == ("")

    def _test_zoekdir(self, monkeypatch, capsys):
        """unittest for MainFrameGui.zoekdir
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.zoekdir(event) == "expected_result"
        assert capsys.readouterr().out == ("")
