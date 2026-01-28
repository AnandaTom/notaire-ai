{# ============================================================================
   PARTIE DÉVELOPPÉE DE L'ACTE DE VENTE
   Cette section contient les clauses détaillées : garanties, diagnostics, etc.
   ============================================================================ #}

{% if quotites_acquises|length > 1 %}
### FIXATION DE LA PROPORTION DE PROPRIÉTÉ INDIVISE

#### Proportions entre les acquéreurs

Les **ACQUEREURS** font la présente acquisition sous les proportions indivises suivantes :

{% for quotite in quotites_acquises %}
- {{ acquereurs[quotite.personne_index].civilite }} {{ acquereurs[quotite.personne_index].prenoms }} {{ acquereurs[quotite.personne_index].nom }} à concurrence de **{{ quotite.pourcentage }} %**
{% endfor %}

Ces quotités sont définitives et déterminent le droit de propriété de chacun des **ACQUEREURS**, elles concordent avec la répartition de l'effort de financement entre eux tel que prévu ci-dessous.

#### Détermination de la contribution des acquéreurs au financement

Les **ACQUEREURS** détaillent leurs apports, leurs obligations aux charges vis-à-vis des créanciers et fixent leurs contributions respectives à celles-ci et ce afin d'établir si nécessaire, lors de la liquidation de l'indivision qui s'effectuera au moment de la vente ou du partage du bien, l'existence de créances liées à un excès de contribution.
Ils déclarent que les quotités d'acquisition ont été calculées tenant compte du coût global de l'opération et de la prise en charge de chacun quant à son financement, ainsi qu'il est détaillé ci-après.

#### Coût et financement de l'opération

Le coût et le financement de l'opération sont les suivants :

| | |
| :---- | ----: |
| Prix | {{ prix.montant|format_nombre }} {{ prix.devise }} |
| Frais de la vente | {{ frais_vente|default(19000)|format_nombre }} {{ prix.devise }} |
{% if paiement.prets %}| Frais de prêt | {{ frais_pret|default(1500)|format_nombre }} {{ prix.devise }} |{% endif %}
| **Ensemble** | {{ (prix.montant + frais_vente|default(19000) + frais_pret|default(1500))|format_nombre }} {{ prix.devise }} |
| | |
| **FINANCEMENT** | |
| Fonds personnels | {{ (prix.montant + frais_vente|default(19000) + frais_pret|default(1500) - paiement.fonds_empruntes|default(0))|format_nombre }} {{ prix.devise }} |
{% if paiement.fonds_empruntes %}| Fonds empruntés | {{ paiement.fonds_empruntes|format_nombre }} {{ prix.devise }} |{% endif %}
| | |
| **Ensemble** | {{ (prix.montant + frais_vente|default(19000) + frais_pret|default(1500))|format_nombre }} {{ prix.devise }} |

#### Prise en charge du financement de l'opération

**Fonds personnels**

Le financement du prix et des frais au moyen de leur apport personnel est réalisé par chacun des **ACQUEREURS** à concurrence des sommes suivantes :

{% for quotite in quotites_acquises %}
{% set apport = apports_personnels[quotite.personne_index] if apports_personnels is defined and apports_personnels[quotite.personne_index] is defined else none %}
- {{ acquereurs[quotite.personne_index].civilite }} {{ acquereurs[quotite.personne_index].prenoms }} {{ acquereurs[quotite.personne_index].nom }} apporte {{ apport.montant_lettres if apport else 'sa quote-part' }} ({{ (apport.montant if apport else 0)|format_nombre }} {{ prix.devise }}) provenant de fonds lui appartenant à titre personnel.
{% endfor %}

{% if paiement.fonds_empruntes > 0 %}
**Fonds empruntés**

A ce financement personnel s'ajoute un financement extérieur à concurrence d'une somme empruntée pour un montant de **{{ paiement.fonds_empruntes_lettres }} ({{ paiement.fonds_empruntes|format_nombre }} {{ prix.devise }})** auprès {{ paiement.prets[0].etablissement.nom }}.
Les **ACQUEREURS** sont, au titre de l'obligation à la dette, solidaires de leur remboursement.
La prise en charge de ces remboursements sera assurée par eux de la façon suivante : {% for quotite in quotites_acquises %}**{{ acquereurs[quotite.personne_index].civilite }} {{ acquereurs[quotite.personne_index].prenoms }} {{ acquereurs[quotite.personne_index].nom }}** à concurrence de **{{ quotite.pourcentage }} %**{% if not loop.last %} et {% endif %}{% endfor %}.
Cette convention est inopposable au créancier compte tenu de la solidarité rappelée ci-dessus.
S'il est dérogé à cette convention de répartition, il en sera tenu compte au jour de la liquidation de cette indivision, sous réserve d'en justifier à cette date.
L'assurance décès-invalidité, dans la mesure où elle serait mise en œuvre, profitera en toute hypothèse à l'indivision et ne sera pas constitutive d'une créance.
{% endif %}

#### Prise en charge d'un financement extérieur ultérieur

En cas de financement extérieur ultérieur pour des travaux, il est conseillé aux **ACQUEREURS** d'établir également une convention de ce type afin de prévenir toute difficulté lors de la liquidation de l'indivision. A défaut le financement sera présumé proportionnel aux quotités acquises.

#### Prise en charge d'un financement personnel ultérieur

Si l'un des indivisaires améliore l'état du bien indivis, ou si l'indivision retire un profit des dépenses nécessaires à la conservation de l'immeuble réalisées par l'un des indivisaires seul, ou pour un montant supérieur à sa part dans l'immeuble, il lui en sera tenu compte conformément aux dispositions de l'article 815-13 du Code civil.

#### Industrie personnelle

Il est fait observer que l'industrie personnelle des **ACQUEREURS** (leur travail) et celle de leurs ayants droit dans les travaux effectués, qu'ils soient d'entretien ou non, ne seront ni cause de créance ni cause d'indemnité.

#### Vie courante

Les dépenses d'entretien, les charges courantes, les assurances, les impôts locaux, taxes et autres directement liés à l'usage de l'immeuble, seront supportés, au titre de l'obligation à la dette, par les **ACQUEREURS** sous la même proportionnalité que leurs droits de propriété, sauf à tenir compte de la solidarité en matière fiscale. Il sera tenu compte de la contribution effective de chacun d'entre eux lors de la liquidation de l'indivision, à charge pour le demandeur d'en justifier.

#### Répartition lors de la revente

Il conviendra de distinguer si les sommes empruntées lors de l'acquisition seront ou non remboursées au moment de la revente.

**Les sommes empruntées lors de l'acquisition sont remboursées**
La proportion de propriété telle qu'arrêtée entre les indivisaires aux présentes sera celle qui sera utilisée pour la répartition du prix de revente, sous réserve de l'apurement des comptes pouvant exister entre eux.

**Les sommes empruntées lors de l'acquisition ne sont pas remboursées**
Avant toute répartition entre les indivisaires, seront prélevés sur le prix de vente : l'impôt sur la plus-value éventuelle, les impôts locaux et taxes exigibles ou à valoir, le solde des sommes empruntées, en capital, intérêts et accessoires, ainsi que les charges de toutes sortes exigibles ou estimées liées au bien indivis et à son utilisation, en ce compris le cas échéant les frais attachés à la radiation des inscriptions.
Le reliquat du prix sera ensuite réparti de la manière suivante.
Chaque indivisaire se verra attribuer une quote-part sur le disponible du prix de revente qui correspondra à son financement réel par rapport au financement global, selon la formule suivante :
Solde du prix multiplié par Apports personnels + montant des mensualités pris à sa charge divisé par le Total des apports + total des mensualités réglées.

#### Répartition lors du partage

Il conviendra là aussi de distinguer si les sommes empruntées lors de l'acquisition seront ou non remboursées au moment du partage.

**Les sommes empruntées lors de l'acquisition sont remboursées**
La proportion de propriété telle qu'arrêtée entre les indivisaires aux présentes sera celle qui sera utilisée par rapport à la valeur du bien au jour du partage pour déterminer la soulte, sous réserve de l'apurement des comptes pouvant exister entre eux.

**Les sommes empruntées lors de l'acquisition ne sont pas remboursées**
Avant toute répartition entre les indivisaires, les impôts locaux et taxes exigibles ou à valoir, le solde des sommes empruntées, en capital, intérêts et accessoires, ainsi que les charges de toutes sortes exigibles ou estimées liées au bien indivis et à son utilisation, seront déduits de la valeur du bien indivis au jour de ce partage, en ce compris le cas échéant les frais attachés à la radiation des inscriptions si l'attributaire venait à ne pas reprendre le prêt.

La soulte sera déterminée de la manière suivante.
Chaque indivisaire se verra déterminer sa quote-part sur la valeur du bien indivis qui correspondra à son financement réel par rapport au financement global, selon la formule suivante :
Valeur nette du bien indivis multipliée par Apports personnels + montant des mensualités pris à sa charge divisée par le total des apports + total des mensualités réglées.

Ces conventions sont acceptées par chacun des **ACQUEREURS** indivisaires.
{% endif %}

{% if avant_contrat %}
### Purge de la faculté de rétractation

Les parties ont conclu, en vue de la réalisation de cette vente, {{ "une promesse unilatérale de vente" if avant_contrat.type == "promesse_unilaterale" else "un compromis de vente" }} aux termes d'un acte reçu par {{ avant_contrat.notaire }}, le {{ avant_contrat.date | format_date }}.
En vertu des dispositions de l'article L 271-1 du Code de la construction et de l'habitation, les **BIENS** étant destinés à l'habitation et l'**ACQUEREUR** étant un non-professionnel de l'immobilier, ce dernier bénéficiait de la faculté de se rétracter.

{% if avant_contrat.notification %}
Une copie de l'acte a été notifiée à chacun des acquéreurs avec son accord par lettre recommandée électronique le {{ avant_contrat.notification.date | format_date }}.
Aucune rétractation n'est intervenue de la part des acquéreurs dans le délai légal.
Une copie des courriels de notification ainsi que les accusés de réception sont annexés.

**Annexe n°3 : Courriers de notification et accusés de réception**
{% endif %}
{% endif %}

### Remise des pièces

Pour répondre aux exigences de l'article L 721-2 du Code de la construction et de l'habitation, les pièces suivantes ont été communiquées à l'**ACQUEREUR** :

* Le règlement de copropriété et l'état descriptif de division ainsi que tous leurs modificatifs éventuels publiés.

* Les procès-verbaux des assemblées générales des trois dernières années.

* Les informations financières suivantes :

* Le montant des charges courantes du budget prévisionnel et des charges hors budget prévisionnel payées par le vendeur sur les deux exercices précédant la vente.

* Les sommes susceptibles d'être dues au syndicat des copropriétaires par l'acquéreur.

* L'état global des impayés de charges au sein du syndicat et de la dette envers les fournisseurs.

* La quote-part du fonds de travaux attachée au lot principal vendu et le montant de la dernière cotisation au fonds versée par le vendeur au titre de son lot.

* La fiche synthétique de la copropriété prévue à l'article 8-2 de la loi numéro 65-557 du 10 juillet 1965 dont le contenu est fixé par décret numéro 2016-1822 du 21 décembre 2016.

* Le carnet d'entretien de l'ensemble immobilier.

L'**ACQUEREUR** déclare que ces pièces lui ont été notifiées par lettre recommandée électronique avec accusé de réception dans le cadre de la purge de son délai de rétractation relatée ci-avant.

### CONDITIONS ET DÉCLARATIONS GÉNÉRALES

#### Garantie contre le risque d'éviction

Le **VENDEUR** garantit l'**ACQUEREUR** contre le risque d'éviction conformément aux dispositions de l'article 1626 du Code civil.

A ce sujet le **VENDEUR** déclare :

* qu'il n'existe à ce jour aucune action ou litige en cours pouvant porter atteinte au droit de propriété,

* qu'il n'y a eu aucun empiètement sur le fonds voisin,

* que le **BIEN** ne fait l'objet d'aucune injonction de travaux,

* que le **BIEN** n'a pas fait de sa part l'objet de travaux modifiant l'aspect extérieur de l'immeuble ou les parties communes qui n'auraient pas été régulièrement autorisés par l'assemblée des copropriétaires et les services de l'urbanisme,

* qu'il n'a pas modifié la destination du **BIEN** en contravention des dispositions du règlement de copropriété,

* que le **BIEN** n'a pas été modifié de son fait par une annexion ou une utilisation irrégulière privative de parties communes,

* qu'il n'a conféré à personne d'autre que l'**ACQUEREUR** un droit quelconque sur le **BIEN** pouvant empêcher la vente,

* subroger l'**ACQUEREUR** dans tous ses droits et actions relatifs au **BIEN**.

#### Garantie de jouissance

Le **VENDEUR** déclare qu'il n'a pas délivré de congé à un ancien locataire lui permettant d'exercer un droit de préemption.

#### Garantie hypothécaire

Le **VENDEUR** s'oblige, s'il existe un ou plusieurs créanciers hypothécaires inscrits, à régler l'intégralité des sommes pouvant leur être encore dues, à rapporter à ses frais les certificats de radiation des inscriptions, et à en justifier auprès de l'**ACQUEREUR**.

{% if hypotheques and hypotheques.inscriptions %}
Un état hypothécaire délivré le {{ hypotheques.date_etat | format_date }} révèle :

{% for inscription in hypotheques.inscriptions %}
* Une inscription de {{ inscription.type }} prise au profit de {{ inscription.beneficiaire }}, pour sureté de la somme en principal de {{ inscription.montant_lettres }} ({{ inscription.montant|format_nombre }} {{ prix.devise }}), inscrite au service de la publicité foncière de {{ inscription.service }}, le {{ inscription.date | format_date }}, volume {{ inscription.volume }}, n°{{ inscription.numero }}, avec effet jusqu'au {{ inscription.date_effet | format_date }}.

{% endfor %}

{% if hypotheques.credits_soldes %}
**Etant observé que le notaire soussigné a reçu la réponse du créancier indiquant que les crédits objets des inscriptions ci-avant relatées sont à ce jour soldés, réponse annexée. Le VENDEUR donne l'ordre à son notaire de prélever sur le prix de la vente les frais de mainlevée.**
{% endif %}

Étant précisé que cet état a été complété le {{ hypotheques.date_complement | format_date }}.

Le **VENDEUR** déclare que la situation hypothécaire est identique à la date de ce jour et n'est susceptible d'aucun changement.

**Annexe n°4 : Attestations crédits soldés**
{% endif %}

#### Servitudes

L'**ACQUEREUR** profite ou supporte les servitudes ou les droits de jouissance spéciale, s'il en existe.

Le **VENDEUR** déclare :

* ne pas avoir créé ou laissé créer de servitude ou de droit de jouissance spéciale qui ne seraient pas relatés aux présentes,

* qu'à sa connaissance, il n'existe pas d'autres servitudes ou droits de jouissance spéciale que celles ou ceux résultant, le cas échéant, de l'acte, de la situation naturelle et environnementale des lieux, de l'urbanisme, et du règlement de copropriété et de ses modificatifs,

* ne pas avoir connaissance de faits ou actes tels qu'ils seraient de nature à remettre en cause l'exercice de servitude relatée aux présentes.

#### Etat du bien

L'**ACQUEREUR** prend le **BIEN** dans l'état où il se trouve au jour de l'entrée en jouissance, sans recours contre le **VENDEUR** pour quelque cause que ce soit notamment en raison :

* des vices apparents,

* des vices cachés.

S'agissant des vices cachés, il est précisé que cette exonération de garantie ne s'applique pas :

* si le **VENDEUR** a la qualité de professionnel de l'immobilier ou de la construction, sauf si l'**ACQUEREUR** a également cette qualité,

* ou s'il est prouvé par l'**ACQUEREUR**, dans le délai légal, que les vices cachés étaient en réalité connus du **VENDEUR**.

Toutefois, le **VENDEUR** est avisé que, s'agissant des travaux qu'il a pu exécuter par lui-même, la jurisprudence tend à écarter toute efficacité de la clause d'exonération de garantie des vices cachés.

#### Contenance du terrain d'assiette

Le **VENDEUR** ne confère aucune garantie de contenance du terrain d'assiette de l'ensemble immobilier.

#### Equipements

Le **VENDEUR** déclare qu'à sa connaissance le bien est équipé ou n'est pas équipé des éléments suivants :

{% if equipements is defined %}
| | | OUI | NON | NE SAIT PAS |
| :---: | :---- | :---: | :---: | :---: |
| **1** | Détecteur de fumée | {{ "**X**" if equipements.detecteur_fumee else "" }} | {{ "X" if equipements.detecteur_fumee == false else "" }} | {{ "X" if equipements.detecteur_fumee is none else "" }} |
| **2*** | Cheminée privative à foyer ouvert | {{ "**X**" if equipements.cheminee_ouverte else "" }} | {{ "X" if equipements.cheminee_ouverte == false else "" }} | |
| **3*** | Cheminée privative à foyer fermé / poêle | {{ "**X**" if equipements.cheminee_fermee else "" }} | {{ "X" if equipements.cheminee_fermee == false else "" }} | |
| **4*** | Chaudière individuelle | {{ "**X**" if equipements.chaudiere_individuelle else "" }} | {{ "X" if equipements.chaudiere_individuelle == false else "" }} | |
| | Chaudière Collective | {{ "**X**" if equipements.chaudiere_collective else "" }} | {{ "X" if equipements.chaudiere_collective == false else "" }} | |
| **5* / 6*** | Cuve à fioul ou Cuve à gaz privative | {{ "**X**" if equipements.cuve_fioul_gaz else "" }} | {{ "X" if equipements.cuve_fioul_gaz == false else "" }} | |
| **8*** | Pompe à chaleur ou Climatisation privative | {{ "**X**" if equipements.pac_clim else "" }} | {{ "X" if equipements.pac_clim == false else "" }} | |
| **9* / 10*** | Panneaux photovoltaïques privatifs | {{ "**X**" if equipements.panneaux_pv else "" }} | {{ "X" if equipements.panneaux_pv == false else "" }} | |
| **11*** | Source ou Récupération des eaux de pluies | {{ "**X**" if equipements.recuperation_eau else "" }} | {{ "X" if equipements.recuperation_eau == false else "" }} | |
| **12*/13*** | Puits ou forage privatif | {{ "**X**" if equipements.puits_forage else "" }} | {{ "X" if equipements.puits_forage == false else "" }} | |
| **14*** | WC type broyeur ou chimique | {{ "**X**" if equipements.wc_broyeur else "" }} | {{ "X" if equipements.wc_broyeur == false else "" }} | |
| **15*** | Vidéosurveillance privative | {{ "**X**" if equipements.videosurveillance else "" }} | {{ "X" if equipements.videosurveillance == false else "" }} | |
| **16*** | Alarme privative | {{ "**X**" if equipements.alarme else "" }} | {{ "X" if equipements.alarme == false else "" }} | |
| **17** | Bien raccordé à la Fibre | {{ "**X**" if equipements.fibre else "" }} | {{ "X" if equipements.fibre == false else "" }} | |
| **18** | Point de recharge pour véhicule électrique | {{ "**X**" if equipements.recharge_ve else "" }} | {{ "X" if equipements.recharge_ve == false else "" }} | |
| **19*** | Coffre-fort inséré dans un mur | {{ "**X**" if equipements.coffre_fort else "" }} | {{ "X" if equipements.coffre_fort == false else "" }} | |
| **22 / 23** | Piscine enterrée / hors-sol | {{ "**X**" if equipements.piscine else "" }} | {{ "X" if equipements.piscine == false else "" }} | |
| **24** | Loggia fermée par une baie vitrée | {{ "**X**" if equipements.loggia_fermee else "" }} | {{ "X" if equipements.loggia_fermee == false else "" }} | |
{% else %}
*(informations sur les équipements à compléter)*
{% endif %}

L'**ACQUEREUR**, informé de cette situation, déclare prendre le **BIEN** en l'état.

{% if equipements and equipements.chauffage %}
#### SYSTÈME DE CHAUFFAGE

Le **VENDEUR** déclare que le système de chauffage est {{ equipements.chauffage.description }}.
{% endif %}

#### Impôts et taxes

**Impôts locaux**

Le **VENDEUR** déclare être à jour des mises en recouvrement des impôts locaux.
L'**ACQUEREUR** est redevable à compter de ce jour des impôts et contributions.
La taxe d'habitation sur les résidences secondaires, si elle est exigible, est due pour l'année entière par l'occupant au premier jour du mois de janvier.
La taxe foncière, ainsi que la taxe d'enlèvement des ordures ménagères si elle est due, sont réparties entre le **VENDEUR** et l'**ACQUEREUR** prorata temporis en fonction du temps pendant lequel chacun aura été propriétaire au cours de cette année.

L'**ACQUEREUR** règle ce jour au **VENDEUR** qui le reconnaît, la comptabilité de l'office notarial, les proratas de taxes foncières et, le cas échéant, de taxes d'enlèvement des ordures ménagères, déterminés par convention entre les parties sur le montant de la dernière imposition.
Ce règlement est définitif entre les parties, éteignant toute créance ou dette l'une vis-à-vis de l'autre à ce sujet, quelle que soit la modification éventuelle des taxes foncières pour l'année en cours.

**Avantage fiscal lié à un engagement de location**

Le **VENDEUR** déclare ne pas souscrire actuellement à l'un des régimes fiscaux lui permettant de bénéficier de la déduction des amortissements en échange de l'obligation de louer à certaines conditions.

**Aide personnalisée au logement**

Le **VENDEUR** déclare ne pas avoir conclu de convention avec l'Etat dans le cadre des dispositions applicables aux logements conventionnés à l'égard de l'A.P.L..

**Agence nationale de l'habitat**

Le **VENDEUR** déclare ne pas avoir conclu de convention avec l'agence nationale de l'habitat.

**Obligation déclarative du propriétaire de bien à usage d'habitation**

Conformément à la loi de finances n° 2019-1479 du 28 décembre 2019, une nouvelle obligation déclarative, en vigueur à partir du 1er janvier 2023, a été mise en place à l'égard des propriétaires de biens immobiliers à usage d'habitation, afin de pouvoir déterminer ceux qui sont encore redevables de la taxe d'habitation (pour les résidences secondaires ou logements locatifs) ou de la taxe sur les logements vacants.
Ainsi, à compter du 1er janvier et jusqu'au 30 juin inclus de chaque année, tous les propriétaires, particuliers ou personnes morales, d'une résidence principale ou secondaire ou d'un bien locatif ou vacant, doivent impérativement déclarer à l'administration fiscale :

* s'ils occupent leur logement à titre de résidence principale ou secondaire, ou s'il est vacant,

* lorsque le **BIEN** est occupé par un tiers, l'identité des occupants et la période d'occupation.

Cette obligation déclarative concerne aussi bien les propriétaires indivis, que les usufruitiers ou les sociétés civiles immobilières, et son non-respect est passible de l'octroi d'une amende d'un montant forfaitaire de 150 euros.
Cette déclaration peut s'opérer :

* via le service en ligne "Gérer mes biens immobiliers", accessible depuis le portail impots.gouv.fr,

* ou via les autres moyens mis à disposition par l'administration.

#### Contrats de distribution et de fourniture

L'**ACQUEREUR** fait son affaire personnelle, dès son entrée en jouissance, de la continuation ou de la résiliation de tous contrats de distribution et de fourniture souscrits par le **VENDEUR**.
Les parties déclarent avoir été averties de la nécessité d'établir entre elles un relevé des compteurs faisant l'objet d'un comptage individuel.
Le **VENDEUR** déclare être à jour des factures mises en recouvrement liées à ses contrats de distribution et de fourniture.

#### Assurance

L'**ACQUEREUR**, tout en étant informé de l'obligation immédiate de souscription, ne continuera pas les polices d'assurance actuelles garantissant le **BIEN** et confère à cet effet mandat au **VENDEUR**, qui accepte, de résilier les contrats lorsqu'il avertira son assureur de la réalisation des présentes.
L'ensemble immobilier dans lequel se trouve le **BIEN** étant assuré par une police souscrite par le syndicat des copropriétaires, l'**ACQUEREUR** doit se conformer à toutes les décisions du syndicat la concernant.
Il est rappelé à l'**ACQUEREUR** l'obligation pour chaque copropriétaire de s'assurer contre les risques de responsabilité civile dont il doit répondre en sa qualité soit de copropriétaire occupant, soit de copropriétaire non-occupant.

#### Contrat d'affichage

Le **VENDEUR** déclare qu'il n'a pas été conclu de contrat d'affichage.

{% if quotites_acquises|length > 1 %}
### RAPPEL DES TEXTES EN MATIÈRE D'INDIVISION

Les acquéreurs reconnaissent que le notaire les a parfaitement informés des dispositions légales applicables en matière d'indivision et plus particulièrement du droit de préemption reconnu aux indivisaires en matière de cession à titre onéreux à une personne étrangère à l'indivision.
Pour compléter leur information sont rappelées, ci-après, les dispositions des articles 815, 815-3, 815-5-1, 815-14, 815-16, 815-17 et 815-18 du Code civil.

**Article 815**
*"Nul ne peut être contraint à demeurer dans l'indivision et le partage peut toujours être provoqué, à moins qu'il n'y ait été sursis par jugement ou convention."*

**Article 815-3**
*"Le ou les indivisaires titulaires d'au moins deux tiers des droits indivis peuvent, à cette majorité :
1° Effectuer les actes d'administration relatifs aux biens indivis ;
2° Donner à l'un ou plusieurs des indivisaires ou à un tiers un mandat général d'administration ;
3° Vendre les meubles indivis pour payer les dettes et charges de l'indivision ;
4° Conclure et renouveler les baux autres que ceux portant sur un immeuble à usage agricole, commercial, industriel ou artisanal.
Ils sont tenus d'en informer les autres indivisaires. A défaut, les décisions prises sont inopposables à ces derniers.
Toutefois, le consentement de tous les indivisaires est requis pour effectuer tout acte qui ne ressortit pas à l'exploitation normale des biens indivis et pour effectuer tout acte de disposition autre que ceux visés au 3°.
Si un indivisaire prend en main la gestion des biens indivis, au su des autres et néanmoins sans opposition de leur part, il est censé avoir reçu un mandat tacite, couvrant les actes d'administration mais non les actes de disposition ni la conclusion ou le renouvellement des baux."*

**Article 815-5-1**
*"Sauf en cas de démembrement de la propriété du bien ou si l'un des indivisaires se trouve dans l'un des cas prévus à l'article 836, l'aliénation d'un bien indivis peut être autorisée par le tribunal judiciaire, à la demande de l'un ou des indivisaires titulaires d'au moins deux tiers des droits indivis, suivant les conditions et modalités définies aux alinéas suivants.
Le ou les indivisaires titulaires d'au moins deux tiers des droits indivis expriment devant un notaire, à cette majorité, leur intention de procéder à l'aliénation du bien indivis.
Dans le délai d'un mois suivant son recueil, le notaire fait signifier cette intention aux autres indivisaires. Si l'un ou plusieurs des indivisaires s'opposent à l'aliénation du bien indivis ou ne se manifestent pas dans un délai de trois mois à compter de la signification, le notaire le constate par procès-verbal.
Dans ce cas, le tribunal judiciaire peut autoriser l'aliénation du bien indivis si celle-ci ne porte pas une atteinte excessive aux droits des autres indivisaires.
Cette aliénation s'effectue par licitation. Les sommes qui en sont retirées ne peuvent faire l'objet d'un remploi sauf pour payer les dettes et charges de l'indivision.
L'aliénation effectuée dans les conditions fixées par l'autorisation du tribunal judiciaire est opposable à l'indivisaire dont le consentement a fait défaut, sauf si l'intention d'aliéner le bien du ou des indivisaires titulaires d'au moins deux tiers des droits indivis ne lui avait pas été signifiée selon les modalités prévues au troisième alinéa."*

**Article 815-14**
*"L'indivisaire qui entend céder, à titre onéreux, à une personne étrangère à l'indivision, tout ou partie de ses droits dans les biens indivis ou dans un ou plusieurs de ces biens est tenu de notifier par acte extrajudiciaire aux autres indivisaires le prix et les conditions de la cession projetée ainsi que les nom, domicile et profession de la personne qui se propose d'acquérir.
Tout indivisaire peut, dans le délai d'un mois qui suit cette notification, faire connaître au cédant, par acte extrajudiciaire, qu'il exerce un droit de préemption aux prix et conditions qui lui ont été notifiés.
En cas de préemption, celui qui l'exerce dispose pour la réalisation de l'acte de vente d'un délai de deux mois à compter de la date d'envoi de sa réponse au vendeur. Passé ce délai, sa déclaration de préemption est nulle de plein droit, quinze jours après une mise en demeure restée sans effet, et sans préjudice des dommages-intérêts qui peuvent lui être demandés par le vendeur.
Si plusieurs indivisaires exercent leur droit de préemption, ils sont réputés, sauf convention contraire, acquérir ensemble la portion mise en vente en proportion de leur part respective dans l'indivision.
Lorsque des délais de paiement ont été consentis par le cédant, l'article 828 est applicable."*

**Article 815-16**
*"Est nulle toute cession ou toute licitation opérée au mépris des dispositions des articles 815-14 et 815-15. L'action en nullité se prescrit par cinq ans. Elle ne peut être exercée que par ceux à qui les notifications devaient être faites ou par leurs héritiers."*

**Article 815-17**
*"Les créanciers qui auraient pu agir sur les biens indivis avant qu'il y eût indivision, et ceux dont la créance résulte de la conservation ou de la gestion des biens indivis, seront payés par prélèvement sur l'actif avant le partage. Ils peuvent en outre poursuivre la saisie et la vente des biens indivis.
Les créanciers personnels d'un indivisaire ne peuvent saisir sa part dans les biens indivis, meubles ou immeubles.
Ils ont toutefois la faculté de provoquer le partage au nom de leur débiteur ou d'intervenir dans le partage provoqué par lui. Les coïndivisaires peuvent arrêter le cours de l'action en partage en acquittant l'obligation au nom et en l'acquit du débiteur. Ceux qui exerceront cette faculté se rembourseront par prélèvement sur les biens indivis."*

**Article 815-18**
*"Les dispositions des articles 815 à 815-17 sont applicables aux indivisions en usufruit en tant qu'elles sont compatibles avec les règles de l'usufruit.
Les notifications prévues par les articles 815-14, 815-15 et 815-16 doivent être adressées à tout nu-propriétaire et à tout usufruitier. Mais un usufruitier ne peut acquérir une part en nue-propriété que si aucun nu-propriétaire ne s'en porte acquéreur; un nu-propriétaire ne peut acquérir une part en usufruit que si aucun usufruitier ne s'en porte acquéreur."*
{% endif %}

### DISPOSITIONS RELATIVES À L'URBANISME

#### Urbanisme

**Note d'urbanisme**
{% if urbanisme and urbanisme.note_urbanisme %}
La commune a répondu le {{ urbanisme.note_urbanisme.date | format_date }} à une demande de note d'urbanisme. Cette réponse est annexée.
{% endif %}

L'**ACQUEREUR** s'oblige à faire son affaire personnelle de l'exécution des charges et prescriptions, du respect des servitudes publiques et autres limitations administratives au droit de propriété mentionnées sur cette note.

**Annexe n°5 : Note d'urbanisme**

{% if urbanisme and urbanisme.note_urbanisme and urbanisme.note_urbanisme.revelations %}
La note d'urbanisme révèle :
{% for revelation in urbanisme.note_urbanisme.revelations %}
\- {{ revelation }}
{% endfor %}
{% endif %}

{% if urbanisme and urbanisme.note_voirie %}
**Note de voirie**
Une note de renseignements de voirie annexée a été délivrée par l'autorité compétente le {{ urbanisme.note_voirie.date | format_date }}. Il résulte de cette note que « *{{ urbanisme.note_voirie.resultat }}* ».

**Annexe n°6 : Note de voirie**
{% endif %}

{% if urbanisme and urbanisme.certificat_non_peril %}
**Certificat de non-péril**
Il résulte d'un certificat délivré par l'autorité compétente le {{ urbanisme.certificat_non_peril.date | format_date }}, annexé, que l'immeuble {{ urbanisme.certificat_non_peril.resultat }}.

**Annexe n°7 : Certificat de non-péril**
{% endif %}

### DISPOSITIONS RELATIVES À LA PRÉEMPTION

#### Droit de préemption urbain

La vente ne donne pas ouverture au droit de préemption urbain, le **BIEN** constituant un seul local à usage d'habitation avec ses locaux accessoires dans un bâtiment dont le règlement de copropriété a été publié depuis plus de dix ans au fichier immobilier (article L 211-4, a, du Code de l'urbanisme) ou, à défaut de règlement de copropriété, si l'état descriptif de division a été publié depuis plus de dix ans au fichier immobilier.
En outre, il résulte des documents d'urbanisme obtenus que la commune n'a pas pris de délibération motivée pour déroger à ces dispositions légales.

