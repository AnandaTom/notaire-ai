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


# Fixation de la proportion de propriété indivise

{% if indivision %}
{% if indivision.proportion %}

## Proportions entre les acquéreurs

Les acquéreurs déclareront acquérir le bien dans les proportions suivantes :

{% for acquereur in indivision.acquereurs %}
- <<<VAR_START>>>{{ acquereur.civilite }} {{ acquereur.prenom }} {{ acquereur.nom | upper }}<<<VAR_END>>> : <<<VAR_START>>>{{ acquereur.quotite }}<<<VAR_END>>> %
{% endfor %}

{% if indivision.justification %}
Cette répartition est justifiée par les éléments suivants : <<<VAR_START>>>{{ indivision.justification }}<<<VAR_END>>>.
{% endif %}

## Détermination de la contribution des acquéreurs au financement

{% if indivision.financement %}

### Coût et financement de l'opération

Le coût global de l'opération s'établit comme suit :

| Poste | Montant |
|-------|---------|
| Prix d'acquisition | <<<VAR_START>>>{{ prix.montant | format_nombre }}<<<VAR_END>>> EUR |
{% if indivision.financement.frais_notaire %}
| Frais de notaire et droits | <<<VAR_START>>>{{ indivision.financement.frais_notaire | format_nombre }}<<<VAR_END>>> EUR |
{% endif %}
{% if indivision.financement.frais_agence %}
| Frais d'agence | <<<VAR_START>>>{{ indivision.financement.frais_agence | format_nombre }}<<<VAR_END>>> EUR |
{% endif %}
{% if indivision.financement.autres_frais %}
| Autres frais | <<<VAR_START>>>{{ indivision.financement.autres_frais | format_nombre }}<<<VAR_END>>> EUR |
{% endif %}
| **TOTAL** | **<<<VAR_START>>>{{ indivision.financement.cout_total | format_nombre }}<<<VAR_END>>> EUR** |

### Prise en charge du financement de l'opération

Le financement de cette opération sera assuré comme suit :

{% for acquereur in indivision.acquereurs %}
**<<<VAR_START>>>{{ acquereur.civilite }} {{ acquereur.prenom }} {{ acquereur.nom | upper }}<<<VAR_END>>>**

{% if acquereur.financement.apport_personnel %}
##### Fonds personnels

Apport personnel : <<<VAR_START>>>{{ acquereur.financement.apport_personnel | format_nombre }}<<<VAR_END>>> EUR

{% if acquereur.financement.origine_fonds %}
Origine des fonds : <<<VAR_START>>>{{ acquereur.financement.origine_fonds }}<<<VAR_END>>>
{% endif %}
{% endif %}

{% if acquereur.financement.emprunt %}
##### Fonds empruntés

Emprunt bancaire : <<<VAR_START>>>{{ acquereur.financement.emprunt.montant | format_nombre }}<<<VAR_END>>> EUR

{% if acquereur.financement.emprunt.etablissement %}
Établissement prêteur : <<<VAR_START>>>{{ acquereur.financement.emprunt.etablissement }}<<<VAR_END>>>
{% endif %}

{% if acquereur.financement.emprunt.duree %}
Durée : <<<VAR_START>>>{{ acquereur.financement.emprunt.duree }}<<<VAR_END>>> mois
{% endif %}

{% if acquereur.financement.emprunt.taux %}
Taux : <<<VAR_START>>>{{ acquereur.financement.emprunt.taux }}<<<VAR_END>>> % l'an
{% endif %}
{% endif %}

{% if acquereur.financement.aide %}
##### Aides

{% if acquereur.financement.aide.ptz %}
- Prêt à Taux Zéro (PTZ) : <<<VAR_START>>>{{ acquereur.financement.aide.ptz | format_nombre }}<<<VAR_END>>> EUR
{% endif %}

{% if acquereur.financement.aide.action_logement %}
- Action Logement : <<<VAR_START>>>{{ acquereur.financement.aide.action_logement | format_nombre }}<<<VAR_END>>> EUR
{% endif %}

{% if acquereur.financement.aide.autres %}
{% for aide in acquereur.financement.aide.autres %}
- {{ aide.type }} : <<<VAR_START>>>{{ aide.montant | format_nombre }}<<<VAR_END>>> EUR
{% endfor %}
{% endif %}
{% endif %}

**Total contribution** : <<<VAR_START>>>{{ acquereur.financement.total | format_nombre }}<<<VAR_END>>> EUR (<<<VAR_START>>>{{ acquereur.financement.pourcentage }}<<<VAR_END>>>%)

{% endfor %}

### Récapitulatif de l'effort respectif de financement

| Acquéreur | Apport personnel | Emprunt | Aides | Total | % |
|-----------|------------------|---------|-------|-------|---|
{% for acquereur in indivision.acquereurs %}
| {{ acquereur.nom }} | {{ acquereur.financement.apport_personnel | format_nombre }} EUR | {{ acquereur.financement.emprunt.montant | default(0) | format_nombre }} EUR | {{ acquereur.financement.aide.total | default(0) | format_nombre }} EUR | **{{ acquereur.financement.total | format_nombre }} EUR** | **{{ acquereur.financement.pourcentage }}%** |
{% endfor %}

### Prise en charge d'un financement extérieur ultérieur

{% if indivision.financement.ulterieur %}
En cas de nécessité d'un financement extérieur ultérieur pour l'acquisition de biens complémentaires ou la réalisation de travaux, les acquéreurs s'engagent à le prendre en charge dans les proportions suivantes :

{% for acquereur in indivision.acquereurs %}
- {{ acquereur.nom }} : <<<VAR_START>>>{{ acquereur.proportion_financement_ulterieur | default(acquereur.quotite) }}<<<VAR_END>>>%
{% endfor %}
{% endif %}

### Prise en charge d'un financement personnel ultérieur

