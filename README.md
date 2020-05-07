Changelog :
 - v.0.9 : Compatibilité Qgis3.x (voir Branch Master)
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
<p>L'extension permet 2 choses :</p>
<ol>
<li>S&eacute;parer une couche shape contenant plusieurs mesures en autant de nouvelles mesures (ex : une couche nomm&eacute;e ligne.shp contient les mesures ME1, MR1, MR2, MC1, MC2, MC3 r&eacute;unit au dans un champ "mesure". Lorsque cette option est utilis&eacute;e, l'extension va cr&eacute;er les couches ME1.shp, MR1.shp, MR2.shp, MC1.shp, MC2.shp, MC3.shp puis va les charger dans l'interface de Qgis)</li>
<li>Mise en forme de la table attributaire pour r&eacute;aliser l'import dans QGis. L'objectif est donc de cr&eacute;er une table attributaire compatible avec un import dans G&eacute;oMCE avec la possibilit&eacute; de saisir les champs n&eacute;cessaires</li>
</ol>
<h3>1. S&eacute;paration d'une couche en plusieurs couches :</h3>
<p>Soit une couche nomm&eacute;e "ligne.shp" qui contient les entit&eacute;s suivantes : ME1, MR1, MR2, MC1, MC2, MC3 r&eacute;unit dans un champ "mesure"</p>
<p><img src="https://nsa40.casimages.com/img/2020/04/14/200414121423203360.png" width="1000" height="484" /></p>
<p>En s&eacute;lectionnant "ligne" comme couhe &agrave; s&eacute;parer et "mesure" comme champ s&eacute;parateur ...</p>
<p><img src="https://nsa40.casimages.com/img/2020/04/14/200414121423141611.png" alt="" width="872" height="93" /></p>
<p>... on va automatiquement cr&eacute;er autant de chouches qu'il y a d'entit&eacute; dans ce champ pr&eacute;cis.</p>
<p><img src="https://nsa40.casimages.com/img/2020/04/14/200414121423455452.png" alt="" width="1004" height="490" /></p>
<p>Les nouveaux shapes sont automatiquement cr&eacute;&eacute;s dans le dossier C:/GeoMCE/date_nom_de_couche_d'origine_nom_champ_separateur de votre ordinateur (dans ce cas pr&eacute;cis : C:/GeoMCE/2020-30-05_15-04_ligne_mesure)</p>
<p style="color: #2e6c80;"><img src="https://nsa40.casimages.com/img/2020/04/14/200414122334248749.png" alt="" width="279" height="287" /></p>
<p>&nbsp;</p>
<h3>2. Mise en forme des tables attributaires pour un import vers G&eacute;oMCE :</h3>
<p><span style="text-decoration: underline;">ATTENTION</span> : cette partie de l'extension va mettre en forme vos couches. Cela n&eacute;cessite d'&eacute;craser les donn&eacute;es de la table attributaire existante. <strong>Cette op&eacute;ration est irr&eacute;versible!</strong> A l'exception des couches g&eacute;n&eacute;r&eacute;es pr&eacute;c&eacute;demment, il convient de travailler avec des copies plut&ocirc;t que le shape original</p>
<ol>
<li>Selectionner la couche &agrave; traiter puis appuyer sur le bouton "Cr&eacute;ation des champs compatibles avec l'outil G&eacute;oMCE"<br /> <img src="https://nsa40.casimages.com/img/2020/04/14/200414123540261902.png" alt="" width="868" height="60" /><br /> L'op&eacute;ration va donc supprimer les champs existants et cr&eacute;er les nouveaux champs : id, nom, categorie, cible, descriptio, decision, refei, duree, unit&eacute;, modalite et communes. La couche est bascul&eacute;e en mode &eacute;dition et les champs sont vides.<br /> <img src="https://nsa40.casimages.com/img/2020/04/14/200414124001798954.png" alt="" width="1142" height="270" /><br /><br /></li>
<li>Vous pouvez saisir les informations que vous souhaitez voir figurer dans vos champs<br /> <img src="https://nsa40.casimages.com/img/2020/04/14/200414014113823394.png" alt="" width="870" height="247" /><br /> Remarques : <br /> - La plupart des champs sont limit&eacute;s &agrave; 254 caract&egrave;res (limitation propre aux fichiers shape)<br /> - Pour le champ Cat&eacute;gorie, se reporter au <a href="https://www.ecologique-solidaire.gouv.fr/sites/default/files/Th%C3%A9ma%20-%20Guide%20d%E2%80%99aide%20%C3%A0%20la%20d%C3%A9finition%20des%20mesures%20ERC.pdf"> guide d&rsquo;aide &agrave; la d&eacute;finition des mesures ERC</a><br />- Ne pas utiliser de caract&egrave;res sp&eacute;ciaux (&eacute;, &egrave;, &agrave;, ...)</li>
<li>Le champ "communes" n&eacute;cessite d'utiliser les codes INSEE s&eacute;par&eacute;s par un | (Alt Gr + 6). L'extension vous permet de r&eacute;cup&eacute;rer automatiquement ces informations ou de laisser le champ vide. Pour r&eacute;cup&eacute;rer les codes INSEE, il faut au pr&eacute;alable t&eacute;l&eacute;charger et enregistrer dans votre ordinateur la couche COMMUNE.shp du fichier suivant : <a href="ftp://Admin_Express_ext:Dahnoh0eigheeFok@ftp3.ign.fr/ADMIN-EXPRESS-COG_2-0__SHP__FRA_L93_2019-09-24.7z.001">ADMIN-EXPRESS-COG &eacute;dition 2019 par territoire</a> (donn&eacute;e IGN gratuite). <img src="https://nsa40.casimages.com/img/2020/04/14/200414014113487745.png" /></li>
<li>Une fois vos informations saisies, cliquer sur "Ecrire les nouvelles valeurs" puis "Sauvegarder les modifications". Vous pouvez v&eacute;rifier votre nouvelle table attributaire en cliquant sur "Afficher la nouvelle table attributaire"<br /><img src="https://nsa40.casimages.com/img/2020/04/14/200414014113568105.png" alt="" width="867" height="44" /></li>
<li>R&eacute;sultat attendu :<img src="https://nsa40.casimages.com/img/2020/04/14/200414020834903578.png" alt="" width="1122" height="142" /></li>
<li>Il ne reste plus qu'&agrave; zipper les shapes pr&eacute;sents dans le dossier C:/GeoMCE/nom_de_couche_d_origine puis &agrave; les importer dans G&eacute;oMCE.</li>
