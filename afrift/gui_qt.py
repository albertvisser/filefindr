"""AFRIFT PyQt specific classes
"""
import os
import sys
import PyQt6.QtWidgets as qtw
import PyQt6.QtGui as gui
import PyQt6.QtCore as core
TXTW = 200


class AfriftGui(qtw.QWidget):
    """main screen
    """
    def __init__(self, master):
        self.master = master        # verwijzing naar Afrift - voor als het nodig is
        self.app = qtw.QApplication(sys.argv)
        parent = None
        super().__init__(parent)
        self.setWindowTitle(master.title)
        self.setWindowIcon(gui.QIcon(master.iconame))

    def init_screen(self):
        "set up screen for the various modes"
        self.grid = qtw.QGridLayout()
        self.row = -1

        vbox = qtw.QVBoxLayout()
        vbox.addLayout(self.grid)

        self.setLayout(vbox)

    def add_combobox_row(self, labeltext, itemlist, initial='', button=None, callback=None, **kwargs):
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
            btn = qtw.QPushButton(button[0], self)
            btn.clicked.connect(button[1])
            box = qtw.QHBoxLayout()
            box.addWidget(cb)
            box.addWidget(btn)
            box.addStretch()
            self.grid.addLayout(box, self.row, 1)
        else:
            self.grid.addWidget(cb, self.row, 1)
        if kwargs.get('completer', '') == 'case':
            cb.completer().setCaseSensitivity(core.Qt.CaseSensitivity.CaseSensitive)
        elif kwargs.get('completer', '') == 'off':
            cb.setCompleter(None)
        if callback:
            cb.editTextChanged[str].connect(callback)
        return cb

    def add_checkbox_row(self, text, toggler=None, spinner=None, indent=0):
        """create a row of widgets in the GUI
        """
        self.row += 1
        cb = qtw.QCheckBox(text, self)
        if toggler:
            cb.toggle()
        if 'letters' in text:
            cb.checkStateChanged.connect(self.check_casing)
        if spinner:
            sb = qtw.QSpinBox(self)
            sb.setValue(spinner[0])
            sb.setMinimum(spinner[1])
            box = qtw.QHBoxLayout()
            box.addWidget(cb)
            box.addWidget(sb)
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
        if spinner:
            return cb, sb
        return cb

    def add_label_to_grid(self, text, fullwidth=False, new_row=False, left_align=False):
        "place a label"
        if new_row or fullwidth:
            self.row += 1
        if fullwidth:
            self.grid.addWidget(qtw.QLabel(text), self.row, 0, 1, 2)
        elif left_align:
            box = qtw.QHBoxLayout()
            box.addWidget(qtw.QLabel(text))
            box.addStretch()
            self.grid.addLayout(box, self.row, 1)
        else:
            self.grid.addWidget(qtw.QLabel(text), self.row, 0)

    def add_listbox_to_grid(self, listitems):
        "place the listbox with the filenames"
        self.row += 1
        lb = qtw.QListWidget(self)
        lb.insertItems(0, listitems)
        self.grid.addWidget(lb, self.row, 0, 1, 2)
        return lb

    def add_buttons(self, buttondefs):
        "add the button strip at the bottom"
        self.row += 1
        hbox = qtw.QHBoxLayout()
        hbox.addStretch()
        for text, callback in buttondefs:
            btn = qtw.QPushButton(text, self)
            btn.clicked.connect(callback)
            hbox.addWidget(btn)
        hbox.addStretch()
        self.grid.addLayout(hbox, self.row, 0, 1, 2)

    def set_focus_to(self, widget):
        "determine the input field to start from"
        widget.setFocus()

    def get_combobox_value(self, cb):
        "return the selected/entered value from a combobox"
        return cb.currentText()

    def get_checkbox_value(self, cb):
        "return the value from a checkbox"
        return cb.isChecked()

    def get_spinbox_value(self, sb):
        "return the value from a spinbox"
        return sb.value()

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

    def add_item_to_searchlist(self, itemlist, item):
        "add string to list of items searched for"
        itemlist.insertItem(0, item)

    def set_waitcursor(self, value):
        """switch back and forth to a "busy" cursor
        """
        if value:
            self.app.setOverrideCursor(gui.QCursor(core.Qt.CursorShape.WaitCursor))
        else:
            self.app.restoreOverrideCursor()

    def go(self):
        "show screen and handle events"
        self.show()
        sys.exit(self.app.exec())

    def einde(self):
        """applicatie afsluiten"""
        self.close()

    def check_casing(self, val):
        """autocompletion voor zoektekst in overeenstemming brengen met case indicator
        """
        # self.master.vraag_zoek.setAutoCompletionCaseSensitivity(new_value)
        completer = self.master.vraag_zoek.completer()
        new_value = (core.Qt.CaseSensitivity.CaseSensitive if val == core.Qt.CheckState.Checked
                     else core.Qt.CaseSensitivity.CaseInsensitive)
        completer.setCaseSensitivity(new_value)
        self.master.vraag_zoek.setCompleter(completer)


    def get_sender_value(self, *args):
        "return the text value from the callback"
        return args[0]

    def replace_combobox_items(self, cmb, itemlist):
        "repopulate a combobox's selection list"
        cmb.clear()
        cmb.addItems(itemlist)

    def set_checkbox_value(self, cb, state):
        "set a checkbox's state"
        cb.setChecked(state)

    # beter implementeren met accelerators
    def keyPressEvent(self, event):
        """event handler voor toetsaanslagen"""
        # if event.key() == core.Qt.Key.Key_Escape:
        if event.key() == core.Qt.Key.Key_Q and event.modifiers() == core.Qt.Modifiers.AltModifier:
            self.close()

    def zoekdir(self):
        """event handler voor 'zoek in directory'"""
        oupad = self.vraag_dir.currentText()
        dlg = qtw.QFileDialog.getExistingDirectory(self, "Choose a directory:", oupad)
        if dlg:
            self.vraag_dir.setEditText(dlg)