{% if indivision.financement.personnel_ulterieur %}
Les acquéreurs conviennent que tout financement personnel ultérieur effectué par l'un d'eux au profit du bien indivis (travaux d'amélioration, réparations, etc.) devra faire l'objet d'une déclaration écrite aux autres indivisaires et pourra donner lieu à ajustement des droits indivis.
{% endif %}

### Industrie personnelle

{% if indivision.industrie_personnelle %}
Les parties conviennent que toute contribution en industrie personnelle (travaux réalisés personnellement par un indivisaire) sera valorisée sur la base du coût des travaux équivalents effectués par un professionnel et pourra donner lieu à ajustement des droits indivis.
{% endif %}

{% endif %}

{% endif %}
{% endif %}

# Conditions et déclarations générales

{% if indivision %}
{% if indivision.conditions_generales %}

## Vie courante

{% if indivision.conditions_generales.vie_courante %}
Les indivisaires conviennent des règles suivantes concernant la gestion courante du bien :

{% if indivision.conditions_generales.vie_courante.occupation %}
### Occupation du bien

<<<VAR_START>>>{{ indivision.conditions_generales.vie_courante.occupation.regles }}<<<VAR_END>>>

{% if indivision.conditions_generales.vie_courante.occupation.indemnite %}
Indemnité d'occupation : <<<VAR_START>>>{{ indivision.conditions_generales.vie_courante.occupation.indemnite | format_nombre }}<<<VAR_END>>> EUR par mois
{% endif %}
{% endif %}

{% if indivision.conditions_generales.vie_courante.charges %}
### Charges courantes

Les charges courantes du bien (copropriété, taxes, assurances, entretien) seront réparties entre les indivisaires proportionnellement à leurs quotes-parts respectives.

{% if indivision.conditions_generales.vie_courante.charges.modalites %}
Modalités de paiement : <<<VAR_START>>>{{ indivision.conditions_generales.vie_courante.charges.modalites }}<<<VAR_END>>>
{% endif %}
{% endif %}

{% if indivision.conditions_generales.vie_courante.decisions %}
### Décisions courantes

Les décisions concernant la gestion courante du bien (travaux d'entretien, choix des assurances, etc.) seront prises :

{% if indivision.conditions_generales.vie_courante.decisions.regle == 'unanimite' %}
- À l'unanimité des indivisaires
{% elif indivision.conditions_generales.vie_courante.decisions.regle == 'majorite' %}
- À la majorité {% if indivision.conditions_generales.vie_courante.decisions.seuil %}des {{ indivision.conditions_generales.vie_courante.decisions.seuil }}%{% endif %}
{% elif indivision.conditions_generales.vie_courante.decisions.regle == 'gerant' %}
- Par le gérant désigné : <<<VAR_START>>>{{ indivision.conditions_generales.vie_courante.decisions.gerant }}<<<VAR_END>>>
{% endif %}
{% endif %}
{% endif %}

## Répartition lors de la revente

{% if indivision.conditions_generales.revente %}
En cas de revente du bien, le prix de vente, déduction faite des frais de vente et des dettes éventuelles grevant le bien, sera réparti entre les indivisaires {% if indivision.conditions_generales.revente.repartition == 'quotes_parts' %}proportionnellement à leurs quotes-parts respectives{% elif indivision.conditions_generales.revente.repartition == 'contribution' %}en fonction de leur contribution effective au financement{% elif indivision.conditions_generales.revente.repartition == 'conventionnelle' %}selon les modalités conventionnelles suivantes : <<<VAR_START>>>{{ indivision.conditions_generales.revente.modalites }}<<<VAR_END>>>{% endif %}.

{% if indivision.conditions_generales.revente.plus_value %}
La plus-value éventuelle sera répartie dans les mêmes proportions que le prix de vente.
{% endif %}

{% if indivision.conditions_generales.revente.droit_preference %}
En cas de souhait de vente par l'un des indivisaires, les autres indivisaires bénéficieront d'un droit de préférence pour acquérir sa quote-part aux conditions proposées par un tiers.

Délai d'exercice du droit de préférence : <<<VAR_START>>>{{ indivision.conditions_generales.revente.droit_preference.delai | default(30) }}<<<VAR_END>>> jours à compter de la notification.
{% endif %}
{% endif %}

## Répartition lors du partage

{% if indivision.conditions_generales.partage %}
En cas de partage du bien indivis, qu'il soit amiable ou judiciaire, les indivisaires conviennent des règles suivantes :

{% if indivision.conditions_generales.partage.modalites == 'attribution' %}
### Attribution préférentielle

{% if indivision.conditions_generales.partage.attribution_preferentielle %}
Un droit d'attribution préférentielle est reconnu à <<<VAR_START>>>{{ indivision.conditions_generales.partage.attribution_preferentielle.beneficiaire }}<<<VAR_END>>>.

{% if indivision.conditions_generales.partage.attribution_preferentielle.conditions %}
Conditions : <<<VAR_START>>>{{ indivision.conditions_generales.partage.attribution_preferentielle.conditions }}<<<VAR_END>>>
{% endif %}

{% if indivision.conditions_generales.partage.attribution_preferentielle.soulte %}
Le bénéficiaire de l'attribution devra verser une soulte calculée sur la base de la valeur du bien au jour du partage.
{% endif %}
{% endif %}

{% elif indivision.conditions_generales.partage.modalites == 'licitation' %}
### Licitation

En l'absence d'accord sur l'attribution du bien, celui-ci sera vendu aux enchères publiques (licitation).

Le prix de vente sera réparti entre les indivisaires proportionnellement à leurs quotes-parts, déduction faite des frais de vente.

{% elif indivision.conditions_generales.partage.modalites == 'rachat' %}
### Rachat de quote-part

Chaque indivisaire dispose de la faculté de racheter la quote-part des autres indivisaires, à un prix déterminé par expertise.

{% if indivision.conditions_generales.partage.rachat.expert %}
L'expert sera désigné : <<<VAR_START>>>{{ indivision.conditions_generales.partage.rachat.expert }}<<<VAR_END>>>
{% endif %}
{% endif %}

{% if indivision.conditions_generales.partage.frais %}
Les frais de partage (notaire, expert, géomètre) seront supportés par les indivisaires proportionnellement à leurs quotes-parts.
{% endif %}
{% endif %}

{% endif %}
{% endif %}

# Rappel des textes en matière d'indivision

{% if indivision %}
{% if indivision.rappel_textes %}

Les parties ont été expressément informées par le notaire soussigné des dispositions légales applicables à l'indivision, et notamment :

## Dispositions générales (articles 815 et suivants du Code civil)

**Article 815** : Nul ne peut être contraint à demeurer dans l'indivision et le partage peut toujours être provoqué, à moins qu'il n'y ait été sursis par jugement ou convention.

**Article 815-3** : Les biens indivis sont affectés par privilège au remboursement des dépenses faites pour les actes de conservation, d'administration ou d'amélioration et au paiement des dettes et charges de l'indivision.

**Article 815-9** : Chaque indivisaire peut user et jouir des biens indivis conformément à leur destination, dans la mesure compatible avec le droit des autres indivisaires et avec l'effet des actes régulièrement passés au cours de l'indivision.

## Gestion de l'indivision (articles 815-10 et suivants)

**Article 815-10** : Les décisions concernant la jouissance, l'administration et la disposition des biens indivis sont prises :

- À l'unanimité pour les actes de disposition
- À la majorité des deux tiers pour les actes d'administration
- Sans l'accord des autres indivisaires pour les actes conservatoires

**Article 815-11** : Un mandataire peut être désigné pour administrer les biens indivis, soit à l'unanimité des indivisaires, soit, en cas de mésentente, par autorisation du juge.

## Protection des indivisaires (articles 815-14 et suivants)

**Article 815-14** : Tout indivisaire peut demander au tribunal judiciaire de l'autoriser à passer seul un acte pour lequel le consentement d'un coïndivisaire serait nécessaire, si le refus de ce dernier met en péril l'intérêt commun.

**Article 815-17** : Un indivisaire peut, à tout moment, provoquer le partage, sauf convention contraire ne pouvant excéder cinq ans.

## Convention d'indivision (article 1873-1 et suivants)

Les indivisaires peuvent conclure une convention d'indivision fixant les règles de gestion et de partage du bien indivis pour une durée maximale de cinq ans, renouvelable.

{% if indivision.rappel_textes.convention_souhaitee %}
Les parties déclarent souhaiter établir une convention d'indivision complémentaire aux présentes, et donnent mandat au notaire soussigné pour la rédiger.
{% endif %}

## Fiscalité de l'indivision

**Impôts locaux** : Les taxes foncières et d'habitation sont dues par les indivisaires proportionnellement à leurs quotes-parts.

**Revenus fonciers** : En cas de mise en location du bien, les revenus sont répartis entre les indivisaires selon leurs quotes-parts et déclarés individuellement.

**Plus-values immobilières** : En cas de vente, la plus-value est imposée au nom de chaque indivisaire proportionnellement à sa quote-part.

{% if indivision.rappel_textes.fiscalite %}
{% if indivision.rappel_textes.fiscalite.impots_locaux %}
### Impôts locaux

Modalités de prise en charge : <<<VAR_START>>>{{ indivision.rappel_textes.fiscalite.impots_locaux.modalites }}<<<VAR_END>>>
{% endif %}

{% if indivision.rappel_textes.fiscalite.avantage_fiscal %}
### Avantage fiscal lié à un engagement de location

{% if indivision.rappel_textes.fiscalite.avantage_fiscal.dispositif %}
Le bien peut bénéficier du dispositif fiscal <<<VAR_START>>>{{ indivision.rappel_textes.fiscalite.avantage_fiscal.dispositif }}<<<VAR_END>>> sous réserve du respect des conditions légales.
{% endif %}
{% endif %}
{% endif %}

Les parties déclarent avoir pris connaissance de ces dispositions et en accepter les conséquences.

{% endif %}
{% endif %}

# DISPOSITIONS RELATIVES A L'URBANISME

## Urbanisme

{% if urbanisme %}

### Note d'urbanisme

{% if urbanisme.note_urbanisme %}
La commune a répondu le <<<VAR_START>>>{{ urbanisme.note_urbanisme.date | format_date }}<<<VAR_END>>> à une demande de note d'urbanisme. Cette réponse est annexée.

L'ACQUEREUR s'oblige à faire son affaire personnelle de l'exécution des charges et prescriptions, du respect des servitudes publiques et autres limitations administratives au droit de propriété mentionnées sur cette note.

**Annexe** : Note d'urbanisme

{% if urbanisme.note_urbanisme.informations %}
La note d'urbanisme révèle :

{% for info in urbanisme.note_urbanisme.informations %}
- {{ info }}
{% endfor %}
{% endif %}
{% endif %}

### Certificat d'urbanisme

{% if urbanisme.certificat_urbanisme %}
Un certificat d'urbanisme a été délivré le <<<VAR_START>>>{{ urbanisme.certificat_urbanisme.date | format_date }}<<<VAR_END>>> par <<<VAR_START>>>{{ urbanisme.certificat_urbanisme.autorite }}<<<VAR_END>>>.

**Référence** : <<<VAR_START>>>{{ urbanisme.certificat_urbanisme.numero }}<<<VAR_END>>>

{% if urbanisme.certificat_urbanisme.type == 'information' %}
Il s'agit d'un certificat d'urbanisme d'information (article L. 410-1 du Code de l'urbanisme).
{% elif urbanisme.certificat_urbanisme.type == 'operationnel' %}
Il s'agit d'un certificat d'urbanisme opérationnel (article L. 410-1 du Code de l'urbanisme).
{% endif %}

**Annexe** : Certificat d'urbanisme
{% endif %}

### Plan local d'urbanisme (PLU)

{% if urbanisme.plu %}
Le BIEN est situé sur le territoire de la commune de <<<VAR_START>>>{{ bien.adresse.ville }}<<<VAR_END>>>, soumise au {% if urbanisme.plu.type == 'PLU' %}Plan Local d'Urbanisme{% elif urbanisme.plu.type == 'PLUi' %}Plan Local d'Urbanisme intercommunal{% elif urbanisme.plu.type == 'POS' %}Plan d'Occupation des Sols{% endif %} approuvé le <<<VAR_START>>>{{ urbanisme.plu.date_approbation | format_date }}<<<VAR_END>>>.

{% if urbanisme.plu.zonage %}
**Zonage** : Le BIEN est situé en zone <<<VAR_START>>>{{ urbanisme.plu.zonage }}<<<VAR_END>>>.
{% endif %}

{% if urbanisme.plu.reglement %}
Le VENDEUR et l'ACQUEREUR déclarent avoir pris connaissance du règlement d'urbanisme applicable.
{% endif %}

{% if urbanisme.plu.servitudes %}
Le BIEN est soumis aux servitudes d'utilité publique suivantes : <<<VAR_START>>>{{ urbanisme.plu.servitudes | join(', ') }}<<<VAR_END>>>.
{% endif %}
{% endif %}

### Périmètre monument historique

{% if urbanisme.monument_historique %}
{% if urbanisme.monument_historique.perimetre %}
Le BIEN est situé dans le périmètre de protection d'un monument historique (rayon de <<<VAR_START>>>{{ urbanisme.monument_historique.rayon | default(500) }}<<<VAR_END>>> mètres).

**Monument concerné** : <<<VAR_START>>>{{ urbanisme.monument_historique.nom }}<<<VAR_END>>>

Conformément à l'article L. 621-30 du Code du patrimoine, tous travaux susceptibles de modifier l'aspect extérieur de l'immeuble sont soumis à autorisation spéciale de l'Architecte des Bâtiments de France.

L'ACQUEREUR déclare avoir été informé de cette situation et des contraintes qui en découlent.
{% else %}
Le BIEN n'est pas situé dans le périmètre de protection d'un monument historique.
{% endif %}
{% endif %}

### Alignement

{% if urbanisme.alignement %}
{% if urbanisme.alignement.plan_alignement %}
Le BIEN est soumis à un plan d'alignement approuvé le <<<VAR_START>>>{{ urbanisme.alignement.date_approbation | format_date }}<<<VAR_END>>>.

{% if urbanisme.alignement.reserves %}
Des réserves d'alignement existent : <<<VAR_START>>>{{ urbanisme.alignement.reserves }}<<<VAR_END>>>.
{% else %}
Aucune réserve d'alignement n'affecte le BIEN.
{% endif %}
{% else %}
Le BIEN n'est pas soumis à un plan d'alignement.
{% endif %}
{% endif %}

### Note de voirie

{% if urbanisme.note_voirie %}
Une note de renseignements de voirie a été délivrée par l'autorité compétente le <<<VAR_START>>>{{ urbanisme.note_voirie.date | format_date }}<<<VAR_END>>>.

{% if urbanisme.note_voirie.conclusion %}
Il résulte de cette note que : "<<<VAR_START>>>{{ urbanisme.note_voirie.conclusion }}<<<VAR_END>>>".
{% endif %}

**Annexe** : Note de voirie
{% endif %}

### Certificat de non-péril

{% if urbanisme.certificat_non_peril %}
Il résulte d'un certificat délivré par l'autorité compétente le <<<VAR_START>>>{{ urbanisme.certificat_non_peril.date | format_date }}<<<VAR_END>>>, annexé, que l'immeuble :

"<<<VAR_START>>>{{ urbanisme.certificat_non_peril.contenu }}<<<VAR_END>>>"

**Annexe** : Certificat de non-péril
{% endif %}

{% endif %}

# Dispositions relatives à la préemption

{% if urbanisme.preemption %}

## Droit de préemption urbain

{% if urbanisme.preemption.dpu %}
La commune de <<<VAR_START>>>{{ bien.adresse.ville }}<<<VAR_END>>> a instauré un droit de préemption urbain {% if urbanisme.preemption.dpu.type == 'simple' %}simple{% elif urbanisme.preemption.dpu.type == 'renforce' %}renforcé{% endif %} par délibération du <<<VAR_START>>>{{ urbanisme.preemption.dpu.date_deliberation | format_date }}<<<VAR_END>>>.

{% if urbanisme.preemption.dpu.zone %}
Le BIEN est situé dans la zone : <<<VAR_START>>>{{ urbanisme.preemption.dpu.zone }}<<<VAR_END>>>.
{% endif %}

Conformément aux dispositions des articles L. 211-1 et suivants du Code de l'urbanisme, la présente vente sera notifiée à la commune qui disposera d'un délai de deux mois pour exercer son droit de préemption.

L'ACQUEREUR est informé que la commune peut se substituer à lui dans les conditions prévues par la loi.
{% else %}
Le BIEN n'est pas situé dans une zone de préemption urbaine.
{% endif %}

## Autres droits de préemption

{% if urbanisme.preemption.autres %}
{% for autre_preemption in urbanisme.preemption.autres %}
**{{ autre_preemption.type }}**

{{ autre_preemption.description }}

{% if autre_preemption.beneficiaire %}
**Bénéficiaire** : <<<VAR_START>>>{{ autre_preemption.beneficiaire }}<<<VAR_END>>>
{% endif %}

{% if autre_preemption.delai %}
**Délai d'exercice** : <<<VAR_START>>>{{ autre_preemption.delai }}<<<VAR_END>>> jours
{% endif %}
{% endfor %}
{% endif %}

{% endif %}

# Dispositions relatives à la construction

{% if urbanisme.construction %}

## Autorisations d'urbanisme

{% if urbanisme.construction.permis_construire %}
### Permis de construire

Un permis de construire a été délivré le <<<VAR_START>>>{{ urbanisme.construction.permis_construire.date | format_date }}<<<VAR_END>>> sous le numéro <<<VAR_START>>>{{ urbanisme.construction.permis_construire.numero }}<<<VAR_END>>>.

{% if urbanisme.construction.permis_construire.objet %}
**Objet** : <<<VAR_START>>>{{ urbanisme.construction.permis_construire.objet }}<<<VAR_END>>>
{% endif %}

{% if urbanisme.construction.permis_construire.purge %}
Ce permis est devenu définitif le <<<VAR_START>>>{{ urbanisme.construction.permis_construire.date_purge | format_date }}<<<VAR_END>>>, aucun recours n'ayant été exercé dans le délai légal.
{% endif %}

**Annexe** : Permis de construire
{% endif %}

{% if urbanisme.construction.declaration_prealable %}
### Déclaration préalable

Une déclaration préalable a été déposée le <<<VAR_START>>>{{ urbanisme.construction.declaration_prealable.date_depot | format_date }}<<<VAR_END>>> sous le numéro <<<VAR_START>>>{{ urbanisme.construction.declaration_prealable.numero }}<<<VAR_END>>>.

{% if urbanisme.construction.declaration_prealable.non_opposition %}
La commune n'a pas fait opposition dans le délai d'un mois. Les travaux peuvent être entrepris.
{% endif %}

**Annexe** : Déclaration préalable
{% endif %}

## Conformité des travaux

{% if urbanisme.construction.conformite %}
{% if urbanisme.construction.conformite.certificat %}
Un certificat de conformité a été délivré le <<<VAR_START>>>{{ urbanisme.construction.conformite.date | format_date }}<<<VAR_END>>> attestant de la conformité des travaux réalisés avec l'autorisation délivrée.

**Annexe** : Certificat de conformité
{% else %}
Les travaux ont été réalisés conformément aux autorisations délivrées. Un certificat de conformité pourra être demandé si nécessaire.
{% endif %}
{% endif %}

## Diagnostics techniques construction

{% if urbanisme.construction.diagnostics %}
Les diagnostics techniques relatifs à la construction ont été réalisés :

{% for diagnostic in urbanisme.construction.diagnostics %}
- **{{ diagnostic.type }}** : Réalisé le <<<VAR_START>>>{{ diagnostic.date | format_date }}<<<VAR_END>>> par <<<VAR_START>>>{{ diagnostic.professionnel }}<<<VAR_END>>>
{% endfor %}
{% endif %}

{% endif %}

# DIAGNOSTICS TECHNIQUES

Les diagnostics techniques suivants ont été réalisés conformément aux dispositions légales :

### Plomb

{% if diagnostics.plomb %}
L'ENSEMBLE IMMOBILIER a été construit {% if diagnostics.plomb.construction_avant_1949 %}avant le 1er janvier 1949{% else %}depuis le 1er janvier 1949{% endif %}.

{% if diagnostics.plomb.construction_avant_1949 %}
Un constat de risque d'exposition au plomb a été établi le <<<VAR_START>>>{{ diagnostics.plomb.date | format_date }}<<<VAR_END>>> par <<<VAR_START>>>{{ diagnostics.plomb.diagnostiqueur.nom }}<<<VAR_END>>>.

Conclusion : <<<VAR_START>>>{{ diagnostics.plomb.conclusion }}<<<VAR_END>>>.
{% else %}
En conséquence, le bien n'entre pas dans le champ d'application des dispositions relatives au diagnostic plomb.
{% endif %}
{% endif %}

### Amiante

{% if diagnostics.amiante %}
Un état mentionnant la présence ou l'absence de matériaux ou produits contenant de l'amiante a été établi le <<<VAR_START>>>{{ diagnostics.amiante.date | format_date }}<<<VAR_END>>> par <<<VAR_START>>>{{ diagnostics.amiante.diagnostiqueur.nom }}<<<VAR_END>>>.

Conclusion : <<<VAR_START>>>{{ diagnostics.amiante.conclusion }}<<<VAR_END>>>.

{% if diagnostics.amiante.presence %}
Des matériaux contenant de l'amiante ont été repérés. Le rapport complet est annexé aux présentes.
{% endif %}
{% endif %}

### Termites

{% if diagnostics.termites %}
Un état relatif à la présence de termites a été établi le <<<VAR_START>>>{{ diagnostics.termites.date | format_date }}<<<VAR_END>>> par <<<VAR_START>>>{{ diagnostics.termites.diagnostiqueur.nom }}<<<VAR_END>>>.

Conclusion : <<<VAR_START>>>{{ diagnostics.termites.conclusion }}<<<VAR_END>>>.
{% endif %}

### Mérules

{% if diagnostics.merules %}
Une information sur la présence d'un risque de mérule a été fournie conformément aux dispositions de l'article L 133-8 du Code de la construction et de l'habitation.

La commune de <<<VAR_START>>>{{ bien.adresse.ville }}<<<VAR_END>>> {% if diagnostics.merules.zone_delimitee %}a fait l'objet d'un arrêté préfectoral délimitant une zone de présence d'un risque de mérule{% else %}n'a pas fait l'objet d'un arrêté préfectoral délimitant une zone de présence d'un risque de mérule{% endif %}.
{% endif %}

### Contrôle de l'installation de gaz

{% if diagnostics.gaz and diagnostics.gaz.diagnostiqueur %}
Un état de l'installation intérieure de gaz a été établi le <<<VAR_START>>>{{ diagnostics.gaz.date | format_date }}<<<VAR_END>>> par <<<VAR_START>>>{{ diagnostics.gaz.diagnostiqueur.nom }}<<<VAR_END>>>.

Conclusion : <<<VAR_START>>>{{ diagnostics.gaz.conclusion }}<<<VAR_END>>>.

{% if diagnostics.gaz.anomalies %}
Des anomalies ont été relevées. Le rapport complet est annexé aux présentes.
{% endif %}
{% elif diagnostics.gaz and diagnostics.gaz.applicable is sameas false %}
Le BIEN n'est pas équipé d'une installation intérieure de gaz. Le diagnostic gaz n'est pas requis.
{% endif %}

### Contrôle de l'installation intérieure d'électricité

{% if diagnostics.electricite %}
Un état de l'installation intérieure d'électricité a été établi le <<<VAR_START>>>{{ diagnostics.electricite.date | format_date }}<<<VAR_END>>> par <<<VAR_START>>>{{ diagnostics.electricite.diagnostiqueur.nom }}<<<VAR_END>>>.

Conclusion : <<<VAR_START>>>{{ diagnostics.electricite.conclusion }}<<<VAR_END>>>.

{% if diagnostics.electricite.anomalies %}
Des anomalies ont été relevées. Le rapport complet est annexé aux présentes.
{% endif %}
{% endif %}

### Diagnostic de performance énergétique (DPE)

{% if diagnostics.dpe %}
Un diagnostic de performance énergétique a été établi le <<<VAR_START>>>{{ diagnostics.dpe.date | format_date }}<<<VAR_END>>> par <<<VAR_START>>>{{ diagnostics.dpe.diagnostiqueur.nom }}<<<VAR_END>>>.

**Classe énergie** : <<<VAR_START>>>{{ diagnostics.dpe.classe_energie }}<<<VAR_END>>>
**Classe GES** : <<<VAR_START>>>{{ diagnostics.dpe.classe_ges }}<<<VAR_END>>>

{% if diagnostics.dpe.classe_energie in ['F', 'G'] %}
**Information importante** : Le bien présente une classe de performance énergétique {{ diagnostics.dpe.classe_energie }}.

Conformément à la loi Climat et Résilience du 22 août 2021, les logements classés G ne pourront plus être proposés à la location à compter du 1er janvier 2025, les logements classés F à compter du 1er janvier 2028.

L'ACQUEREUR déclare avoir été informé de cette situation et des travaux de rénovation énergétique qui pourraient s'avérer nécessaires.
{% endif %}
{% endif %}

### Carnet d'information du logement

{% if diagnostics.carnet_logement %}
Conformément aux dispositions des articles L 126-35-2 à L 126-35-11 et R 126-32 à R 126-34 du Code de la construction et de l'habitation, le carnet d'information du logement a été établi et est communiqué à l'ACQUEREUR.

Le VENDEUR s'engage à transmettre à l'ACQUEREUR une copie de ce carnet d'information au plus tard à la date de signature de l'acte authentique de vente.

**Annexe : Carnet d'information du logement**
{% endif %}

### Audit énergétique

{% if diagnostics.audit_energetique %}
Le BIEN objet des présentes relevant de la loi n° 65-557 du 10 juillet 1965 fixant le statut de la copropriété des immeubles bâtis, un audit énergétique <<<VAR_START>>>{% if diagnostics.audit_energetique.existe %}a été réalisé{% else %}n'est pas requis{% endif %}<<<VAR_END>>>.

{% if diagnostics.audit_energetique.existe %}
L'audit énergétique a été établi le <<<VAR_START>>>{{ diagnostics.audit_energetique.date | format_date }}<<<VAR_END>>> par <<<VAR_START>>>{{ diagnostics.audit_energetique.auditeur.nom }}<<<VAR_END>>>.

**Annexe : Audit énergétique**
{% endif %}
{% endif %}

### Assainissement

{% if diagnostics.assainissement %}
{% if diagnostics.assainissement.type == 'collectif' %}
Le BIEN est raccordé au réseau public d'assainissement collectif.
{% else %}
Le BIEN est équipé d'une installation d'assainissement non collectif.

Un diagnostic de bon fonctionnement et d'entretien de l'installation d'assainissement non collectif a été établi le <<<VAR_START>>>{{ diagnostics.assainissement.diagnostic_date | format_date }}<<<VAR_END>>>.

Conclusion : <<<VAR_START>>>{{ diagnostics.assainissement.conclusion }}<<<VAR_END>>>.
{% endif %}
{% endif %}

### État des risques et pollutions

{% if diagnostics.erp %}
Un état des risques et pollutions a été établi le <<<VAR_START>>>{{ diagnostics.erp.date | format_date }}<<<VAR_END>>>.

La commune de <<<VAR_START>>>{{ bien.adresse.ville }}<<<VAR_END>>> est située dans une zone couverte par <<<VAR_START>>>{% if diagnostics.erp.ppr %}un plan de prévention des risques{% else %}aucun plan de prévention des risques{% endif %}<<<VAR_END>>>.

{% if diagnostics.erp.risques %}
Les risques identifiés sont les suivants : <<<VAR_START>>>{{ diagnostics.erp.risques | join(', ') }}<<<VAR_END>>>.
{% endif %}

**Annexe : État des risques et pollutions**
{% endif %}

### Zone de bruit - Plan d'exposition au bruit des aérodromes

{% if diagnostics.zone_bruit %}
{% if diagnostics.zone_bruit.concerne %}
Le BIEN est situé dans le périmètre d'exposition au bruit des aérodromes défini par l'arrêté préfectoral du <<<VAR_START>>>{{ diagnostics.zone_bruit.arrete_date | format_date }}<<<VAR_END>>>.

Zone concernée : <<<VAR_START>>>{{ diagnostics.zone_bruit.zone }}<<<VAR_END>>>.
{% else %}
Le BIEN n'est pas situé dans le périmètre d'exposition au bruit des aérodromes.
{% endif %}
{% endif %}

### Radon

{% if diagnostics.radon %}
La commune de <<<VAR_START>>>{{ bien.adresse.ville }}<<<VAR_END>>> est classée en zone <<<VAR_START>>>{{ diagnostics.radon.zone }}<<<VAR_END>>> au regard du potentiel radon.

{% if diagnostics.radon.zone in ['2', '3'] %}
Information : Les zones 2 et 3 correspondent à des zones où la présence de radon dans les bâtiments peut atteindre des concentrations élevées. Des mesures préventives peuvent être mises en œuvre pour réduire les concentrations en radon.
{% endif %}
{% endif %}
### REGLEMENTATIONS SPECIFIQUES A LA COPROPRIETE

# NEGOCIATION

{% if negociation %}
{% if negociation.agent_immobilier %}
La présente vente a été négociée par <<<VAR_START>>>{{ negociation.agent_immobilier.nom }}<<<VAR_END>>>, {% if negociation.agent_immobilier.statut == 'agent' %}agent immobilier{% elif negociation.agent_immobilier.statut == 'commercial' %}agent commercial{% endif %}, immatriculé au Registre spécial des agents commerciaux du Tribunal de commerce de <<<VAR_START>>>{{ negociation.agent_immobilier.tribunal }}<<<VAR_END>>> sous le numéro <<<VAR_START>>>{{ negociation.agent_immobilier.numero_rsac }}<<<VAR_END>>>.

{% if negociation.agent_immobilier.carte_professionnelle %}
Carte professionnelle n° <<<VAR_START>>>{{ negociation.agent_immobilier.carte_professionnelle }}<<<VAR_END>>> délivrée par la Chambre de Commerce et d'Industrie de <<<VAR_START>>>{{ negociation.agent_immobilier.cci }}<<<VAR_END>>>.
{% endif %}

{% if negociation.agent_immobilier.garantie_financiere %}
Garantie financière souscrite auprès de <<<VAR_START>>>{{ negociation.agent_immobilier.garantie_financiere.organisme }}<<<VAR_END>>> à hauteur de <<<VAR_START>>>{{ negociation.agent_immobilier.garantie_financiere.montant | format_nombre }}<<<VAR_END>>> EUR.
{% endif %}

{% if negociation.commission %}
La commission de l'agent, d'un montant de <<<VAR_START>>>{{ negociation.commission.montant | format_nombre }}<<<VAR_END>>> EUR TTC (<<<VAR_START>>>{{ negociation.commission.montant | montant_en_lettres }}<<<VAR_END>>> euros), est à la charge {% if negociation.commission.charge == 'vendeur' %}du VENDEUR{% elif negociation.commission.charge == 'acquereur' %}de l'ACQUEREUR{% elif negociation.commission.charge == 'partagee' %}des parties à parts égales{% endif %} et sera acquittée lors de la signature des présentes.
{% endif %}
{% else %}
La présente vente n'a fait l'objet d'aucune intervention d'un agent immobilier ou d'un courtier. Elle résulte de pourparlers directs entre les parties.
{% endif %}
{% endif %}

# Modalités de délivrance de la copie authentique

Les parties sont informées que la présente vente sera publiée au service de la publicité foncière de <<<VAR_START>>>{{ bien.adresse.departement }}<<<VAR_END>>>.

{% if modalites_delivrance %}
{% if modalites_delivrance.copie_authentique %}
La copie authentique de l'acte sera délivrée :

{% if modalites_delivrance.copie_authentique.delai %}
- Dans un délai de <<<VAR_START>>>{{ modalites_delivrance.copie_authentique.delai }}<<<VAR_END>>> jours suivant la réalisation de la formalité de publicité foncière
{% endif %}

{% if modalites_delivrance.copie_authentique.mode == 'remise_main_propre' %}
- Par remise en main propre à l'étude
{% elif modalites_delivrance.copie_authentique.mode == 'envoi_postal' %}
- Par envoi postal recommandé avec accusé de réception
{% elif modalites_delivrance.copie_authentique.mode == 'electronique' %}
- Par voie électronique sécurisée
{% endif %}

{% if modalites_delivrance.copie_authentique.frais %}
Les frais de délivrance de la copie authentique, d'un montant de <<<VAR_START>>>{{ modalites_delivrance.copie_authentique.frais | format_nombre }}<<<VAR_END>>> EUR, sont à la charge de l'ACQUEREUR.
{% endif %}
{% endif %}
{% endif %}

# CONCLUSION DU CONTRAT

Les parties déclarent que les dispositions de ce contrat ont été, en respect des règles impératives de l'article 1104 du Code civil, négociées de bonne foi. Elles affirment qu'il reflète l'équilibre voulu par chacune d'elles.

{% if conclusion_contrat %}
{% if conclusion_contrat.negociation_bonne_foi %}
Les parties attestent avoir négocié de manière loyale et transparente, chacune ayant eu la possibilité de formuler ses observations et propositions.
{% endif %}

{% if conclusion_contrat.information_prealable %}
Les parties reconnaissent avoir reçu et pris connaissance de toutes les informations nécessaires à la formation de leur consentement, notamment :

{% for info in conclusion_contrat.information_prealable %}
- {{ info }}
{% endfor %}
{% endif %}
{% endif %}

# DEVOIR D'INFORMATION RECIPROQUE

Les parties s'engagent réciproquement à s'informer mutuellement de tout élément nouveau susceptible d'avoir une incidence sur l'exécution du présent contrat.

{% if devoir_information %}
Cet engagement porte notamment sur :

{% if devoir_information.elements %}
{% for element in devoir_information.elements %}
- {{ element }}
{% endfor %}
{% else %}
- Tout changement de situation personnelle (adresse, état civil, capacité juridique)
- Toute modification affectant le bien (sinistre, travaux, servitudes nouvelles)
- Tout litige ou contentieux relatif au bien
- Toute évolution réglementaire ou fiscale ayant un impact sur les droits et obligations des parties
{% endif %}

Le manquement à cette obligation pourra engager la responsabilité de la partie défaillante sur le fondement des articles 1104 et suivants du Code civil.
{% endif %}

# Renonciation à l'imprévision

{% if imprevision %}
{% if imprevision.renonciation %}
En application de l'article 1195 du Code civil, les parties conviennent expressément de renoncer à se prévaloir du régime de l'imprévision.

En conséquence, même si un changement de circonstances imprévisible lors de la conclusion du contrat rend l'exécution excessivement onéreuse pour une partie qui n'avait pas accepté d'en assumer le risque, celle-ci ne pourra demander une renégociation du contrat à son cocontractant ni saisir le juge à cette fin.

Les parties reconnaissent avoir été informées par le notaire soussigné de la portée de cette renonciation.
{% else %}
Les parties n'ont pas renoncé à l'application de l'article 1195 du Code civil relatif à l'imprévision.
{% endif %}
{% endif %}

# CONVENTIONS ANTERIEURES

{% if conventions_anterieures %}
{% if conventions_anterieures.compromis %}
Les présentes font suite à un compromis de vente sous signature privée en date du <<<VAR_START>>>{{ conventions_anterieures.compromis.date | format_date }}<<<VAR_END>>>, enregistré le <<<VAR_START>>>{{ conventions_anterieures.compromis.date_enregistrement | format_date }}<<<VAR_END>>> au Service de l'enregistrement de <<<VAR_START>>>{{ conventions_anterieures.compromis.lieu_enregistrement }}<<<VAR_END>>>, folio <<<VAR_START>>>{{ conventions_anterieures.compromis.folio }}<<<VAR_END>>>, case <<<VAR_START>>>{{ conventions_anterieures.compromis.case }}<<<VAR_END>>>.

Le présent acte réitère et complète les termes de ce compromis, les parties déclarant qu'il n'existe aucune contre-lettre ni aucun avenant modificatif autres que ceux éventuellement mentionnés aux présentes.

{% if conventions_anterieures.compromis.conditions_suspensives %}
Les conditions suspensives stipulées au compromis {% if conventions_anterieures.compromis.conditions_realisees %}ont toutes été réalisées{% else %}ont été levées ou sont devenues caduques{% endif %}.
{% endif %}
{% else %}
Le présent acte n'est précédé d'aucun avant-contrat.
{% endif %}

{% if conventions_anterieures.autres %}
{% for convention in conventions_anterieures.autres %}
**{{ convention.type }}**

{{ convention.description }}

{% if convention.date %}
Date : <<<VAR_START>>>{{ convention.date | format_date }}<<<VAR_END>>>
{% endif %}
{% endfor %}
{% endif %}
{% endif %}

# Médiation

Les parties sont informées qu'en cas de litige entre elles ou avec un tiers, elles pourront, préalablement à toute instance judiciaire, le soumettre à un médiateur qui sera désigné et missionné par le **Centre de médiation notariale** dont elles trouveront toutes les coordonnées et renseignements utiles sur le site : **https://www.mediation.notaires.fr**.

{% if mediation %}
{% if mediation.clause_obligatoire %}
Les parties s'engagent à recourir obligatoirement à la médiation avant toute action en justice, sauf en cas d'urgence ou de mesures conservatoires.

Le délai de médiation ne pourra excéder <<<VAR_START>>>{{ mediation.delai_maximum | default(3) }}<<<VAR_END>>> mois.

Les frais de médiation seront partagés par moitié entre les parties, sauf accord contraire.
{% endif %}
{% endif %}

# ELECTION DE DOMICILE

Les parties élisent domicile :

- En leur demeure ou siège respectif pour l'exécution des présentes et de leurs suites
- En l'office notarial pour la publicité foncière, l'envoi des pièces et la correspondance s'y rapportant

{% if election_domicile %}
{% if election_domicile.vendeur %}
**VENDEUR** : <<<VAR_START>>>{{ election_domicile.vendeur }}<<<VAR_END>>>
{% endif %}

{% if election_domicile.acquereur %}
**ACQUEREUR** : <<<VAR_START>>>{{ election_domicile.acquereur }}<<<VAR_END>>>
{% endif %}

Chacune des parties s'oblige à communiquer au notaire tout changement de domicile ou siège et ce par lettre recommandée avec demande d'avis de réception.
{% endif %}

En suite des présentes, la correspondance et le renvoi des pièces à l'ACQUEREUR devront s'effectuer à l'adresse du bien présentement acquis.

La correspondance auprès du VENDEUR s'effectuera à l'adresse indiquée en tête des présentes.

# TITRES - CORRESPONDANCE ET RENVOI DES PIECES

Il ne sera remis aucun ancien titre de propriété à l'ACQUEREUR qui pourra se faire délivrer, à ses frais, ceux dont il pourrait avoir besoin, et sera subrogé dans tous les droits du VENDEUR à ce sujet.

{% if titres %}
{% if titres.anciens_titres %}
Les anciens titres de propriété concernant le BIEN sont les suivants :

{% for titre in titres.anciens_titres %}
- {{ titre.type }} du <<<VAR_START>>>{{ titre.date | format_date }}<<<VAR_END>>> reçu par Maître <<<VAR_START>>>{{ titre.notaire }}<<<VAR_END>>>, publié au service de la publicité foncière de <<<VAR_START>>>{{ titre.conservation }}<<<VAR_END>>> le <<<VAR_START>>>{{ titre.date_publication | format_date }}<<<VAR_END>>>, volume <<<VAR_START>>>{{ titre.volume }}<<<VAR_END>>>, numéro <<<VAR_START>>>{{ titre.numero }}<<<VAR_END>>>
{% endfor %}
{% endif %}

{% if titres.correspondance %}
La correspondance relative à l'exécution du présent acte sera adressée :

- Pour le VENDEUR : <<<VAR_START>>>{{ titres.correspondance.vendeur }}<<<VAR_END>>>
- Pour l'ACQUEREUR : <<<VAR_START>>>{{ titres.correspondance.acquereur }}<<<VAR_END>>>
{% endif %}
{% endif %}

# Pouvoirs - Publicité foncière

Pour l'accomplissement des formalités de publicité foncière ou réparer une erreur matérielle telle que l'omission d'une pièce annexe dont le contenu est relaté aux présentes, les parties agissant dans un intérêt commun donnent tous pouvoirs nécessaires à tout notaire ou à tout collaborateur de l'office notarial dénommé en tête des présentes, à l'effet de faire dresser et signer tous actes complémentaires ou rectificatifs pour mettre le présent acte en concordance avec tous les documents hypothécaires, cadastraux ou d'état civil.

{% if pouvoirs %}
{% if pouvoirs.complementaires %}
Les parties donnent également pouvoir pour :

{% for pouvoir in pouvoirs.complementaires %}
- {{ pouvoir }}
{% endfor %}
{% endif %}

{% if pouvoirs.restrictions %}
Ces pouvoirs sont limités aux opérations suivantes : <<<VAR_START>>>{{ pouvoirs.restrictions | join(', ') }}<<<VAR_END>>>.
{% endif %}
{% endif %}

# Affirmation de sincérité

Les parties affirment, sous les peines édictées par l'article 1837 du Code général des impôts, que le présent acte exprime l'intégralité du prix.

Elles reconnaissent avoir été informées par le notaire soussigné des sanctions fiscales et des peines correctionnelles encourues en cas d'inexactitude de cette affirmation ainsi que des conséquences civiles édictées par l'article 1202 du Code civil.

Le notaire soussigné précise qu'à sa connaissance le présent acte n'est modifié ni contredit par aucune contre-lettre contenant augmentation du prix.

{% if affirmation %}
{% if affirmation.sanctions %}
Les parties ont été expressément informées que :

- Toute dissimulation de prix est punie d'une amende de 50% du montant dissimulé (article 1840 G ter du CGI)
- La minoration du prix peut constituer le délit d'escroquerie au jugement puni de 5 ans d'emprisonnement et 375 000 EUR d'amende (article 313-1 du Code pénal)
- La dissimulation de prix permet à l'administration fiscale de se prévaloir d'une présomption de revenu d'origine indéterminée
{% endif %}
{% endif %}

# Demande de restitution – Autorisation de destruction des documents et pièces

Les originaux des documents et pièces remis par les parties au notaire leur seront restitués, si elles en font la demande expresse dans le délai de <<<VAR_START>>>{{ restitution.delai | default('un mois') }}<<<VAR_END>>> à compter des présentes.

A défaut, les parties autorisent l'office notarial à détruire ces documents et pièces, et notamment tout avant-contrat sous signature privée pouvant avoir été établi en vue de la conclusion du présent acte, considérant que celui-ci contient l'intégralité des conventions auxquelles elles ont entendu donner le caractère d'authenticité.

{% if restitution %}
{% if restitution.documents_conserves %}
Les parties demandent expressément la conservation des documents suivants :

{% for doc in restitution.documents_conserves %}
- {{ doc }}
{% endfor %}
{% endif %}

{% if restitution.duree_conservation %}
Les documents seront conservés pendant une durée de <<<VAR_START>>>{{ restitution.duree_conservation }}<<<VAR_END>>> ans.
{% endif %}
{% endif %}

# Mention sur la protection des données personnelles

L'Office notarial traite des données personnelles concernant les personnes mentionnées aux présentes, pour l'accomplissement des activités notariales, notamment de formalités d'actes.

Ce traitement est fondé sur le respect d'une obligation légale et l'exécution d'une mission relevant de l'exercice de l'autorité publique déléguée par l'Etat dont sont investis les notaires, officiers publics, conformément à l'ordonnance n°45-2590 du 2 novembre 1945.

Ces données seront susceptibles d'être transférées aux destinataires suivants :

- Les administrations ou partenaires légalement habilités tels que la Direction Générale des Finances Publiques, ou, le cas échéant, le livre foncier
- Les instances notariales
- Les organismes du notariat
- Les fichiers centraux de la profession notariale (Fichier Central Des Dernières Volontés, Minutier Central Électronique des Notaires, registre du PACS, etc.)

{% if rgpd %}
{% if rgpd.duree_conservation %}
Les données seront conservées pendant la durée légale de conservation des actes notariés, soit <<<VAR_START>>>{{ rgpd.duree_conservation | default(75) }}<<<VAR_END>>> ans à compter de la signature de l'acte.
{% endif %}

Les personnes concernées disposent d'un droit d'accès, de rectification, d'effacement, de limitation et de portabilité de leurs données ainsi que d'un droit d'opposition au traitement et d'un droit de définir des directives relatives au sort de leurs données après leur décès.

Ces droits peuvent être exercés auprès de l'office notarial :

{% if rgpd.contact_dpo %}
- Par courrier : <<<VAR_START>>>{{ rgpd.contact_dpo.adresse }}<<<VAR_END>>>
- Par email : <<<VAR_START>>>{{ rgpd.contact_dpo.email }}<<<VAR_END>>>
{% endif %}

En cas de difficulté, les personnes concernées peuvent saisir la Commission Nationale de l'Informatique et des Libertés (CNIL) : www.cnil.fr.
{% endif %}

# Certification d'identité

Le notaire soussigné certifie que l'identité complète des parties telle qu'elle est indiquée en tête des présentes lui a été régulièrement justifiée.

{% if certification_identite %}
{% if certification_identite.documents_presentes %}
Les documents d'identité suivants ont été présentés :

**VENDEUR** :
{% for doc in certification_identite.documents_presentes.vendeur %}
- {{ doc.type }} n° <<<VAR_START>>>{{ doc.numero }}<<<VAR_END>>> délivré le <<<VAR_START>>>{{ doc.date | format_date }}<<<VAR_END>>> par <<<VAR_START>>>{{ doc.autorite }}<<<VAR_END>>>
{% endfor %}

**ACQUEREUR** :
{% for doc in certification_identite.documents_presentes.acquereur %}
- {{ doc.type }} n° <<<VAR_START>>>{{ doc.numero }}<<<VAR_END>>> délivré le <<<VAR_START>>>{{ doc.date | format_date }}<<<VAR_END>>> par <<<VAR_START>>>{{ doc.autorite }}<<<VAR_END>>>
{% endfor %}
{% endif %}

Le notaire a procédé à la vérification de l'authenticité de ces documents conformément aux dispositions de l'article 1369 du Code civil.
{% endif %}

# Origine de propriété

{% if origine_propriete %}
{% include 'sections/section_origine_propriete.md' %}
{% endif %}

{% if bien and bien.lots and bien.lots|length > 0 %}
{% include 'sections/section_lots_details.md' %}
{% endif %}

{% if fiscalite and fiscalite.contribution_securite_immobiliere %}
{% include 'sections/section_fiscalite_complete.md' %}
{% endif %}

{% if garanties %}
{% include 'sections/section_garanties.md' %}
{% endif %}

{% if servitudes %}
{% include 'sections/section_servitudes.md' %}
{% endif %}

{% if etat_bien %}
{% include 'sections/section_etat_bien.md' %}
{% endif %}

{% if equipements %}
{% include 'sections/section_equipements.md' %}
{% endif %}

{% if impots %}
{% include 'sections/section_impots_taxes.md' %}
{% endif %}

{% if obligations_proprietaire %}
{% include 'sections/section_obligations_proprietaire.md' %}
{% endif %}

{% if contrats_fourniture %}
{% include 'sections/section_contrats_fourniture.md' %}
{% endif %}

{% if assurance %}
{% include 'sections/section_assurance.md' %}
{% endif %}

{% if contrat_affichage %}
{% include 'sections/section_contrat_affichage.md' %}
{% endif %}

{% if urbanisme and (urbanisme.plu or urbanisme.servitudes_utilite_publique or urbanisme.droit_preemption) %}
{% include 'sections/section_urbanisme_detail.md' %}
{% endif %}

{% if diagnostics %}
{% include 'sections/section_diagnostics_complets.md' %}
{% endif %}

{% if avantages_fiscaux or ptz %}
{% include 'sections/section_avantages_fiscaux.md' %}
{% endif %}

{% if travaux %}
{% include 'sections/section_travaux_construction.md' %}
{% endif %}

{% if absence_construction %}
{% include 'sections/section_absence_construction.md' %}
{% endif %}

{% if paiement and paiement.prets and paiement.prets|length > 0 %}
{% include 'sections/section_financement_detail.md' %}
{% endif %}

{% if aides %}
{% include 'sections/section_aides_logement.md' %}
{% endif %}

{% if risques_pollution or erp %}
{% include 'sections/section_risques_pollution.md' %}
{% endif %}

{% if diagnostics and (diagnostics.erp or diagnostics.sinistres or diagnostics.environnement) %}
{% include 'sections/section_diagnostics_environnementaux.md' %}
{% endif %}

{% if situation_environnementale %}
{% include 'sections/section_situation_environnementale.md' %}
{% endif %}

{% if copropriete and copropriete.syndic %}
{% include 'sections/section_syndic_informations.md' %}
{% endif %}

{% if copropriete %}
{% include 'sections/section_copropriete_reglementations.md' %}
{% endif %}

{% if copropriete %}
{% include 'sections/section_repartition_charges.md' %}
{% endif %}

{% if conventions_parties or consultation_bases %}
{% include 'sections/section_conventions_parties.md' %}
{% endif %}

{% if copropriete %}
{% include 'sections/section_travaux_urgents.md' %}
{% endif %}

{% if copropriete and (copropriete.reglement_charges or copropriete.solde_anterieur or copropriete.avances) %}
{% include 'sections/section_reglement_charges.md' %}
{% endif %}

{% if copropriete and copropriete.syndic %}
{% include 'sections/section_notification_mutation.md' %}
{% endif %}

{% if negociation %}
{% include 'sections/section_negociation.md' %}
{% endif %}

# Formalisme lié aux annexes

Le présent acte est complété par les annexes suivantes, qui en font partie intégrante :

{% if annexes %}
{% for annexe in annexes %}
**Annexe n°{{ loop.index }}** : {{ annexe.titre }}
{% if annexe.description %}
{{ annexe.description }}
{% endif %}
{% endfor %}

Les parties déclarent avoir pris connaissance de l'ensemble de ces annexes préalablement à la signature des présentes.
{% else %}
Aucune annexe n'est jointe au présent acte.
{% endif %}
