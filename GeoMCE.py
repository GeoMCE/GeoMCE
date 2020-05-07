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
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from qgis.PyQt.QtGui import *
from qgis.utils import *
from aboutdialog import AboutDialog
from processing.tools.vector import VectorWriter
# Initialize Qt resources from file resources.py
import resources, os, processing, fnmatch, sys, glob
# Import the code for the dialog
from GeoMCE_dialog import GeoMCEDialog
import os.path
import datetime



class GeoMCE:
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
        self.dlg.mFieldComboBox.clear()
        self.dlg.mMapLayerComboBox.clear()
        self.dlg.mMapLayerComboBox_2.clear()

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

#fonctions personnalisees-------------------------------------------------------------------------------------------------------------
#fonctions generale-------------------------------------------------------------------------------------------------------------------
 #verification si couche vecteur sont chargees
    def checkvector(self):
        count = 0
        for name, layer in QgsMapLayerRegistry.instance().mapLayers().iteritems():
            if layer.type() == QgsMapLayer.VectorLayer:
                count += 1
        return count

    def refresh_layers(self):
        for layer in qgis.utils.iface.mapCanvas().layers():
            layer.triggerRepaint()
            
# fonction relative a splitlayer vector-----------------------------------------------------------------------------------------------
 #chemin d enregistrement du traitement splitvectorlayer 
    def select_save_folder(self):
        qfd_1 = QFileDialog()
        title_1 = u'T\'enregistre ça où?'
        path_1 = ""
        filename = QFileDialog.getExistingDirectory(qfd_1, title_1, path_1)
        self.dlg.enregistrement.setText(filename) 
 
 #on recupere le chemin du dossier d enregistrement du traitement pour plus tard
    def get_enregistrement(self):
        new_enregistrement = self.dlg.enregistrement.text()
        return new_enregistrement

 #choix de la couche a pour traitement splitlayervector
    def chooselayer(self):
        self.dlg.mMapLayerComboBox_2.clear()
        self.dlg.mMapLayerComboBox.clear()
        self.dlg.mFieldComboBox.clear()        
        layerlist=[]
        slist=[]
        layers = self.iface.legendInterface().layers()
        for layer in layers:
            layerType = layer.type()
            if layerType == QgsMapLayer.VectorLayer:
                self.dlg.mMapLayerComboBox_2.addItem(layer.name())
        self.set_select_attributes()

 #choix du champ separateur pour fonction splitlayervector
    def set_select_attributes(self):
        self.dlg.mMapLayerComboBox_2.clear()
        self.dlg.mFieldComboBox.clear()
        if self.dlg.mMapLayerComboBox.currentText() != "":
            layername = self.dlg.mMapLayerComboBox.currentText()
            for name, selectlayer in QgsMapLayerRegistry.instance().mapLayers().iteritems():
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
               
        #separation de la couche active par le champ defini au debut du script et enregistrement dans le dossier c:/GeoMCE/nom_de_la_couche_d_origine
        sep = processing.runalg("qgis:splitvectorlayer", self.dlg.mMapLayerComboBox_2.currentText(), self.dlg.mFieldComboBox.currentText(), p)

        # chargement de toutes les couches issues de la separation contenu dans le dossier c:/geomce/nom_de_la_couche_d_origine
        def find_files(directory, pattern, only_root_directory):
            for root, dirs, files in os.walk(directory):
                for basename in files:
                    if fnmatch.fnmatch(basename.lower(), pattern):
                        filename = os.path.join(root, basename)
                        yield filename
                if (only_root_directory):
                    break

        count = 0
        for src_file in find_files(p, '*.shp', True):
            (head, tail) = os.path.split(src_file)
            (name, ext) = os.path.splitext(tail)
            vlayer = iface.addVectorLayer(src_file, name, "ogr")
        output = count
        self.dlg.mFieldComboBox.clear()
        self.dlg.mMapLayerComboBox_2.clear()

