{FIRST_PAGE_HEADER_START}
{{ reference_acte }}
{{ initiales_notaire }}/

Le {{ date_acte.day }} {{ date_acte.month|mois_en_lettres }} {{ date_acte.year }}
{FIRST_PAGE_HEADER_END}

**DONATION-PARTAGE**
**Par {{ donateur_1.civilite }} {{ donateur_1.prenom }} {{ donateur_1.nom|upper }}**
{% if donateur_2 %}**Et {{ donateur_2.civilite }} {{ donateur_2.prenom }} {{ donateur_2.nom_naissance|upper }} née {{ donateur_2.nom_naissance|upper }}**{% endif %}
**Au profit de leurs {{ nombre_enfants_lettres }} enfants**
***************************************************************

**L'AN {{ date_acte.year|nombre_en_lettres|upper }}, LE {{ date_acte.day|jour_en_lettres|upper }} {{ date_acte.month|mois_en_lettres|upper }}**
**À {{ lieu_signature.ville|upper }} ({{ lieu_signature.code_postal }}), {{ lieu_signature.adresse }},**
**{{ notaire.civilite }} {{ notaire.prenom }} {{ notaire.nom|upper }}, Notaire au sein de la {{ notaire.type_societe }} dénommée « {{ notaire.nom_societe }} » titulaire d'un Office notarial situé à {{ notaire.office.ville|upper }} ({{ notaire.office.departement }}), {{ notaire.office.adresse }}, identifié sous le numéro CRPCEN {{ notaire.crpcen }},**

**EST ETABLIE LA PRESENTE DONATION-PARTAGE**

## IDENTIFICATION DES PARTIES

### DONATEURS

{{ donateur_1.civilite }} {{ donateur_1.prenom }} {{ donateur_1.deuxieme_prenom|default('') }} {{ donateur_1.nom|upper }}, {{ donateur_1.profession }}, et {{ donateur_2.civilite }} {{ donateur_2.prenom }} {{ donateur_2.deuxieme_prenom|default('') }} {{ donateur_2.troisieme_prenom|default('') }} {{ donateur_2.nom_naissance|upper }}, {{ donateur_2.profession }}, demeurant ensemble à {{ donateur_1.adresse.ville|upper }} ({{ donateur_1.adresse.code_postal }}) {{ donateur_1.adresse.numero }} {{ donateur_1.adresse.voie }}.

{{ donateur_1.civilite_court }} est né{{ 'e' if donateur_1.civilite == 'Madame' else '' }} à {{ donateur_1.naissance.ville|upper }} le {{ donateur_1.naissance.date.day|jour_en_lettres }} {{ donateur_1.naissance.date.month|mois_en_lettres }} {{ donateur_1.naissance.date.year }},

{{ donateur_2.civilite_court }} est né{{ 'e' if donateur_2.civilite == 'Madame' else '' }} à {{ donateur_2.naissance.ville|upper }} le {{ donateur_2.naissance.date.day|jour_en_lettres }} {{ donateur_2.naissance.date.month|mois_en_lettres }} {{ donateur_2.naissance.date.year }}.

Mariés à la mairie de {{ mariage.ville|upper }} ({{ mariage.code_postal }}) le {{ mariage.date.day|jour_en_lettres }} {{ mariage.date.month|mois_en_lettres }} {{ mariage.date.year }} sous le régime de {{ mariage.regime }}, tel qu'il est défini par les articles {{ mariage.articles_code_civil }} du Code civil, en vertu du contrat de mariage reçu par {{ mariage.notaire.civilite }} {{ mariage.notaire.prenom }} {{ mariage.notaire.nom|upper }}, notaire à {{ mariage.notaire.ville|upper }} ({{ mariage.notaire.code_postal }}), le {{ mariage.contrat.date.day|jour_en_lettres }} {{ mariage.contrat.date.month|mois_en_lettres }} {{ mariage.contrat.date.year }}.

Ce régime matrimonial n'a pas fait l'objet de modification.

{{ donateur_1.civilite_court }} est de nationalité {{ donateur_1.nationalite }}.
{{ donateur_2.civilite_court }} est de nationalité {{ donateur_2.nationalite }}.

Résidents au sens de la réglementation fiscale.

**sont présents à l'acte.**

Ci-après figurant sous le nom le **"DONATEUR"**.

### DONATAIRES

{% for donataire in donataires %}
**{{ loop.index }}°) {{ donataire.civilite }} {{ donataire.prenom }} {{ donataire.deuxieme_prenom|default('') }} {{ donataire.troisieme_prenom|default('') }} {{ donataire.nom|upper }}**, {{ donataire.profession }}, demeurant à {{ donataire.adresse.ville|upper }} ({{ donataire.adresse.code_postal }}) {{ donataire.adresse.numero }} {{ donataire.adresse.voie }}.

Né{{ 'e' if donataire.civilite == 'Madame' else '' }} à {{ donataire.naissance.ville|upper }} le {{ donataire.naissance.date.day|jour_en_lettres }} {{ donataire.naissance.date.month|mois_en_lettres }} {{ donataire.naissance.date.year }}.

{{ donataire.situation_familiale }}.

{% if donataire.situation_familiale == 'Célibataire' %}Non lié{{ 'e' if donataire.civilite == 'Madame' else '' }} par un pacte civil de solidarité.{% endif %}

De nationalité {{ donataire.nationalite }}.

Résident{{ 'e' if donataire.civilite == 'Madame' else '' }} au sens de la réglementation fiscale.

**est présent{{ 'e' if donataire.civilite == 'Madame' else '' }} à l'acte.**

{% endfor %}

Ci-après figurant sous le nom le **"DONATAIRE"** ou les **"DONATAIRES"**.

**SEULS ENFANTS** du **"DONATEUR"** et ses seuls présomptifs héritiers.

{ELEMENTS_PREALABLES_BOX_START}
## ELEMENTS PREALABLES

### TERMINOLOGIE

Le mot **"DONATEUR"** sera employé au masculin singulier et désignera indifféremment toute personne physique homme ou femme, qu'il n'y en ait qu'une ou plusieurs.

Les mots **"DONATAIRE"** ou **"DONATAIRES"** désigneront indifféremment un ou plusieurs attributaires.

### DECLARATIONS DES PARTIES

Les parties déclarent :

• Que leur état-civil et leur domicile sont ceux indiqués aux présentes.

• Qu'elles ne font l'objet d'aucune mesure ou procédure susceptible de restreindre leur capacité civile.

• Qu'elles ne sont pas et n'ont jamais été en état de faillite personnelle, liquidation judiciaire, règlement judiciaire, redressement judiciaire ou cessation de paiement et spécialement pour le DONATEUR ne pas être soumis à une procédure de rétablissement personnel.

• Qu'elles ont connaissance des dispositions de l'article L 132-8 du Code de l'action sociale et des familles relatives à la récupération des aides sociales, si le DONATEUR a demandé des aides sociales récupérables dans les dix années précédant la présente donation, ou s'il devait en demander dans les dix ans suivant la présente donation, l'Etat ou le département bénéficierait d'un droit à récupération à l'encontre des DONATAIRES.

### DOCUMENTS RELATIFS A LA CAPACITE ET A LA QUALITE DES PARTIES

Les pièces suivantes ont été produites à l'appui des déclarations des parties sur leur capacité :

{% for donateur in [donateur_1, donateur_2] %}
**Concernant {{ donateur.civilite }} {{ donateur.prenom }} {{ donateur.nom|upper }} :**
Extrait d'acte de naissance.
Extrait d'acte de mariage.
Carte nationale d'identité.
Compte rendu de l'interrogation du site bodacc.fr.

{% endfor %}

{% for donataire in donataires %}
**Concernant {{ donataire.civilite }} {{ donataire.prenom }} {{ donataire.nom|upper }}:**
Extrait d'acte de naissance.
Carte nationale d'identité.
Compte rendu de l'interrogation du site bodacc.fr.

{% endfor %}

{% if societe %}
**Concernant la société {{ societe.denomination }}**
Extrait Kbis
Certificat de non-faillite
{% endif %}

Ces documents ne révèlent aucun empêchement des parties à la signature des présentes.

Conformément à la loi n°78-17 du 6 janvier 1978 relative à l'informatique, aux fichiers et aux libertés, dite loi Informatique et Libertés, au Règlement Général sur la Protection des Données (RGPD) du 27 avril 2016 entré en application le 25 mai 2018 et à la Circulaire du Conseil Supérieur du Notariat en date du 12 mai 2022, les documents relatifs à la capacité des parties contenant des données à caractère personnel ne seront pas annexés aux présentes.
{ELEMENTS_PREALABLES_BOX_END}

