"AFRIFT PyQt5 versie"

import os
import sys
import subprocess
import PyQt5.QtWidgets as qtw
import PyQt5.QtGui as gui
import PyQt5.QtCore as core
from .findr_files import Finder
from .afrift_base import iconame, ABase, log
common_path_txt = 'De bestanden staan allemaal in of onder de directory "{}"'
TXTW = 200


class SelectNames(qtw.QDialog):
    """Tussenscherm om te verwerken files te kiezen"""

    def __init__(self, parent, files=True):
        self.dofiles = files
        self.parent = parent
        super().__init__(parent)
        self.setWindowTitle(self.parent.title + " - file list")
        self.setWindowIcon(gui.QIcon(iconame))
        vbox = qtw.QVBoxLayout()

        if files:
            text = "Selecteer de bestanden die je *niet* wilt verwerken"
            self.names = {str(x): x for x in self.parent.names}
        else:
            text = "Selecteer de directories die je *niet* wilt verwerken"
        txt = qtw.QLabel(text, self)
        hbox = qtw.QHBoxLayout()
        hbox.addWidget(txt)
        vbox.addLayout(hbox)
        self.sel_all = qtw.QCheckBox('Select/Unselect All', self)
        self.sel_all.clicked.connect(self.select_all)
        hbox = qtw.QHBoxLayout()
        hbox.addSpacing(10)
        hbox.addWidget(self.sel_all)
        self.flip_sel = qtw.QPushButton('Invert selection', self)
        self.flip_sel.clicked.connect(self.invert_selection)
        hbox.addStretch()
        hbox.addWidget(self.flip_sel)
        hbox.addSpacing(20)
        vbox.addLayout(hbox)

        frm = qtw.QFrame(self)
        fvbox = qtw.QVBoxLayout()
        self.checklist = []
        for item in self.parent.names:
            if files:
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

        b_can = qtw.QPushButton("&Terug", self)
        b_can.clicked.connect(self.reject)
        b_ok = qtw.QPushButton("&Klaar", self)
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

    def select_all(self):
        ""
        state = self.sel_all.isChecked()
        for cb in self.checklist:
            cb.setChecked(state)

    def invert_selection(self):
        ""
        for cb in self.checklist:
            cb.setChecked(not cb.isChecked())

    def accept(self):
        "dialoog afsluiten"
        dirs = []
        for cb in self.checklist:
            if cb.isChecked():
                if self.dofiles:
                    self.names.pop(cb.text())
                else:
                    dirs.append(cb.text())
        if self.dofiles:
            self.parent.names = [self.names[x] for x in sorted(self.names.keys())]
        else:
            self.parent.names = dirs
        super().accept()


