# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GeoMCE
 GeoMCE permet de mettre en forme descouches shape en vue des les impoprter 
 dans laplateforme nationale de géolocalisation des mesures compensatoire 
 environnementales prévue par la loi surlareconquète de la biodiveristé et
 des paysages du 16 aouit 2016
                              -------------------
        begin                : 2020-03-26
        git sha              : $Format:%H$
        copyright            : (C) 2020 by DREAL Auvergne-Rhône-Alpes
        email                : cedric.claude@developpement-durable.gouv.fr
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


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load GeoMCE class from file GeoMCE.

    :param iface: A QGIS interface instance.
    :type iface: QgisInterface
    """
    #
    from .GeoMCE import GeoMCE
    return GeoMCE(iface)