{EXPOSE_PREALABLE_BOX_START}
## EXPOSE PREALABLE
{EXPOSE_PREALABLE_BOX_END}

Les DONATEURS ont pour seuls présomptifs héritiers les DONATAIRES.

En vue de prévenir toutes difficultés que pourrait faire naître, après leurs décès, le partage de certains de leurs biens entre eux, les DONATEURS leur ont proposé, ce qu'ils ont accepté, de leur faire, dès à présent, donation à titre de partage anticipé desdits biens.

{% if donation_anterieure %}
{DONATION_ANTERIEURE_BOX_START}
### I- DONATION ANTERIEURE NON INCORPOREE
{DONATION_ANTERIEURE_BOX_END}

Le DONATEUR déclare avoir consenti, jusqu'à ce jour, une donation aux termes d'un acte reçu par {{ donation_anterieure.notaire.civilite }} {{ donation_anterieure.notaire.nom|upper }}, notaire à {{ donation_anterieure.notaire.ville|upper }} ({{ donation_anterieure.notaire.code_postal }}) le {{ donation_anterieure.date.day|jour_en_lettres }} {{ donation_anterieure.date.month|mois_en_lettres }} {{ donation_anterieure.date.year }}, {{ donation_anterieure.donateurs }}, donateurs aux présentes, ont donné en avancement de part successorale à leurs {{ nombre_enfants_lettres }} enfants, donataires au présentes, {{ donation_anterieure.objet }}, pour une valeur totale en nue-propriété de {{ donation_anterieure.valeur_lettres|upper }} ({{ donation_anterieure.valeur }} EUR).

Ladite donation a eu lieu aux charges et conditions ordinaires et de droits en pareille matière et notamment la clause d'exclusion de communauté et d'indivision pacsimoniale.

Il est expressément convenu que cette donation ne sera pas réincorporée aux présentes. Il n'en sera tenu compte que pour le calcul des droits, des abattements et des tranches dans la mesure où elles ont, pour les dernières, une antériorité de moins de quinze ans de la date des présentes.

Les dispositions de l'article 784 du Code général des impôts sont rapportées en tant que de besoin aux présentes :

*"Les parties sont tenues de faire connaître, dans tout acte constatant une transmission entre vifs à titre gratuit et dans toute déclaration de succession, s'il existe ou non des donations antérieures consenties à un titre et sous une forme quelconque par le donateur ou le défunt aux donataires, héritiers ou légataires et, dans l'affirmative, le montant de ces donations ainsi que, le cas échéant, les noms, qualités et résidences des officiers ministériels qui ont reçu les actes de donation, et la date de l'enregistrement de ces actes.*

*La perception est effectuée en ajoutant à la valeur des biens compris dans la donation ou la déclaration de succession celle des biens qui ont fait l'objet de donations antérieures, à l'exception de celles passées depuis plus de quinze ans, et, lorsqu'il y a lieu à application d'un tarif progressif, en considérant ceux de ces biens dont la transmission n'a pas encore été assujettie au droit de mutation à titre gratuit comme inclus dans les tranches les plus élevées de l'actif imposable.*

*Pour le calcul des abattements et réductions édictés par les articles 779,784,790 B, 790 D, 790 E et 790 F il est tenu compte des abattements et des réductions effectués sur les donations antérieures visées au deuxième alinéa consenties par la même personne."*
{% endif %}

{% if societe %}
{CONSTITUTION_SOCIETE_BOX_START}
### {{ 'II' if donation_anterieure else 'I' }}- CONSTITUTION DE LA SOCIETE DENOMMEE « {{ societe.denomination }} »
{CONSTITUTION_SOCIETE_BOX_END}

Aux termes d'un acte sous seing privé, en date du {{ societe.constitution.date.day|jour_en_lettres }} {{ societe.constitution.date.month|mois_en_lettres }} {{ societe.constitution.date.year }}, il a été constituée une société civile dénommée « {{ societe.denomination }} » au capital de {{ societe.capital_lettres|upper }} ({{ societe.capital }} EUR) identifiée au SIREN sous le numéro {{ societe.siren }} et immatriculée au Registre du Commerce et des Sociétés de {{ societe.rcs }}, dont le siège social est à {{ societe.siege.ville|upper }} ({{ societe.siege.code_postal }}), {{ societe.siege.adresse }}, entre :

{% for associe in societe.associes_fondateurs %}
**{{ loop.index }}°) {{ associe.civilite }} {{ associe.prenom }} {{ associe.nom|upper }}**, {% if associe.conjoint %}époux{{ 'se' if associe.civilite == 'Madame' else '' }} de {{ associe.conjoint.civilite }} {{ associe.conjoint.prenom }} {{ associe.conjoint.nom|upper }}{% endif %} demeurant à {{ associe.adresse.ville|upper }} ({{ associe.adresse.code_postal }}) {{ associe.adresse.numero }} {{ associe.adresse.voie }}.

Né{{ 'e' if associe.civilite == 'Madame' else '' }} à {{ associe.naissance.ville|upper }} le {{ associe.naissance.date.day|jour_en_lettres }} {{ associe.naissance.date.month|mois_en_lettres }} {{ associe.naissance.date.year }},

{% if associe.mariage %}
Marié{{ 'e' if associe.civilite == 'Madame' else '' }} à la mairie de {{ associe.mariage.ville|upper }} ({{ associe.mariage.code_postal }}) le {{ associe.mariage.date.day|jour_en_lettres }} {{ associe.mariage.date.month|mois_en_lettres }} {{ associe.mariage.date.year }} sous le régime de {{ associe.mariage.regime }}, tel qu'il est défini par les articles {{ associe.mariage.articles_code_civil }} du Code civil, en vertu du contrat de mariage reçu par {{ associe.mariage.notaire.civilite }} {{ associe.mariage.notaire.prenom }} {{ associe.mariage.notaire.nom|upper }}, notaire à {{ associe.mariage.notaire.ville|upper }} ({{ associe.mariage.notaire.code_postal }}), le {{ associe.mariage.contrat.date.day|jour_en_lettres }} {{ associe.mariage.contrat.date.month|mois_en_lettres }} {{ associe.mariage.contrat.date.year }}.

Ce régime matrimonial n'a pas fait l'objet de modification.
{% endif %}

{% endfor %}

Ladite société, ayant les caractéristiques principales suivantes :

**Dénomination sociale : {{ societe.denomination }}**

**Objet :**

Il est ci-après littéralement rapporté les dispositions de l'article deux (2) des statuts, savoir :

*« La Société a pour objet :*

{% for objet in societe.objet_social %}
*- {{ objet }} ;*
{% endfor %}

*- Et plus généralement, la réalisation de toutes opérations se rattachant directement ou indirectement à l'objet social sus-indiqué, pourvu que ces opérations n'affectent pas le caractère civil de la société ».*

**Siège :** Le siège de la société est fixé à {{ societe.siege.ville|upper }} ({{ societe.siege.code_postal }}) {{ societe.siege.adresse }} dans le ressort du Tribunal de Commerce de {{ societe.tribunal_commerce }}, lieu de son immatriculation au Registre du commerce et des Sociétés.

**Durée :** La durée de la société est fixée à **{{ societe.duree_lettres }} ({{ societe.duree }})** années à compter de son immatriculation au Registre du Commerce et des Sociétés, sauf dissolution anticipée ou prorogation.

**Apports :**
{% for apport in societe.apports %}
-{{ apport.associe.civilite }} {{ apport.associe.prenom }} {{ apport.associe.nom|upper }} a apporté la somme de {{ apport.montant_lettres|upper }} ({{ apport.montant }} EUR) ;
{% endfor %}

Lesquels apports ont été intégralement libérés.

**Capital social :**

Il est ci-après littéralement rapporté les dispositions de l'article sept (7) des statuts, savoir :

*« ARTICLE 7 - CAPITAL SOCIAL*

*Le capital social est fixé à {{ societe.capital_lettres|upper }} ({{ societe.capital }} euros).*

*Il est divisé en {{ societe.nombre_parts_lettres|upper }} ({{ societe.nombre_parts }}) parts de {{ societe.valeur_part_lettres|upper }} ({{ societe.valeur_part }} €) chacune, lesquelles sont attribuées comme suit :*