### DISPOSITIONS RELATIVES À LA CONSTRUCTION

#### Existence de travaux

Le **VENDEUR** déclare être informé des dispositions des articles L 241-1 et L 242-1 du Code des assurances imposant à tout propriétaire de souscrire avant toute ouverture de chantier de construction et/ou travaux de gros oeuvre ou de second oeuvre, une assurance garantissant le paiement des travaux de réparation des dommages relevant de la garantie décennale, ainsi qu'une assurance couvrant sa responsabilité au cas où il interviendrait dans la construction en tant que concepteur, entrepreneur ou maître d'oeuvre.

{% if travaux and travaux.realises %}
Depuis son acquisition, le **VENDEUR** déclare que les travaux ci-après indiqués ont été effectués :
{% for travail in travaux.realises %}
\- **{{ travail.description }}** suivant facture du {{ travail.date_facture | format_date }} de {{ travail.entreprise }}. {{ travail.observations|default('') }}
{% endfor %}

{% if travaux.annexes %}
**Annexe n°8 : Courriels de demande d'attestation décennale**
**Annexe n°9 : Factures et décennales**
{% endif %}
{% endif %}

Les travaux, compte tenu de la description faite par le **VENDEUR**, ne nécessitaient pas de déclaration préalable.

Il est précisé qu'une déclaration préalable de travaux est nécessaire dans les cas suivants :

