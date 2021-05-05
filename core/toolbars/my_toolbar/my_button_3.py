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

from ...ui.ui_manager import DlgButton3
from ....settings import giswater_folder, tools_qt
dialog = importlib.import_module('.dialog', package=f'{giswater_folder}.core.toolbars')


class MyButton3(dialog.GwAction):

    def __init__(self, icon_path, action_name, text, toolbar, action_group):
        super().__init__(icon_path, action_name, text, toolbar, action_group)


    def clicked_event(self):
        self.dlg_btn3 = DlgButton3()
        tools_qt.fill_table(self.dlg_btn3.tbl_layer_info, "arc")
        self.dlg_btn3.open()