{% for attribution in societe.attributions_initiales %}
*à {{ attribution.associe.civilite }} {{ attribution.associe.prenom }} {{ attribution.associe.nom|upper }},*
*{{ attribution.nombre_parts_lettres }} parts sociales en pleine propriété, ci {{ attribution.nombre_parts }} parts*
{% endfor %}

*Total égal au nombre de parts composant le capital social : {{ societe.nombre_parts }} parts sociales.*

*Conformément à la loi, les associés déclarent expressément que les {{ societe.nombre_parts }} parts sociales présentement créées sont souscrites en totalité par les associés, et qu'elles sont réparties entre les associés dans les proportions indiquées ci-dessus ».*

**Clause d'agrément en cas de transmission à titre gratuit :**

Aux termes de l'article treize (13) des statuts, il est prévu la clause d'agrément ci-après partiellement relatée :

*« ARTICLE 13 – CESSION ET TRANSMISSION DES PARTS SOCIALES*

*1 - Cession entre vifs*

*Toute cession de parts doit être constatée par un acte notarié ou sous signature privée.*

*Pour être opposable à la Société, elle doit, conformément aux dispositions de l'article 1690 du Code civil, lui être signifiée par exploit de commissaire de justice ou être acceptée par elle dans un acte notarié.*

*Elle n'est opposable aux tiers qu'après accomplissement de ces formalités et après publication au Registre du commerce et des sociétés ; ce dépôt peut être effectué par voie électronique.*

*Lorsque deux époux sont simultanément membres de la Société, les cessions faites par l'un d'eux à l'autre doivent, pour être valables, résulter d'un acte notarié ou d'un acte sous signature privée ayant acquis date certaine autrement que par le décès du cédant, en application des dispositions de l'article 1861 du Code civil.*

***Les parts sociales ne peuvent être cédées qu'avec un agrément donné dans les conditions ci-dessous, et ce, même si les cessions sont consenties au conjoint ou à des ascendants ou descendants du cédant.***

*L'agrément des associés est donné dans la forme et les conditions d'une décision collective extraordinaire.*

*(…)*

*4 - Donation - dissolution de communauté ou de Pacs du vivant de l'associé*

***La transmission des parts sociales par voie de donation est soumise aux mêmes conditions d'agrément que les cessions susvisées.***

*Il en est de même de toute mutation de propriété qui serait l'effet d'une liquidation de communauté de biens entre époux (…) ».*

Par conséquent l'agrément est nécessaire à la présente donation de parts {{ societe.denomination }}. Cet agrément est donné dans la forme et les conditions d'une décision collective extraordinaire :

*« ARTICLE 17 – DECISIONS COLLECTIVES*

*(…)*

*2 - Modalités*

***Les décisions collectives des associés s'expriment, soit par la participation de tous les associés à un même acte, authentique ou sous signature privée, soit en assemblée. Elles peuvent aussi résulter d'une consultation par correspondance »***

#### Information sur les parts données

{% for info_parts in societe.informations_parts_donnees %}
Les {{ info_parts.nombre_parts_lettres }} ({{ info_parts.nombre_parts }}) parts sociales en nue-propriété, objets de la donation, dont est titulaire {{ info_parts.donateur.civilite }} {{ info_parts.donateur.prenom }} {{ info_parts.donateur.nom|upper }} à titre de biens personnels lui ont été attribuées en contrepartie de son apport en numéraire lors de la constitution de la société.
{% endfor %}

#### Information sur les comptes sociaux

Les DONATAIRES reconnaissent avoir parfaite connaissance des comptes sociaux, les bilans et comptes de résultats de la société depuis sa constitution, ces éléments lui ayant été remis antérieurement aux présentes.

#### Patrimoine de la société

**a) Elément d'actif**

{% if societe.actifs.scpi %}
La société est propriétaire de parts de SCPI, savoir :
{% for scpi in societe.actifs.scpi %}
- {{ scpi.description }} numérotées de {{ scpi.numero_debut }} à {{ scpi.numero_fin }}
{% endfor %}

Le tout ainsi qu'il résulte des attestations de propriété et de valeur ci-annexées.

**Annexe n°1 : Attestations de propriété et de valeurs SCPI**
{% endif %}

**b) Eléments de passif**

{% if societe.passifs.comptes_courants %}
Les DONATEURS détiennent à ce jour une créance sur la société civile dénommée {{ societe.denomination }}, constituée des soldes créditeurs des comptes courants ouverts à leurs noms dans les livres de la société pour un montant total de {{ societe.passifs.total_lettres|upper }} ({{ societe.passifs.total }} EUR) répartis de la manière suivante :

{% for cc in societe.passifs.comptes_courants %}
- {{ cc.montant_lettres|upper }} ({{ cc.montant }} EUR) au nom de {{ cc.titulaire.civilite }} {{ cc.titulaire.prenom }} {{ cc.titulaire.nom|upper }}
{% endfor %}

Chacun arrêté à la date du {{ societe.passifs.date_arrete.day|jour_en_lettres }} {{ societe.passifs.date_arrete.month|mois_en_lettres }} {{ societe.passifs.date_arrete.year }}, ainsi qu'il résulte d'un extrait du bilan dont une copie dématérialisée est demeurée ci-jointe et annexée après mention.

**Annexe n°2 : Extrait bilan – Balance globale**
{% endif %}

#### Fiscalité de la société

{% if societe.fiscalite.is_option %}
Il est précisé que la société est soumise à l'impôt sur les sociétés sur option depuis la constitution.
{% endif %}

#### Valorisation des parts sociales

Les DONATEURS déclarent que compte tenu du patrimoine actif et passif de la société, la valeur de l'ensemble des parts sociales s'élève à {{ societe.valorisation.total_lettres|upper }} ({{ societe.valorisation.total }} EUR) en pleine propriété soit une valeur unitaire de {{ societe.valorisation.valeur_unitaire }} euros.

Ainsi qu'il résulte d'une attestation du {{ societe.valorisation.attestation.date.day|jour_en_lettres }} {{ societe.valorisation.attestation.date.month|mois_en_lettres }} {{ societe.valorisation.attestation.date.year }} délivrée par le cabinet d'expertise comptable {{ societe.valorisation.attestation.cabinet }} sis au {{ societe.valorisation.attestation.adresse }} dont une copie est annexée aux présentes.

**Annexe n°3 : Attestation valorisation parts**

Le notaire soussigné rappelle aux parties l'importance d'une évaluation réelle tant pour éviter tout redressement par l'administration fiscale en cas de contrôle, que pour éviter un déséquilibre entre les donataires dans l'attribution des lots.

En conséquence, les parties déchargent entièrement le notaire soussigné de toute responsabilité en cas de contestation de la valorisation et de la société par l'une des parties ou un tiers (administration fiscale) et renonce à tout recours contre ce dernier considérant avoir reçu toutes les explications nécessaires en la matière.

{% endif %}
{CONSTITUTION_SOCIETE_BOX_END}

Ceci exposé, il est passé à la donation-partage objet du présent acte.

{DONATION_PARTAGE_BOX_START}
## DONATION-PARTAGE

Le **DONATEUR** fait, par ces présentes, **donation entre vifs à titre de partage anticipé, conformément aux dispositions des articles 1075 et suivants du Code civil.**

Aux **DONATAIRES**, présomptifs héritiers, ici présents et qui acceptent,

**DE LA NUE-PROPRIETE pour y réunir l'usufruit au jour de son extinction, des biens ci-après désignés.**

Les opérations seront divisées en quatre parties qui comprendront :

| **PREMIERE PARTIE** | **MASSE DES BIENS DONNES ET A PARTAGER** |
| **DEUXIEME PARTIE** | **VALEURS DES DROITS A ATTRIBUER AUX COPARTAGES** |
| **TROISIEME PARTIE** | **ATTRIBUTIONS AUX COPARTAGES** |
| **QUATRIEME PARTIE** | **CARACTERISTIQUES, CONDITIONS, FISCALITE** |
{DONATION_PARTAGE_BOX_END}

### PREMIERE PARTIE - MASSE DES BIENS DONNES ET A PARTAGER

La présente donation-partage porte sur les biens ci-après désignés répartis dans les lots établis par le DONATEUR avec le consentement des DONATAIRES.

{% if biens_donnes.biens_personnels_donateur_2 %}
#### Biens personnels de {{ donateur_2.civilite }} {{ donateur_2.prenom }} {{ donateur_2.nom|upper }}

{% for bien in biens_donnes.biens_personnels_donateur_2 %}
**ARTICLE {{ bien.numero_article|nombre_en_lettres|upper }}**

{{ bien.designation }}