* travaux qui créent entre 5 m² ou 20 m² de surface de plancher ou d'emprise au sol. Le seuil de 20 m² est porté à 40 m² si la construction est située dans une zone urbaine d'une commune couverte par un plan local d'urbanisme (PLU) ou un document assimilé. Toutefois, entre 20 et 40 m² de surface de plancher ou d'emprise au sol, un permis de construire est exigé si, après réalisation, la surface ou l'emprise totale de la construction dépasse 150 m²,

* travaux ayant pour effet de modifier l'aspect extérieur d'un bâtiment existant, à l'exception des travaux de ravalement,

* travaux changeant la destination d'un bâtiment (par exemple, transformation d'un local commercial en local d'habitation) même lorsque celle-ci n'implique pas de travaux.

Le **VENDEUR** confirme que les travaux effectués n'entrent pas dans l'un des cas ci-dessus.
Le **VENDEUR** est averti que celui qui a réalisé un ouvrage est réputé en connaître les vices et doit donc être assimilé à un sachant et cela même s'il n'a pas la qualité de professionnel. Si un dysfonctionnement, inconnu de l'**ACQUEREUR** et préexistant à la vente survient par la suite, le **VENDEUR** est constitué de mauvaise foi. L'**ACQUEREUR** a alors un délai de deux ans pour agir à compter de la découverte du vice.
L'**ACQUEREUR** est averti de l'importance de se faire fournir par le **VENDEUR** toutes les factures de ces travaux.

