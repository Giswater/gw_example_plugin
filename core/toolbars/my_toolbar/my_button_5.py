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

from qgis.PyQt.QtCore import Qt

from ....settings import giswater_folder, tools_log, tools_qgis, tools_qt, tools_gw
maptool = importlib.import_module('.maptool', package=f'{giswater_folder}.core.toolbars')
info_button = importlib.import_module('.info_button', package=f'{giswater_folder}.core.toolbars.basic')


class MyButton5(maptool.GwMaptool):

    def __init__(self, icon_path, action_name, text, toolbar, action_group):

        self.icon_path = icon_path
        self.action_name = action_name
        self.text = text
        self.toolbar = toolbar
        self.action_group = action_group
        info_button.GwInfoButton(self.icon_path, self.action_name, self.text, self.toolbar, self.action_group)

