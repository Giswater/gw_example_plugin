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
        self.dlg = DlgButton7()
        self.dlg.setWindowTitle("New title")

        # Manage widgets dynamically
        widget_name = "cbo_function"
        widget = tools_qt.get_widget(self.dlg, widget_name)
        if widget:
            widget.addItem("execute_processing")
            widget.addItem("execute_pg_function")
            widget.addItem("execute_pg_json_function")
        else:
            tools_qgis.show_warning(f"Widget not found: '{widget_name}'")

        # Select a default option
        tools_qt.set_widget_text(self.dlg, widget_name, "execute_pg_function")

        # Set signals
        self.dlg.btn_accept.clicked.connect(self.accept_clicked)
        self.dlg.btn_open_dialog.clicked.connect(self.show_test_dialog)
        self.dlg.btn_close.clicked.connect(self.dlg.close)

        # Open form
        self.dlg.open()


    def accept_clicked(self):

        # Get selected item from QComboBox
        method_name = tools_qt.get_selected_item(self.dlg, "cbo_function")

        # Check if selected method exists in our class
        if not hasattr(self, method_name):
            tools_qgis.show_warning(f"Method not found: {method_name}")
            return

        # Dynamically get method object. Execute it
        method_object = getattr(self, method_name)
        method_object()


    def test_dialog_signal(self):
        print("test_dialog_signal executed")


    def show_test_dialog(self):

        test_dialog = QgsDialog(parent=self.iface.mainWindow(), fl=Qt.WindowFlags(), buttons=QDialogButtonBox.Close)
        test_dialog.setWindowTitle("TEST DIALOG")
        test_dialog.resize(300, 150)
        date_time_edit = QgsDateTimeEdit(test_dialog)
        date_time_edit.setMinimumSize(150, 30)
        date_time_edit.move(20, 30)
        btn_accept = QPushButton(test_dialog)
        btn_accept.move(20, 80)
        btn_accept.setText("Accept")
        btn_accept.clicked.connect(self.test_dialog_signal)
        test_dialog.open()


    def execute_processing(self, get_active_layer=True):

        tools_log.log_info("execute_processing")

        if get_active_layer:
            layer = global_vars.iface.activeLayer()
        else:
            filename = 'geopackage.gpkg'
            filepath = os.path.join(global_vars.plugin_dir, 'data', filename)
            if not os.path.exists(filepath):
                tools_qgis.show_warning(f"File not found: {filepath}")
                return
            layer = f"{filepath}|layername=cities"

        if layer is None:
            tools_qgis.show_warning("Any layer selected")
            return

        # Execute 'buffer' from processing toolbox
        params = {'INPUT': layer, 'DISTANCE': 10, 'SEGMENTS': 5, 'END_CAP_STYLE': 0, 'JOIN_STYLE': 0,
                  'MITER_LIMIT': 2, 'DISSOLVE': False, 'OUTPUT': 'memory:'}
        processing.runAndLoadResults("native:buffer", params)


    def check_db_connection(self):
        """ Check database connection """

        tools_log.log_info("check_db_connection")

        connection_status, not_version, layer_source = tools_db.set_database_connection()
        if not connection_status:
            tools_log.log_warning(f"Error connecting to database:\n {layer_source}")
            return False

        tools_log.log_info("Connection to database successful")
        tools_log.log_info(f"Credentials: {gw_global_vars.dao_db_credentials}")

        if gw_global_vars.schema_name is None:
            tools_log.log_warning("Global var 'schema_name' not set")
            gw_global_vars.schema_name = global_vars.schema_name

        return True


    def execute_pg_function(self):

        tools_log.log_info("execute_pg_function")

        if not self.check_db_connection():
            return

        function_name = "test_function"
        row = tools_db.check_function(function_name)
        if not row:
            tools_qgis.show_warning("Function not found in database", parameter=function_name)
            return

        # Set PostgreSQL parameter 'search_path'
        tools_db.set_search_path(gw_global_vars.schema_name)

        # Execute PostgreSQL function
        sql = f"SELECT {gw_global_vars.schema_name}.{function_name}();"
        row = tools_db.get_row(sql, log_sql=True)
        if row:
            tools_qgis.show_info(f"Function result: {row[0]}")


    def execute_pg_json_function(self):

        function_name = "test_json_function"
        row = tools_db.check_function(function_name)
        if not row:
            tools_qgis.show_warning("Function not found in database", parameter=function_name)
            return

        # Set PostgreSQL parameter 'search_path'
        tools_db.set_search_path(gw_global_vars.schema_name)

        body = None
        # body = tools_gw.create_body()
        result = tools_gw.execute_procedure(function_name, body, gw_global_vars.schema_name, log_sql=True)
        if result is not None and result['status'] == 'Accepted' and result['message']:
            level = int(result['message']['level']) if 'level' in result['message'] else 1
            tools_qgis.show_message(result['message']['text'], level)

