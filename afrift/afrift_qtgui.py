#! /usr/bin/env python
"AFRIFT PyQt versie"

import os
import sys
import PyQt4.QtGui as gui
import PyQt4.QtCore as core
from .findr_files import Finder
from .afrift_base import iconame, ABase

class SelectNames(gui.QDialog):
    """Tussenscherm om te verwerken files te kiezen"""

    def __init__(self, parent, files=True):
        self.dofiles = files
        self.parent = parent
        self.results = []
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
        self.connect(b1, core.SIGNAL('clicked()'), self.klaar)
        hboks = gui.QHBoxLayout()
        hbox = gui.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(b1)
        hbox.addStretch(1)
        hboks.addLayout(hbox)
        vbox.addLayout(hboks)

        self.setLayout(vbox)
        self.exec_()

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
    """Resultaten scherm"""

    def __init__(self, parent):
        self.parent = parent
        self.results = []
        if self.parent.apptype == "":
            breedte, titel = 300, 'File/Regel'
        elif self.parent.apptype == "single":
            breedte, titel = 50, 'Regel'
        elif self.parent.apptype == "multi":
            breedte, titel = 200, 'File/Regel'
        gui.QDialog.__init__(self, parent)
        self.setWindowTitle(self.parent.resulttitel)
        self.setWindowIcon(gui.QIcon(iconame))

        txt = gui.QLabel("{0} ({1} items)".format(self.parent.zoekvervang.rpt[0],
            len(self.parent.zoekvervang.rpt)-1), self)
        self.lijst = gui.QTableWidget(self)
        self.lijst.setColumnCount(2)
        self.lijst.setHorizontalHeaderLabels((titel, 'Data'))
        self.lijst.verticalHeader().setVisible(False)
        ## self.lijst.setShowGrid(False) # hierbij komt de tweede kolom top- ipv middle-aligned
        self.lijst.setGridStyle(core.Qt.NoPen)# hierbij niet
        self.lijst.setColumnWidth(0, breedte)
        self.lijst.setColumnWidth(1, 520)
        self.populate_list()
        ## self.lijst.resizeRowsToContents()

        b1 = gui.QPushButton("&Klaar", self)
        self.connect(b1, core.SIGNAL('clicked()'), self.klaar)
        b2 = gui.QPushButton("&Copy to File", self)
        self.connect(b2, core.SIGNAL('clicked()'), self.kopie)
        self.cb = gui.QCheckBox("toon directorypad in uitvoer", self)

        vbox = gui.QVBoxLayout()

        hbox = gui.QHBoxLayout()
        hbox.addWidget(txt)
        vbox.addLayout(hbox)

        hbox = gui.QHBoxLayout()
        hbox.addWidget(self.lijst)
        vbox.addLayout(hbox)

        hboks = gui.QHBoxLayout()
        hbox = gui.QHBoxLayout()
        hbox.addWidget(b1)
        hbox.addWidget(b2)
        hbox.addWidget(self.cb)
        hbox.insertStretch(0, 1)
        hbox.addStretch(1)
        hboks.addLayout(hbox)
        vbox.addLayout(hboks)

        self.setLayout(vbox)
        self.resize(574 + breedte, 480)
        self.exec_()

    def populate_list(self):
        "resultaten in de listbox zetten"
        # table.setItem(row, column, QtGui.QWidget(self))
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
                self.lijst.insertRow(ix - 1)
                self.lijst.setRowHeight(ix - 1, 18)
                ## headers.append('')
                item = gui.QTableWidgetItem(where)
                item.setFlags(core.Qt.ItemIsSelectable | core.Qt.ItemIsEnabled)
                self.lijst.setItem(ix - 1, 0, item)
                item = gui.QTableWidgetItem(what)
                item.setFlags(core.Qt.ItemIsSelectable | core.Qt.ItemIsEnabled)
                self.lijst.setItem(ix - 1, 1, item)
                self.results.append((where, what))
        ## self.lijst.setVerticalHeaderLabels(headers)
        self.results.insert(0, kop)

    def klaar(self):
        "dialoog afsluiten"
        gui.QDialog.done(self, 0)

    def kopie(self):
        "callback for button 'Copy to file'"
        toonpad = True if self.cb.isChecked() else False
        f = self.parent.p["zoek"]
        for char in '/\\?%*:|"><.':
            if char in f:
                f = f.replace(char, "~")
        f +=  ".txt"
        dlg = gui.QFileDialog.getSaveFileName(self,
            "Resultaat naar bestand kopieren",
            os.path.join(self.parent.hier,f),
            "Text files (*.txt);;All files (*.*)",
            )
        if not dlg:
            return
        with open(dlg, "w") as f_out:
            f_out.write("{0}\n".format(self.results[0]))
            for r1, r2 in self.results[1:]:
                if toonpad:
                    f_out.write("{0} {1}\n".format(r1, r2))
                else:
                    f_out.write("{0} {1}\n".format(r1.split(os.sep)[-1], r2))

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

        TXTW = 200
        grid = gui.QGridLayout()

        row = 0
        grid.addWidget(gui.QLabel('Zoek naar:'), row, 0)
        cb = gui.QComboBox(self)
        cb.setMaximumWidth(TXTW)
        cb.insertItems(0, self._mru_items["zoek"])
        cb.setEditable(True)
        cb.clearEditText()
        grid.addWidget(cb, row, 1)
        self.vraagZoek = cb

        row += 1
        grid.addWidget(gui.QLabel('Vervang door:'), row, 0)
        cb = gui.QComboBox(self)
        cb.setMaximumWidth(TXTW)
        cb.insertItems(0, self._mru_items["verv"])
        cb.setEditable(True)
        cb.clearEditText()
        grid.addWidget(cb, row, 1)
        self.vraagVerv = cb

        row += 1
        vbox = gui.QVBoxLayout()
        cb = gui.QCheckBox("lege vervangtekst = weghalen", self)
        if self._vervleeg:
            cb.toggle()
        vbox.addWidget(cb)
        self.cVervang = cb
        cb = gui.QCheckBox("hoofd/kleine letters gelijk", self)
        if self.p["case"]:
            cb.toggle()
        vbox.addWidget(cb)
        self.vraagCase = cb
        cb = gui.QCheckBox("hele woorden", self)
        if self.p["woord"]:
            cb.toggle()
        vbox.addWidget(cb)
        self.vraagWoord = cb
        grid.addLayout(vbox, row, 1)

        t = ""
        if self.apptype == "":
            row += 1
            grid.addWidget(gui.QLabel("In directory:"), row, 0)
            box = gui.QHBoxLayout()
            cb = gui.QComboBox(self)
            cb.setMaximumWidth(TXTW)
            cb.insertItems(0, self._mru_items["dirs"])
            cb.setEditable(True)
            cb.clearEditText()
            box.addWidget(cb)
            self.vraagDir = cb
            self.zoek = gui.QPushButton("&Zoek")
            self.connect(self.zoek, core.SIGNAL('clicked()'), self.zoekdir)
            box.addWidget(self.zoek)
            box.addStretch()
            grid.addLayout(box, row, 1)

        elif self.apptype == "single":
            row += 1
            grid.addWidget(gui.QLabel("In file/directory:"), row, 0)
            box = gui.QHBoxLayout()
            box.addWidget(gui.QLabel(self.fnames[0]))
            box.addStretch()
            grid.addLayout(box, row, 1)

        elif self.apptype == "multi":
            t = "van geselecteerde directories "

        if self.apptype != "single" or os.path.isdir(self.fnames[0]):
            row += 1
            cb = gui.QCheckBox(t + "ook subdirectories doorzoeken")
            if self.p["subdirs"]:
                cb.toggle()
            grid.addWidget(cb, row, 1)
            self.vraagSubs = cb

            row += 1
            choice = gui.QCheckBox("symlinks volgen")
            box = gui.QHBoxLayout()
            box.addWidget(choice)
            self.vraag_links = choice
            box2 = gui.QHBoxLayout()
            box2.addWidget(gui.QLabel("    max. diepte (-1 is alles):"))
            choice = gui.QSpinBox(self)
            choice.setMinimum(-1)
            choice.setValue(5)
            box2.addWidget(choice)
            box2.addStretch()
            box.addLayout(box2)
            grid.addLayout(box, row, 1)
            self.vraag_diepte = choice

            row += 1
            choice = gui.QCheckBox("selecteer directories om over te slaan")
            choice.toggle()
            box = gui.QHBoxLayout()
            box.addWidget(choice)
            self.ask_skipdirs = choice
            grid.addLayout(box, row, 1)

            row += 1
            choice = gui.QCheckBox("selecteer bestanden om over te slaan")
            choice.toggle()
            box = gui.QHBoxLayout()
            box.addWidget(choice)
            self.ask_skipfiles = choice
            grid.addLayout(box, row, 1)

        if self.apptype != "single" or os.path.isdir(self.fnames[0]):
            row += 1
            grid.addWidget(gui.QLabel("alleen files van type:"), row, 0)
            cb = gui.QComboBox(self)
            cb.setMaximumWidth(TXTW)
            cb.insertItems(0, self._mru_items["types"])
            cb.setEditable(True)
            cb.clearEditText()
            grid.addWidget(cb, row, 1)
            self.vraagTypes = cb

        if self.apptype == "multi":
            row += 1
            grid.addWidget(gui.QLabel("In de volgende files/directories:"), row, 0,
                1, 2)
            row += 1
            cb = gui.QListWidget(self)
            ## cb.setMaximumWidth(TXTW)
            cb.insertItems(0, self.fnames)
            grid.addWidget(cb, row, 0, 1, 2)
            self.lb = cb

        row += 1
        cb = gui.QCheckBox("gewijzigd(e) bestand(en) backuppen")
        if self._backup:
            cb.toggle()
        grid.addWidget(cb, row, 1)
        self.vraagBackup = cb
        row += 1
        cb = gui.QCheckBox("direct afsluiten na vervangen")
        if self._exit_when_ready:
            cb.toggle()
        grid.addWidget(cb, row, 1)
        self.vraag_exit = cb

        row += 1
        hbox = gui.QHBoxLayout()
        hbox.addStretch(1)
        self.DoIt = gui.QPushButton('&Uitvoeren', self)
        self.connect(self.DoIt, core.SIGNAL('clicked()'), self.doe)
        hbox.addWidget(self.DoIt)
        self.Cancel = gui.QPushButton('&Einde', self)
        self.connect(self.Cancel, core.SIGNAL('clicked()'),
            self.close)
        hbox.addWidget(self.Cancel)
        hbox.addStretch(1)
        grid.addLayout(hbox, row, 0, 1, 2)

        vbox = gui.QVBoxLayout()
        vbox.addLayout(grid)

        self.setLayout(vbox)
        ## self.resize(250, 150)
        self.vraagZoek.setFocus()

        self.show()
        sys.exit(app.exec_())

    def keyPressEvent(self, event):
        """event handler voor toetsaanslagen"""
        if event.key() == core.Qt.Key_Escape:
            self.close()

    def doe(self):
        """Zoekactie uitvoeren en resultaatscherm tonen"""
        mld = self.checkzoek(str(self.vraagZoek.currentText()))
        if not mld:
            self.checkverv(str(self.vraagVerv.currentText()),
                self.cVervang.isChecked())
            self.checkattr(self.vraagCase.isChecked(), self.vraagWoord.isChecked())
            if self.apptype != "single" or os.path.isdir(self.fnames[0]):
                self.checktype(str(self.vraagTypes.currentText()))
            if not self.apptype:
                mld = self.checkpath(str(self.vraagDir.currentText()))
        if not mld:
            if self.apptype != "single" or os.path.isdir(self.fnames[0]):
                self.checksubs(self.vraagSubs.isChecked(), self.vraag_links.isChecked(),
                    self.vraag_diepte.value())
            elif self.apptype == "single" and os.path.islink(self.fnames[0]):
                self.p["follow_symlinks"] = True
        self.p["backup"] = self.vraagBackup.isChecked()

        if mld:
            gui.QMessageBox.critical(self, self.fouttitel, mld, gui.QMessageBox.Ok)
            return

        self.schrijfini()
        self.zoekvervang = Finder(**self.p)
        if not self.zoekvervang.filenames:
            gui.QMessageBox.information(self, self.resulttitel,
                "Geen bestanden gevonden", gui.QMessageBox.Ok)
            return

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
                    for name in self.names:
                        for fname in fnames:
                            if fname.startswith(name + '/'):
                                ## try:
                                self.zoekvervang.filenames.remove(fname)
                                ## except ValueError:
                                    ## pass # may already be removed
            if self.ask_skipfiles.isChecked():
                self.names = self.zoekvervang.filenames
                dlg = SelectNames(self)
                self.zoekvervang.filenames = self.names

        self.zoekvervang.do_action()
        if len(self.zoekvervang.rpt) == 1:
            gui.QMessageBox.information(self, self.resulttitel, "Niks gevonden",
                gui.QMessageBox.Ok)
        else:
            dlg = Results(self)
        if self.vraag_exit.isChecked() and self.p["vervang"] is not None:
            self.close()

    def zoekdir(self):
        """event handler voor 'zoek in directory'"""
        oupad = self.vraagDir.currentText()
        dlg = gui.QFileDialog.getExistingDirectory(self, "Choose a directory:",
            oupad)
        if dlg:
            self.vraagDir.setEditText(dlg)