Evaluée pour la totalité en pleine propriété à {{ bien.valeur_pp_lettres|upper }} ({{ bien.valeur_pp }} EUR)

Dont il y a lieu de déduire l'usufruit appartenant à {{ bien.usufruitier.civilite }} {{ bien.usufruitier.prenom }} {{ bien.usufruitier.nom|upper }}, {% if bien.usufruitier.sexe == 'F' %}donatrice{% else %}donateur{% endif %} aux présentes, évalué eu égard à son âge à {{ bien.taux_usufruit }} %.

Soit une nue-propriété d'une valeur de {{ bien.valeur_np_lettres|upper }}

Ci ...................................................................................................{{ bien.valeur_np }} EUR

{% endfor %}

---------------------
**Ensemble** ......................................................................................{{ biens_donnes.total_donateur_2 }} EUR
{% endif %}

{% if biens_donnes.biens_personnels_donateur_1 %}
#### Biens personnels de {{ donateur_1.civilite }} {{ donateur_1.prenom }} {{ donateur_1.nom|upper }}

{% for bien in biens_donnes.biens_personnels_donateur_1 %}
**ARTICLE {{ bien.numero_article|nombre_en_lettres|upper }}**

{{ bien.designation }}

Evaluée pour la totalité en pleine propriété à {{ bien.valeur_pp_lettres|upper }} ({{ bien.valeur_pp }} EUR)

Dont il y a lieu de déduire l'usufruit appartenant à {{ bien.usufruitier.civilite }} {{ bien.usufruitier.prenom }} {{ bien.usufruitier.nom|upper }}, {% if bien.usufruitier.sexe == 'F' %}donatrice{% else %}donateur{% endif %} aux présentes, évalué eu égard à son âge à {{ bien.taux_usufruit }} %.

Soit une nue-propriété d'une valeur de {{ bien.valeur_np_lettres|upper }}

Ci, ..................................................................................................{{ bien.valeur_np }} EUR

{% endfor %}
{% endif %}

---------------------
**Valeur totale de la masse** ......................................................... : {{ biens_donnes.total_masse }} EUR

### DEUXIEME PARTIE – VALEURS DES DROITS A ATTRIBUER AUX COPARTAGES

Le DONATEUR, usant de la faculté réservée par l'article 1075 du Code civil, procède ainsi qu'il suit à l'attribution des lots ci-dessus formés.

#### REPARTITION EGALITAIRE

Les biens donnés et à partager seront répartis égalitairement entre les DONATAIRES, à concurrence de **{{ repartition.fraction_lettres|upper }} ({{ repartition.fraction }})** chacun et ce à titre de condition impulsive et déterminante des présentes sans laquelle les parties ne seraient pas intervenues.

Par conséquent, chaque DONATAIRE doit recevoir des attributions pour une valeur totale égale à ses droits de {{ repartition.valeur_par_donataire_lettres|upper }} ({{ repartition.valeur_par_donataire }} EUR) ({{ biens_donnes.total_masse }}/{{ nombre_donataires }})

### TROISIEME PARTIE – ATTRIBUTIONS AUX COPARTAGES

La masse des biens donnés et à partager est répartie entre les DONATAIRES selon la volonté du DONATEUR ainsi qu'il suit.

{% for donataire in donataires %}
#### Attributions à {{ donataire.civilite }} {{ donataire.prenom }} {{ donataire.nom|upper }}

Il {% if donataire.civilite == 'Madame' %}lui{% else %}lui{% endif %} est attribué, ce qu'{% if donataire.civilite == 'Madame' %}elle{% else %}il{% endif %} accepte :

{% for attribution in donataire.attributions %}
**{{ loop.index }}°)** {{ attribution.designation }}

Ci {% if loop.last %},...........................................................................................{% else %}.....................................................................................................{% endif %} {{ attribution.valeur }} EUR

{% endfor %}

**Soit total égal à**............................................................................ {{ donataire.total_attributions }} EUR

{% endfor %}

{QUATRIEME_PARTIE_BOX_START}
### QUATRIEME PARTIE - CARACTERISTIQUES, CONDITIONS, FISCALITE
{QUATRIEME_PARTIE_BOX_END}

#### CARACTERE DE LA DONATION-PARTAGE

La présente donation-partage est consentie à titre **d'avancement de part successorale**. Les biens donnés s'imputent sur la part de réserve des DONATAIRES conformément à l'article 1077 du Code civil.

#### MODE DE CALCUL DE LA QUOTITE DISPONIBLE

Conformément aux dispositions de l'article 1078 du Code civil, les biens donnés seront évalués au moment du décès du DONATEUR selon leur valeur au jour de la présente donation-partage pour l'imputation et le calcul de la réserve, chacun des enfants ayant reçu et accepté un lot dans le partage anticipé et aucune réserve d'usufruit portant sur une somme d'argent n'ayant été stipulée.

#### CONDITIONS PARTICULIERES

##### CLAUSE D'EXCLUSION DE COMMUNAUTE

À titre de condition essentielle et déterminante des présentes, le DONATEUR stipule que les BIENS présentement donnés devront rester exclus de toute communauté ou société d'acquêts présente ou à venir des DONATAIRES que ce soit par mariage ou remariage subséquent ou changement total ou partiel de régime matrimonial.

Il en sera également de même pour le ou les BIENS qui viendraient à leur être subrogés.

Le DONATAIRE déclare avoir été parfaitement informé par le rédacteur des présentes de l'utilité et des formes du remploi visé à l'article 1434 du Code civil.

Cette clause d'exclusion est limitée à la durée de vie du DONATEUR.

##### CLAUSE D'EXCLUSION DU REGIME DE L'INDIVISION DU PACS

À titre de condition essentielle et déterminante des présentes, le DONATEUR exige que le ou les BIENS présentement donnés restent exclus de tout régime de l'indivision du PACS présente ou à venir des DONATAIRES.

Il en sera également de même pour le ou les BIENS qui viendraient à leur être subrogés.

Cette clause d'exclusion est limitée à la durée de vie du DONATEUR.

##### RESERVE DU DROIT DE RETOUR

Le DONATEUR se réserve l'exercice, à titre facultatif, du droit de retour sur le BIEN présentement donné, conformément à l'article 951 du Code civil pour les cas où, de son vivant :

• le DONATAIRE et tous ses descendants, quelle que soit l'origine de la filiation, viendraient à décéder avant lui,

• les descendants du DONATAIRE viendraient à être exclus de la succession du DONATAIRE prédécédé pour cause de renonciation ou d'indignité.

##### DROIT DE RETOUR LEGAL DES PERE ET MERE

Lorsque le droit de retour conventionnel ne s'exerce pas, le DONATEUR bénéficie, en tant que père et/ou mère du DONATAIRE, d'un droit de retour légal du BIEN donné s'il venait à lui prédécéder sans postérité, et ce aux termes et dans les conditions de l'article 738-2 du Code civil. Le DONATEUR n'a pas la faculté de renoncer à ce droit légal de nature successorale avant l'ouverture de la succession en question.

##### INFORMATION SUR LE DROIT DE RETOUR LEGAL DES FRERES ET SŒURS

Les copartageants sont informés des dispositions de l'article 757-3 du Code civil en vertu desquelles, s'ils venaient à décéder sans postérité en laissant leur conjoint héritier pour le tout, les biens présentement reçus de leur(s) ascendant(s) et qui se trouveraient en nature dans leur propre succession, seraient dévolus par moitié entre les collatéraux privilégiés et le conjoint survivant.

Ce droit de retour au profit des frères et sœurs, et leurs descendants s'applique même si ces biens sont reçus à charge de soulte et sans obligation pour les collatéraux privilégiés d'indemniser la succession du copartageant.

En cas d'améliorations ou de constructions apportées aux biens, aux frais du copartageant, et d'exercice de ce droit de retour, le copartageant requiert que les collatéraux privilégiés indemnisent le conjoint survivant, ce que ces deniers acceptent dès à présent. Cette indemnisation, si elle existe, se fera à dire d'expert si nécessaire.

Les dispositions de l'article 757-3 du Code civil n'étant pas d'ordre public, les copartageants peuvent faire échec à son application en établissant par la suite des dispositions contraires.

##### INTERDICTION D'ALIENER ET DE NANTIR

Le DONATEUR interdit formellement aux DONATAIRES qui s'y soumettent, de **vendre, aliéner, nantir ou remettre en garantie** les titres donnés aux présentes, pendant sa vie, à peine de nullité de toute aliénation ou nantissement et de révocation des présentes pendant la même durée, sauf accord exprès

