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
#        self.label_3 = QtGui.QLabel(About)
#        self.label_3.setGeometry(QtCore.QRect(280, 0, 191, 41))
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
#        self.label_3.setFont(font)
#        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
#        self.label_3.setObjectName(_fromUtf8("label_3"))
#        self.label = QtGui.QLabel(About)
#        self.label.setGeometry(QtCore.QRect(220, 40, 311, 41))
        font = QtGui.QFont()
        font.setPointSize(9)
#        self.label.setFont(font)
#        self.label.setAlignment(QtCore.Qt.AlignCenter)
#        self.label.setObjectName(_fromUtf8("label"))
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
        self.webView.setProperty("zoomFactor", 0.699999988079)
        self.webView.setObjectName(_fromUtf8("webView"))

        self.retranslateUi(About)
        QtCore.QMetaObject.connectSlotsByName(About)

    def retranslateUi(self, About):
        About.setWindowTitle(_translate("A propos", "A propos/Aide", None))
        #self.label_3.setText(_translate("A propos", "GeoMCE v 0.1", None))
        #self.label.setText(_translate("A propos", "les copyright qui vont bien\n"
#" si ya\n"
#" besoin", None))
        self.textBrowser.setHtml(_translate("A propos", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Ubuntu\'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">GéoMCE v.0.1 - Version initiale</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">GéoMCE v.0.2 - Ajout du module d'aide</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Compatible avec Qgis v2.x seulement - développement pour Qgis v3.x en cours</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Plug-in qui permet la mise en forme des couches shapes dans un format compatible pour un import sur la plateforme GéoMCE (services de l'Etat)</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Les remarques/suggestions sont les bienvenues!</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Pour plus de renseignement sur la géolocalisation des mesures de compensations et GéoMCE : https://www.ecologique-solidaire.gouv.fr/biodiversite-nouvelle-version-geomce </p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Les mesures de compensations visibles sur Géoportail : https://www.geoportail.gouv.fr/donnees/mesures-compensatoires-des-atteintes-a-la-biodiversite </p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Les mesures de compensations téléchargeables via CeremaData : https://www.cdata.cerema.fr/geonetwork/srv/fre/catalog.search#/metadata/48ac3589-499d-4f42-9716-73b4eefef35c </p></body></html>", None))

from PyQt4 import QtWebKit
