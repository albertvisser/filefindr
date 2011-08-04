#! /usr/bin/env python
"AFRIFT PyGT versie"

import os
import sys
import PyQt4.QtGui as gui
import PyQt4.QtCore as core
from findr_files import findr
from afrift_base import iconame, ABase

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
        self.lijst.setColumnWidth(0, breedte)
        self.lijst.setColumnWidth(1, 520)
        self.populate_list()

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
        headers = []
        for ix, line in enumerate(self.parent.zoekvervang.rpt):
            if ix == 0:
                kop = line
            elif line != "":
                where, what = line.split(": ", 1)
                if self.parent.apptype == "single":
                    fname, lineno = where.split("r.", 1)
                    if ix == 1:
                        kop += " in {0}".format(fname)
                    where = lineno
                self.lijst.insertRow(ix - 1)
                headers.append('')
                item = gui.QTableWidgetItem(where)
                item.setFlags(core.Qt.ItemIsSelectable | core.Qt.ItemIsEnabled)
                self.lijst.setItem(ix - 1, 0, item)
                item = gui.QTableWidgetItem(what)
                item.setFlags(core.Qt.ItemIsSelectable | core.Qt.ItemIsEnabled)
                self.lijst.setItem(ix - 1, 1, item)
                self.results.append((where, what))
        self.lijst.setVerticalHeaderLabels(headers)
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
    hmmm... sizen werkt wel met een QWidget maar niet met een QMainWindow?

    QWidget::setLayout: Attempting to set QLayout "" on MainWindow "",
    which already has a layout

    geeft nog steeds een segfault bij afsluiten"""

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
        c1 = gui.QComboBox(self)
        c1.setMaximumWidth(TXTW)
        c1.insertItems(0, self._mruItems["zoek"])
        c1.setEditable(True)
        c1.clearEditText()
        grid.addWidget(c1, row, 1)
        self.vraagZoek = c1

        row += 1
        grid.addWidget(gui.QLabel('Vervang door:'), row, 0)
        c2 = gui.QComboBox(self)
        c2.setMaximumWidth(TXTW)
        c2.insertItems(0, self._mruItems["verv"])
        c2.setEditable(True)
        c2.clearEditText()
        grid.addWidget(c2, row, 1)
        self.vraagVerv = c2

        row += 1
        vbox = gui.QVBoxLayout()
        c3 = gui.QCheckBox("lege vervangtekst = weghalen", self)
        if self._vervleeg:
            c3.toggle()
        vbox.addWidget(c3)
        self.cVervang = c3
        c4 = gui.QCheckBox("hoofd/kleine letters gelijk", self)
        if self.p["case"]:
            c4.toggle()
        vbox.addWidget(c4)
        self.vraagCase = c4
        c5 = gui.QCheckBox("hele woorden", self)
        if self.p["woord"]:
            c5.toggle()
        vbox.addWidget(c5)
        self.vraagWoord = c5
        grid.addLayout(vbox, row, 1)

        t = ""
        if self.apptype == "":
            row += 1
            grid.addWidget(gui.QLabel("In directory:"), row, 0)
            c6 = gui.QComboBox(self)
            c6.setMaximumWidth(TXTW)
            c6.insertItems(0, self._mruItems["dirs"])
            c6.setEditable(True)
            c6.clearEditText()
            grid.addWidget(c6, row, 1)
            self.vraagDir = c6
            self.zoek = gui.QPushButton("&Zoek")
            self.connect(self.zoek, core.SIGNAL('clicked()'), self.zoekdir)
            grid.addWidget(self.zoek, row, 2)
        elif self.apptype == "single":
            row += 1
            grid.addWidget(gui.QLabel("In file/directory:"), row, 0)
            grid.addWidget(gui.QLabel(self.fnames[0]), row, 1)
            grid.addWidget(gui.QLabel(""), row, 2) # size = (120,-1))
        elif self.apptype == "multi":
            t = "van geselecteerde directories "

        if self.apptype != "single" or os.path.isdir(self.fnames[0]):
            row += 1
            c7 = gui.QCheckBox(t + "ook subdirectories doorzoeken")
            if self.p["subdirs"]:
                c7.toggle()
            grid.addWidget(c7, row, 1)
            self.vraagSubs = c7

            row += 1
            grid.addWidget(gui.QLabel("alleen files van type:"), row, 0)
            c8 = gui.QComboBox(self)
            c8.setMaximumWidth(TXTW)
            c8.insertItems(0, self._mruItems["types"])
            c8.setEditable(True)
            c8.clearEditText()
            grid.addWidget(c8, row, 1)
            self.vraagTypes = c8

        if self.apptype == "multi":
            row += 1
            grid.addWidget(gui.QLabel("In de volgende files/directories:"), row, 0)
            row += 1
            c9 = gui.QListWidget(self)
            ## c9.setMaximumWidth(TXTW)
            c9.insertItems(0, self.fnames)
            grid.addWidget(c9, row, 0)
            self.lb = c9

        row += 1
        c10 = gui.QCheckBox("gewijzigd(e) bestand(en) backuppen")
        if self._backup:
            c10.toggle()
        grid.addWidget(c10, row, 1)
        self.vraagBackup = c10

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
        grid.addLayout(hbox, row, 0, 1, 3)

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
            self.checkverv(str(self.vraagVerv.currentText()), self.cVervang.isChecked())
            self.checkattr(self.vraagCase.isChecked(), self.vraagWoord.isChecked())
            if self.apptype != "single" or os.path.isdir(self.fnames[0]):
                b = str(self.vraagTypes.currentText())
                if b:
                    self.checktype(b)
            if not self.apptype:
                mld = self.checkpath(str(self.vraagDir.currentText()))
        if not mld:
            if self.apptype != "single" or os.path.isdir(self.fnames[0]):
                self.checksubs(self.vraagSubs.isChecked())
        self.p["backup"] = self.vraagBackup.isChecked()

        if mld:
            gui.QMessageBox.critical(self, self.fouttitel, mld, gui.QMessageBox.Ok)
            return

        self.schrijfini()
        self.zoekvervang = findr(**self.p)

        if len(self.zoekvervang.rpt) == 1:
            gui.QMessageBox.information(self, self.resulttitel, "Niks gevonden",
                gui.QMessageBox.Ok)
        else:
            dlg = Results(self)

    def zoekdir(self):
        """event handler voor 'zoek in directory'"""
        oupad = self.vraagDir.currentText()
        dlg = gui.QFileDialog.getExistingDirectory(self, "Choose a directory:",
            oupad)
        if dlg:
            self.vraagDir.setEditText(dlg)

def test():
    "test routine"
    ## win = MainFrame()
    MainFrame(apptype = "single", fnaam = '/home/albert/filefindr/afrift/afrift_gui.py')
    ## win = MainFrame(apptype="multi", fnaam = 'CMDAE.tmp')

if __name__ == "__main__":
    test()
