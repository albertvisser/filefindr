#! /usr/bin/env python
"AFRIFT PyQt versie"

import os
import sys
import PyQt4.QtGui as gui
import PyQt4.QtCore as core
from .findr_files import Finder
from .afrift_base import iconame, ABase, log
common_path_txt = 'De bestanden staan allemaal in of onder de directory "{}"'
TXTW = 200

class SelectNames(gui.QDialog):
    """Tussenscherm om te verwerken files te kiezen"""

    def __init__(self, parent, files=True):
        self.dofiles = files
        self.parent = parent
        gui.QDialog.__init__(self, parent)
        self.setWindowTitle(self.parent.title + " - file list")
        self.setWindowIcon(gui.QIcon(iconame))
        vbox = gui.QVBoxLayout()

        if files:
            text = "Selecteer de bestanden die je *niet* wilt verwerken"
        else:
            text = "Selecteer de directories die je *niet* wilt verwerken"
        txt = gui.QLabel(text, self)
        hbox = gui.QHBoxLayout()
        hbox.addWidget(txt)
        vbox.addLayout(hbox)
        self.sel_all = gui.QCheckBox('Select/Unselect All', self)
        self.sel_all.clicked.connect(self.select_all)
        hbox = gui.QHBoxLayout()
        hbox.addSpacing(10)
        hbox.addWidget(self.sel_all)
        ## vbox.addLayout(hbox)
        self.flip_sel = gui.QPushButton('Invert selection', self)
        self.flip_sel.clicked.connect(self.invert_selection)
        ## hbox = gui.QHBoxLayout()
        ## hbox.addSpacing(10)
        hbox.addStretch()
        hbox.addWidget(self.flip_sel)
        vbox.addLayout(hbox)

        frm = gui.QFrame(self)
        fvbox = gui.QVBoxLayout()
        self.checklist = []
        for item in self.parent.names:
            cb = gui.QCheckBox(item, frm)
            fhbox = gui.QHBoxLayout()
            fhbox.addWidget(cb)
            self.checklist.append(cb)
            fvbox.addLayout(fhbox)
        frm.setLayout(fvbox)
        scrl = gui.QScrollArea(self)
        scrl.setWidget(frm)
        hbox = gui.QHBoxLayout()
        hbox.addWidget(scrl)
        vbox.addLayout(hbox)

        b1 = gui.QPushButton("&Klaar", self)
        b1.clicked.connect(self.klaar)
        hboks = gui.QHBoxLayout()
        hbox = gui.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(b1)
        hbox.addStretch(1)
        hboks.addLayout(hbox)
        vbox.addLayout(hboks)

        self.setLayout(vbox)
        self.exec_()

    def select_all(self):
        state = self.sel_all.isChecked()
        for cb in self.checklist:
            cb.setChecked(state)

    def invert_selection(self):
        for cb in self.checklist:
            cb.setChecked(not cb.isChecked())

    def klaar(self):
        "dialoog afsluiten"
        dirs = []
        for cb in self.checklist:
            if cb.isChecked():
                if self.dofiles:
                    self.parent.names.remove(cb.text())
                else:
                    dirs.append(cb.text())
        if not self.dofiles:
            self.parent.names = dirs
        gui.QDialog.done(self, 0)