#### Rappel des articles 1792 et suivants

**Article 1792**
*Tout constructeur d'un ouvrage est responsable de plein droit, envers le maître ou l'acquéreur de l'ouvrage, des dommages, même résultant d'un vice du sol, qui compromettent la solidité de l'ouvrage ou qui, l'affectant dans l'un de ses éléments constitutifs ou l'un de ses éléments d'équipement, le rendent impropre à sa destination. Une telle responsabilité n'a point lieu si le constructeur prouve que les dommages proviennent d'une cause étrangère.*

**Article 1792-1**
*Est réputé constructeur de l'ouvrage :
1° Tout architecte, entrepreneur, technicien ou autre personne liée au maître de l'ouvrage par un contrat de louage d'ouvrage ;
2° Toute personne qui vend, après achèvement, un ouvrage qu'elle a construit ou fait construire ;
3° Toute personne qui, bien qu'agissant en qualité de mandataire du propriétaire de l'ouvrage, accomplit une mission assimilable à celle d'un locateur d'ouvrage.*

**Article 1792-2**
*La présomption de responsabilité établie par l'article 1792 s'étend également aux dommages qui affectent la solidité des éléments d'équipement d'un ouvrage, mais seulement lorsque ceux-ci font indissociablement corps avec les ouvrages de viabilité, de fondation, d'ossature, de clos ou de couvert. Un élément d'équipement est considéré comme formant indissociablement corps avec l'un des ouvrages de viabilité, de fondation, d'ossature, de clos ou de couvert lorsque sa dépose, son démontage ou son remplacement ne peut s'effectuer sans détérioration ou enlèvement de matière de cet ouvrage.*

**Article 1792-3**
*Les autres éléments d'équipement de l'ouvrage font l'objet d'une garantie de bon fonctionnement d'une durée minimale de deux ans à compter de sa réception.*

**Article 1792-4-1**
*Toute personne physique ou morale dont la responsabilité peut être engagée en vertu des articles 1792 à 1792-4 du présent code est déchargée des responsabilités et garanties pesant sur elle, en application des articles 1792 à 1792-2, après dix ans à compter de la réception des travaux ou, en application de l'article 1792-3, à l'expiration du délai visé à cet article.*

{% if travaux and travaux.assurance_do %}
#### Assurance dommages ouvrage

Le **BIEN** ayant fait l'objet de travaux de rénovation depuis moins de dix ans tels que ceux déclarés par le vendeur, le régime de la responsabilité et d'assurance auquel il se trouve soumis est celui institué par les articles L 241-1 et suivants du Code des assurances.

{% if not travaux.assurance_do.souscrite %}
**Le VENDEUR déclare qu'aucune police d'assurance dommages ouvrage n'a été souscrite pour la réalisation de ces rénovations.**

L'**ACQUEREUR** a été informé que :
Les articles L 241-2 et L 242-1 du Code des assurances ont prévu que les constructions soumises au régime de la responsabilité qu'elle organise doivent être protégées par deux régimes d'assurances :
\- assurance de responsabilité : elle ne paie que dans la mesure où la responsabilité de celui qu'elle garantit est retenue,
\- assurance de dommages : elle est destinée à fournir les fonds nécessaires pour réparer les dommages aux constructions en dehors de toute recherche de responsabilité. Elle permet au propriétaire de l'immeuble d'éviter de mettre en jeu les responsabilités incombant aux divers intervenants à la construction, avec les risques d'un contentieux long et onéreux.

**VENDEUR** et **ACQUEREUR** reconnaissent avoir reçu du notaire soussigné toutes explications utiles concernant les conséquences pouvant résulter de l'absence de souscription de telles polices d'assurances.
{% endif %}
{% endif %}

{% if not travaux or not travaux.realises %}
#### Absence d'opération de construction ou de rénovation depuis dix ans

Le **VENDEUR** déclare qu'à sa connaissance :

* aucune construction, aucune rénovation et aucuns travaux entrant dans le champ d'application des dispositions des articles L 241-1 et L 242-1 du Code des assurances n'ont été effectués dans les dix dernières années.

* aucun élément constitutif d'ouvrage ou équipement indissociable de l'ouvrage au sens de l'article 1792 du Code civil n'a été réalisé dans ce délai.
{% endif %}

### DIAGNOSTICS

#### Diagnostics techniques

**Plomb**

L'ENSEMBLE IMMOBILIER a été construit depuis le 1er janvier 1949, en conséquence il n'entre pas dans le champ d'application des dispositions des articles L 1334-5 et suivants du Code de la santé publique relatifs à la lutte contre la présence de plomb.

**Amiante**

L'article L 1334-13 premier alinéa du Code de la santé publique commande au **VENDEUR** de faire établir un état constatant la présence ou l'absence de matériaux ou produits de la construction contenant de l'amiante.
Cet état s'impose à tous les bâtiments dont le permis de construire a été délivré avant le 1er juillet 1997.
Il doit être intégré au dossier de diagnostics techniques, annexé à l'avant-contrat, ou à défaut, à l'acte authentique de vente.

Il a pour objet de repérer :

* les matériaux et produits de la liste A (dits matériaux friables tels que les flocages, calorifugeages et faux plafonds),

* et les matériaux et produits de la liste B (dits matériaux non friables y compris les produits situés en extérieur tels que les matériaux de couverture, les bardages, les conduits de fumée etc.) de l'annexe 13-9 du Code de la santé publique.

Des recommandations sont préconisées au propriétaire dans ce rapport en fonction du résultat du repérage et de l'état de conservation des éléments contenant de l'amiante.

{% if diagnostics and diagnostics.amiante_pp %}
**Pour les parties privatives**
Un état établi par {{ diagnostics.amiante_pp.diagnostiqueur }} le {{ diagnostics.amiante_pp.date }}, accompagné de la certification de compétence, est annexé.
**{{ diagnostics.amiante_pp.resultat }}**

**Annexe n°10 : Synthèse et diagnostic amiante parties privatives**
{% endif %}

{% if diagnostics and diagnostics.amiante_pc %}
**Pour les parties communes**
Un diagnostic technique a été établi par {{ diagnostics.amiante_pc.diagnostiqueur }} le {{ diagnostics.amiante_pc.date }}.
Les conclusions sont les suivantes : ***"{{ diagnostics.amiante_pc.resultat }}"***
Ce diagnostic porte sur les points visés par le décret n° 2011-629 du 3 juin 2011.

**Annexe n°11 : Diagnostic amiante parties communes**
{% endif %}

**Termites**

Le **VENDEUR** déclare :

* qu'à sa connaissance le **BIEN** n'est pas infesté par les termites ;

* qu'il n'a lui-même procédé ni fait procéder par une entreprise à un traitement curatif contre les termites ;

* qu'il n'a reçu du maire aucune injonction de rechercher des termites ou de procéder à des travaux préventifs ou d'éradication ;

* que le **BIEN** n'est pas situé dans une zone contaminée par les termites.

**Mérules**

Les parties ont été informées des dégâts pouvant être occasionnés par la présence de mérules dans un bâtiment, la mérule étant un champignon qui se développe dans l'obscurité, en espace non ventilé et en présence de bois humide.

Le **BIEN** ne se trouve pas actuellement dans une zone de présence d'un risque de mérule délimitée par un arrêté préfectoral.
Le **VENDEUR** déclare ne pas avoir constaté l'existence de zones de condensation interne, de moisissures ou encore de présence d'effritements ou de déformation dans le bois ou l'existence de filaments blancs à l'aspect cotonneux, tous des éléments parmi les plus révélateurs de la potentialité de la présence de ce champignon.

{% if diagnostics and diagnostics.gaz %}
**Contrôle de l'installation de gaz**

Conformément aux dispositions de l'article L 134-9 du Code de la construction et de l'habitation, la vente d'un bien immobilier à usage d'habitation comportant une installation intérieure de gaz réalisée depuis plus de quinze ans doit être précédée d'un diagnostic de celle-ci.

{% if diagnostics.gaz.existe %}
Un état de l'installation de gaz a été établi par {{ diagnostics.gaz.diagnostiqueur }} le {{ diagnostics.gaz.date }}.
Les conclusions sont les suivantes : ***"{{ diagnostics.gaz.resultat }}"***
{% else %}
Les parties déclarent que le **BIEN** ne possède pas d'installation intérieure de gaz.
{% endif %}
{% endif %}

{% if diagnostics and diagnostics.electricite and diagnostics.electricite.requis %}
**Contrôle de l'installation intérieure d'électricité**

Conformément aux dispositions de l'article L 134-7 du Code de la construction et de l'habitation, la vente d'un bien immobilier à usage d'habitation comportant une installation intérieure d'électricité réalisée en tout ou partie depuis plus de quinze ans doit être précédée d'un diagnostic de celle-ci.

Le **BIEN** dispose d'une installation intérieure électrique au moins pour partie de plus de quinze ans.
Le **VENDEUR** a fait établir un état de celle-ci par {{ diagnostics.diagnostiqueur.nom }} - {{ diagnostics.diagnostiqueur.adresse }} répondant aux critères de l'article L 271-6 du Code de la construction et de l'habitation, le {{ diagnostics.electricite.date }}, annexé.
Les conclusions sont les suivantes : ***"{{ diagnostics.electricite.resultat }}"***

**Annexe n°12 : Diagnostic électricité**

Il est rappelé à l'**ACQUEREUR** qu'en cas d'accidents électriques consécutifs aux anomalies pouvant être révélées par l'état annexé, sa responsabilité pourrait être engagée tant civilement que pénalement, de la même façon que la compagnie d'assurances pourrait invoquer le défaut d'aléa afin de refuser de garantir le sinistre électrique. D'une manière générale, le propriétaire au jour du sinistre est seul responsable de l'état du système électrique.
{% endif %}

{% if diagnostics and diagnostics.dpe %}
**Diagnostic de performance énergétique**

Conformément aux dispositions des articles L 126-26 et suivants du Code de la construction et de l'habitation, un diagnostic de performance énergétique doit être établi.
Ce diagnostic doit notamment permettre d'évaluer :

* Les caractéristiques du logement ainsi que le descriptif des équipements.

* Le descriptif des équipements de chauffage, d'eau chaude sanitaire, de refroidissement, et indication des conditions d'utilisation et de gestion.

* La valeur isolante du **BIEN** immobilier.

* La consommation d'énergie et l'émission de gaz à effet de serre.

Il existe 7 classes d'énergie de "A" (**BIEN** économe) à "G" (**BIEN** énergivore).

Les logements mis en location doivent respecter des critères de décence énergétique répondant à un niveau de performance minimal prévu par l'article 6 de la loi du 6 juillet 1989.

Ainsi, depuis le 1er janvier 2025, la location des logements d'habitation avec un DPE de classe G est interdite. A compter du 1er janvier 2028, cette interdiction s'étendra aux logements de classe F, et à partir du 1er janvier 2034 aux logements de classe E. Aucune révision, majoration ou réévaluation du loyer n'est possible pour les logements d'habitation classés F ou G.

Un diagnostic établi par {{ diagnostics.diagnostiqueur.nom }} - {{ diagnostics.diagnostiqueur.adresse }} le {{ diagnostics.dpe.date }}, est annexé.

Les conclusions sont les suivantes :

* Consommation énergétique : {{ diagnostics.dpe.consommation_energie }} kWhep/m².an

* Émissions de gaz à effet de serre : {{ diagnostics.dpe.emission_ges }} kg éqCO2/m².an

