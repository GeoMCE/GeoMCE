from PyQt4 import QtCore, QtGui
from about import Ui_About
# create the dialog
class AboutDialog(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        # Set up the user interface from Designer.
        self.ui =Ui_About()
        self.ui.setupUi(self)


