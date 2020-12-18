# -*- coding: utf-8 -*-
"""
/***************************************************************************
        begin                : 2016-01-05
        copyright            : (C) 2016 by BGEO SL
        email                : derill@bgeo.es
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""
import os
import sys
plugin_path = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.append(plugin_path)



def classFactory(iface): 
    """ Load Giswater class from file giswater.
    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    from .main import GWPluginExample
    return GWPluginExample(iface)