class Results(gui.QDialog):
    """Show results on screen
    """

    def __init__(self, parent, common_path=''):
        self.parent = parent
        self.common = common_path
        self.show_context = self.parent.p["context"]
        self.results = []
        titel = 'Regel' if self.parent.apptype == "single" else 'File/Regel'
        breedte = 50 if self.parent.apptype == "single" else 150
        ## if self.parent.apptype == "":
            ## breedte, titel = 300, 'File/Regel'
        ## elif self.parent.apptype == "single":
            ## breedte, titel = 50, 'Regel'
        ## elif self.parent.apptype == "multi":
            ## breedte, titel = 200, 'File/Regel'
        gui.QDialog.__init__(self, parent)
        self.setWindowTitle(self.parent.resulttitel)
        self.setWindowIcon(gui.QIcon(iconame))
        vbox = gui.QVBoxLayout()

        hbox = gui.QHBoxLayout()
        label_txt = "{0} ({1} items)".format(self.parent.zoekvervang.rpt[0],
                len(self.parent.zoekvervang.rpt) - 1)
        if self.parent.apptype == "multi":
            label_txt += '\n' + common_path_txt.format(self.common)
        self.txt = gui.QLabel(label_txt, self)
        hbox.addWidget(self.txt)
        vbox.addLayout(hbox)

        hbox = gui.QHBoxLayout()
        self.lijst = gui.QTableWidget(self)
        self.lijst.verticalHeader().setVisible(False)
        ## self.lijst.setShowGrid(False) # hierbij komt de tweede kolom top- ipv middle-aligned
        self.lijst.setGridStyle(core.Qt.NoPen)# hierbij niet
        if self.show_context:
            self.lijst.setColumnCount(3)
            self.lijst.setColumnWidth(1,200)
            self.lijst.setColumnWidth(2,340)
            self.lijst.setHorizontalHeaderLabels((titel, 'Context', 'Tekst'))
        else:
            self.lijst.setColumnCount(2)
            self.lijst.setColumnWidth(1, 520)
            self.lijst.setHorizontalHeaderLabels((titel, 'Tekst'))
        self.lijst.setColumnWidth(0, breedte)
        self.lijst.horizontalHeader().setStretchLastSection(True)
        self.populate_list()
        ## self.lijst.resizeRowsToContents()
        hbox.addWidget(self.lijst)
        vbox.addLayout(hbox)

        hbox = gui.QHBoxLayout()
        hbox.addStretch(1)
        btn = gui.QPushButton("&Klaar", self)
        btn.clicked.connect(self.klaar)
        hbox.addWidget(btn)
        btn = gui.QPushButton("&Repeat Search", self)
        btn.clicked.connect(self.refresh)
        if self.parent.p['vervang']:
            btn.setEnabled(False)
        hbox.addWidget(btn)
        btn = gui.QPushButton("Copy to &File", self)
        btn.clicked.connect( self.kopie)
        hbox.addWidget(btn)
        btn = gui.QPushButton("Copy to &Clipboard", self)
        btn.clicked.connect(self.to_clipboard)
        hbox.addWidget(btn)
        self.cb = gui.QCheckBox("toon directorypad in uitvoer", self)
        if self.parent.apptype == "single":
            self.cb.setEnabled(False)
        hbox.addWidget(self.cb)
        self.cb2 = gui.QCheckBox("comma-delimited", self)
        hbox.addWidget(self.cb2)
        hbox.addStretch(1)
        vbox.addLayout(hbox)

        self.setLayout(vbox)
        self.resize(574 + breedte, 480)
        self.exec_()

    def populate_list(self):
        """copy results to listbox
        """
        ## headers = []
        for ix, line in enumerate(self.parent.zoekvervang.rpt):
            if ix == 0:
                kop = line
            elif line != "":
                where, what = line.split(": ", 1)
                if self.parent.apptype == "single":
                    if "r. " in where:
                        fname, lineno = where.split("r. ", 1)
                        ## if ix == 1:
                            ## kop += " in {0}".format(fname)
                        where = lineno
                    else:
                        where = ""
                if self.common:
                    where = where.replace(self.common, "")
                if self.show_context:
                    where, rest = where.split(' (')
                    context = rest.split(')')[0]
                self.lijst.insertRow(ix - 1)
                self.lijst.setRowHeight(ix - 1, 18)
                ## headers.append('')
                col = 0
                rowitem = []
                item = gui.QTableWidgetItem(where)
                item.setFlags(core.Qt.ItemIsSelectable | core.Qt.ItemIsEnabled)
                self.lijst.setItem(ix - 1, col, item)
                rowitem.append(where)
                if self.show_context:
                    col += 1
                    item = gui.QTableWidgetItem(context)
                    item.setFlags(core.Qt.ItemIsSelectable | core.Qt.ItemIsEnabled)
                    self.lijst.setItem(ix - 1, col, item)
                    rowitem.append(context)
                col += 1
                item = gui.QTableWidgetItem(what)
                item.setFlags(core.Qt.ItemIsSelectable | core.Qt.ItemIsEnabled)
                self.lijst.setItem(ix - 1, col, item)
                rowitem.append(what)
                self.results.append(tuple(rowitem))
        ## self.lijst.setVerticalHeaderLabels(headers)
        self.results.insert(0, kop)

    def klaar(self):
        """finish dialog
        """
        gui.QDialog.done(self, 0)

    def get_results(self): # , toonpad):
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
            elif not toonpad and self.parent.apptype != 'multi':
                result[0] = result[0].split(os.sep)[-1]
            if comma:
                writer.writerow(result)
            else:
                text.append(" ".join(result))
        if comma:
            text = textbuf.getvalue().split("\n")
            textbuf.close()
        return text

    def refresh(self):
        self.results = []
        self.lijst.clearContents()
        self.parent.zoekvervang.rpt = ["".join(self.parent.zoekvervang.specs)]
        self.parent.zoekvervang.do_action(search_python=self.parent.p["context"])
        if len(self.parent.zoekvervang.rpt) == 1:
            gui.QMessageBox.information(self, self.resulttitel, "Niks gevonden",
                gui.QMessageBox.Ok)
            gui.QDialog.done(self, 0)
        label_txt = "{0} ({1} items)".format(self.parent.zoekvervang.rpt[0],
                len(self.parent.zoekvervang.rpt) - 1)
        if self.parent.apptype == "multi":
            label_txt += '\n' + common_path_txt.format(self.common)
        self.txt.setText(label_txt)
        self.populate_list()

    def kopie(self):
        """callback for button 'Copy to file'
        """
        f = self.parent.p["zoek"]
        for char in '/\\?%*:|"><.':
            if char in f:
                f = f.replace(char, "~")
        f =  f.join(("files containing ", ".txt"))
        dlg = gui.QFileDialog.getSaveFileName(self,
            "Resultaat naar bestand kopieren",
            os.path.join(self.parent.hier,f),
            "Text files (*.txt);;All files (*.*)",
            )
        if not dlg:
            return
        with open(dlg, "w") as f_out:
            for line in self.get_results(): # toonpad):
                f_out.write(line + "\n")

    def to_clipboard(self):
        """callback for button 'Copy to clipboard'
        """
        clp = gui.QApplication.clipboard()
        clp.setText('\n'.join(self.get_results())) # toonpad)))

