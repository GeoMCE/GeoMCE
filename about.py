# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QUrl
import os
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_About(object):
    def setupUi(self, About):
        About.setObjectName(_fromUtf8("A propos"))
        About.resize(810, 559)
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.textBrowser = QtGui.QTextBrowser(About)
        self.textBrowser.setGeometry(QtCore.QRect(20, 100, 761, 151))
        self.textBrowser.setObjectName(_fromUtf8("textBrowser"))
        self.label_2 = QtGui.QLabel(About)
        self.label_2.setGeometry(QtCore.QRect(0, 0, 810, 93))
        self.label_2.setText(_fromUtf8(""))
        self.label_2.setPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/GeoMCE/geomce.png")))
        self.label_2.setScaledContents(True)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.webView = QtWebKit.QWebView(About)
        file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "aide.html"))
        self.webView.setGeometry(QtCore.QRect(20, 270, 771, 271))
        self.webView.setProperty("url", QUrl.fromLocalFile(file_path))
        self.webView.setProperty("zoomFactor", 1)
        self.webView.setObjectName(_fromUtf8("webView"))
        self.retranslateUi(About)
        QtCore.QMetaObject.connectSlotsByName(About)

    def retranslateUi(self, About):
        About.setWindowTitle(_translate("A propos", "Aide - A propos", None))
        self.textBrowser.setHtml(_translate("A propos", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Ubuntu\'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Plug-in qui permet la mise en forme des couches shapes dans un format compatible pour un import sur la plateforme GéoMCE (services de l'Etat)</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Compatible avec Qgis v2.x seulement - développement pour Qgis v3.x en cours</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Changelog :</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"> - v.0.6 - Retouches cosmétiques</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"> - v.0.5 - (Gros) Nettoyage du code et ajout d'explications des fonctions</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"> - v.0.4 - Modification de la fonction de séparation des couches : le nom du dossier crée est maintenant horodaté et mentionne également le champ séparateur. Permet de créer un dossier par manipulation</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"> - v.0.3 - Amélioration de la fonction de suppression des champs existants par itération</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"> - v.0.2 - Corrections mineurs / Ajout du module d'aide</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"> - v.0.1 - Version initiale</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Les remarques/suggestions sont les bienvenues!</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">\nPour plus de renseignement sur la géolocalisation des mesures de compensations et GéoMCE : https://www.ecologique-solidaire.gouv.fr/biodiversite-nouvelle-version-geomce </p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Les mesures de compensations visibles sur Géoportail : https://www.geoportail.gouv.fr/donnees/mesures-compensatoires-des-atteintes-a-la-biodiversite </p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Les mesures de compensations téléchargeables via CeremaData : https://www.cdata.cerema.fr/geonetwork/srv/fre/catalog.search#/metadata/48ac3589-499d-4f42-9716-73b4eefef35c </p></body></html>", None))

from PyQt4 import QtWebKit