# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GeoMCE
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
from __future__ import absolute_import
from builtins import str
from builtins import range
from builtins import object
from PyQt5.QtCore import *
from PyQt5 import QtWidgets
from PyQt5.QtGui import *
from qgis.core import *
from qgis.gui import *
from qgis.PyQt.QtGui import *
from qgis.utils import *
from PyQt5.QtWidgets import QAction, QDialog, QFormLayout, QFileDialog, QProgressBar, QListWidgetItem
import  os, processing, fnmatch, sys, glob, datetime, unicodedata, zipfile, os.path
# Import the code for the dialog
from .GeoMCE_dialog import GeoMCEDialog
from .aboutdialog import AboutDialog
from .resources import *
from os.path import basename


class GeoMCE(object):
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgisInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'GeoMCE_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        self.dlg = GeoMCEDialog()
        self.dlga = AboutDialog()
        #initialization for select features
        self.turnedoffLayers = []
        self.selectList = []
        self.cLayer = None
        self.provider = None
        self.saved = False
        self.countchange = 0
        selectall = 0

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&GeoMCE')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'GeoMCE')
        self.toolbar.setObjectName(u'GeoMCE')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('GeoMCE', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        # Create the dialog (after translation) and keep reference
        self.dlg = GeoMCEDialog()

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToVectorMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS G"""

        icon_path = ':/plugins/GeoMCE/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'GeoMCE'),
            callback=self.run,
            parent=self.iface.mainWindow())
        valcom = self.get_communes()
        self.dlg.communes.setText(valcom)
        valtamponpoint = self.distance_tampon_point_read()
        valtamponligne = self.distance_tampon_ligne_read()
        self.checkBox_read()
        self.tampon_read()
        self.dlg.fusion.clicked.connect(self.fusion)
        self.dlg.checkBox.stateChanged.connect(self.checkBox_write)
        self.dlg.checkBox.stateChanged.connect(self.checkBox_read)
        self.dlg.tampon.stateChanged.connect(self.tampon_write)
        self.dlg.tampon.stateChanged.connect(self.tampon_read)
        self.dlg.mMapLayerComboBox_2.currentIndexChanged.connect(self.set_select_attributes)
        self.dlg.mMapLayerComboBox.currentIndexChanged.connect(self.set_select_attributes)
        self.dlg.save.clicked.connect(self.save_edits)
        self.dlg.show_t.clicked.connect(self.show_table)
        self.dlg.show_t_2.clicked.connect(self.show_table_2)
        self.dlg.create_new_field.clicked.connect(self.newfield_connect)
        self.dlg.create_new_field_2.clicked.connect(self.newfield_connect_2)
        self.dlg.change_another.clicked.connect(self.change_to_any)
        self.dlg.pushButton.clicked.connect(self.select_output_file_store)
        self.dlg.pushButton_3.clicked.connect(self.select_save_folder)
        self.dlg.about.clicked.connect(self.doabout)
        #self.dlg.nom.setPlaceholderText(u'Nom de la mesure - 100 caractères max')
        #self.dlg.description.setPlaceholderText(u'Description de la mesure - 254 caractères max')
        #self.dlg.decision.setPlaceholderText(u'Références de l\'acte et de l\'article prescrivant la mesure - 254 caractères max')
        #self.dlg.refei.setPlaceholderText(u'Références à l\'étude d\'impact décrivant la mesure - 254 caractères max')
        #self.dlg.faunes.setDefaultText(u'Espèces animales concernées par la mesure - Respecter la casse des noms latins - 254 caractères max')
        #self.dlg.flores.setPlaceholderText(u'Espèces végétales concernées par la mesure - Respecter la casse des noms latins - 254 caractères max')
        #self.dlg.echeances.setPlaceholderText(u'Libéllé de la mesure de suivi - 254 caractères max')
        self.listWidget()
        QgsProject.instance().layersAdded.connect(self.listWidget)
        QgsProject.instance().layersRemoved.connect(self.listWidget)
        self.dlg.Exit.clicked.connect(self.exit)
        self.dlg.Exit_2.clicked.connect(self.exit)
        self.dlg.zipbutton.clicked.connect(self.archive)
        self.dlg.zipbutton_2.clicked.connect(self.archive_2)
        self.dlg.dossier.clicked.connect(self.dossier)
        self.dlg.dossier_2.clicked.connect(self.dossier_2)
        self.dlg.sauvegarder_tampon.clicked.connect(self.sauv_dist_tampon)

    def checkBox_write(self):
        s = QSettings()
        s.setValue('/GeoMCE-Sortie_shp', self.dlg.checkBox.isChecked())
        self.iface.messageBar().pushMessage(u'GéoMCE',u'Paramètre sauvegardé', level=Qgis.Info, duration=3)
            
    def checkBox_read(self):
        s = QSettings()
        self.dlg.checkBox.setChecked(s.value('/GeoMCE-Sortie_shp', False, type=bool))

    def tampon_write(self):
        s = QSettings()
        s.setValue('/GeoMCE-tampon', self.dlg.tampon.isChecked())
        self.iface.messageBar().pushMessage(u'GéoMCE',u'Paramètre sauvegardé', level=Qgis.Info, duration=3)

    def tampon_read(self):
        s = QSettings()
        self.dlg.tampon.setChecked(s.value('/GeoMCE-tampon', False, type=bool))
		
    def distance_tampon_point_read(self):
        s = QSettings()
        self.dlg.distance_tampon_point.setValue(s.value('/GeoMCE-distance_tampon_point', True, type=int))

    def distance_tampon_ligne_read(self):
        s = QSettings()
        self.dlg.distance_tampon_ligne.setValue(s.value('/GeoMCE-distance_tampon_ligne', True, type=int))
        
#fonctions personnalisees-------------------------------------------------------------------------------------------------------------
#fonctions generale-------------------------------------------------------------------------------------------------------------------
#verification si couche vecteur sont chargees
    def checkvector(self):
        count = 0
        for name, layer in QgsProject.instance().mapLayers().items():
            if layer.type() == QgsMapLayer.VectorLayer:
                count += 1
        return count
           
# fonction relative a splitlayer vector-----------------------------------------------------------------------------------------------
 #chemin d enregistrement du traitement splitvectorlayer 
    def select_save_folder(self):
        qfd_1 = QFileDialog()
        title_1 = u'T\'enregistres ça où?'
        path_1 = ""
        filename = QFileDialog.getExistingDirectory(qfd_1, title_1, path_1)
        self.dlg.enregistrement.setText(filename) 
 
 #on recupere le chemin du dossier d enregistrement du traitement pour plus tard
    def get_enregistrement(self):
        chemin_couche = self.dlg.mMapLayerComboBox_2.currentLayer()
        source_chemin_couche = chemin_couche.dataProvider().dataSourceUri() 
        chemin_couche_separer = os.path.dirname(source_chemin_couche)      
        if self.dlg.enregistrement.text() =="":
            new_enregistrement = chemin_couche_separer        
        else:
               new_enregistrement = self.dlg.enregistrement.text()
        return new_enregistrement

 #choix de la couche a pour traitement splitlayervector
    def chooselayer(self):
        self.dlg.mMapLayerComboBox_2.clear()
        self.dlg.mMapLayerComboBox.clear()
        self.dlg.mFieldComboBox.clear()
        self.dlg.mMapLayerComboBox.setFilters(QgsMapLayerProxyModel.VectorLayer)        
        layerlist=[]
        slist=[]
        layers = [layer for layer in QgsProject.instance().mapLayers().values()]
        for layer in layers:
            layerType = layer.type()
            if layerType == QgsMapLayer.VectorLayer:
                self.dlg.mMapLayerComboBox_2.addItem(layer.name())
        self.set_select_attributes()

 #choix du champ separateur pour fonction splitlayervector
    def set_select_attributes(self):
        self.dlg.mMapLayerComboBox_2.clear()
        self.dlg.mMapLayerComboBox_2.setFilters(QgsMapLayerProxyModel.VectorLayer)        
        self.dlg.mFieldComboBox.clear()
        if self.dlg.mMapLayerComboBox.currentText() != "":
            layername = self.dlg.mMapLayerComboBox.currentText()
            for name, selectlayer in QgsProject.instance().mapLayers().items():
                if selectlayer.name() == layername:
                    for field in selectlayer.dataProvider().fields():
                        self.dlg.mFieldComboBox.addItem(field.name())

 #on connecte le champ en fonction de la couche a séparer
    def select_layer_fields2(self, vlayer): 
        self.dlg.mFieldComboBox.setLayer(vlayer)
        field = self.dlg.mFieldComboBox.setLayer(vlayer)
        
    def newfield_connect(self):
        self.create_new_field()
        self.set_select_attributes()
        return

    def newfield_connect_2(self):
        self.create_new_field_2()
        self.set_select_attributes()
        return

 #on lance splitlayervector   
    def create_new_field(self) :
        #creation d un dossier dans C: nomme GeoMCE et d un sous dossier horodate qui va porter le nom de la couche + le nom du champ separateur qui va etre traiter
        couche = self.dlg.mMapLayerComboBox_2.currentText()
        champ = self.dlg.mFieldComboBox.currentText()
        path = self.get_enregistrement()
        p = path + "/" + datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + "_" + couche + "_" + champ 
        os.makedirs(p)    
                  
        #separation de la couche active par le champ defini au debut du script et enregistrement dans le dossier choisi par lafonction get_enregistrement. Attention, QGIS3 genere par defaut des fichiers geopackage sauf qu on veut du shape ...
        split = processing.run("qgis:splitvectorlayer", {'INPUT':self.dlg.mMapLayerComboBox_2.currentText(),'FIELD': self.dlg.mFieldComboBox.currentText(), 'OUTPUT' : p})

        #permet de scanner le dossier de get_enregistrement
        def find_files(directory, pattern, only_root_directory):
            for root, dirs, files in os.walk(directory):
                for basename in files:
                    if fnmatch.fnmatch(basename.lower(), pattern):
                        filename = os.path.join(root, basename)
                        yield filename
                if (only_root_directory):
                    break
        if self.dlg.checkBox.isChecked():
            #... puis on scanne le dossier a la recherche des shapes et on les charge dans l interface
            count = 0
            for src_file in find_files(p, '*.shp', True):
                (head, tail) = os.path.split(src_file)
                (name, ext) = os.path.splitext(tail)
                vlayer = iface.addVectorLayer(src_file, name, "ogr")
            output = count
        else :
            count = 0
            for src_file in find_files(p, '*.gpkg', True):
                (head, tail) = os.path.split(src_file)
                (name, ext) = os.path.splitext(tail)
                vlayer = QgsVectorLayer(src_file, name, "ogr")
                #...et on les convertis en shape ...
                QgsVectorFileWriter.writeAsVectorFormat(vlayer,p+ "/" + vlayer.name(), 'UTF-8',vlayer.crs(), 'ESRI Shapefile')
            output = count
            #... puis on scanne le dossier a la recherche des shapes et on les charge dans l interface
            count = 0
            for src_file in find_files(p, '*.shp', True):
                (head, tail) = os.path.split(src_file)
                (name, ext) = os.path.splitext(tail)
                vlayer = iface.addVectorLayer(src_file, name, "ogr")
            output = count
        self.dlg.mFieldComboBox.clear()
        self.dlg.mMapLayerComboBox_2.clear()  
        self.iface.messageBar().pushMessage(u'GéoMCE',u'Les nouvelles couches ont été créées dans le dossier ' + self.get_enregistrement() + u' et chargées dans l\'interface', level=Qgis.Info, duration=3)

#fonctions assurant la mise en forme des couches pour un import dans GeoMCE---------------------------------------------------------------
 #choix de la couche a traiter
    def chooselayer_2(self):
        self.dlg.mMapLayerComboBox.clear()
        Layers = [layer for layer in QgsProject.instance().mapLayers().values()]
        Layer_list = []
        for layer in Layers:
            Layer_list.append (layer.name())
            self.dlg.mMapLayerComboBox.addItems(Layer_list)
        self.set_select_attributes()

 #on efface tous les champs existants et on cree ceux qui permettent un import dans GeoMCE        
    def create_new_field_2(self):
        self.dlg.mMapLayerComboBox.clear()
        layer = self.dlg.mMapLayerComboBox.currentLayer()
        layer.startEditing()
        #on efface tout les champs existants...
        prov = layer.dataProvider()
        field_names = [field.name() for field in prov.fields()]
        for count, f in enumerate(field_names):
            jean = range(count, count +1 )
            paul = range(count)
            jeanpaul = list(range(count, count +1 )) + list (range(count))
        layer.dataProvider().deleteAttributes(jeanpaul)

        #... et creation des nouveaux champs compatibles avec un import dans GeoMCE 
        layer.dataProvider().addAttributes(
                    [QgsField("id", QVariant.Int,'Integer64',10,0),
                    QgsField("nom", QVariant.String,'String',100,0),
                    QgsField("categorie", QVariant.String,'String',7,0),
                    QgsField("cible", QVariant.String,'String',100,0),
                    QgsField("descriptio", QVariant.String,'String',254,0),
                    QgsField("decision", QVariant.String,'String',254,0),
                    QgsField("refei", QVariant.String,'String',254,0),
                    QgsField("duree", QVariant.String,'String',25,0),
                    QgsField("unite", QVariant.String,'String',25,0),
                    QgsField("modalite", QVariant.String,'String',50,0),
                    QgsField("cout",QVariant.Int,'Integer64', 10,0),
                    QgsField("montant_pr",QVariant.Int,'Integer64', 10,0),
                    QgsField("faunes",QVariant.String, 'String', 254,0),
                    QgsField("flores",QVariant.String, 'String', 254,0),
                    QgsField("echeances",QVariant.String, 'String', 254,0),
                    QgsField("communes", QVariant.String,'String',220,0)])         
        layer.updateFields()
        layer.selectAll()
        self.iface.messageBar().pushMessage(u'GéoMCE',u'Tout a été effacé, j\'espère que tu ne le regretteras pas!', level=Qgis.Info, duration=5)
        return

#les champs de saisi texte et listes deroulantes.Les caracteres speciaux sont remplaces par leurequivalant sans   
    def get_new_nom(self):
        new_nom = ''.join((c for c in unicodedata.normalize('NFD', self.dlg.nom.text()) if unicodedata.category(c) != 'Mn'))
        return new_nom
    def get_description(self):
        new_val_description = ''.join((c for c in unicodedata.normalize('NFD', self.dlg.description.text()) if unicodedata.category(c) != 'Mn'))
        return new_val_description
    def get_decision(self):
        new_val_decicision = ''.join((c for c in unicodedata.normalize('NFD', self.dlg.decision.text()) if unicodedata.category(c) != 'Mn'))
        return new_val_decicision
    def get_refei(self):
        new_val_refei = ''.join((c for c in unicodedata.normalize('NFD', self.dlg.refei.text()) if unicodedata.category(c) != 'Mn'))
        return new_val_refei
    def get_duree(self):
        new_val_duree = self.dlg.duree.text()
        return new_val_duree
    def get_categorie(self):
        #on s assure de ne recuperer que les codes et pas le texte complet : l'import dan l outil etant limite a 7 caracteres max
        numero_categorie = [u'E',u'E1',u'E1-1.',u'E1-1-a.',u'E1-1-b.',u'E1-1-c.',u'E1-1-d.',u'E2',u'E2-1.',u'E2-1-a.',u'E2-1-b.',u'E2-1-c.',u'E2-2.',u'E2-2-a.',u'E2-2-b.',u'E2-2-c.',u'E2-2-d.',u'E2-2-e.',u'E2-2-f.',u'E2-2-g.',u'E3',u'E3-1.',u'E3-1-a.',u'E3-1-b.',u'E3-2.',u'E3-2-a.',u'E3-2-b.',u'E3-2-c.',u'E4',u'E4-1.',u'E4-1-a.',u'E4-1-b.',u'E4-1-c.',u'E4-2.',u'E4-2-a.',u'E4-2-b.',u'E4-2-c.',u'-',u'R',u'R1',u'R1-1.',u'R1-1-a.',u'R1-1-b.',u'R1-1-c.',u'R1-1-d.',u'R1-2.',u'R1-2-a.',u'R1-2-b.',u'R1-2-c.',u'R2',u'R2-1.',u'R2-1-a.',u'R2-1-b.',u'R2-1-c.',u'R2-1-d.',u'R2-1-e.',u'R2-1-f.',u'R2-1-g.',u'R2-1-h.',u'R2-1-i.',u'R2-1-j.',u'R2-1-k.',u'R2-1-l.',u'R2-1-m.',u'R2-1-n.',u'R2-1-o.',u'R2-1-p.',u'R2-1-q.',u'R2-1-r.',u'R2-1-s.',u'R2-1-t.',u'R2-1-t.',u'R2-2.',u'R2-2-a.',u'R2-2-b.',u'R2-2-c.',u'R2-2-d.',u'R2-2-e.',u'R2-2-f.',u'R2-2-g.',u'R2-2-h.',u'R2-2-i.',u'R2-2-j.',u'R2-2-k.',u'R2-2-l.',u'R2-2-m.',u'R2-2-n.',u'R2-2-o.',u'R2-2-p.',u'R3',u'R3-1.',u'R3-1-a.',u'R3-1-b.',u'R3-1-c.',u'R3-2.',u'R3-2-a.',u'R3-2-b.',u'R3-2-c.',u'-',u'C',u'C1',u'C1-1.',u'C1-1-a.',u'C1-1-b.',u'C1-1-c.',u'C2',u'C2-1.',u'C2-1-a.',u'C2-1-b.',u'C2-1-c.',u'C2-1-d.',u'C2-1-e.',u'C2-1-f.',u'C2-1-g.',u'C2-1-h.',u'C2-2.',u'C2-2-a.',u'C2-2-b.',u'C2-2-c.',u'C2-2-d.',u'C2-2-e.',u'C2-2-f.',u'C2-2-g.',u'C2-2-h.',u'C2-2-i.',u'C2-2-j.',u'C2-2-k.',u'C3',u'C3-1.',u'C3-1-a.',u'C3-1-b.',u'C3-1-c.',u'C3-1-d.',u'C3-2.',u'C3-2-a.',u'C3-2-b.',u'C3-2-c.',u'C3-2-d.',u'C3-2-e.',u'-',u'A',u'A1',u'A1-1.',u'A1-1-a.',u'A1-2.',u'A1-2-a.',u'A2',u'A2-1.',u'A2-1-a.',u'A2-1-b.',u'A2-1-c.',u'A2-1-d.',u'A3',u'A3-1.',u'A3-1-a.',u'A3-1-b.',u'A3-1-c.',u'A4',u'A4-1.',u'A4-1-a.',u'A4-1-b.',u'A4-1-c.',u'A4-1-d.',u'A4-2.',u'A4-2-a.',u'A4-2-b.',u'A4-2-c.',u'A4-2-d.',u'A5',u'A5-1.',u'A5-1-a.',u'A5-1-b.',u'A5-1-c.',u'A6',u'A6-1.',u'A6-1-a.',u'A6-1-b.',u'A6-1-c.',u'A6-2.',u'A6-2-a.',u'A6-2-b.',u'A6-2-c.',u'A6-2-d.',u'A6-2-e.',u'A7',u'A7-1.',u'A7-1-a.']
        new_val_categorie = self.dlg.comboBox.currentIndex()
        index = numero_categorie[new_val_categorie]
        return index
    def get_cible(self):
        new_val_cible = self.dlg.comboBox_2.currentText()
        return new_val_cible
    def get_unite(self):
        new_val_unite = self.dlg.comboBox_3.currentText()
        return new_val_unite
    def get_modalite(self):
        new_val_modalite = self.dlg.comboBox_4.currentText()
        return new_val_modalite
    def get_communes(self):
        s = QSettings()
        new_val_communes = s.value('/GeoMCE-chemin_communes.shp')
        self.dlg.communes.setText(new_val_communes)
        return new_val_communes
    def get_cout(self):
        new_val_cout = self.dlg.cout.text()
        return new_val_cout
    def get_montant(self):
        new_val_montant = self.dlg.montant.text()
        return new_val_montant
    def get_faunes(self):
        new_val_faunes = self.dlg.faunes.currentText()
        return new_val_faunes
    def get_flores(self):
        new_val_flores = self.dlg.flores.currentText()
        return new_val_flores
    def get_echeances(self):
        new_val_echeances = ''.join((c for c in unicodedata.normalize('NFD', self.dlg.echeances.text()) if unicodedata.category(c) != 'Mn'))
        return new_val_echeances
    def distance_tampon_point(self):
        s= QSettings()
        new_val_distance_point =  self.dlg.distance_tampon_point.text()
        s.setValue('/GeoMCE-distance_tampon_point', new_val_distance_point)  
        return new_val_distance_point		
    def distance_tampon_ligne(self):
        s= QSettings()
        new_val_distance_ligne = self.dlg.distance_tampon_ligne.text()
        s.setValue('/GeoMCE-distance_tampon_ligne', new_val_distance_ligne)  
        return new_val_distance_ligne

    def sauv_dist_tampon(self):
        self.distance_tampon_ligne()
        self.distance_tampon_point()	
        self.iface.messageBar().pushMessage(u'GéoMCE',u'Paramètres sauvegardés', level=Qgis.Info, duration=3)
        
 #on va chercher le fichier commune.shp pour recuperer le code insee et on l enregistre dans le fichier de configuration de QGIS
    def select_output_file_store(self, text):
        s= QSettings()
        filename, _filter = QFileDialog.getOpenFileName(self.dlg, u'Il est où ton fichier Commune.shp?',"", '*.shp')
        self.dlg.communes.setText(filename)
        s.setValue('/GeoMCE-chemin_communes.shp', filename)
        self.iface.messageBar().pushMessage(u'GéoMCE',u'La couche '+ filename + u' est paramétrée comme couche COMMUNES par défaut', level=Qgis.Info, duration=3)
        
 #selection des toutes les entites de la couche
    def select_all(self):
        self.selectall = 0
        layername = self.dlg.mMapLayerComboBox.currentLayer()
        for name, selectlayer in QgsProject.instance().mapLayers().items():
            if selectlayer.name() == layername:
                selectlayer.setSelectedFeatures([])
                selectlayer.invertSelection()
                self.selectall = 1

        #permet de recuperer le code INSEE des communes concernes par la mesure. Necessite de changer les champs compare_field_index, concat_field_index et new_field_index en fonction du shape commune.
    def codeinsee(self):
        #ici se trouve le chemin vers couche contenant toutes les communes de votre region. 
        self.dlg.mMapLayerComboBox.clear()
        layer5 = self.dlg.mMapLayerComboBox.currentLayer()
        val15 = self.get_communes()
        if val15 != "" :
            layer_communes_region = QgsVectorLayer(val15, "communes", "ogr")
            #application d une extraction par localisation
            extraction = processing.run('qgis:extractbylocation',{'INPUT' : layer_communes_region, 'INTERSECT' :layer5, 'PREDICATE' :[0], 'OUTPUT' :'TEMPORARY_OUTPUT'})
            layer_extraction = extraction['OUTPUT']
            #layer_extraction.startEditing()
            type = layer_extraction.dataProvider().fieldNameIndex('TYPE')
            insee =layer_extraction.dataProvider().fieldNameIndex('INSEE_COM')
            dep = layer_extraction.dataProvider().fieldNameIndex('INSEE_DEP')
            compare_field_index = type
            concat_field_index = insee
            new_field_index = dep
            feature_dict = {f.id(): f for f in layer_extraction.getFeatures()}
            for f in feature_dict.values():
                if f[concat_field_index]:
                    new_field_text = f[concat_field_index]
                else:
                    new_field_text = f[concat_field_index]
                for compare_f in feature_dict.values():
                    if (f != compare_f
                            and f[compare_field_index] == compare_f[compare_field_index]):
                        if compare_f[concat_field_index]:
                            new_field_text += "|"+compare_f[concat_field_index]
                f[new_field_index] = new_field_text
            return new_field_text
        else :
            pass

 #application des nouvelles valeurs dans la nouvelle table attributaire
    def change_to_any(self):
        kiki = self.dlg.mMapLayerComboBox.currentLayer()
        source_chemin_couche = kiki.dataProvider().dataSourceUri() 
        chemin_tampon = os.path.dirname(source_chemin_couche)
        nom_couche= self.dlg.mMapLayerComboBox.currentText()
        path = chemin_tampon+"/"+nom_couche+"_TAMPON"
        shape= path+'.shp'
        gpkg= path+'.gpkg'
        distance_point = self.distance_tampon_point()
        distance_ligne = self.distance_tampon_ligne()
        if self.dlg.tampon.isChecked() :
            if kiki.geometryType()==QgsWkbTypes.PointGeometry:
                tampon = processing.run('qgis:buffer',{'INPUT': kiki,'DISTANCE': distance_point,'SEGMENTS': 5,'DISSOLVE': True,'END_CAP_STYLE': 0,'JOIN_STYLE': 0,'MITER_LIMIT': 2,'OUTPUT': path})
                #layer = tampon['OUTPUT']
                if self.dlg.checkBox.isChecked():
                    layer = iface.addVectorLayer(shape, "", "ogr")
                    layer.startEditing()
                    prov = layer.dataProvider()
                    field_names = [field.name() for field in prov.fields()]
                    for count, f in enumerate(field_names):
                        jean = range(count, count +1 )
                        paul = range(count)
                        jeanpaul = list(range(count, count +1 )) + list (range(count))
                    layer.dataProvider().deleteAttributes(jeanpaul)
                    #... et creation des nouveaux champs compatibles avec un import dans GeoMCE 
                    layer.dataProvider().addAttributes(
                                [QgsField("id", QVariant.Int,'Integer64',10,0),
                                QgsField("nom", QVariant.String,'String',100,0),
                                QgsField("categorie", QVariant.String,'String',7,0),
                                QgsField("cible", QVariant.String,'String',100,0),
                                QgsField("descriptio", QVariant.String,'String',254,0),
                                QgsField("decision", QVariant.String,'String',254,0),
                                QgsField("refei", QVariant.String,'String',254,0),
                                QgsField("duree", QVariant.String,'String',25,0),
                                QgsField("unite", QVariant.String,'String',25,0),
                                QgsField("modalite", QVariant.String,'String',50,0),
                                QgsField("cout",QVariant.Int,'Integer64', 10,0),
                                QgsField("montant_pr",QVariant.Int,'Integer64', 10,0),
                                QgsField("faunes",QVariant.String, 'String', 254,0),
                                QgsField("flores",QVariant.String, 'String', 254,0),
                                QgsField("echeances",QVariant.String, 'String', 254,0),
                                QgsField("communes", QVariant.String,'String',220,0)])         
                    layer.updateFields()
                else :
                    dede = QgsVectorLayer(gpkg, "", "ogr")         
                    zaza = QgsVectorFileWriter.writeAsVectorFormat(dede,path,'UTF-8',dede.crs(), "ESRI Shapefile")
                    layer = iface.addVectorLayer(shape, "", "ogr")
                    layer.startEditing()
                    prov = layer.dataProvider()
                    field_names = [field.name() for field in prov.fields()]
                    for count, f in enumerate(field_names):
                        jean = range(count, count +1 )
                        paul = range(count)
                        jeanpaul = list(range(count, count +1 )) + list (range(count))
                    layer.dataProvider().deleteAttributes(jeanpaul)
                    #... et creation des nouveaux champs compatibles avec un import dans GeoMCE 
                    layer.dataProvider().addAttributes(
                                [QgsField("id", QVariant.Int,'Integer64',10,0),
                                QgsField("nom", QVariant.String,'String',100,0),
                                QgsField("categorie", QVariant.String,'String',7,0),
                                QgsField("cible", QVariant.String,'String',100,0),
                                QgsField("descriptio", QVariant.String,'String',254,0),
                                QgsField("decision", QVariant.String,'String',254,0),
                                QgsField("refei", QVariant.String,'String',254,0),
                                QgsField("duree", QVariant.String,'String',25,0),
                                QgsField("unite", QVariant.String,'String',25,0),
                                QgsField("modalite", QVariant.String,'String',50,0),
                                QgsField("cout",QVariant.Int,'Integer64', 10,0),
                                QgsField("montant_pr",QVariant.Int,'Integer64', 10,0),
                                QgsField("faunes",QVariant.String, 'String', 254,0),
                                QgsField("flores",QVariant.String, 'String', 254,0),
                                QgsField("echeances",QVariant.String, 'String', 254,0),
                                QgsField("communes", QVariant.String,'String',220,0)])         
                    layer.updateFields()
            elif kiki.geometryType()== QgsWkbTypes.LineGeometry:
                tampon = processing.run('qgis:buffer',{'INPUT': kiki,'DISTANCE': distance_ligne,'SEGMENTS': 5,'DISSOLVE': True,'END_CAP_STYLE': 0,'JOIN_STYLE': 0,'MITER_LIMIT': 2,'OUTPUT': path})
                #layer = tampon['OUTPUT']
                if self.dlg.checkBox.isChecked():
                    layer = iface.addVectorLayer(shape, "", "ogr")
                    layer.startEditing()
                    prov = layer.dataProvider()
                    field_names = [field.name() for field in prov.fields()]
                    for count, f in enumerate(field_names):
                        jean = range(count, count +1 )
                        paul = range(count)
                        jeanpaul = list(range(count, count +1 )) + list (range(count))
                    layer.dataProvider().deleteAttributes(jeanpaul)
                    #... et creation des nouveaux champs compatibles avec un import dans GeoMCE 
                    layer.dataProvider().addAttributes(
                                [QgsField("id", QVariant.Int,'Integer64',10,0),
                                QgsField("nom", QVariant.String,'String',100,0),
                                QgsField("categorie", QVariant.String,'String',7,0),
                                QgsField("cible", QVariant.String,'String',100,0),
                                QgsField("descriptio", QVariant.String,'String',254,0),
                                QgsField("decision", QVariant.String,'String',254,0),
                                QgsField("refei", QVariant.String,'String',254,0),
                                QgsField("duree", QVariant.String,'String',25,0),
                                QgsField("unite", QVariant.String,'String',25,0),
                                QgsField("modalite", QVariant.String,'String',50,0),
                                QgsField("cout",QVariant.Int,'Integer64', 10,0),
                                QgsField("montant_pr",QVariant.Int,'Integer64', 10,0),
                                QgsField("faunes",QVariant.String, 'String', 254,0),
                                QgsField("flores",QVariant.String, 'String', 254,0),
                                QgsField("echeances",QVariant.String, 'String', 254,0),
                                QgsField("communes", QVariant.String,'String',220,0)])         
                    layer.updateFields()
                else :
                    dede = QgsVectorLayer(gpkg, "", "ogr")         
                    zaza = QgsVectorFileWriter.writeAsVectorFormat(dede,path,'UTF-8',dede.crs(), "ESRI Shapefile")
                    layer = iface.addVectorLayer(shape, "", "ogr")
                    layer.startEditing()
                    prov = layer.dataProvider()
                    field_names = [field.name() for field in prov.fields()]
                    for count, f in enumerate(field_names):
                        jean = range(count, count +1 )
                        paul = range(count)
                        jeanpaul = list(range(count, count +1 )) + list (range(count))
                    layer.dataProvider().deleteAttributes(jeanpaul)
                    #... et creation des nouveaux champs compatibles avec un import dans GeoMCE 
                    layer.dataProvider().addAttributes(
                                [QgsField("id", QVariant.Int,'Integer64',10,0),
                                QgsField("nom", QVariant.String,'String',100,0),
                                QgsField("categorie", QVariant.String,'String',7,0),
                                QgsField("cible", QVariant.String,'String',100,0),
                                QgsField("descriptio", QVariant.String,'String',254,0),
                                QgsField("decision", QVariant.String,'String',254,0),
                                QgsField("refei", QVariant.String,'String',254,0),
                                QgsField("duree", QVariant.String,'String',25,0),
                                QgsField("unite", QVariant.String,'String',25,0),
                                QgsField("modalite", QVariant.String,'String',50,0),
                                QgsField("cout",QVariant.Int,'Integer64', 10,0),
                                QgsField("montant_pr",QVariant.Int,'Integer64', 10,0),
                                QgsField("faunes",QVariant.String, 'String', 254,0),
                                QgsField("flores",QVariant.String, 'String', 254,0),
                                QgsField("echeances",QVariant.String, 'String', 254,0),
                                QgsField("communes", QVariant.String,'String',220,0)])         
                    layer.updateFields()
            else:
                layer = self.dlg.mMapLayerComboBox.currentLayer()
        else :
            layer = self.dlg.mMapLayerComboBox.currentLayer()
        val1 = self.get_new_nom()
        val2 = self.get_description()
        val3 = self.get_decision()
        val4 = self.get_refei()
        val5 = self.get_duree()
        val6 = self.get_categorie()
        val7 = self.get_cible()
        val8 = self.get_unite()
        val9 = self.get_modalite()
        val10 = self.get_cout()
        val11 = self.get_montant()
        val12 = self.get_faunes()
        val13 = self.get_flores()
        val14 = self.get_echeances()
        val15 = self.codeinsee()
        if self.dlg.tampon.isChecked():
            for feat in layer.getFeatures():
                layer.changeAttributeValue(feat.id(),0,feat.id())
                if val1 == "":
                    layer.changeAttributeValue(feat.id(),1,"-")
                else :
                    layer.changeAttributeValue(feat.id(),1,val1)
                if val6 == "":
                    layer.changeAttributeValue(feat.id(),2,"E")
                else :
                    layer.changeAttributeValue(feat.id(),2, val6)
                if val7 == "":
                    layer.changeAttributeValue(feat.id(),3,"Habitats naturels")
                else :
                    layer.changeAttributeValue(feat.id(),3, val7)
                if val2 == "":
                    layer.changeAttributeValue(feat.id(),4,"-")
                else :
                    layer.changeAttributeValue(feat.id(),4,val2)
                if val3 == "":
                    layer.changeAttributeValue(feat.id(),5,"-")
                else :
                    layer.changeAttributeValue(feat.id(),5,val3)                
                if val4 == "":
                    layer.changeAttributeValue(feat.id(),6,"-")
                else :
                    layer.changeAttributeValue(feat.id(),6,val4)
                if val5 == "":
                    layer.changeAttributeValue(feat.id(),7,"-")
                else :
                    layer.changeAttributeValue(feat.id(),7,val5)
                if val8 == "":
                    layer.changeAttributeValue(feat.id(),8,"Annee")
                else :
                    layer.changeAttributeValue(feat.id(),8, val8)
                if val9 == "":
                    layer.changeAttributeValue(feat.id(),9,"Bilan/compte rendu de suivi")
                else :
                    layer.changeAttributeValue(feat.id(),9, val9)
                if val10 == "":
                    layer.changeAttributeValue(feat.id(),10,"")
                else :
                    layer.changeAttributeValue(feat.id(),10,val10)
                if val11 == "":
                    layer.changeAttributeValue(feat.id(),11,"")
                else :
                    layer.changeAttributeValue(feat.id(),11,val11)
                if val12 == "":
                    layer.changeAttributeValue(feat.id(),12,"")
                else :
                    layer.changeAttributeValue(feat.id(),12,val12)
                if val13 == "":
                    layer.changeAttributeValue(feat.id(),13,"")
                else :
                    layer.changeAttributeValue(feat.id(),13,val13)
                if val14 == "":
                    layer.changeAttributeValue(feat.id(),14,"-")
                else :
                    layer.changeAttributeValue(feat.id(),14,val14)
                if self.get_communes()=="":
                    layer.changeAttributeValue(feat.id(),15, "")
                else :
                    layer.changeAttributeValue(feat.id(),15, val15)
            for feat in kiki.getFeatures():
                kiki.changeAttributeValue(feat.id(),0,feat.id())
                if val1 == "":
                    kiki.changeAttributeValue(feat.id(),1,"-")
                else :
                    kiki.changeAttributeValue(feat.id(),1,val1)
                if val6 == "":
                    kiki.changeAttributeValue(feat.id(),2,"E")
                else :
                    kiki.changeAttributeValue(feat.id(),2, val6)
                if val7 == "":
                    kiki.changeAttributeValue(feat.id(),3,"Habitats naturels")
                else :
                    kiki.changeAttributeValue(feat.id(),3, val7)
                if val2 == "":
                    kiki.changeAttributeValue(feat.id(),4,"-")
                else :
                    kiki.changeAttributeValue(feat.id(),4,val2)
                if val3 == "":
                    kiki.changeAttributeValue(feat.id(),5,"-")
                else :
                    kiki.changeAttributeValue(feat.id(),5,val3)                
                if val4 == "":
                    kiki.changeAttributeValue(feat.id(),6,"-")
                else :
                    kiki.changeAttributeValue(feat.id(),6,val4)
                if val5 == "":
                    kiki.changeAttributeValue(feat.id(),7,"-")
                else :
                    kiki.changeAttributeValue(feat.id(),7,val5)
                if val8 == "":
                    kiki.changeAttributeValue(feat.id(),8,"Annee")
                else :
                    kiki.changeAttributeValue(feat.id(),8, val8)
                if val9 == "":
                    kiki.changeAttributeValue(feat.id(),9,"Bilan/compte rendu de suivi")
                else :
                    kiki.changeAttributeValue(feat.id(),9, val9)
                if val10 == "":
                    kiki.changeAttributeValue(feat.id(),10,"")
                else :
                    kiki.changeAttributeValue(feat.id(),10,val10)
                if val11 == "":
                    kiki.changeAttributeValue(feat.id(),11,"")
                else :
                    kiki.changeAttributeValue(feat.id(),11,val11)
                if val12 == "":
                    kiki.changeAttributeValue(feat.id(),12,"")
                else :
                    kiki.changeAttributeValue(feat.id(),12,val12)
                if val13 == "":
                    kiki.changeAttributeValue(feat.id(),13,"")
                else :
                    kiki.changeAttributeValue(feat.id(),13,val13)
                if val14 == "":
                    kiki.changeAttributeValue(feat.id(),14,"-")
                else :
                    kiki.changeAttributeValue(feat.id(),14,val14)
                if self.get_communes()=="":
                    kiki.changeAttributeValue(feat.id(),15, "")
                else :
                    kiki.changeAttributeValue(feat.id(),15, val15)
        else :
            for feat in layer.getFeatures():
                layer.changeAttributeValue(feat.id(),0,feat.id())
                if val1 == "":
                    layer.changeAttributeValue(feat.id(),1,"-")
                else :
                    layer.changeAttributeValue(feat.id(),1,val1)
                if val6 == "":
                    layer.changeAttributeValue(feat.id(),2,"E")
                else :
                    layer.changeAttributeValue(feat.id(),2, val6)
                if val7 == "":
                    layer.changeAttributeValue(feat.id(),3,"Habitats naturels")
                else :
                    layer.changeAttributeValue(feat.id(),3, val7)
                if val2 == "":
                    layer.changeAttributeValue(feat.id(),4,"-")
                else :
                    layer.changeAttributeValue(feat.id(),4,val2)
                if val3 == "":
                    layer.changeAttributeValue(feat.id(),5,"-")
                else :
                    layer.changeAttributeValue(feat.id(),5,val3)                
                if val4 == "":
                    layer.changeAttributeValue(feat.id(),6,"-")
                else :
                    layer.changeAttributeValue(feat.id(),6,val4)
                if val5 == "":
                    layer.changeAttributeValue(feat.id(),7,"-")
                else :
                    layer.changeAttributeValue(feat.id(),7,val5)
                if val8 == "":
                    layer.changeAttributeValue(feat.id(),8,"Annee")
                else :
                    layer.changeAttributeValue(feat.id(),8, val8)
                if val9 == "":
                    layer.changeAttributeValue(feat.id(),9,"Bilan/compte rendu de suivi")
                else :
                    layer.changeAttributeValue(feat.id(),9, val9)
                if val10 == "":
                    layer.changeAttributeValue(feat.id(),10,"")
                else :
                    layer.changeAttributeValue(feat.id(),10,val10)
                if val11 == "":
                    layer.changeAttributeValue(feat.id(),11,"")
                else :
                    layer.changeAttributeValue(feat.id(),11,val11)
                if val12 == "":
                    layer.changeAttributeValue(feat.id(),12,"")
                else :
                    layer.changeAttributeValue(feat.id(),12,val12)
                if val13 == "":
                    layer.changeAttributeValue(feat.id(),13,"")
                else :
                    layer.changeAttributeValue(feat.id(),13,val13)
                if val14 == "":
                    layer.changeAttributeValue(feat.id(),14,"-")
                else :
                    layer.changeAttributeValue(feat.id(),14,val14)
                if self.get_communes()=="":
                    layer.changeAttributeValue(feat.id(),15, "")
                else :
                    layer.changeAttributeValue(feat.id(),15, val15)
        layername = self.dlg.mMapLayerComboBox.currentText()
        self.iface.messageBar().pushMessage(u'GéoMCE',u'Les nouvelles valeurs ont été écrites dans la couche '+layername, level=Qgis.Info, duration=3)

 #sauvegarde des elements saisis dans la table attributaire
    def save_edits(self):
        if self.dlg.tampon.isChecked():
            layer = iface.activeLayer()  
            layer.commitChanges()
            self.saved = False
            layername = self.dlg.mMapLayerComboBox.currentText()
            for name, selectlayer in QgsProject.instance().mapLayers().items():
                if selectlayer.name() == layername:
                    if (selectlayer.isEditable()):
                        selectlayer.commitChanges()
                        self.saved = True
                        self.countchange = 0
        else :
            self.saved = False
            layername = self.dlg.mMapLayerComboBox.currentText()
            for name, selectlayer in QgsProject.instance().mapLayers().items():
                if selectlayer.name() == layername:
                    if (selectlayer.isEditable()):
                        selectlayer.commitChanges()
                        self.saved = True
                        self.countchange = 0
        self.iface.messageBar().pushMessage(u'GéoMCE',u'Les nouvelles valeurs ont été enregistrées dans la couche '+layername, level=Qgis.Success, duration=5)
        return self.saved

 #on deselectionne les entites modifies 
#   def clearselection(self):
#       clearlist = []
#       for name, selectlayer in QgsProject.instance().mapLayers().items():
#           if selectlayer.type() == QgsMapLayer.VectorLayer:
#                selectlayer.setSelectedFeatures(clearlist)

 #permet d afficher la table attributaire de la couche qui a ete traiter
    def show_table(self):
        if self.dlg.tampon.isChecked():
            self.iface.showAttributeTable(iface.activeLayer())
        else :
            table_layer=self.dlg.mMapLayerComboBox.currentText()
            for name, selectlayer in QgsProject.instance().mapLayers().items():
                if selectlayer.name() == table_layer:
                    show_layer_t = selectlayer
                    self.iface.showAttributeTable(show_layer_t) 

    def show_table_2(self):
        self.iface.showAttributeTable(iface.activeLayer())

# permet de zipper les fichiers de lacouche de traitement    
    def archive (self, path):    
        if self.dlg.tampon.isChecked():
            chemin_couche = self.iface.activeLayer()
            source_chemin_couche = chemin_couche.dataProvider().dataSourceUri() 
            chemin_zip = os.path.dirname(source_chemin_couche)  
            nom_couche = self.iface.activeLayer().name()
        else:
            chemin_couche = self.dlg.mMapLayerComboBox.currentLayer()
            source_chemin_couche = chemin_couche.dataProvider().dataSourceUri() 
            chemin_zip = os.path.dirname(source_chemin_couche)  
            nom_couche= self.dlg.mMapLayerComboBox.currentText()
        nom_zip = self.get_new_nom()
        nom_zip_complet = chemin_zip + "/" + nom_zip +'.zip'
        nom_ok = ''.join((c for c in unicodedata.normalize('NFD', nom_zip_complet) if unicodedata.category(c) != 'Mn'))
        archive = zipfile.ZipFile(nom_ok, mode='w')
        f_shp = chemin_zip + "/" + nom_couche + '.shp'
        f_shx = chemin_zip + "/" + nom_couche + '.shx'
        f_cpg = chemin_zip + "/" +  nom_couche + '.cpg'
        f_dbf = chemin_zip + "/" +  nom_couche + '.dbf'
        f_prj = chemin_zip + "/" +  nom_couche + '.prj'
        archive.write(f_shp,basename(f_shp))
        archive.write(f_shx,basename(f_shx))
        archive.write(f_cpg,basename(f_cpg))
        archive.write(f_dbf,basename(f_dbf))
        archive.write(f_prj,basename(f_prj))
        archive.close()
        self.iface.messageBar().pushMessage(u'GéoMCE',u'Les fichiers ' + f_shp + ', '+f_cpg+ ', '+f_dbf+ ', '+f_prj+ ' et '+ f_shx +' ont été ajoutés dans l\'archive ' + nom_ok + u' dans le dossier suivant : ' + chemin_zip, level=Qgis.Success, duration=3) 

    def archive_2 (self, path):    
        chemin_couche = self.dlg.mQgsFileWidget.lineEdit().text()
        chemin_zip = os.path.dirname(chemin_couche)  
        nom_couche= self.iface.activeLayer().name()
        nom_zip_complet = chemin_zip + "/" + nom_couche +'.zip'
        #nom_ok = ''.join((c for c in unicodedata.normalize('NFD', nom_zip_complet) if unicodedata.category(c) != 'Mn'))
        archive = zipfile.ZipFile(nom_zip_complet, mode='w')
        f_shp = chemin_couche + '.shp'
        f_shx = chemin_couche + '.shx'
        f_cpg = chemin_couche + '.cpg'
        f_dbf = chemin_couche + '.dbf'
        f_prj = chemin_couche + '.prj'
        archive.write(f_shp,basename(f_shp))
        archive.write(f_shx,basename(f_shx))
        archive.write(f_cpg,basename(f_cpg))
        archive.write(f_dbf,basename(f_dbf))
        archive.write(f_prj,basename(f_prj))
        archive.close()
        self.iface.messageBar().pushMessage(u'GéoMCE',u'Les fichiers ' + f_shp + ', '+f_cpg+ ', '+f_dbf+ ', '+f_prj+ ' et '+ f_shx +' ont été ajoutés dans l\'archive ' + nom_couche + u' dans le dossier suivant : ' + chemin_zip, level=Qgis.Success, duration=3)
       
#ouvre le dossier contenant les fichiers
    def dossier(self):
        if self.dlg.tampon.isChecked(): 
            layername = self.iface.activeLayer()
        else:    
            layername = self.dlg.mMapLayerComboBox.currentLayer()
        doudai = layername.dataProvider().dataSourceUri() 
        path = os.path.dirname(doudai)
        os.startfile(path)    
        
    def dossier_2(self):
        path = self.dlg.mQgsFileWidget.lineEdit().text()
        path_fusion = os.path.dirname(path)
        os.startfile(path_fusion)
        
 #on ferme le plugin
    def exit(self):
        #on nettoie et deconnecte
        self.dlg.nom.clear()
        self.dlg.reject()
        self.dlg.description.clear()
        self.dlg.decision.clear()
        self.dlg.refei.clear()
        self.dlg.duree.clear()
        self.dlg.comboBox.clear()
        self.dlg.comboBox_2.clear()
        self.dlg.comboBox_3.clear()
        self.dlg.comboBox_4.clear()
        self.dlg.cout.clear()
        self.dlg.montant.clear()
        self.dlg.faunes.clear()
        self.dlg.flores.clear()
        self.dlg.echeances.clear()

    def listWidget(self):
        self.dlg.mComboBox.clear()
        layers = [layer for layer in QgsProject.instance().mapLayers().values()]
        for layer in layers:
            layerType = layer.type()
            if layerType == QgsMapLayer.VectorLayer:
                self.dlg.mComboBox.addItem(layer.name())

    def fusion(self):
        layers = self.dlg.mComboBox.checkedItems()
        p = self.dlg.mQgsFileWidget.filePath()
        path = self.dlg.mQgsFileWidget.lineEdit().text()
        path_fusion = os.path.dirname(path)
        shape = path +'.shp'
        gpkg = path+'.gpkg'
        nom_fusion = [layers for layers in self.dlg.mComboBox.checkedItems()]
        merge = processing.run("qgis:mergevectorlayers", 
                             {'LAYERS':nom_fusion,
                             'CRS':None,
                             'OUTPUT':'TEMPORARY_OUTPUT'})
        vlayer = merge['OUTPUT']
        processing.run("qgis:refactorfields",{'INPUT':vlayer, 'FIELDS_MAPPING' : [{'expression': '"id"', 'length': 10, 'name': 'id', 'precision': 0, 'type': 2}, {'expression': '"nom"', 'length': 100, 'name': 'nom', 'precision': 0, 'type': 10}, {'expression': '"categorie"', 'length': 7, 'name': 'categorie', 'precision': 0, 'type': 10}, {'expression': '"cible"', 'length': 100, 'name': 'cible', 'precision': 0, 'type': 10}, {'expression': '"descriptio"', 'length': 254, 'name': 'descriptio', 'precision': 0, 'type': 10}, {'expression': '"decision"', 'length': 254, 'name': 'decision', 'precision': 0, 'type': 10}, {'expression': '"refei"', 'length': 254, 'name': 'refei', 'precision': 0, 'type': 10}, {'expression': '"duree"', 'length': 25, 'name': 'duree', 'precision': 0, 'type': 10}, {'expression': '"unite"', 'length': 25, 'name': 'unite', 'precision': 0, 'type': 10}, {'expression': '"modalite"', 'length': 50, 'name': 'modalite', 'precision': 0, 'type': 10}, {'expression': '"cout"', 'length': 10, 'name': 'cout', 'precision': 0, 'type': 10}, {'expression': '"montant_pr"', 'length': 10, 'name': 'montant_pr', 'precision': 0, 'type': 10}, {'expression': '"faunes"', 'length': 254, 'name': 'faunes', 'precision': 0, 'type': 10}, {'expression': '"flores"', 'length': 254, 'name': 'flores', 'precision': 0, 'type': 10}, {'expression': '"echeances"', 'length': 254, 'name': 'echeances', 'precision': 0, 'type': 10}, {'expression': '"communes"', 'length': 220, 'name': 'communes', 'precision': 0, 'type': 10}, {'expression': '"layer"', 'length': 100, 'name': 'layer', 'precision': 0, 'type': 10}, {'expression': '"path"', 'length': 200, 'name': 'path', 'precision': 0, 'type': 10}], 'OUTPUT' :p})
        if self.dlg.checkBox.isChecked():
            dede = iface.addVectorLayer(shape, "", "ogr")
            dede.startEditing()
            dede.dataProvider().deleteAttributes([16,17])
            dede.commitChanges()
        else :
            popo = QgsVectorLayer(gpkg, "Fusion", "ogr")         
            zaza = QgsVectorFileWriter.writeAsVectorFormat(popo,path,'UTF-8',vlayer.crs(), "ESRI Shapefile")
            zaza = iface.addVectorLayer(shape, "", "ogr")
            zaza.startEditing()
            zaza.dataProvider().deleteAttributes([0,17,18])
            zaza.commitChanges()

  #ouvre la boite de dialogue Aide/A propos
    def doabout(self):
        self.dlga.show()

    def unload(self):
        """Removes the plugin menu item and icon from QGIS G"""
        for action in self.actions:
            self.iface.removePluginVectorMenu(
                self.tr(u'&GeoMCE'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def run(self):
        #pas de vecteurs, pas de chocolat
        self.countchange = 0
        self.turnedoffLayers = []
        self.saved = None
        self.selectall = 0
        check = 0
        check = self.checkvector()
        if check == 0:
            self.iface.messageBar().pushMessage(u'GéoMCE',u'J\'peux pas bosser sans couches vecteurs!', level=Qgis.Critical, duration=3)
            return
        else:
            self.dlg.show()
            self.chooselayer()
            self.set_select_attributes()
            self.dlg.mFieldComboBox.clear()
            self.dlg.mMapLayerComboBox.clear()
            self.dlg.mMapLayerComboBox_2.clear()
            self.dlg.mMapLayerComboBox_2.layerChanged.connect(self.select_layer_fields2)
            self.dlg.comboBox.clear()
            categorie = [u'E - Évitement',u'|- E1 - Évitement « amont » (stade anticipé)',u'|-- E1-1. - Phase de conception du dossier de demande',u'|--- E1-1-a. - Évitement des populations connues d\'espèces protégées ou à fort enjeux',u'|--- E1-1-b. - Évitement des sites à enjeux du territoire',u'|--- E1-1-c. - Redéfinition des caractéristiques du projet',u'|--- E1-1-d. - Autre : à préciser',u'|- E2 - Évitement géographique',u'|-- E2-1. - Phase travaux',u'|--- E2-1-a. - Balisage préventif divers ou mise en défens ou dispositif de protection d\'une station d\'une espèce patrimoniale, d\'un habitat d\'une espèce patrimoniale, d\'habitats d\'espèces, d\'arbres remarquable',u'|--- E2-1-b. - Limitation des emprises des travaux',u'|--- E2-1-c. - Autre : à préciser',u'|-- E2-2. - Phase exploitation / fonctionnement',u'|--- E2-2-a. - Éloignement de l\'ouvrage vis-à-vis des populations (humaines) sensibles',u'|--- E2-2-b. - Mesure des documents de planification délimitant des zones et affectant les sols de manière à éloigner les populations sensibles, application de marges de recul (urbanisations futures)',u'|--- E2-2-c. - Mesure d\'orientation d\'une installation ou d\'optimisation de la géométrie du projet',u'|--- E2-2-d. - Mesure d\'acquisition hors emprise du projet',u'|--- E2-2-e. - Limitation des emprises du projet',u'|--- E2-2-f. - Positionnement du projet sur un secteur de moindre enjeu',u'|--- E2-2-g. - Autre : à préciser',u'|- E3 - Évitement technique',u'|-- E3-1. - Phase travaux',u'|--- E3-1-a. - Absence de rejet dans le milieu naturel (air, eau, sol)',u'|--- E3-1-b. - Autre : à préciser',u'|-- E3-2. - Phase exploitation / fonctionnement',u'|--- E3-2-a. - Absence totale d\'utilisation de produits phytosanitaires',u'|--- E3-2-b. - Modifications / adaptations des choix d\'aménagement, des caractéristiques du projet (à préciser)',u'|--- E3-2-c. - Autre : à préciser',u'|- E4 - Évitement temporel',u'|-- E4-1. - Phase travaux',u'|--- E4-1-a. - Adaptation de la période des travaux sur l\'année',u'|--- E4-1-b. - Adaptation des horaires des travaux (en journalier)',u'|--- E4-1-c. - Autre : à préciser',u'|-- E4-2. - Phase exploitation / fonctionnement',u'|--- E4-2-a. - Adaptation des périodes d\'exploitation sur l\'année',u'|--- E4-2-b. - Adaptation des horaires d\'exploitation (fonctionnement diurne, nocturne)',u'|--- E4-2-c. - Autre : à préciser',u'------------------------------------------',u'R - Réduction',u'|- R1 - Réduction géographique',u'|-- R1-1. - Phase travaux',u'|--- R1-1-a. - Limitation / adaptation des emprises des travaux et/ou des zones d\'accès et/ou des zones de circulation des engins de chantier',u'|--- R1-1-b. - Limitation / adaptation des installations de chantier',u'|--- R1-1-c. - Balisage préventif divers ou mise en défens (pour partie) ou dispositif de protection d\'une station d\'une espèce patrimoniale, d\'un habitat d\'une espèce patrimoniale, d\'habitats d\'espèces, arbres remarquables',u'|--- R1-1-d. - Autre : à préciser',u'|-- R1-2. - Phase exploitation / fonctionnement',u'|--- R1-2-a. - Limitation / adaptation des emprises du projet',u'|--- R1-2-b. - Balisage définitif divers ou mise en défens définitive (pour partie) ou dispositif de protection définitif d\'une station d\'une espèce patrimoniale, d\'un habitat d\'une espèce patrimoniale, d\'habitats d\'espèces, arbres remarquables',u'|--- R1-2-c. - Autre : à préciser',u'|- R2 - Réduction technique',u'|-- R2-1. - Phase travaux',u'|--- R2-1-a. - Adaptation des modalités de circulation des engins de chantier',u'|--- R2-1-b. - Mise en place d\'écran naturel ou artificiel temporaire',u'|--- R2-1-c. - Mode particulier d\'évacuation des matériaux, déblais et résidus de chantier : transport fluvial, transport ferroviaire, etc.',u'|--- R2-1-d. - Procédé technique limitant les impacts du chantier à la source',u'|--- R2-1-e. - Optimisation de la gestion des matériaux et déblais',u'|--- R2-1-f. - Dispositif préventif de lutte contre une pollution et dispositif d\'assainissement provisoire de gestion des eaux pluviales et de chantier',u'|--- R2-1-g. - Actions correctives faisant suite à une mise en évidence d\'une dégradation sur le milieu',u'|--- R2-1-h. - Dispositif préventif de lutte contre l\'érosion des sols',u'|--- R2-1-i. - Dispositif préventif de lutte contre les espèces exotiques envahissantes',u'|--- R2-1-j. - Dispositif limitant les impacts liés au passage des engins de chantier',u'|--- R2-1-k. - Clôture et dispositif de franchissement provisoires adaptés aux espèces animales cibles',u'|--- R2-1-l. - Dispositif permettant d\'éloigner les espèces à enjeux et limitant leur installation. Mise en ouvre avant les travaux ou pendant la phase travaux',u'|--- R2-1-m. - Dispositif de limitation des nuisances autre que écran',u'|--- R2-1-n. - Maintien d\'un débit minimum de cours d\'eau',u'|--- R2-1-o. - Maintien d\'une connexion latérale (espèces aquatiques)',u'|--- R2-1-p. - Récupération et transfert d\'une partie du milieu naturel',u'|--- R2-1-q. - Prélèvement ou sauvetage avant destruction de spécimens d\'espèces - Espèce(s) à préciser',u'|--- R2-1-r. - Gestion écologique temporaire des habitats dans la zone d\'emprise des travaux',u'|--- R2-1-s. - Dispositif d\'aide à la recolonisation du milieu',u'|--- R2-1-t. - Dispositif de repli du chantier',u'|--- R2-1-t. - Autre : à préciser',u'|-- R2-2. - Phase exploitation / fonctionnement',u'|--- R2-2-a. - Action sur les conditions de circulation (ferroviaire, routier, aérien)',u'|--- R2-2-b. - Procédés techniques limitant les émissions polluantes et sonores à la source',u'|--- R2-2-c. - Procédés techniques limitant la dispersion des polluants et la propagation des ondes acoustiques (écrans, etc.)',u'|--- R2-2-d. - Dispositif anti-collision et d\'effarouchement (hors clôture spécifique)',u'|--- R2-2-e. - Adaptation d\'un ouvrage de franchissement hydraulique pour le passage de la faune',u'|--- R2-2-f. - Passage à faune (supérieur et inférieur)',u'|--- R2-2-g. - Choix d\'aménagements permettant de limiter l\'exposition aux nuisances (TC, modes actifs, élévation d\'un bâtiment)',u'|--- R2-2-h. - Dispositif complémentaire au droit d\'un passage faune afin de favoriser sa fonctionnalité',u'|--- R2-2-i. - Dispositif de limitation des nuisances',u'|--- R2-2-j. - Maintien d\'un débit minimum biologique de cours d\'eau pour le maintien des populations en bon état écologique ou d\'une connexion latérale',u'|--- R2-2-k. - Clôture spécifique (y compris échappatoire) et dispositif anti-pénétration dans les emprises',u'|--- R2-2-l. - Plantation sur talus type up-over',u'|--- R2-2-m. - Installation d\'abris ou de gîtes artificiels pour la faune au droit du projet ou à proximité',u'|--- R2-2-n. - Dispositif technique limitant les impacts sur la continuité hydraulique',u'|--- R2-2-o. - Optimisation de la gestion des matériaux et déblais',u'|--- R2-2-p. - Autre : à préciser',u'|- R3 - Réduction temporelle',u'|-- R3-1. - Phase travaux',u'|--- R3-1-a. - Adaptation de la période des travaux sur l\'année',u'|--- R3-1-b. - Adaptation des horaires des travaux (en journalier)',u'|--- R3-1-c. - Autre : à préciser',u'|-- R3-2. - Phase exploitation / fonctionnement',u'|--- R3-2-a. - Adaptation des périodes d\'exploitation / d\'activité (sur l\'année)',u'|--- R3-2-b. - Adaptation des horaires d\'exploitation / d\'activité (fonctionnement diurne, nocturne)',u'|--- R3-2-c. - Autre : à préciser',u'------------------------------------------',u'C - Compensation',u'|- C1 - Création / Renaturation de milieu',u'|-- C1-1. - Action concernant tous types de milieux',u'|--- C1-1-a. - Création ou renaturation d\'habitats et d\'habitats favorables aux espèces cibles et à leur guilde (à préciser)',u'|--- C1-1-b. - Aménagement ponctuel (abris ou gîtes artificiels pour la faune) complémentaire à une mesure C1.a Se distingue de la mesure R2-2 « installation d\'abris ou de gîtes artificiels pour la faune » car n\'est pas localisé sur le site impacté mais sur le site de compensation',u'|--- C1-1-c. - Autre : à préciser',u'|- C2 - Restauration / Réhabilitation',u'|-- C2-1. - Action concernant tous types de milieux (sauf cours d\'eau)',u'|--- C2-1-a. - Enlèvement de dispositifs d\'aménagements antérieurs (déconstruction) hors ouvrages en eau (voir C2.2.i)',u'|--- C2-1-b. - Enlèvement / traitement d\'espèces exotiques envahissantes',u'|--- C2-1-c. - Etrépage / Décapage / Décaissement du sol ou suppression de remblais,',u'|--- C2-1-d. - Réensemencement de milieux dégradés, replantation, restauration de haies existantes mais dégradées',u'|--- C2-1-e. - Réouverture du milieu par débroussaillage d\'espèces ligneuses, abattage d\'arbres, etc.',u'|--- C2-1-f. - Restauration de corridor écologique',u'|--- C2-1-g. - Aménagement ponctuel (abris ou gîtes artificiels pour la faune) complémentaire à une autre mesure C2 Se distingue de la mesure R2-2t « installation d\'abris ou de gîtes artificiels pour la faune » car n\'est pas localisé sur le site impacté mais sur le site de compensation',u'|--- C2-1-h. - Autre : à préciser',u'|-- C2-2. - Actions spécifiques aux cours d\'eau (lit mineur + lit majeur), annexes hydrauliques, étendues d\'eau stagnantes et zones humides',u'|--- C2-2-a. - Reprofilage / Restauration de berges (yc suppression des protections artificielles)',u'|--- C2-2-b. - Amélioration / entretien d\'annexes hydrauliques / décolmatage de fond et action sur la source du colmatage',u'|--- C2-2-c. - Reconnexion d\'annexes hydrauliques avec le cours d\'eau / reconnexion lit mineur/lit majeur',u'|--- C2-2-d. - Restauration des conditions hydromorphologique du lit mineur (hors emprise)',u'|--- C2-2-e. - Restauration des modalités d\'alimentation et de circulation de l\'eau au sein d\'une ZH',u'|--- C2-2-f. - Restauration des zones de frayes',u'|--- C2-2-g. - Restauration de ripisylves existantes mais dégradées',u'|--- C2-2-h. - Modification ou équipement d\'ouvrage existant (hors emprise du projet)',u'|--- C2-2-i. - Arasement ou dérasement d\'un obstacle transversal, d\'un seuil, d\'un busage (cours d\'eau)',u'|--- C2-2-j. - Aménagement d\'un point d\'abreuvement et mise en défens des berges',u'|--- C2-2-k. - Autre : à préciser',u'|- C3 - Evolution des pratiques de gestion',u'|-- C3-1. - Abandon ou changement total des modalités de gestion antérieures',u'|--- C3-1-a. - Abandon ou forte réduction de tout traitement phytosanitaire – messicoles',u'|--- C3-1-b. - Abandon de toute gestion :  îlot de senescence, autre (à préciser)',u'|--- C3-1-c. - Changement des pratiques culturales par conversion de terres cultivées ou exploitées de manière intensive',u'|--- C3-1-d. - Autre : à préciser',u'|-- C3-2. - Simple évolution des modalités de gestion antérieures',u'|--- C3-2-a. - Modification de la gestion des niveaux d\'eau',u'|--- C3-2-b. - Modification des modalités de fauche et/ou de pâturage',u'|--- C3-2-c. - Mise en place de pratiques de gestion alternatives plus respectueuses',u'|--- C3-2-d. - Modification des modalités de fréquentation humaine',u'|--- C3-2-e. - Autre : à préciser',u'------------------------------------------',u'A - Accompagnement',u'|- A1 - Préservation foncière',u'|-- A1-1. - Site en bon état écologique et fortement menacé répondant au cas dérogatoire des LD ERC',u'|--- A1-1-a. - Acquisition de parcelle sans mise en ouvre d\'action écologique complémentaire',u'|-- A1-2. - Site en bon état de conservation',u'|--- A1-2-a. - Acquisition de parcelle sans mise en ouvre d\'action écologique complémentaire. Le milieu acquis peut ne pas respecter la condition d\'équivalence écologique',u'|- A2 - Pérennité des mesures compensatoires C1 à C3 et A2',u'|-- A2-1. - Pérennité des mesures compensatoires C1 à C3 et A2',u'|--- A2-1-a. - Mise en place d\'un outil réglementaire du Code de l\'Environnement ou du Code Rural et de la pêche ou du Code de l\'Urbanisme',u'|--- A2-1-b. - Rattachement du foncier à un réseau de sites locaux',u'|--- A2-1-c. - Cession / rétrocession du foncier',u'|--- A2-1-d. - Mise en place d\'obligations réelles environnementales',u'|- A3 - Réaménagement / rétablissement',u'|-- A3-1. - Réaménagement / rétablissement',u'|--- A3-1-a. - Aménagement ponctuel (abris ou gîtes artificiels pour la faune)',u'|--- A3-1-b. - Aide à la recolonisation végétale',u'|--- A3-1-c. - Autre : à préciser',u'|- A4 - Financement',u'|-- A4-1. - Financement intégral du maître d\'ouvrage',u'|--- A4-1-a. - Aide financière au fonctionnement de structures locales',u'|--- A4-1-b. - Approfondissement des connaissances relatives à une espèce ou un habitat impacté, à la qualité de l\'air et aux niveaux de bruit',u'|--- A4-1-c. - Financement de programmes de recherche',u'|--- A4-1-d. - Autre : à préciser',u'|-- A4-2. - Contribution à une politique publique',u'|--- A4-2-a. - Contribution financière au déploiement d\'actions prévues par un document couvrant le territoire impacté',u'|--- A4-2-b. - Contribution au financement de la réalisation de document d\'action en faveur d\'une espèce ou d\'un habitat impacté par le projet',u'|--- A4-2-c. - Financement de programmes de recherche',u'|--- A4-2-d. - Autre : à préciser',u'|- A5 - Actions expérimentales',u'|-- A5-1. - Actions expérimentales',u'|--- A5-1-a. - Action expérimentale de génie-écologique',u'|--- A5-1-b. - Action expérimentale de renforcement de population ou de transplantation d\'individus / translocation manuelle ou mécanique',u'|--- A5-1-c. - Autre : à préciser',u'|- A6 - Action de gouvernance/ sensibilisation / communication /',u'|-- A6-1. - Gouvernance',u'|--- A6-1-a. - Organisation administrative du chantier',u'|--- A6-1-b. - Mise en place d\'un comité de suivi des mesures',u'|--- A6-1-c. - Autre : à préciser',u'|-- A6-2. - Communication, sensibilisation ou de diffusion des connaissances',u'|--- A6-2-a. - Action de gestion de la connaissance collective',u'|--- A6-2-b. - Déploiement d\'actions de communication',u'|--- A6-2-c. - Déploiement d\'actions de sensibilisation',u'|--- A6-2-d. - Dispositif de canalisation du public ou de limitation des accès',u'|--- A6-2-e. - Autre : à préciser',u'|- A7 - Autre',u'|-- A7-1. - autre',u'|--- A7-1-a. - Mesure d\'accompagnement ne rentrant dans aucune des catégories ci-avant A1 à A6 ']
            self.dlg.comboBox.addItems(categorie)
            self.dlg.comboBox_2.clear()
            cible = [u'Sol',u'Sites et paysages',u'Population',u'Patrimoine culturel et archeologique',u'Habitats naturels',u'Faune et flore',u'Facteurs climatiques',u'Espaces naturels, agricoles, forestiers, maritimes ou de loisirs','Equilibres biologiques',u'Biens materiels',u'Eau',u'Bruit',u'Continuites ecologiques']
            self.dlg.comboBox_2.addItems(cible)
            self.dlg.comboBox_3.clear()
            unite = [u'Annee', u'Mois',u'Jour']
            self.dlg.comboBox_3.addItems(unite)
            self.dlg.comboBox_4.clear()
            modalite = [u'Audit de chantier',u'Bilan/compte rendu de suivi',u'Rapport de fin de chantier',u'Autre']
            self.dlg.comboBox_4.addItems(modalite)
            flores = [u'---Angiospermes---',u'Acanthoprasium frutescens',u'Acer monspessulanum',u'Achillea erba-rotta subsp. erba-rotta',u'Achillea maritima',u'Achillea maritima subsp. atlantica',u'Achillea maritima subsp. maritima',u'Achillea ptarmica',u'Achillea ptarmica subsp. ptarmica',u'Achillea ptarmica subsp. pyrenaica',u'Achillea ptarmica var. ptarmica',u'Achillea ptarmica var. pubescens',u'Achillea ptarmica var. vulgaris',u'Achillea tomentosa',u'Aciotis purpurascens',u'Acis fabrei',u'Acis longifolia',u'Acis nicaeensis',u'Aconitum anthora',u'Aconitum carmichaelii',u'Aconitum lycoctonum',u'Aconitum lycoctonum subsp. neapolitanum',u'Aconitum lycoctonum subsp. vulparia',u'Aconitum napellus',u'Aconitum napellus subsp. burnatii',u'Aconitum napellus subsp. corsicum',u'Aconitum napellus subsp. lusitanicum',u'Aconitum napellus subsp. napellus',u'Aconitum napellus subsp. vulgare',u'Aconitum napellus var. napellus',u'Aconitum variegatum',u'Aconitum variegatum subsp. oenipontanum',u'Aconitum variegatum subsp. paniculatum',u'Aconitum variegatum subsp. pyrenaicum',u'Aconitum x molle',u'Aconitum x zahlbruckneri',u'Acrocomia aculeata',u'Actaea spicata',u'Adenocarpus complicatus',u'Adenocarpus complicatus subsp. complicatus',u'Adenocarpus complicatus subsp. complicatus x Adenocarpus complicatus subsp. parvifolius',u'Adenocarpus complicatus subsp. parvifolius',u'Adenostyles alliariae',u'Adonis aestivalis',u'Adonis aestivalis subsp. aestivalis',u'Adonis aestivalis subsp. squarrosa',u'Adonis flammea',u'Adonis pyrenaica',u'Adonis vernalis',u'Aechmea serrata',u'Aethionema monospermum',u'Aethionema thomasianum',u'Agrimonia procera',u'Agropyron cristatum subsp. pectinatum',u'Agrostemma githago',u'Agrostis castellana',u'Agrostis castellana var. castellana',u'Agrostis castellana var. mutica',u'Agrostis curtisii',u'Agrostis schraderiana',u'Aira elegantissima',u'Aira provincialis',u'Airopsis tenella',u'Ajuga chamaepitys',u'Ajuga chamaepitys subsp. chamaepitys',u'Ajuga pyramidalis var. meonantha',u'Alcea biennis',u'Alchemilla amphisericea',u'Alchemilla flabellata',u'Alchemilla glaucescens',u'Alchemilla hoppeana',u'Alchemilla xanthochlora',u'Aldrovanda vesiculosa',u'Alisma gramineum',u'Alisma lanceolatum',u'Alkanna lutea',u'Allium angulosum',u'Allium carinatum',u'Allium chamaemoly',u'Allium coloratum',u'Allium commutatum',u'Allium ericetorum',u'Allium flavum',u'Allium lusitanicum',u'Allium moly',u'Allium nigrum',u'Allium roseum',u'Allium roseum subsp. roseum',u'Allium savii',u'Allium schoenoprasum',u'Allium schoenoprasum subsp. schoenoprasum',u'Allium scorodoprasum',u'Allium siculum',u'Allium strictum',u'Allium suaveolens',u'Allium subhirsutum',u'Allium subhirsutum subsp. subhirsutum',u'Allium trifoliatum',u'Alnus alnobetula',u'Alnus alnobetula subsp. alnobetula',u'Alnus alnobetula subsp. suaveolens',u'Alopecurus aequalis',u'Alopecurus bulbosus',u'Alopecurus bulbosus subsp. bulbosus',u'Alopecurus rendlei',u'Althaea officinalis',u'Althenia filiformis',u'Althenia filiformis subsp. filiformis',u'Althenia filiformis subsp. orientalis',u'Alyssum alyssoides',u'Alyssum cacuminum',u'Alyssum corsicum',u'Alyssum flexicaule',u'Alyssum loiseleurii',u'Alyssum montanum',u'Alyssum montanum subsp. collicola',u'Alyssum montanum subsp. montanum',u'Alyssum montanum var. montanum',u'Alyssum montanum var. thiebautii',u'Amaranthus hybridus subsp. bouchonii',u'Ambrosina bassii',u'Amelanchier ovalis',u'Amelanchier ovalis subsp. embergeri',u'Amelanchier ovalis subsp. ovalis',u'Ammannia coccinea',u'Ampelodesmos mauritanicus',u'Anacamptis collina',u'Anacamptis coriophora',u'Anacamptis coriophora subsp. coriophora',u'Anacamptis coriophora subsp. martrinii',u'Anacamptis fragrans',u'Anacamptis laxiflora',u'Anacamptis morio',u'Anacamptis morio subsp. champagneuxii',u'Anacamptis morio subsp. longicornu',u'Anacamptis morio subsp. morio',u'Anacamptis morio subsp. picta',u'Anacamptis palustris',u'Anacamptis palustris subsp. palustris',u'Anacamptis palustris subsp. robusta',u'Anacamptis papilionacea',u'Anacamptis pyramidalis',u'Anacamptis pyramidalis var. pyramidalis',u'Anacamptis pyramidalis var. tanayensis',u'Anagyris foetida',u'Anarrhinum bellidifolium',u'Anchusa crispa',u'Anchusa crispa subsp. crispa',u'Anchusa crispa subsp. valincoana',u'Andromeda polifolia',u'Andropogon distachyos',u'Androsace alpina',u'Androsace chaixii',u'Androsace ciliata',u'Androsace cylindrica',u'Androsace cylindrica subsp. cylindrica',u'Androsace cylindrica subsp. hirtella',u'Androsace elongata',u'Androsace elongata subsp. breistrofferi',u'Androsace elongata subsp. elongata',u'Androsace halleri',u'Androsace helvetica',u'Androsace lactea',u'Androsace pubescens',u'Androsace pyrenaica',u'Androsace septentrionalis',u'Androsace vandellii',u'Anemone alpina',u'Anemone alpina subsp. alpina',u'Anemone alpina subsp. apiifolia',u'Anemone alpina subsp. cantabrica',u'Anemone alpina subsp. cottianaea',u'Anemone alpina subsp. millefoliata',u'Anemone coronaria',u'Anemone halleri',u'Anemone halleri subsp. halleri',u'Anemone hepatica',u'Anemone narcissiflora',u'Anemone narcissiflora subsp. narcissiflora',u'Anemone palmata',u'Anemone pulsatilla',u'Anemone pulsatilla subsp. bogenhardtiana',u'Anemone pulsatilla subsp. pulsatilla',u'Anemone ranunculoides',u'Anemone ranunculoides subsp. ranunculoides',u'Anemone rubra',u'Anemone rubra var. rubra',u'Anemone rubra var. serotina',u'Anemone sylvestris',u'Anemone trifolia',u'Anemone trifolia subsp. trifolia',u'Anemone vernalis',u'Angelica archangelica',u'Angelica heterocarpa',u'Aniba ramageana',u'Anisantha fasciculata',u'Anisantha fasciculata subsp. fasciculata',u'Anisantha tectorum',u'Antennaria dioica',u'Anthemis secundiramea',u'Anthericum liliago',u'Anthericum liliago var. liliago',u'Anthericum liliago var. multiflorum',u'Anthericum liliago var. sphaerocarpum',u'Anthericum ramosum',u'Anthriscus sylvestris subsp. alpina',u'Anthriscus sylvestris var. alpina',u'Anthriscus sylvestris var. angustisecta',u'Anthriscus sylvestris var. torquata',u'Anthyllis barba-jovis',u'Anthyllis circinnata',u'Anthyllis cytisoides',u'Anthyllis montana',u'Anthyllis montana subsp. montana',u'Anthyllis montana var. montana',u'Anthyllis montana var. sericea',u'Antinoria agrostidea',u'Antinoria agrostidea subsp. agrostidea',u'Antinoria insularis',u'Antirrhinum majus subsp. tortuosum',u'Aphyllanthes monspeliensis',u'Apium graveolens',u'Apium graveolens var. graveolens',u'Aquilegia alpina',u'Aquilegia reuteri',u'Aquilegia viscosa',u'Aquilegia vulgaris',u'Aquilegia vulgaris subsp. subalpina',u'Aquilegia vulgaris subsp. vulgaris',u'Arabidopsis arenosa',u'Arabidopsis arenosa subsp. arenosa',u'Arabidopsis arenosa subsp. borbasii',u'Arabidopsis cebennensis',u'Arabis alpina',u'Arabis auriculata',u'Arabis scabra',u'Arabis soyeri subsp. soyeri',u'Arbutus unedo',u'Arctium nemorosum',u'Arctostaphylos uva-ursi',u'Arctostaphylos uva-ursi var. crassifolius',u'Arenaria cinerea',u'Arenaria controversa',u'Arenaria grandiflora',u'Arenaria grandiflora subsp. grandiflora',u'Arenaria hispida',u'Arenaria ligericina',u'Arenaria modesta',u'Arenaria modesta subsp. modesta',u'Arenaria provincialis',u'Arenaria purpurascens',u'Arenaria serpyllifolia',u'Arenaria serpyllifolia var. macrocarpa',u'Arenaria serpyllifolia var. serpyllifolia',u'Arenaria serpyllifolia var. viscida',u'Argyrolobium zanonii',u'Aristavena setacea',u'Aristolochia clematitis',u'Aristolochia clusii',u'Armeria arenaria',u'Armeria arenaria subsp. arenaria',u'Armeria arenaria subsp. bupleuroides',u'Armeria arenaria subsp. pradetensis',u'Armeria arenaria subsp. praecox',u'Armeria belgenciensis',u'Armeria girardii',u'Armeria malinvaudii',u'Armeria maritima subsp. halleri',u'Armeria maritima subsp. maritima',u'Armeria maritima subsp. miscella',u'Armeria pubinervis',u'Armeria pungens',u'Armeria ruscinonensis',u'Armeria ruscinonensis subsp. littorifuga',u'Armeria ruscinonensis subsp. ruscinonensis',u'Armeria soleirolii',u'Armeria vulgaris',u'Arnica montana',u'Arnica montana var. atlantica',u'Arnica montana var. montana',u'Arnoseris minima',u'Artemisia alba',u'Artemisia borealis',u'Artemisia campestris',u'Artemisia campestris subsp. alpina',u'Artemisia campestris subsp. campestris',u'Artemisia campestris subsp. glutinosa',u'Artemisia campestris subsp. maritima',u'Artemisia eriantha',u'Artemisia insipida',u'Artemisia maritima',u'Artemisia maritima subsp. maritima',u'Artemisia maritima var. maritima',u'Artemisia maritima var. pseudogallica',u'Artemisia molinieri',u'Artemisia umbelliformis',u'Artemisia umbelliformis subsp. gabriellae',u'Artemisia umbelliformis subsp. umbelliformis',u'Arundo donaciformis',u'Arundo micrantha',u'Asarina procumbens',u'Asarum europaeum',u'Asarum europaeum subsp. europaeum',u'Asparagus acutifolius',u'Asparagus maritimus',u'Asparagus officinalis',u'Asparagus officinalis subsp. prostratus',u'Asparagus tenuifolius',u'Asperula arvensis',u'Asperula capillacea',u'Asperula hexaphylla',u'Asperula laevigata',u'Asperula occidentalis',u'Asperula taurina',u'Asperula taurina subsp. taurina',u'Asperula tinctoria',u'Asperula x jordanii',u'Asphodelus macrocarpus subsp. arrondeaui',u'Aster alpinus',u'Aster alpinus var. alpinus',u'Aster alpinus var. cebennensis',u'Aster amellus',u'Aster pyrenaeus',u'Astragalus alopecuroides',u'Astragalus alopecuroides subsp. alopecuroides',u'Astragalus alopecurus',u'Astragalus baionensis',u'Astragalus boeticus',u'Astragalus boeticus var. boeticus',u'Astragalus boeticus var. subinflatus',u'Astragalus cicer',u'Astragalus danicus',u'Astragalus echinatus',u'Astragalus glaux',u'Astragalus glycyphyllos',u'Astragalus leontinus',u'Astragalus monspessulanus',u'Astragalus monspessulanus subsp. monspessulanus',u'Astragalus tragacantha',u'Astrantia major',u'Astrantia major subsp. involucrata',u'Astrantia major subsp. major',u'Astrantia major var. involucrata',u'Astrantia major var. major',u'Astrantia major var. pyrenaica',u'Athamanta cretensis',u'Athamanta cretensis var. cretensis',u'Athamanta cretensis var. mutellinoides',u'Atocion armeria',u'Atractylis cancellata',u'Atractylis humilis',u'Atriplex glabriuscula',u'Atriplex littoralis',u'Atriplex longipes',u'Atropa belladonna',u'Avellinia festucoides',u'Baldellia ranunculoides',u'Bartsia alpina',u'Bartsia trixago',u'Bassia laniflora',u'Bellevalia romana',u'Bellevalia trifoliata',u'Bellis sylvestris',u'Berardia lanuginosa',u'Berberis vulgaris',u'Betonica alopecuros',u'Betonica alopecuros subsp. godronii',u'Betula nana',u'Betula pubescens var. glabrata',u'Bidens radiata',u'Biscutella arvernensis',u'Biscutella brevicaulis',u'Biscutella cichoriifolia',u'Biscutella laevigata',u'Biscutella laevigata subsp. laevigata',u'Biscutella laevigata subsp. varia',u'Biscutella lima',u'Biscutella rotgesii',u'Biserrula epiglottis',u'Biserrula pelecinus',u'Biserrula pelecinus subsp. pelecinus',u'Bistorta officinalis',u'Bituminaria bituminosa',u'Blackstonia acuminata',u'Blackstonia acuminata subsp. acuminata',u'Blackstonia imperfoliata',u'Blackstonia perfoliata',u'Blackstonia perfoliata subsp. intermedia',u'Blackstonia perfoliata subsp. perfoliata',u'Blysmus compressus',u'Bombycilaena discolor',u'Bombycilaena erecta',u'Bothriochloa ischaemum',u'Brachypodium distachyon',u'Brassica insularis',u'Brassica insularis var. angustifolia',u'Brassica insularis var. aquellae',u'Brassica insularis var. ayliesii',u'Brassica insularis var. insularis',u'Brassica montana',u'Brassica oleracea',u'Brassica oleracea subsp. oleracea',u'Brassica repanda',u'Brassica repanda subsp. galissieri',u'Brassica repanda subsp. repanda',u'Brassica repanda subsp. saxatilis',u'Bromus grossus',u'Bromus secalinus',u'Bufonia paniculata',u'Buglossoides gastonii',u'Buglossoides incrassata',u'Buglossoides purpurocaerulea',u'Buphthalmum salicifolium',u'Buphthalmum salicifolium subsp. salicifolium',u'Bupleurum falcatum',u'Bupleurum falcatum subsp. cernuum',u'Bupleurum falcatum subsp. falcatum',u'Bupleurum falcatum var. angustifolium',u'Bupleurum falcatum var. falcatum',u'Bupleurum falcatum var. petiolare',u'Bupleurum gerardi',u'Bupleurum longifolium',u'Bupleurum longifolium subsp. longifolium',u'Bupleurum ranunculoides',u'Bupleurum ranunculoides subsp. ranunculoides',u'Bupleurum ranunculoides subsp. telonense',u'Bupleurum ranunculoides var. gramineum',u'Bupleurum ranunculoides var. ranunculoides',u'Bupleurum semicompositum',u'Bupleurum tenuissimum',u'Bupleurum tenuissimum subsp. tenuissimum',u'Butomus umbellatus',u'Buxus sempervirens',u'Calamagrostis arundinacea',u'Calamagrostis canescens',u'Calamagrostis canescens subsp. canescens',u'Calamagrostis neglecta',u'Calamagrostis neglecta subsp. neglecta',u'Calamagrostis phragmitoides',u'Calamagrostis pseudophragmites',u'Calamagrostis pseudophragmites subsp. pseudophragmites',u'Caldesia parnassifolia',u'Calla palustris',u'Callitriche brutia',u'Callitriche hamulata',u'Callitriche truncata subsp. occidentalis',u'Campanula albicans',u'Campanula baumgartenii',u'Campanula cervicaria',u'Campanula cochleariifolia',u'Campanula erinus',u'Campanula glomerata',u'Campanula glomerata subsp. farinosa',u'Campanula glomerata subsp. glomerata',u'Campanula latifolia',u'Campanula patula',u'Campanula patula var. costae',u'Campanula patula var. patula',u'Campanula persicifolia',u'Campanula persicifolia var. hispida',u'Campanula persicifolia var. lasiocalyx',u'Campanula persicifolia var. persicifolia',u'Campanula rhomboidalis',u'Campanula rotundifolia subsp. hispanica',u'Campanula speciosa',u'Campanula thyrsoides',u'Canella winterana',u'Cardamine amara',u'Cardamine amara subsp. amara',u'Cardamine amara subsp. pyrenaea',u'Cardamine asarifolia',u'Cardamine bulbifera',u'Cardamine chelidonia',u'Cardamine dentata',u'Cardamine heptaphylla',u'Cardamine impatiens',u'Cardamine parviflora',u'Cardamine pentaphyllos',u'Cardamine plumieri',u'Cardamine raphanifolia',u'Carduus acicularis',u'Carduus aurosicus',u'Carduus defloratus',u'Carduus defloratus subsp. argemone',u'Carduus defloratus subsp. carlinifolius',u'Carduus defloratus subsp. defloratus',u'Carduus defloratus subsp. medius',u'Carduus defloratus subsp. rhaeticus',u'Carduus personata',u'Carex alba',u'Carex appropinquata',u'Carex arenaria',u'Carex atrofusca',u'Carex bicolor',u'Carex binervis',u'Carex bipartita',u'Carex bohemica',u'Carex brevicollis',u'Carex brizoides',u'Carex buxbaumii',u'Carex canescens',u'Carex cespitosa',u'Carex chordorrhiza',u'Carex colchica',u'Carex davalliana',u'Carex depauperata',u'Carex depressa',u'Carex depressa subsp. basilaris',u'Carex diandra',u'Carex digitata',u'Carex dioica',u'Carex distans',u'Carex divulsa',u'Carex elongata',u'Carex ericetorum',u'Carex extensa',u'Carex fimbriata',u'Carex firma',u'Carex frigida',u'Carex fritschii',u'Carex glacialis',u'Carex grioletii',u'Carex halleriana',u'Carex halleriana subsp. halleriana',u'Carex hartmanii',u'Carex heleonastes',u'Carex hordeistichos',u'Carex humilis',u'Carex lachenalii',u'Carex lachenalii subsp. lachenalii',u'Carex laevigata',u'Carex lasiocarpa',u'Carex lepidocarpa',u'Carex limosa',u'Carex liparocarpos',u'Carex liparocarpos subsp. liparocarpos',u'Carex magellanica subsp. irrigua',u'Carex mairei',u'Carex maritima',u'Carex melanostachya',u'Carex microglochin',u'Carex montana',u'Carex mucronata',u'Carex olbiensis',u'Carex ornithopoda',u'Carex ornithopoda subsp. elongata',u'Carex ornithopoda subsp. ornithopoda',u'Carex ornithopoda subsp. ornithopodioides',u'Carex pauciflora',u'Carex pendula',u'Carex pilosa',u'Carex praecox',u'Carex pseudobrizoides',u'Carex pseudocyperus',u'Carex pulicaris',u'Carex punctata',u'Carex remota',u'Carex repens',u'Carex strigosa',u'Carex tomentosa',u'Carex trinervis',u'Carex umbrosa var. umbrosa',u'Carex vaginata',u'Carex vulpina',u'Carlina acanthifolia',u'Carlina acanthifolia subsp. acanthifolia',u'Carlina acanthifolia subsp. cynara',u'Carlina acanthifolia subsp. lecoqii',u'Carlina acaulis',u'Carlina acaulis f. caulescens',u'Carlina acaulis f. nana',u'Carlina acaulis subsp. caulescens',u'Carlina biebersteinii',u'Carlina biebersteinii subsp. biebersteinii',u'Carlina corymbosa',u'Caropsis verticillato-inundata',u'Carpesium cernuum',u'Carthamus caeruleus',u'Carthamus lanatus',u'Carthamus mitissimus',u'Catabrosa aquatica',u'Catananche caerulea',u'Caucalis platycarpos',u'Caucalis platycarpos var. platycarpos',u'Centaurea collina',u'Centaurea corymbosa',u'Centaurea jordaniana',u'Centaurea jordaniana subsp. aemilii',u'Centaurea jordaniana subsp. balbisiana',u'Centaurea jordaniana subsp. jordaniana',u'Centaurea jordaniana subsp. verguinii',u'Centaurea melitensis',u'Centaurea pseudocineraria',u'Centaurea scabiosa subsp. alpestris',u'Centaurium chloodes',u'Centaurium erythraea var. capitatum',u'Centaurium favargeri',u'Centaurium littorale',u'Centaurium littorale subsp. littorale',u'Centaurium maritimum',u'Centaurium portense',u'Centaurium pulchellum',u'Centranthus lecoqii',u'Centranthus lecoqii subsp. lecoqii',u'Centranthus trinervis',u'Cephalanthera damasonium',u'Cephalanthera longifolia',u'Cephalanthera rubra',u'Cephalaria syriaca',u'Cephalaria transylvanica',u'Cerastium alpinum',u'Cerastium alpinum subsp. alpinum',u'Cerastium alpinum var. alpinum',u'Cerastium alpinum var. glabratum',u'Cerastium alpinum var. glanduliferum',u'Cerastium alpinum var. nevadense',u'Cerastium arvense',u'Cerastium arvense subsp. arvense',u'Cerastium arvense subsp. molle',u'Cerastium arvense subsp. strictum',u'Cerastium arvense subsp. suffruticosum',u'Cerastium comatum',u'Cerastium dubium',u'Cerastium pyrenaicum',u'Cerastium siculum',u'Ceratocapnos claviculata',u'Ceratonia siliqua',u'Ceratophyllum submersum',u'Cerinthe glabra subsp. glabra',u'Cerinthe glabra subsp. pyrenaica',u'Cerinthe tenuiflora',u'Cervaria rivini',u'Chaerophyllum aureum',u'Chaerophyllum bulbosum',u'Chaerophyllum nodosum',u'Chaetonychia cymosa',u'Chamaerops humilis',u'Chamaerops humilis var. humilis',u'Chamorchis alpina',u'Charybdis maritima',u'Charybdis undulata',u'Chiliadenus glutinosus',u'Chimaphila umbellata',u'Chondrilla juncea',u'Chrysosplenium alternifolium',u'Chrysosplenium oppositifolium',u'Cicendia filiformis',u'Cicuta virosa',u'Circaea alpina',u'Circaea alpina subsp. alpina',u'Circaea lutetiana',u'Circaea x intermedia',u'Cirsium alsophilum',u'Cirsium carniolicum subsp. rufescens',u'Cirsium erisithales',u'Cirsium glabrum',u'Cirsium heterophyllum',u'Cirsium monspessulanum',u'Cirsium monspessulanum subsp. monspessulanum',u'Cirsium tuberosum',u'Cistus crispus',u'Cistus inflatus',u'Cistus lasianthus subsp. alyssoides',u'Cistus laurifolius',u'Cistus laurifolius subsp. laurifolius',u'Cistus populifolius',u'Cistus populifolius subsp. populifolius',u'Cistus pouzolzii',u'Cistus salviifolius',u'Cistus umbellatus',u'Cistus umbellatus subsp. umbellatus',u'Cistus umbellatus subsp. viscosus',u'Cistus x revolii',u'Cistus x revolii subsp. revolii',u'Cladium mariscus',u'Cladium mariscus subsp. jamaicense',u'Clematis flammula',u'Clematis flammula var. flammula',u'Clematis flammula var. maritima',u'Clypeola jonthlaspi',u'Cneorum tricoccon',u'Cochlearia aestuaria',u'Cochlearia anglica',u'Cochlearia officinalis',u'Cochlearia pyrenaica',u'Coeloglossum viride',u'Cohniella juncifolia',u'Colchicum autumnale',u'Colchicum corsicum',u'Colchicum cupanii',u'Colchicum filifolium',u'Coleanthus subtilis',u'Colubrina elliptica',u'Comarum palustre',u'Comastoma tenellum',u'Convallaria majalis',u'Convolvulus cantabrica',u'Convolvulus lanuginosus',u'Convolvulus lineatus',u'Convolvulus siculus',u'Convolvulus silvaticus',u'Convolvulus soldanella',u'Corallorhiza trifida',u'Corispermum pallasii',u'Cornus mas',u'Coronilla coronata',u'Coronilla minima',u'Coronilla minima subsp. lotoides',u'Coronilla minima subsp. minima',u'Coronilla scorpioides',u'Coronilla securidaca',u'Coronilla vaginalis',u'Coronilla valentina',u'Coronilla varia',u'Corrigiola telephiifolia',u'Corydalis intermedia',u'Corydalis solida',u'Corydalis solida var. integra',u'Corydalis solida var. solida',u'Corynephorus canescens',u'Cotoneaster delphinensis',u'Cotoneaster integerrimus',u'Cotoneaster tomentosus',u'Crambe maritima',u'Crassula tillaea',u'Crassula vaillantii',u'Crepis aurea',u'Crepis aurea subsp. aurea',u'Crepis dioscoridis',u'Crepis paludosa',u'Crepis praemorsa',u'Crepis pyrenaica',u'Crepis rhaetica',u'Crepis suffreniana',u'Cressa cretica',u'Crithmum maritimum',u'Crocus ligusticus',u'Crocus neapolitanus',u'Crocus nudiflorus',u'Crocus vernus',u'Crucianella maritima',u'Crypsis aculeata',u'Crypsis alopecuroides',u'Crypsis schoenoides',u'Cupania americana',u'Cupania triquetra',u'Cuscuta europaea',u'Cutandia maritima',u'Cyanus montanus',u'Cyanus triumfettii',u'Cyclamen balearicum',u'Cyclamen purpurascens',u'Cyclamen repandum',u'Cymodocea nodosa',u'Cynanchum acutum',u'Cynoglossum dioscoridis',u'Cynoglossum germanicum',u'Cynoglossum germanicum subsp. germanicum',u'Cynoglossum germanicum subsp. pellucidum',u'Cynoglossum germanicum subsp. rotundum',u'Cynophalla hastata',u'Cynosurus echinatus',u'Cyperus capitatus',u'Cyperus fuscus',u'Cyperus laevigatus',u'Cyperus laevigatus subsp. distachyos',u'Cyperus longus',u'Cyperus michelianus',u'Cypripedium calceolus',u'Cytisophyllum sessilifolium',u'Cytisus ardoinoi',u'Cytisus ardoinoi subsp. ardoinoi',u'Cytisus ardoinoi subsp. sauzeanus',u'Cytisus decumbens',u'Cytisus elongatus',u'Cytisus hirsutus',u'Cytisus oromediterraneus',u'Cytisus scoparius subsp. maritimus',u'Daboecia cantabrica',u'Daboecia cantabrica var. alba',u'Daboecia cantabrica var. cantabrica',u'Dactylorhiza elata',u'Dactylorhiza fuchsii',u'Dactylorhiza fuchsii var. fuchsii',u'Dactylorhiza fuchsii var. psychrophila',u'Dactylorhiza incarnata',u'Dactylorhiza incarnata f. incarnata',u'Dactylorhiza incarnata f. ochrantha',u'Dactylorhiza incarnata subsp. cruenta',u'Dactylorhiza incarnata subsp. incarnata',u'Dactylorhiza incarnata subsp. pyrenaica',u'Dactylorhiza incarnata var. brevibracteata',u'Dactylorhiza incarnata var. dufftii',u'Dactylorhiza incarnata var. hyphaematodes',u'Dactylorhiza incarnata var. incarnata',u'Dactylorhiza incarnata var. latissima',u'Dactylorhiza incarnata var. reichenbachii',u'Dactylorhiza incarnata var. serotina',u'Dactylorhiza incarnata var. straminea',u'Dactylorhiza majalis',u'Dactylorhiza majalis subsp. alpestris',u'Dactylorhiza majalis subsp. majalis',u'Dactylorhiza praetermissa',u'Dactylorhiza praetermissa subsp. integrata',u'Dactylorhiza praetermissa subsp. praetermissa',u'Dactylorhiza praetermissa var. integrata',u'Dactylorhiza praetermissa var. junialis',u'Dactylorhiza praetermissa var. maculosa',u'Dactylorhiza praetermissa var. praetermissa',u'Dactylorhiza sambucina',u'Dactylorhiza sambucina f. rubra',u'Dactylorhiza sambucina f. sambucina',u'Dactylorhiza sphagnicola',u'Dactylorhiza traunsteineri',u'Dactylorhiza traunsteineri subsp. lapponica',u'Dactylorhiza traunsteineri subsp. traunsteineri',u'Damasonium alisma',u'Damasonium polyspermum',u'Danthonia alpina',u'Danthonia decumbens subsp. decumbens',u'Daphne alpina',u'Daphne cneorum',u'Daphne gnidium',u'Daphne laureola',u'Daphne laureola subsp. laureola',u'Daphne laureola subsp. philippi',u'Daphne mezereum',u'Daphne striata',u'Dasiphora fruticosa',u'Daucus carota subsp. gadecaei',u'Delphinium ajacis',u'Delphinium dubium',u'Delphinium elatum',u'Delphinium elatum subsp. helveticum',u'Delphinium fissum',u'Delphinium fissum subsp. fissum',u'Delphinium verdunense',u'Deschampsia media',u'Deschampsia media subsp. media',u'Descurainia sophia',u'Dianthus armeria',u'Dianthus armeria subsp. armeria',u'Dianthus arrosti',u'Dianthus balbisii',u'Dianthus balbisii subsp. balbisii',u'Dianthus barbatus',u'Dianthus barbatus subsp. barbatus',u'Dianthus benearnensis',u'Dianthus carthusianorum',u'Dianthus carthusianorum subsp. atrorubens',u'Dianthus carthusianorum subsp. carthusianorum',u'Dianthus caryophyllus',u'Dianthus deltoides',u'Dianthus deltoides subsp. deltoides',u'Dianthus furcatus',u'Dianthus furcatus subsp. furcatus',u'Dianthus gallicus',u'Dianthus geminiflorus',u'Dianthus godronianus',u'Dianthus graniticus',u'Dianthus gratianopolitanus',u'Dianthus gyspergerae',u'Dianthus hyssopifolius',u'Dianthus longicaulis',u'Dianthus pavonius',u'Dianthus pungens',u'Dianthus pungens subsp. pungens',u'Dianthus pungens subsp. ruscinonensis',u'Dianthus pyrenaicus',u'Dianthus pyrenaicus subsp. attenuatus',u'Dianthus pyrenaicus subsp. pyrenaicus',u'Dianthus saxicola',u'Dianthus scaber',u'Dianthus seguieri',u'Dianthus seguieri subsp. pseudocollinus',u'Dianthus seguieri subsp. requienii',u'Dianthus seguieri subsp. seguieri',u'Dianthus subacaulis',u'Dianthus superbus',u'Dianthus superbus subsp. autumnalis',u'Dianthus superbus subsp. superbus',u'Dianthus vigoi',u'Dianthus x aschersonii',u'Dianthus x borderei',u'Dianthus x bottemeri',u'Dianthus x courtoisii',u'Dianthus x digeneus',u'Dianthus x dufftii',u'Dianthus x exilis',u'Dianthus x fallens',u'Dianthus x flahaultii',u'Dianthus x gisellae',u'Dianthus x hanryi',u'Dianthus x hellwigii',u'Dianthus x heterophyllus',u'Dianthus x huebneri',u'Dianthus x jaczonis',u'Dianthus x laucheanus',u'Dianthus x lisae',u'Dianthus x loretii',u'Dianthus x mammingianorum',u'Dianthus x mikii',u'Dianthus x ponsii',u'Dianthus x rouyanus',u'Dianthus x saxatilis',u'Dianthus x subfissus',u'Dianthus x varians',u'Dianthus x warionii',u'Dichoropetalum carvifolia',u'Dichoropetalum schottii',u'Dictamnus albus',u'Digitalis grandiflora',u'Digitalis lutea',u'Dioscorea pyrenaica',u'Dipcadi serotinum',u'Diplotaxis viminea',u'Diplotaxis viminea var. integrifolia',u'Diplotaxis viminea var. viminea',u'Dipsacus laciniatus',u'Dipsacus pilosus',u'Doronicum austriacum',u'Doronicum clusii',u'Doronicum pardalianches',u'Doronicum plantagineum',u'Dorycnopsis gerardi',u'Draba aizoides',u'Draba dubia subsp. laevipes',u'Draba incana',u'Draba loiseleurii',u'Draba muralis',u'Draba nemorosa',u'Dracocephalum austriacum',u'Dracocephalum ruyschiana',u'Drosera intermedia',u'Drosera longifolia',u'Drosera rotundifolia',u'Dryas octopetala',u'Drymocallis rupestris',u'Echinophora spinosa',u'Echium asperrimum',u'Echium plantagineum',u'Elatine alsinastrum',u'Elatine brochonii',u'Elatine hexandra',u'Elatine hydropiper',u'Elatine macropoda',u'Elatine triandra',u'Eleocharis acicularis',u'Eleocharis multicaulis',u'Eleocharis ovata',u'Eleocharis quinqueflora',u'Eleocharis uniglumis',u'Elleanthus cephalotus',u'Elleanthus dussii',u'Elytrigia corsica',u'Elytrigia elongata subsp. elongata',u'Empetrum nigrum',u'Empetrum nigrum subsp. hermaphroditum',u'Empetrum nigrum subsp. nigrum',u'Endressia pyrenaica',u'Epilobium alsinifolium',u'Epilobium anagallidifolium',u'Epilobium dodonaei',u'Epilobium dodonaei subsp. dodonaei',u'Epilobium dodonaei subsp. fleischeri',u'Epilobium dodonaei subsp. prantlii',u'Epilobium duriaei',u'Epilobium nutans',u'Epipactis atrorubens',u'Epipactis helleborine',u'Epipactis helleborine subsp. helleborine',u'Epipactis helleborine subsp. lusitanica',u'Epipactis helleborine subsp. minor',u'Epipactis helleborine subsp. neerlandica',u'Epipactis helleborine subsp. tremolsii',u'Epipactis leptochila',u'Epipactis leptochila subsp. leptochila',u'Epipactis leptochila subsp. provincialis',u'Epipactis microphylla',u'Epipactis muelleri',u'Epipactis palustris',u'Epipactis phyllanthes',u'Epipactis phyllanthes var. degenera',u'Epipactis phyllanthes var. olarionensis',u'Epipactis phyllanthes var. phyllanthes',u'Epipactis purpurata',u'Epipogium aphyllum',u'Erica carnea',u'Erica ciliaris',u'Erica cinerea',u'Erica erigena',u'Erica lusitanica',u'Erica lusitanica subsp. cantabrica',u'Erica scoparia',u'Erica scoparia subsp. scoparia',u'Erica tetralix',u'Erica vagans',u'Erigeron alpinus',u'Erigeron alpinus subsp. alpinus',u'Erigeron alpinus subsp. intermedius',u'Erigeron paolii',u'Erinacea anthyllis',u'Erinacea anthyllis subsp. anthyllis',u'Eriophorum angustifolium',u'Eriophorum angustifolium subsp. angustifolium',u'Eriophorum gracile',u'Eriophorum latifolium',u'Eriophorum scheuchzeri',u'Eriophorum vaginatum',u'Erodium botrys',u'Erodium foetidum',u'Erodium glandulosum',u'Erodium malacoides',u'Erodium manescavii',u'Erodium maritimum',u'Erodium rodiei',u'Eruca vesicaria',u'Erucastrum nasturtiifolium',u'Erucastrum nasturtiifolium subsp. nasturtiifolium',u'Erucastrum nasturtiifolium subsp. sudrei',u'Erucastrum supinum',u'Eryngium alpinum',u'Eryngium campestre',u'Eryngium maritimum',u'Eryngium pusillum',u'Eryngium spinalba',u'Eryngium viviparum',u'Erysimum cheiranthoides',u'Erysimum cheiranthoides subsp. cheiranthoides',u'Erysimum incanum',u'Erysimum incanum subsp. aurigeranum',u'Erythronium dens-canis',u'Eudianthe coelirosa',u'Eudianthe laeta',u'Eugenia gryposperma',u'Euonymus latifolius',u'Euphorbia corsica',u'Euphorbia dulcis',u'Euphorbia dulcis subsp. incompta',u'Euphorbia esula',u'Euphorbia esula subsp. esula',u'Euphorbia esula subsp. saratoi',u'Euphorbia falcata',u'Euphorbia falcata subsp. falcata',u'Euphorbia falcata var. acuminata',u'Euphorbia falcata var. falcata',u'Euphorbia flavicoma subsp. costeana',u'Euphorbia flavicoma subsp. verrucosa',u'Euphorbia graminifolia',u'Euphorbia hyberna',u'Euphorbia palustris',u'Euphorbia peplis',u'Euphorbia segetalis subsp. portlandica',u'Euphorbia seguieriana',u'Euphorbia seguieriana subsp. loiseleurii',u'Euphorbia seguieriana subsp. seguieriana',u'Euphorbia terracina',u'Euphorbia variabilis',u'Euphorbia variabilis subsp. valliniana',u'Euphrasia salisburgensis',u'Exaculum pusillum',u'Fagus sylvatica',u'Falcaria vulgaris',u'Fallopia dumetorum',u'Ferulago campestris',u'Festuca amethystina',u'Festuca amethystina subsp. amethystina',u'Festuca borderei',u'Festuca duvalii',u'Festuca lahonderei',u'Festuca marginata subsp. gallica',u'Festuca ovina subsp. bigoudenensis',u'Festuca patzkei',u'Festuca valesiaca',u'Filago carpetana',u'Filago tyrrhenica',u'Filipendula vulgaris',u'Fimbristylis bisumbellata',u'Fourraea alpina',u'Frankenia laevis',u'Fraxinus angustifolia',u'Fraxinus angustifolia subsp. angustifolia',u'Fritillaria meleagris',u'Fritillaria moggridgei',u'Fritillaria montana',u'Fritillaria pyrenaica',u'Fritillaria tubiformis',u'Fuirena pubescens',u'Fumana ericoides',u'Fumana procumbens',u'Gagea bohemica',u'Gagea bohemica subsp. bohemica',u'Gagea bohemica subsp. saxatilis',u'Gagea bohemica var. bohemica',u'Gagea bohemica var. corsica',u'Gagea granatelli',u'Gagea lacaitae',u'Gagea lutea',u'Gagea minima',u'Gagea pratensis',u'Gagea soleirolii',u'Gagea spathacea',u'Gagea villosa',u'Galanthus nivalis',u'Galanthus nivalis var. nivalis',u'Galatella linosyris',u'Galatella linosyris var. armoricana',u'Galatella linosyris var. linosyris',u'Galeopsis segetum',u'Galium boreale',u'Galium debile',u'Galium fleurotii',u'Galium fleurotii var. bretonii',u'Galium fleurotii var. fleurotii',u'Galium fleurotii var. gracilicaule',u'Galium glaucum',u'Galium minutulum',u'Galium neglectum',u'Galium rubioides',u'Galium saxatile',u'Galium trifidum',u'Galium verrucosum',u'Galium verrucosum var. halophilum',u'Galium verrucosum var. verrucosum',u'Gasparrinia peucedanoides',u'Genista aetnensis',u'Genista aetnensis subsp. fraisseorum',u'Genista anglica',u'Genista anglica var. anglica',u'Genista anglica var. subinermis',u'Genista delphinensis',u'Genista florida',u'Genista florida subsp. polygaliphylla',u'Genista germanica',u'Genista horrida',u'Genista linifolia',u'Genista lobelii',u'Genista pilosa',u'Genista pilosa subsp. cebennensis',u'Genista pilosa subsp. jordanii',u'Genista pilosa subsp. pilosa',u'Genista pulchella subsp. villarsiana',u'Genista radiata',u'Genista sagittalis',u'Genista scorpius',u'Genista tinctoria',u'Gennaria diphylla',u'Gentiana acaulis',u'Gentiana acaulis var. acaulis',u'Gentiana acaulis var. minor',u'Gentiana asclepiadea',u'Gentiana clusii',u'Gentiana clusii subsp. clusii',u'Gentiana clusii subsp. costei',u'Gentiana clusii subsp. pyrenaica',u'Gentiana cruciata',u'Gentiana ligustica',u'Gentiana lutea',u'Gentiana lutea subsp. lutea',u'Gentiana pneumonanthe',u'Gentiana pneumonanthe subsp. pneumonanthe',u'Gentiana pneumonanthe var. latifolia',u'Gentiana pneumonanthe var. pneumonanthe',u'Gentiana utriculosa',u'Gentiana verna',u'Gentiana verna subsp. delphinensis',u'Gentiana verna subsp. verna',u'Gentianella amarella',u'Gentianella campestris',u'Gentianella campestris f. campestris',u'Gentianella campestris f. hypericifolia',u'Gentianella campestris subsp. baltica',u'Gentianella germanica',u'Gentianopsis ciliata',u'Geonoma pinnatifrons',u'Geonoma pinnatifrons subsp. martinicensis',u'Geranium argenteum',u'Geranium bohemicum',u'Geranium cinereum',u'Geranium endressii',u'Geranium lanuginosum',u'Geranium lucidum',u'Geranium macrorrhizum',u'Geranium nodosum',u'Geranium palustre',u'Geranium phaeum',u'Geranium phaeum var. lividum',u'Geranium phaeum var. phaeum',u'Geranium sanguineum',u'Geranium sanguineum var. sanguineum',u'Geranium sylvaticum',u'Geranium tuberosum',u'Geum heterocarpum',u'Geum hispidum',u'Geum rivale',u'Gladiolus dubius',u'Gladiolus gallaecicus',u'Gladiolus italicus',u'Gladiolus palustris',u'Glandora prostrata',u'Glandora prostrata subsp. prostrata',u'Glebionis segetum',u'Globularia bisnagarica',u'Globularia cordifolia',u'Globularia nudicaulis',u'Globularia nudicaulis f. nudicaulis',u'Globularia vulgaris',u'Glyceria maxima',u'Gnaphalium uliginosum',u'Goodyera repens',u'Gratiola officinalis',u'Guaiacum officinale',u'Gymnadenia conopsea',u'Gymnadenia nigra',u'Gymnadenia nigra f. bourneriasii',u'Gymnadenia nigra f. corneliana',u'Gymnadenia nigra f. vesubiana',u'Gymnadenia nigra subsp. austriaca',u'Gymnadenia nigra subsp. cenisia',u'Gymnadenia nigra subsp. corneliana',u'Gymnadenia nigra subsp. delphineae',u'Gymnadenia nigra subsp. eggeriana',u'Gymnadenia nigra subsp. gabasiana',u'Gymnadenia nigra subsp. rhellicani',u'Gymnadenia odoratissima',u'Hackelia deflexa',u'Halimione pedunculata',u'Hammarbya paludosa',u'Hedysarum boutignyanum',u'Hedysarum boveanum subsp. europaeum',u'Hedysarum spinosissimum',u'Helianthemum aegyptiacum',u'Helianthemum apenninum',u'Helianthemum apenninum subsp. apenninum',u'Helianthemum apenninum subsp. croceum',u'Helianthemum apenninum subsp. lazarei',u'Helianthemum apenninum var. apenninum',u'Helianthemum apenninum var. virgatum',u'Helianthemum canum',u'Helianthemum canum var. canum',u'Helianthemum canum var. dolomiticum',u'Helianthemum canum var. piloselloides',u'Helianthemum ledifolium',u'Helianthemum lunulatum',u'Helianthemum marifolium',u'Helianthemum marifolium subsp. marifolium',u'Helianthemum nummularium',u'Helianthemum salicifolium',u'Helianthemum syriacum',u'Helichrysum arenarium',u'Helichrysum italicum',u'Helichrysum italicum subsp. italicum',u'Helichrysum italicum subsp. microphyllum',u'Helichrysum italicum subsp. serotinum',u'Helichrysum stoechas',u'Helichrysum stoechas subsp. stoechas',u'Helicodiceros muscivorus',u'Helictochloa marginata',u'Helictochloa pratensis',u'Helictochloa pratensis subsp. amethystea',u'Helictochloa pratensis subsp. iberica',u'Helictochloa pratensis subsp. pratensis',u'Helictotrichon cantabricum',u'Heliotropium supinum',u'Helleborus foetidus',u'Helleborus niger',u'Helleborus viridis subsp. occidentalis',u'Helosciadium inundatum',u'Helosciadium repens',u'Heracleum pumilum',u'Herminium monorchis',u'Herniaria litardierei',u'Hesperis matronalis subsp. inodora',u'Heteropogon contortus',u'Hibiscus palustris',u'Hieracium alpinum',u'Hieracium eriophorum',u'Hieracium fourcadei',u'Hieracium humile',u'Hieracium massoniae',u'Hieracium scorzonerifolium',u'Hieracium vogesiacum',u'Hierochloe odorata',u'Hierochloe odorata subsp. odorata',u'Hieronyma alchorneoides',u'Himantoglossum hircinum',u'Hippocrepis comosa',u'Hippocrepis emerus',u'Hippocrepis emerus subsp. emerus',u'Hippuris vulgaris',u'Holosteum breistrofferi',u'Honckenya peploides',u'Honckenya peploides subsp. peploides',u'Honorius nutans',u'Hordelymus europaeus',u'Hordeum marinum',u'Hordeum secalinum',u'Hormathophylla halimifolia',u'Hormathophylla lapeyrousiana',u'Hormathophylla macrocarpa',u'Hormathophylla pyrenaica',u'Hormathophylla spinosa',u'Horminum pyrenaicum',u'Hornungia petraea',u'Hornungia procumbens',u'Hornungia procumbens var. pauciflorus',u'Hornungia procumbens var. procumbens',u'Hornungia procumbens var. revelierei',u'Hottonia palustris',u'Hyacinthoides italica',u'Hyacinthoides non-scripta',u'Hyacinthus orientalis',u'Hydrocharis morsus-ranae',u'Hydrocotyle vulgaris',u'Hyoseris scabra',u'Hypecoum procumbens',u'Hypericum androsaemum',u'Hypericum elodes',u'Hypericum gentianoides',u'Hypericum linariifolium',u'Hypericum montanum',u'Hypericum richeri',u'Hypericum richeri subsp. burseri',u'Hypericum richeri subsp. richeri',u'Hypericum x desetangsii',u'Hypericum x desetangsii nothosubsp. carinthiacum',u'Hypericum x desetangsii nothosubsp. desetangsii',u'Hypochaeris maculata',u'Hyssopus officinalis',u'Hyssopus officinalis subsp. aristatus',u'Hyssopus officinalis subsp. canescens',u'Hyssopus officinalis subsp. montanus',u'Hyssopus officinalis subsp. officinalis',u'Iberis amara',u'Iberis aurosica',u'Iberis bernardiana',u'Iberis carnosa',u'Iberis carnosa subsp. carnosa',u'Iberis intermedia',u'Iberis intermedia subsp. beugesiaca',u'Iberis intermedia subsp. intermedia',u'Iberis intermedia subsp. violletii',u'Iberis intermedia var. collina',u'Iberis intermedia var. contejanii',u'Iberis intermedia var. delphinensis',u'Iberis intermedia var. durandii',u'Iberis intermedia var. lamottei',u'Iberis intermedia var. maialis',u'Iberis intermedia var. polita',u'Iberis intermedia var. villarsii',u'Iberis linifolia',u'Iberis linifolia subsp. linifolia',u'Iberis linifolia subsp. stricta',u'Iberis nana',u'Iberis saxatilis',u'Iberis saxatilis subsp. saxatilis',u'Iberis timeroyi',u'Illecebrum verticillatum',u'Impatiens noli-tangere',u'Imperata cylindrica',u'Inula bifrons',u'Inula britannica',u'Inula helenioides',u'Inula helvetica',u'Inula hirta',u'Inula montana',u'Inula salicina',u'Ionopsidium glastifolium',u'Ipomoea sagittata',u'Iris graminea',u'Iris lutescens',u'Iris lutescens subsp. lutescens',u'Iris perrieri',u'Iris reichenbachiana',u'Iris sibirica',u'Iris tuberosa',u'Iris xiphium',u'Isatis alpina',u'Isolepis fluitans',u'Isopyrum thalictroides',u'Jacobaea adonidifolia',u'Jacobaea erratica',u'Jacobaea leucophylla',u'Jacobaea paludosa',u'Jacobaea paludosa subsp. angustifolia',u'Jacobaea uniflora',u'Jasione crispa subsp. arvernensis',u'Jasione laevis',u'Jasione montana',u'Jasione montana subsp. montana',u'Jasione montana var. imbricans',u'Jasione montana var. latifolia',u'Jasione montana var. littoralis',u'Jasione montana var. montana',u'Jasminum fruticans',u'Juncus alpinoarticulatus subsp. fuscoater',u'Juncus anceps',u'Juncus arcticus',u'Juncus balticus subsp. pyrenaeus',u'Juncus bulbosus',u'Juncus bulbosus subsp. bulbosus',u'Juncus bulbosus subsp. kochii',u'Juncus capitatus',u'Juncus gerardi',u'Juncus heterophyllus',u'Juncus pygmaeus',u'Juncus squarrosus',u'Juncus striatus',u'Juncus subnodulosus',u'Juncus tenageia',u'Jurinea humilis',u'Kadenia dubia',u'Kali soda',u'Kalmia procumbens',u'Kengia serotina subsp. serotina',u'Kickxia cirrhosa',u'Kickxia commutata',u'Kickxia commutata subsp. commutata',u'Klasea lycopifolia',u'Klasea nudicaulis',u'Knautia godetii',u'Koeleria cenisia',u'Koeleria pyramidata',u'Koeleria pyramidata subsp. pyramidata',u'Koeleria vallesiana',u'Koeleria vallesiana subsp. abbreviata',u'Koeleria vallesiana subsp. humilis',u'Koeleria vallesiana subsp. vallesiana',u'Koeleria vallesiana var. alpicola',u'Koeleria vallesiana var. pubescens',u'Koeleria vallesiana var. vallesiana',u'Kosteletzkya pentacarpos',u'Lactuca perennis',u'Lactuca plumieri',u'Lactuca quercina',u'Lactuca quercina subsp. chaixii',u'Lamium hybridum',u'Laphangium luteoalbum',u'Laser trilobum',u'Laserpitium gallicum',u'Laserpitium gallicum subsp. gallicum',u'Laserpitium gallicum var. angustifolium',u'Laserpitium gallicum var. gallicum',u'Laserpitium gallicum var. platyphyllum',u'Laserpitium latifolium',u'Laserpitium latifolium subsp. latifolium',u'Laserpitium latifolium var. glabrum',u'Laserpitium latifolium var. latifolium',u'Laserpitium prutenicum',u'Laserpitium prutenicum subsp. dufourianum',u'Laserpitium prutenicum subsp. prutenicum',u'Lathraea clandestina',u'Lathraea squamaria',u'Lathyrus bauhinii',u'Lathyrus heterophyllus',u'Lathyrus heterophyllus var. heterophyllus',u'Lathyrus japonicus subsp. maritimus',u'Lathyrus niger',u'Lathyrus niger subsp. niger',u'Lathyrus niger var. angustifolius',u'Lathyrus niger var. niger',u'Lathyrus palustris',u'Lathyrus pannonicus var. asphodeloides',u'Lathyrus sphaericus',u'Lathyrus sylvestris',u'Lathyrus sylvestris subsp. pyrenaicus',u'Lathyrus sylvestris subsp. sylvestris',u'Lathyrus venetus',u'Lavandula latifolia',u'Leersia oryzoides',u'Legousia falcata subsp. castellana',u'Legousia hybrida',u'Legousia speculum-veneris',u'Lemna trisulca',u'Leontodon hispidus subsp. hyoseroides',u'Leontodon hispidus var. hyoseroides',u'Leontodon hispidus var. pseudocrispus',u'Leontopodium nivale',u'Leontopodium nivale subsp. alpinum',u'Leonurus cardiaca',u'Leucanthemopsis alpina subsp. tomentosa',u'Leucanthemum burnatii',u'Leucanthemum corsicum',u'Leucanthemum corsicum subsp. corsicum',u'Leucanthemum corsicum subsp. fenzlii',u'Leucanthemum crassifolium',u'Leucanthemum graminifolium',u'Leucanthemum graminifolium var. controversum',u'Leucanthemum graminifolium var. graminifolium',u'Leucanthemum maximum',u'Leucanthemum meridionale',u'Leucanthemum monspeliense',u'Leucanthemum subglaucum',u'Leucojum aestivum',u'Leucojum vernum',u'Leucopoa pulchella',u'Leucopoa pulchella subsp. jurana',u'Leucopoa pulchella subsp. pulchella',u'Leymus arenarius',u'Libanotis pyrenaica',u'Libanotis pyrenaica subsp. pyrenaica',u'Libanotis pyrenaica var. libanotis',u'Libanotis pyrenaica var. pyrenaica',u'Ligularia sibirica',u'Lilium bulbiferum var. croceum',u'Lilium martagon',u'Lilium pomponium',u'Lilium pyrenaicum',u'Limbarda crithmoides',u'Limbarda crithmoides subsp. crithmoides',u'Limbarda crithmoides subsp. longifolia',u'Limodorum abortivum',u'Limodorum trabutianum',u'Limoniastrum monopetalum',u'Limoniastrum monopetalum subsp. monopetalum',u'Limonium articulatum',u'Limonium auriculiursifolium',u'Limonium auriculiursifolium x Limonium ovalifolium',u'Limonium auriculiursifolium x Limonium virgatum',u'Limonium bellidifolium',u'Limonium binervosum',u'Limonium binervosum subsp. binervosum',u'Limonium binervosum x Limonium dodartii',u'Limonium binervosum x Limonium vulgare',u'Limonium bonifaciense',u'Limonium companyonis',u'Limonium confusum',u'Limonium contortirameum',u'Limonium cordatum',u'Limonium cordatum x Limonium pseudominutum',u'Limonium corsicum',u'Limonium cuspidatum',u'Limonium densissimum',u'Limonium dodartii',u'Limonium dubium',u'Limonium duriusculum',u'Limonium echioides',u'Limonium florentinum',u'Limonium geronense',u'Limonium girardianum',u'Limonium greuteri',u'Limonium humile',u'Limonium lambinonii',u'Limonium legrandii',u'Limonium narbonense',u'Limonium narbonense x Limonium vulgare',u'Limonium normannicum',u'Limonium obtusifolium',u'Limonium ovalifolium',u'Limonium patrimoniense',u'Limonium portovecchiense',u'Limonium portovecchiense x Limonium virgatum',u'Limonium pseudominutum',u'Limonium strictissimum',u'Limonium tarcoense',u'Limonium virgatum',u'Limonium vulgare',u'Limonium x abnorme',u'Limonium x ambiguum',u'Limonium x glaucophyllum',u'Limonium x neumannii',u'Limonium x pseudoconfusum',u'Limonium x sennenii',u'Limonium x virgatoformis',u'Limosella aquatica',u'Linaria alpina',u'Linaria alpina subsp. aciculifolia',u'Linaria alpina subsp. alpina',u'Linaria alpina subsp. petraea',u'Linaria arenaria',u'Linaria flava',u'Linaria flava subsp. sardoa',u'Linaria pelisseriana',u'Linaria reflexa',u'Linaria spartea',u'Linaria supina',u'Linaria supina subsp. maritima',u'Linaria supina subsp. pyrenaica',u'Linaria supina subsp. supina',u'Linaria thymifolia',u'Linaria triphylla',u'Lindernia procumbens',u'Linnaea borealis',u'Linum austriacum',u'Linum leonii',u'Linum strictum',u'Linum strictum subsp. corymbulosum',u'Linum strictum subsp. strictum',u'Linum strictum var. spicatum',u'Linum strictum var. strictum',u'Linum viscosum',u'Liparis loeselii',u'Liparis loeselii var. loeselii',u'Liparis loeselii var. ovata',u'Littorella uniflora',u'Lobelia dortmanna',u'Lobelia urens',u'Loeflingia hispanica',u'Logfia minima',u'Lolium parabolicae',u'Lomelosia graminifolia',u'Loncomelos pyrenaicus',u'Loncomelos pyrenaicus subsp. pyrenaicus',u'Lonicera caerulea',u'Lonicera caerulea subsp. caerulea',u'Lotus angustissimus',u'Lotus conimbricensis',u'Lotus maritimus',u'Lotus maritimus var. hirsutus',u'Lotus maritimus var. maritimus',u'Lotus parviflorus',u'Lotus tetragonolobus',u'Ludwigia palustris',u'Lunaria rediviva',u'Lupinus angustifolius',u'Lupinus angustifolius subsp. angustifolius',u'Lupinus angustifolius subsp. reticulatus',u'Luronium natans',u'Luzula luzulina',u'Luzula nivea',u'Luzula sylvatica',u'Luzula sylvatica subsp. sieberi',u'Luzula sylvatica subsp. sylvatica',u'Lysimachia ephemerum',u'Lysimachia europaea',u'Lysimachia maritima',u'Lysimachia minima',u'Lysimachia nummularia',u'Lysimachia tenella',u'Lysimachia thyrsiflora',u'Lysimachia tyrrhenia',u'Lythrum borysthenicum',u'Lythrum hyssopifolia',u'Lythrum thesioides',u'Lythrum thymifolium',u'Lythrum tribracteatum',u'Maclura tinctoria',u'Macrosyringion glutinosum',u'Maianthemum bifolium',u'Malcolmia ramosissima',u'Malva punctata',u'Malva subovata',u'Matthiola fruticulosa',u'Matthiola tricuspidata',u'Matthiola valesiaca',u'Medicago marina',u'Medicago monspeliaca',u'Medicago orbicularis',u'Medicago orbicularis var. castellana',u'Medicago orbicularis var. glandulosa',u'Medicago orbicularis var. marginata',u'Medicago orbicularis var. orbicularis',u'Medicago polyceratia',u'Medicago rugosa',u'Medicago sativa subsp. glomerata',u'Medicago secundiflora',u'Medicago soleirolii',u'Melampyrum cristatum',u'Melampyrum sylvaticum',u'Melica ciliata',u'Melica ciliata subsp. ciliata',u'Melica ciliata subsp. magnolii',u'Melica ciliata subsp. thuringiaca',u'Melica ciliata subsp. transsilvanica',u'Melica ciliata var. typhina',u'Melica nutans',u'Melilotus messanensis',u'Meliosma herbertii',u'Melomphis arabica',u'Mentha cervina',u'Mentha pulegium',u'Menyanthes trifoliata',u'Mesembryanthemum crystallinum',u'Mesembryanthemum nodiflorum',u'Meum athamanticum',u'Meum athamanticum subsp. athamanticum',u'Miconia angustifolia',u'Micranthes clusii',u'Micranthes hieraciifolia',u'Micranthes stellaris',u'Micromeria graeca subsp. graeca',u'Micropyrum tenellum',u'Micropyrum tenellum f. aristatum',u'Micropyrum tenellum f. tenellum',u'Milium vernale',u'Milium vernale subsp. scabrum',u'Milium vernale subsp. vernale',u'Minuartia capillacea',u'Minuartia cerastiifolia',u'Minuartia hybrida',u'Minuartia hybrida subsp. hybrida',u'Minuartia hybrida subsp. laxa',u'Minuartia hybrida subsp. tenuifolia',u'Minuartia lanuginosa',u'Minuartia laricifolia subsp. diomedis',u'Minuartia rupestris',u'Minuartia rupestris subsp. clementei',u'Minuartia rupestris subsp. rupestris',u'Minuartia stricta',u'Minuartia viscosa',u'Moehringia intermedia',u'Moehringia lebrunii',u'Moehringia sedoides',u'Moehringia sedoides var. sedoides',u'Moenchia erecta',u'Moenchia erecta var. erecta',u'Moenchia erecta var. octandra',u'Molineriella minuta',u'Molineriella minuta subsp. minuta',u'Molopospermum peloponnesiacum',u'Molopospermum peloponnesiacum subsp. peloponnesiacum',u'Moneses uniflora',u'Montia fontana',u'Moraea sisyrinchium',u'Morisia monanthos',u'Muscari botryoides',u'Muscari botryoides subsp. botryoides',u'Muscari botryoides subsp. lelievrei',u'Muscari motelayi',u'Mutellina adonidifolia var. mutellina',u'Myosotis alpestris',u'Myosotis balbisiana',u'Myosotis corsicana',u'Myosotis corsicana subsp. corsicana',u'Myosotis corsicana subsp. pyrenaeorum',u'Myosotis minutiflora',u'Myosotis pusilla',u'Myosotis ramosissima subsp. lebelii',u'Myosotis sicula',u'Myosotis soleirolii',u'Myosotis speluncicola',u'Myosotis stricta',u'Myosotis sylvatica',u'Myosurus minimus',u'Myrica gale',u'Myriolimon diffusum',u'Myriophyllum alterniflorum',u'Myriophyllum verticillatum',u'Najas marina',u'Najas marina subsp. armata',u'Najas marina subsp. intermedia',u'Najas marina subsp. marina',u'Najas minor',u'Nananthea perpusilla',u'Narcissus assoanus',u'Narcissus bulbocodium',u'Narcissus jonquilla',u'Narcissus poeticus',u'Narcissus poeticus subsp. poeticus',u'Narcissus poeticus subsp. radiiflorus',u'Narcissus poeticus subsp. verbanensis',u'Narcissus pseudonarcissus',u'Narcissus pseudonarcissus subsp. major',u'Narcissus pseudonarcissus subsp. pallidiflorus',u'Narcissus pseudonarcissus subsp. provincialis',u'Narcissus pseudonarcissus subsp. pseudonarcissus',u'Narcissus tazetta',u'Narcissus tazetta subsp. aureus',u'Narcissus tazetta subsp. italicus',u'Narcissus tazetta subsp. tazetta',u'Narcissus triandrus var. loiseleurii',u'Nardus stricta',u'Narthecium ossifragum',u'Naufraga balearica',u'Neatostema apulum',u'Nectaroscilla hyacinthoides',u'Neoschischkinia elegans',u'Neoschischkinia pourretii',u'Neoschischkinia truncatula subsp. durieui',u'Neotinea lactea',u'Neotinea maculata',u'Neotinea tridentata',u'Neotinea ustulata',u'Neotinea ustulata var. aestivalis',u'Neotinea ustulata var. ustulata',u'Neottia cordata',u'Neottia nidus-avis',u'Nerium oleander',u'Nigella arvensis',u'Nigella arvensis subsp. arvensis',u'Nigella hispanica var. hispanica',u'Nigella nigellastrum',u'Noccaea caerulescens',u'Noccaea caerulescens subsp. arenaria',u'Noccaea caerulescens subsp. caerulescens',u'Noccaea caerulescens subsp. firmiensis',u'Noccaea caerulescens subsp. occitanica',u'Noccaea caerulescens subsp. tallonis',u'Noccaea caerulescens subsp. virens',u'Noccaea montana',u'Noccaea montana subsp. montana',u'Noccaea montana subsp. villarsiana',u'Noccaea praecox',u'Nonea erecta',u'Nothobartsia spicata',u'Notobasis syriaca',u'Nuphar lutea',u'Nuphar pumila',u'Nuphar x spenneriana',u'Nymphaea alba',u'Nymphaea alba f. alba',u'Nymphaea alba subsp. alba',u'Nymphaea alba subsp. occidentalis',u'Nymphoides peltata',u'Odontites jaubertianus',u'Odontites jaubertianus var. chrysanthus',u'Odontites jaubertianus var. jaubertianus',u'Odontites luteus',u'Odontites luteus subsp. lanceolatus',u'Odontites luteus subsp. luteus',u'Odontites luteus subsp. provincialis',u'Oenanthe aquatica',u'Oenanthe crocata',u'Oenanthe crocata var. crocata',u'Oenanthe crocata var. longissima',u'Oenanthe fistulosa',u'Oenanthe fluviatilis',u'Oenanthe foucaudii',u'Oenanthe lachenalii',u'Oenanthe peucedanifolia',u'Oenanthe pimpinelloides',u'Oenanthe pimpinelloides var. chaerophylloides',u'Oenanthe pimpinelloides var. pimpinelloides',u'Oenanthe silaifolia',u'Omphalodes linifolia',u'Omphalodes littoralis',u'Omphalodes littoralis subsp. littoralis',u'Oncidium altissimum',u'Onobrychis aequidentata',u'Onobrychis arenaria',u'Onobrychis arenaria subsp. arenaria',u'Ononis alopecuroides',u'Ononis aragonensis',u'Ononis mitissima',u'Ononis pubescens',u'Ononis pusilla',u'Ononis pusilla subsp. pusilla',u'Ononis reclinata',u'Ononis striata',u'Onopordum acaulon',u'Onopordum acaulon subsp. acaulon',u'Onosma arenaria',u'Onosma arenaria subsp. pyramidata',u'Onosma pseudoarenaria subsp. delphinensis',u'Onosma tricerosperma subsp. atlantica',u'Ophrys aegirtica',u'Ophrys annae',u'Ophrys annae x Ophrys conradiae',u'Ophrys apifera',u'Ophrys apifera subsp. purpurea',u'Ophrys apifera var. almaracensis',u'Ophrys apifera var. apifera',u'Ophrys apifera var. aurita',u'Ophrys apifera var. basiliensis',u'Ophrys apifera var. belgarum',u'Ophrys apifera var. bicolor',u'Ophrys apifera var. botteronii',u'Ophrys apifera var. brevilabellata',u'Ophrys apifera var. chlorantha',u'Ophrys apifera var. curviflora',u'Ophrys apifera var. flavescens',u'Ophrys apifera var. friburgensis',u'Ophrys apifera var. fulvofusca',u'Ophrys apifera var. immaculata',u'Ophrys apifera var. saraepontana',u'Ophrys apifera var. trollii',u'Ophrys apifera x Ophrys bertolonii',u'Ophrys apifera x Ophrys conradiae',u'Ophrys apifera x Ophrys provincialis',u'Ophrys apifera x Ophrys saratoi',u'Ophrys arachnitiformis',u'Ophrys arachnitiformis x Ophrys bertolonii',u'Ophrys arachnitiformis x Ophrys exaltata',u'Ophrys arachnitiformis x Ophrys fusca',u'Ophrys arachnitiformis x Ophrys incubacea',u'Ophrys arachnitiformis x Ophrys provincialis',u'Ophrys arachnitiformis x Ophrys scolopax',u'Ophrys aranifera',u'Ophrys aranifera subsp. aranifera',u'Ophrys aranifera subsp. massiliensis',u'Ophrys aranifera subsp. praecox',u'Ophrys aranifera x Ophrys bertolonii',u'Ophrys aranifera x Ophrys catalaunica',u'Ophrys aranifera x Ophrys fusca',u'Ophrys aranifera x Ophrys tenthredinifera subsp. ficalhoana',u'Ophrys argensonensis',u'Ophrys aveyronensis',u'Ophrys aveyronensis x Ophrys exaltata',u'Ophrys aveyronensis x Ophrys tenthredinifera subsp. ficalhoana',u'Ophrys aveyronensis x Ophrys virescens',u'Ophrys aymoninii',u'Ophrys aymoninii x Ophrys passionis',u'Ophrys aymoninii x Ophrys scolopax',u'Ophrys bertolonii',u'Ophrys bertolonii subsp. bertolonii',u'Ophrys bertolonii x Ophrys passionis',u'Ophrys bertolonii x Ophrys provincialis',u'Ophrys bombyliflora',u'Ophrys bombyliflora x Ophrys eleonorae',u'Ophrys bombyliflora x Ophrys fusca',u'Ophrys bombyliflora x Ophrys scolopax',u'Ophrys bombyliflora x Ophrys virescens',u'Ophrys catalaunica',u'Ophrys catalaunica x Ophrys passionis',u'Ophrys catalaunica x Ophrys scolopax',u'Ophrys conradiae',u'Ophrys corbariensis',u'Ophrys exaltata',u'Ophrys exaltata x Ophrys fuciflora',u'Ophrys exaltata x Ophrys funerea',u'Ophrys exaltata x Ophrys passionis',u'Ophrys exaltata x Ophrys speculum',u'Ophrys fuciflora',u'Ophrys fuciflora subsp. elatior',u'Ophrys fuciflora subsp. elatior x Ophrys fuciflora',u'Ophrys fuciflora subsp. fuciflora',u'Ophrys fuciflora subsp. montiliensis',u'Ophrys fuciflora subsp. souchei',u'Ophrys fuciflora x Ophrys incubacea',u'Ophrys fuciflora x Ophrys passionis',u'Ophrys fuciflora x Ophrys scolopax',u'Ophrys fuciflora x Ophrys virescens',u'Ophrys funerea',u'Ophrys funerea x Ophrys fusca',u'Ophrys funerea x Ophrys scolopax',u'Ophrys fusca',u'Ophrys fusca x Ophrys aranifera subsp. praecox',u'Ophrys fusca x Ophrys passionis',u'Ophrys fusca x Ophrys virescens',u'Ophrys incubacea',u'Ophrys incubacea x Ophrys aranifera subsp. praecox',u'Ophrys incubacea x Ophrys provincialis',u'Ophrys incubacea x Ophrys saratoi',u'Ophrys insectifera',u'Ophrys insectifera x Ophrys subinsectifera',u'Ophrys iricolor',u'Ophrys lupercalis x Ophrys aranifera subsp. massiliensis',u'Ophrys lupercalis x Ophrys lutea',u'Ophrys lupercalis x Ophrys tenthredinifera',u'Ophrys lutea',u'Ophrys lutea subsp. corsica',u'Ophrys lutea subsp. lutea',u'Ophrys lutea x Ophrys marmorata',u'Ophrys lutea x Ophrys provincialis',u'Ophrys magniflora x Ophrys passionis',u'Ophrys marmorata',u'Ophrys montis-aviarii',u'Ophrys morisii',u'Ophrys morisii x Ophrys incubacea',u'Ophrys occidentalis x Ophrys lupercalis',u'Ophrys occidentalis x Ophrys lutea',u'Ophrys occidentalis x Ophrys scolopax',u'Ophrys occidentalis x Ophrys speculum',u'Ophrys occidentalis x Ophrys tenthredinifera',u'Ophrys passionis',u'Ophrys passionis x Ophrys speculum',u'Ophrys passionis x Ophrys vasconica',u'Ophrys philippi',u'Ophrys provincialis',u'Ophrys provincialis x Ophrys scolopax',u'Ophrys saratoi',u'Ophrys saratoi x Ophrys vetula',u'Ophrys scolopax',u'Ophrys scolopax subsp. apiformis',u'Ophrys scolopax subsp. scolopax',u'Ophrys scolopax x Ophrys tenthredinifera subsp. ficalhoana',u'Ophrys speculum',u'Ophrys speculum x Ophrys aranifera subsp. praecox',u'Ophrys speculum x Ophrys provincialis',u'Ophrys subinsectifera',u'Ophrys tenthredinifera',u'Ophrys tenthredinifera subsp. aprilia',u'Ophrys tenthredinifera subsp. ficalhoana',u'Ophrys tenthredinifera subsp. neglecta',u'Ophrys tenthredinifera subsp. tenthredinifera',u'Ophrys vasconica',u'Ophrys vetula',u'Ophrys virescens',u'Ophrys virescens x Ophrys provincialis',u'Ophrys virescens x Ophrys sulcata',u'Ophrys x albertiana',u'Ophrys x alejandrei',u'Ophrys x ambrosii',u'Ophrys x apicula',u'Ophrys x barauensis',u'Ophrys x barbaricina',u'Ophrys x bastianii',u'Ophrys x bergonii',u'Ophrys x bernardii',u'Ophrys x broeckii',u'Ophrys x carqueirannensis',u'Ophrys x cascalesii',u'Ophrys x castroviejoi',u'Ophrys x cataldii',u'Ophrys x celani',u'Ophrys x chiesesica',u'Ophrys x chimaera',u'Ophrys x chobautii',u'Ophrys x circaea',u'Ophrys x clapensis',u'Ophrys x colin-tocainae',u'Ophrys x corinthiaca',u'Ophrys x cortesii',u'Ophrys x corvey-bironii',u'Ophrys x cosana',u'Ophrys x costei',u'Ophrys x cranbrookiana',u'Ophrys x cugniensis',u'Ophrys x daneschianum',u'Ophrys x daunia',u'Ophrys x devenensis',u'Ophrys x domitia',u'Ophrys x domus-maria',u'Ophrys x duvigneaudiana',u'Ophrys x eliasii',u'Ophrys x enobarbia',u'Ophrys x epeirophora',u'Ophrys x estacensis',u'Ophrys x etrusca',u'Ophrys x ezcaraiensis',u'Ophrys x fabrei',u'Ophrys x fayencensis',u'Ophrys x fernandii',u'Ophrys x ferruginea',u'Ophrys x flahaultii',u'Ophrys x fonsaudiensis',u'Ophrys x gauthieri',u'Ophrys x glanensis',u'Ophrys x godferyana',u'Ophrys x grampinii',u'Ophrys x grinincensis',u'Ophrys x heraultii',u'Ophrys x hermosillae',u'Ophrys x hoeppneri',u'Ophrys x hybrida',u'Ophrys x insidiosa',u'Ophrys x inzengae',u'Ophrys x jacquetii',u'Ophrys x jarigei',u'Ophrys x jeanpertii',u'Ophrys x jegouae',u'Ophrys x kelleri',u'Ophrys x kohlmuellerorum',u'Ophrys x laconensis',u'Ophrys x lebeaultii',u'Ophrys x leguerrierae',u'Ophrys x lievrae',u'Ophrys x llenasii',u'Ophrys x lorenzii',u'Ophrys x luizetii',u'Ophrys x lumenii',u'Ophrys x lyrata',u'Ophrys x macchiatii',u'Ophrys x maelleae',u'Ophrys x maladroxiensis',u'Ophrys x maremmae',u'Ophrys x maurensis',u'Ophrys x minuticauda',u'Ophrys x mirandana',u'Ophrys x monachorum',u'Ophrys x nelsonii',u'Ophrys x neocamusii',u'Ophrys x neorupperti',u'Ophrys x neowalteri',u'Ophrys x nouletii',u'Ophrys x obscura',u'Ophrys x olbiensis',u'Ophrys x panattensis',u'Ophrys x pantaliciensis',u'Ophrys x peltieri',u'Ophrys x perrinii',u'Ophrys x personii',u'Ophrys x personii nothosubsp. bourlieri',u'Ophrys x personii nothosubsp. personii',u'Ophrys x pietzschii',u'Ophrys x piscinica',u'Ophrys x pourteiniae',u'Ophrys x proxima',u'Ophrys x pseudapifera',u'Ophrys x pseudofusca',u'Ophrys x pseudospeculum',u'Ophrys x quadriloba',u'Ophrys x ragusana',u'Ophrys x raimbaultii',u'Ophrys x rainii',u'Ophrys x royanensis',u'Ophrys x samuelii',u'Ophrys x sanconoensis',u'Ophrys x sanctae-sofiae',u'Ophrys x sancticyrensis',u'Ophrys x semibombyliflora',u'Ophrys x socae',u'Ophrys x sommieri',u'Ophrys x souliei',u'Ophrys x spanui',u'Ophrys x spuria',u'Ophrys x subfusca',u'Ophrys x subfusca nothosubsp. fenarolii',u'Ophrys x subfusca nothosubsp. subfusca',u'Ophrys x surdi',u'Ophrys x tavignanensis',u'Ophrys x todaroana',u'Ophrys x turiana',u'Ophrys x tytecaeana',u'Ophrys x vicina',u'Orchis anthropophora',u'Orchis langei',u'Orchis mascula',u'Orchis mascula subsp. mascula',u'Orchis mascula subsp. speciosa',u'Orchis militaris',u'Orchis pallens',u'Orchis pauciflora',u'Orchis provincialis',u'Orchis purpurea',u'Orchis simia',u'Orchis spitzelii',u'Oreoselinum nigrum',u'Orlaya grandiflora',u'Ornithogalum exscapum subsp. sandalioticum',u'Ornithopus compressus',u'Ornithopus pinnatus',u'Ornithopus sativus subsp. sativus',u'Orobanche alba',u'Orobanche alsatica',u'Orobanche artemisii-campestris',u'Orobanche elatior',u'Orobanche laserpitii-sileris',u'Orobanche teucrii',u'Orthilia secunda',u'Osyris alba',u'Oxybasis chenopodioides',u'Oxytropis fetida',u'Oxytropis fetida subsp. fetida',u'Oxytropis fetida subsp. viscosa',u'Paeonia mascula',u'Paeonia mascula subsp. mascula',u'Paeonia officinalis',u'Paeonia officinalis subsp. huthii',u'Paeonia officinalis subsp. microcarpa',u'Paeonia officinalis subsp. officinalis',u'Pallenis maritima',u'Pallenis spinosa',u'Pallenis spinosa subsp. spinosa',u'Pancratium maritimum',u'Papaver alpinum subsp. alpinum',u'Papaver alpinum subsp. suaveolens',u'Papaver cambricum',u'Papaver dubium',u'Papaver dubium subsp. dubium',u'Papaver dubium subsp. lecoqii',u'Papaver pinnatifidum',u'Papaver rhaeticum',u'Paradisea liliastrum',u'Parentucellia latifolia',u'Paris quadrifolia',u'Parnassia palustris',u'Patzkea paniculata subsp. spadicea',u'Pedicularis ascendens',u'Pedicularis foliosa',u'Pedicularis palustris',u'Pedicularis palustris subsp. palustris',u'Pedicularis recutita',u'Pedicularis rosea',u'Pedicularis rosea subsp. allionii',u'Pedicularis sylvatica',u'Pedicularis sylvatica subsp. sylvatica',u'Pedicularis verticillata',u'Pentaglottis sempervirens',u'Persicaria decipiens',u'Persicaria mitis',u'Petasites albus',u'Petrocoptis pyrenaica',u'Petrocoptis pyrenaica subsp. pyrenaica',u'Peucedanum gallicum',u'Peucedanum officinale',u'Peucedanum officinale subsp. officinale',u'Peucedanum officinale var. catalaunicum',u'Peucedanum officinale var. officinale',u'Phagnalon rupestre subsp. annoticum',u'Phalaris aquatica',u'Phalaris paradoxa',u'Phelipanche arenaria',u'Phelipanche purpurea',u'Phelipanche purpurea subsp. millefolii',u'Phelipanche purpurea subsp. purpurea',u'Phillyrea angustifolia',u'Phillyrea latifolia',u'Phleum phleoides',u'Phleum phleoides var. blepharodes',u'Phleum phleoides var. phleoides',u'Phyllodoce caerulea',u'Physospermum cornubiense',u'Phyteuma charmelii',u'Phyteuma cordatum',u'Phyteuma gallicum',u'Phyteuma globulariifolium subsp. rupicola',u'Phyteuma nigrum',u'Phyteuma orbiculare',u'Phyteuma orbiculare subsp. orbiculare',u'Phyteuma orbiculare subsp. tenerum',u'Phyteuma villarsii',u'Picrasma excelsa',u'Picris rhagadioloides',u'Pilosella aurantiaca',u'Pilosella aurantiaca subsp. aurantiaca',u'Pilosella cymosa',u'Pilosella cymosa subsp. sabina',u'Pilosella cymosa subsp. vaillantii',u'Pilosella peleteriana',u'Pilosella peleteriana subsp. ligerica',u'Pilosella peleteriana subsp. peleteriana',u'Pilosella peleteriana subsp. subpeleteriana',u'Pilosella peleteriana subsp. tenuiscapa',u'Pimpinella lutea',u'Pimpinella siifolia',u'Pinguicula arvetii',u'Pinguicula grandiflora',u'Pinguicula grandiflora subsp. grandiflora',u'Pinguicula grandiflora subsp. rosea',u'Pinguicula grandiflora var. grandiflora',u'Pinguicula grandiflora var. pallida',u'Pinguicula longifolia subsp. caussensis',u'Pinguicula longifolia subsp. longifolia',u'Pinguicula lusitanica',u'Pinguicula reichenbachiana',u'Pinguicula vulgaris',u'Pinguicula vulgaris f. alpicola',u'Pinguicula vulgaris f. bicolor',u'Pinguicula vulgaris f. vulgaris',u'Pinguicula vulgaris var. alpicola',u'Pinguicula vulgaris var. vulgaris',u'Piptatherum virescens',u'Pistacia terebinthus',u'Pistacia terebinthus subsp. terebinthus',u'Pisum sativum subsp. biflorum',u'Plantago cornutii',u'Plantago holosteum',u'Plantago holosteum var. holosteum',u'Plantago holosteum var. littoralis',u'Plantago maritima',u'Plantago maritima subsp. maritima',u'Plantago maritima subsp. serpentina',u'Plantago monosperma',u'Plantago monosperma subsp. monosperma',u'Plantago sempervirens',u'Plantago subulata',u'Platanthera chlorantha',u'Poa chaixii',u'Poa glauca',u'Poa glauca var. glauca',u'Poa hybrida',u'Poa palustris',u'Poa palustris var. glabra',u'Poa palustris var. palustris',u'Podospermum laciniatum',u'Podospermum laciniatum subsp. decumbens',u'Podospermum laciniatum subsp. laciniatum',u'Polemonium caeruleum',u'Polycarpon polycarpoides',u'Polycarpon polycarpoides subsp. catalaunicum',u'Polycarpon tetraphyllum',u'Polycarpon tetraphyllum subsp. alsinifolium',u'Polycarpon tetraphyllum subsp. diphyllum',u'Polycarpon tetraphyllum subsp. tetraphyllum',u'Polycnemum majus',u'Polygala amarella',u'Polygala amarella var. amarella',u'Polygala antillensis',u'Polygala calcarea',u'Polygala comosa',u'Polygala exilis',u'Polygonatum verticillatum',u'Polygonum arenarium',u'Polygonum maritimum',u'Polygonum raii',u'Polygonum romanum',u'Polygonum romanum subsp. gallicum',u'Polypogon monspeliensis',u'Polypogon subspathaceus',u'Posidonia oceanica',u'Potamogeton acutifolius',u'Potamogeton alpinus',u'Potamogeton coloratus',u'Potamogeton compressus',u'Potamogeton friesii',u'Potamogeton gramineus',u'Potamogeton nodosus',u'Potamogeton obtusifolius',u'Potamogeton perfoliatus',u'Potamogeton polygonifolius',u'Potamogeton praelongus',u'Potamogeton rutilus',u'Potamogeton trichoides',u'Potamogeton x nitens',u'Potamogeton x zizii',u'Potentilla alba',u'Potentilla anglica',u'Potentilla anglica subsp. anglica',u'Potentilla anglica subsp. nesogenes',u'Potentilla caulescens',u'Potentilla caulescens subsp. caulescens',u'Potentilla caulescens subsp. cebennensis',u'Potentilla caulescens subsp. iserensis',u'Potentilla caulescens subsp. petiolulata',u'Potentilla crantzii',u'Potentilla delphinensis',u'Potentilla montana',u'Potentilla multifida',u'Potentilla neglecta',u'Potentilla nivea',u'Potentilla puberula',u'Potentilla saxifraga',u'Potentilla supina',u'Potentilla supina subsp. supina',u'Potentilla verna',u'Prangos trifida',u'Prenanthes purpurea',u'Primula allionii',u'Primula halleri',u'Primula lutea',u'Primula lutea subsp. lutea',u'Primula marginata',u'Primula matthioli',u'Primula pedemontana',u'Primula vulgaris',u'Primula vulgaris subsp. vulgaris',u'Prockia crucis',u'Prospero autumnale',u'Prunella grandiflora',u'Prunus lusitanica',u'Prunus lusitanica subsp. lusitanica',u'Prunus mahaleb',u'Prunus padus',u'Prunus padus var. padus',u'Prunus padus var. petraea',u'Prunus pleuradenia',u'Pseudorchis albida',u'Pseudorchis albida subsp. albida',u'Pseudorchis albida subsp. tricuspis',u'Pseudorlaya pumila',u'Pseudorlaya pumila var. breviaculeata',u'Pseudorlaya pumila var. microcarpa',u'Pseudorlaya pumila var. pumila',u'Pseudosclerochloa rupestris',u'Pseudoturritis turrita',u'Ptilostemon casabonae',u'Puccinellia fasciculata',u'Puccinellia fasciculata subsp. fasciculata',u'Pulicaria sicula',u'Pulicaria vulgaris',u'Pulmonaria angustifolia',u'Pyrola chlorantha',u'Pyrola media',u'Pyrola minor',u'Pyrola rotundifolia var. arenaria',u'Quercus crenata',u'Quercus pyrenaica',u'Radiola linoides',u'Ranunculus auricomus',u'Ranunculus canutii',u'Ranunculus gramineus',u'Ranunculus gramineus var. gramineus',u'Ranunculus hederaceus',u'Ranunculus lateriflorus',u'Ranunculus lingua',u'Ranunculus macrophyllus',u'Ranunculus millefoliatus',u'Ranunculus nodiflorus',u'Ranunculus ololeucos',u'Ranunculus omiophyllus',u'Ranunculus ophioglossifolius',u'Ranunculus paludosus',u'Ranunculus parnassifolius',u'Ranunculus parnassifolius subsp. favargeri',u'Ranunculus parnassifolius subsp. heterocarpus',u'Ranunculus parnassifolius subsp. parnassifolius',u'Ranunculus parviflorus',u'Ranunculus parviflorus subsp. parviflorus',u'Ranunculus peltatus',u'Ranunculus peltatus subsp. baudotii',u'Ranunculus peltatus subsp. fucoides',u'Ranunculus peltatus subsp. peltatus',u'Ranunculus penicillatus',u'Ranunculus penicillatus subsp. penicillatus',u'Ranunculus penicillatus subsp. pseudofluitans',u'Ranunculus penicillatus var. calcareus',u'Ranunculus penicillatus var. penicillatus',u'Ranunculus penicillatus var. vertumnus',u'Ranunculus platanifolius',u'Ranunculus polyanthemoides',u'Ranunculus revelierei',u'Ranunculus rionii',u'Ranunculus sceleratus',u'Ranunculus sceleratus subsp. sceleratus',u'Ranunculus trilobus',u'Ranunculus tripartitus',u'Ranunculus velutinus',u'Reseda jacquinii',u'Rhamnus alpina',u'Rhamnus alpina subsp. alpina',u'Rhamnus pumila',u'Rhamnus saxatilis f. saxatilis',u'Rhamnus saxatilis subsp. saxatilis',u'Rhaponticoides alpina',u'Rhaponticum centauroides',u'Rhaponticum coniferum',u'Rhaponticum coniferum subsp. coniferum',u'Rhaponticum scariosum subsp. scariosum',u'Rhodiola rosea',u'Rhododendron hirsutum',u'Rhus coriaria',u'Rhynchospora alba',u'Rhynchospora fusca',u'Ribes rubrum',u'Rochefortia spinosa',u'Romulea bulbocodium',u'Romulea columnae',u'Romulea columnae subsp. columnae',u'Romulea columnae subsp. coronata',u'Romulea columnae subsp. subalbida',u'Romulea ligustica',u'Romulea requienii',u'Romulea revelieri',u'Rorippa amphibia',u'Rosa gallica',u'Rosa jundzillii',u'Rosa spinosissima',u'Rosa spinosissima subsp. myriacantha',u'Rosa spinosissima subsp. spinosissima',u'Rosa stylosa',u'Rosa tomentosa',u'Rosa villosa',u'Rouya polygama',u'Rubia peregrina',u'Rubia peregrina subsp. longifolia',u'Rubia peregrina subsp. peregrina',u'Rubia peregrina subsp. requienii',u'Rubus polyoplon',u'Rubus saxatilis',u'Rumex aquitanicus',u'Rumex maritimus',u'Rumex palustris',u'Rumex rupestris',u'Rumex scutatus',u'Rumex scutatus subsp. scutatus',u'Rumex scutatus var. glaucus',u'Rumex scutatus var. insularis',u'Rumex scutatus var. scutatus',u'Rumex tuberosus',u'Ruppia maritima',u'Ruppia maritima var. brevirostris',u'Ruppia maritima var. maritima',u'Ruscus aculeatus',u'Ruta graveolens',u'Sagina nodosa',u'Sagina subulata',u'Sagina subulata subsp. revelierei',u'Sagina subulata subsp. subulata',u'Sagina subulata var. gracilis',u'Sagina subulata var. subulata',u'Sagittaria sagittifolia',u'Salicornia europaea',u'Salicornia europaea subsp. disarticulata',u'Salicornia europaea subsp. europaea',u'Salicornia europaea subsp. x marshallii',u'Salicornia procumbens',u'Salicornia procumbens subsp. procumbens',u'Salix bicolor',u'Salix breviserrata',u'Salix daphnoides',u'Salix glaucosericea',u'Salix helvetica',u'Salix herbacea',u'Salix laggeri',u'Salix lapponum',u'Salix pentandra',u'Salix repens',u'Salix repens subsp. repens',u'Salix repens var. dunensis',u'Salix repens var. fusca',u'Salix repens var. repens',u'Salvia aethiopis',u'Salvia glutinosa',u'Salvia officinalis subsp. gallica',u'Samolus valerandi',u'Sanguisorba officinalis',u'Saponaria bellidifolia',u'Saponaria caespitosa',u'Saponaria lutea',u'Sarcocapnos enneaphylla',u'Saussurea alpina',u'Saussurea alpina subsp. alpina',u'Saussurea discolor',u'Saxifraga androsacea',u'Saxifraga biflora',u'Saxifraga bryoides',u'Saxifraga cebennensis',u'Saxifraga cochlearis',u'Saxifraga cotyledon',u'Saxifraga cuneata',u'Saxifraga delphinensis',u'Saxifraga diapensioides',u'Saxifraga florulenta',u'Saxifraga fragosoi',u'Saxifraga granulata',u'Saxifraga granulata f. granulata',u'Saxifraga granulata var. glaucescens',u'Saxifraga granulata var. granulata',u'Saxifraga hirculus',u'Saxifraga iratiana',u'Saxifraga lamottei',u'Saxifraga media',u'Saxifraga muscoides',u'Saxifraga mutata',u'Saxifraga mutata subsp. mutata',u'Saxifraga oppositifolia',u'Saxifraga oppositifolia subsp. oppositifolia',u'Saxifraga paniculata',u'Saxifraga prostii',u'Saxifraga pubescens',u'Saxifraga rosacea',u'Saxifraga rosacea subsp. rosacea',u'Saxifraga rosacea subsp. sponhemica',u'Saxifraga seguieri',u'Saxifraga valdensis',u'Scabiosa atropurpurea',u'Scabiosa atropurpurea var. atropurpurea',u'Scabiosa atropurpurea var. maritima',u'Scabiosa canescens',u'Scabiosa columbaria',u'Scabiosa lucida',u'Scabiosa lucida subsp. lucida',u'Scandix stellata',u'Schenkia spicata',u'Scheuchzeria palustris',u'Schoenoplectus mucronatus',u'Schoenoplectus pungens',u'Schoenoplectus supinus',u'Schoenoplectus tabernaemontani',u'Schoenoplectus triqueter',u'Schoenus ferrugineus',u'Schoenus nigricans',u'Scilla bifolia',u'Scirpus sylvaticus',u'Scleranthus perennis',u'Scleranthus perennis subsp. perennis',u'Scleranthus perennis subsp. polycnemoides',u'Sclerochloa dura',u'Scolymus hispanicus',u'Scolymus hispanicus subsp. hispanicus',u'Scolymus hispanicus subsp. occidentalis',u'Scorpiurus muricatus',u'Scorzonera austriaca',u'Scorzonera austriaca subsp. austriaca',u'Scorzonera austriaca subsp. bupleurifolia',u'Scorzonera hirsuta',u'Scorzonera hispanica',u'Scorzonera hispanica subsp. asphodeloides',u'Scorzonera hispanica subsp. crispatula',u'Scorzonera humilis',u'Scorzonera parviflora',u'Scrophularia canina subsp. hoppii',u'Scrophularia canina subsp. ramosissima',u'Scrophularia pyrenaica',u'Scrophularia scorodonia',u'Scrophularia vernalis',u'Scutellaria columnae subsp. columnae',u'Scutellaria hastifolia',u'Scutellaria minor',u'Sedum alpestre',u'Sedum amplexicaule',u'Sedum amplexicaule subsp. amplexicaule',u'Sedum andegavense',u'Sedum caespitosum',u'Sedum cepaea',u'Sedum dasyphyllum',u'Sedum dasyphyllum var. dasyphyllum',u'Sedum dasyphyllum var. glanduliferum',u'Sedum fragrans',u'Sedum hirsutum',u'Sedum hirsutum subsp. hirsutum',u'Sedum litoreum',u'Sedum monregalense',u'Sedum multiceps',u'Sedum ochroleucum',u'Sedum rubens',u'Sedum sediforme',u'Sedum sexangulare',u'Sedum villosum',u'Sedum villosum subsp. glandulosum',u'Sedum villosum subsp. villosum',u'Selinum carvifolia',u'Sempervivum arachnoideum',u'Sempervivum arachnoideum var. arachnoideum',u'Sempervivum arachnoideum var. tomentosum',u'Sempervivum fauconnetii',u'Sempervivum globiferum subsp. allionii',u'Sempervivum tectorum subsp. arvernense',u'Senecio bayonnensis',u'Senecio cacaliaster',u'Senecio doria',u'Senecio doria subsp. doria',u'Senecio leucanthemifolius',u'Senecio leucanthemifolius subsp. crassifolius',u'Senecio lividus',u'Senecio rosinae',u'Senecio ruthenensis',u'Senecio sarracenicus',u'Serapias cordigera',u'Serapias lingua',u'Serapias neglecta',u'Serapias nurrica',u'Serapias olbia',u'Serapias parviflora',u'Serapias vomeracea var. vomeracea',u'Serratula tinctoria subsp. seoanei',u'Sesamoides purpurascens',u'Sesamoides pygmaea',u'Seseli annuum',u'Seseli annuum subsp. annuum',u'Seseli annuum subsp. carvifolium',u'Seseli djianeae',u'Seseli montanum',u'Seseli montanum subsp. montanum',u'Seseli montanum subsp. nanum',u'Seseli praecox',u'Sesleria caerulea',u'Sesleria caerulea subsp. caerulea',u'Sesleria ovata',u'Sibbaldia procumbens',u'Sibthorpia europaea',u'Sideritis hyssopifolia subsp. guillonii',u'Sideroxylon foetidissimum',u'Silaum silaus',u'Silaum silaus var. angustifolium',u'Silaum silaus var. latissimum',u'Silaum silaus var. silaus',u'Silene baccifera',u'Silene badaroi',u'Silene ciliata',u'Silene conica',u'Silene muscipula',u'Silene nutans var. brachypoda',u'Silene otites',u'Silene portensis',u'Silene sedoides',u'Silene sedoides subsp. sedoides',u'Silene uniflora subsp. thorei',u'Silene uniflora subsp. uniflora',u'Silene uniflora var. montana',u'Silene uniflora var. uniflora',u'Silene velutina',u'Silene viridiflora',u'Silene vulgaris subsp. glareosa',u'Simethis mattiazzii',u'Sinapis pubescens',u'Sinapis pubescens subsp. pubescens',u'Sison amomum',u'Sisymbrella aspera',u'Sisymbrella aspera subsp. aspera',u'Sisymbrella aspera subsp. boissieri',u'Sisymbrella aspera subsp. praeterita',u'Sisymbrium austriacum',u'Sisymbrium austriacum subsp. austriacum',u'Sisymbrium austriacum subsp. chrysanthum',u'Sisymbrium austriacum subsp. contortum',u'Sisymbrium austriacum subsp. erysimifolium',u'Sisymbrium austriacum subsp. villarsii',u'Sium latifolium',u'Sloanea dussii',u'Smilax aspera',u'Smilax aspera var. aspera',u'Smyrnium perfoliatum subsp. rotundifolium',u'Soldanella alpina',u'Soldanella alpina subsp. alpina',u'Soldanella villosa',u'Solenopsis laurentia',u'Solidago virgaurea subsp. macrorhiza',u'Sonchus bulbosus',u'Sonchus bulbosus subsp. bulbosus',u'Sonchus palustris',u'Sophora tomentosa',u'Sorbus aria',u'Sorbus aria subsp. aria',u'Sorbus latifolia',u'Sparganium angustifolium',u'Sparganium emersum',u'Sparganium emersum subsp. emersum',u'Sparganium natans',u'Spartina maritima',u'Spergula heldreichii',u'Spergula macrorrhiza',u'Spergula media',u'Spergula morisonii',u'Spergula pentandra',u'Spergula segetalis',u'Spiraea hypericifolia subsp. obovata',u'Spiranthes aestivalis',u'Spiranthes spiralis',u'Spirodela polyrhiza',u'Stachys alpina',u'Stachys brachyclada',u'Stachys germanica',u'Stachys germanica subsp. albereana',u'Stachys germanica subsp. germanica',u'Stachys germanica subsp. salviifolia',u'Stachys heraclea',u'Stachys maritima',u'Stachys marrubiifolia',u'Stachys ocymastrum',u'Stachys palustris',u'Stachys recta',u'Stachys recta subsp. recta',u'Stachys recta var. recta',u'Staehelina dubia',u'Staphisagria macrosperma',u'Staphisagria picta subsp. requienii',u'Staphylea pinnata',u'Stellaria nemorum',u'Stellaria nemorum subsp. kersii',u'Stellaria nemorum subsp. montana',u'Stellaria nemorum subsp. nemorum',u'Stellaria palustris',u'Sternbergia colchiciflora',u'Stipa pennata',u'Stipa pennata subsp. pennata',u'Stipellula capensis',u'Stipellula parviflora',u'Stratiotes aloides',u'Streptopus amplexifolius',u'Stuckenia filiformis',u'Stuckenia helvetica',u'Suaeda vera',u'Suaeda vera subsp. vera',u'Subularia aquatica',u'Succowia balearica',u'Swertia perennis',u'Syagrus amara',u'Symphytum bulbosum',u'Tamarix africana',u'Tanacetum audibertii',u'Tanacetum corymbosum',u'Tanacetum corymbosum var. corymbosum',u'Tanacetum corymbosum var. subcorymbosum',u'Tanacetum corymbosum var. tenuifolium',u'Tanaecium crucigerum',u'Taraxacum bessarabicum',u'Taraxacum palustre',u'Teesdalia coronopifolia',u'Teesdalia nudicaulis',u'Telephium imperati',u'Telephium imperati subsp. imperati',u'Tephroseris balbisiana',u'Tephroseris helenitis',u'Tephroseris helenitis subsp. candida',u'Tephroseris helenitis subsp. helenitis',u'Tephroseris helenitis subsp. macrochaeta',u'Tephroseris helenitis var. arvernensis',u'Tephroseris helenitis var. discoidea',u'Tephroseris helenitis var. helenitis',u'Tephroseris palustris',u'Ternstroemia elliptica',u'Ternstroemia peduncularis',u'Teucrium aristatum',u'Teucrium aristatum subsp. cravense',u'Teucrium botrys',u'Teucrium dunense',u'Teucrium fruticans',u'Teucrium fruticans subsp. fruticans',u'Teucrium massiliense',u'Teucrium montanum',u'Teucrium polium subsp. purpurascens',u'Teucrium pseudochamaepitys',u'Teucrium pyrenaicum',u'Teucrium pyrenaicum subsp. pyrenaicum',u'Teucrium scordium',u'Teucrium scordium subsp. scordioides',u'Teucrium scordium subsp. scordium',u'Thalictrum aquilegiifolium',u'Thalictrum flavum',u'Thalictrum macrocarpum',u'Thalictrum minus',u'Thalictrum minus subsp. dunense',u'Thalictrum minus subsp. pratense',u'Thalictrum minus subsp. pubescens',u'Thalictrum minus subsp. saxatile',u'Thalictrum simplex',u'Thalictrum simplex subsp. galioides',u'Thalictrum simplex subsp. simplex',u'Thalictrum simplex subsp. tenuifolium',u'Thalictrum tuberosum',u'Thalictrum x timeroyi',u'Thesium alpinum',u'Thesium alpinum var. alpinum',u'Thesium alpinum var. tenuifolium',u'Thesium humifusum',u'Thesium humifusum subsp. divaricatum',u'Thesium humifusum subsp. humifusum',u'Thesium humile',u'Thesium linophyllon',u'Thesium linophyllon subsp. linophyllon',u'Thesium linophyllon subsp. montanum',u'Thlaspi alliaceum',u'Thymelaea hirsuta',u'Thymelaea ruizii',u'Thymelaea tartonraira',u'Thymelaea tartonraira subsp. tartonraira',u'Thymelaea tartonraira subsp. thomasii',u'Thymelaea tartonraira subsp. transiens',u'Thymelaea tinctoria subsp. nivalis',u'Thymus dolomiticus',u'Thymus nitens',u'Thymus praecox',u'Thymus praecox subsp. praecox',u'Thysselinum lancifolium',u'Thysselinum palustre',u'Tofieldia pusilla',u'Tofieldia pusilla subsp. pusilla',u'Tolpis umbellata',u'Tolumnia variegata',u'Tozzia alpina',u'Tractema lilio-hyacinthus',u'Trapa natans',u'Traunsteinera globosa',u'Trichophorum alpinum',u'Trichophorum cespitosum',u'Trichophorum cespitosum nothosubsp. foersteri',u'Trichophorum cespitosum subsp. cespitosum',u'Trichophorum cespitosum subsp. germanicum',u'Trichophorum pumilum',u'Trifolium bocconei',u'Trifolium bocconei var. bocconei',u'Trifolium cernuum',u'Trifolium glomeratum',u'Trifolium hirtum',u'Trifolium lappaceum',u'Trifolium leucanthum',u'Trifolium ligusticum',u'Trifolium medium',u'Trifolium medium subsp. medium',u'Trifolium michelianum',u'Trifolium montanum',u'Trifolium montanum subsp. gayanum',u'Trifolium montanum subsp. montanum',u'Trifolium montanum subsp. rupestre',u'Trifolium ornithopodioides',u'Trifolium pallescens',u'Trifolium pannonicum',u'Trifolium retusum',u'Trifolium rubens',u'Trifolium saxatile',u'Trifolium scabrum',u'Trifolium scabrum subsp. lucanicum',u'Trifolium scabrum subsp. scabrum',u'Trifolium spadiceum',u'Trifolium spumosum',u'Trifolium squamosum',u'Trifolium squamosum var. squamosum',u'Trifolium squamosum var. xatardii',u'Trifolium squarrosum',u'Trifolium stellatum',u'Trifolium stellatum var. longiflorum',u'Trifolium stellatum var. stellatum',u'Trifolium striatum',u'Trifolium strictum',u'Trifolium subterraneum',u'Trifolium subterraneum subsp. subterraneum',u'Trifolium subterraneum var. flagelliforme',u'Trifolium subterraneum var. subterraneum',u'Triglochin barrelieri',u'Triglochin laxiflora',u'Triglochin maritima',u'Triglochin palustris',u'Trigonella gladiata',u'Trinia glauca',u'Trinia glauca subsp. glauca',u'Trinia glauca var. elatior',u'Trinia glauca var. glauca',u'Tripolium pannonicum',u'Tripolium pannonicum f. discoideus',u'Tripolium pannonicum subsp. pannonicum',u'Tripolium pannonicum subsp. tripolium',u'Tripolium pannonicum subvar. tripolium',u'Trisetum gracile',u'Trisetum spicatum subsp. ovatipaniculatum',u'Trocdaris verticillatum',u'Trochiscanthes nodiflora',u'Tuberaria guttata',u'Tulipa agenensis',u'Tulipa clusiana',u'Tulipa gesneriana',u'Tulipa raddii',u'Tulipa sylvestris subsp. sylvestris',u'Turpinia occidentalis',u'Turritis glabra',u'Typha laxmannii',u'Typha minima',u'Typha shuttleworthii',u'Ulex gallii',u'Ulex minor',u'Ulmus laevis',u'Urginea fugax',u'Urtica membranacea',u'Urtica pilulifera',u'Utricularia australis',u'Utricularia bremii',u'Utricularia intermedia',u'Utricularia minor',u'Utricularia ochroleuca',u'Utricularia vulgaris',u'Vaccinium microcarpum',u'Vaccinium myrtillus',u'Vaccinium oxycoccos',u'Vaccinium uliginosum',u'Vaccinium uliginosum subsp. microphyllum',u'Vaccinium uliginosum subsp. uliginosum',u'Vaccinium vitis-idaea',u'Vaccinium vitis-idaea subsp. minus',u'Vaccinium vitis-idaea subsp. vitis-idaea',u'Valantia hispida',u'Valeriana celtica',u'Valeriana celtica subsp. celtica',u'Valeriana dioica',u'Valeriana dioica subsp. dioica',u'Valeriana officinalis subsp. hispidula',u'Valeriana officinalis subsp. officinalis',u'Valeriana officinalis subsp. tenuifolia',u'Valeriana saliunca',u'Valeriana tripteris',u'Valeriana tuberosa',u'Valerianella eriocarpa',u'Valerianella eriocarpa f. eriocarpa',u'Vallisneria spiralis',u'Vanilla pleei',u'Ventenata dubia',u'Veratrum album',u'Veratrum album subsp. album',u'Veratrum album subsp. lobelianum',u'Veratrum nigrum',u'Verbascum conocarpum subsp. conocarpum',u'Verbena supina',u'Veronica dillenii',u'Veronica longifolia',u'Veronica prostrata',u'Veronica scutellata',u'Veronica scutellata var. pilosa',u'Veronica scutellata var. scutellata',u'Veronica spicata',u'Veronica spicata subsp. spicata',u'Veronica teucrium',u'Vicia altissima',u'Vicia argentea',u'Vicia cassubica',u'Vicia cusnae',u'Vicia dumetorum',u'Vicia laeta',u'Vicia melanops',u'Vicia melanops var. loiseaui',u'Vicia melanops var. melanops',u'Vicia narbonensis',u'Vicia pisiformis',u'Vicia pyrenaica',u'Vincetoxicum hirundinaria',u'Vincetoxicum hirundinaria subsp. contiguum',u'Vincetoxicum hirundinaria subsp. hirundinaria',u'Vincetoxicum hirundinaria subsp. intermedium',u'Vincetoxicum hirundinaria subsp. luteolum',u'Viola alba',u'Viola alba subsp. alba',u'Viola alba subsp. dehnhardtii',u'Viola alba subsp. scotophylla',u'Viola alba var. cadevalii',u'Viola alba var. dehnhardtii',u'Viola alba var. lactea',u'Viola alba var. picta',u'Viola arborescens',u'Viola canina',u'Viola canina subsp. canina',u'Viola canina subsp. einseleana',u'Viola canina subsp. ruppii',u'Viola canina var. canina',u'Viola canina var. dunensis',u'Viola collina',u'Viola cryana',u'Viola diversifolia',u'Viola elatior',u'Viola hispida',u'Viola jordanii',u'Viola kitaibeliana',u'Viola kitaibeliana var. kitaibeliana',u'Viola kitaibeliana var. trimestris',u'Viola lactea',u'Viola mirabilis',u'Viola palustris',u'Viola persicifolia',u'Viola pinnata',u'Viola pseudomirabilis',u'Viola pumila',u'Viola rupestris',u'Viola tricolor subsp. curtisii',u'Viola x multicaulis',u'Viscaria alpina',u'Viscaria vulgaris',u'Viscaria vulgaris subsp. vulgaris',u'Vitex agnus-castus',u'Vitis vinifera subsp. sylvestris',u'Vulpiella stipoides',u'Wahlenbergia hederacea',u'Xanthoselinum alsaticum',u'Xanthoselinum alsaticum subsp. alsaticum',u'Xanthoselinum alsaticum subsp. venetum',u'Xanthoselinum alsaticum var. alsaticum',u'Xanthoselinum alsaticum var. discolor',u'Xatardia scabra',u'Xeranthemum cylindraceum',u'Xeranthemum inapertum',u'Xylosma buxifolia',u'Zannichellia obtusifolia',u'Zannichellia palustris',u'Zannichellia palustris subsp. palustris',u'Zannichellia peltata',u'Zostera marina',u'Zostera marina var. angustifolia',u'Zostera marina var. marina',u'Zostera noltei',u'Zygia latifolia',u'---Chlorophytes et Charophytes---',u'Enteromorpha dangeardii',u'Enteromorpha hendayensis',u'Lamprothamnium papulosum',u'Lamprothamnium papulosum f. aragonense',u'Lamprothamnium papulosum f. pouzolsii',u'Lamprothamnium papulosum var. hansenii',u'Lamprothamnium papulosum var. toletanum',u'Tolypella salina',u'---Gymnospermes---',u'Ephedra distachya',u'Ephedra distachya subsp. distachya',u'Ephedra distachya subsp. helvetica',u'Ephedra major',u'Ephedra major subsp. major',u'Juniperus communis',u'Juniperus communis subsp. communis',u'Juniperus communis subsp. intermedia',u'Juniperus communis subsp. nana',u'Juniperus oxycedrus subsp. macrocarpa',u'Juniperus thurifera',u'Juniperus thurifera var. thurifera',u'Pinus mugo',u'Pinus mugo nothosubsp. rotundata',u'Pinus mugo subsp. mugo',u'---Hépatiques et Anthocérotes---',u'Anastrophyllum minutum',u'Bazzania trilobata',u'Bazzania trilobata var. depauperata',u'Bazzania trilobata var. trilobata',u'Blasia pusilla',u'Calypogeia muelleriana',u'Cephaloziella dentata',u'Cephaloziella elachista',u'Cololejeunea calcarea',u'Cololejeunea rossettiana',u'Douinia ovata',u'Fuscocephaloziopsis connivens',u'Fuscocephaloziopsis pleniceps',u'Gymnocolea inflata',u'Gymnocolea inflata var. inflata',u'Harpanthus scutatus',u'Jungermannia pumila',u'Leiomylia anomala',u'Lepidozia cupressina',u'Mannia triandra',u'Marchesinia mackaii',u'Marsupella sprucei',u'Metzgeria pubescens',u'Moerckia hibernica',u'Mylia taylorii',u'Nardia compressa',u'Neoorthocaulis attenuatus',u'Nowellia curvifolia',u'Odontoschisma fluitans',u'Oxymitra incrassata',u'Pallavicinia lyellii',u'Ptilidium ciliare',u'Riccia breidleri',u'Riella helicophylla',u'Riella notarisii',u'Riella parisii',u'Saccogyna viticulosa',u'Southbya nigrella',u'Southbya tophacea',u'Tritomaria capitata',u'---Lichens---',u'Cladonia rangiferina',u'Lobaria pulmonaria',u'Lobaria pulmonaria var. meridionalis',u'Lobaria pulmonaria var. pulmonaria',u'Peltigera ponojensis',u'---Mousses---',u'Andreaea crassinervia',u'Andreaea rothii',u'Andreaea rothii subsp. falcata',u'Andreaea rothii subsp. rothii',u'Andreaea rupestris',u'Andreaea rupestris var. papillosa',u'Andreaea rupestris var. rupestris',u'Anomobryum julaceum',u'Anomodontella longifolia',u'Bartramia stricta',u'Bruchia vogesiaca',u'Buxbaumia viridis',u'Campylopus oerstedianus',u'Campylostelium saxicola',u'Cinclidium stygium',u'Cleistocarpidium palustre',u'Coscinodon cribrosus',u'Crossidium aberrans',u'Dichelyma capillaceum',u'Dichodontium palustre',u'Dicranum polysetum',u'Dicranum spurium',u'Dicranum viride',u'Didymodon giganteus',u'Drepanocladus lycopodioides',u'Drepanocladus trifarius',u'Ephemerum serratum',u'Fissidens bryoides var. caespitans',u'Fissidens fontanus',u'Fissidens monguillonii',u'Fissidens osmundoides',u'Fissidens rivularis',u'Fissidens viridulus',u'Fissidens viridulus var. incurvus',u'Fissidens viridulus var. viridulus',u'Grimmia torquata',u'Hamatocaulis vernicosus',u'Hennediella heimii',u'Hennediella heimii var. heimii',u'Hookeria lucens',u'Hyocomium armoricum',u'Leucobryum glaucum',u'Meesia longiseta',u'Meesia triquetra',u'Meesia uliginosa',u'Orthotrichum rogeri',u'Paludella squarrosa',u'Phascum cuspidatum',u'Physcomitrium eurystomum',u'Physcomitrium eurystomum subsp. eurystomum',u'Pseudocampylium radicale',u'Ptychostomum cyclophyllum',u'Ptychostomum pseudotriquetrum var. pseudotriquetrum',u'Pyramidula tetragona',u'Rhizomnium pseudopunctatum',u'Rhytidium rugosum',u'Sanionia uncinata',u'Seligeria donniana',u'Sematophyllum substrumulosum',u'Sphagnum affine',u'Sphagnum angustifolium',u'Sphagnum auriculatum',u'Sphagnum austinii',u'Sphagnum balticum',u'Sphagnum capillifolium',u'Sphagnum centrale',u'Sphagnum compactum',u'Sphagnum contortum',u'Sphagnum cuspidatum',u'Sphagnum denticulatum f. crassicladum',u'Sphagnum divinum',u'Sphagnum fallax',u'Sphagnum fimbriatum',u'Sphagnum flexuosum',u'Sphagnum fuscum',u'Sphagnum girgensohnii',u'Sphagnum inundatum',u'Sphagnum lindbergii',u'Sphagnum majus',u'Sphagnum majus subsp. norvegicum',u'Sphagnum medium',u'Sphagnum molle',u'Sphagnum obtusum',u'Sphagnum palustre',u'Sphagnum papillosum',u'Sphagnum platyphyllum',u'Sphagnum pulchrum',u'Sphagnum pylaesii',u'Sphagnum quinquefarium',u'Sphagnum riparium',u'Sphagnum rubellum',u'Sphagnum russowii',u'Sphagnum squarrosum',u'Sphagnum subnitens',u'Sphagnum subnitens subsp. subnitens',u'Sphagnum subsecundum',u'Sphagnum tenellum',u'Sphagnum teres',u'Sphagnum warnstorfii',u'Splachnum ampullaceum',u'Tayloria tenuis',u'Tortella nitida',u'Tortella nitida var. media',u'Tortella nitida var. obtusa',u'Tortella nitida var. subtortuosa',u'Trematodon ambiguus',u'Weissia squarrosa',u'---Ochrophytes---'u'Fucus chalonii',u'---Ptéridophytes---'u'Adiantum capillus-veneris',u'Allosorus acrosticus',u'Allosorus hispanicus',u'Allosorus tinaei',u'Anogramma leptophylla',u'Asplenium cuneifolium',u'Asplenium cuneifolium subsp. cuneifolium',u'Asplenium fissum',u'Asplenium foreziense',u'Asplenium jahandiezii',u'Asplenium lepidum',u'Asplenium lepidum subsp. lepidum',u'Asplenium marinum',u'Asplenium obovatum',u'Asplenium obovatum subsp. billotii',u'Asplenium obovatum subsp. cyrnosardoum',u'Asplenium obovatum subsp. obovatum',u'Asplenium petrarchae',u'Asplenium petrarchae subsp. petrarchae',u'Asplenium sagittatum',u'Asplenium scolopendrium',u'Asplenium seelosii',u'Asplenium seelosii subsp. glabrum',u'Asplenium septentrionale',u'Asplenium septentrionale subsp. septentrionale',u'Asplenium trichomanes subsp. pachyrachis',u'Asplenium viride',u'Asplenium x alternifolium',u'Asplenium x alternifolium nothosubsp. alternifolium',u'Asplenium x alternifolium nothosubsp. heufleri',u'Asplenium x sleepiae',u'Asplenium x sleepiae nothosubsp. krameri',u'Asplenium x sleepiae nothosubsp. sleepiae',u'Athyrium distentifolium',u'Blechnum spicant',u'Blechnum spicant var. spicant',u'Botrychium lanceolatum',u'Botrychium lunaria',u'Botrychium matricariifolium',u'Botrychium simplex',u'Cosentinia vellea',u'Cosentinia vellea subsp. vellea',u'Cryptogramma crispa',u'Cyclosorus pozoi',u'Cyrtomium fortunei',u'Cystopteris diaphana',u'Cystopteris dickieana',u'Cystopteris fragilis',u'Cystopteris fragilis var. fragilis',u'Cystopteris fragilis var. huteri',u'Cystopteris montana',u'Dryopteris aemula',u'Dryopteris affinis subsp. cambrensis',u'Dryopteris cristata',u'Dryopteris pallida',u'Dryopteris pallida subsp. pallida',u'Dryopteris remota',u'Dryopteris submontana',u'Dryopteris tyrrhena',u'Dryopteris x deweveri',u'Equisetum hyemale',u'Equisetum hyemale subsp. hyemale',u'Equisetum ramosissimum',u'Equisetum ramosissimum subsp. ramosissimum',u'Equisetum sylvaticum',u'Equisetum variegatum',u'Equisetum variegatum subsp. variegatum',u'Equisetum x mackayi',u'Equisetum x mackayi nothosubsp. mackayi',u'Equisetum x moorei',u'Gymnocarpium dryopteris',u'Gymnocarpium robertianum',u'Huperzia selago',u'Huperzia selago subsp. selago',u'Hymenophyllum tunbrigense',u'Hymenophyllum wilsonii',u'Isoetes boryana',u'Isoetes duriei',u'Isoetes echinospora',u'Isoetes histrix',u'Isoetes lacustris',u'Isoetes setacea',u'Isoetes velata',u'Isoetes velata subsp. tenuissima',u'Isoetes velata subsp. velata',u'Lycopodiella inundata',u'Lycopodium alpinum',u'Lycopodium annotinum',u'Lycopodium annotinum subsp. annotinum',u'Lycopodium clavatum',u'Lycopodium clavatum subsp. clavatum',u'Lycopodium complanatum',u'Lycopodium tristachyum',u'Marsilea quadrifolia',u'Marsilea strigosa',u'Matteuccia struthiopteris',u'Ophioglossum azoricum',u'Ophioglossum lusitanicum',u'Ophioglossum vulgatum',u'Oreopteris limbosperma',u'Osmunda regalis',u'Paragymnopteris marantae',u'Paragymnopteris marantae subsp. marantae',u'Phegopteris connectilis',u'Pilularia globulifera',u'Pilularia minuta',u'Polypodium cambricum',u'Polypodium cambricum subsp. cambricum',u'Polystichum aculeatum',u'Polystichum braunii',u'Polystichum lonchitis',u'Polystichum setiferum',u'Polystichum setiferum var. hastulatum',u'Polystichum setiferum var. setiferum',u'Pteris cretica',u'Salvinia natans',u'Sceptridium multifidum',u'Selaginella denticulata',u'Selaginella helvetica',u'Thelypteris palustris',u'Vandenboschia speciosa',u'Woodsia alpina',u'Woodsia ilvensis',u'Woodwardia radicans']
            self.dlg.flores.addItems(flores) 
            faunes = [u'---Amphibiens---',u'Allobates chalcopis',u'Alytes obstetricans almogavarii',u'Alytes obstetricans obstetricans',u'Alytes obstetricans',u'Bombina variegata variegata',u'Bombina variegata',u'Bufo bufo',u'Bufotes viridis balearicus',u'Bufotes viridis viridis',u'Bufotes viridis',u'Calotriton asper',u'Discoglossus montalentii',u'Discoglossus pictus',u'Discoglossus sardus',u'Eleutherodactylus martinicensis',u'Epidalea calamita',u'Euproctus montanus',u'Hyla arborea arborea',u'Hyla arborea',u'Hyla meridionalis',u'Hyla sarda',u'Ichthyosaura alpestris alpestris',u'Ichthyosaura alpestris apuana',u'Ichthyosaura alpestris',u'Lissotriton helveticus helveticus',u'Lissotriton helveticus',u'Lissotriton vulgaris vulgaris',u'Lissotriton vulgaris',u'Pelobates cultripes',u'Pelobates fuscus fuscus',u'Pelobates fuscus',u'Pelodytes punctatus',u'Pelophylax kl. esculentus',u'Pelophylax kl. grafi',u'Pelophylax lessonae bergeri',u'Pelophylax lessonae lessonae',u'Pelophylax lessonae',u'Pelophylax perezi',u'Pelophylax ridibundus',u'Rana arvalis arvalis',u'Rana arvalis',u'Rana dalmatina',u'Rana pyrenaica',u'Rana temporaria canigonensis',u'Rana temporaria temporaria',u'Rana temporaria',u'Salamandra atra atra',u'Salamandra atra',u'Salamandra corsica',u'Salamandra lanzai',u'Salamandra salamandra fastuosa',u'Salamandra salamandra salamandra',u'Salamandra salamandra terrestris',u'Salamandra salamandra',u'Speleomantes strinatii',u'Triturus carnifex',u'Triturus cristatus x T. marmoratus',u'Triturus cristatus',u'Triturus marmoratus',u'---Arachnides---',u'Caribena versicolor',u'---Autres---',u'Centrostephanus longispinus',u'---Bivalves---',u'Lithophaga lithophaga',u'Margaritifera margaritifera',u'Pinna nobilis',u'Pinna rudis',u'Pseudunio auricularius',u'Unio crassus courtillieri',u'Unio crassus crassus',u'Unio crassus',u'---Crustacés---',u'Astacus astacus',u'Austropotamobius pallipes',u'Austropotamobius torrentium',u'Scyllarides latus',u'---Gastéropodes---',u'Abida ateni',u'Alzoniella elliptica',u'Alzoniella pyrenaica',u'Anisus vorticulus',u'Avenionia brevis',u'Bythinella bicarinata',u'Bythinella carinulata',u'Bythinella pupoides phreaticola',u'Bythinella pupoides pupoides',u'Bythinella pupoides',u'Bythinella reyniesii',u'Bythinella vesontiana',u'Bythinella viridis',u'Bythiospeum articense',u'Bythiospeum bourguignati',u'Bythiospeum bressanum',u'Bythiospeum diaphanum diaphanum',u'Bythiospeum diaphanum fernetense',u'Bythiospeum diaphanum luberonense',u'Bythiospeum diaphanum michaellense',u'Bythiospeum diaphanum montbrunense',u'Bythiospeum diaphanum regalonense',u'Bythiospeum diaphanum sarriansense',u'Bythiospeum diaphanum',u'Bythiospeum garnieri',u'Chondrina megacheilos caziotana',u'Chondrina megacheilos',u'Cryptazeca monodonta',u'Cryptazeca subcylindrica',u'Cyrnotheba corsica',u'Elona quimperiana',u'Fissuria boui',u'Helix ceratina',u'Heraultiella exilis',u'Hypnophila remyi',u'Islamia minuta minuta',u'Macrogastra mellae leia',u'Macularia niciensis dupuyi',u'Macularia niciensis guebhardi',u'Macularia niciensis niciensis',u'Macularia niciensis',u'Macularia saintivesi',u'Moitessieria locardi',u'Moitessieria rolandiana',u'Moitessieria simoniana',u'Neniatlanta pauli',u'Norelona pyrenaica',u'Otala punctata',u'Palacanthilhiopsis vervierii',u'Paladilhia pleurotoma',u'Patella ferruginea',u'Plagigeyeria deformata',u'Platyla foliniana',u'Renea bourguignatiana',u'Renea gormonti',u'Renea moutonii moutonii',u'Renea moutonii singularis',u'Renea moutonii',u'Renea paillona',u'Semisalsa scamandri',u'Solatopupa cianensis',u'Solatopupa guidoni guidoni',u'Solatopupa guidoni',u'Solatopupa psarolena',u'Spiralix puteana',u'Spiralix rayi',u'Spiralix vitrea',u'Tacheocampylaea raspailii',u'Trissexodon constrictus',u'Truncatellina arcyensis',u'Vitrea pseudotrolli',u'---Insectes---',u'Actinotia radiosa',u'Aegosoma scabricorne',u'Aeshna grandis',u'Agonum piceum',u'Agrotis bigramma',u'Amara fusca',u'Anaplectoides prasina',u'Anarta odontites',u'Apamea anceps',u'Aphaenops aeacus',u'Aphaenops alberti',u'Aphaenops baretosanus baretosanus',u'Aphaenops baretosanus gaudini',u'Aphaenops baretosanus',u'Aphaenops bessoni',u'Aphaenops blancheti',u'Aphaenops bonneti',u'Aphaenops bouilloni',u'Aphaenops bourgoini bourgoini',u'Aphaenops bourgoini crassus',u'Aphaenops bourgoini vandeli',u'Aphaenops bourgoini',u'Aphaenops bucephalus',u'Aphaenops carrerei',u'Aphaenops cerberus bruneti',u'Aphaenops cerberus cerberus',u'Aphaenops cerberus inaequalis',u'Aphaenops cerberus obtusus',u'Aphaenops cerberus truncatus',u'Aphaenops cerberus',u'Aphaenops chappuisi',u'Aphaenops chaudoiri',u'Aphaenops cissauguensis',u'Aphaenops colluvii',u'Aphaenops crypticola',u'Aphaenops ehlersi',u'Aphaenops elegans',u'Aphaenops eskualduna',u'Aphaenops giraudi delicatulus',u'Aphaenops giraudi giraudi',u'Aphaenops giraudi',u'Aphaenops gracilis',u'Aphaenops hortensis',u'Aphaenops hustachei',u'Aphaenops jauzioni',u'Aphaenops jeanneli',u'Aphaenops laurenti',u'Aphaenops leschenaulti',u'Aphaenops linderi labarthei',u'Aphaenops linderi linderi',u'Aphaenops linderi',u'Aphaenops longicollis',u'Aphaenops loubensi',u'Aphaenops ludovici ludovici',u'Aphaenops ludovici queffeleci',u'Aphaenops ludovici',u'Aphaenops mariaerosae',u'Aphaenops michaeli',u'Aphaenops minos',u'Aphaenops mouriesi',u'Aphaenops navaricus',u'Aphaenops ochsi cabidochei',u'Aphaenops ochsi ochsi',u'Aphaenops ochsi reymondi',u'Aphaenops ochsi',u'Aphaenops orionis bassaburensis',u'Aphaenops orionis orionis',u'Aphaenops orionis',u'Aphaenops pandellei ambiellensis',u'Aphaenops pandellei pandellei',u'Aphaenops pandellei',u'Aphaenops pecoudi',u'Aphaenops penacollaradensis weilli',u'Aphaenops penacollaradensis',u'Aphaenops pluto hydrophilus',u'Aphaenops pluto pluto',u'Aphaenops pluto',u'Aphaenops pseudocrypticola',u'Aphaenops rebereti',u'Aphaenops rhadamanthus',u'Aphaenops sinester',u'Aphaenops sioberae',u'Aphaenops tiresias aerosus',u'Aphaenops tiresias juliettae',u'Aphaenops tiresias robustus',u'Aphaenops tiresias tiresias',u'Aphaenops tiresias tisiphone',u'Aphaenops tiresias',u'Aphaenops vandeli bouiganensis',u'Aphaenops vandeli vandeli',u'Aphaenops vandeli',u'Aphaenops vasconicus',u'Aporia crataegi',u'Arctia matronula matronula',u'Arctia matronula',u'Arenostola phragmitidis',u'Arethusana arethusa ganda',u'Arethusana arethusa',u'Aulops alpina alpina',u'Aulops alpina',u'Blethisa multipunctata multipunctata',u'Blethisa multipunctata',u'Bolbelasmus unicornis',u'Boloria aquilonaris',u'Boloria dia',u'Boloria eunomia',u'Bombus cullumanus',u'Bombus distinguendus',u'Bombus humilis',u'Bombus ruderatus',u'Bombus subterraneus',u'Bombus sylvarum',u'Bombus veteranus',u'Boyeria irene',u'Callimorpha dominula',u'Calliptamus barbarus barbarus',u'Calliptamus barbarus',u'Calosoma auropunctatum auropunctatum',u'Calosoma auropunctatum',u'Carabus auratus honnoratii',u'Carabus auronitens auronitens',u'Carabus nodulosus',u'Carabus solieri bonadonai',u'Carabus solieri bonnetianus',u'Carabus solieri clairi',u'Carabus solieri solieri',u'Carabus solieri',u'Carterocephalus palaemon',u'Cerambyx cerdo cerdo',u'Cerambyx cerdo',u'Cerura vinula',u'Cetonischema speciosissima',u'Chelis maculosa maculosa',u'Chelis maculosa stertzi',u'Chelis maculosa',u'Chilodes maritima',u'Chlaenius tristis',u'Cicadetta montana',u'Cicindela sylvatica',u'Clostera anastomosis',u'Coenagrion hastulatum',u'Coenagrion mercuriale',u'Coenagrion scitulum',u'Coenonympha hero',u'Coenonympha oedippus',u'Coenonympha tullia',u'Colias palaeno europome',u'Colias palaeno europomene',u'Colias palaeno',u'Conisania luteago behouneki',u'Conisania luteago olbiena',u'Conisania luteago',u'Cordulegaster boltonii boltonii',u'Cordulegaster boltonii',u'Cucujus cinnaberinus',u'Cybister lateralimarginalis lateralimarginalis',u'Cybister lateralimarginalis',u'Cymindis miliaris',u'Decticus verrucivorus monspelliensis',u'Decticus verrucivorus verrucivorus',u'Decticus verrucivorus',u'Diacrisia metelkana',u'Dicerca berolinensis',u'Distoleon tetragrammicus',u'Drymonia velitaris',u'Dytiscus latissimus',u'Epatolmis luctifera',u'Epitheca bimaculata',u'Erebia medusa',u'Erebia sudetica belledonnae',u'Erebia sudetica liorana',u'Erebia sudetica',u'Eriogaster catax',u'Eucarta amethystina',u'Euphydryas aurinia aurinia',u'Euphydryas aurinia provincialis',u'Euphydryas aurinia pyrenesdebilis',u'Euphydryas aurinia sareptana',u'Euphydryas aurinia',u'Euphydryas beckeri',u'Euphydryas desfontainii',u'Euphydryas maturna',u'Eurythyrea quercus',u'Fabriciana elisa',u'Glaucopsyche alexis',u'Globia sparganii',u'Gomphus graslinii',u'Gortyna borelii',u'Graellsia isabellae',u'Graphiphora augur',u'Graphoderus bilineatus',u'Hadena albimacula',u'Hadena perplexa',u'Hipparchia fagi',u'Hipparchia statilinus',u'Hyles hippophaes hippophaes',u'Hyles hippophaes',u'Iphiclides podalirius podalirius',u'Iphiclides podalirius',u'Ischnura pumilio',u'Lacon querceus',u'Lamia textor',u'Lamprodila festiva festiva',u'Lamprodila festiva',u'Ledra aurita',u'Lemonia dumi',u'Lestes dryas',u'Leucorrhinia albifrons',u'Leucorrhinia caudalis',u'Leucorrhinia pectoralis',u'Leucorrhinia rubicunda',u'Libelloides coccajus',u'Libelloides longicornis',u'Limenitis populi',u'Liocola marmorata marmorata',u'Lopinga achine',u'Lycaena dispar',u'Lycaena helle arduinnae',u'Lycaena helle arvernica',u'Lycaena helle deslandesi',u'Lycaena helle eneli',u'Lycaena helle leonia',u'Lycaena helle magdalenae',u'Lycaena helle perretei',u'Lycaena helle',u'Macromia splendens',u'Mantis religiosa',u'Melitaea athalia',u'Melitaea cinxia',u'Melitaea didyma',u'Melitaea phoebe',u'Meloe proscarabaeus proscarabaeus',u'Meloe proscarabaeus',u'Naenia typica',u'Nymphalis antiopa',u'Nymphalis polychloros',u'Oecanthus pellucens pellucens',u'Oecanthus pellucens',u'Oedipoda caerulescens caerulescens',u'Oedipoda caerulescens sardeti',u'Oedipoda caerulescens',u'Oodes gracilis',u'Ophiogomphus cecilia',u'Ophonus cordatus',u'Osmoderma eremita eremita',u'Osmoderma eremita',u'Osmylus fulvicephalus',u'Oxygastra curtisii',u'Pachetra sagittigera',u'Panagaeus cruxmajor',u'Papilio alexanor alexanor',u'Papilio alexanor destelensis',u'Papilio alexanor',u'Papilio hospiton',u'Parnassius apollo geminus',u'Parnassius apollo lioranus',u'Parnassius apollo lozerae',u'Parnassius apollo meridionalis',u'Parnassius apollo nivatus',u'Parnassius apollo pyrenaicus',u'Parnassius apollo',u'Parnassius corybas gazeli',u'Parnassius corybas sacerdos',u'Parnassius corybas',u'Parnassius mnemosyne cassiensis',u'Parnassius mnemosyne ceuzensis',u'Parnassius mnemosyne dinianus',u'Parnassius mnemosyne excelsus',u'Parnassius mnemosyne gallicus',u'Parnassius mnemosyne mixtus',u'Parnassius mnemosyne montdorensis',u'Parnassius mnemosyne parmenides',u'Parnassius mnemosyne rencurelensis',u'Parnassius mnemosyne turatii',u'Parnassius mnemosyne vernetanus',u'Parnassius mnemosyne vivaricus',u'Parnassius mnemosyne',u'Phengaris alcon',u'Phengaris arion',u'Phengaris nausithous',u'Phengaris teleius',u'Phryganophilus ruficollis',u'Pieris ergane',u'Pieris mannii',u'Plebejus argyrognomon',u'Plebejus idas',u'Poecilus kugelanni',u'Polia hepatica',u'Polymixis xanthomista xanthomista',u'Polymixis xanthomista',u'Prionotropis azami',u'Prionotropis rhodanica',u'Proserpinus proserpina',u'Pseudophilotes baton',u'Pterostichus aterrimus aterrimus',u'Pterostichus aterrimus nigerrimus',u'Pterostichus aterrimus',u'Pterostichus quadrifoveolatus',u'Rosalia alpina alpina',u'Rosalia alpina',u'Ruspolia nitidula nitidula',u'Ruspolia nitidula',u'Saga pedo',u'Saturnia pyri',u'Satyrium w-album',u'Senta flammea',u'Sideridis turbida',u'Stylurus flavipes',u'Sympecma paedisca',u'Sympetrum danae',u'Sympetrum flaveolum',u'Synuchus vivalis',u'Trichaphaenops cerdonicus',u'Trichaphaenops gounellei annae',u'Trichaphaenops gounellei attenuatus',u'Trichaphaenops gounellei gounellei',u'Trichaphaenops gounellei',u'Trichaphaenops obesus',u'Trichaphaenops sollaudi sollaudi',u'Trichaphaenops sollaudi',u'Zabrus curtus curtus',u'Zabrus curtus',u'Zerynthia polyxena',u'Zerynthia rumina',u'Zygaena brizae vesubiana',u'Zygaena fausta',u'Zygaena rhadamanthus',u'---Mammifères---',u'Arctocephalus forsteri',u'Arctocephalus gazella',u'Arctocephalus tropicalis',u'Ardops nichollsi koopmani',u'Ardops nichollsi',u'Artibeus jamaicensis',u'Arvicola sapidus tenebricus',u'Arvicola sapidus',u'Balaenoptera acutorostrata acutorostrata',u'Balaenoptera acutorostrata',u'Balaenoptera bonaerensis',u'Balaenoptera borealis borealis',u'Balaenoptera borealis schlegelii',u'Balaenoptera borealis',u'Balaenoptera edeni',u'Balaenoptera musculus brevicauda',u'Balaenoptera musculus intermedia',u'Balaenoptera musculus musculus',u'Balaenoptera musculus',u'Balaenoptera physalus physalus',u'Balaenoptera physalus quoyi',u'Balaenoptera physalus',u'Barbastella barbastellus',u'Berardius arnuxii',u'Brachyphylla cavernarum',u'Canis lupus lupus',u'Canis lupus',u'Caperea marginata',u'Capra ibex',u'Capra pyrenaica',u'Castor fiber',u'Cephalorhynchus commersonii kerguelensis',u'Cephalorhynchus commersonii',u'Cricetus cricetus',u'Cystophora cristata',u'Delphinapterus leucas',u'Delphinus delphis capensis',u'Delphinus delphis delphis',u'Delphinus delphis',u'Dugong dugon',u'Eptesicus nilssonii',u'Eptesicus serotinus',u'Erignathus barbatus barbatus',u'Erignathus barbatus',u'Erinaceus europaeus',u'Eubalaena australis',u'Eubalaena glacialis',u'Felis silvestris lybica',u'Felis silvestris silvestris',u'Felis silvestris',u'Feresa attenuata',u'Galemys pyrenaicus',u'Genetta genetta',u'Globicephala macrorhynchus',u'Globicephala melas edwardii',u'Globicephala melas melas',u'Globicephala melas',u'Grampus griseus',u'Halichoerus grypus',u'Hydrurga leptonyx',u'Hyperoodon ampullatus',u'Hyperoodon planifrons',u'Hypsugo savii',u'Indopacetus pacificus',u'Kogia breviceps',u'Kogia sima',u'Lagenodelphis hosei',u'Lagenorhynchus acutus',u'Lagenorhynchus albirostris',u'Lagenorhynchus cruciger',u'Lagenorhynchus obscurus obscurus',u'Lagenorhynchus obscurus',u'Leptonychotes weddellii',u'Lissodelphis peronii',u'Lobodon carcinophagus',u'Lutra lutra',u'Lynx lynx carpathicus',u'Lynx lynx',u'Megaptera novaeangliae australis',u'Megaptera novaeangliae novaeangliae',u'Megaptera novaeangliae',u'Mesoplodon bidens',u'Mesoplodon densirostris',u'Mesoplodon europaeus',u'Mesoplodon layardii',u'Mesoplodon mirus',u'Miniopterus schreibersii',u'Mirounga leonina',u'Molossus molossus',u'Monachus monachus',u'Monophyllus plethodon luciae',u'Monophyllus plethodon',u'Muscardinus avellanarius',u'Mustela lutreola',u'Myotis alcathoe',u'Myotis bechsteinii',u'Myotis blythii oxygnathus',u'Myotis blythii',u'Myotis brandtii',u'Myotis capaccinii capaccinii',u'Myotis capaccinii',u'Myotis dasycneme',u'Myotis daubentonii',u'Myotis emarginatus',u'Myotis escalerai',u'Myotis martiniquensis',u'Myotis myotis',u'Myotis mystacinus',u'Myotis nattereri',u'Myotis punicus',u'Natalus stramineus',u'Neomys anomalus anomalus',u'Neomys anomalus milleri',u'Neomys anomalus',u'Neomys fodiens fodiens',u'Neomys fodiens',u'Noctilio leporinus',u'Nyctalus lasiopterus',u'Nyctalus leisleri leisleri',u'Nyctalus leisleri',u'Nyctalus noctula',u'Odobenus rosmarus rosmarus',u'Odobenus rosmarus',u'Ommatophoca rossii',u'Orcinus orca',u'Ovis gmelinii musimon',u'Pagophilus groenlandicus',u'Peponocephala electra',u'Phoca vitulina concolor',u'Phoca vitulina vitulina',u'Phoca vitulina',u'Phocoena dioptrica',u'Phocoena phocoena phocoena',u'Phocoena phocoena',u'Physeter macrocephalus',u'Pipistrellus kuhlii',u'Pipistrellus nathusii',u'Pipistrellus pipistrellus',u'Pipistrellus pygmaeus',u'Plecotus auritus auritus',u'Plecotus auritus',u'Plecotus austriacus',u'Plecotus macrobullaris',u'Pseudorca crassidens',u'Pteronotus davyi',u'Pusa hispida hispida',u'Pusa hispida',u'Rhinolophus euryale',u'Rhinolophus ferrumequinum ferrumequinum',u'Rhinolophus ferrumequinum',u'Rhinolophus hipposideros',u'Rhinolophus mehelyi',u'Sciurus vulgaris fuscoater',u'Sciurus vulgaris',u'Sotalia guianensis',u'Sousa plumbea',u'Stenella attenuata attenuata',u'Stenella attenuata',u'Stenella clymene',u'Stenella coeruleoalba',u'Stenella frontalis',u'Stenella longirostris longirostris',u'Stenella longirostris orientalis',u'Stenella longirostris',u'Steno bredanensis',u'Sturnira angeli',u'Tadarida brasiliensis',u'Tadarida teniotis',u'Trichechus manatus manatus',u'Trichechus manatus',u'Tursiops aduncus',u'Tursiops truncatus truncatus',u'Tursiops truncatus',u'Ursus arctos arctos',u'Ursus arctos',u'Vespertilio murinus',u'Ziphius cavirostris',u'---Oiseaux---',u'Acanthis flammea cabaret',u'Acanthis flammea flammea',u'Acanthis flammea',u'Acanthis hornemanni',u'Accipiter gentilis arrigonii',u'Accipiter gentilis gentilis',u'Accipiter gentilis',u'Accipiter nisus',u'Acrocephalus agricola',u'Acrocephalus arundinaceus',u'Acrocephalus dumetorum',u'Acrocephalus melanopogon',u'Acrocephalus paludicola',u'Acrocephalus palustris',u'Acrocephalus schoenobaenus',u'Acrocephalus scirpaceus',u'Actitis hypoleucos',u'Actitis macularius',u'Aegithalos caudatus',u'Aegolius funereus',u'Aegypius monachus',u'Alaudala rufescens',u'Alca torda',u'Alcedo atthis',u'Alectoris barbara',u'Alectoris chukar',u'Alle alle',u'Anas crecca carolinensis',u'Anas eatoni drygalskii',u'Anas eatoni eatoni',u'Anas eatoni',u'Anas falcata',u'Anas rubripes',u'Anous stolidus',u'Anser brachyrhynchus',u'Anser caerulescens',u'Anser erythropus',u'Anthropoides virgo',u'Anthus campestris',u'Anthus cervinus',u'Anthus godlewskii',u'Anthus gustavi',u'Anthus hodgsoni',u'Anthus petrosus littoralis',u'Anthus petrosus petrosus',u'Anthus petrosus',u'Anthus pratensis',u'Anthus richardi',u'Anthus rubescens',u'Anthus spinoletta',u'Anthus trivialis',u'Antigone canadensis',u'Aphrodroma brevirostris',u'Aptenodytes forsteri',u'Aptenodytes patagonicus halli',u'Aptenodytes patagonicus',u'Apus affinis',u'Apus apus',u'Apus pallidus',u'Aquila adalberti',u'Aquila chrysaetos',u'Aquila fasciata',u'Aquila heliaca',u'Aquila nipalensis',u'Ardea alba alba',u'Ardea alba egretta',u'Ardea alba',u'Ardea cinerea',u'Ardea herodias',u'Ardea melanocephala',u'Ardea purpurea',u'Ardenna carneipes',u'Ardenna gravis',u'Ardenna grisea',u'Ardeola ralloides',u'Arenaria interpres',u'Asio flammeus',u'Asio otus',u'Athene noctua',u'Aythya affinis',u'Aythya collaris',u'Aythya nyroca',u'Aythya valisineria',u'Bartramia longicauda',u'Bombycilla garrulus',u'Botaurus stellaris',u'Branta bernicla bernicla',u'Branta bernicla hrota',u'Branta bernicla nigricans',u'Branta bernicla',u'Branta leucopsis',u'Branta ruficollis',u'Bubo bubo',u'Bubo scandiacus',u'Bubulcus ibis ibis',u'Bubulcus ibis',u'Bucanetes githagineus',u'Bucephala albeola',u'Bucephala islandica',u'Bulweria bulwerii',u'Burhinus oedicnemus',u'Buteo buteo vulpinus',u'Buteo buteo',u'Buteo lagopus',u'Buteo platypterus rivierei',u'Buteo platypterus',u'Buteo rufinus cirtensis',u'Buteo rufinus',u'Butorides striata',u'Butorides virescens',u'Calandrella brachydactyla',u'Calcarius lapponicus',u'Calidris acuminata',u'Calidris alba',u'Calidris alpina alpina',u'Calidris alpina arctica',u'Calidris alpina schinzii',u'Calidris alpina',u'Calidris bairdii',u'Calidris canutus',u'Calidris falcinellus',u'Calidris ferruginea',u'Calidris fuscicollis',u'Calidris himantopus',u'Calidris maritima',u'Calidris mauri',u'Calidris melanotos',u'Calidris minuta',u'Calidris minutilla',u'Calidris pusilla',u'Calidris ruficollis',u'Calidris subminuta',u'Calidris subruficollis',u'Calidris temminckii',u'Calonectris diomedea',u'Caprimulgus europaeus',u'Caprimulgus ruficollis',u'Cardellina canadensis',u'Carduelis carduelis',u'Carduelis citrinella',u'Carduelis corsicana',u'Carpodacus erythrinus',u'Catharus minimus',u'Catharus ustulatus',u'Cecropis daurica',u'Cepphus grylle',u'Cercotrichas galactotes',u'Certhia brachydactyla',u'Certhia familiaris',u'Cettia cetti',u'Chaetura martinica',u'Chaetura pelagica',u'Charadrius alexandrinus',u'Charadrius asiaticus',u'Charadrius dubius',u'Charadrius hiaticula',u'Charadrius leschenaultii',u'Charadrius mongolus',u'Charadrius pecuarius',u'Charadrius semipalmatus',u'Charadrius vociferus',u'Charadrius wilsonia',u'Chersophilus duponti',u'Chionis minor crozettensis',u'Chionis minor minor',u'Chionis minor',u'Chlamydotis macqueenii',u'Chlidonias hybrida',u'Chlidonias leucopterus',u'Chlidonias niger',u'Chloris chloris',u'Chordeiles minor',u'Chroicocephalus genei',u'Chroicocephalus philadelphia',u'Chroicocephalus ridibundus',u'Ciconia ciconia',u'Ciconia nigra',u'Cinclocerthia ruficauda tremula',u'Cinclocerthia ruficauda',u'Cinclus cinclus',u'Circaetus gallicus',u'Circus aeruginosus',u'Circus cyaneus',u'Circus macrourus',u'Circus pygargus',u'Cisticola juncidis',u'Clamator glandarius',u'Clanga clanga',u'Clanga pomarina',u'Coccothraustes coccothraustes',u'Coccyzus americanus',u'Coccyzus erythropthalmus',u'Coccyzus minor',u'Coereba flaveola martinicana',u'Coereba flaveola',u'Contopus latirostris brunneicapillus',u'Contopus latirostris',u'Coracias garrulus',u'Corvus corax',u'Corvus corone cornix',u'Corvus dauuricus',u'Corvus monedula monedula',u'Corvus monedula soemmeringii',u'Corvus monedula spermologus',u'Corvus monedula',u'Corvus splendens',u'Crex crex',u'Crotophaga ani',u'Cuculus canorus',u'Cursorius cursor',u'Cyanistes caeruleus',u'Cyanistes cyanus',u'Cyanophaia bicolor',u'Cyanopica cyanus',u'Cygnus columbianus bewickii',u'Cygnus cygnus',u'Cygnus olor',u'Cypseloides niger',u'Daption capense',u'Delichon urbicum',u'Dendrocopos leucotos',u'Dendrocopos major',u'Dendrocopos medius',u'Dendrocopos minor',u'Dendrocygna bicolor',u'Diomedea exulans amsterdamensis',u'Diomedea exulans',u'Dolichonyx oryzivorus',u'Dryocopus martius',u'Egretta caerulea',u'Egretta garzetta',u'Egretta gularis',u'Egretta thula',u'Elaenia martinica',u'Elanus caeruleus',u'Emberiza aureola',u'Emberiza bruniceps',u'Emberiza caesia',u'Emberiza calandra',u'Emberiza chrysophrys',u'Emberiza cia',u'Emberiza cirlus',u'Emberiza citrinella',u'Emberiza hortulana',u'Emberiza leucocephalos',u'Emberiza melanocephala',u'Emberiza pusilla',u'Emberiza rustica',u'Emberiza schoeniclus schoeniclus',u'Emberiza schoeniclus witherbyi',u'Emberiza schoeniclus',u'Emberiza spodocephala',u'Eremophila alpestris',u'Erithacus rubecula',u'Eudromias morinellus',u'Eudyptes chrysocome filholi',u'Eudyptes chrysocome',u'Eudyptes chrysolophus',u'Eudyptes schlegeli',u'Eulampis holosericeus',u'Eulampis jugularis',u'Euphonia musica flavifrons',u'Euphonia musica',u'Falco biarmicus',u'Falco cherrug',u'Falco columbarius',u'Falco concolor',u'Falco eleonorae',u'Falco naumanni',u'Falco peregrinus calidus',u'Falco peregrinus peregrinus',u'Falco peregrinus',u'Falco rusticolus',u'Falco sparverius caribaearum',u'Falco sparverius',u'Falco subbuteo',u'Falco tinnunculus',u'Falco vespertinus',u'Ficedula albicollis',u'Ficedula hypoleuca',u'Ficedula parva',u'Ficedula semitorquata',u'Francolinus francolinus',u'Fratercula arctica',u'Fregata magnificens',u'Fregetta grallaria',u'Fregetta tropica',u'Fringilla coelebs',u'Fringilla montifringilla',u'Fulica americana',u'Fulica cristata',u'Fulmarus glacialis',u'Fulmarus glacialoides',u'Galerida cristata',u'Galerida theklae',u'Gallinago delicata',u'Gallinago media',u'Garrodia nereis',u'Gavia adamsii',u'Gavia arctica',u'Gavia immer',u'Gavia stellata',u'Gelochelidon nilotica',u'Geokichla sibirica',u'Geotrygon montana martinica',u'Geotrygon montana',u'Geotrygon mystacea',u'Geronticus eremita',u'Glareola maldivarum',u'Glareola nordmanni',u'Glareola pratincola',u'Glaucidium passerinum',u'Grus grus',u'Gypaetus barbatus',u'Gyps fulvus',u'Gyps rueppellii',u'Haliaeetus albicilla',u'Halobaena caerulea',u'Hieraaetus pennatus',u'Himantopus himantopus himantopus',u'Himantopus himantopus',u'Hippolais icterina',u'Hippolais polyglotta',u'Hirundo rustica',u'Histrionicus histrionicus',u'Hydrobates castro',u'Hydrobates leucorhous',u'Hydrobates monorhis',u'Hydrobates pelagicus melitensis',u'Hydrobates pelagicus pelagicus',u'Hydrobates pelagicus',u'Hydrocoloeus minutus',u'Hydroprogne caspia',u'Hydropsalis cayennensis manati',u'Hydropsalis cayennensis',u'Ichthyaetus audouinii',u'Ichthyaetus ichthyaetus',u'Ichthyaetus melanocephalus',u'Icterus bonana',u'Iduna caligata',u'Iduna opaca',u'Iduna pallida',u'Iduna rama',u'Ixobrychus minutus',u'Jynx torquilla',u'Lagopus lagopus albus',u'Lagopus lagopus',u'Lanius collurio',u'Lanius cristatus',u'Lanius excubitor',u'Lanius isabellinus',u'Lanius meridionalis',u'Lanius minor',u'Lanius nubicus',u'Lanius senator badius',u'Lanius senator senator',u'Lanius senator',u'Larus argentatus',u'Larus cachinnans',u'Larus canus',u'Larus delawarensis',u'Larus dominicanus judithae',u'Larus dominicanus',u'Larus fuscus fuscus',u'Larus fuscus graellsii',u'Larus fuscus intermedius',u'Larus fuscus',u'Larus glaucoides',u'Larus hyperboreus',u'Larus marinus',u'Larus michahellis',u'Larus smithsonianus',u'Leucophaeus atricilla',u'Leucophaeus pipixcan',u'Limnodromus griseus',u'Limnodromus scolopaceus',u'Linaria cannabina',u'Linaria flavirostris',u'Locustella certhiola',u'Locustella fasciolata',u'Locustella fluviatilis',u'Locustella lanceolata',u'Locustella luscinioides',u'Locustella naevia',u'Lophodytes cucullatus',u'Lophophanes cristatus',u'Loxia curvirostra',u'Loxia leucoptera',u'Loxia pytyopsittacus',u'Loxigilla noctis',u'Lullula arborea',u'Luscinia calliope',u'Luscinia luscinia',u'Luscinia megarhynchos',u'Luscinia svecica cyanecula',u'Luscinia svecica namnetum',u'Luscinia svecica svecica',u'Luscinia svecica',u'Macronectes giganteus',u'Macronectes halli',u'Mareca americana',u'Marmaronetta angustirostris',u'Megaceryle alcyon',u'Megaceryle torquata stictipennis',u'Megaceryle torquata',u'Melanitta americana',u'Melanitta deglandi',u'Melanitta perspicillata',u'Melanocorypha bimaculata',u'Melanocorypha calandra',u'Mergellus albellus',u'Mergus merganser',u'Mergus serrator',u'Merops apiaster',u'Merops persicus',u'Microcarbo pygmaeus',u'Milvus migrans',u'Milvus milvus',u'Mimus gilvus antillarum',u'Mimus gilvus',u'Mniotilta varia',u'Molothrus ater',u'Monticola saxatilis',u'Monticola solitarius',u'Montifringilla nivalis',u'Morus bassanus',u'Morus serrator',u'Motacilla alba alba',u'Motacilla alba subpersonata',u'Motacilla alba yarrellii',u'Motacilla alba',u'Motacilla cinerea',u'Motacilla citreola',u'Motacilla flava cinereocapilla',u'Motacilla flava flava',u'Motacilla flava flavissima',u'Motacilla flava iberiae',u'Motacilla flava thunbergi',u'Motacilla flava',u'Muscicapa striata',u'Myadestes genibarbis',u'Myiarchus stolidus',u'Neophron percnopterus',u'Nomonyx dominicus',u'Nucifraga caryocatactes caryocatactes',u'Nucifraga caryocatactes macrorhynchus',u'Nucifraga caryocatactes',u'Numenius tenuirostris',u'Nyctanassa violacea',u'Nycticorax nycticorax',u'Oceanites oceanicus',u'Oenanthe deserti',u'Oenanthe hispanica',u'Oenanthe isabellina',u'Oenanthe leucopyga',u'Oenanthe leucura',u'Oenanthe oenanthe leucorhoa',u'Oenanthe oenanthe oenanthe',u'Oenanthe oenanthe',u'Oenanthe pleschanka',u'Onychoprion anaethetus',u'Onychoprion fuscatus',u'Oriolus oriolus',u'Orthorhyncus cristatus',u'Otis tarda',u'Otus scops',u'Oxyura jamaicensis',u'Oxyura leucocephala',u'Pachyptila belcheri',u'Pachyptila desolata',u'Pachyptila salvini macgillivrayi',u'Pachyptila salvini',u'Pachyptila turtur',u'Pagodroma nivea',u'Pagophila eburnea',u'Pandion haliaetus',u'Panurus biarmicus',u'Parkesia motacilla',u'Parkesia noveboracensis',u'Parus major',u'Passer domesticus domesticus',u'Passer domesticus',u'Passer hispaniolensis',u'Passer montanus',u'Pastor roseus',u'Pelecanoides georgicus',u'Pelecanoides urinatrix exsul',u'Pelecanoides urinatrix',u'Pelecanus crispus',u'Pelecanus occidentalis occidentalis',u'Pelecanus occidentalis',u'Pelecanus onocrotalus',u'Periparus ater',u'Pernis apivorus',u'Petrochelidon pyrrhonota',u'Petronia petronia',u'Phaethon aethereus mesonauta',u'Phaethon aethereus',u'Phaethon lepturus catesbyi',u'Phaethon lepturus',u'Phalacrocorax aristotelis aristotelis',u'Phalacrocorax aristotelis desmarestii',u'Phalacrocorax aristotelis',u'Phalacrocorax auritus',u'Phalacrocorax carbo carbo',u'Phalacrocorax carbo sinensis',u'Phalacrocorax carbo',u'Phalacrocorax melanogenis',u'Phalacrocorax verrucosus',u'Phalaropus fulicarius',u'Phalaropus lobatus',u'Pheucticus ludovicianus',u'Phoebetria fusca',u'Phoebetria palpebrata',u'Phoeniconaias minor',u'Phoenicopterus roseus',u'Phoenicurus moussieri',u'Phoenicurus ochruros',u'Phoenicurus phoenicurus',u'Phylloscopus bonelli',u'Phylloscopus borealis',u'Phylloscopus collybita abietinus',u'Phylloscopus collybita collyba',u'Phylloscopus collybita tristis',u'Phylloscopus collybita',u'Phylloscopus fuscatus',u'Phylloscopus humei',u'Phylloscopus ibericus',u'Phylloscopus inornatus',u'Phylloscopus orientalis',u'Phylloscopus proregulus',u'Phylloscopus schwarzi',u'Phylloscopus sibilatrix',u'Phylloscopus trochiloides',u'Phylloscopus trochilus acredula',u'Phylloscopus trochilus trochilus',u'Phylloscopus trochilus',u'Picoides tridactylus',u'Picus canus',u'Picus viridis viridis',u'Picus viridis',u'Pinicola enucleator',u'Piranga olivacea',u'Platalea ajaja',u'Platalea leucorodia',u'Plectrophenax nivalis',u'Plegadis falcinellus',u'Pluvialis dominica',u'Pluvialis fulva',u'Pluvianus aegyptius',u'Podiceps auritus',u'Podiceps cristatus',u'Podiceps grisegena',u'Podiceps nigricollis',u'Podilymbus podiceps',u'Poecile montanus montanus',u'Poecile montanus rhenanus',u'Poecile montanus',u'Poecile palustris',u'Polysticta stelleri',u'Porphyrio alleni',u'Porphyrio martinicus',u'Porphyrio porphyrio',u'Porzana carolina',u'Porzana porzana',u'Procellaria aequinoctialis',u'Procellaria cinerea',u'Progne dominicensis',u'Protonotaria citrea',u'Prunella atrogularis',u'Prunella collaris',u'Prunella modularis',u'Pterocles alchata',u'Pterodroma feae',u'Pterodroma lessonii',u'Pterodroma macroptera',u'Pterodroma mollis',u'Ptyonoprogne rupestris',u'Puffinus assimilis elegans',u'Puffinus assimilis',u'Puffinus lherminieri',u'Puffinus mauretanicus',u'Puffinus puffinus',u'Puffinus yelkouan',u'Pycnonotus barbatus',u'Pygoscelis adeliae',u'Pygoscelis antarcticus',u'Pygoscelis papua',u'Pyrrhocorax graculus',u'Pyrrhocorax pyrrhocorax',u'Pyrrhula pyrrhula europaea',u'Pyrrhula pyrrhula pyrrhula',u'Pyrrhula pyrrhula',u'Quiscalus lugubris guadeloupensis',u'Quiscalus lugubris',u'Ramphocinclus brachyurus',u'Recurvirostra avosetta',u'Regulus ignicapilla',u'Regulus regulus',u'Remiz pendulinus',u'Rhodostethia rosea',u'Riparia paludicola',u'Riparia riparia',u'Rissa tridactyla',u'Saltator albicollis',u'Saxicola rubetra',u'Saxicola rubicola',u'Scolopax minor',u'Seiurus aurocapilla',u'Serinus canaria',u'Serinus serinus',u'Setophaga americana',u'Setophaga citrina',u'Setophaga coronata',u'Setophaga discolor',u'Setophaga fusca',u'Setophaga pensylvanica',u'Setophaga petechia ruficapilla',u'Setophaga petechia',u'Setophaga ruticilla',u'Setophaga striata',u'Setophaga virens',u'Sibirionetta formosa',u'Sitta europaea',u'Sitta whiteheadi',u'Somateria spectabilis',u'Spatula discors',u'Spinus spinus',u'Steganopus tricolor',u'Stercorarius antarcticus lonnbergi',u'Stercorarius antarcticus',u'Stercorarius longicaudus',u'Stercorarius maccormicki',u'Stercorarius parasiticus',u'Stercorarius pomarinus',u'Stercorarius skua',u'Sterna dougallii',u'Sterna forsteri',u'Sterna hirundo',u'Sterna paradisaea',u'Sterna virgata',u'Sterna vittata',u'Sternula albifrons',u'Streptopelia orientalis',u'Streptopelia senegalensis',u'Strix aluco',u'Sturnus unicolor',u'Sula dactylatra dactylatra',u'Sula dactylatra',u'Sula leucogaster',u'Sula sula',u'Surnia ulula',u'Sylvia atricapilla',u'Sylvia borin',u'Sylvia cantillans albistriata',u'Sylvia cantillans iberiae',u'Sylvia cantillans',u'Sylvia communis',u'Sylvia conspicillata',u'Sylvia curruca',u'Sylvia deserticola',u'Sylvia hortensis',u'Sylvia melanocephala',u'Sylvia nana',u'Sylvia nisoria',u'Sylvia ruppeli',u'Sylvia sarda',u'Sylvia undata dartfordiensis',u'Sylvia undata undata',u'Sylvia undata',u'Syrrhaptes paradoxus',u'Tachybaptus ruficollis',u'Tachymarptis melba',u'Tadorna ferruginea',u'Tadorna tadorna',u'Tetrao urogallus aquitanicus',u'Tetrao urogallus crassirostris',u'Tetrao urogallus',u'Tetrax tetrax',u'Thalassarche cauta',u'Thalassarche chlororhynchos',u'Thalassarche chrysostoma',u'Thalassarche melanophris',u'Thalasseus bengalensis',u'Thalasseus elegans',u'Thalasseus maximus',u'Thalasseus sandvicensis sandvicensis',u'Thalasseus sandvicensis',u'Tiaris bicolor',u'Tichodroma muraria',u'Tringa flavipes',u'Tringa glareola',u'Tringa melanoleuca',u'Tringa ochropus',u'Tringa semipalmata',u'Tringa solitaria',u'Tringa stagnatilis',u'Troglodytes aedon',u'Troglodytes troglodytes',u'Turdus atrogularis',u'Turdus eunomus',u'Turdus naumanni',u'Turdus nudigenis',u'Turdus obscurus',u'Turdus ruficollis',u'Turdus torquatus alpestris',u'Turdus torquatus torquatus',u'Turdus torquatus',u'Tyrannus dominicensis',u'Tyto alba',u'Upupa epops',u'Uria aalge',u'Uria lomvia',u'Vanellus gregarius',u'Vanellus leucurus',u'Vireo altiloquus barbadensis',u'Vireo altiloquus',u'Vireo olivaceus',u'Xanthocephalus xanthocephalus',u'Xema sabini',u'Xenus cinereus',u'Zapornia parva',u'Zapornia pusilla',u'Zonotrichia albicollis',u'Zonotrichia leucophrys',u'Zoothera aurea',u'---Poissons---',u'Acipenser sturio',u'Aetobatus narinari',u'Aetomylaeus maculatus',u'Aetomylaeus vespertilio',u'Alopias pelagicus',u'Alopias superciliosus',u'Alopias vulpinus',u'Alosa alosa',u'Alosa fallax',u'Apristurus albisoma',u'Apristurus longicephalus',u'Apristurus melanoasper',u'Apristurus microps',u'Asymbolus galacticus',u'Aulohalaelurus kanakorum',u'Barbus meridionalis',u'Bathyraja leucomelanos',u'Carcharhinus albimarginatus',u'Carcharhinus amblyrhynchos',u'Carcharhinus brevipinna',u'Carcharhinus falciformis',u'Carcharhinus leucas',u'Carcharhinus limbatus',u'Carcharhinus longimanus',u'Carcharhinus melanopterus',u'Carcharhinus obscurus',u'Carcharhinus plumbeus',u'Carcharhinus sorrah',u'Carcharodon carcharias',u'Centrophorus harrissoni',u'Centrophorus moluccensis',u'Centroscymnus owstonii',u'Centroscymnus plunketi',u'Cephaloscyllium signourum',u'Cirrhigaleus barbifer',u'Cobitis taenia',u'Coregonus lavaretus',u'Dalatias licha',u'Deania quadrispinosa',u'Echinorhinus cookei',u'Esox aquitanicus',u'Esox lucius',u'Etmopterus brachyurus',u'Etmopterus caudistigmus',u'Etmopterus dianthus',u'Etmopterus dislineatus',u'Etmopterus lucifer',u'Etmopterus molleri',u'Etmopterus pseudosqualiolus',u'Etmopterus splendidus',u'Euprotomicrus bispinatus',u'Galeocerdo cuvier',u'Galeus priapus',u'Gollum attenuatus',u'Hemitriakis abdita',u'Hemitriakis japanica',u'Hemitrygon bennettii',u'Hemitrygon fluviorum',u'Heptranchias perlo',u'Hexanchus nakamurai',u'Hexatrygon bickelli',u'Iago garricki',u'Isistius brasiliensis',u'Isurus oxyrinchus',u'Isurus paucus',u'Lampetra fluviatilis',u'Lampetra planeri',u'Leuciscus bearnensis',u'Leuciscus burdigalensis',u'Leuciscus idus',u'Leuciscus leuciscus',u'Leuciscus oxyrrhis',u'Misgurnus fossilis',u'Mobula alfredi',u'Mobula birostris',u'Mobula tarapacana',u'Mustelus manazo',u'Nebrius ferrugineus',u'Negaprion acutidens',u'Neotrygon kuhlii',u'Neotrygon trigonoides',u'Notoraja alisae',u'Notoraja sapphira',u'Odontaspis ferox',u'Odontaspis noronhai',u'Parmaturus albimarginatus',u'Parmaturus albipenis',u'Pastinachus sephen',u'Pateobatis fai',u'Petromyzon marinus',u'Plesiobatis daviesi',u'Prionace glauca',u'Pseudocarcharias kamoharai',u'Rhina ancylostoma',u'Rhincodon typus',u'Rhodeus amarus',u'Rhynchobatus australiae',u'Rhynchobatus djiddensis',u'Salaria fluviatilis',u'Salmo salar',u'Salmo trutta',u'Salvelinus alpinus',u'Sphyrna lewini',u'Sphyrna mokarran',u'Squalus blainville',u'Squalus bucephalus',u'Squalus megalops',u'Squalus melanurus',u'Squalus mitsukurii',u'Stegostoma fasciatum',u'Taeniura lymma',u'Taeniura meyeni',u'Tetronarce macneilli',u'Thymallus ligericus',u'Thymallus thymallus',u'Triaenodon obesus',u'Urogymnus asperrimus',u'Urogymnus granulatus',u'Urolophus deforgesi',u'Urolophus neocaledoniensis',u'Urolophus papilio',u'Urolophus piperatus',u'Zingel asper',u'---Reptiles---',u'Algyroides fitzingeri',u'Anguis fragilis',u'Archaeolacerta bedriagae bedriagae',u'Archaeolacerta bedriagae',u'Bothrops lanceolatus',u'Caretta caretta',u'Chalcides striatus',u'Chelonia mydas',u'Coronella austriaca austriaca',u'Coronella austriaca',u'Coronella girondica',u'Dactyloa roquet',u'Dermochelys coriacea',u'Emys orbicularis galloitalica',u'Emys orbicularis occidentalis',u'Emys orbicularis orbicularis',u'Emys orbicularis',u'Eretmochelys imbricata',u'Erythrolamprus cursor',u'Euleptes europaea',u'Gymnophthalmus pleii pleii',u'Hemidactylus turcicus turcicus',u'Hemidactylus turcicus',u'Hierophis viridiflavus',u'Iguana delicatissima',u'Lacerta agilis agilis',u'Lacerta agilis garzoni',u'Lacerta agilis',u'Lacerta bilineata bilineata',u'Lacerta bilineata',u'Lepidochelys kempii',u'Lepidochelys olivacea',u'Mabuya mabouya',u'Malpolon monspessulanus monspessulanus',u'Malpolon monspessulanus',u'Mauremys leprosa leprosa',u'Mauremys leprosa',u'Natrix helvetica corsa',u'Natrix helvetica helvetica',u'Natrix helvetica',u'Natrix maura',u'Podarcis liolepis cebennensis',u'Podarcis liolepis liolepis',u'Podarcis liolepis sebastiani',u'Podarcis liolepis',u'Podarcis muralis',u'Podarcis siculus',u'Podarcis tiliguerta contii',u'Podarcis tiliguerta eiselti',u'Podarcis tiliguerta granchii',u'Podarcis tiliguerta grandisonae',u'Podarcis tiliguerta maresi',u'Podarcis tiliguerta pardii',u'Podarcis tiliguerta rodulphisimonii',u'Podarcis tiliguerta sammicheli',u'Podarcis tiliguerta tiliguerta',u'Podarcis tiliguerta',u'Psammodromus algirus jeanneae',u'Psammodromus algirus',u'Psammodromus edwarsianus',u'Sphaerodactylus festus',u'Sphaerodactylus vincenti adamas',u'Sphaerodactylus vincenti josephinae',u'Sphaerodactylus vincenti psammius',u'Sphaerodactylus vincenti',u'Tarentola mauritanica mauritanica',u'Tarentola mauritanica',u'Testudo graeca',u'Testudo hermanni',u'Tetracheilostoma bilineatum',u'Thecadactylus rapicauda',u'Timon lepidus lepidus',u'Timon lepidus',u'Vipera aspis aspis',u'Vipera aspis zinnikeri',u'Vipera aspis',u'Vipera berus berus',u'Vipera berus',u'Vipera seoanei seoanei',u'Vipera seoanei',u'Vipera ursinii ursinii',u'Vipera ursinii',u'Zamenis longissimus longissimus',u'Zamenis longissimus',u'Zamenis scalaris',u'Zootoca vivipara louislantzi',u'Zootoca vivipara vivipara',u'Zootoca vivipara',u'---Scléractiniaires---',u'Acropora cervicornis',u'Acropora palmata',u'Acropora prolifera',u'Agaricia grahamae',u'Agaricia lamarcki',u'Agaricia undata',u'Cladocora arbuscula',u'Dendrogyra cylindrus',u'Mycetophyllia aliciae',u'Mycetophyllia danaana',u'Mycetophyllia ferox',u'Mycetophyllia lamarckana',u'Oculina diffusa',u'Orbicella annularis',u'Orbicella faveolata',u'Orbicella franksi']
            self.dlg.faunes.addItems(faunes)
            vlayer = self.dlg.mMapLayerComboBox_2.currentLayer()                           
            self.dlg.mFieldComboBox.setLayer(vlayer)                                     