* Numéro ADEME : {{ diagnostics.dpe.numero_ademe }}

**Annexe n°13 : Diagnostic de performance énergétique**
{% endif %}

**Carnet d'information du logement**

Conformément aux dispositions des articles L 126-35-2 à L 126-35-11 et R 126-32 à R 126-34 du Code de la construction et de l'habitation, un carnet d'information du logement, s'il est à usage d'habitation, doit être établi par le propriétaire ou le maître de l'ouvrage lors de sa construction ou à l'occasion de la réalisation de travaux de rénovation ayant une incidence significative sur sa performance énergétique, sous réserve que ces constructions ou travaux aient débuté à compter du 1er janvier 2023.
Le contenu de ce carnet est fixé par les textes susvisés.
L'**ACQUEREUR** déclare avoir été informé, par le notaire soussigné, de l'obligation d'établir ledit carnet et de le transmettre au nouveau propriétaire lors de toute mutation du logement tel qu'il est au moment de la mutation.

{% if carnet_information_logement and carnet_information_logement.etabli %}
Le **VENDEUR** déclare que le **BIEN** dont il s'agit entre dans le champ d'application des articles L 126-35-2 et suivants du Code de la construction et de l'habitation, en conséquence, le carnet d'information du logement a été établi conformément aux articles R 126-32 à R 126-34 dudit Code par le **VENDEUR**, **dont la remise sera effectuée sous huit jours aux nouveaux propriétaires.**
{% endif %}

Le nouveau propriétaire est informé qu'il devra mettre à jour ce carnet en cas d'extension du logement ou de travaux de rénovation ayant une incidence significative sur la performance énergétique celui-ci.

**Audit énergétique**

Le **BIEN** objet des présentes relevant de la loi n° 65-557 du 10 juillet 1965 fixant le statut de la copropriété des immeubles bâtis, il n'entre pas dans le champ d'application des dispositions de l'article L 126-28-1 du Code de la construction et de l'habitation, par suite il n'a pas été établi d'audit énergétique.

**Zone de bruit - Plan d'exposition au bruit des aérodromes**

L'immeuble ne se trouve pas dans une zone de bruit définie par un plan d'exposition au bruit des aérodromes, prévu par l'article L 112-6 du Code de l'urbanisme ainsi qu'il résulte de l'Etat des Nuisances Sonores Aériennes établi le {{ diagnostics.etat_risques.date|default('') }} et intégré à l'état des risques ci-après relaté.

**Radon**

Le radon est un gaz radioactif d'origine naturelle qui représente le tiers de l'exposition moyenne de la population française aux rayonnements ionisants.
Il est issu de la désintégration de l'uranium et du radium présents dans la croûte terrestre.
Il est présent partout à la surface de la planète et provient surtout des sous-sols granitiques et volcaniques ainsi que de certains matériaux de construction.
Le radon peut s'accumuler dans les espaces clos, notamment dans les maisons. Les moyens pour diminuer les concentrations en radon dans les maisons sont simples :

* aérer et ventiler les bâtiments, les sous-sols et les vides sanitaires,

* améliorer l'étanchéité des murs et planchers.

L'activité volumique du radon (ou concentration de radon) à l'intérieur des habitations s'exprime en becquerel par mètre cube (Bq/m3).

L'article L 1333-22 du Code de la santé publique dispose que les propriétaires ou exploitants d'immeubles bâtis situés dans les zones à potentiel radon où l'exposition au radon est susceptible de porter atteinte à la santé sont tenus de mettre en oeuvre les mesures nécessaires pour réduire cette exposition et préserver la santé des personnes.
Aux termes des dispositions de l'article R 1333-29 de ce Code le territoire national est divisé en trois zones à potentiel radon définies en fonction des flux d'exhalation du radon des sols :

* Zone 1 : zones à potentiel radon faible.

* Zone 2 : zones à potentiel radon faible mais sur lesquelles des facteurs géologiques particuliers peuvent faciliter le transfert du radon vers les bâtiments.

* Zone 3 : zones à potentiel radon significatif.

L'article R 125-23 5° du Code de l'environnement dispose que l'obligation d'information s'impose dans les zones à potentiel radon de niveau 3.

La liste des communes réparties entre ces trois zones est fixée par un arrêté du 27 juin 2018.

La commune se trouvant **en zone 1 (faible),** l'obligation d'information n'est pas nécessaire, ainsi qu'il résulte de l'état des risques ci-annexé.

#### Diagnostics environnementaux

**Assainissement**

**En ce qui concerne l'installation de l'ensemble immobilier dont dépendent les biens objet des présentes :**
Le **VENDEUR** déclare que l'**ENSEMBLE IMMOBILIER** est raccordé à un réseau d'assainissement collectif des eaux usées domestiques conformément aux dispositions de l'article L 1331-1 du Code de la santé publique.
Aux termes des dispositions des articles L 1331-4 et L 1331-6 de ce Code, les parties sont informées que l'entretien et le bon fonctionnement des ouvrages permettant d'amener les eaux usées domestiques de l'immeuble à la partie publique sont soumis au contrôle de la commune, qui peut procéder sous astreinte et aux frais du syndicat des copropriétaires, répartis entre les copropriétaires en fonction de leur quote-part, aux travaux indispensables à ces effets.
Il est, en outre, précisé que le système d'écoulement des eaux pluviales doit être distinct de l'installation d'évacuation des eaux usées, étant spécifié que le régime d'évacuation des eaux pluviales est fixé par le règlement sanitaire départemental.
L'évacuation des eaux pluviales doit être assurée et maîtrisée en permanence, elles ne doivent pas être versées sur les fonds voisins et la voie publique.

**En ce qui concerne l'installation intérieure des biens vendus :**
Le **VENDEUR** déclare que le **BIEN** vendu est relié aux canalisations collectives de l'**ENSEMBLE IMMOBILIER** dont il dépend et qu'il ne constate pas de difficultés d'utilisation.
Il précise, par ailleurs, qu'il n'existe pas d'installation de type "sanibroyeur" ou de toilettes chimiques.

Le **VENDEUR** informe l'**ACQUEREUR** qu'à sa connaissance les ouvrages permettant d'amener les eaux usées domestiques de l'**ENSEMBLE IMMOBILIER** à la partie publique ne présentent pas d'anomalie ni aucune difficulté particulière d'utilisation, et que l'évacuation des eaux pluviales s'effectue sans difficulté et sans nuisance.

{% if diagnostics and diagnostics.etat_risques %}
**Etat des risques**

Un état des risques en date du {{ diagnostics.etat_risques.date }} est annexé.

**Annexe n°14 : Etat des risques**

**Absence de sinistres avec indemnisation**
Le **VENDEUR** déclare qu'à sa connaissance l'immeuble n'a pas subi de sinistres ayant donné lieu au versement d'une indemnité en application de l'article L 125-2 ou de l'article L 128-2 du Code des assurances.
{% endif %}

**SITUATION ENVIRONNEMENTALE**

**Consultation de bases de données environnementales**

Les bases de données suivantes ont été consultées :

* La base de données relative aux anciens sites industriels et activités de service (BASIAS).

* La base de données relative aux sites et sols pollués ou potentiellement pollués appelant une action des pouvoirs publics, à titre préventif ou curatif (BASOL).

* La base de données relative aux risques naturels et technologiques (Géorisques).

* La base de données des installations classées soumises à autorisation ou à enregistrement du ministère de l'Environnement, de l'énergie et de la mer.

* La base de données dédiée aux anciens sites miniers d'uranium (Mimausa)

* La base de données sur les risques naturels GEODERIS.

* La base de données relative à la localisation des déchets radioactifs produits en France.

Une copie de ces consultations est annexée.

**Annexe n°15 : Données environnementales**

### REGLEMENTATIONS SPECIFIQUES A LA COPROPRIETE

Un certificat du syndic de la copropriété, délivré en application de l'article 20 II de la loi n° 65-557 du 10 juillet 1965, atteste que l'**ACQUEREUR** et son conjoint, ou partenaire lié à lui par un pacte civil de solidarité, ne sont pas déjà propriétaires d'un lot dans l'ensemble immobilier dont il s'agit.
Ce certificat est annexé ci-après.
L'article 20 II précise en tant que de besoin que le terme "acquéreur" s'entend tant de lui-même, s'il s'agit d'une personne physique, que des mandataires sociaux et associés de la société, s'il s'agit d'une personne morale.

**Annexe n°16 : Certificat article 20 II**

#### Immatriculation du syndicat des copropriétaires

L'article L 711-1 du Code de la construction et de l'habitation institue un registre auquel sont immatriculés les syndicats de copropriétaires définis à l'article 14 de la loi n° 65-557 du 10 juillet 1965 fixant le statut de la copropriété des immeubles bâtis, qui administrent des immeubles à destination partielle ou totale d'habitation.

Le syndicat des copropriétaires est immatriculé sous le numéro **{{ copropriete.immatriculation }}**.

**Annexe n°17 : Attestation d'immatriculation**

#### Carnet d'entretien de l'ensemble immobilier

Un carnet d'entretien de l'ensemble immobilier doit être tenu par le syndic.

Ce carnet d'entretien a pour objet de mentionner :

* si des travaux importants ont été réalisés,

* si des contrats d'assurance dommages souscrits par le syndicat des copropriétaires sont en cours,

* s'il existe des contrats d'entretien et de maintenance des équipements communs,

* l'échéancier du programme pluriannuel de travaux décidés par l'assemblée générale s'il en existe un.

L'état délivré par le syndic révèle l'existence du carnet d'entretien.

#### Diagnostic technique global

Le 1er alinéa de l'article L 731-1 du Code de la construction et de l'habitation dispose que :
*"Afin d'assurer l'information des copropriétaires sur la situation technique générale de l'immeuble et, le cas échéant, aux fins d'élaboration d'un plan pluriannuel de travaux, l'assemblée générale des copropriétaires se prononce sur la question de faire réaliser par un tiers, disposant de compétences précisées par décret, un diagnostic technique global pour tout immeuble à destination partielle ou totale d'habitation relevant du statut de la copropriété."*

L'article L 731-4 du Code de la construction et de l'habitation dispose que :
*"Toute mise en copropriété d'un immeuble construit depuis plus de dix ans est précédée du diagnostic technique global prévu à l'article L. 731-1."*

Ce dossier doit comporter :

* une analyse de l'état apparent des parties communes et des équipements communs de l'immeuble,

* un état technique de l'immeuble et des équipements communs au regard des obligations légales et réglementaires au titre de la construction,

* une analyse des améliorations possibles de la gestion technique et patrimoniale de l'immeuble,

* un diagnostic de performance énergétique de l'immeuble tel que prévu par les dispositions des articles L 126-28 ou L 126-31 du Code de la construction et de l'habitation.

L'autorité administrative compétente peut à tout moment, pour vérifier l'état de bon usage et de sécurité des parties communes d'un immeuble collectif à usage principal d'habitation soumis au statut de la copropriété présentant des désordres potentiels, demander au syndic de produire ce diagnostic. À défaut de sa production dans un délai d'un mois après notification de la demande, l'autorité administrative compétente mentionnée peut le faire réaliser d'office en lieu et place du syndicat des copropriétaires et à ses frais.

{% if copropriete.diagnostic_technique_global and copropriete.diagnostic_technique_global.etabli %}
Le vendeur déclare que le diagnostic technique global **a été établi.**
{% else %}
Le vendeur déclare que le diagnostic technique global **n'a pas été établi.**

Le notaire précise que l'absence d'un tel diagnostic ne permet pas à l'**ACQUEREUR** d'apprécier valablement l'importance matérielle et financière des dépenses à prévoir dans la copropriété dans les années à venir.
{% endif %}

#### Plan pluriannuel de travaux