Dans l'hypothèse envisagée où les titres objet de la présente donation-partage seraient apportés à une autre société, avec l'accord du DONATEUR, cette interdiction s'appliquerait alors aux titres de ladite société attribués aux DONATAIRES en représentation de leurs apports.

Dans le cas où les titres de cette nouvelle société représentatifs des apports des titres objet de la présente donation-partage, seraient eux-mêmes apportés à une nouvelle société, avec l'accord du DONATEUR, l'interdiction s'appliquerait alors aux titres de cette nouvelle société, ces titres étant eux-mêmes considérés comme étant purement et simplement subrogés à ceux de la présente donation-partage.

En outre, s'agissant de la donation de biens personnels faite par chacun des DONATEURS avec réserve d'usufruit et usufruit successif sur la tête du conjoint, lesdits DONATEURS entendent, en cas de prédécès, que l'interdiction d'aliéner et de nantir soit également stipulée en faveur de son conjoint.

Les DONATEURS précisent que cette interdiction a vocation à s'appliquer jusqu'au décès du survivant d'eux, et est fondée aux présentes sur **la conservation des biens dans le cercle familial**.

##### ACTION REVOCATOIRE

À défaut par le DONATAIRE, d'exécuter les conditions de la présente donation, le DONATEUR pourra, comme de droit, en faire prononcer la révocation.

Le notaire soussigné rappelle aux parties les dispositions des articles 953 et 955 du Code civil :

Article 953 : *"La donation entre vifs ne pourra être révoquée que pour cause d'inexécution des conditions sous lesquelles elle aura été faite, pour cause d'ingratitude, et pour cause de survenance d'enfants."*

Article 955 : *"La donation entre vifs ne pourra être révoquée pour cause d'ingratitude que dans les cas suivants :*

*1° Si le donataire a attenté à la vie du donateur ;*

*2° S'il s'est rendu coupable envers lui de sévices, délits ou injures graves ;*

*3° S'il lui refuse des aliments."*

##### Action révocatoire pour cause d'ingratitude

Le DONATEUR se réserve expressément le droit d'agir en révocation de la présente donation pour cause d'ingratitude du DONATAIRE dans les conditions prévues aux articles 955 et 957 du Code civil.

Les parties sont informées que la révocation pour ingratitude, une fois prononcée par le juge, n'a pas d'effet rétroactif. La révocation ne préjudicie ni aux aliénations, ni aux sûretés et autres charges réelles que le DONATAIRE aurait pu consentir. Le DONATAIRE est amené, dans ce cas, à restituer la valeur du BIEN aliéné conformément à l'article 958 du Code civil.

##### CONDITION DE NE PAS ATTAQUER LA DONATION-PARTAGE

Le DONATEUR impose aux DONATAIRES la condition de ne pas attaquer le présent partage anticipé.

Si ce partage venait à être attaqué, au mépris de cette condition, pour quelque cause que ce soit, par l'un ou l'autre des DONATAIRES, le DONATEUR déclare priver le ou les responsables de cette action de toute part dans la quotité disponible de sa succession sur les biens compris aux présentes et faire donation, hors part successorale, de cette portion dans la quotité disponible à celui ou ceux des DONATAIRES contre lesquels l'action est intentée.

Le DONATEUR et les DONATAIRES sont informés par le notaire soussigné que la présente clause n'a pas pour effet de porter une atteinte excessive au droit d'agir en justice mais de prévenir les conflits intempestifs et infondés.

##### INFORMATION SUR LE CONSENTEMENT A L'ALIENATION

Les parties reconnaissent avoir été informées par le notaire soussigné des dispositions de l'article 924-4, alinéa deuxième, du Code civil ci-après littéralement rapportées :

*"Lorsque, au jour de la donation ou postérieurement, le donateur et tous les héritiers réservataires présomptifs ont consenti à l'aliénation du bien donné, aucun héritier réservataire, même né après que le consentement de tous les héritiers intéressés a été recueilli, ne peut exercer l'action contre les tiers détenteurs. S'agissant des biens légués, cette action ne peut plus être exercée lorsque les héritiers réservataires ont consenti à l'aliénation."*

En conséquence, les parties et particulièrement le DONATAIRE prennent acte de la nécessité du consentement du DONATEUR et de ses autres descendants, s'il en existe, en cas d'aliénation du ou des biens donnés, afin qu'aucune action en réduction ou en revendication ne puisse alors être exercée contre le tiers détenteur.

##### RAPPORT DE DONATION SI RENONCIATION A SUCCESSION

À titre de condition essentielle du présent acte, le DONATEUR exige, dans le cas où le DONATAIRE renoncerait à sa succession, que la présente donation-partage soit rapportée à la succession ainsi que lui permettent les dispositions de l'article 845 du Code civil, et le rapport sera évalué conformément aux dispositions des articles 843 et suivants du Code civil.

##### CONDITIONS PARTICULIERES

Le DONATEUR stipule comme condition de la présente donation-partage, qu'en cas de cession avec l'accord de l'usufruitier de tout ou partie des titres sociaux présentement donnés et sans que ce prix de cession soit employé à acquérir de nouveaux titres, les DONATAIRES **auront l'obligation de verser les fonds provenant desdites cessions sur un compte démembré** : Nue-propriété au nom de chaque DONATAIRE / Usufruit au nom du DONATEUR à ouvrir dans toute banque au gré de l'usufruitier desdits titres.

Les DONATAIRES acceptent cette condition et s'obligent à la remplir expressément, donnant, dès à présent, au DONATEUR mandat de gestion exclusif des fonds ainsi placés.

Toutefois, ils n'en auront la jouissance qu'au jour du décès du survivant des DONATEURS, réserve expresse de l'usufruit des biens présentement donnés étant faite à leur profit, sans réduction au décès du prémourant, ce qui est accepté par chacun d'eux.

Le notaire soussigné a porté en tant que de besoin à la connaissance des parties les dispositions du premier alinéa de l'article 265 du Code civil : *« Le divorce est sans incidence sur les avantages matrimoniaux qui prennent effet au cours du mariage et sur les donations de biens présents quelle que soit leur forme »* précisant que l'irrévocabilité des donations de biens présents ne s'appliquent pas aux donations entre époux de biens présents qui ne prennent pas effet au cours du mariage.

Les DONATEURS déclarent avoir connaissance des conséquences de la présente réversion par les explications qui lui ont été données par le notaire soussigné, déclarant dès à présent se soumettre aux conditions et conséquences de cet usufruit.

#### TRANSFERT DE PROPRIETE - MODALITES DE JOUISSANCE

##### EN CE QUI CONCERNE LES TITRES SOCIAUX

###### PROPRIETE-JOUISSANCE - TITRES DE SOCIETE

Au moyen de la présente donation-partage, les DONATAIRES auront la nue-propriété des titres sociaux à eux donnés et attribués à compter de ce jour, le DONATEUR s'en réserve l'entier usufruit.

###### EXERCICE DE L'USUFRUIT

L'usufruitier jouira de l'usufruit réservé raisonnablement, et aux conditions et charges de droit en pareille matière.

L'usufruitier exercera tous les droits attachés aux titres sociaux donnés conformément aux statuts et participera seul aux résultats sociaux.

###### CONDITIONS DE L'USUFRUIT RESERVE

L'usufruitier n'aura droit qu'aux bénéfices distribués des titres objets des présentes, ainsi qu'à ceux des titres acquis grâce à des bénéfices non distribués.

En application des dispositions d'ordre public du troisième alinéa de l'article 1844 du Code civil le nu-propriétaire et l'usufruitier ont le droit de participer aux décisions collectives.

###### Usufruit successif – Biens personnels

Les DONATAIRES seront nus-propriétaires à compter de ce jour des biens personnels donnés et compris dans leur attribution.

{% if usufruit_successif %}
Le DONATEUR constitue, sur le ou les biens qui lui sont personnels donnés aux présentes, un usufruit successif au profit de son conjoint s'il lui survit en cette qualité, et ce aux mêmes modalités que l'usufruit qu'il se réserve en premier rang.

Conformément aux dispositions de l'article 758-6 du Code civil, la donation d'usufruit résultant des présentes s'imputera sur les droits en usufruit du conjoint survivant dans la succession du DONATEUR.

En conséquence, les DONATAIRES n'auront la jouissance des biens donnés qu'au décès du DONATEUR ou de son conjoint s'il lui survit en cette qualité.

###### Caducité de la réversion d'usufruit

