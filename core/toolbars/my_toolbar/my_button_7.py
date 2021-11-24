"""
This file is part of Giswater 3
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-
import importlib
import os
import sys

import processing
from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QDialog, QDialogButtonBox, QPushButton
from qgis.core import QgsApplication
from qgis.gui import QgsDialog, QgsDateTimeEdit

from ...ui.ui_manager import DlgButton7
from .... import global_vars
from ....settings import giswater_folder, tools_db, tools_log, tools_qgis, tools_qt, tools_gw, gw_global_vars
dialog = importlib.import_module('.dialog', package=f'{giswater_folder}.core.toolbars')
importlib.reload(dialog)
importlib.reload(tools_gw)


class MyButton7(dialog.GwAction):

    def __init__(self, icon_path, action_name, text, toolbar, action_group):
        super().__init__(icon_path, action_name, text, toolbar, action_group)


    def clicked_event(self):

        self.show_main_dialog()


    def show_main_dialog(self):

        # Create form
        self.dlg_btn7 = DlgButton7()
        self.dlg_btn7.setWindowTitle("New title")

        # Manage widgets dynamically
        widget_name = "cbo_function"
        widget = tools_qt.get_widget(self.dlg_btn7, widget_name)
        if widget:
            widget.addItem("test_function")
        else:
            print(f"Widget not found: '{widget_name}'")

        # Set signals
        self.dlg_btn7.btn_accept.clicked.connect(self.accept_clicked)
        self.dlg_btn7.btn_open_dialog.clicked.connect(self.show_test_dialog)
        self.dlg_btn7.btn_close.clicked.connect(self.dlg_btn7.close)

        # Open form
        self.dlg_btn7.show()


    def accept_clicked(self):

        # Get selected item from QComboBox
        method_name = tools_qt.get_selected_item(self.dlg_btn7, "cbo_function")

        # Check if selected method exists in our class
        if not hasattr(self, method_name):
            print(f"Method not found: {method_name}")
            return

        # Dynamically get method object. Execute it
        method_object = getattr(self, method_name)
        method_object()


    def test_dialog_signal(self):
        print("test_dialog_signal executed")


    def show_test_dialog(self):

        parent_window = self.iface.mainWindow()
        test_dialog = QgsDialog(parent=parent_window, fl=Qt.WindowFlags(), buttons=QDialogButtonBox.Close)
        test_dialog.setWindowTitle("TEST DIALOG")
        test_dialog.resize(300, 150)
        test_dialog.move(500, 300)
        date_time_edit = QgsDateTimeEdit(test_dialog)
        date_time_edit.setMinimumSize(150, 30)
        date_time_edit.move(20, 30)
        btn_accept = QPushButton(test_dialog)
        btn_accept.move(20, 80)
        btn_accept.setText("Accept")
        btn_accept.clicked.connect(self.test_dialog_signal)

        test_dialog.show()


    def execute_processing(self):

        tools_log.log_info("execute_processing")

        #processing.algorithmHelp("native:buffer")
        filename = 'geopackage.gpkg'
        filepath = os.path.join(global_vars.plugin_dir, 'data', filename)
        if not os.path.exists(filepath):
            tools_qgis.show_warning(f"File not found: {filepath}")
            return

        uri_places = f"{filepath}|layername=cities"
        params = {'INPUT': uri_places, 'DISTANCE': 0.5, 'SEGMENTS': 5, 'END_CAP_STYLE': 0, 'JOIN_STYLE': 0,
                  'MITER_LIMIT': 2, 'DISSOLVE': False, 'OUTPUT': 'memory:'}

        # Execute 'buffer' from processing toolbox
        processing.runAndLoadResults("native:buffer", params)


    def execute_pg_function(self):

        if gw_global_vars.schema_name:
            tools_qgis.show_warning("Database schema name not found!")
            return

        sql = f"SELECT {gw_global_vars.schema_name}.test_function();"
        row = tools_db.get_row(sql, log_sql=True)
        if row:
            tools_qgis.show_info(f"Function result: {row[0]}")


    def execute_pg_json_function(self):

        if gw_global_vars.schema_name is None:
            tools_qgis.show_warning("Database schema name not found!")
            return

        body = None
        # body = tools_gw.create_body()
        result = tools_gw.execute_procedure('test_json_function', body, gw_global_vars.schema_name,
            log_sql=True, log_result=True)
        if result is not None and result['status'] == 'Accepted' and result['message']:
            level = int(result['message']['level']) if 'level' in result['message'] else 1
            tools_qgis.show_message(result['message']['text'], level)

