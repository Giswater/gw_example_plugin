"""
This file is part of Giswater 3
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-
import importlib
import os, sys
from functools import partial

from qgis.core import QgsVectorLayer
from qgis.utils import iface

from ...ui.ui_manager import DlgBoton1
from ....settings import giswater_folder
dialog_button = importlib.import_module('.dialog_button', package=f'{giswater_folder}.core.toolbars')
tools_qgis = importlib.import_module('.tools_qgis', package=f'{giswater_folder}.lib')
tools_qt = importlib.import_module('.tools_qt', package=f'{giswater_folder}.lib')
tools_gw = importlib.import_module('.tools_gw', package=f'{giswater_folder}.core.utils')


class MyBoton1(dialog_button.GwDialogButton):

    def __init__(self, icon_path, action_name, text, toolbar, action_group):
        super().__init__(icon_path, action_name, text, toolbar, action_group)


    def clicked_event(self):

        self.dlg_btn1 = DlgBoton1()
        tools_gw.load_settings(self.dlg_btn1)
        self.dlg_btn1.rejected.connect(partial(tools_gw.save_settings, self.dlg_btn1))
        self.dlg_btn1.btn_close.clicked.connect(self.dlg_btn1.close)
        self.dlg_btn1.cmb_layers.currentIndexChanged.connect(self.set_active_layer)
        self.dlg_btn1.btn_selection.clicked.connect(self.selection_init)

        self.fill_combo_layers()

        tools_gw.open_dialog(self.dlg_btn1)


    def selection_init(self):

        # Fem que l'eina de selecció estigui activa
        iface.actionSelect().trigger()

        # Listeners d'Events
        iface.mapCanvas().selectionChanged.connect(self.selection_changed)


    def selection_changed(self) -> None:

        try:
            # Obtenim una llista de les Features seleccionades a la capa activa del mapa
            layer = iface.activeLayer()
            if not layer: return
            selected_features = layer.selectedFeatures()

            # Revisem si l'usuari no ha seleccionat res, en aquest cas deixem d'executar
            if len(selected_features) == 0:
                return

            list_ids = []

            # Desem l'ID de l'últim Feature seleccionat i ho mostrem a la consola
            for i in selected_features:
                attr_id = i.attribute("node_id")
                list_ids.append(attr_id)

            tools_qt.set_widget_text(self.dlg_btn1, self.dlg_btn1.lbl_selected_items, ','.join(list_ids))

        except Exception as e:
            print(f"EXCEPTION: {type(e).__name__}, {e}")

        finally:
            # Tanquem la subscripció de l'event per evitar la duplicació
            iface.mapCanvas().selectionChanged.disconnect(self.selection_changed)


    def set_active_layer(self):

        print("activar seleccion sobre la capa seleccionada")
        layer = tools_qt.get_combo_value(self.dlg_btn1, self.dlg_btn1.cmb_layers, 0)
        if type(layer) != QgsVectorLayer:
            msg = "Invalid layer"
            tools_gw.show_warning(msg)
            return
        iface.setActiveLayer(layer)


    def fill_combo_layers(self):

        lyrs = tools_qgis.get_visible_layers(True)
        lyrs = lyrs.replace("[", "")
        lyrs = lyrs.replace("]", "")
        lyrs = lyrs.replace('"', '')
        lyrs = list(lyrs.split(", "))
        layers = [["", ""]]
        for l in list(lyrs):
            layer = tools_qgis.get_layer_by_tablename(l)
            elem = [layer, layer.name()]
            layers.append(elem)

        tools_qt.fill_combo_values(self.dlg_btn1.cmb_layers, layers, 1)