class Results(qtw.QDialog):
    """Show results on screen
    """

    def __init__(self, parent, common_path=''):
        self.parent = parent
        self.common = common_path
        self.show_context = self.parent.p["context"]
        self.results = []
        titel = 'Regel' if self.parent.apptype == "single" else 'File/Regel'
        breedte = 50 if self.parent.apptype == "single" else 150
        super().__init__(parent)
        self.setWindowTitle(self.parent.resulttitel)
        self.setWindowIcon(gui.QIcon(iconame))
        vbox = qtw.QVBoxLayout()

        hbox = qtw.QHBoxLayout()
        label_txt = "{} ({} items)".format(self.parent.zoekvervang.rpt[0],
                                           len(self.parent.zoekvervang.rpt) - 1)
        if self.parent.apptype == "multi":
            label_txt += '\n' + common_path_txt.format(self.common.rstrip(os.sep))
        self.txt = qtw.QLabel(label_txt, self)
        hbox.addWidget(self.txt)
        vbox.addLayout(hbox)

        hbox = qtw.QHBoxLayout()
        self.lijst = qtw.QTableWidget(self)
        self.lijst.verticalHeader().setVisible(False)
        self.lijst.setGridStyle(core.Qt.NoPen)
        if self.show_context:
            self.lijst.setColumnCount(3)
            self.lijst.setColumnWidth(1, 200)
            self.lijst.setColumnWidth(2, 340)
            self.lijst.setHorizontalHeaderLabels((titel, 'Context', 'Tekst'))
        else:
            self.lijst.setColumnCount(2)
            self.lijst.setColumnWidth(1, 520)
            self.lijst.setHorizontalHeaderLabels((titel, 'Tekst'))
        self.lijst.setColumnWidth(0, breedte)
        self.lijst.horizontalHeader().setStretchLastSection(True)
        self.populate_list()
        self.lijst.cellDoubleClicked[int, int].connect(self.goto_result)
        act = qtw.QAction('Help', self)
        act.setShortcut('F1')
        act.triggered.connect(self.help)
        self.addAction(act)
        act = qtw.QAction('Goto Result', self)
        act.setShortcut('Ctrl+G')
        act.triggered.connect(self.to_result)
        self.addAction(act)
        hbox.addWidget(self.lijst)
        vbox.addLayout(hbox)

        hbox = qtw.QHBoxLayout()
        hbox.addStretch(1)
        btn = qtw.QPushButton("&Klaar", self)
        btn.clicked.connect(self.klaar)
        hbox.addWidget(btn)
        btn = qtw.QPushButton("&Repeat Search", self)
        btn.clicked.connect(self.refresh)
        if self.parent.p['vervang']:
            btn.setEnabled(False)
        hbox.addWidget(btn)
        btn = qtw.QPushButton("Copy to &File", self)
        btn.clicked.connect(self.kopie)
        hbox.addWidget(btn)
        btn = qtw.QPushButton("Copy to &Clipboard", self)
        btn.clicked.connect(self.to_clipboard)
        hbox.addWidget(btn)
        self.cb = qtw.QCheckBox("toon directorypad in uitvoer", self)
        if self.parent.apptype == "single":
            self.cb.setEnabled(False)
        hbox.addWidget(self.cb)
        self.cb2 = qtw.QCheckBox("comma-delimited", self)
        hbox.addWidget(self.cb2)
        hbox.addStretch(1)
        vbox.addLayout(hbox)

        self.setLayout(vbox)
        self.resize(574 + breedte, 480)

    def populate_list(self):
        """copy results to listbox
        """
        for ix, line in enumerate(self.parent.zoekvervang.rpt):
            if ix == 0:
                kop = line
            elif line != "":
                where, what = line.split(": ", 1)
                if self.parent.apptype == "single":
                    if "r. " in where:
                        where = where.split("r. ", 1)[1]
                    else:
                        where = ""
                if self.common:
                    where = where.replace(str(self.common), "")
                if self.show_context:
                    where, rest = where.rsplit(' (', 1)
                    context = rest.split(')')[0]
                self.lijst.insertRow(ix - 1)
                self.lijst.setRowHeight(ix - 1, 18)
                col = 0
                rowitem = []
                item = qtw.QTableWidgetItem(where)
                item.setFlags(core.Qt.ItemIsSelectable | core.Qt.ItemIsEnabled)
                self.lijst.setItem(ix - 1, col, item)
                rowitem.append(where)
                if self.show_context:
                    col += 1
                    item = qtw.QTableWidgetItem(context)
                    item.setFlags(core.Qt.ItemIsSelectable | core.Qt.ItemIsEnabled)
                    self.lijst.setItem(ix - 1, col, item)
                    rowitem.append(context)
                col += 1
                item = qtw.QTableWidgetItem(what)
                item.setFlags(core.Qt.ItemIsSelectable | core.Qt.ItemIsEnabled)
                self.lijst.setItem(ix - 1, col, item)
                rowitem.append(what)
                self.results.append(tuple(rowitem))
        self.results.insert(0, kop)

    def klaar(self):
        """finish dialog
        """
        qtw.QDialog.done(self, 0)

    def get_results(self):
        """apply switch to show complete path to results
        """
        toonpad = True if self.cb.isChecked() else False
        comma = True if self.cb2.isChecked() else False
        text = ["{}".format(self.results[0])]
        if self.parent.apptype == "multi" and not toonpad:
            text.append(common_path_txt.format(self.common) + '\n')
        if comma:
            import io
            import csv
            textbuf = io.StringIO()
            writer = csv.writer(textbuf, dialect='unix')
        for item in self.results[1:]:
            result = list(item)
            if toonpad and self.parent.apptype == 'multi':
                result[0] = self.common + result[0]
            if comma:
                writer.writerow(result)
            else:
                text.append(" ".join(result))
        if comma:
            text = textbuf.getvalue().split("\n")
            textbuf.close()
        return text

    def refresh(self):
        """repeat search and show new results
        """
        self.results = []
        self.lijst.clearContents()
        self.parent.zoekvervang.rpt = ["".join(self.parent.zoekvervang.specs)]
        self.parent.app.setOverrideCursor(gui.QCursor(core.Qt.WaitCursor))
        self.parent.zoekvervang.do_action(search_python=self.parent.p["context"])
        self.parent.app.restoreOverrideCursor()
        if len(self.parent.zoekvervang.rpt) == 1:
            qtw.QMessageBox.information(self, self.parent.resulttitel, "Niks gevonden")
            super().done(0)
        label_txt = "{} ({} items)".format(self.parent.zoekvervang.rpt[0],
                                           len(self.parent.zoekvervang.rpt) - 1)
        if self.parent.apptype == "multi":
            label_txt += '\n' + common_path_txt.format(self.common)
        self.txt.setText(label_txt)
        self.populate_list()

    def kopie(self):
        """callback for button 'Copy to file'
        """
        f_nam = self.parent.p["zoek"]
        for char in '/\\?%*:|"><.':
            if char in f_nam:
                f_nam = f_nam.replace(char, "~")
        f_nam = f_nam.join(("files containing ", ".txt"))
        dlg = qtw.QFileDialog.getSaveFileName(
            self,
            "Resultaat naar bestand kopieren",
            str(self.parent.hier / f_nam),
            "Text files (*.txt);;All files (*.*)", )
        if not dlg[0]:
            return
        with open(dlg[0], "w") as f_out:
            for line in self.get_results():
                f_out.write(line + "\n")

    def help(self):
        """show instructions
        """
        qtw.QMessageBox.information(
            self,
            'info',
            "Select a line and doubleclick or press Ctrl-G to open the indicated file\n"
            "at the indicated line (not in single file mode)")

    def to_clipboard(self):
        """callback for button 'Copy to clipboard'
        """
        clp = qtw.QApplication.clipboard()
        clp.setText('\n'.join(self.get_results()))

    def to_result(self):
        """show result in file
        """
        self.goto_result(self.lijst.currentRow(), self.lijst.currentColumn())

    def goto_result(self, row, col):
        """open the file containing the selected item
        """
        if self.parent.apptype == 'single':
            qtw.QMessageBox.information(self, 'ahem', 'Not in single file mode')
            return
        selected = self.results[row + 1]
        target, line = selected[0].split(' r. ')
        target = self.common + target
        prog, fileopt, lineopt = self.parent.editor_option
        subprocess.run([prog, fileopt.format(target), lineopt.format(line)])