#fonctions assurant la mise en forme des couches pour un import dans GeoMCE---------------------------------------------------------------
 #choix de la couche a traiter
    def chooselayer_2(self):
        self.dlg.mMapLayerComboBox.clear()
        self.dlg.txtFeedBack.clear()
        Layers = self.iface.legendInterface().layers()
        Layer_list = []
        for layer in Layers:
            Layer_list.append (layer.name())
            self.dlg.mMapLayerComboBox.addItems(Layer_list)
        self.set_select_attributes()

 #on efface tous les champs existants et on cree ceux indispensable pour un import dans GeoMCE        
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
            jeanpaul = jean + paul
        layer.dataProvider().deleteAttributes(jeanpaul)

        #... et creation des nouveaux champs compatibles avec un import dans GeoMCE (sur v2.2.6)  
        layer.dataProvider().addAttributes(
                    [QgsField("id", QVariant.Int,'Integer64',10,0),
                    QgsField("nom", QVariant.String,'String',254,0),
                    QgsField("categorie", QVariant.String,'String',7,0),
                    QgsField("cible", QVariant.String,'String',100,0),
                    QgsField("descriptio", QVariant.String,'String',254,0),
                    QgsField("decision", QVariant.String,'String',254,0),
                    QgsField("refei", QVariant.String,'String',254,0),
                    QgsField("duree", QVariant.String,'String',25,0),
                    QgsField("unite", QVariant.String,'String',25,0),
                    QgsField("modalite",QVariant.String, 'String', 50,0),
                    QgsField("communes", QVariant.String,'String',220,0)])         
        layer.updateFields()
        layer.selectAll()
        return
         
 #les champs de saisi texte et listes deroulantes    
    def get_new_nom(self):
        new_nom = self.dlg.nom.text()
        return new_nom
    def get_description(self):
        new_val_description = self.dlg.description.text()
        return new_val_description
    def get_decision(self):
        new_val_decicision = self.dlg.decision.text()
        return new_val_decicision
    def get_refei(self):
        new_val_refei = self.dlg.refei.text()
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
        new_val_communes = self.dlg.communes.text()
        return new_val_communes
 
 #on va chercher le fichier commune.shp pour recuperer le code insee
    def select_output_file(self):
        qfd = QFileDialog()
        title = u'Il est où ton fichier Commune.shp?'
        path = ""
        filename = QFileDialog.getOpenFileName(qfd, title, path)
        self.dlg.communes.setText(filename)

 #selection des toutes les entites de la couche
    def select_all(self):
        self.selectall = 0
        layername = self.dlg.mMapLayerComboBox.currentLayer()
        for name, selectlayer in QgsMapLayerRegistry.instance().mapLayers().iteritems():
            if selectlayer.name() == layername:
                selectlayer.setSelectedFeatures([])
                selectlayer.invertSelection()
                self.selectall = 1

 #application des nouvelles valeurs dans la nouvelle table attributaire
    def change_to_any(self):
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

        #permet de recuperer le code INSEE des communes concernes par la mesure. Necessite de changer les champs compare_field_index, concat_field_index et new_field_index en fonction du shape commune.
        def codeinsee():
            #ici se trouve le chemin vers couche contenant toutes les communes de votre region. 
            self.dlg.mMapLayerComboBox.clear()
            layer5 = self.dlg.mMapLayerComboBox.currentLayer()
            val10 = self.get_communes()
            if val10 != "" :
                layer_communes_region = QgsVectorLayer(val10, "communes", "ogr")
                #application d une extraction par localisation
                extraction = processing.runalg('qgis:extractbylocation', layer_communes_region, layer5, u'intersects',0, None)
                layer_extraction = QgsVectorLayer(extraction['OUTPUT'],"extraction","ogr")
                layer_extraction.startEditing()
                #les chiffres doivent correspondre a des champ identiques de votre couche commune. ex : 5 --> nom_dept; 3-->code_insee a recuperer; 6--> nom_reg
                compare_field_index = 5
                concat_field_index = 2
                new_field_index = 4
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
            layer.changeAttributeValue(feat.id(),10, codeinsee())

 #sauvegarde des elements saisis dans la table attributaire
    def save_edits(self):
        self.saved = False
        layername = self.dlg.mMapLayerComboBox.currentText()
        for name, selectlayer in QgsMapLayerRegistry.instance().mapLayers().iteritems():
            if selectlayer.name() == layername:
                if (selectlayer.isEditable()):
                    selectlayer.commitChanges()
                    self.saved = True
                    self.countchange = 0
        return self.saved

 #on deselectionne les entites modifies 
    def clearselection(self):
        clearlist = []
        for name, selectlayer in QgsMapLayerRegistry.instance().mapLayers().iteritems():
            if selectlayer.type() == QgsMapLayer.VectorLayer:
                selectlayer.setSelectedFeatures(clearlist)

 #permet d afficher la table attributaire de la couche qui a ete traiter
    def show_table(self):
        #shows attribute table of chosen layer 
        table_layer=self.dlg.mMapLayerComboBox.currentText()
        for name, selectlayer in QgsMapLayerRegistry.instance().mapLayers().iteritems():
            if selectlayer.name() == table_layer:
                show_layer_t = selectlayer
                self.iface.showAttributeTable(show_layer_t)

 #on ferme le plugin
    def exit(self):
        self.clearselection()
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
        self.dlg.communes.clear()

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
            self.iface.messageBar().pushMessage(u'GéoMCE',u'J\'peux pas bosser sans couches vecteurs!', level=QgsMessageBar.CRITICAL, duration=3)
            return
        else:
            self.dlg.show()
            self.chooselayer()
            QObject.connect(self.dlg.mMapLayerComboBox_2, SIGNAL("currentIndexChanged(QString)"), self.set_select_attributes)
            QObject.connect(self.dlg.mMapLayerComboBox_2, SIGNAL("currentIndexChanged(QString)"), self.clearselection)
            QObject.connect(self.dlg.mMapLayerComboBox, SIGNAL("currentIndexChanged(QString)"), self.set_select_attributes)
            QObject.connect(self.dlg.mMapLayerComboBox, SIGNAL("currentIndexChanged(QString)"), self.clearselection)
            QObject.connect(self.dlg.save, SIGNAL("clicked()"), self.save_edits)
            QObject.connect(self.dlg.show_t, SIGNAL("clicked()"), self.show_table)
            QObject.connect(self.dlg.create_new_field, SIGNAL("clicked()"), self.newfield_connect)
            QObject.connect(self.dlg.create_new_field_2, SIGNAL("clicked()"), self.newfield_connect_2)
            QObject.connect(self.dlg.change_another, SIGNAL("clicked()"), self.change_to_any)
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
            vlayer = self.dlg.mMapLayerComboBox_2.currentLayer()                           
            self.dlg.mFieldComboBox.setLayer(vlayer)                                     
            self.dlg.pushButton.clicked.connect(self.select_output_file)
            self.dlg.pushButton_3.clicked.connect(self.select_save_folder)
            QObject.connect(self.dlg.Exit, SIGNAL("clicked()"), self.exit)
            QObject.connect(self.dlg.Exit_2, SIGNAL("clicked()"), self.exit)
            #----boite de dialogue Aide - A propos
            QObject.connect(self.dlg.about, SIGNAL("clicked()"), self.doabout)
