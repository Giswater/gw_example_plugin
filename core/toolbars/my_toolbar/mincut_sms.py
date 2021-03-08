"""
This file is part of Giswater 3
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-
from qgis.PyQt.QtWidgets import QAction

from ...ui.ui_manager import MincutUi
from ....settings import tools_qgis, tools_qt, tools_gw, tools_db, mincut, dialog


class MincutSms(dialog.GwAction):
    def __init__(self, icon_path, action_name, text, toolbar, action_group):
        super().__init__(icon_path, action_name, text, toolbar, action_group)

    def clicked_event(self):
        self.mincut = mincut.GwMincut()
        self.mincut.set_dialog(MincutUi())
        self.dlg_mincut = self.mincut.dlg_mincut

        self.mincut.get_mincut()
        action = self.dlg_mincut.findChild(QAction, "actionShowNotified")
        action.triggered.connect(self.show_notified_list)



    def show_notified_list(self):

        mincut_id = tools_qt.get_text(self.dlg_mincut, self.dlg_mincut.result_mincut_id)
        sql = (f"SELECT notified FROM om_mincut "
               f"WHERE id = '{mincut_id}'")
        row = tools_db.get_row(sql)
        if not row or row[0] is None:
            text = "Nothing to show"
            tools_qt.show_info_box(str(text), "Sms info")
            return
        text = ""
        for item in row[0]:
            text += f"SMS sended on date: {item['date']}, with code result: {item['code']} .\n"
        tools_qt.show_info_box(str(text), "Sms info")
