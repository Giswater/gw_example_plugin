"""
This file is part of Giswater 3
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-
import sys, os
sys.path.append(os.path.abspath('../giswater'))

from qgis.PyQt.QtCore import Qt

from giswater.core.toolbars.maptool_button import GwMaptoolButton
from giswater.core.utils import tools_gw
from giswater.lib import tools_qt
from giswater.core.toolbars.basic import info_btn
from giswater.core.shared import info


class MyBoton5(GwMaptoolButton):

    def __init__(self, icon_path, action_name, text, toolbar, action_group):

        # super().__init__(icon_path, action_name, text, toolbar, action_group)
        self.icon_path = icon_path
        self.action_name = action_name
        self.text = text
        self.toolbar = toolbar
        self.action_group = action_group

        GwInfo = info_btn.GwInfoButton(self.icon_path, self.action_name, self.text, self.toolbar, self.action_group)


    """ QgsMapTools inherited event functions """
    def activate(self):
        print(f"ACTIVATE")

    def canvasMoveEvent(self, event):
        pass

    def canvasReleaseEvent(self, event):
        print("CANVAS RE")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.action.trigger()
            return

