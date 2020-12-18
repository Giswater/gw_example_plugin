"""
This file is part of Giswater 3
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-
import os, sys
from qgis.PyQt.QtCore import Qt



sys.path.append(os.path.abspath('../giswater'))
from giswater.core.toolbars.parent_dialog import GwParentAction
from giswater.core.toolbars.parent_maptool import GwParentMapTool




class MyBoton2(GwParentMapTool):


    def __init__(self, icon_path, action_name, text, toolbar, action_group):
        """ Class constructor """

        super().__init__(icon_path, action_name, text, toolbar, action_group)

    """ QgsMapTools inherited event functions """
    def activate(self):
        print(f"ACTIVATE")

    def canvasMoveEvent(self, event):
        pass


    def canvasReleaseEvent(self, event):
        pass


    def keyPressEvent(self, event):

        if event.key() == Qt.Key_Escape:
            self.action.trigger()
            return