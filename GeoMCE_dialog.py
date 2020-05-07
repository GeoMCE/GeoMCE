# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GeoMCEDialog
                                 A QGIS plugin
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
"""

import os

from PyQt5 import QtGui, uic, QtWidgets
#from .GeoMCE_dialog import GeoMCEDialog

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'GeoMCE_dialog_base.ui'))


class GeoMCEDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(GeoMCEDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