L'article 14-2 de la loi n° 65-557 du 10 juillet 1965 dispose notamment ce qui suit :
*"I.- A l'expiration d'un délai de quinze ans à compter de la date de réception des travaux de construction de l'immeuble, un projet de plan pluriannuel de travaux est élaboré dans les immeubles à destination partielle ou totale d'habitation soumis à la présente loi. Il est actualisé tous les dix ans."*

{% if copropriete.plan_pluriannuel_travaux and copropriete.plan_pluriannuel_travaux.existe %}
Le vendeur déclare **qu'il existe** un plan pluriannuel de travaux.
{% else %}
Le vendeur déclare **qu'il n'existe pas** de plan pluriannuel de travaux.
{% endif %}

{% if copropriete.fiche_synthetique %}
#### Fiche synthétique

La fiche synthétique de la copropriété est prévue par les dispositions de l'article 8-2 de la loi numéro 65-557 du 10 juillet 1965 dont le contenu est fixé par décret numéro 2016-1822 du 21 décembre 2016. Elle est obligatoire pour les immeubles qui sont à usage total ou partiel d'habitation et doit être établie et mise à jour annuellement par le syndic.

La fiche synthétique a été établie le **{{ copropriete.fiche_synthetique.date }}** dont une copie est annexée.

**Annexe n°18 : Fiche synthétique**
{% endif %}

{% if copropriete.emprunt_collectif and copropriete.emprunt_collectif.existe %}
#### Emprunt collectif

Les articles 26-4 à 26-14 de la loi numéro 65-557 du 10 juillet 1965 donnent la possibilité aux syndicats de copropriétaires de souscrire un emprunt bancaire en leur nom propre en vue de financer non seulement des travaux sur les parties communes de l'immeuble, mais également des travaux d'intérêt collectif sur les parties privatives, des acquisitions de biens conformes à l'objet du syndicat, ou d'assurer le préfinancement de subventions publiques accordées pour la réalisation des travaux votés.

**L'état délivré par le syndic révèle l'existence d'un tel type d'emprunt souscrit, le solde étant en principal et intérêts à la date du {{ copropriete.emprunt_collectif.date_solde | format_date }} de {{ copropriete.emprunt_collectif.solde | format_nombre }} EUR.**

**Le VENDEUR est informé de l'exigibilité de cet emprunt en cas de mutation. Par suite, il donne son accord au notaire détenteur du prix de vente de régler au syndic, par prélèvement sur ce prix, le montant dû afin que ce dernier l'affecte au remboursement de l'emprunt, de sorte que le syndicat et l'ACQUEREUR ne puissent ni être recherchés ni être inquiétés.**
{% endif %}

{% if copropriete.fonds_travaux and copropriete.fonds_travaux.existe %}
#### Fonds de travaux

L'article 14-2-1 de la loi numéro 65-557 du 10 juillet 1965 instaure la création d'un fonds de travaux pour les immeubles soumis au régime de la copropriété et à usage d'habitation en tout ou partie.
Le syndicat des copropriétaires constitue un fonds de travaux au terme d'une période de dix ans à compter de la date de la réception des travaux de construction de l'immeuble, pour faire face aux dépenses résultant :

* De l'élaboration du projet de plan pluriannuel de travaux mentionné à l'article 14-2 de ladite loi et, le cas échéant, du diagnostic technique global mentionné à l'article L 731-1 du Code de la construction et de l'habitation ;

* De la réalisation des travaux prévus dans le plan pluriannuel de travaux adopté par l'assemblée générale des copropriétaires ;

* Des travaux décidés par le syndic en cas d'urgence, dans les conditions prévues au troisième alinéa du I de l'article 18 de la présente loi ;

* Des travaux nécessaires à la sauvegarde de l'immeuble, à la préservation de la santé et de la sécurité des occupants et à la réalisation d'économies d'énergie, non prévus dans le plan pluriannuel de travaux.

Ce fonds de travaux est alimenté par une cotisation annuelle obligatoire. Chaque copropriétaire contribue au fonds selon les mêmes modalités que celles décidées par l'assemblée générale pour le versement des provisions du budget prévisionnel.
Ces sommes sont définitivement acquises au syndicat, la cession des lots ne donne donc pas lieu à leur remboursement par le syndicat.
Lorsque le montant du fonds de travaux sera supérieur à celui du budget prévisionnel le syndic inscrira, à l'ordre du jour de l'assemblée générale, l'élaboration d'un plan pluriannuel de travaux et la suspension des cotisations en fonction des décisions prises par cette assemblée sur le plan de travaux.

L'immeuble entre dans le champ d'application de l'obligation de créer un fonds de travaux.
{% endif %}

#### Garantie de superficie

Conformément aux dispositions de l'article 46 de la loi du 10 juillet 1965, tout contrat réalisant ou constatant la vente d'un lot ou d'une fraction de lot mentionne la superficie de la partie privative de ce lot ou de cette fraction de lot. La nullité de l'acte peut être invoquée sur le fondement de l'absence de toute mention de superficie.
Ces dispositions ne sont pas applicables aux caves, garages, emplacements de stationnement ni aux lots ou fractions de lots d'une superficie inférieure à 8 mètres carrés.
Le **VENDEUR** déclare que la superficie de la partie privative des **BIENS** soumis à la loi ainsi qu'à ses textes subséquents, est de savoir **{{ bien.superficie_carrez.superficie_m2 }} M²** pour le lot numéro {{ bien.superficie_carrez.lot_concerne|upper }}.

{% if bien.superficie_carrez.diagnostiqueur %}
Ainsi qu'il résulte d'une attestation établie par {{ bien.superficie_carrez.diagnostiqueur }} le {{ bien.superficie_carrez.date_mesurage | format_date }} annexée.

**Annexe n°19 : Certificat de superficie**
{% endif %}

Les parties ont été informées par le notaire, ce qu'elles reconnaissent, de la possibilité pour l'**ACQUEREUR** d'agir en révision du prix si, pour au moins un des lots, la superficie réelle est inférieure de plus d'un vingtième à celle exprimée aux présentes. En cas de pluralité d'inexactitudes, il y aura pluralité d'actions, chaque action en révision de prix ne concernant que la propre valeur du lot concerné.
La révision du prix dont il s'agit consistera en une diminution de la valeur du lot concerné proportionnelle à la moindre mesure.
L'action en diminution, si elle est recevable, devra être intentée par l'**ACQUEREUR** dans un délai d'un an à compter des présentes, et ce à peine de déchéance.

Le **VENDEUR** déclare ne pas avoir réalisé d'aménagements de lots susceptibles d'en modifier la superficie ci-dessus indiquée.

Une attestation mentionnant les dispositions de l'article 46 est remise à l'instant même à l'**ACQUEREUR** et au **VENDEUR** qui le reconnaissent et en donnent décharge.

#### Statut de la copropriété

**Règlement de copropriété**

L'**ACQUEREUR** déclare avoir pris connaissance de l'ensemble des documents relatifs au règlement de copropriété et à l'état descriptif de division.
Il s'engage à exécuter toutes les charges, clauses et conditions contenues au règlement de copropriété sus-énoncé et dans ses modificatifs éventuels.
Il atteste être parfaitement informé que les dispositions du règlement de copropriété s'imposent à lui, sauf dans la mesure où des dispositions législatives postérieures à son établissement viendraient à le modifier et ainsi s'imposer à l'ensemble des copropriétaires.
L'**ACQUEREUR** est subrogé dans tous les droits et obligations résultant pour le **VENDEUR** du règlement de copropriété, de son ou de ses modificatifs et des décisions régulièrement prises par l'assemblée des copropriétaires.
Il sera tenu de régler tous les appels de fonds qui seront faits par le syndic à compter de ce jour.
Le notaire avertit les parties que toutes les clauses du règlement de copropriété s'imposent, même celles réputées illicites tant qu'elles n'ont pas été annulées par une décision soit judiciaire soit d'une assemblée générale des copropriétaires dans les conditions de l'article 26b de la loi n°65-557 du 10 juillet 1965. Toutefois, si le règlement contient des clauses obsolètes, c'est-à-dire des clauses qui, lors de son établissement, étaient conformes aux prescriptions légales mais dont le contenu a été modifié ultérieurement par une nouvelle législation, celles-ci ne peuvent plus s'appliquer.
Un exemplaire du règlement de copropriété a été remis dès avant ce jour à l'**ACQUEREUR** qui le reconnaît.

**Syndic de l'immeuble**

Le syndic actuel de l'immeuble est :
**{{ copropriete.syndic.nom }}, {{ copropriete.syndic.adresse }}, {{ copropriete.syndic.code_postal }} {{ copropriete.syndic.ville }}**

**Etat contenant diverses informations sur la copropriété**

L'état contenant les informations prévues par l'article 5 du décret du 17 mars 1967 modifié a été délivré par le syndic et demeure annexé.

**Annexe n°20 : Etat daté**

L**'ACQUEREUR** déclare avoir pris parfaite connaissance de cet état tant par la lecture qui lui en a été faite par le notaire soussigné que par les explications qui lui ont été données par ce dernier.

**Absence de convocation à une assemblée générale entre l'avant-contrat et la vente**

Le **VENDEUR** atteste en outre n'avoir reçu depuis la conclusion de l'avant-contrat de convocation pour une assemblée des copropriétaires, ni avoir reçu précédemment à l'avant-contrat de convocation pour une assemblée générale entre celui-ci et ce jour.

**Dispositions légales et réglementaires sur la répartition des charges de copropriété**

Les parties sont informées des dispositions législatives et réglementaires applicables en matière de répartition entre le **VENDEUR** et l'**ACQUÉREUR** des charges de copropriété contenues dans l'article 6-2 du décret du 17 mars 1967 modifié, lequel dispose :
*"A l'occasion de la mutation à titre onéreux d'un lot :
1°) Le paiement de la provision exigible du budget prévisionnel, en application du troisième alinéa de l'article 14-1 de la loi du 10 juillet 1965 incombe au vendeur.
2°) Le paiement des provisions des dépenses non comprises dans le budget prévisionnel incombe à celui, vendeur ou acquéreur, qui est copropriétaire au moment de l'exigibilité.
3°) Le trop ou moins perçu sur provisions révélé par l'approbation des comptes est porté au crédit ou au débit du compte de celui qui est copropriétaire lors de l'approbation des comptes."*

Etant ici toutefois précisé que le transfert des charges n'est pris en compte par le syndicat des copropriétaires qu'à partir du moment où la vente a été notifiée au syndic (articles 20 de la loi du 10 juillet 1965 et 5 du décret du 17 mars 1967).

Tout aménagement entre les parties des dispositions sus énoncées n'a d'effet qu'entre elles et reste inopposable au syndicat des copropriétaires.
Par suite les demandes émanant du syndic s'effectuant auprès du copropriétaire en place au moment de celles-ci, il appartiendra donc aux parties d'effectuer directement entre elles les comptes et remboursements nécessaires.

**Convention des parties sur la répartition des charges et travaux**

L'**ACQUEREUR** supporte les charges de copropriété à compter du jour de l'entrée en jouissance soit le {{ jouissance.date_jouissance | format_date }}{% if jouissance.convention_occupation and jouissance.convention_occupation.existe %} compte tenu de la convention d'occupation précaire visée ci-avant{% endif %}.
L'**ACQUEREUR** supporte le coût des travaux, à compter de ce jour.
Le **VENDEUR** supporte le coût des travaux de copropriété, exécutés ou non, en cours d'exécution, votés antérieurement à ce jour.

Il est précisé que les compléments de travaux par devis supplémentaires approuvés ou votés après la vente seront donc à la charge de l'ACQUEREUR.

**En outre, les subventions allouées ou versées après réalisation de la vente au titre de travaux réalisés aux frais ou à la charge du VENDEUR devront lui être remboursés par l'ACQUEREUR dans les plus brefs délais, notamment en ce qui concerne les subventions versées au titre des travaux de rénovation énergétique de la copropriété.**

**Convention des parties sur les procédures**

