Changelog :
 - v.0.9 : Compatibilité Qgis3.x
 - v.0.8 : - Refonte graphique : séparation des opérations en onglet pour plus de lisibilité
           - Possibilité de choisir le lieu d'enregistrement du traitement splitlayervector pour plus de commodité
 - v.0.7 : Modification du comportement de la liste déroulante du champ Catégorie
 - v.0.6 : Retouches cosmétiques
 - v.0.5 : (Gros) Nettoyage du code et ajout d'explications des fonctions
 - v.0.4 : Modification de la fonction de séparation des couches : le nom du dossier crée est maintenant horodaté et mentionne également le champ séparateur. Permet de créer un dossier par manipulation
 - v.0.3 : Amélioration de la fonction de suppression des champs existants par itération
 - v.0.2 : Corrections mineurs / Ajout du module d'aide
 - v.0.1 : Version initiale


<h1 style="color: #5e9ca0;">Notice d'utilisation de l'extension G&eacute;oMCE</h1>
<h2 style="color: #2e6c80;">Utilit&eacute; de l'extension :</h2>
<p>L'<a href="https://www.legifrance.gouv.fr/affichTexteArticle.do;jsessionid=B260EC079FBEEED07F572858B35C4D0A.tplgfr29s_1?idArticle=JORFARTI000033016416&amp;cidTexte=JORFTEXT000033016237&amp;dateTexte=29990101&amp;categorieLien=id">article 69</a> de loi sur la reconqu&ecirc;te de la biodiversit&eacute;, de la nature et des paysages du 8 a&ocirc;ut 2016 introduit l'obligation de <em>g&eacute;olocaliser les mesures de compensation des atteintes &agrave; la biodiversit&eacute; d&eacute;finies au I de l'article L. 163-1&nbsp;dans un syst&egrave;me national d'information g&eacute;ographique, accessible au public sur internet</em>. Pour cela, <em>l</em><em>es ma&icirc;tres d'ouvrage fournissent aux services comp&eacute;tents de l'Etat toutes les informations n&eacute;cessaires &agrave; la bonne tenue de cet outil par ces services.</em></p>
<p>Afin de rendre accessible ces donn&eacute;es, le <a href="https://www.ecologique-solidaire.gouv.fr/commissariat-general-au-developpement-durable-cgdd">CGDD</a>, accompagn&eacute; techniquement par le SNUM, est en charge de la mise en place, pour les services de l'Etat, d'un outil capable d'alimenter ce portail : <a href="https://www.ecologique-solidaire.gouv.fr/biodiversite-nouvelle-version-geomce">G&eacute;oMCE</a>.</p>
<p>G&eacute;oMCE peut, sous certaines conditions, importer des fichiers shape (.shp) cr&eacute;&eacute;s depuis un logiciel SIG type Qgis.</p>
<p>L'objectif de cette extension est de r&eacute;aliser les op&eacute;rations n&eacute;cessaires pour modifier les fichiers shape afin de permettre cet import dans l'outil.</p>
<h2 style="color: #2e6c80;">Utilisation de l'extension :</h2>
<p><span style="color: #ff0000;">REMARQUE IMPORTANTE CONCERNANT CE PLUG-IN ET QGIS3.x :&nbsp;</span></p>
<p>Par d&eacute;faut, Qgis3.x favorise le format Geopackage (.gpkg) au format shape (.shp).La bo&icirc;te de traitement est donc configur&eacute;e pour sortir du G&eacute;opackage par d&eacute;faut.</p>
<p> G&eacute;oMCE n'est compatible qu'avec ce format aussi,pour que leplug-in fonctionne correctement, il faut modifier le param&egrave;tre de sortie des traitements.</p>
<p>Pour cela :</p>
<p><strong>Pr&eacute;f&eacute;rences</strong> --&gt; <strong>Options</strong>. La fen&ecirc;tre des options g&eacute;n&eacute;rales de Qgis s'ouvre.</p>
<p>Il faut ensuite se rendre dans "<strong>Traitement</strong>" puis dans "<strong>G&eacute;n&eacute;ral</strong>" et choisir et choisir "<strong>shp</strong>" dans "<strong>Extension par d&eacute;faut de la couche vectorielle en sortie</strong>"</p>
<p>L'extension permet de :</p>
<ol>
<li>Mettre en forme des tables attributaires pour r&eacute;aliser un import de couches cr&eacute;er dans Qgis dans l'outil G&eacute;oMCE</li>
<li>S&eacute;parer une couche shape contenant plusieurs mesures en autant de nouvelles mesures (ex : une couche nomm&eacute;e ligne.shp contient les mesures ME1, MR1, MR2, MC1, MC2, MC3 r&eacute;unit au dans un champ "mesure". Lorsque cette option est utilis&eacute;e, l'extension va cr&eacute;er les couches ME1.shp, MR1.shp, MR2.shp, MC1.shp, MC2.shp, MC3.shp puis va les charger dans l'interface de Qgis)</li>
<li>T&eacute;l&eacute;charger les fichiers Gabarit sous la forme d'un projet Geopackage</li>
</ol>
<p>&nbsp;</p>
<h3>1. Onglet principal : Mise en forme des tables attributaires pour un import vers G&eacute;oMCE</h3>
<p><span style="text-decoration: underline;">ATTENTION</span> : cette partie de l'extension va mettre en forme vos couches. Cela n&eacute;cessite d'&eacute;craser les donn&eacute;es de la table attributaire existante. <strong>Cette op&eacute;ration est irr&eacute;versible!</strong> A l'exception des couches g&eacute;n&eacute;r&eacute;es pr&eacute;c&eacute;demment, il convient de travailler avec des copies plut&ocirc;t que le shape original</p>
<ol>
<li>Selectionner la couche &agrave; traiter puis appuyer sur le bouton "Cr&eacute;ation des champs compatibles avec l'outil G&eacute;oMCE"<br /><img src="https://nsa40.casimages.com/img/2020/04/14/200414123540261902.png" alt="" width="868" height="60" /><br />L'op&eacute;ration va donc supprimer les champs existants et cr&eacute;er les nouveaux champs : id, nom, categorie, cible, descriptio, decision, refei, duree, unit&eacute;, modalite et communes. La couche est bascul&eacute;e en mode &eacute;dition et les champs sont vides.<br /><img src="https://nsa40.casimages.com/img/2020/04/14/200414124001798954.png" alt="" width="1142" height="270" /><br /><br /></li>
<li>Vous pouvez saisir les informations que vous souhaitez voir figurer dans vos champs<br /><img src="https://nsa40.casimages.com/img/2020/04/14/200414014113823394.png" alt="" width="870" height="247" /><br />Remarques : <br />- La plupart des champs sont limit&eacute;s &agrave; 254 caract&egrave;res (limitation propre aux fichiers shape)<br />- Pour le champ Cat&eacute;gorie, se reporter au <a href="https://www.ecologique-solidaire.gouv.fr/sites/default/files/Th%C3%A9ma%20-%20Guide%20d%E2%80%99aide%20%C3%A0%20la%20d%C3%A9finition%20des%20mesures%20ERC.pdf"> guide d&rsquo;aide &agrave; la d&eacute;finition des mesures ERC</a><br />- Ne pas utiliser de caract&egrave;res sp&eacute;ciaux (&eacute;, &egrave;, &agrave;, ...)</li>
<li>Le champ "communes" n&eacute;cessite d'utiliser les codes INSEE s&eacute;par&eacute;s par un | (Alt Gr + 6). L'extension vous permet de r&eacute;cup&eacute;rer automatiquement ces informations ou de laisser le champ vide. Pour r&eacute;cup&eacute;rer les codes INSEE, il faut au pr&eacute;alable t&eacute;l&eacute;charger et enregistrer dans votre ordinateur la couche COMMUNE.shp du fichier suivant : <a href="ftp://Admin_Express_ext:Dahnoh0eigheeFok@ftp3.ign.fr/ADMIN-EXPRESS-COG_2-0__SHP__FRA_L93_2019-09-24.7z.001">ADMIN-EXPRESS-COG &eacute;dition 2019 par territoire</a> (donn&eacute;e IGN gratuite). <img src="https://nsa40.casimages.com/img/2020/04/14/200414014113487745.png" /></li>
<li>Une fois vos informations saisies, cliquer sur "Ecrire les nouvelles valeurs" puis "Sauvegarder les modifications". Vous pouvez v&eacute;rifier votre nouvelle table attributaire en cliquant sur "Afficher la nouvelle table attributaire"<br /><img src="https://nsa40.casimages.com/img/2020/04/14/200414014113568105.png" alt="" width="867" height="44" /></li>
<li>R&eacute;sultat attendu :<img src="https://nsa40.casimages.com/img/2020/04/14/200414020834903578.png" alt="" width="1122" height="142" /></li>
<li>Il ne reste plus qu'&agrave; zipper les shapes pr&eacute;sents dans le dossier C:/GeoMCE/nom_de_couche_d_origine puis &agrave; les importer dans G&eacute;oMCE.</li>
</ol>
<h3>2. Onglet "Fonctionnalit&eacute;s suppl&eacute;mentaires S&eacute;paration d'une couche en plusieurs couches :</h3>
<p>1/ La premi&egrave;re partie de cet onglet permet, si n&eacute;cessaire, de r&eacute;aliser l'op&eacute;ration "<strong>S&eacute;parer une couche vecteur</strong>" direcetement depuis le plugin sans avoir &agrave; le lancer par ailleurs</p>
<p>Soit une couche nomm&eacute;e "ligne.shp" qui contient les entit&eacute;s suivantes : ME1, MR1, MR2, MC1, MC2, MC3 r&eacute;unit dans un champ "mesure"</p>
<p><img src="https://nsa40.casimages.com/img/2020/04/14/200414121423203360.png" width="1000" height="484" /></p>
<p>Choissir le dossier o&ugrave; enregistrer les nouvelles couches puis s&eacute;lectionner "ligne" comme couche &agrave; s&eacute;parer et "mesure" comme champ s&eacute;parateur ...</p>
<p><img src="https://nsa40.casimages.com/img/2020/04/14/200414121423141611.png" alt="" width="872" height="93" /></p>
<p>... on va automatiquement cr&eacute;er autant de chouches qu'il y a d'entit&eacute; dans ce champ pr&eacute;cis dans le dossier voulu. Ces nouvelles couches sont automatiquement charg&eacute;es dans l'interface de Qgis.</p>
<p><img src="https://nsa40.casimages.com/img/2020/04/14/200414121423455452.png" alt="" width="1004" height="490" /></p>
<p></p>
<p style="color: #2e6c80;"><img src="https://nsa40.casimages.com/img/2020/04/14/200414122334248749.png" alt="" width="279" height="287" /></p>
<p>Il est ensuite possible de les mettre en forme depuis l'onglet principal.</p>
<p>2/ Il est possible de t&eacute;l&eacute;charger les fichiers Gabarit pr&eacute; configur&eacute;es directement depuis cet onglet.</p>
<p>L'<a href="https://github.com/GeoMCE/Fichier-Gabarit/archive/v1.0.zip">archive</a> contient un projet nomm&eacute; Projet-Gabarit_GeoMCE.qgs, qui, une fois ouvert dans Qgis, va ouvrir 3 vecteurs (polygone, ligne et point) pr&eacute;configur&eacute;es. Il faut basculer la couche d&eacute;sir&eacute;e en mode Edition, tracer l'entit&eacute; d&eacute;sir&eacute;e puis saisir les informations une fois la saisie finie.</p>
<p>Remarque : ce projet .qgs ne peut &ecirc;tre ouvert lorsqu'un autre projet est en cours d'utilisation. Il lance un nouveau projet &agrave; chaque session</p>
