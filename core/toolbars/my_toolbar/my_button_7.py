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

from .... import global_vars
from ....settings import giswater_folder, tools_db, tools_log, tools_qgis, tools_qt, tools_gw
dialog = importlib.import_module('.dialog', package=f'{giswater_folder}.core.toolbars')
importlib.reload(dialog)
importlib.reload(tools_gw)


class MyButton7(dialog.GwAction):

    def __init__(self, icon_path, action_name, text, toolbar, action_group):
        super().__init__(icon_path, action_name, text, toolbar, action_group)


    def clicked_event(self):
        self.show_test_dialog()
        self.execute_processing()
        self.execute_pg_function()
        self.execute_pg_json_function()


    def test_dialog_signal(self):
        print("test_dialog_signal executed")


    def show_test_dialog(self):

        test_dialog = QgsDialog(parent=self.iface.mainWindow(), fl=Qt.WindowFlags(),
            buttons=QDialogButtonBox.Close, orientation=Qt.Horizontal)
        test_dialog.setWindowTitle("TEST DIALOG")
        test_dialog.resize(400, 200)
        date_time_edit = QgsDateTimeEdit(test_dialog)
        date_time_edit.setMinimumSize(100, 30)
        date_time_edit.move(50, 30)
        btn_accept = QPushButton(test_dialog)
        btn_accept.move(200, 30)
        btn_accept.setText("Accept")
        btn_accept.clicked.connect(self.test_dialog_signal)

        test_dialog.show()


    def execute_processing(self):

        print("execute_processing")

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

        sql = "SELECT ws_dev35.test_function();"
        row = tools_db.get_row(sql, log_sql=True)
        if row:
            tools_qgis.show_info(f"Function result: {row[0]}")


    def execute_pg_json_function(self):

        body = None
        # body = tools_gw.create_body()
        result = tools_gw.execute_procedure('test_json_function', body, 'ws_dev35', log_sql=True, log_result=True)
        if result is not None and result['status'] == 'Accepted' and result['message']:
            level = int(result['message']['level']) if 'level' in result['message'] else 1
            tools_qgis.show_message(result['message']['text'], level)

