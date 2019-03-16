"""AFRIFT PyQt5 specific classes
"""
import os
import sys
import PyQt5.QtWidgets as qtw
import PyQt5.QtGui as gui
import PyQt5.QtCore as core
TXTW = 200


class SelectNamesGui(qtw.QDialog):
    """dialog for selecting directories/files
    """
    def __init__(self, parent, root):
        self.root = root
        super().__init__(parent.gui)
        self.setWindowTitle(root.title)
        self.setWindowIcon(gui.QIcon(root.iconame))

    def setup_screen(self, captions):
        "build widgets"
        vbox = qtw.QVBoxLayout()

        txt = qtw.QLabel(captions['heading'], self)
        hbox = qtw.QHBoxLayout()
        hbox.addWidget(txt)
        vbox.addLayout(hbox)

        self.sel_all = qtw.QCheckBox(captions['sel_all'], self)
        self.sel_all.clicked.connect(self.select_all)
        hbox = qtw.QHBoxLayout()
        hbox.addSpacing(10)
        hbox.addWidget(self.sel_all)

        self.flip_sel = qtw.QPushButton(captions['invert'], self)
        self.flip_sel.clicked.connect(self.invert_selection)
        hbox.addStretch()
        hbox.addWidget(self.flip_sel)
        hbox.addSpacing(20)
        vbox.addLayout(hbox)

        frm = qtw.QFrame(self)
        fvbox = qtw.QVBoxLayout()
        self.checklist = []
        for item in self.root.parent.names:
            if self.root.dofiles:
                cb = qtw.QCheckBox(str(item), frm)
            else:
                cb = qtw.QCheckBox(item, frm)
            fhbox = qtw.QHBoxLayout()
            fhbox.addWidget(cb)
            self.checklist.append(cb)
            fvbox.addLayout(fhbox)
        frm.setLayout(fvbox)
        scrl = qtw.QScrollArea(self)
        scrl.setWidget(frm)
        hbox = qtw.QHBoxLayout()
        hbox.addWidget(scrl)
        vbox.addLayout(hbox)

        b_can = qtw.QPushButton(captions['exit'], self)
        b_can.clicked.connect(self.reject)
        b_ok = qtw.QPushButton(captions['execute'], self)
        b_ok.clicked.connect(self.accept)
        hboks = qtw.QHBoxLayout()
        hbox = qtw.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(b_can)
        hbox.addWidget(b_ok)
        hbox.addStretch(1)
        hboks.addLayout(hbox)
        vbox.addLayout(hboks)

        self.setLayout(vbox)

    def go(self):
        """show the dialog screen
        """
        result = self.exec_()
        if result == qtw.QDialog.Accepted:
            return True
        # elif result == qtw.QDialog.rejected:
        return False

    def select_all(self):
        """check or uncheck all boxes
        """
        state = self.sel_all.isChecked()
        for cb in self.checklist:
            cb.setChecked(state)

    def invert_selection(self):
        """check unchecked and uncheck checked boxes
        """
        for cb in self.checklist:
            cb.setChecked(not cb.isChecked())

    def accept(self):
        "dialoog afsluiten"
        dirs = []
        for cb in self.checklist:
            if cb.isChecked():
                if self.root.dofiles:
                    self.names.pop(cb.text())
                else:
                    dirs.append(cb.text())
        if self.root.dofiles:
            self.root.names = [self.root.names[x] for x in sorted(self.root.names.keys())]
        else:
            self.root.names = dirs
        super().accept()


