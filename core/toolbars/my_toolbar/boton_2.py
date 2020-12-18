"""
This file is part of Giswater 3
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-
import sys
import os

from enum import Enum
from functools import partial

from qgis.PyQt.QtCore import Qt

from qgis.utils import iface

from ...ui.ui_manager import DlgBoton2

sys.path.append(os.path.abspath('../giswater'))

from giswater.core.toolbars.parent_dialog import GwParentAction
from giswater.core.toolbars.parent_maptool import GwParentMapTool
from giswater.core.utils import tools_gw
from giswater.lib import tools_qgis, tools_qt


class SelectionType(Enum):
    ACTIVE = 0
    ALL = 1


class MyBoton2(GwParentAction):

    def __init__(self, icon_path, action_name, text, toolbar, action_group):
        self.dlg_btn2 = None
        self.is_selecting = False
        self.selection_type = SelectionType.ACTIVE

        super().__init__(icon_path, action_name, text, toolbar, action_group)

    def clicked_event(self):
        self.dlg_btn2 = DlgBoton2()
        tools_gw.load_settings(self.dlg_btn2)

        # Secció: selecció de capes
        self.dlg_btn2.rdb_layers_active.clicked.connect(partial(self.selection_type_changed, SelectionType.ACTIVE))
        self.dlg_btn2.rdb_layers_all.clicked.connect(partial(self.selection_type_changed, SelectionType.ALL))

        # Secció: activar l'estat de "seleccionant al mapa"
        self.dlg_btn2.btn_select.clicked.connect(self.selection_start)

        # Secció: sortida
        self.dlg_btn2.btn_close.clicked.connect(self.dlg_btn2.close)
        self.dlg_btn2.rejected.connect(self.close_dialog)

        self.refresh_selection_type()

        tools_gw.open_dialog(self.dlg_btn2)
        tools_qgis.enable_python_console()

    def selection_type_changed(self, new_type):
        self.selection_type = SelectionType(new_type)
        print(f"Selection type changed to { SelectionType(new_type) }")

        self.refresh_selection_type()

    def refresh_selection_type(self):
        if self.selection_type == SelectionType.ACTIVE:
            self.dlg_btn2.chk_layer_arc.setEnabled(False)
            self.dlg_btn2.chk_layer_connec.setEnabled(False)
            self.dlg_btn2.chk_layer_node.setEnabled(False)
        else:
            self.dlg_btn2.chk_layer_arc.setEnabled(True)
            self.dlg_btn2.chk_layer_connec.setEnabled(True)
            self.dlg_btn2.chk_layer_node.setEnabled(True)

    def selection_start(self):
        print(f"Selection state started")

        self.is_selecting = True

        self.dlg_btn2.rdb_layers_active.setEnabled(False)
        self.dlg_btn2.rdb_layers_all.setEnabled(False)
        self.dlg_btn2.btn_select.setEnabled(False)

        if self.selection_type == SelectionType.ACTIVE:
            tools_qgis.manage_snapping_layer(iface.activeLayer())

        self.parent_maptool = GwParentMapTool
        self.snapper_manager = self.parent_maptool.snapper_manager
        self.snapper_manager.set_snapping_layers()

        # Store user snapping configuration
        self.previous_snapping = self.snapper_manager.get_snapping_options()
        # Disable snapping
        self.snapper_manager.enable_snapping()
        # Set snapping to 'node', 'connec' and 'gully'
        self.snapper_manager.set_snapping_layers()
        self.snapper_manager.snap_to_node()
        self.snapper_manager.snap_to_connec()
        self.snapper_manager.snap_to_gully()
        self.snapper_manager.set_snap_mode()

    def selection_end(self):
        print(f"Selection state ended")

        self.is_selecting = False

        tools_qt.show_info_box("Has punxat al punt ? de la capa ?. (X: ?, Y: ?)", "Fi de la selecció")

    def close_dialog(self):
        print("Dialog is closing...")

        partial(tools_gw.save_settings, self.dlg_btn2)

        # Desactivem el mode
        if self.is_selecting:
            print("Was in selection mode: deactivate snapping")

    # """ QgsMapTools inherited event functions """
    # def activate(self):
    #     print(f"ACTIVATE")
    #
    # def canvasMoveEvent(self, event):
    #     pass
    #
    # def canvasReleaseEvent(self, event):
    #     event_point = self.snapper_manager  .get_event_point(event)
    #
    # def keyPressEvent(self, event):
    #
    #     if event.key() == Qt.Key_Escape:
    #         self.action.trigger()
    #         return
