"""
This file is part of Giswater 3
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-
import json
import os
import subprocess
from collections import OrderedDict
from functools import partial

from core.ui.ui_manager import MincutManagerUi
from settings import tools_qgis, tools_qt, tools_gw, tools_db, mincut, dialog


class MincutManagerSms(dialog.GwAction):

    def __init__(self, icon_path, action_name, text, toolbar, action_group):
        super().__init__(icon_path, action_name, text, toolbar, action_group)

    def clicked_event(self):
        self.mincut = mincut.GwMincut()

        self.mincut.manage_mincuts(MincutManagerUi())
        self.dlg_mincut_man = self.mincut.mincut_tools.dlg_mincut_man

        btn_notify = self.dlg_mincut_man.btn_notify
        btn_notify.clicked.connect(partial(self.get_clients_codes, self.dlg_mincut_man.tbl_mincut_edit))
        tools_gw.add_icon(btn_notify, "307")
        try:
            row = tools_gw.get_config_value('om_mincut_enable_alerts', 'value', 'config_param_system')
            if row:
                self.custom_action_sms = json.loads(row[0], object_pairs_hook=OrderedDict)
        except KeyError as e:
            print(f"EXCEPTION: {type(e).__name__}, {e}")


    def get_clients_codes(self, qtable):

        selected_list = qtable.selectionModel().selectedRows()
        if len(selected_list) == 0:
            message = "Any record selected"
            tools_qgis.show_warning(message)
            return

        field_code = self.custom_action_sms['field_code']
        inf_text = "Are you sure you want to send smd to this clients?"
        for i in range(0, len(selected_list)):
            row = selected_list[i].row()
            id_ = qtable.model().record(row).value(str('id'))
            inf_text += f"\n\nMincut: {id_}"
            sql = (f"SELECT t3.{field_code}, t2.forecast_start, t2.forecast_end, anl_cause "
                   f"FROM om_mincut_hydrometer AS t1 "
                   f"JOIN ext_rtc_hydrometer AS t3 ON t1.hydrometer_id::bigint = t3.id::bigint "
                   f"JOIN om_mincut AS t2 ON t1.result_id = t2.id "
                   f"WHERE result_id = {id_}")
            rows = tools_db.get_rows(sql)
            if not rows:
                inf_text += "\nClients: None(No messages will be sent)"
                continue

            inf_text += "\nClients: \n"
            for row in rows:
                inf_text += str(row[0]) + ", "

        inf_text = inf_text[:-2]
        inf_text += "\n"
        answer = tools_qt.show_question(str(inf_text))
        if answer:
            self.call_sms_script(qtable)


    def call_sms_script(self, qtable):

        path = self.custom_action_sms['path_sms_script']
        if path is None or not os.path.exists(path):
            tools_qgis.show_warning("File not found", parameter=path)
            return

        selected_list = qtable.selectionModel().selectedRows()
        field_code = self.custom_action_sms['field_code']

        for i in range(0, len(selected_list)):
            row = selected_list[i].row()
            id_ = qtable.model().record(row).value(str('id'))
            sql = (f"SELECT t3.{field_code}, t2.forecast_start, t2.forecast_end, anl_cause, notified  "
                   f"FROM om_mincut_hydrometer AS t1 "
                   f"JOIN ext_rtc_hydrometer AS t3 ON t1.hydrometer_id::bigint = t3.id::bigint "
                   f"JOIN om_mincut AS t2 ON t1.result_id = t2.id "
                   f"WHERE result_id = {id_}")
            rows = tools_db.get_rows(sql)
            if not rows:
                continue

            from_date = ""
            if rows[0][1] is not None:
                from_date = str(rows[0][1].strftime('%d/%m/%Y %H:%M'))

            to_date = ""
            if rows[0][2] is not None:
                to_date = str(rows[0][2].strftime('%d/%m/%Y %H:%M'))

            _cause = ""
            if rows[0][3] is not None:
                _cause = rows[0][3]

            list_clients = ""
            for row in rows:
                list_clients += str(row[0]) + ", "
            if len(list_clients) != 0:
                list_clients = list_clients[:-2]

            # Call script
            result = subprocess.call([path, _cause, from_date, to_date, list_clients])
            print(f"-->{result}<--")

            # Set a model with selected filter. Attach that model to selected table
            self.mincut.mincut_tools.fill_table_mincut_management(qtable, self.schema_name + ".v_ui_mincut")
            tools_gw.set_tablemodel_config(self.dlg_mincut_man, qtable, "v_ui_mincut", sort_order=1)
