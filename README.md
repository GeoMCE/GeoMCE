<h1 style="color: #5e9ca0;">Notice d'utilisation de l'extension G&eacute;oMCE</h1>
<h2 style="color: #2e6c80;">Utilit&eacute; de l'extension :</h2>
<p>L'<a href="https://www.legifrance.gouv.fr/affichTexteArticle.do;jsessionid=B260EC079FBEEED07F572858B35C4D0A.tplgfr29s_1?idArticle=JORFARTI000033016416&amp;cidTexte=JORFTEXT000033016237&amp;dateTexte=29990101&amp;categorieLien=id">article 69</a> de loi sur la reconqu&ecirc;te de la biodiversit&eacute;, de la nature et des paysages du 8 a&ocirc;ut 2016 introduit l'obligation de <em>g&eacute;olocaliser les mesures de compensation des atteintes &agrave; la biodiversit&eacute; d&eacute;finies au I de l'article L. 163-1&nbsp;dans un syst&egrave;me national d'information g&eacute;ographique, accessible au public sur internet</em>. Pour cela, <em>l</em><em>es ma&icirc;tres d'ouvrage fournissent aux services comp&eacute;tents de l'Etat toutes les informations n&eacute;cessaires &agrave; la bonne tenue de cet outil par ces services.</em></p>
<p>Afin de rendre accessible ces donn&eacute;es, le <a href="https://www.ecologique-solidaire.gouv.fr/commissariat-general-au-developpement-durable-cgdd">CGDD</a>, accompagn&eacute; techniquement par le SNUM, est en charge de la mise en place, pour les services de l'Etat, d'un outil capable d'alimenter ce portail : <a href="https://www.ecologique-solidaire.gouv.fr/biodiversite-nouvelle-version-geomce">G&eacute;oMCE</a>.</p>
<p>G&eacute;oMCE peut, sous certaines conditions, importer des fichiers shape (.shp) cr&eacute;&eacute;s depuis un logiciel SIG type Qgis.</p>
<p>L'objectif de cette extension est de r&eacute;aliser les op&eacute;rations n&eacute;cessaires pour modifier les fichiers shape afin de permettre cet import dans l'outil.</p>
<ul>
<li>Plus de renseignement sur la <a href="https://www.ecologique-solidaire.gouv.fr/biodiversite-nouvelle-version-geomce">g&eacute;olocalisation des mesures de compensations et G&eacute;oMCE</a></li>
<li>Les mesures de compensations visibles sur <a href="https://www.geoportail.gouv.fr/donnees/mesures-compensatoires-des-atteintes-a-la-biodiversite">G&eacute;oportail</a></li>
<li>Les mesures de compensations t&eacute;l&eacute;chargeables via <a href="https://www.cdata.cerema.fr/geonetwork/srv/fre/catalog.search#/metadata/48ac3589-499d-4f42-9716-73b4eefef35c">CeremaData</a></li>
<li>La <a href="https://www.ecologique-solidaire.gouv.fr/eviter-reduire-et-compenser-impacts-sur-lenvironnement">s&eacute;quence ERC</a> et le <a title="Ouverture dans une nouvelle fen&ecirc;tre" href="https://www.ecologique-solidaire.gouv.fr/sites/default/files/Th%C3%A9ma%20-%20Guide%20d%E2%80%99aide%20%C3%A0%20la%20d%C3%A9finition%20des%20mesures%20ERC.pdf" target="_blank" rel="external nofollow noopener" data-action="download" data-type="publication" data-label="&Eacute;valuation environnementale : guide d&rsquo;aide &agrave; la d&eacute;finition des mesures ERC_pdf">guide d&rsquo;aide &agrave; la d&eacute;finition des mesures ERC</a></li>
</ul>
<h2 style="color: #2e6c80;">Installation de l'extension dans QGIS 3.x :</h2>
<p>1/ T&eacute;l&eacute;charger la derni&egrave;re version (GeoMCE.zip) sur <a href="https://github.com/GeoMCE/GeoMCE/releases">Github</a> sur votre ordinateur</p>
<p>2/ Dans QGIS, Extension --&gt; Installer/G&eacute;rer des extensions&nbsp;</p>
<p><img src="https://raw.githubusercontent.com/GeoMCE/ressources/master/instal_1.png" alt="" width="866" height="154" /></p>
<p style="color: #2e6c80;"><span style="color: #000000;">3/ Se rendre ensuite dans param&egrave;tres, puis cocher <strong>Afficher les extensions exp&eacute;rimenatles</strong></span></p>
<p style="color: #2e6c80;"><span style="color: #000000;"><img src="https://raw.githubusercontent.com/GeoMCE/ressources/master/instal_2.png" alt="" width="866" height="243" /></span></p>
<p style="color: #2e6c80;"><span style="color: #000000;">4/ Dans l'onglet <strong>Installer depuis un ZIP</strong>, chercher l'extension t&eacute;l&eacute;charg&eacute;e&nbsp;</span></p>
<p style="color: #2e6c80;"><span style="color: #000000;"><img src="https://raw.githubusercontent.com/GeoMCE/ressources/master/instal_3.png" alt="" width="866" height="205" /></span></p>
<p><span style="color: #000000;">Puis cliquer sur <strong>Installer le plugin</strong>.</span></p>
<p><span style="color: #000000;">5/ Une fois l'extension install&eacute;e, elle est accessible depuis le menu <strong>Vecteur</strong></span></p>
<p><span style="color: #000000;"><strong><img src="https://raw.githubusercontent.com/GeoMCE/ressources/master/instal_4.png" alt="" width="866" height="187" /></strong></span></p>
<p><span style="color: #000000;">6/ Vous pouvez cr&eacute;er un lien directement dans la barre d'outil avec un clic droit puis en cochant GeoMCE. L'icone sera alors disponible depuis l'interface principal</span></p>
<p><span style="color: #000000;"><img src="https://raw.githubusercontent.com/GeoMCE/ressources/master/instal_5a.png" alt="" width="866" height="492" /></span></p>
<p><img src="https://raw.githubusercontent.com/GeoMCE/ressources/master/instal_6.png" alt="" width="284" height="110" /></p>
<h2 style="color: #2e6c80;">Utilisation de l'extension :</h2>
<p><span style="color: #000000;">L'extension s'articule autour de 3 onglets :</span></p>
<ol>
<li><span style="color: #000000;">Mise en forme des vecteurs existants</span></li>
<li><span style="color: #000000;">Fonctionnalit&eacute;s suppl&eacute;mentaires</span></li>
<li><span style="color: #000000;">Parm&egrave;tres de l'extension</span></li>
</ol>
<h2><span style="color: #000000;">1/ Mise en forme des vecteurs existants</span></h2>
<p><span style="color: #000000;">Module principal de l'extension. Il permet de mettre en conformit&eacute; la table attributaire d'un fichier shape avec le standard attendu pour un import dans G&eacute;OMCE.</span></p>
<p><img src="https://raw.githubusercontent.com/GeoMCE/ressources/master/onglet_principal.png" alt="" width="866" height="727" /></p>
<h3><span style="color: #000000;">1.1/ Couche &agrave; traiter</span></h3>
<p><span style="color: #000000;"><img src="https://raw.githubusercontent.com/GeoMCE/ressources/master/onglet_principal_1.png" width="866" height="370" /></span></p>
<p><span style="color: #000000;"><strong>Couche &agrave; traiter</strong> : Vecteur (shape) qui va &ecirc;tre modifier afin d'&ecirc;tre compatible avec G&eacute;oMCE.</span></p>
<p><span style="color: #000000;"><strong>Cr&eacute;ation des champs compatibles avec l'outil G&eacute;oMCE :</strong>&nbsp;La table attributaire est effac&eacute;e et remplac&eacute;e par une nouvellle table. Cette op&eacute;ration est <strong>irr&eacute;versible</strong>. Afin de ne pas perdre vos donn&eacute;es, il est pr&eacute;f&eacute;rable de travailler avec des copies de vos shapes.</span></p>
<h3>1.2/ Formulaire de saisie</h3>
<p>Ensemble des donn&eacute;es qui seront &eacute;crites dans la nouvelle table attributaire.</p>
<p><span style="color: #000000;"><img src="https://raw.githubusercontent.com/GeoMCE/ressources/master/onglet_principal_2.png" alt="" width="866" height="459" /></span><span style="color: #ff0000;"><span style="color: #000000;">Les champs marqu&eacute;s d'un</span> *&nbsp;<span style="color: #000000;">sont <strong>obligatoires</strong>. Les autres champs peuvent &ecirc;tre laiss&eacute;s vides.</span></span></p>
<p><span style="color: #ff0000;"><span style="color: #000000;">Les champs marqu&eacute;s d'un <span style="color: #0000ff;">**<span style="color: #000000;"> autorisent une <strong>saisie multiple</strong>.</span></span></span></span></p>
<p><span style="color: #ff0000;"><span style="color: #000000;"><span style="color: #0000ff;"><span style="color: #000000;">L'ensemble des champs textes sont limit&eacute;s &agrave; <strong>254 caract&egrave;res max</strong> (limite due au format shape).</span></span></span></span></p>
<p><span style="color: #ff0000;"><span style="color: #000000;"><span style="color: #0000ff;"><span style="color: #000000;">La saisie de caract&egrave;res sp&eacute;ciaux (&eacute;, &agrave;, &ccedil;,...) est possible toutefois ils seront convertis dans le fichier shape (e, a, c,...).</span></span></span></span></p>
<h3><span style="color: #ff0000;"><span style="color: #000000;"><span style="color: #0000ff;"><span style="color: #000000;">1.3/ Applications des modifications&nbsp;</span></span></span></span></h3>
<p><span style="color: #ff0000;"><span style="color: #000000;"><span style="color: #0000ff;"><span style="color: #000000;"><img src="https://raw.githubusercontent.com/GeoMCE/ressources/master/onglet_principal_3.png" alt="" width="866" height="154" /></span></span></span></span></p>
<p><strong><span style="color: #000000;">Ecrire les nouvelles valeurs</span></strong><span style="color: #000000;"> : Les valeurs du formulaires sont &eacute;crites dans la nouvelle table attributaire. Les modifications sont encore possible.</span></p>
<p><span style="color: #000000;"><strong>Sauvegarder les modifications</strong> : Enregistre les valeurs &eacute;crites. Si une modification d'un ou plusieurs champs est n&eacute;cessaire, il convient de reprendre au point 1.1.</span></p>
<p><span style="color: #000000;"><strong>Afficher la nouvelle table attributaire</strong> : Affiche la table attributaire finale.Permet de v&eacute;rifier si les valeurs sont correctement saisies.</span></p>
<p><strong><span style="color: #000000;">Cr&eacute;er une archive .zip&nbsp;</span></strong><span style="color: #000000;">: Permet d'archiver la couche traiter au format .zip. L'archive est cr&eacute;er dans le dossier d'origine de la couche et porte le nom d&eacute;finit dans le champ <em>Nom de la mesure</em>&nbsp;du formulaire de saisie. Remarque : si le nom d&eacute;finit est d&eacute;passe 10 caract&egrave;res, l'import dans G&eacute;oMCE peut ne pas fonctionner</span></p>
<p><strong><span style="color: #000000;">Ouvrir le dossier </span></strong><span style="color: #000000;">: Ouvre dans l'explorateur Windows le dossier contenant la couche &agrave; traiter.</span></p>
<h2><span style="color: #000000;">2/ Fonctionnalit&eacute;s suupl&eacute;mentaires</span></h2>
<p><span style="color: #000000;">Ensemble des fonctionnalit&eacute;s facultatives de l'extension.</span></p>
<p><span style="color: #000000;"><img src="https://raw.githubusercontent.com/GeoMCE/ressources/master/Fonc_supp.png" alt="" width="866" height="726" /></span></p>
<h3><span style="color: #000000;">2.1/ S&eacute;parer une couche vecteur</span></h3>
<p><span style="color: #ff0000;"><img src="https://raw.githubusercontent.com/GeoMCE/ressources/master/Fonc_supp_1.png" alt="" width="866" height="229" /></span></p>
<p><span style="color: #000000;">Utilisation du traitement natif de QGIS <strong>Split Vector Layer.</strong> Utile si vous disposez d'une couche contenant plusieurs mesures. </span></p>
<p><span style="color: #000000;"><span style="text-decoration: underline;">Ex :</span>&nbsp;une couche nomm&eacute;e <strong>Projet_x.shp</strong> contient les mesures <strong>ME1, MR1, MR2, MC1, MC2, MC3</strong> r&eacute;unit au dans un champ nomm&eacute; "<strong>mesures</strong>". Lorsque cette fonctionnalit&eacute; est utilis&eacute;e,&nbsp;l'extension va cr&eacute;er les couches <strong>ME1.shp, MR1.shp, MR2.shp, MC1.shp, MC2.shp, MC3.shp</strong> puis va les charger dans l'interface de Qgis.&nbsp;</span></p>
<p><span style="color: #000000;"><strong>Couche d'origine</strong> : Vecteur qui va subir le traitement</span></p>
<p><span style="color: #000000;"><strong>Champ s&eacute;parateur</strong> : Champ d'identifiant unique &agrave; l'origine des nouveaux vecteurs (mesure dans l'exemple)</span></p>
<p><span style="color: #000000;"><strong>Dossier d'enregistrement</strong> : Par d&eacute;faut, les nouvelles couches sont cr&eacute;es dans le dossier de la C<em>ouche d'origine</em> mais vous pouvez d&eacute;finir un autre chemin dans ce champ<em>.</em></span></p>
<h3><span style="color: #000000;">2.2/ Fusionner des couches de m&ecirc;mes g&eacute;om&eacute;tries</span></h3>
<p><span style="color: #ff0000;"><img src="https://raw.githubusercontent.com/GeoMCE/ressources/master/Fonc_supp_2.png" alt="" width="866" height="231" /></span></p>
<p><span style="color: #000000;">Utilisation du traitement natif de QGIS <strong>Merge.</strong></span></p>
<p><span style="color: #000000;">G&eacute;oMCE permet l'import de plusieurs mesures en une seule op&eacute;ration. Cette fonctionnalit&eacute; permet donc de fusionner plusieurs mesures g&eacute;n&eacute;r&eacute;es dans l'onglet principale en une seule couche vecteur.</span></p>
<p><span style="color: #000000;"><strong>Couches &agrave; fusionner</strong> : Vecteurs qui vont &ecirc;tre fusionner</span></p>
<p><span style="color: #000000;"><strong>Enregistrer sous</strong> : Dossier d'enregistrement et nom du nouveau vecteur. Ne pas saisir d'extension (ex :&nbsp;C:\Users\cclau\Documents\exemple qgis\Projet_x_fusion)</span></p>
<p><span style="color: #000000;"><strong>Afficher la nouvelle table attributaire</strong> : Affiche la table du vecteur cr&eacute;e par fusion&nbsp;</span></p>
<p><strong><span style="color: #000000;">Cr&eacute;er une archive .zip&nbsp;</span></strong><span style="color: #000000;">: Permet d'archiver le vecteur cr&eacute;e par fusion au format .zip.</span></p>
<p><span style="color: #000000;"><strong>Ouvrir le dossier</strong> :&nbsp;Ouvre dans l'explorateur Windows le dossier contenant le vecteur fusionn&eacute;.</span></p>
<h2><span style="color: #000000;">3/ Param&egrave;tres de l'extension</span></h2>
<p><span style="color: #000000;">Ensemble des param&egrave;tres de l'extension. Ces param&egrave;tres sont sauvegard&eacute;s dans le fichier QGIS.ini du profil utilisateur.</span></p>
<p><span style="color: #000000;"><img src="https://raw.githubusercontent.com/GeoMCE/ressources/master/parametres.png" alt="" width="866" height="722" /></span></p>
<h3>3.1/ Lien vers le fichier COMMUNE.shp</h3>
<p><span style="color: #000000;"><img src="https://raw.githubusercontent.com/GeoMCE/ressources/master/parametres_1.png" alt="" width="866" height="89" /></span></p>
<p><span style="color: #000000;">G&eacute;oMCE permet de renseigner les codes INSEE des communes concern&eacute;es par les mesures. Afin de saisir ces donn&eacute;es depuis l'extension, il faut au pr&eacute;alable t&eacute;l&eacute;charger <a href="https://geoservices.ign.fr/documentation/diffusion/telechargement-donnees-libres.html#admin-express">les donn&eacute;es ADMIN-EXPRESS</a> sur le site de l'IGN puis extraire les fichiers <strong>COMMUNE</strong> (shp, shx, prj, cpg, dbf) sur votre ordinateur. Renseigner ensuite le chemin d'acc&egrave;s du fichier COMMUNE.shp</span></p>
<p><span style="color: #000000;">La sauvegarde de ce param&egrave;tre est automatique.</span></p>
<h3><span style="color: #000000;">3.2/ Transformer automatiquement les points et les lignes en polygones</span></h3>
<p><span style="color: #000000;"><img src="https://raw.githubusercontent.com/GeoMCE/ressources/master/parametres_2.png" alt="" width="866" height="88" /></span></p>
<p>Utilisation du traitement natif de QGIS <strong>Buffer.</strong></p>
<p><strong>Cette fonctionnalit&eacute; est notamment utile pour fusionner l'ensemble des mesures d'un projet en un seul vecteur quelque soit leur type de g&eacute;om&eacute;trie d'origine.</strong></p>
<p>Lorsque ce param&egrave;tre est coch&eacute;, les vecteurs de type points et lignes se voient appliquer un tampon. La distance de ce tampon est param&eacute;trable en fonction du type de g&eacute;om&eacute;trie (de 1 &agrave; 10 m&egrave;tres). Les nouveaux vecteurs sont cr&eacute;es dans le m&ecirc;me dossier que la<strong> couche &agrave; traiter.</strong></p>
<p>La transformation en tampon s'op&egrave;re lorsque l'utilsateur clique sur le bouton <strong>Ecrire les nouvelles valeurs</strong> dans l'onglet <strong>Mise en forme des vecteurs existants</strong>. Le vecteur d'origine est conserv&eacute;. Le vecteur tampon est charg&eacute; automatiquement et est nomm&eacute; <strong>xxx_TAMPON</strong>. L'enregistrement des nouvelles valeurs du formulaire se fait dans la couche &agrave; traiter et dans son tampon.</p>
<h3><span style="color: #000000;">3.3/&nbsp;Option "Extension par d&eacute;faut de la couche vectorielle" configur&eacute;e sur shape</span></h3>
<p><span style="color: #ff0000;"><img src="https://raw.githubusercontent.com/GeoMCE/ressources/master/parametres_3.png" alt="" width="866" height="49" /></span></p>
<p>Par d&eacute;faut, Qgis3.x privil&eacute;gie le format <strong>Geopackage</strong> (.gpkg) au format <strong>shape</strong> (.shp) mais il est possible de configurer ce param&egrave;tre diff&eacute;rement dans les options de QGIS.</p>
<p>L'extension prend en compte ce comportement par d&eacute;faut de QGIS et transforme les .gpkg g&eacute;n&eacute;r&eacute; (split vector layer, merge, buffer) en .shp. Toutefois, si l'utilisateur configure par d&eacute;faut une sortie en shape, il convient de cocher cette case pour que l'extenions fonctionne en cons&eacute;quence.</p>
<p>Ce param&egrave;tre est exp&eacute;riental et peut ne pas fonctionner correctement. <strong>Il est conseill&eacute; de ne pas changer le comportement natif de QGIS concernant les traitements.</strong></p>
<p><strong>4/ Changelog&nbsp;</strong></p>
<p>v1.4 :</p>
<ul>
<li>Refonte et mise &agrave; jour du module d'aide</li>
<li>Possibilit&eacute; de param&eacute;trer la distance des tampons en fonction du type de g&eacute;om&eacute;trie</li>
</ul>
<p>v1.3 :</p>
<ul>
<li>Depuis le menu configuration, il est possible de param&eacute;trer la transformation des vecteurs "point" et "ligne" en polygone (tampon)</li>
<li>Possibilit&eacute; de fusionner plusieurs couches de m&ecirc;me g&eacute;om&eacute;tries</li>
<li>Possibilit&eacute; de zipper la couche fusionn&eacute;e directement depuis l'extension</li>
<li>Possibilit&eacute; d'ouvrir le dossier contenant la couche fusionn&eacute;e directement depuis l'extension</li>
<li>Corrections de bugs et refonte graphique des onglets "fonctionnalit&eacute;s suppl&eacute;mentaires" et "configuration"</li>
</ul>
<p>V1.2 :</p>
<ul>
<li>Ajout d'un panneau configuration. Sauvegarde du chemin de la couche COMMUNE.shp et de la prise en compte de la modification de sortie des couches vecteurs en shape</li>
<li>Toutes les couches ADMIN-EXPRESS sont compatibles quelque soit le mill&eacute;sime et la projetcion choisie</li>
<li>Possibilit&eacute; de zipper la mesure directement depuis l'extension</li>
<li>Possibilit&eacute; d'ouvrir le dossier contenant la mesure directement depuis l'extension</li>
<li>Mineures corrections esth&eacute;tiques</li>
</ul>
<p>V1.1.1 :</p>
<ul>
<li>Gestion des accents dans les zones de textes. Seront remplac&eacute;s automatiquement par leur &eacute;quivalants sans accents</li>
</ul>
<p>V1.1 :</p>
<ul>
<li>Selection multiple possible pour les champs "cible", "faunes" et "flores"</li>
<li>Les .gpkg sont automatiquement en .shp</li>
<li>Mise &agrave; jour du champ "commune" au dernier mill&eacute;sime de l'IGN</li>
</ul>
<p>V1.0 :</p>
<ul>
<li>1&egrave;re version compl&egrave;te pour QGIS 3.x</li>
</ul>
