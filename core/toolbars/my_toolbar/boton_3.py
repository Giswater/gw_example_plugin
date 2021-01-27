"""
This file is part of Giswater 3
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-
import sys, os
sys.path.append(os.path.abspath('../giswater'))
from ...ui.ui_manager import DlgBoton3
from giswater.core.toolbars.dialog import GwAction
from giswater.lib import tools_qt


class MyBoton3(GwAction):

    def __init__(self, icon_path, action_name, text, toolbar, action_group):
        super().__init__(icon_path, action_name, text, toolbar, action_group)


    def clicked_event(self):
        self.dlg_btn3 = DlgBoton3()
        tools_qt.fill_table(self.dlg_btn3.tbl_layer_info, "ws_sample.arc")
        self.dlg_btn3.open()