La présente institution contractuelle sera révoquée de plein droit en cas d'introduction d'une procédure en divorce ou en séparation de corps, ou encore en cas de jugement de divorce ou de séparation de corps passé ou non en force de chose jugée, sauf volonté contraire du DONATEUR.

Cette volonté contraire sera constatée par le juge soit au moment de l'introduction d'une procédure en divorce ou en séparation de corps soit au moment du prononcé du divorce et rendra irrévocable l'institution contractuelle.

###### Cas de révocation de l'usufruit successif

La présente constitution d'usufruit successif sera révoquée de plein droit en cas d'introduction d'une procédure en divorce, par assignation ou requête conjointe, ou en séparation de corps, ou en cas de signature d'une convention sous signature privée contresignée par avocats portant divorce par consentement mutuel, sauf volonté contraire du DONATEUR.
{% endif %}

{% if societe %}
##### REPARTITION DU DROIT DE VOTE EN CAS DE DEMEMBREMENT DES PARTS SOCIALES

Actuellement, les statuts stipulent ce qui suit en matière de droit de vote en cas de démembrements des parts :

Il est ici rappelé aux parties les dispositions de l'article 11 des statuts de la société dénommée {{ societe.denomination }}, ci-dessous littéralement retranscrites, savoir :

*« (…) Si une part est grevée d'un usufruit, le nu-propriétaire et l'usufruitier ont le droit de participer aux décisions collectives, quel que soit le titulaire du droit de vote. Ils doivent être convoqués à toutes les assemblées et disposent du même droit d'information.*

*Le droit de vote appartient au nu-propriétaire, sauf pour les décisions concernant l'affectation des bénéfices, où il est réservé à l'usufruitier.*

*Toutefois, pour les autres décisions, le nu-propriétaire et l'usufruitier peuvent convenir que le droit de vote sera exercé par l'usufruitier. La convention est notifiée par lettre recommandée à la Société, qui sera tenue d'appliquer cette convention pour toute assemblée qui se réunirait après l'expiration d'un délai d'un mois suivant l'envoi de cette lettre ».*

{% if modification_article_11 %}
Toutefois, les parties déclarent vouloir modifier à titre de condition des présentes cet article 11 de la façon suivante :

*« ARTICLE 11 – INDIVISIBILTE DES PARTS SOCIALES*

*Les parts sociales sont indivisibles à l'égard de la Société qui ne reconnaît qu'un seul propriétaire pour chaque part.*

*Les copropriétaires indivis sont tenus de désigner l'un d'entre eux pour les représenter auprès de la Société ; à défaut d'entente, il appartient à l'indivisaire le plus diligent de faire désigner par voie de justice un mandataire chargé de les représenter, conformément aux dispositions de l'article 1844 du Code civil.*

*Démembrement*

*Le nu-propriétaire et l'usufruitier ont la qualité d'associé et, à ce titre, le droit de participer aux décisions collectives.*

*A cette fin, ils sont convoqués et participent aux assemblées dans les mêmes conditions que les associés en toute propriété. Ils exercent dans les mêmes conditions leur droit de communication et reçoivent les mêmes informations, notamment en cas de consultation écrite ou lorsque la décision des associés résulte de leur consentement exprimé dans un acte.*

*Ils prennent part, s'ils le souhaitent, aux discussions qui précèdent le vote et leurs avis sont, le cas échéant, comme celui des autres associés, mentionnés au procès-verbal.*

***Le droit de vote appartient à l'usufruitier pour toutes les décisions collectives ordinaires et extraordinaires.***

*L'exercice du droit de vote de l'usufruitier ne devra ni amener une augmentation des engagements du nu-propriétaire ni s'exercer dans le dessein de favoriser ses intérêts au détriment de ceux des autres associés ».*

En conséquence, les statuts seront mis à jour à ce sujet.
{% endif %}

##### DECISION D'AGREMENT - INTERVENTION DES ASSOCIES

Les statuts de la société prévoient un agrément dans l'hypothèse de la présente mutation à titre gratuit.

Tel que précisé ci-avant, les statuts prévoient, en son article 17, que l'agrément est donné par une décision collective des associés, lesquels s'expriment soit par la participation de tous les associés à un même acte authentique ou sous signature privée, soit en assemblée.

Par suite, sont intervenus en tant que de besoin, savoir :

{% for associe_intervenant in societe.associes_intervenants %}
**{{ loop.index }}°-{{ associe_intervenant.civilite }} {{ associe_intervenant.prenom }} {{ associe_intervenant.nom|upper }}**, {% if associe_intervenant.qualite_donateur %}donateur aux présentes,{% endif %}
Plus amplement nommé{{ 'e' if associe_intervenant.civilite == 'Madame' else '' }}, qualifié{{ 'e' if associe_intervenant.civilite == 'Madame' else '' }} et domicilié{{ 'e' if associe_intervenant.civilite == 'Madame' else '' }} ci-dessus.
A ce présent{{ 'e' if associe_intervenant.civilite == 'Madame' else '' }} à l'acte.
Agissant en sa qualité de {{ associe_intervenant.qualite_societe }} de la société dénommée {{ societe.denomination }}

{% endfor %}

LESQUELS, seuls et uniques associés de la société dénommée {{ societe.denomination }} et conformément aux articles 13 et 17 des statuts, **déclarent donner leur accord exprès à la présente mutation à titre gratuit.**

##### DISPENSE DE SIGNIFICATION – OPPOSABILITE

Au présent acte sont intervenus en tant que de besoin {{ societe.gerants_noms }} susnommés, gérants de la société émettrices des parts cédés, lesquels :

- Confirment que la société n'a reçue aucune opposition et n'a connaissance d'aucun empêchement pouvant arrêter ou suspendre l'effet de la présente cession de parts sociales ;

- Déclarent au notaire soussigné ainsi qu'aux parties, qu'ils acceptent la présente cession de parts sociales et la reconnaissent opposable à la société, dispensant ainsi de la signification prévue par l'article 1690 du Code civil.

Cette cession ainsi qu'il résulte des dispositions l'article 1865 du Code civil, n'est opposable aux tiers qu'après publication des statuts modifiés au registre du commerce et des sociétés ; ce dépôt peut être effectué par voie électronique.

Cette formalité sera effectuée par le notaire soussigné.

##### CONDITIONS DE TRANSMISSION DES DROITS SOCIAUX

Les DONATAIRES attestent avoir pris connaissance des statuts de la société civile dénommée {{ societe.denomination }}, dès avant ce jour et s'engage par les présentes à les respecter.

###### -1-Absence de garantie de passif

La présente donation est acceptée par les DONATAIRES-ATTRIBUTAIRES **sans garantie de passif** de la part des DONATEURS, les DONATAIRES-BENEFICIAIRES déclarent parfaitement connaître la situation active et passive de la société.

###### -2-Modification des statuts :

Comme conséquence de la présente donation de parts sociales, il y a lieu de modifier l'article des statuts concernant le capital social dont la rédaction sera désormais la suivante :

*« ARTICLE 7 - CAPITAL SOCIAL*

*« -I- A l'origine, le capital social est fixé à {{ societe.capital_lettres|upper }} ({{ societe.capital }} euros).*

*Il est divisé en {{ societe.nombre_parts_lettres|upper }} ({{ societe.nombre_parts }}) parts de {{ societe.valeur_part_lettres|upper }} ({{ societe.valeur_part }} €) chacune, lesquelles sont attribuées comme suit :*

{% for attribution_initiale in societe.attributions_initiales %}
*à {{ attribution_initiale.associe.civilite }} {{ attribution_initiale.associe.prenom }} {{ attribution_initiale.associe.nom|upper }},*
*{{ attribution_initiale.nombre_parts_lettres }} parts sociales en pleine propriété, ci {{ attribution_initiale.nombre_parts }} parts*
{% endfor %}

*Total égal au nombre de parts composant le capital social : {{ societe.nombre_parts }} parts sociales.*

*Conformément à la loi, les associés déclarent expressément que les {{ societe.nombre_parts }} parts sociales présentement créées sont souscrites en totalité par les associés, et qu'elles sont réparties entre les associés dans les proportions indiquées ci-dessus ».*

*-II- Aux termes d'une donation-partage reçu par {{ notaire.civilite }} {{ notaire.prenom }} {{ notaire.nom|upper }} notaire à {{ notaire.office.ville|upper }} ({{ notaire.office.code_postal }}), {{ notaire.office.adresse }}, le {{ date_acte.day|jour_en_lettres }} {{ date_acte.month|mois_en_lettres }} {{ date_acte.year }} {{ societe.modification.texte_donation }}*