class MainFrame(qtw.QWidget, ABase):
    """Hoofdscherm van de applicatie

    QMainWindow is een beetje overkill, daarom maar een QWidget
    """
    def __init__(self, **kwargs):
        self.app = qtw.QApplication(sys.argv)
        parent = None
        super().__init__(parent, **kwargs)

        self.setWindowTitle(self.title)
        self.setWindowIcon(gui.QIcon(iconame))

        self.grid = qtw.QGridLayout()
        self.row = -1
        self.vraag_zoek = self.add_combobox_row(
            'Zoek naar:',
            self._mru_items["zoek"])
        if self.p.get("zoek", ''):
            self.vraag_zoek.setEditText(self.p['zoek'])
        self.vraag_regex = self.add_checkbox_row(
            "regular expression (Python format)",
            self.extraopts['regex'])
        self.vraag_case = self.add_checkbox_row(
            "hoofd/kleine letters gelijk",
            self.p["case"])
        self.vraag_woord = self.add_checkbox_row(
            "hele woorden",
            self.p["woord"])

        self.vraag_verv = self.add_combobox_row(
            'Vervang door:',
            self._mru_items["verv"])
        if self.p.get("verv", ''):
            self.vraag_verv.setEditText(self.p['verv'])
        self.vraag_verv.completer().setCaseSensitivity(core.Qt.CaseSensitive)
        self.vraag_leeg = self.add_checkbox_row(
            "lege vervangtekst = weghalen",
            self._vervleeg)

        if self.apptype == "":
            initial = str(self.fnames[0]) if self.fnames else ''
            self.zoek = qtw.QPushButton("&Zoek")
            self.zoek.clicked.connect(self.zoekdir)
            self.vraag_dir = self.add_combobox_row(
                "In directory:",
                self._mru_items["dirs"],
                initial=initial,
                button=self.zoek)
            self.vraag_dir.setCompleter(None)
            self.vraag_dir.editTextChanged[str].connect(self.check_loc)

        elif self.apptype == "single":
            self.row += 1
            self.grid.addWidget(qtw.QLabel("In file/directory:"), self.row, 0)
            box = qtw.QHBoxLayout()
            box.addWidget(qtw.QLabel(str(self.fnames[0])))
            box.addStretch()
            self.grid.addLayout(box, self.row, 1)

        elif self.apptype == "multi":
            self.row += 1
            self.grid.addWidget(qtw.QLabel("In de volgende files/directories:"),
                                self.row, 0, 1, 2)
            self.row += 1
            self.lb = qtw.QListWidget(self)
            self.lb.insertItems(0, [str(x) for x in self.fnames])
            self.grid.addWidget(self.lb, self.row, 0, 1, 2)

        if self.apptype != "single" or self.fnames[0].is_dir():
            txt = "van geselecteerde directories " if self.apptype == "multi" else ""
            self.vraag_subs = self.add_checkbox_row(
                txt + "ook subdirectories doorzoeken",
                self.p["subdirs"])
            self.vraag_diepte = qtw.QSpinBox(self)
            self.vraag_diepte.setMinimum(-1)
            self.vraag_diepte.setValue(5)
            self.vraag_links = self.add_checkbox_row(
                "symlinks volgen - max. diepte (-1 is alles):",
                toggler=self.extraopts['follow_symlinks'],
                spinner=self.vraag_diepte)
            self.ask_skipdirs = self.add_checkbox_row(
                "selecteer (sub)directories om over te slaan",
                self.extraopts['select_subdirs'])
            self.ask_skipfiles = self.add_checkbox_row(
                "selecteer bestanden om over te slaan",
                self.extraopts['select_files'])
            self.vraag_types = self.add_combobox_row(
                "Alleen files van type:",
                self._mru_items["types"])
            if self.p.get("extlist", ''):
                self.vraag_types.setEditText(self.p['extlist'])

        self.vraag_context = self.add_checkbox_row(
            "context tonen (waar mogelijk, anders overslaan)", self.p["context"])
        self.vraag_backup = self.add_checkbox_row(
            "gewijzigd(e) bestand(en) backuppen", self._backup)
        self.vraag_exit = self.add_checkbox_row(
            "direct afsluiten na vervangen", self._exit_when_ready)

        self.row += 1
        hbox = qtw.QHBoxLayout()
        hbox.addStretch(1)
        self.b_doit = qtw.QPushButton('&Uitvoeren', self)
        self.b_doit.clicked.connect(self.doe)
        hbox.addWidget(self.b_doit)
        self.b_cancel = qtw.QPushButton('&Einde', self)
        self.b_cancel.clicked.connect(self.close)
        hbox.addWidget(self.b_cancel)
        hbox.addStretch(1)
        self.grid.addLayout(hbox, self.row, 0, 1, 2)

        vbox = qtw.QVBoxLayout()
        vbox.addLayout(self.grid)

        self.setLayout(vbox)
        self.vraag_zoek.setFocus()

        if self.extraopts['no_gui']:
            self.doe()
        else:
            self.show()
            sys.exit(self.app.exec_())

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

    def add_checkbox_row(self, text, toggler=None, spinner=None):
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
            self.readini(txt)
            self.vraag_zoek.clear()
            self.vraag_zoek.addItems(self._mru_items["zoek"])
            self.vraag_verv.clear()
            self.vraag_verv.addItems(self._mru_items["verv"])
            self.vraag_types.clear()
            self.vraag_types.addItems(self._mru_items["types"])
            ## self.vraag_dir.clear()
            ## self.vraag_dir.addItems(self._mru_items["dirs"])
            self.vraag_case.setChecked(self.p["case"])
            self.vraag_woord.setChecked(self.p["woord"])
            self.vraag_subs.setChecked(self.p["subdirs"])
            self.vraag_context.setChecked(self.p["context"])


    def keyPressEvent(self, event):
        """event handler voor toetsaanslagen"""
        if event.key() == core.Qt.Key_Escape:
            self.close()

    def determine_common(self):
        """determine common part of filenames
        """
        if self.apptype == 'single':
            test = self.fnames[0]
        elif self.apptype == 'multi':
            test = os.path.commonpath([str(x) for x in self.fnames])
            ## if test in self.fnames:
                ## pass
            ## else:
                ## while test and not os.path.exists(test):
                    ## test = test[:-1]
            # make sure common part is a directory
            if os.path.isfile(test):
                test = os.dirname(test) + os.sep
            else:
                test += os.sep
        else:
            test = self.p["pad"] + os.sep
        return test

    def doe(self):
        """Zoekactie uitvoeren en resultaatscherm tonen"""
        item = str(self.vraag_zoek.currentText())
        mld = self.checkzoek(item)
        if not mld:
            self.checkverv(str(self.vraag_verv.currentText()),
                           self.vraag_leeg.isChecked())
            self.checkattr(self.vraag_regex.isChecked(), self.vraag_case.isChecked(),
                           self.vraag_woord.isChecked())
            if self.apptype != "single" or self.fnames[0].is_dir():
                self.checktype(str(self.vraag_types.currentText()))
            if not self.apptype:
                mld = self.checkpath(str(self.vraag_dir.currentText()))
        if not mld:
            if self.apptype != "single" or self.fnames[0].is_dir():
                self.checksubs(self.vraag_subs.isChecked(),
                               self.vraag_links.isChecked(), self.vraag_diepte.value())
            elif self.apptype == "single" and self.fnames[0].is_symlink():
                self.p["follow_symlinks"] = True
        self.p["backup"] = self.vraag_backup.isChecked()
        self.p["context"] = self.vraag_context.isChecked()
        self.p["fallback_encoding"] = self._fallback_encoding

        if mld:
            qtw.QMessageBox.critical(self, self.fouttitel, mld, qtw.QMessageBox.Ok)
            return

        self.vraag_zoek.insertItem(0, item)
        if not self.extraopts['dont_save']:
            loc = self.p.get('pad', '') or str(self.p['filelist'][0].parent)
            self.schrijfini(loc)
        self.zoekvervang = Finder(**self.p)

        if not self.zoekvervang.ok:
            msg = '\n'.join(self.zoekvervang.rpt)
            qtw.QMessageBox.information(self, self.resulttitel, msg, qtw.QMessageBox.Ok)
            return

        if not self.zoekvervang.filenames:
            qtw.QMessageBox.information(self, self.resulttitel, "Geen bestanden gevonden",
                                        qtw.QMessageBox.Ok)
            return

        common_part = self.determine_common()
        if self.apptype == "single" or (
                len(self.fnames) == 1 and self.fnames[0].is_file()):
            pass
        else:
            go_on = self.ask_skipdirs.isChecked() or self.ask_skipfiles.isChecked()
            canceled = False
            while go_on:
                if self.ask_skipdirs.isChecked():
                    # eerste ronde: toon directories
                    if self.zoekvervang.dirnames:
                        self.names = sorted(self.zoekvervang.dirnames)
                        dlg = SelectNames(self, files=False).exec_()
                        if dlg == qtw.QDialog.Rejected:
                            canceled = True
                            break
                        # tweede ronde: toon de files die overblijven
                        fnames = self.zoekvervang.filenames[:]
                        for entry in fnames:
                            for name in self.names:
                                if str(entry).startswith(name + '/'):
                                    self.zoekvervang.filenames.remove(entry)
                                    break
                        if not self.ask_skipfiles.isChecked():
                            go_on = False
                if self.ask_skipfiles.isChecked():
                    self.names = sorted(self.zoekvervang.filenames, key=lambda x:
                        str(x))
                    dlg = SelectNames(self).exec_()
                    if dlg == qtw.QDialog.Rejected and not self.ask_skipdirs.isChecked():
                        canceled = True
                        break
                    if dlg == qtw.QDialog.Accepted:
                        self.zoekvervang.filenames = self.names
                        go_on = False
            if canceled:
                return

        self.app.setOverrideCursor(gui.QCursor(core.Qt.WaitCursor))
        self.zoekvervang.do_action(search_python=self.p["context"])
        self.app.restoreOverrideCursor()
        if len(self.zoekvervang.rpt) == 1:
            if self.extraopts['output_file']:
                print('No results')
            else:
                qtw.QMessageBox.information(self, self.resulttitel, "Niks gevonden",
                                            qtw.QMessageBox.Ok)
        else:
            dlg = Results(self, common_part)
            if self.extraopts['output_file']:
                with self.extraopts['output_file'] as f_out:
                    for line in dlg.get_results():
                        f_out.write(line + "\n")
            else:
                dlg.exec_()
        if (self.extraopts['no_gui'] and self.extraopts['output_file']) or (
                self.vraag_exit.isChecked() and self.p["vervang"] is not None):
            self.close()

    def zoekdir(self):
        """event handler voor 'zoek in directory'"""
        oupad = self.vraag_dir.currentText()
        dlg = qtw.QFileDialog.getExistingDirectory(self, "Choose a directory:", oupad)
        if dlg:
            self.vraag_dir.setEditText(dlg)