class ResultsGui(qtw.QDialog):
    """results screen
    """
    def __init__(self, parent, root):
        self.root = root
        super().__init__(parent.gui)
        # qtw.QDialog.__init__(self)
        self.setWindowTitle(parent.resulttitel)
        self.setWindowIcon(gui.QIcon(root.iconame))

    def setup_screen(self, captions):
        "build widgets"
        breedte = 50 if self.root.parent.apptype == "single" else 150  # qt versie
        vbox = qtw.QVBoxLayout()
        hbox = qtw.QHBoxLayout()
        self.txt = qtw.QLabel(captions['heading'], self)
        hbox.addWidget(self.txt)
        vbox.addLayout(hbox)

        if not self.root.label_only:
            hbox = qtw.QHBoxLayout()
            self.lijst = qtw.QTableWidget(self)
            self.lijst.verticalHeader().setVisible(False)
            self.lijst.setGridStyle(core.Qt.NoPen)
            if self.root.show_context:
                self.lijst.setColumnCount(3)
                self.lijst.setColumnWidth(1, 200)
                self.lijst.setColumnWidth(2, 340)
                self.lijst.setHorizontalHeaderLabels((self.root.titel, captions['ctxt'],
                                                      captions['txt']))
            else:
                self.lijst.setColumnCount(2)
                self.lijst.setColumnWidth(1, 520)
                self.lijst.setHorizontalHeaderLabels((self.root.titel, captions['txt']))
            self.lijst.setColumnWidth(0, breedte)
            self.lijst.horizontalHeader().setStretchLastSection(True)

            self.populate_list()

            self.lijst.cellDoubleClicked[int, int].connect(self.root.goto_result)
            act = qtw.QAction(captions['hlp'], self)
            act.setShortcut('F1')
            act.triggered.connect(self.root.help)
            self.addAction(act)
            act = qtw.QAction(captions['rslt'], self)
            act.setShortcut('Ctrl+G')
            act.triggered.connect(self.root.goto_result)
            self.addAction(act)
            hbox.addWidget(self.lijst)
            vbox.addLayout(hbox)

        hbox = qtw.QHBoxLayout()
        hbox.addStretch(1)
        btn = qtw.QPushButton(captions['exit'], self)
        btn.clicked.connect(self.klaar)
        hbox.addWidget(btn)
        if not self.root.label_only:
            btn = qtw.QPushButton(captions['rpt'], self)
            btn.clicked.connect(self.root.refresh)
            if self.root.parent.p['vervang']:
                btn.setEnabled(False)
            hbox.addWidget(btn)
            btn = qtw.QPushButton(captions['cpy'], self)
            btn.clicked.connect(self.root.kopie)
            hbox.addWidget(btn)
            btn = qtw.QPushButton(captions['clp'], self)
            btn.clicked.connect(self.root.to_clipboard)
            hbox.addWidget(btn)
            gbox = qtw.QGridLayout()
            gbox.addWidget(qtw.QLabel(captions['fmt'], self), 0, 0)
            self.cb_path = qtw.QCheckBox(captions['pth'], self)
            if self.root.parent.apptype == "single":
                self.cb_path.setEnabled(False)
            gbox.addWidget(self.cb_path, 1, 0)
            self.cb_delim = qtw.QCheckBox(captions['dlm'], self)
            self.cb_smrz = qtw.QCheckBox(captions['sum'], self)
            gbox.addWidget(self.cb_delim, 0, 1)
            gbox.addWidget(self.cb_smrz, 1, 1)
            hbox.addLayout(gbox)
            hbox.addStretch(1)
        vbox.addLayout(hbox)

        self.setLayout(vbox)
        if not self.root.label_only:
            self.resize(574 + breedte, 480)

    def populate_list(self):
        """copy results to listbox
        """
        print('in populate_list:', self.root.results[0])
        for ix, result in enumerate(self.root.results[1:]):

            self.lijst.insertRow(ix)
            self.lijst.setRowHeight(ix, 18)
            col = 0
            item = qtw.QTableWidgetItem(result[0])
            item.setFlags(core.Qt.ItemIsSelectable | core.Qt.ItemIsEnabled)
            self.lijst.setItem(ix, col, item)

            if self.root.show_context:
                col += 1
                item = qtw.QTableWidgetItem(result[1])
                item.setFlags(core.Qt.ItemIsSelectable | core.Qt.ItemIsEnabled)
                self.lijst.setItem(ix, col, item)

            col += 1
            item = qtw.QTableWidgetItem(result[-1])
            item.setFlags(core.Qt.ItemIsSelectable | core.Qt.ItemIsEnabled)
            self.lijst.setItem(ix, col, item)

    def clear_contents(self):
        "remove all entries from list"
        self.lijst.clearContents()

    def go(self):
        """show the dialog screen
        """
        self.exec_()

    def breekaf(self, message):
        "show reason and end dialog"
        self.meld(self.root.resulttitel, message)
        super().done(0)

    def set_header(self, text):
        "set header for list"
        self.txt.setText(text)

    def get_pth(self):
        "get indicator to show path"
        return self.cb_path.isChecked()

    def get_csv(self):
        "get indicator to save as csv"
        return self.cb_delim.isChecked()

    def get_sum(self):
        "get indicator to show as summarized"
        return self.cb_smrz.isChecked()

    def get_savefile(self, fname, ext):
        """callback for button 'Copy to file'
        """
        if ext == '.csv':
            f_filter = 'Comma delimited files (*.csv)'
        elif ext == '.txt':
            f_filter = 'Text files (*.txt)'
        f_filter = "{};;All files (*.*)".format(f_filter)
        dlg = qtw.QFileDialog.getSaveFileName(self, "Resultaat naar bestand kopieren",
                                              str(self.root.parent.hier / fname), f_filter)
        return dlg[0]

    def meld(self, title, message):
        "show message"
        qtw.QMessageBox.information(self, title, message)

    def copy_to_clipboard(self, text):
        """callback for button 'Copy to clipboard'
        """
        clp = qtw.QApplication.clipboard()
        clp.setText(text)

    def to_result(self):
        """show result in file
        """
        self.root.goto_result(self.lijst.currentRow(), self.lijst.currentColumn())

    def klaar(self):
        """finish dialog
        """
        super().done(0)


