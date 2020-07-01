# -*- coding: utf-8 -*-

import sys,os
from PyQt5 import QtCore, QtGui, QtWidgets, QtWebKitWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebKit import *
from PyQt5.QtWebKitWidgets import QWebView
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtWidgets.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context, text, disambig)

class Ui_About(object):
    def setupUi(self, About):
        About.setObjectName(_fromUtf8("A propos"))
        About.resize(950, 900)
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label_2 = QtWidgets.QLabel(About)
        self.label_2.setGeometry(QtCore.QRect(0, 0, 950, 131))
        self.label_2.setText(_fromUtf8(""))
        self.label_2.setPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/GeoMCE/geomce.png")))
        self.label_2.setScaledContents(True)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.webView = QtWebKitWidgets.QWebView(About)
        file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "aide.html"))
        self.webView.setGeometry(QtCore.QRect(20, 141, 910, 730))
        self.webView.setProperty("url", QUrl.fromLocalFile(file_path))
        self.webView.setProperty("zoomFactor", 1)
        self.webView.setObjectName(_fromUtf8("webView"))
        QtCore.QMetaObject.connectSlotsByName(About)

from PyQt5 import QtWebKit