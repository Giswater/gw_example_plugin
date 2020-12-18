"""
This file is part of Giswater 3
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-
import sys
import os
from functools import partial

from ...ui.ui_manager import DlgConfigVars

sys.path.append(os.path.abspath('../giswater'))
from giswater.core.toolbars.parent_dialog import GwParentAction
from giswater.core.utils import tools_gw
from giswater.lib import tools_qgis, tools_qt




class MyBoton6(GwParentAction):

    def __init__(self, icon_path, action_name, text, toolbar, action_group):
        super().__init__(icon_path, action_name, text, toolbar, action_group)

    def clicked_event(self):
        dlg_config = DlgConfigVars()
        tools_gw.load_settings(dlg_config)
        dlg_config.rejected.connect(partial(tools_gw.save_settings, dlg_config))
        dlg_config.btn_accept.clicked.connect(partial(self.save_values, dlg_config))

        dlg_config.txt_user_config.setText('2')
        tools_gw.open_dialog(dlg_config)


    def save_values(self, dialog):
        # \users\user\giswater\config/session.config
        value = tools_qt.get_text(dialog, dialog.txt_user_config, False, False)
        tools_gw.set_config_parser('docker', 'position', value, None, 'user', 'user')

        # \users\user\giswater\config/session.config
        value = tools_qt.get_text(dialog, dialog.txt_sesion_config_x, False, False)
        tools_gw.set_config_parser('dialogs_position', 'dlg_info_feature_x', value, None, 'user', 'session')
        value = tools_qt.get_text(dialog, dialog.txt_sesion_config_y, False, False)
        tools_gw.set_config_parser('dialogs_position', 'dlg_info_feature_y', value, None, 'user', 'session')

        # \Users\Nestor\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\giswater\config/project
        value = tools_qt.get_text(dialog, dialog.lineEdit_4, False, False)
        tools_gw.set_config_parser('test', 'test_var', value, None, 'project', 'user')