class MainFrame(gui.QWidget, ABase):
    """Hoofdscherm van de applicatie

    QMainWindow is een beetje overkill, daarom maar een QWidget
    """
    def __init__(self, parent = None, apptype = "", fnaam = ""):
        app = gui.QApplication(sys.argv)
        ABase.__init__(self, parent, apptype, fnaam)
        gui.QWidget.__init__(self, parent)

        self.setWindowTitle(self.title)
        self.setWindowIcon(gui.QIcon(iconame))

        self.grid = gui.QGridLayout()
        self.row = -1
        self.vraag_zoek = self.add_combobox_row('Zoek naar:',
            self._mru_items["zoek"])
        self.vraag_regex = self.add_checkbox_row("regular expression "
            "(Python format)")
        self.vraag_case = self.add_checkbox_row("hoofd/kleine letters gelijk",
            self.p["case"])
        self.vraag_woord = self.add_checkbox_row("hele woorden", self.p["woord"])

        self.vraag_verv = self.add_combobox_row('Vervang door:',
            self._mru_items["verv"])
        self.vraag_verv.setAutoCompletionCaseSensitivity(core.Qt.CaseSensitive)
        self.vraag_leeg = self.add_checkbox_row("lege vervangtekst = weghalen",
            self._vervleeg)

        if self.apptype == "":
            initial = self.fnames[0] if self.fnames else ''
            self.zoek = gui.QPushButton("&Zoek")
            self.zoek.clicked.connect(self.zoekdir)
            self.vraag_dir = self.add_combobox_row("In directory:",
                self._mru_items["dirs"], initial=initial, button=self.zoek)

        elif self.apptype == "single":
            self.row += 1
            self.grid.addWidget(gui.QLabel("In file/directory:"), self.row, 0)
            box = gui.QHBoxLayout()
            box.addWidget(gui.QLabel(self.fnames[0]))
            box.addStretch()
            self.grid.addLayout(box, self.row, 1)

        elif self.apptype == "multi":
            self.row += 1
            self.grid.addWidget(gui.QLabel("In de volgende files/directories:"),
                self.row, 0, 1, 2)
            self.row += 1
            self.lb = gui.QListWidget(self)
            self.lb.insertItems(0, self.fnames)
            self.grid.addWidget(self.lb, self.row, 0, 1, 2)

        if self.apptype != "single" or os.path.isdir(self.fnames[0]):
            t = "van geselecteerde directories " if self.apptype == "multi" else ""
            self.vraag_subs = self.add_checkbox_row(t + "ook subdirectories "
                "doorzoeken", self.p["subdirs"])
            self.vraag_diepte = gui.QSpinBox(self)
            self.vraag_diepte.setMinimum(-1)
            self.vraag_diepte.setValue(5)
            self.vraag_links = self.add_checkbox_row("symlinks volgen - max. diepte "
                "(-1 is alles):", spinner=self.vraag_diepte)
            self.ask_skipdirs = self.add_checkbox_row("selecteer (sub)directories "
                "om over te slaan")
            self.ask_skipfiles = self.add_checkbox_row("selecteer bestanden "
                "om over te slaan")
            self.vraag_types = self.add_combobox_row("Alleen files van type:",
                self._mru_items["types"])

        self.vraag_context = self.add_checkbox_row("context tonen (waar mogelijk, "
            "anders overslaan)", self.p["context"])
        self.vraag_backup = self.add_checkbox_row("gewijzigd(e) bestand(en) "
            "backuppen", self._backup)
        self.vraag_exit = self.add_checkbox_row("direct afsluiten na vervangen",
            self._exit_when_ready)

        self.row += 1
        hbox = gui.QHBoxLayout()
        hbox.addStretch(1)
        self.b_doit = gui.QPushButton('&Uitvoeren', self)
        self.b_doit.clicked.connect(self.doe)
        hbox.addWidget(self.b_doit)
        self.b_cancel = gui.QPushButton('&Einde', self)
        self.b_cancel.clicked.connect(self.close)
        hbox.addWidget(self.b_cancel)
        hbox.addStretch(1)
        self.grid.addLayout(hbox, self.row, 0, 1, 2)

        vbox = gui.QVBoxLayout()
        vbox.addLayout(self.grid)

        self.setLayout(vbox)
        ## self.resize(250, 150)
        self.vraag_zoek.setFocus()

        self.show()
        sys.exit(app.exec_())

    def add_combobox_row(self, labeltext, itemlist, initial='', button=None):
        self.row += 1
        self.grid.addWidget(gui.QLabel(labeltext), self.row, 0)
        cb = gui.QComboBox(self)
        cb.setMaximumWidth(TXTW)
        cb.setMinimumWidth(TXTW)
        cb.insertItems(0, itemlist)
        cb.setEditable(True)
        cb.clearEditText()
        if initial:
            cb.setEditText(initial)
        if button:
            box = gui.QHBoxLayout()
            box.addWidget(cb)
            box.addWidget(button)
            box.addStretch()
            self.grid.addLayout(box, self.row, 1)
        else:
            self.grid.addWidget(cb, self.row, 1)
        return cb

    def add_checkbox_row(self, text, toggler=None, spinner=None):
        self.row += 1
        cb = gui.QCheckBox(text, self)
        if toggler:
            cb.toggle()
        if spinner:
            box = gui.QHBoxLayout()
            box.addWidget(cb)
            box.addWidget(spinner)
            box.addStretch()
            self.grid.addLayout(box, self.row, 1)
        else:
            self.grid.addWidget(cb, self.row, 1)
        return cb

    def check_case(self, int):
        """autocompletion voor zoektekst in overeenstemming brengen met case
        indicator"""
        if int == core.Qt.Checked:
            new_value = core.Qt.CaseSensitive
        else:
            new_value = core.Qt.CaseInSensitive
        self.vraag_zoek.setAutoCompletionCaseSensitivity(new_value)

    def keyPressEvent(self, event):
        """event handler voor toetsaanslagen"""
        if event.key() == core.Qt.Key_Escape:
            self.close()

    def determine_common(self):
        if self.apptype == 'single':
            test = self.fnames[0]
        elif self.apptype == 'multi':
            test = os.path.commonprefix(self.fnames)
            if test in self.fnames:
                pass
            else:
                while test and not os.path.exists(test):
                    test = test[:-1]
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
            if self.apptype != "single" or os.path.isdir(self.fnames[0]):
                self.checktype(str(self.vraag_types.currentText()))
            if not self.apptype:
                mld = self.checkpath(str(self.vraag_dir.currentText()))
        if not mld:
            if self.apptype != "single" or os.path.isdir(self.fnames[0]):
                self.checksubs(self.vraag_subs.isChecked(),
                    self.vraag_links.isChecked(), self.vraag_diepte.value())
            elif self.apptype == "single" and os.path.islink(self.fnames[0]):
                self.p["follow_symlinks"] = True
        self.p["backup"] = self.vraag_backup.isChecked()
        self.p["context"] = self.vraag_context.isChecked()
        self.p["fallback_encoding"] = self._fallback_encoding

        if mld:
            gui.QMessageBox.critical(self, self.fouttitel, mld, gui.QMessageBox.Ok)
            return

        self.vraag_zoek.insertItem(0, item)
        self.schrijfini()
        self.zoekvervang = Finder(**self.p)
        if not self.zoekvervang.ok:
            msg = '\n'.join(self.zoekvervang.rpt)
            gui.QMessageBox.information(self, self.resulttitel,
                msg, gui.QMessageBox.Ok)
            return

        if not self.zoekvervang.filenames:
            gui.QMessageBox.information(self, self.resulttitel,
                "Geen bestanden gevonden", gui.QMessageBox.Ok)
            return

        common_part = self.determine_common()
        if self.apptype == "single" or (
                len(self.fnames) == 1 and os.path.isfile(self.fnames[0])):
            pass
        else:
            ## print(self.skipdirs_overslaan, self.skipfiles_overslaan)
            if self.ask_skipdirs.isChecked():
                # eerste ronde: toon directories
                if self.zoekvervang.dirnames:
                    self.names = sorted(self.zoekvervang.dirnames)
                    dlg = SelectNames(self, files=False)
                    # tweede ronde: toon de files die overblijven
                    fnames = self.zoekvervang.filenames[:]
                    for fname in fnames:
                        for name in self.names:
                            if fname.startswith(name + '/'):
                                self.zoekvervang.filenames.remove(fname)
                                break
                log(self.zoekvervang.filenames)
            if self.ask_skipfiles.isChecked():
                self.names = self.zoekvervang.filenames
                dlg = SelectNames(self)
                self.zoekvervang.filenames = self.names

        self.zoekvervang.do_action(search_python = self.p["context"])
        if len(self.zoekvervang.rpt) == 1:
            gui.QMessageBox.information(self, self.resulttitel, "Niks gevonden",
                gui.QMessageBox.Ok)
        else:
            dlg = Results(self, common_part)
        if self.vraag_exit.isChecked() and self.p["vervang"] is not None:
            self.close()

    def zoekdir(self):
        """event handler voor 'zoek in directory'"""
        oupad = self.vraagDir.currentText()
        dlg = gui.QFileDialog.getExistingDirectory(self, "Choose a directory:",
            oupad)
        if dlg:
            self.vraagDir.setEditText(dlg)
