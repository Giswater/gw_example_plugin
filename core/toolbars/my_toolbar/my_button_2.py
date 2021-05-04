"""
This file is part of Giswater 3
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-
import importlib
import sys
import os
from enum import Enum
from functools import partial

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QColor
from qgis.gui import QgsMapToolEmitPoint, QgsVertexMarker

from ...ui.ui_manager import DlgBoton2
from ....settings import giswater_folder, tools_log, tools_qgis, tools_qt, tools_gw
dialog = importlib.import_module('.dialog', package=f'{giswater_folder}.core.toolbars')
snap_manager = importlib.import_module('.snap_manager', package=f'{giswater_folder}.core.utils')

class SelectionType(Enum):
    ACTIVE = 0
    ALL = 1


# TODO: comprobar si se cierra bien la map tool o no
# TODO: comprobar si se restablece correctamente la configuracion de usuario
# TODO: limpiar, ordenar y comentar codigo
# TODO: mirate como funcionan los radiobuttons, hay mas formas

class MyButton2(dialog.GwAction):

    def __init__(self, icon_path, action_name, text, toolbar, action_group):

        super().__init__(icon_path, action_name, text, toolbar, action_group)
        self.vertex_marker = None
        self.emit_point = None


    def clicked_event(self):

        self.selection_type = SelectionType.ACTIVE
        self.dlg_btn2 = DlgBoton2()
        tools_gw.load_settings(self.dlg_btn2)

        # Secció: selecció de capes
        self.dlg_btn2.rdb_layers_active.clicked.connect(partial(self.selection_type_changed, SelectionType.ACTIVE))
        self.dlg_btn2.rdb_layers_all.clicked.connect(partial(self.selection_type_changed, SelectionType.ALL))

        # Secció: activar l'estat de "seleccionant al mapa"
        self.dlg_btn2.btn_select.clicked.connect(self.selection_start)
        self.dlg_btn2.btn_cancel.clicked.connect(self.deactivate_signals)
        self.dlg_btn2.btn_cancel.clicked.connect(lambda: self.dlg_btn2.rdb_layers_active.setEnabled(True))
        self.dlg_btn2.btn_cancel.clicked.connect(lambda: self.dlg_btn2.rdb_layers_all.setEnabled(True))
        # Secció: sortida
        self.dlg_btn2.btn_close.clicked.connect(self.dlg_btn2.close)
        self.dlg_btn2.rejected.connect(partial(tools_gw.save_settings, self.dlg_btn2))
        self.dlg_btn2.rejected.connect(partial(self.deactivate_signals))

        self.refresh_selection_type()

        tools_gw.open_dialog(self.dlg_btn2)


    def selection_type_changed(self, new_type):

        self.selection_type = SelectionType(new_type)
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

        self.is_selecting = True
        self.dlg_btn2.rdb_layers_active.setEnabled(False)
        self.dlg_btn2.rdb_layers_all.setEnabled(False)
        self.emit_point = QgsMapToolEmitPoint(self.canvas)
        self.canvas.setMapTool(self.emit_point)

        # Snapper
        self.snapper_manager = snap_manager.GwSnapManager(self.iface)
        self.snapper = self.snapper_manager.get_snapper()

        # Vertex marker
        self.vertex_marker = QgsVertexMarker(self.canvas)
        self.vertex_marker.setColor(QColor(255, 100, 255))
        self.vertex_marker.setIconSize(15)
        self.vertex_marker.setIconType(QgsVertexMarker.ICON_CROSS)
        self.vertex_marker.setPenWidth(3)

        # Store user snapping configuration
        self.previous_snapping = self.snapper_manager.get_snapping_options()

        if self.selection_type == SelectionType.ACTIVE:
            tools_log.log_info("single selector")
            self.activate_snapping(self.emit_point)
        elif self.selection_type == SelectionType.ALL:
            tools_log.log_info("all selector")
            # Store user snapping configuration
            if tools_qt.is_checked(self.dlg_btn2, self.dlg_btn2.chk_layer_arc) or \
                    tools_qt.is_checked(self.dlg_btn2, self.dlg_btn2.chk_layer_connec) or \
                    tools_qt.is_checked(self.dlg_btn2, self.dlg_btn2.chk_layer_node):
                self.set_user_config()
            self.activate_snapping(self.emit_point)


    def set_user_config(self):

        # Disable snapping
        self.snapper_manager.set_snapping_status()

        # Set snapping to 'arc', 'node', 'connec' and 'gully'
        self.snapper_manager.set_snapping_layers()

        if tools_qt.is_checked(self.dlg_btn2, self.dlg_btn2.chk_layer_arc):
            self.snapper_manager.config_snap_to_arc()

        if tools_qt.is_checked(self.dlg_btn2, self.dlg_btn2.chk_layer_connec):
            self.snapper_manager.config_snap_to_connec()

        if tools_qt.is_checked(self.dlg_btn2, self.dlg_btn2.chk_layer_node):
            self.snapper_manager.config_snap_to_node()

        self.snapper_manager.set_snap_mode()


    def activate_snapping(self, emit_point):

        # Set signals
        self.canvas.xyCoordinates.connect(self.canvas_move_event)
        emit_point.canvasClicked.connect(partial(self.canvas_release_event, emit_point))


    def canvas_move_event(self, point):

        # Get clicked point
        self.vertex_marker.hide()
        event_point = self.snapper_manager.get_event_point(point=point)
        if self.selection_type == SelectionType.ACTIVE:
            result = self.snapper_manager.snap_to_current_layer(event_point)
        elif self.selection_type == SelectionType.ALL:
            result = self.snapper_manager.snap_to_project_config_layers(event_point)

        if self.snapper_manager.result_is_valid() and result:
            self.snapper_manager.add_marker(result, self.vertex_marker)


    def canvas_release_event(self, emit_point, point, btn):

        if btn == Qt.RightButton:
            if btn == Qt.RightButton:
                tools_qgis.disconnect_snapping(False, emit_point, self.vertex_marker)
                return

        # Get coordinates
        event_point = self.snapper_manager.get_event_point(point=point)
        if self.selection_type == SelectionType.ACTIVE:
            result = self.snapper_manager.snap_to_current_layer(event_point)
        elif self.selection_type == SelectionType.ALL:
            result = self.snapper_manager.snap_to_project_config_layers(event_point)
        if result is None:
            return
        if not result.isValid():
            return

        layer = self.snapper_manager.get_snapped_layer(result)
        # Get the point. Leave selection
        snapped_feat = self.snapper_manager.get_snapped_feature(result)
        feature_id = self.snapper_manager.get_snapped_feature_id(result)
        snapped_point = self.snapper_manager.get_snapped_point(result)
        layer.select([feature_id])
        self.snapper_manager.restore_snap_options(self.previous_snapping)
        self.deactivate_signals()


    def deactivate_signals(self):

        if self.vertex_marker:
            self.vertex_marker.hide()

        try:
            self.canvas.xyCoordinates.disconnect()
        except TypeError:
            pass

        try:
            if self.emit_point:
                self.emit_point.canvasClicked.disconnect()
        except TypeError:
            pass