*Par suite des faits et actes suivants, le capital social est dorénavant réparti de la manière suivante savoir :*

{{ societe.tableau_repartition }}

*Total égal au nombre de parts composant le capital social*

*Ci ....................................................................................{{ societe.nombre_parts }} parts sociales ».*

###### -3-Publication :

Conformément aux prescriptions légales et réglementaires, le présent acte sera déposé au Greffe du Tribunal de Commerce auprès duquel la société est immatriculée, tous pouvoirs étant donnés à tout porteur d'expéditions du présent acte en vue de l'accomplissement de cette formalité.

###### -4- Opposabilité des mutations à la société

Etant ici précisé que la mutation de parts sociales n'est opposable à la société qu'autant qu'elle lui aura été signifiée par acte d'Huissier de Justice ou qu'elle aura été acceptée par elle dans un acte authentique, conformément à l'article 1690 du Code civil.

###### -5- Opposabilité des mutations aux tiers

La mutation n'est opposable aux tiers qu'après dépôt au registre du commerce et des sociétés compétent d'une copie authentique de l'acte de mutation ou de deux originaux s'il est sous seing privé.

##### MIS A JOUR DES STATUTS

Conformément à l'obligation édictée à l'article R 123-89 du Code de commerce, le notaire soussigné fera publier la modification des statuts dans un support d'annonces légales et au greffe du tribunal compétent par l'intermédiaire du guichet unique.

{% endif %}

#### ORIGINE DE PROPRIETE DES PARTS SOCIALES DETENUES PAR LE DONATEUR

{% if societe %}
Les parts sociales ci-dessus données appartiennent aux DONATEURS, pour se les avoir fait attribuer dans l'acte constitutif de la société en rémunération de son apport en numéraire.
{% endif %}

#### DROIT DE PREEMPTION URBAIN – EXEMPTION

La donation ne donne pas ouverture au droit de préemption urbain, la donation étant consentie à un parent ou à un allié défini par l'article L 213-1-1 du Code de l'urbanisme.

#### DECHARGE RESPECTIVE

Les DONATAIRES déclarent être entièrement remplis de leurs droits dans la présente donation-partage.

En conséquence, ils se consentent respectivement toutes décharges nécessaires et renoncent à jamais s'inquiéter ni se rechercher dans l'avenir au sujet des biens compris aux présentes, pour quelque cause que ce soit.

#### PRESOMPTION DE PROPRIETE

En application des dispositions de l'article 751 du Code général des impôts, premier alinéa, sont présumés faire partie de la succession pour la liquidation et le paiement des droits de mutation par décès tout bien meuble ou immeuble appartenant pour l'usufruit au défunt et pour la nue-propriété à l'un de ses présomptifs héritiers sauf si le démembrement résulte d'une donation reçue par acte authentique plus de trois mois avant le décès et si la valeur de la nue-propriété a été déterminée selon le barème fiscal. A défaut d'un tel acte, la preuve contraire peut notamment résulter d'une donation des deniers constatée par un acte ayant date certaine quel qu'en soit l'auteur en vue de financer plus de trois mois avant le décès l'acquisition de tout ou partie de la nue-propriété d'un bien, sous réserve de justifier de l'origine des deniers dans l'acte en constatant l'emploi, ou encore par la production d'éléments suffisants pour démontrer la sincérité de la donation.

En application des dispositions de l'article 752 du Code général des impôts, premier alinéa, sont présumés jusqu'à preuve du contraire faire partie de la succession pour la liquidation et le paiement des droits de mutation par décès, les valeurs mobilières, parts sociales et créances dont le défunt a perçu les revenus ou à raison desquelles il a effectué une opération quelconque moins d'un an avant son décès. Cette présomption, en vertu du deuxième alinéa de cet article, est écartée pour les présentes.

{DECLARATIONS_FISCALES_BOX_START}
## DECLARATIONS FISCALES
{DECLARATIONS_FISCALES_BOX_END}

### INFORMATIONS DES PARTIES SUR LE RAPPEL FISCAL

La règle du **"RAPPEL FISCAL"** des donations est actuellement régie par les dispositions de l'article 784 du Code générale des impôts.

Elle prévoit que les héritiers, légataires ou personnes bénéficiaires d'une donation sont tenus de faire connaître dans toute déclaration de succession ou d'acte de donation les donations antérieures qui leur ont été déjà consenties par le défunt (ou le donateur).

Ce délai a été porté de six (6) à dix (10) ans par la loi de finances rectificative pour 2011 numéro 2011-900 du 29 juillet 2011 publié au journal officiel le 30 juillet 2011.

Puis, par la loi de finance rectificative pour 2012 numéro 2012-958 en date du 16 août 2012 publiée le 17 août 2012, ce délai a été rallongé à **quinze (15) ans**.

Cette mesure est applicable au jour de la publication de ladite loi, soit le 17 août 2012.

### DONATIONS ANTERIEURES

{% if donation_anterieure %}
Les DONATEURS déclarent qu'ils n'ont consenti aucune donation, sous quelque forme que ce soit, antérieurement à ce jour à l'exception de celle relatée dans l'exposé en tête des présentes.

Le rappel fiscal s'exerce sur l'acte de donation consenti par {{ donation_anterieure.rappel_texte }}.

{{ donation_anterieure.calcul_droits }}

{% else %}
Les DONATEURS déclarent qu'ils n'ont consenti aucune donation, sous quelque forme que ce soit, antérieurement à ce jour.
{% endif %}

Les DONATAIRES entendent bénéficier pour le présent acte de donation-partage des abattements et réductions prévus par les articles 779 et suivants du Code général des impôts dans la mesure de leur applicabilité aux présentes.

La situation fiscale est la suivante :

### CALCUL DES DROITS

{% for donataire in donataires %}
{% for donateur in [donateur_1, donateur_2] %}
{% set donateur_key = 'donateur_' ~ loop.index %}
**{{ donataire.civilite }} {{ donataire.prenom }} {{ donataire.nom|upper }} a reçu de {{ donateur.civilite }} {{ donateur.prenom }} {{ donateur.nom|upper }} :**

Part lui revenant : {{ donataire.calcul_droits[donateur_key].part }} €
A déduire montant des exonérations : - {{ donataire.calcul_droits[donateur_key].exonerations }} €
A déduire donation(s) incorporée(s) : - {{ donataire.calcul_droits[donateur_key].donations_incorporees }} €
Part imposable : {{ donataire.calcul_droits[donateur_key].part_imposable }} €

Abattement applicable : - {{ donataire.calcul_droits[donateur_key].abattement_applicable }} €
Abattement déjà utilisé : - {{ donataire.calcul_droits[donateur_key].abattement_utilise }} €
Abattement utilisé : - {{ donataire.calcul_droits[donateur_key].abattement_nouveau }} €

Part nette taxable : {{ donataire.calcul_droits[donateur_key].part_nette_taxable }} €

Calcul des droits :
{{ donataire.calcul_droits[donateur_key].calcul_detail }}

Total des droits : {{ donataire.calcul_droits[donateur_key].total_droits }} €

Droits à payer : {{ donataire.calcul_droits[donateur_key].droits_a_payer }} €

{% endfor %}
{% endfor %}

**Total des droits à payer {{ total_droits_a_payer }} €**

### Nombre d'enfants des DONATEURS

Les DONATEURS déclarent avoir {{ nombre_enfants_lettres }} enfants, les DONATAIRES aux présentes.

### PLUS-VALUES IMMOBILIERES

Le notaire soussigné a averti les parties de la réglementation actuellement applicable en matière de plus-values immobilières en cas de vente.

{% if societe %}
### MODIFICATION DES STATUTS

Tous les associés sont présents ou représentés.

Les associés décident de compléter l'article 21 des statuts intitulé **« AFFECTATION ET REPARTITION DES RESULTATS »** en présence de parts démembrées de la manière suivante :

*« Attribution du résultat courant à l'usufruitier et le résultat exceptionnel au nu-propriétaire sous réserve de quasi- usufruit*

*Le bénéfice social et le report à nouveau bénéficiaire provenant d'un résultat courant, s'ils sont mis en distribution reviennent en pleine propriété à l'usufruitier des parts.*

*Le bénéfice provenant d'un résultat exceptionnel revient en nue-propriété au nu-propriétaire et sous forme de quasi- usufruit à l'usufruitier des parts à charge pour lui de restituer la somme au nu-propriétaire à l'extinction de son droit. L'usufruitier des parts est dispensé de dresser inventaire, de fournir caution et de toute obligation d'emploi.*

