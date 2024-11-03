"""AFRIFT PyQt specific classes
"""
import os
import sys
import PyQt6.QtWidgets as qtw
import PyQt6.QtGui as gui
import PyQt6.QtCore as core
TXTW = 200


class SelectNamesGui(qtw.QDialog):
    """dialog for selecting directories/files
    """
    def __init__(self, parent, master):
        self.master = master
        super().__init__(parent.gui)
        self.setWindowTitle(master.title)
        self.setWindowIcon(gui.QIcon(master.iconame))

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
        for item in self.master.parent.names:
            cb = qtw.QCheckBox(str(item), frm) if self.master.do_files else qtw.QCheckBox(item, frm)
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
        result = self.exec()
        return result == qtw.QDialog.DialogCode.Accepted

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
                if self.master.do_files:
                    self.master.names.pop(cb.text())
                else:
                    dirs.append(cb.text())
        if self.master.do_files:
            self.master.names = [self.master.names[x] for x in sorted(self.master.names.keys())]
        else:
            self.master.names = dirs
        super().accept()


class ResultsGui(qtw.QDialog):
    """results screen
    """
    def __init__(self, parent, master):
        self.master = master
        super().__init__(parent.gui)
        # qtw.QDialog.__init__(self)
        # self.setWindowTitle(parent.resulttitel)
        self.setWindowTitle(self.master.parent.resulttitel)
        self.setWindowIcon(gui.QIcon(master.iconame))
        self.show_result_details = True  # wordt in master.__init__ op juiste waarde gezet

    def setup_screen(self, captions):
        "build widgets"
        def add_ampersand(text):
            "& teken tussenvoegen t.b.v. accelerator"
            return '&'.join((text[0], text[1:]))
        # breedte = 50 if self.master.parent.apptype == "single" else 150  # qt versie
        breedte = 50 if self.master.parent.apptype.startswith("single") else 150  # qt versie
        vbox = qtw.QVBoxLayout()
        hbox = qtw.QHBoxLayout()
        self.txt = qtw.QLabel(captions['heading'], self)
        hbox.addWidget(self.txt)
        vbox.addLayout(hbox)

        if self.show_result_details:
            hbox = qtw.QHBoxLayout()
            self.lijst = qtw.QTableWidget(self)
            self.lijst.verticalHeader().setVisible(False)
            self.lijst.setGridStyle(core.Qt.PenStyle.NoPen)
            if self.master.show_context:
                self.lijst.setColumnCount(3)
                self.lijst.setColumnWidth(1, 200)
                self.lijst.setColumnWidth(2, 340)
                self.lijst.setHorizontalHeaderLabels((self.master.titel, captions['ctxt'],
                                                      captions['txt']))
            else:
                self.lijst.setColumnCount(2)
                self.lijst.setColumnWidth(1, 520)
                self.lijst.setHorizontalHeaderLabels((self.master.titel, captions['txt']))
            self.lijst.setColumnWidth(0, breedte)
            self.lijst.horizontalHeader().setStretchLastSection(True)

            self.populate_list()

            self.lijst.cellDoubleClicked[int, int].connect(self.master.goto_result)
            act = gui.QAction(captions['hlp'], self)
            act.setShortcut('F1')
            act.triggered.connect(self.master.help)
            self.addAction(act)
            act = gui.QAction(captions['rslt'], self)
            act.setShortcut('Ctrl+G')
            act.triggered.connect(self.to_result)
            self.addAction(act)
            hbox.addWidget(self.lijst)
            vbox.addLayout(hbox)

        hbox = qtw.QHBoxLayout()
        hbox.addStretch(1)
        btn = qtw.QPushButton(captions['exit'], self)
        btn.clicked.connect(self.klaar)
        hbox.addWidget(btn)
        if self.show_result_details:
            vbox2 = qtw.QVBoxLayout()
            hbox2 = qtw.QHBoxLayout()
            btn = qtw.QPushButton(captions['rpt'], self)
            btn.clicked.connect(self.master.refresh)
            if self.master.parent.p['vervang']:
                btn.setEnabled(False)
            hbox2.addWidget(btn)
            btn = qtw.QPushButton(captions['cpy'], self)
            btn.clicked.connect(self.master.kopie)
            hbox2.addWidget(btn)
            btn = qtw.QPushButton(captions['clp'], self)
            btn.clicked.connect(self.master.to_clipboard)
            hbox2.addWidget(btn)
            hbox2.addStretch(1)
            vbox2.addLayout(hbox2)

            hbox2 = qtw.QHBoxLayout()
            btn = qtw.QPushButton(captions['alt'], self)
            btn.clicked.connect(self.master.zoek_anders)
            hbox2.addWidget(btn)
            btn = qtw.QPushButton(captions['sel'], self)
            btn.clicked.connect(self.master.vervang_in_sel)
            if self.master.parent.p['vervang']:
                btn.setEnabled(False)
            hbox2.addWidget(btn)
            btn = qtw.QPushButton(captions['all'], self)
            btn.clicked.connect(self.master.vervang_alles)
            if self.master.parent.p['vervang']:
                btn.setEnabled(False)
            hbox2.addWidget(btn)
            vbox2.addLayout(hbox2)

            hbox.addLayout(vbox2)
            gbox = qtw.QGridLayout()
            gbox.addWidget(qtw.QLabel(captions['fmt'], self), 0, 0)
            self.cb_path = qtw.QCheckBox('&' + captions['pth'], self)
            self.cb_path.setChecked(self.master.parent.outopts['full_path'])
            # if self.master.parent.apptype == "single":
            if self.master.parent.apptype == "single-file":
                self.cb_path.setEnabled(False)
            gbox.addWidget(self.cb_path, 1, 0)
            self.cb_delim = qtw.QCheckBox(add_ampersand(captions['dlm']), self)
            self.cb_delim.setChecked(self.master.parent.outopts['as_csv'])
            gbox.addWidget(self.cb_delim, 0, 1)
            self.cb_smrz = qtw.QCheckBox(add_ampersand(captions['sum']), self)
            self.cb_smrz.setChecked(self.master.parent.outopts['summarize'])
            gbox.addWidget(self.cb_smrz, 1, 1)
            hbox.addLayout(gbox)
            hbox.addStretch(1)
        vbox.addLayout(hbox)

        self.setLayout(vbox)
        if self.show_result_details:
            self.resize(574 + breedte, 488)

    def populate_list(self):
        """copy results to listbox
        """
        for ix, result in enumerate(self.master.results[1:]):
            self.lijst.insertRow(ix)
            self.lijst.setRowHeight(ix, 18)
            col = 0
            item = qtw.QTableWidgetItem(result[0])
            item.setToolTip(result[0])
            item.setFlags(core.Qt.ItemFlag.ItemIsSelectable | core.Qt.ItemFlag.ItemIsEnabled)
            self.lijst.setItem(ix, col, item)

            if self.master.show_context:
                col += 1
                item = qtw.QTableWidgetItem(result[1])
                item.setToolTip(result[1])
                item.setFlags(core.Qt.ItemFlag.ItemIsSelectable | core.Qt.ItemFlag.ItemIsEnabled)
                self.lijst.setItem(ix, col, item)

            col += 1
            item = qtw.QTableWidgetItem(result[-1])
            item.setToolTip(result[-1])
            item.setFlags(core.Qt.ItemFlag.ItemIsSelectable | core.Qt.ItemFlag.ItemIsEnabled)
            self.lijst.setItem(ix, col, item)

    def clear_contents(self):
        "remove all entries from list"
        self.lijst.clearContents()

    def go(self):
        """show the dialog screen
        """
        self.exec()

    def breekaf(self, message, done=True):
        "show reason and end dialog"
        self.meld(self.master.parent.resulttitel, message)
        if done:
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
        f_filter = f"{f_filter};;All files (*.*)"
        dlg = qtw.QFileDialog.getSaveFileName(self, "Resultaat naar bestand kopieren",
                                              str(self.master.parent.hier / fname), f_filter)
        return dlg[0]

    def meld(self, title, message):
        "show message"
        qtw.QMessageBox.information(self, title, message)

    def get_text_from_user(self, title, prompt):
        "pop up a dialog to get user input"
        return qtw.QInputDialog.getText(self, title, prompt)

    def get_selection(self):
        "get the selected items"
        # selected_rows = set([x.row() for x in self.lijst.selectedItems()])
        selected_rows = {x.row() for x in self.lijst.selectedItems()}
        selected_lines = [self.lijst.item(x, 0).text() for x in selected_rows]
        return selected_lines

    def copy_to_clipboard(self, text):
        """callback for button 'Copy to clipboard'
        """
        clp = qtw.QApplication.clipboard()
        clp.setText(text)

    def to_result(self):
        """show result in file
        """
        self.master.goto_result(self.lijst.currentRow(), self.lijst.currentColumn())

    def remember_settings(self):
        "save options to configuration"
        self.master.parent.outopts['full_path'] = self.get_pth()
        self.master.parent.outopts['as_csv'] = self.get_csv()
        self.master.parent.outopts['summarize'] = self.get_sum()
        self.master.parent.write_to_ini()

    def klaar(self):
        """finish dialog
        """
        super().done(0)


