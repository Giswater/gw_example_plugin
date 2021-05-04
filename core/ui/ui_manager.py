"""
This file is part of Giswater 3
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-
import configparser
import os
import webbrowser

from qgis.PyQt import uic, QtCore
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QMainWindow, QDialog, QDockWidget, QWhatsThis, QLineEdit


class GwDockWidget(QDockWidget):

    dlg_closed = QtCore.pyqtSignal()
    
    def __init__(self, subtag=None):
        super().__init__()
        self.setupUi(self)
        self.subtag = subtag


    def closeEvent(self, event):
        self.dlg_closed.emit()
        return super().closeEvent(event)


class GwDialog(QDialog):

    def __init__(self, subtag=None):
        super().__init__()
        self.setupUi(self)
        self.subtag = subtag
        self.installEventFilter(self)


    def eventFilter(self, object, event):

        if event.type() == QtCore.QEvent.EnterWhatsThisMode and self.isActiveWindow():
            QWhatsThis.leaveWhatsThisMode()
            parser = configparser.ConfigParser()
            path = os.path.dirname(__file__) + os.sep + 'config' + os.sep + 'init.config'
            if not os.path.exists(path):
                print(f"File not found: {path}")
                webbrowser.open_new_tab('https://giswater.org/giswater-manual')
                return True

            parser.read(path)
            if self.subtag is not None:
                tag = f'{self.objectName()}_{self.subtag}'
            else:
                tag = str(self.objectName())

            try:
                web_tag = parser.get('web_tag', tag)
                webbrowser.open_new_tab(f'https://giswater.org/giswater-manual/#{web_tag}')
            except Exception:
                webbrowser.open_new_tab('https://giswater.org/giswater-manual')
            finally:
                return True

        return False


class GwMainWindowDialog(QMainWindow):

    dlg_closed = QtCore.pyqtSignal()
    key_escape = QtCore.pyqtSignal()
    key_enter = QtCore.pyqtSignal()

    def __init__(self, subtag=None):
        super().__init__()
        self.setupUi(self)
        self.subtag = subtag
        self.installEventFilter(self)


    def closeEvent(self, event):
        try:
            self.dlg_closed.emit()
            return super().closeEvent(event)
        except RuntimeError:
            pass


    def eventFilter(self, object, event):

        if event.type() == QtCore.QEvent.EnterWhatsThisMode and self.isActiveWindow():
            QWhatsThis.leaveWhatsThisMode()
            parser = configparser.ConfigParser()
            path = os.path.dirname(__file__) + os.sep + 'config' + os.sep + 'init.config'
            if not os.path.exists(path):
                print(f"File not found: {path}")
                webbrowser.open_new_tab('https://giswater.org/giswater-manual')
                return True

            parser.read(path)
            if self.subtag is not None:
                tag = f'{self.objectName()}_{self.subtag}'
            else:
                tag = str(self.objectName())
            try:
                web_tag = parser.get('web_tag', tag)
                webbrowser.open_new_tab(f'https://giswater.org/giswater-manual/#{web_tag}')
            except Exception:
                webbrowser.open_new_tab('https://giswater.org/giswater-manual')
            return True
        return False


    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.key_escape.emit()
            return super().keyPressEvent(event)
        if event.key() == QtCore.Qt.Key_Return or event.key() == QtCore.Qt.Key_Enter:
            self.key_enter.emit()
            return super().keyPressEvent(event)


def get_ui_class(ui_file_name, subfolder=None):
    """ Get UI Python class from @ui_file_name """

    ui_folder_path = os.path.dirname(__file__)
    if subfolder:
        ui_folder_path = os.path.join(ui_folder_path, subfolder)
    ui_file_path = os.path.abspath(os.path.join(ui_folder_path, ui_file_name))
    #print(f"{ui_file_path}")
    return uic.loadUiType(ui_file_path)[0]


# Dialogs of toolbar: my_toolbar
FORM_CLASS = get_ui_class('dlg_boton1.ui', 'my_toolbar')
class DlgBoton1(GwDialog, FORM_CLASS):
    pass

FORM_CLASS = get_ui_class('dlg_boton2.ui', 'my_toolbar')
class DlgBoton2(GwDialog, FORM_CLASS):
    pass

FORM_CLASS = get_ui_class('dlg_boton3.ui', 'my_toolbar')
class DlgBoton3(GwDialog, FORM_CLASS):
    pass

# Dialogs of toolbar: mincut
FORM_CLASS = get_ui_class('mincut_manager.ui', 'mincut')
class MincutManagerUi(GwDialog, FORM_CLASS):
    pass

FORM_CLASS = get_ui_class('mincut.ui', 'mincut')
class MincutUi(GwMainWindowDialog, FORM_CLASS):
    def __init__(self):
        self.closeMainWin = False
        self.mincutCanceled = True
        super().__init__()