*Les réserves distribuées appartiennent à l'usufruitier sous forme de quasi-usufruit*

*Sous réserve de l'intervention ultérieure d'une convention entre le nu-propriétaire et l'usufruitier des parts, la distribution des réserves et les sommes assimilées, telles que les primes d'émissions, primes de fusions, appartiendra au nu-propriétaire.*

*Les bénéfices mis en réserve constitueront un accroissement de l'actif social revenant au nu-propriétaire.*

*Sous réserve de l'intervention ultérieure d'une convention précitée, les dividendes distribués prélevés sur les réserves appartiendront au nu-propriétaire. Mais pour assurer à l'usufruitier la jouissance de ces sommes, il sera constitué à son profit un quasi- usufruit sur ces sommes avec l'obligation de restitution à l'extinction de son droit au profit du nu-propriétaire.*

*L'usufruitier est dispensé de dresser inventaire, de fournir caution et de toute obligation d'emploi ».*
{% endif %}

### ENREGISTREMENT

Les présentes seront soumises à la formalité de l'enregistrement auprès du service compétent.

### MODALITES DE DELIVRANCE DE LA COPIE AUTHENTIQUE

Le notaire rédacteur adressera, à l'attention des DONATAIRES, une copie authentique sur support papier ou sur support électronique des présentes qu'ultérieurement, notamment en cas de demande expresse de ces derniers, de leur mandataire, de leur notaire, ou de leur ayant droit.

Néanmoins, le notaire leur adressera, immédiatement après la signature des présentes, une copie scannée de l'acte si l'acte a été signé sur support papier, ou une copie de l'acte électronique s'il a été signé sous cette forme.

Cet envoi se fera par courriel à l'adresse des DONATAIRES qui a été utilisée pour correspondre avec eux durant toute la durée du dossier.

### FRAIS

Tous les frais, droits et émoluments des présentes, et de leurs suites et conséquences, en ce compris les conséquences financières d'un redressement fiscal, seront à la charge du DONATEUR qui s'y oblige expressément.

### TITRES

Il ne sera remis aucun ancien titre de propriété au DONATAIRE qui sera subrogé dans tous les droits du DONATEUR pour se faire délivrer, en payant les frais, tous extraits ou copies authentiques d'actes ou tous originaux concernant le ou les biens.

### POUVOIRS - PUBLICITE FONCIERE

Pour l'accomplissement des formalités de publicité foncière ou réparer une erreur matérielle telle que l'omission d'une pièce annexe dont le contenu est relaté aux présentes, les parties agissant dans un intérêt commun donnent tous pouvoirs nécessaires à tout notaire ou à tout collaborateur de l'office notarial dénommé en tête des présentes, à l'effet de faire dresser et signer tous actes complémentaires ou rectificatifs pour mettre le présent acte en concordance avec tous les documents hypothécaires, cadastraux ou d'état civil.

### ELECTION DE DOMICILE

Pour l'exécution des présentes et de leurs suites, les parties font élection de domicile en leurs demeures respectives sus-indiquées.

### AFFIRMATION DE SINCERITE

Les parties affirment, sous les peines édictées à l'article 1837 du Code général des impôts, que le présent acte exprime l'intégralité des valeurs attribuées et elles reconnaissent avoir été informées par le notaire des sanctions fiscales et des peines correctionnelles encourues en cas d'inexactitude de cette affirmation ainsi que des conséquences civiles édictées par l'article 1202 du Code civil.

En outre, le notaire soussigné précise qu'à sa connaissance le présent acte n'est modifié ou contredit par aucune contre-lettre.

### MEDIATION

Les parties sont informées qu'en cas de litige entre elles ou avec un tiers, elles pourront, préalablement à toute instance judiciaire, le soumettre à un médiateur qui sera désigné et missionné par le Centre de médiation notariale dont elles trouveront toutes les coordonnées et renseignements utiles sur le site : https://www.mediation.notaires.fr.

### AUTORISATION DE DESTRUCTION DES DOCUMENTS ET PIECES

Les parties autorisent l'office notarial à détruire toutes pièces et documents pouvant avoir été établis en vue de la conclusion du présent acte, considérant que celui-ci contient l'intégralité des conventions auxquelles elles ont entendu donner le caractère d'authenticité.

### MENTION SUR LA PROTECTION DES DONNEES PERSONNELLES

L'Office notarial traite des données personnelles concernant les personnes mentionnées aux présentes, pour l'accomplissement des activités notariales, notamment de formalités d'actes.

Ce traitement est fondé sur le respect d'une obligation légale et l'exécution d'une mission relevant de l'exercice de l'autorité publique déléguée par l'Etat dont sont investis les notaires, officiers publics, conformément à l'ordonnance n°45-2590 du 2 novembre 1945.

Ces données seront susceptibles d'être transférées aux destinataires suivants :

• les administrations ou partenaires légalement habilités tels que la Direction Générale des Finances Publiques, ou, le cas échéant, le livre foncier, les instances notariales, les organismes du notariat, les fichiers centraux de la profession notariale (Fichier Central Des Dernières Volontés, Minutier Central Électronique des Notaires, registre du PACS, etc.),

• les offices notariaux participant ou concourant à l'acte,

• les établissements financiers concernés,

• les organismes de conseils spécialisés pour la gestion des activités notariales,

• le Conseil supérieur du notariat ou son délégataire, pour la production des statistiques permettant l'évaluation des biens immobiliers, en application du décret n° 2013-803 du 3 septembre 2013,

• les organismes publics ou privés pour des opérations de vérification dans le cadre de la recherche de personnalités politiquement exposées ou ayant fait l'objet de gel des avoirs ou sanctions, de la lutte contre le blanchiment des capitaux et le financement du terrorisme. Ces vérifications font l'objet d'un transfert de données dans un pays situé hors de l'Union Européenne disposant d'une législation sur la protection des données reconnue comme équivalente par la Commission européenne.

La communication de ces données à ces destinataires peut être indispensable pour l'accomplissement des activités notariales.

Les documents permettant d'établir, d'enregistrer et de publier les actes sont conservés 30 ans à compter de la réalisation de l'ensemble des formalités. L'acte authentique et ses annexes sont conservés 75 ans et 100 ans lorsque l'acte porte sur des personnes mineures ou majeures protégées. Les vérifications liées aux personnalités politiquement exposées, au blanchiment des capitaux et au financement du terrorisme sont conservées 5 ans après la fin de la relation d'affaires.

Conformément à la réglementation en vigueur relative à la protection des données personnelles, les intéressés peuvent demander l'accès aux données les concernant. Le cas échéant, ils peuvent demander la rectification ou l'effacement de celles-ci, obtenir la limitation du traitement de ces données ou s'y opposer pour des raisons tenant à leur situation particulière. Ils peuvent également définir des directives relatives à la conservation, à l'effacement et à la communication de leurs données personnelles après leur décès.

L'Office notarial a désigné un Délégué à la protection des données que les intéressés peuvent contacter à l'adresse suivante : dpo.notaires@datavigiprotection.fr.

Si ces personnes estiment, après avoir contacté l'Office notarial, que leurs droits ne sont pas respectés, elles peuvent introduire une réclamation auprès d'une autorité européenne de contrôle, la Commission Nationale de l'Informatique et des Libertés pour la France.

### CERTIFICATION D'IDENTITE

Le notaire soussigné certifie que l'identité complète des parties, personnes physiques, dénommées dans le présent acte, telle qu'elle est indiquée en tête à la suite de leur nom, lui a été régulièrement justifiée.

### FORMALISME LIE AUX ANNEXES

Les annexes, s'il en existe, font partie intégrante de la minute.

Lorsque l'acte est établi sur support papier, les pièces annexées à l'acte sont revêtues d'une mention constatant cette annexe et signée du notaire, sauf si les feuilles de l'acte et des annexes sont réunies par un procédé empêchant toute substitution ou addition.

Si l'acte est établi sur support électronique, la signature du notaire en fin d'acte vaut également pour ses annexes.

**DONT ACTE** sans renvoi

Généré en l'office notarial et visualisé sur support électronique aux lieu, jour, mois et an indiqués en en-tête du présent acte.

Et lecture faite, les parties ont certifié exactes les déclarations les concernant, avant d'apposer leur signature manuscrite sur tablette numérique.

Le notaire, qui a recueilli l'image de leur signature, a lui-même apposé sa signature manuscrite, puis signé l'acte au moyen d'un procédé de signature électronique qualifié.

{{ signature_parties }}