class MainFrameGui(qtw.QWidget):
    """main screen
    """
    def __init__(self, master):
        self.master = master        # verwijzing naar MainFrame - voor als het nodig is
        self.app = qtw.QApplication(sys.argv)
        parent = None
        super().__init__(parent)
        self.setWindowTitle(master.title)
        self.setWindowIcon(gui.QIcon(master.iconame))

    def setup_screen(self, captions):
        "set up screen for the various modes"
        self.grid = qtw.QGridLayout()
        self.row = -1
        self.vraag_zoek = self.add_combobox_row(captions['vraag_zoek'],
                                                self.master.mru_items["zoek"])
        if self.master.p.get("zoek", ''):
            self.vraag_zoek.setEditText(self.master.p['zoek'])
        self.vraag_regex = self.add_checkbox_row(captions['regex'], self.master.extraopts['regex'])
        self.vraag_case = self.add_checkbox_row(captions['case'], self.master.p["case"])
        self.vraag_woord = self.add_checkbox_row(captions['woord'], self.master.p["woord"])

        self.vraag_verv = self.add_combobox_row(captions['vraag_verv'],
                                                self.master.mru_items["verv"])
        if self.master.p.get("verv", ''):
            self.vraag_verv.setEditText(self.master.p['verv'])
        self.vraag_verv.completer().setCaseSensitivity(core.Qt.CaseSensitivity.CaseSensitive)
        self.vraag_leeg = self.add_checkbox_row(captions['empty'], self.master.always_replace)
        self.vraag_backup = self.add_checkbox_row(captions["backup"], self.master.maak_backups)
        self.vraag_exit = self.add_checkbox_row(captions['exit'], self.master.exit_when_ready)

        if self.master.apptype == "open":
            initial = str(self.master.p['filelist'][0]) if self.master.p['filelist'] else ''
            self.zoek = qtw.QPushButton(captions['zoek'])
            self.zoek.clicked.connect(self.zoekdir)
            self.vraag_dir = self.add_combobox_row(captions['in'], self.master.mru_items["dirs"],
                                                   initial=initial, button=self.zoek)
            self.vraag_dir.setCompleter(None)
            self.vraag_dir.editTextChanged[str].connect(self.check_loc)
        elif self.master.apptype.startswith("single"):
            self.row += 1
            self.grid.addWidget(qtw.QLabel(captions['in_s']), self.row, 0)
            box = qtw.QHBoxLayout()
            box.addWidget(qtw.QLabel(str(self.master.p['filelist'][0])))
            box.addStretch()
            self.grid.addLayout(box, self.row, 1)
        elif self.master.apptype == "multi":
            self.row += 1
            self.grid.addWidget(qtw.QLabel(captions['in_m']), self.row, 0, 1, 2)
            self.row += 1
            self.lb = qtw.QListWidget(self)
            self.lb.insertItems(0, [str(x) for x in self.master.p['filelist']])
            self.grid.addWidget(self.lb, self.row, 0, 1, 2)

        if self.master.apptype != "single-file":
            txt = captions['subs_m'] if self.master.apptype == "multi" else ""
            self.vraag_subs = self.add_checkbox_row(txt + captions['subs'], self.master.p["subdirs"])
            self.vraag_diepte = qtw.QSpinBox(self)
            self.vraag_diepte.setMinimum(-1)
            self.vraag_diepte.setValue(5)
            self.vraag_links = self.add_checkbox_row(captions['link'],
                                                     toggler=self.master.extraopts['follow_symlinks'],
                                                     spinner=self.vraag_diepte)
            self.ask_skipdirs = self.add_checkbox_row(captions['skipdirs'],
                                                      self.master.extraopts['select_subdirs'])
            self.ask_skipfiles = self.add_checkbox_row(captions['skipfiles'],
                                                       self.master.extraopts['select_files'])
            self.vraag_types = self.add_combobox_row(captions['ftypes'],
                                                     self.master.mru_items["types"])
            if self.master.p.get("extlist", ''):
                self.vraag_types.setEditText(self.master.p['extlist'])

        self.vraag_context = self.add_checkbox_row(captions["context"], self.master.p["context"])
        self.vraag_uitsluit = self.add_checkbox_row(captions["negeer"], self.master.p["negeer"],
                                                    indent=22)

        self.row += 1
        hbox = qtw.QHBoxLayout()
        hbox.addStretch(1)
        self.b_doit = qtw.QPushButton(captions['exec'], self)
        self.b_doit.clicked.connect(self.master.doe)
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
        qtw.QMessageBox.critical(self, titel, message, qtw.QMessageBox.StandardButton.Ok)

    def meld(self, titel, message, additional=None):
        "show an informational message"
        if additional:
            dlg = qtw.QMessageBox(qtw.QMessageBox.Icon.Information, titel, message,
                                  qtw.QMessageBox.StandardButton.Ok, parent=self)
            dlg.setDetailedText('\n'.join(additional))
            dlg.exec()
            dlg.close()
        else:
            qtw.QMessageBox.information(self, titel, message, qtw.QMessageBox.StandardButton.Ok)

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
            self.app.setOverrideCursor(gui.QCursor(core.Qt.CursorShape.WaitCursor))
        else:
            self.app.restoreOverrideCursor()

    def get_exit(self):
        "get indicator to exit program when ready"
        return self.vraag_exit.isChecked()

    def go(self):
        "show screen and handle events"
        self.show()
        sys.exit(self.app.exec())

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
        new_value = (core.Qt.CaseSensitivity.CaseSensitive if val == core.Qt.CheckState.Checked
                     else core.Qt.CaseSensitivity.CaseInsensitive)
        self.vraag_zoek.setAutoCompletionCaseSensitivity(new_value)

    def check_loc(self, txt):
        """update location to get settings from
        """
        if os.path.exists(txt) and not txt.endswith(os.path.sep):
            self.master.read_from_ini(txt)
            self.vraag_zoek.clear()
            self.vraag_zoek.addItems(self.master.mru_items["zoek"])
            self.vraag_verv.clear()
            self.vraag_verv.addItems(self.master.mru_items["verv"])
            self.vraag_types.clear()
            self.vraag_types.addItems(self.master.mru_items["types"])
            ## self.vraag_dir.clear()
            ## self.vraag_dir.addItems(self.master.mru_items["dirs"])
            self.vraag_case.setChecked(self.master.p["case"])
            self.vraag_woord.setChecked(self.master.p["woord"])
            self.vraag_subs.setChecked(self.master.p["subdirs"])
            self.vraag_context.setChecked(self.master.p["context"])

    def keyPressEvent(self, event):
        """event handler voor toetsaanslagen"""
        if event.key() == core.Qt.Key.Key_Escape:
            self.close()

    def zoekdir(self):
        """event handler voor 'zoek in directory'"""
        oupad = self.vraag_dir.currentText()
        dlg = qtw.QFileDialog.getExistingDirectory(self, "Choose a directory:", oupad)
        if dlg:
            self.vraag_dir.setEditText(dlg)