class SelectNamesGui(qtw.QDialog):
    """dialog for selecting directories/files
    """
    def __init__(self, parent, master):
        self.master = master
        super().__init__(parent.gui)
        self.setWindowTitle(master.title)
        self.setWindowIcon(gui.QIcon(master.iconame))

    def setup_screen(self):
        "build widgets"
        self.vbox = qtw.QVBoxLayout()
        self.setLayout(self.vbox)

    def add_line(self):
        "start a new screen line"
        hbox = qtw.QHBoxLayout()
        self.vbox.addLayout(hbox)
        return hbox

    def add_text_to_line(self, hbox, text):
        "show some fixed text on the current line"
        txt = qtw.QLabel(text, self)
        hbox.addWidget(txt)

    def add_checkbox_to_line(self, hbox, text, callback):
        "show a textbox on the current line"
        cb = qtw.QCheckBox(text, self)
        cb.clicked.connect(callback)
        hbox.addSpacing(10)
        hbox.addWidget(cb)
        return cb

    def add_button_to_line(self, hbox, text, callback):
        "show a textbox on the current line"
        button = qtw.QPushButton(text, self)
        button.clicked.connect(callback)
        hbox.addStretch()
        hbox.addWidget(button)
        hbox.addSpacing(20)
        return button

    def add_selectionlist(self, hbox, namelist):
        "show the list of names that can be selected"
        # frm is een attribuut m.h.o.o. unittest
        self.frm = qtw.QFrame(self)
        fvbox = qtw.QVBoxLayout()
        checklist = []
        for item in namelist:
            cb = (qtw.QCheckBox(str(item), self.frm) if self.master.do_files
                  else qtw.QCheckBox(item, self.frm))
            fhbox = qtw.QHBoxLayout()
            fhbox.addWidget(cb)
            checklist.append(cb)
            fvbox.addLayout(fhbox)
        self.frm.setLayout(fvbox)
        scrl = qtw.QScrollArea(self)
        scrl.setWidget(self.frm)
        hbox.addWidget(scrl)
        return checklist

    def add_buttons(self, hbox, buttondefs):
        "add a button strip"
        hbox.addStretch(1)
        for text, callback in buttondefs:
            button = qtw.QPushButton(text, self)
            button.clicked.connect(callback)
            hbox.addWidget(button)
        hbox.addStretch(1)

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

    def cancel(self):
        "dialoog afbreken"
        super().reject()

    def confirm(self):
        "dialoog afsluiten"
        dirs = []
        for cb in self.master.checklist:
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
        self.vbox = qtw.QVBoxLayout()

    def add_line(self):
        "add a new line to the display"
        hbox = qtw.QHBoxLayout()
        self.vbox.addLayout(hbox)
        return hbox

    def add_text_to_line(self, hbox, text):
        "add some fixed text to a screen line"
        txt = qtw.QLabel(text, self)
        hbox.addWidget(txt)
        return txt

    def add_buttons_to_line(self, hbox, buttondefs):  # , start=False, end=False):
        "add one or more buttons to a screen line"
        # if start:
        #     hbox.addStretch(1)
        # if end:
        #     hbox.addStretch()
        for caption, callback, enable in buttondefs:
            btn = qtw.QPushButton(caption, self)
            btn.clicked.connect(callback)
            btn.setEnabled(enable)
            hbox.addWidget(btn)

    def add_results_list(self, hbox, headers, actiondefs, listitems):
        "add the list with results to a the display and return a reference to it"
        lijst = qtw.QTableWidget(self)
        lijst.verticalHeader().setVisible(False)
        lijst.setGridStyle(core.Qt.PenStyle.NoPen)
        lijst.setColumnCount(len(headers))
        lijst.setHorizontalHeaderLabels(headers)
        lijst.horizontalHeader().setStretchLastSection(True)
        self.populate_list(lijst, listitems)
        lijst.resizeColumnsToContents()
        lijst.cellDoubleClicked[int, int].connect(self.master.goto_result)
        hbox.addWidget(lijst)
        for caption, keydef, callback in actiondefs:
            act = gui.QAction(caption, self)
            act.setShortcut(keydef)
            act.triggered.connect(callback)
            self.addAction(act)
        return lijst

    def add_checkbox_to_line(self, hbox, caption, checkvalue):
        "show another checkbox on the current line and return a reference to it"
        cb = qtw.QCheckBox(caption, self)
        cb.setChecked(checkvalue)
        hbox.addWidget(cb)
        return cb

    def add_stretch_to_line(self, hbox):
        "make the widgets align to the opposite side"
        hbox.addStretch()

    def disable_widget(self, widget):
        """make a widget inaccessible
        """
        widget.setEnabled(False)

    def finalize_display(self):
        "do layout and set window size"
        breedte = 50 if self.master.parent.apptype.startswith("single") else 150
        self.setLayout(self.vbox)
        if self.show_result_details:
            if self.master.show_context:
                breedte += 200
            self.resize(574 + breedte, 488)

    def populate_list(self, lijst, lijstitems):
        """copy results to listbox
        """
        for ix, result in enumerate(lijstitems[1:]):
            lijst.insertRow(ix)
            lijst.setRowHeight(ix, 18)
            col = 0
            item = qtw.QTableWidgetItem(result[0])
            item.setToolTip(result[0])
            item.setFlags(core.Qt.ItemFlag.ItemIsSelectable | core.Qt.ItemFlag.ItemIsEnabled)
            lijst.setItem(ix, col, item)

            if self.master.show_context:
                col += 1
                item = qtw.QTableWidgetItem(result[1])
                item.setToolTip(result[1])
                item.setFlags(core.Qt.ItemFlag.ItemIsSelectable | core.Qt.ItemFlag.ItemIsEnabled)
                lijst.setItem(ix, col, item)

            col += 1
            item = qtw.QTableWidgetItem(result[-1])
            item.setToolTip(result[-1])
            item.setFlags(core.Qt.ItemFlag.ItemIsSelectable | core.Qt.ItemFlag.ItemIsEnabled)
            lijst.setItem(ix, col, item)

    def clear_contents(self):
        "remove all entries from list"
        self.lijst.clearContents()

    def go(self):
        """show the dialog screen
        """
        self.exec()

    def set_header(self, widget, text):
        "set header for list"
        widget.setText(text)

    def get_checkbox_value(self, widget):
        "return the state of a checkbox"
        return widget.isChecked()

    def get_savefile(self, title, dirname, fname, exts):
        """callback for button 'Copy to file'
        """
        # if ext == '.csv':
        #     f_filter = 'Comma delimited files (*.csv)'
        # else:  # if ext == '.txt':  momenteel geen andere mogelijkheid
        #     f_filter = 'Text files (*.txt)'
        # f_filter = f"{f_filter};;All files (*.*)"
        f_filter = ';;'.join([f'{oms} (*{ext})' for ext, oms in exts])
        dlg = qtw.QFileDialog.getSaveFileName(self, title, os.path.join(dirname, fname), f_filter)
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
        row, column = self.lijst.currentRow(), self.lijst.currentColumn()
        if any((row == -1, column == -1)):
            self.meld(self.master.parent.resulttitel, 'Select a result first')
            return
        self.master.goto_result(row, column)

    def klaar(self):
        """finish dialog
        """
        super().done(0)