class MainFrameGui(qtw.QWidget):
    """main screen
    """
    def __init__(self, root):
        self.root = root        # verwijzing naar MainFrame - voor als het nodig is
        self.app = qtw.QApplication(sys.argv)
        parent = None
        super().__init__(parent)
        print('MF after init:', self.root.p['context'])

    def setup_screen(self, captions):
        "set up screen for the various modes"
        self.grid = qtw.QGridLayout()
        self.row = -1
        self.vraag_zoek = self.add_combobox_row(captions['vraag_zoek'],
                                                self.root._mru_items["zoek"])
        if self.root.p.get("zoek", ''):
            self.vraag_zoek.setEditText(self.root.p['zoek'])
        self.vraag_regex = self.add_checkbox_row(captions['regex'], self.root.extraopts['regex'])
        self.vraag_case = self.add_checkbox_row(captions['case'], self.root.p["case"])
        self.vraag_woord = self.add_checkbox_row(captions['woord'], self.root.p["woord"])

        self.vraag_verv = self.add_combobox_row(captions['vraag_verv'],
                                                self.root._mru_items["verv"])
        if self.root.p.get("verv", ''):
            self.vraag_verv.setEditText(self.root.p['verv'])
        self.vraag_verv.completer().setCaseSensitivity(core.Qt.CaseSensitive)
        self.vraag_leeg = self.add_checkbox_row(captions['empty'], self.root._vervleeg)

        if self.root.apptype == "":
            initial = str(self.root.fnames[0]) if self.root.fnames else ''
            self.zoek = qtw.QPushButton(captions['zoek'])
            self.zoek.clicked.connect(self.zoekdir)
            self.vraag_dir = self.add_combobox_row(captions['in'], self.root._mru_items["dirs"],
                                                   initial=initial, button=self.zoek)
            self.vraag_dir.setCompleter(None)
            self.vraag_dir.editTextChanged[str].connect(self.check_loc)
        elif self.root.apptype == "single":
            self.row += 1
            self.grid.addWidget(qtw.QLabel(captions['in_s']), self.row, 0)
            box = qtw.QHBoxLayout()
            box.addWidget(qtw.QLabel(str(self.root.fnames[0])))
            box.addStretch()
            self.grid.addLayout(box, self.row, 1)
        elif self.root.apptype == "multi":
            self.row += 1
            self.grid.addWidget(qtw.QLabel(captions['in_m']), self.row, 0, 1, 2)
            self.row += 1
            self.lb = qtw.QListWidget(self)
            self.lb.insertItems(0, [str(x) for x in self.root.fnames])
            self.grid.addWidget(self.lb, self.row, 0, 1, 2)

        if self.root.apptype != "single" or self.root.fnames[0].is_dir():
            txt = captions['subs_m'] if self.root.apptype == "multi" else ""
            self.vraag_subs = self.add_checkbox_row(txt + captions['subs'], self.root.p["subdirs"])
            self.vraag_diepte = qtw.QSpinBox(self)
            self.vraag_diepte.setMinimum(-1)
            self.vraag_diepte.setValue(5)
            self.vraag_links = self.add_checkbox_row(captions['link'],
                                                     toggler=self.root.extraopts['follow_symlinks'],
                                                     spinner=self.vraag_diepte)
            self.ask_skipdirs = self.add_checkbox_row(captions['skipdirs'],
                                                      self.root.extraopts['select_subdirs'])
            self.ask_skipfiles = self.add_checkbox_row(captions['skipfiles'],
                                                       self.root.extraopts['select_files'])
            self.vraag_types = self.add_combobox_row(captions['ftypes'],
                                                     self.root._mru_items["types"])
            if self.root.p.get("extlist", ''):
                self.vraag_types.setEditText(self.root.p['extlist'])

        print(self.root.p['context'])
        self.vraag_context = self.add_checkbox_row(
            "context tonen (waar mogelijk, anders overslaan)", self.root.p["context"])
        self.vraag_uitsluit = self.add_checkbox_row(
            "commentaren en docstrings negeren", self.root.p["negeer"], indent=22)
        self.vraag_backup = self.add_checkbox_row(
            "gewijzigd(e) bestand(en) backuppen", self.root._backup)
        self.vraag_exit = self.add_checkbox_row(
            "direct afsluiten na vervangen", self.root._exit_when_ready)

        self.row += 1
        hbox = qtw.QHBoxLayout()
        hbox.addStretch(1)
        self.b_doit = qtw.QPushButton(captions['exec'], self)
        self.b_doit.clicked.connect(self.root.doe)
        hbox.addWidget(self.b_doit)
        self.b_cancel = qtw.QPushButton(captions['end'], self)
        self.b_cancel.clicked.connect(self.close)
        hbox.addWidget(self.b_cancel)
        hbox.addStretch(1)
        self.grid.addLayout(hbox, self.row, 0, 1, 2)

        vbox = qtw.QVBoxLayout()
        vbox.addLayout(self.grid)

        self.setLayout(vbox)
        self.vraag_zoek.setFocus()

    def get_searchtext(self):
        "get value of search field"
        return self.vraag_zoek.currentText()

    def get_replace_args(self):
        "get value of replace field"
        return self.vraag_verv.currentText(), self.vraag_leeg.isChecked()

    def get_search_attr(self):
        "read switches for type of search"
        return (self.vraag_regex.isChecked(), self.vraag_case.isChecked(),
                self.vraag_woord.isChecked())

    def get_types_to_search(self):
        "get filetypes to search"
        return self.vraag_types.currentText()

    def get_dir_to_search(self):
        "get directory to search"
        return self.vraag_dir.currentText()

    def get_subdirs_to_search(self):
        "get parameters for search in subdirectories"
        return (self.vraag_subs.isChecked(), self.vraag_links.isChecked(),
                self.vraag_diepte.value())

    def get_backup(self):
        "get backup indicator"
        return self.vraag_backup.isChecked()

    def get_ignore(self):
        "get indicator not to search in comments amd docstrings"
        return self.vraag_uitsluit.isChecked()

    def get_context(self):
        "get indicator to do context specific search"
        return self.vraag_context.isChecked()

    def error(self, titel, message):
        "show an error message"
        qtw.QMessageBox.critical(self, titel, message, qtw.QMessageBox.Ok)

    def meld(self, titel, message):
        "show an informational message"
        qtw.QMessageBox.information(self, titel, message, qtw.QMessageBox.Ok)

    def add_item_to_searchlist(self, item):
        "add string to list of items searched for"
        self.vraag_zoek.insertItem(0, item)

    def get_skipdirs(self):
        "get indicator to select directories to skip"
        return self.ask_skipdirs.isChecked()

    def get_skipfiles(self):
        "get indicator to select files to skip"
        return self.ask_skipfiles.isChecked()

    def set_waitcursor(self, value):
        """switch back and forth to a "busy" cursor
        """
        if value:
            self.app.setOverrideCursor(gui.QCursor(core.Qt.WaitCursor))
        else:
            self.app.restoreOverrideCursor()

    def get_exit(self):
        "get indicator to exot program when ready"
        self.vraag_exit.isChecked()

    def go(self):
        "show screen and handle events"
        self.show()
        sys.exit(self.app.exec_())

    def einde(self):
        """applicatie afsluiten"""
        self.close()

    def add_combobox_row(self, labeltext, itemlist, initial='', button=None):
        """create a row of widgets in the GUI
        """
        self.row += 1
        self.grid.addWidget(qtw.QLabel(labeltext), self.row, 0)
        cb = qtw.QComboBox(self)
        cb.setMaximumWidth(TXTW)
        cb.setMinimumWidth(TXTW)
        cb.insertItems(0, itemlist)
        cb.setEditable(True)
        cb.clearEditText()
        if initial:
            cb.setEditText(initial)
        if button:
            box = qtw.QHBoxLayout()
            box.addWidget(cb)
            box.addWidget(button)
            box.addStretch()
            self.grid.addLayout(box, self.row, 1)
        else:
            self.grid.addWidget(cb, self.row, 1)
        return cb

    def add_checkbox_row(self, text, toggler=None, spinner=None, indent=0):
        """create a row of widgets in the GUI
        """
        self.row += 1
        cb = qtw.QCheckBox(text, self)
        if toggler:
            cb.toggle()
        if spinner:
            box = qtw.QHBoxLayout()
            box.addWidget(cb)
            box.addWidget(spinner)
            box.addStretch()
            self.grid.addLayout(box, self.row, 1)
        elif indent:
            box = qtw.QHBoxLayout()
            box.addSpacing(indent)
            box.addWidget(cb)
            box.addStretch()
            self.grid.addLayout(box, self.row, 1)
        else:
            self.grid.addWidget(cb, self.row, 1)
        return cb

    def check_case(self, val):
        """autocompletion voor zoektekst in overeenstemming brengen met case
        indicator"""
        if val == core.Qt.Checked:
            new_value = core.Qt.CaseSensitive
        else:
            new_value = core.Qt.CaseInsensitive
        self.vraag_zoek.setAutoCompletionCaseSensitivity(new_value)

    def check_loc(self, txt):
        """update location to get settings from
        """
        if os.path.exists(txt) and not txt.endswith(os.path.sep):
            self.root.readini(txt)
            self.vraag_zoek.clear()
            self.vraag_zoek.addItems(self.root._mru_items["zoek"])
            self.vraag_verv.clear()
            self.vraag_verv.addItems(self.root._mru_items["verv"])
            self.vraag_types.clear()
            self.vraag_types.addItems(self.root._mru_items["types"])
            ## self.vraag_dir.clear()
            ## self.vraag_dir.addItems(self._mru_items["dirs"])
            self.vraag_case.setChecked(self.root.p["case"])
            self.vraag_woord.setChecked(self.root.p["woord"])
            self.vraag_subs.setChecked(self.root.p["subdirs"])
            self.vraag_context.setChecked(self.root.p["context"])

    def keyPressEvent(self, event):
        """event handler voor toetsaanslagen"""
        if event.key() == core.Qt.Key_Escape:
            self.close()

    def zoekdir(self):
        """event handler voor 'zoek in directory'"""
        oupad = self.vraag_dir.currentText()
        dlg = qtw.QFileDialog.getExistingDirectory(self, "Choose a directory:", oupad)
        if dlg:
            self.vraag_dir.setEditText(dlg)