Le **VENDEUR** déclare qu'il n'existe actuellement à sa connaissance aucune procédure en cours.
L'**ACQUEREUR** sera subrogé dans tous les droits et obligations du **VENDEUR** dans les procédures pouvant être révélées concernant la copropriété, sauf si ces procédures sont le résultat d'une faute du **VENDEUR**. En conséquence, le **VENDEUR** déclare se désister en faveur de l'**ACQUEREUR** du bénéfice de toutes sommes qui pourraient lui être ultérieurement allouées ou remboursées à ce titre, relativement au **BIEN**.

**Travaux urgents décidés par le syndic (article 18 de la loi du 10 juillet 1965)**

Le **VENDEUR** déclare qu'à sa connaissance aucuns travaux nécessaires à la sauvegarde de l'immeuble n'ont été décidés par le syndic depuis la date de signature de l'avant-contrat.

**Règlement définitif des charges**

L'**ACQUEREUR** a versé à l'instant même au **VENDEUR**, la comptabilité de l'Office Notarial, la somme correspondant au prorata des charges du trimestre en cours dont le paiement a déjà été appelé par le syndic et réglé par le **VENDEUR**. Ce paiement est effectué à titre définitif entre les parties, et ce quel que soit le décompte définitif des charges sur l'exercice en cours. Les parties reconnaissent avoir été informées par le rédacteur des présentes que le trop ou le moins perçu sur provisions, révélé par l'approbation des comptes, est porté au crédit ou au débit du compte de celui qui est copropriétaire lors de l'approbation de ces comptes.
Compte tenu des montants versés lors du dernier exercice, il n'est pas apparu aux parties nécessaire de procéder par versement provisionnel.
Ce règlement définitif n'est valable que sur les comptes de l'exercice en cours dans la mesure où l'année précédente n'aurait pas été encore clôturée.

**Solde de l'exercice antérieur**

Les comptes de l'exercice précédent ne sont pas précisément connus à ce jour du **VENDEUR**.
Son solde créditeur ou débiteur non encore imputé sur le compte du copropriétaire fera le bénéfice ou la perte du **VENDEUR** exclusivement, ce dernier s'engageant à rembourser à l'**ACQUEREUR** à première demande de ce dernier, les sommes qui seraient réclamées à ce titre, et l'**ACQUEREUR** s'engageant également à rembourser au **VENDEUR** sans délai, le solde créditeur qui pourrait subsister concernant cet exercice.
En tout état de cause, l'**ACQUEREUR** s'oblige à adresser, dès sa réception, au **VENDEUR** le relevé de compte de charges où figurera le solde de compte débiteur ou créditeur de l'exercice antérieur.
Compte tenu des provisions versées pour cet exercice par le **VENDEUR** et des comptes de l'exercice précédent, il n'est pas apparu nécessaire aux parties de séquestrer une somme en garantie du paiement du solde dû par l'une ou l'autre d'entre elles.

{% if copropriete.emprunt_collectif and copropriete.emprunt_collectif.existe %}
**Règlement effectué par prélèvement sur le prix des travaux votés et non appelés en tout ou partie**

Le **VENDEUR** donne à l'instant même son accord au notaire détenteur du prix de vente pour régler au syndic, en l'acquit de l'**ACQUEREUR**, par prélèvement sur ce prix, la somme de {{ copropriete.emprunt_collectif.solde | format_nombre }} EUR correspondant à sa quote-part dans les travaux votés mais non encore appelés (en tout ou partie), conformément aux indications fournies par le syndic dans l'état susvisé et en application de l'avant-contrat.
{% endif %}

{% if copropriete.fonds_travaux and copropriete.fonds_travaux.existe %}
**Fonds de travaux**

L'état révèle l'existence d'une cotisation annuelle à un fonds de travaux.
Précision étant ici faite qu'il a été voté en assemblée générale des copropriétaires la constitution d'un fonds de travaux.
Ces sommes sont rattachées aux lots et sont définitivement acquises au syndicat des copropriétaires. Elles ne donnent pas lieu à leur remboursement par le syndicat lors de la cession de lots.

Par suite, les parties conviennent d'effectuer directement entre elles le remboursement des sommes ainsi versées ce jour, l'**ACQUEREUR** devenant alors subrogé dans les droits du **VENDEUR** sur ce fonds.
{% endif %}

**Absence d'avances**

Le **VENDEUR** déclare n'avoir versé aucune avance, ainsi constaté aux termes de l'état délivré par le syndic.

**Election de domicile pour l'opposition du syndic**

Pour l'opposition éventuelle du syndic, domicile spécial est élu en l'office notarial du notaire rédacteur des présentes, détenteur des fonds.

**Notification de la mutation au syndic – Article 20 loi 10 juillet 1965**

En application de l'article 20 de la loi numéro 65-557 du 10 juillet 1965, un avis de la vente sera adressé sous quinze jours au syndic de copropriété et ce par lettre recommandée avec demande d'avis de réception.
Avant l'expiration d'un délai de quinze jours à compter de la réception de cet avis, le syndic pourra former, par acte extrajudiciaire, opposition au versement des fonds dans la limite des sommes restant dues par le **VENDEUR**.

Le notaire libèrera le prix de vente disponible dès l'accord entre le syndic et le **VENDEUR** sur les sommes restant dues. A défaut d'accord dans les trois mois de la constitution par le syndic de l'opposition régulière, il versera les sommes retenues au syndicat, sauf contestation judiciaire de cette opposition.
La notification de transfert sera également adressée par les soins du notaire au syndic de copropriété. A cette occasion, l'**ACQUEREUR** autorise le notaire à communiquer au syndic son adresse électronique ainsi que son numéro de téléphone.

{% if origine_propriete %}
### ORIGINE DE PROPRIÉTÉ

{% for origine in origine_propriete %}
**Concernant {{ "le lot numéro" if origine.lots_concernes|length == 1 else "les lots numéros" }} {{ origine.lots_concernes|join(' et ') }}**

**Origine immédiate**
{% for v in vendeurs %}{{ v.civilite }} {{ v.prenoms }} {{ v.nom }}{% if not loop.last %} et {% endif %}{% endfor %} {{ "est propriétaire indivis" if vendeurs|length == 1 else "sont propriétaires indivis" }} à concurrence de moitié chacun {{ "du lot numéro" if origine.lots_concernes|length == 1 else "des lots numéros" }} {{ origine.lots_concernes|join(' et ') }} susvisés par suite de l'acquisition qu'{{ "il" if vendeurs|length == 1 else "ils" }} en {{ "a" if vendeurs|length == 1 else "ont" }} faite de :

{% if origine.vendeur_precedent %}
{% for vp in origine.vendeur_precedent %}
{{ vp.civilite }} {{ vp.prenoms }}{% if vp.nom_naissance %} {{ vp.nom }} née {{ vp.nom_naissance }}{% else %} {{ vp.nom }}{% endif %}, {{ vp.profession }}, demeurant à {{ vp.ville }} ({{ vp.code_postal }}) {{ vp.adresse }}.
Né{{ "e" if vp.civilite == "Madame" else "" }} à {{ vp.lieu_naissance }}, le {{ vp.date_naissance | format_date }}.
{% if vp.situation_matrimoniale.statut == "celibataire" %}Célibataire.{% endif %}
{% if vp.situation_matrimoniale.statut == "divorce" %}Divorcé{{ "e" if vp.civilite == "Madame" else "" }}{% if vp.situation_matrimoniale.divorce.rang %} en {{ vp.situation_matrimoniale.divorce.rang }}{% endif %} de {{ vp.situation_matrimoniale.divorce.ex_conjoint }} suivant jugement rendu par le {{ vp.situation_matrimoniale.divorce.tribunal }} le {{ vp.situation_matrimoniale.divorce.date | format_date }}, et non remarié{{ "e" if vp.civilite == "Madame" else "" }}.{% endif %}
{% if vp.situation_matrimoniale.statut == "marie" %}Marié{{ "e" if vp.civilite == "Madame" else "" }} à la mairie de {{ vp.situation_matrimoniale.mariage.lieu }} le {{ vp.situation_matrimoniale.mariage.date | format_date }} sous le régime de {{ vp.situation_matrimoniale.mariage.regime_libelle }} aux termes du contrat de mariage reçu par {{ vp.situation_matrimoniale.mariage.contrat_mariage.notaire }}, le {{ vp.situation_matrimoniale.mariage.contrat_mariage.date | format_date }}.
Ce régime matrimonial n'a pas fait l'objet de modification.{% endif %}
{% if vp.situation_matrimoniale.statut == "pacse" %}Ayant conclu un pacte civil de solidarité sous le régime de la séparation de biens, suivant contrat reçu par {{ vp.situation_matrimoniale.pacs.notaire }}, le {{ vp.situation_matrimoniale.pacs.date | format_date }}.{% endif %}
{% if not vp.situation_matrimoniale or vp.situation_matrimoniale.statut in ["celibataire", "divorce"] %}Non lié{{ "e" if vp.civilite == "Madame" else "" }} par un pacte civil de solidarité.{% endif %}
De nationalité {{ vp.nationalite }}.
Résident{{ "e" if vp.civilite == "Madame" else "" }} au sens de la réglementation fiscale.
{% if not loop.last %}

Et {% endif %}
{% endfor %}
{% elif origine.origine_immediate.vendeur_precedent %}
{{ origine.origine_immediate.vendeur_precedent }}
{% else %}
*(identité du vendeur précédent à compléter)*
{% endif %}

Suivant acte reçu par {{ origine.origine_immediate.notaire }}, le {{ origine.origine_immediate.date | format_date }}.
Le prix a été payé comptant et quittancé audit acte.
Cet acte a été publié au service de la publicité foncière de {{ origine.origine_immediate.publication.service }}, le {{ origine.origine_immediate.publication.date | format_date }}, volume {{ origine.origine_immediate.publication.volume }}, numéro {{ origine.origine_immediate.publication.numero }}.

{% if origine.etat_publication %}{{ origine.etat_publication }}{% else %}L'état délivré sur cette publication n'a pas été présenté au notaire soussigné.{% endif %}

{% if origine.origine_anterieure %}
**Origine antérieure**

L'origine antérieure est ci-après relatée telle qu'elle résulte de l'acte de vente susvisé :

{{ origine.origine_anterieure }}
{% endif %}

{% if origine.origine_anterieure_2 %}
**ORIGINE DE PROPRIETE ANTERIEURE**

{{ origine.origine_anterieure_2 }}
{% endif %}

{% if origine.origine_plus_anterieure %}
**ORIGINE DE PROPRIETE PLUS ANTERIEURE**

L'origine de propriété plus antérieure est ci-après littéralement relatée, telle qu'elle figure dans l'acte de vente susvisé :

{{ origine.origine_plus_anterieure }}
{% endif %}

{% endfor %}
{% endif %}

{% if negociation %}
### NÉGOCIATION

La vente a été négociée par {{ negociation.agence }} titulaire d'un mandat donné par le VENDEUR sous le numéro {{ negociation.numero_mandat }} en date du {{ negociation.date_mandat | format_date }} non encore expiré, ainsi déclaré.
En conséquence, **le VENDEUR** qui en a seul la charge aux termes du mandat, doit à l'agence une rémunération de {{ negociation.honoraires|format_nombre }} EUR taxe sur la valeur ajoutée incluse.
Cette rémunération est réglée par la comptabilité de l'office notarial.
Etant ici précisé que le montant de la négociation est compris dans le prix indiqué ci-dessous.
{% endif %}

### MODALITÉS DE DÉLIVRANCE DE LA COPIE AUTHENTIQUE

Le notaire rédacteur adressera, à l'attention de l'**ACQUEREUR**, une copie authentique, sur support papier ou sur support électronique, des présentes qu'ultérieurement, notamment en cas de demande expresse de ce dernier, de son mandataire, de son notaire, ou de son ayant droit.
Néanmoins, le notaire lui adressera, immédiatement après la signature des présentes, une copie scannée de l'acte si l'acte a été signé sur support papier, ou une copie de l'acte électronique s'il a été signé sous cette forme.

L'**ACQUEREUR** donne son agrément à ces modalités de délivrance, sans que cet agrément vaille dispense pour le notaire de délivrer ultérieurement la copie authentique.

### CONCLUSION DU CONTRAT

Les parties déclarent que les dispositions de ce contrat ont été, en respect des règles impératives de l'article 1104 du Code civil, négociées de bonne foi. Elles affirment qu'il reflète l'équilibre voulu par chacune d'elles.

### DEVOIR D'INFORMATION RECIPROQUE

En application de l'article 1112-1 du Code civil qui impose aux parties un devoir précontractuel d'information, qui ne saurait toutefois porter sur le prix, le **VENDEUR** déclare avoir porté à la connaissance de l'**ACQUEREUR** l'ensemble des informations dont il dispose ayant un lien direct et nécessaire avec le contenu du présent contrat et dont l'importance pourrait être déterminante de son consentement.
Ce devoir s'applique à toute information sur les caractéristiques juridiques, matérielles et environnementales relatives au **BIEN**, ainsi qu'à son usage, dont il a personnellement connaissance par lui-même et par des tiers, sans que ces informations puissent être limitées dans le temps.
Le **VENDEUR** reconnaît être informé qu'un manquement à ce devoir serait sanctionné par la mise en oeuvre de sa responsabilité, avec possibilité d'annulation du contrat s'il a vicié le consentement de l'**ACQUEREUR**.
Pareillement, l'**ACQUEREUR** déclare avoir rempli les mêmes engagements, tout manquement pouvant être sanctionné comme indiqué ci-dessus.
Le devoir d'information est donc réciproque.
En outre, conformément aux dispositions de l'article 1602 du Code civil, le **VENDEUR** est tenu d'expliquer clairement ce à quoi il s'oblige, tout pacte obscur ou ambigu s'interprétant contre lui.
Les **PARTIES** attestent que les informations déterminantes connues d'elles, données et reçues, sont rapportées aux présentes.

### RENONCIATION À L'IMPRÉVISION

Le mécanisme de l'imprévision nécessite un changement de circonstances rendant l'exécution d'un contrat excessivement onéreuse, changement imprévisible lors de la conclusion de celui-ci.
Ce mécanisme est prévu à l'article 1195 du Code civil dont les dispositions sont littéralement rapportées :
*"Si un changement de circonstances imprévisible lors de la conclusion du contrat rend l'exécution excessivement onéreuse pour une partie qui n'avait pas accepté d'en assumer le risque, celle-ci peut demander une renégociation du contrat à son cocontractant. Elle continue à exécuter ses obligations durant la renégociation.
En cas de refus ou d'échec de la renégociation, les parties peuvent convenir de la résolution du contrat, à la date et aux conditions qu'elles déterminent, ou demander d'un commun accord au juge de procéder à son adaptation. A défaut d'accord dans un délai raisonnable, le juge peut, à la demande d'une partie, réviser le contrat ou y mettre fin, à la date et aux conditions qu'il fixe".*
Les parties écartent de leur contrat les dispositions de l'article 1195 du Code civil permettant la révision du contrat pour imprévision, estimant que compte tenu du contexte des présentes, cette renonciation n'aura pas de conséquences déraisonnables à l'endroit de l'une d'entre elles. Par suite, elles ne pourront pas solliciter judiciairement la renégociation des présentes s'il survient un évènement imprévisible rendant l'exécution excessivement onéreuse pour l'une d'entre elles. Toutefois cette renonciation n'aura d'effet que pour les évènements qui n'auront pas été prévus aux termes des présentes.
Une telle renonciation ne concerne pas le cas de force majeure caractérisé par l'irrésistibilité et l'imprévisibilité qui impliquent l'impossibilité pour le débiteur d'exécuter son obligation et dont seul le débiteur peut se prévaloir.
Aux termes de l'article 1218 du Code civil "*Il y a force majeure en matière contractuelle lorsqu'un événement échappant au contrôle du débiteur, qui ne pouvait être raisonnablement prévu lors de la conclusion du contrat et dont les effets ne peuvent être évités par des mesures appropriées, empêche l'exécution de son obligation par le débiteur.
Si l'empêchement est temporaire, l'exécution de l'obligation est suspendue à moins que le retard qui en résulterait ne justifie la résolution du contrat. Si l'empêchement est définitif, le contrat est résolu de plein droit et les parties sont libérées de leurs obligations dans les conditions prévues aux articles 1351 et 1351-1.*"

{% if avant_contrat %}
### CONVENTIONS ANTERIEURES

Les présentes entrant dans le champ d'application de l'article L 271-1 du Code de la construction et de l'habitation issu de la loi relative à la solidarité et au renouvellement urbain, les parties attestent que les conventions contenues dans le présent acte sont identiques à celles figurant dans l'avant-contrat.
Si toutefois des différences existaient les parties précisent qu'il ne s'agit alors que de points mineurs n'altérant pas les conditions essentielles et déterminantes de la vente telles qu'elles sont relatées dans l'avant contrat.
{% endif %}

### MÉDIATION

Les parties sont informées qu'en cas de litige entre elles ou avec un tiers, elles pourront, préalablement à toute instance judiciaire, le soumettre à un médiateur qui sera désigné et missionné par le Centre de médiation notariale dont elles trouveront toutes les coordonnées et renseignements utiles sur le site : https://www.mediation.notaires.fr.

### ELECTION DE DOMICILE

Les parties élisent domicile :

* en leur demeure ou siège respectif pour l'exécution des présentes et de leurs suites,

* en l'office notarial pour la publicité foncière, l'envoi des pièces et la correspondance s'y rapportant.

### TITRES - CORRESPONDANCE ET RENVOI DES PIECES

Il ne sera remis aucun ancien titre de propriété à l'**ACQUEREUR** qui pourra se faire délivrer, à ses frais, ceux dont il pourrait avoir besoin, et sera subrogé dans tous les droits du **VENDEUR** à ce sujet.
En suite des présentes, la correspondance et le renvoi des pièces à l'**ACQUEREUR** devront s'effectuer à l'adresse du bien présentement acquis.
La correspondance auprès du **VENDEUR** s'effectuera à l'adresse indiquée en tête des présentes.
Chacune des parties s'oblige à communiquer au notaire tout changement de domicile ou siège et ce par lettre recommandée avec demande d'avis de réception.

### POUVOIRS - PUBLICITÉ FONCIÈRE

Pour l'accomplissement des formalités de publicité foncière ou réparer une erreur matérielle telle que l'omission d'une pièce annexe dont le contenu est relaté aux présentes, les parties agissant dans un intérêt commun donnent tous pouvoirs nécessaires à tout notaire ou à tout collaborateur de l'office notarial dénommé en tête des présentes, à l'effet de faire dresser et signer tous actes complémentaires ou rectificatifs pour mettre le présent acte en concordance avec tous les documents hypothécaires, cadastraux ou d'état civil.

### AFFIRMATION DE SINCÉRITÉ

Les parties affirment, sous les peines édictées par l'article 1837 du Code général des impôts, que le présent acte exprime l'intégralité du prix.
Elles reconnaissent avoir été informées par le notaire soussigné des sanctions fiscales et des peines correctionnelles encourues en cas d'inexactitude de cette affirmation ainsi que des conséquences civiles édictées par l'article 1202 du Code civil.
Le notaire soussigné précise qu'à sa connaissance le présent acte n'est modifié ni contredit par aucune contre-lettre contenant augmentation du prix.

### DEMANDE DE RESTITUTION – AUTORISATION DE DESTRUCTION DES DOCUMENTS ET PIÈCES

Les originaux des documents et pièces remis par les parties au notaire leur seront restitués, si elles en font la demande expresse dans le délai d'un mois à compter des présentes.
A défaut, les parties autorisent l'office notarial à détruire ces documents et pièces, et notamment tout avant-contrat sous signature privée pouvant avoir été établi en vue de la conclusion du présent acte, considérant que celui-ci contient l'intégralité des conventions auxquelles elles ont entendu donner le caractère d'authenticité.

### MENTION SUR LA PROTECTION DES DONNÉES PERSONNELLES

L'Office notarial traite des données personnelles concernant les personnes mentionnées aux présentes, pour l'accomplissement des activités notariales, notamment de formalités d'actes.
Ce traitement est fondé sur le respect d'une obligation légale et l'exécution d'une mission relevant de l'exercice de l'autorité publique déléguée par l'Etat dont sont investis les notaires, officiers publics, conformément à l'ordonnance n°45-2590 du 2 novembre 1945.
Ces données seront susceptibles d'être transférées aux destinataires suivants :

* les administrations ou partenaires légalement habilités tels que la Direction Générale des Finances Publiques, ou, le cas échéant, le livre foncier, les instances notariales, les organismes du notariat, les fichiers centraux de la profession notariale (Fichier Central Des Dernières Volontés, Minutier Central Électronique des Notaires, registre du PACS, etc.),

* les offices notariaux participant ou concourant à l'acte,

* les établissements financiers concernés,

* les organismes de conseils spécialisés pour la gestion des activités notariales,

* le Conseil supérieur du notariat ou son délégataire, pour la production des statistiques permettant l'évaluation des biens immobiliers, en application du décret n° 2013-803 du 3 septembre 2013,

* les organismes publics ou privés pour des opérations de vérification dans le cadre de la recherche de personnalités politiquement exposées ou ayant fait l'objet de gel des avoirs ou sanctions, de la lutte contre le blanchiment des capitaux et le financement du terrorisme. Ces vérifications font l'objet d'un transfert de données dans un pays situé hors de l'Union Européenne disposant d'une législation sur la protection des données reconnue comme équivalente par la Commission européenne.

La communication de ces données à ces destinataires peut être indispensable pour l'accomplissement des activités notariales.
Les documents permettant d'établir, d'enregistrer et de publier les actes sont conservés 30 ans à compter de la réalisation de l'ensemble des formalités. L'acte authentique et ses annexes sont conservés 75 ans et 100 ans lorsque l'acte porte sur des personnes mineures ou majeures protégées. Les vérifications liées aux personnalités politiquement exposées, au blanchiment des capitaux et au financement du terrorisme sont conservées 5 ans après la fin de la relation d'affaires.
Conformément à la réglementation en vigueur relative à la protection des données personnelles, les intéressés peuvent demander l'accès aux données les concernant. Le cas échéant, ils peuvent demander la rectification ou l'effacement de celles-ci, obtenir la limitation du traitement de ces données ou s'y opposer pour des raisons tenant à leur situation particulière. Ils peuvent également définir des directives relatives à la conservation, à l'effacement et à la communication de leurs données personnelles après leur décès.
L'Office notarial a désigné un Délégué à la protection des données que les intéressés peuvent contacter à l'adresse suivante : dpo.notaires@datavigiprotection.fr.
Si ces personnes estiment, après avoir contacté l'Office notarial, que leurs droits ne sont pas respectés, elles peuvent introduire une réclamation auprès d'une autorité européenne de contrôle, la Commission Nationale de l'Informatique et des Libertés pour la France.

### CERTIFICATION D'IDENTITÉ

Le notaire soussigné certifie que l'identité complète des parties dénommées dans le présent document telle qu'elle est indiquée en tête des présentes à la suite de leur nom ou dénomination lui a été régulièrement justifiée.

### FORMALISME LIÉ AUX ANNEXES

Les annexes, s'il en existe, font partie intégrante de la minute.
Lorsque l'acte est établi sur support papier, les pièces annexées à l'acte sont revêtues d'une mention constatant cette annexe et signée du notaire, sauf si les feuilles de l'acte et des annexes sont réunies par un procédé empêchant toute substitution ou addition.
Si l'acte est établi sur support électronique, la signature du notaire en fin d'acte vaut également pour ses annexes.
