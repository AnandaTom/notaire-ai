{# ============================================================================
   PROMESSE UNILATÉRALE DE VENTE EN VIAGER
   Version: 1.0.0 - 10 février 2026
   Basée sur Trame L (viager) — Template séparé (+25% contenu unique)

   Contient :
   - En-tête et comparution (CRÉDIRENTIER / DÉBIRENTIER)
   - Terminologie viager
   - Désignation du bien (hors copropriété)
   - Santé du promettant (articles 1974-1975 C. civ.)
   - Prix : bouquet + rente viagère + valeurs vénale/économique
   - Droit d'usage et d'habitation (DUH)
   - Rente viagère (conventions, indexation, rachat)
   - Garanties viager (privilège, clause pénale, résolutoire)
   - Conditions suspensives
   - Diagnostics et environnement
   - Dispositions finales
   ============================================================================ #}

{FIRST_PAGE_HEADER_START}
{{ acte.numero_repertoire }}
{{ acte.reference_interne }}

Le {{ acte.date.jour }} {{ acte.date.mois | mois_en_lettres }} {{ acte.date.annee }}
{FIRST_PAGE_HEADER_END}
**PROMESSE UNILATERALE DE VENTE EN VIAGER**
**Par {% for promettant in promettants %}{{ promettant.civilite }} {{ promettant.nom }}{% if not loop.last %} et {% endif %}{% endfor %}**
**Au profit de {% for beneficiaire in beneficiaires %}{{ beneficiaire.civilite }} {{ beneficiaire.nom }}{% if not loop.last %} et {% endif %}{% endfor %}**
**\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\***

**L'AN {{ acte.date.annee | annee_en_lettres }},**
**Le {{ acte.date.jour | jour_en_lettres }} {{ acte.date.mois | mois_en_lettres | upper }}**
**A {{ acte.notaire.ville }} ({{ acte.notaire.departement }}), {{ acte.notaire.adresse }}, au siège de l'Office Notarial, ci-après nommé,**
**{{ acte.notaire.civilite }} {{ acte.notaire.prenom }} {{ acte.notaire.nom }}, Notaire de la société par actions simplifiée dénommée « {{ acte.notaire.societe }} » dont le siège social est situé à {{ acte.notaire.ville }} ({{ acte.notaire.departement }}), {{ acte.notaire.adresse }}, identifié sous le numéro CRPCEN {{ acte.notaire.crpcen }},**
**Notaire assistant le PROMETTANT**

{% if acte.notaire_beneficiaire %}
**Avec la participation de {{ acte.notaire_beneficiaire.civilite }} {{ acte.notaire_beneficiaire.prenom }} {{ acte.notaire_beneficiaire.nom }}, notaire à {{ acte.notaire_beneficiaire.ville }}, assistant le BENEFICIAIRE.**
{% endif %}

**A RECU le présent acte contenant PROMESSE DE VENTE EN VIAGER à la requête de :**

# PROMETTANT (CRÉDIRENTIER)

{% for promettant in promettants %}
{{ promettant.civilite }} {{ promettant.prenoms }} {{ promettant.nom }}, {{ promettant.profession }}, demeurant à {{ promettant.adresse }}, {{ promettant.code_postal }} {{ promettant.ville }}.
{% if promettant.civilite == "Madame" %}Née{% else %}Né{% endif %} à {{ promettant.lieu_naissance }} le {{ promettant.date_naissance | format_date }}.
{% if promettant.civilite == "Madame" %}Âgée{% else %}Âgé{% endif %} de {{ promettant.age }} ans.
{% if promettant.situation_matrimoniale.statut == "celibataire" %}
Célibataire.
{% if promettant.civilite == "Madame" %}Non liée{% else %}Non lié{% endif %} par un pacte civil de solidarité.
{% elif promettant.situation_matrimoniale.statut == "marie" %}
{% if promettant.civilite == "Madame" %}Mariée{% else %}Marié{% endif %} sous le régime de {{ promettant.situation_matrimoniale.regime_libelle | default("la communauté légale") }}{% if promettant.situation_matrimoniale.contrat_mariage %}, aux termes d'un contrat de mariage reçu par {{ promettant.situation_matrimoniale.contrat_mariage.notaire }} le {{ promettant.situation_matrimoniale.contrat_mariage.date }}{% endif %}.
{% elif promettant.situation_matrimoniale.statut == "pacse" %}
{% if promettant.civilite == "Madame" %}Soumise{% else %}Soumis{% endif %} à un pacte civil de solidarité sous le régime de {{ promettant.situation_matrimoniale.pacs.regime_libelle }} en date du {{ promettant.situation_matrimoniale.pacs.date | format_date }} enregistré à {{ promettant.situation_matrimoniale.pacs.lieu_enregistrement }}.
{% elif promettant.situation_matrimoniale.statut == "divorce" %}
{% if promettant.civilite == "Madame" %}Divorcée{% else %}Divorcé{% endif %}.
{% elif promettant.situation_matrimoniale.statut == "veuf" %}
{% if promettant.civilite == "Madame" %}Veuve{% else %}Veuf{% endif %}.
{% endif %}
De nationalité {{ promettant.nationalite }}.
{% if promettant.resident_fiscal %}{% if promettant.civilite == "Madame" %}Résidente{% else %}Résident{% endif %} au sens de la réglementation fiscale.{% endif %}

{% if promettant.coordonnees %}
**<u>Coordonnées :</u>**

<u>{{ promettant.civilite }} {{ promettant.nom }}</u>
{% if promettant.coordonnees.telephone %}Téléphone mobile : {{ promettant.coordonnees.telephone }}{% endif %}
{% if promettant.coordonnees.courriel %}Courriel : {{ promettant.coordonnees.courriel }}{% endif %}
{% endif %}

{% endfor %}

# BENEFICIAIRE (DÉBIRENTIER)

{% for beneficiaire in beneficiaires %}
{{ beneficiaire.civilite }} {{ beneficiaire.prenoms }} {{ beneficiaire.nom }}, {{ beneficiaire.profession }}, demeurant à {{ beneficiaire.adresse }}, {{ beneficiaire.code_postal }} {{ beneficiaire.ville }}.
{% if beneficiaire.civilite == "Madame" %}Née{% else %}Né{% endif %} à {{ beneficiaire.lieu_naissance }} le {{ beneficiaire.date_naissance | format_date }}.
{% if beneficiaire.situation_matrimoniale.statut == "celibataire" %}
Célibataire.
{% if beneficiaire.civilite == "Madame" %}Non liée{% else %}Non lié{% endif %} par un pacte civil de solidarité.
{% elif beneficiaire.situation_matrimoniale.statut == "marie" %}
{% if beneficiaire.civilite == "Madame" %}Mariée{% else %}Marié{% endif %} sous le régime de {{ beneficiaire.situation_matrimoniale.regime_libelle | default("la communauté légale") }}{% if beneficiaire.situation_matrimoniale.contrat_mariage %}, aux termes d'un contrat de mariage reçu par {{ beneficiaire.situation_matrimoniale.contrat_mariage.notaire }} le {{ beneficiaire.situation_matrimoniale.contrat_mariage.date }}{% endif %}.
{% elif beneficiaire.situation_matrimoniale.statut == "pacse" %}
{% if beneficiaire.civilite == "Madame" %}Soumise{% else %}Soumis{% endif %} à un pacte civil de solidarité sous le régime de {{ beneficiaire.situation_matrimoniale.pacs.regime_libelle }} en date du {{ beneficiaire.situation_matrimoniale.pacs.date | format_date }} enregistré à {{ beneficiaire.situation_matrimoniale.pacs.lieu_enregistrement }}.
{% elif beneficiaire.situation_matrimoniale.statut == "divorce" %}
{% if beneficiaire.civilite == "Madame" %}Divorcée{% else %}Divorcé{% endif %}.
{% elif beneficiaire.situation_matrimoniale.statut == "veuf" %}
{% if beneficiaire.civilite == "Madame" %}Veuve{% else %}Veuf{% endif %}.
{% endif %}
De nationalité {{ beneficiaire.nationalite }}.
{% if beneficiaire.resident_fiscal %}{% if beneficiaire.civilite == "Madame" %}Résidente{% else %}Résident{% endif %} au sens de la réglementation fiscale.{% endif %}

{% if beneficiaire.coordonnees %}
**<u>Coordonnées :</u>**

<u>{{ beneficiaire.civilite }} {{ beneficiaire.nom }}</u>
{% if beneficiaire.coordonnees.telephone %}Téléphone mobile : {{ beneficiaire.coordonnees.telephone }}{% endif %}
{% if beneficiaire.coordonnees.courriel %}Courriel : {{ beneficiaire.coordonnees.courriel }}{% endif %}
{% endif %}

{% endfor %}

# Quotités acquises

{% if quotites_a_determiner %}
{% for beneficiaire in beneficiaires %}{{ beneficiaire.civilite }} {{ beneficiaire.nom }}{% if not loop.last %} et {% endif %}{% endfor %} feront l'acquisition de la **nue-propriété** du **BIEN** dans des quotités à déterminer au plus tard lors de la réitération des présentes.
{% else %}
{% for quotite in quotites_beneficiaires %}
{{ beneficiaires[quotite.personne_index].civilite }} {{ beneficiaires[quotite.personne_index].nom }} acquerra {{ quotite.quotite }} en {{ quotite.type_propriete | replace("_", " ") }}.
{% endfor %}
{% endif %}

# Déclarations des parties sur leur capacité
Les parties, et le cas échéant leurs représentants, attestent que rien ne peut limiter leur capacité pour l'exécution des engagements qu'elles prennent aux présentes, et elles déclarent notamment :

* que leur état civil et leurs qualités indiqués en tête des présentes sont exacts,
* qu'elles ne sont pas en état de cessation de paiement, de rétablissement professionnel, de redressement ou liquidation judiciaire ou sous procédure de sauvegarde des entreprises,
* qu'elles n'ont pas été associées dans une société mise en liquidation judiciaire suivant jugement publié depuis moins de cinq ans et dans laquelle elles étaient tenues indéfiniment et solidairement ou seulement conjointement du passif social,
* qu'il n'a été formé aucune opposition au présent acte par un éventuel cogérant,
* qu'elles ne sont concernées :
* par aucune des mesures légales relatives aux personnes protégées qui ne seraient pas révélées aux présentes,
* par aucune des dispositions du Code de la consommation sur le règlement des situations de surendettement, sauf là aussi ce qui peut être spécifié aux présentes,
* et pour le **BENEFICIAIRE** spécialement qu'il n'est, ni à titre personnel, ni en tant qu'associé ou mandataire social, soumis à l'interdiction d'acquérir prévue par l'article 225-26 du Code pénal.

# Documents relatifs à la capacité et à la qualité des parties
Les pièces suivantes ont été portées à la connaissance du rédacteur des présentes à l'appui des déclarations des parties :

{% for promettant in promettants %}
**Concernant {{ promettant.civilite }} {{ promettant.nom }}**

* Carte nationale d'identité.
* Compte rendu de l'interrogation du site bodacc.fr.

{% endfor %}
{% for beneficiaire in beneficiaires %}
**Concernant {{ beneficiaire.civilite }} {{ beneficiaire.nom }}**

* Carte nationale d'identité.
* Compte rendu de l'interrogation du site bodacc.fr.

{% endfor %}

Ces documents ne révèlent aucun empêchement des parties à la signature des présentes.

# Présence - représentation
{% for promettant in promettants %}
- {{ promettant.civilite }} {{ promettant.nom }} est {% if promettant.civilite == "Madame" %}présente{% else %}présent{% endif %} à l'acte.
{% endfor %}
{% for beneficiaire in beneficiaires %}
- {{ beneficiaire.civilite }} {{ beneficiaire.nom }} est {% if beneficiaire.civilite == "Madame" %}présente{% else %}présent{% endif %} à l'acte.
{% endfor %}

# CONCLUSION DU CONTRAT
Les parties déclarent que les dispositions de ce contrat ont été, en respect des règles impératives de l'article 1104 du Code civil, négociées de bonne foi. Elles affirment qu'il reflète l'équilibre voulu par chacune d'elles.

# DEVOIR D'INFORMATION RECIPROQUE
En application de l'article 1112-1 du Code civil qui impose aux parties un devoir précontractuel d'information, qui ne saurait toutefois porter sur le prix, le **PROMETTANT** déclare avoir porté à la connaissance du **BENEFICIAIRE** l'ensemble des informations dont il dispose ayant un lien direct et nécessaire avec le contenu du présent contrat et dont l'importance pourrait être déterminante de son consentement.
Ce devoir s'applique à toute information sur les caractéristiques juridiques, matérielles et environnementales relatives au bien, ainsi qu'à son usage, dont il a personnellement connaissance par lui-même et par des tiers, sans que ces informations puissent être limitées dans le temps.
Le **PROMETTANT** reconnaît être informé qu'un manquement à ce devoir serait sanctionné par la mise en œuvre de sa responsabilité, avec possibilité d'annulation du contrat s'il a vicié le consentement du **BENEFICIAIRE**.
Pareillement, le **BENEFICIAIRE** déclare avoir rempli les mêmes engagements, tout manquement pouvant être sanctionné comme indiqué ci-dessus.
Le devoir d'information est donc réciproque.
En outre, conformément aux dispositions de l'article 1602 du Code civil, le **PROMETTANT** est tenu d'expliquer clairement ce à quoi il s'oblige, tout pacte obscur ou ambigu s'interprétant contre lui.
Les **PARTIES** attestent que les informations déterminantes connues d'elles, données et reçues, sont rapportées aux présentes.

# OBJET DU CONTRAT – PROMESSE UNILATERALE DE VENTE EN VIAGER
Le **PROMETTANT** confère au **BENEFICIAIRE** la faculté d'acquérir en viager les **BIENS** ci-dessous identifiés.
Le **PROMETTANT** prend cet engagement pour lui-même ou ses ayants droit même protégés.
Le **BENEFICIAIRE** accepte la présente promesse de vente en tant que promesse, mais se réserve la faculté d'en demander ou non la réalisation.

# TERMINOLOGIE
Pour la compréhension de certains termes aux présentes, il est préalablement expliqué ce qui suit :
**-** Le **"PROMETTANT"** ou **"CRÉDIRENTIER"** désignera le ou les promettants (vendeurs), qui en cas de pluralité contracteront les obligations mises à leur charge solidairement entre eux.
**-** Le **"BENEFICIAIRE"** ou **"DÉBIRENTIER"** désignera le ou les bénéficiaires (acquéreurs), qui en cas de pluralité contracteront les obligations mises à leur charge solidairement entre eux.
**-** Les **"BIENS"** désigneront les biens et droits immobiliers objet de la présente promesse de vente.
**-** Le **"BOUQUET"** désignera le capital versé comptant au jour de la réitération de la vente en la forme authentique.
**-** La **"RENTE VIAGÈRE"** désignera la somme versée périodiquement par le débirentier au crédirentier, sa vie durant, en contrepartie du transfert de propriété du bien.

# Identification du bien

{% if bien.adresse %}
| Lieu de situation du bien vendu | |
| :---- | :---- |
| **Adresse** | {{ bien.adresse.numero }} {{ bien.adresse.voie }}, {{ bien.adresse.code_postal }} {{ bien.adresse.ville }} |
| **Commune** | {{ bien.adresse.ville }} ({{ bien.adresse.departement }}) |
{% if bien.adresse.code_insee %}
| **Code INSEE** | {{ bien.adresse.code_insee }} |
{% endif %}
{% if bien.cadastre and bien.cadastre[0] %}
| **Références cadastrales** | Section {{ bien.cadastre[0].section }} n° {{ bien.cadastre[0].numero }} |
{% endif %}
{% endif %}

## Désignation

**Un bien immobilier situé à {{ bien.adresse.ville }} ({{ bien.adresse.departement }}) {{ bien.adresse.code_postal }} {{ bien.adresse.numero }} {{ bien.adresse.voie }}.**

{{ bien.description }}

{% if bien.nature %}
**Nature du bien** : {{ bien.nature }}
{% endif %}

Figurant ainsi au cadastre :

| Section | N° | Lieudit | Surface |
| :---- | :---- | :---- | :---- |
{% for parcelle in bien.cadastre %}
| {{ parcelle.section }} | {{ parcelle.numero }} | {{ parcelle.lieudit }} | {{ parcelle.surface }}{% if parcelle.surface_m2 %} ({{ parcelle.surface_m2 }} m²){% endif %} |
{% endfor %}
{% if bien.cadastre_total_surface %}
| | | **Total** | **{{ bien.cadastre_total_surface }}** |
{% endif %}

Un extrait de plan cadastral est annexé.
Un extrait de plan Géoportail avec vue aérienne est annexé.

**Annexe n°1 : Plans cadastral et géoportail**

{% if bien.division_cadastrale %}
**Rappel de division cadastrale**

La parcelle, sise sur la commune de {{ bien.adresse.ville }} ({{ bien.adresse.code_postal }}), originairement cadastrée {{ bien.division_cadastrale.parcelle_origine }} a fait l'objet d'une division en plusieurs parcelles de moindre importance.
De cette division sont issues les parcelles cadastrées {{ bien.division_cadastrale.parcelles_issues | join(", ") }}.
Le document modificatif du parcellaire cadastral, créant cette division, a fait l'objet d'une publication au service de la publicité foncière de {{ bien.division_cadastrale.publication.service }}, le {{ bien.division_cadastrale.publication.date }}, volume {{ bien.division_cadastrale.publication.volume }}, numéro {{ bien.division_cadastrale.publication.numero }}.
{% endif %}

{% if bien.superficie_habitable %}
## Superficie habitable
La superficie habitable du bien est de **{{ bien.superficie_habitable }} m²**.
{% endif %}

Tel que le **BIEN** existe, avec tous droits y attachés, sans aucune exception ni réserve.

**Déclaration désignation – environnement du bien - voisinage**

Les parties déclarent que la description du **BIEN** telle qu'elle vient d'être indiquée correspond précisément à celle actuelle.
Etant ici précisé que la désignation des lieux correspond à la déclaration faite par les parties et n'a, à aucun moment, été vérifiée par le notaire soussigné, qui ne peut être tenu responsable d'une inexactitude dans les caractéristiques et éléments déclarés.

Le **BENEFICIAIRE** déclare avoir visité les lieux préalablement aux présentes et, accepte expressément la désignation telle qu'elle figure ci-dessus.
Le **BENEFICIAIRE** déclare avoir été informé de la nécessité de s'informer préalablement à la signature des présentes sur la situation, le voisinage et l'environnement du **BIEN** et, sur toutes éventuelles modifications à venir de l'environnement du **BIEN**.

{% if bien.equipements %}
**Déclarations diverses**

Le **PROMETTANT** déclare qu'à sa connaissance le bien est équipé ou n'est pas équipé des éléments suivants :

|  |  | OUI | NON | NE SAIT PAS |
| :---: | :---- | :---: | :---: | :---: |
| **1** | Détecteur de fumée | {% if bien.equipements.detecteur_fumee %}X{% endif %} | {% if bien.equipements.detecteur_fumee == false %}X{% endif %} |  |
| **2*** | Cheminée privative à foyer ouvert | {% if bien.equipements.cheminee_foyer_ouvert %}X{% endif %} | {% if bien.equipements.cheminee_foyer_ouvert == false %}X{% endif %} |  |
| **3*** | Cheminée privative à foyer fermé / poêle | {% if bien.equipements.cheminee_foyer_ferme %}X{% endif %} | {% if bien.equipements.cheminee_foyer_ferme == false %}X{% endif %} |  |
| **4*** | Chaudière individuelle | {% if bien.equipements.chaudiere_individuelle %}X{% endif %} | {% if bien.equipements.chaudiere_individuelle == false %}X{% endif %} |  |
| **8*** | Pompe à chaleur ou Climatisation | {% if bien.equipements.pompe_chaleur or bien.equipements.climatisation %}X{% endif %} | {% if bien.equipements.pompe_chaleur == false and bien.equipements.climatisation == false %}X{% endif %} |  |
| **17** | Bien raccordé à la Fibre | {% if bien.equipements.fibre %}X{% endif %} | {% if bien.equipements.fibre == false %}X{% endif %} |  |

Le **BENEFICIAIRE,** informé de cette situation, déclare prendre le **BIEN** en l'état.
{% endif %}

{% if bien.chauffage %}
**Système de chauffage**

Le **PROMETTANT** déclare que le système de chauffage est {{ bien.chauffage.type }} {% if bien.chauffage.collectif %}collective{% else %}individuelle{% endif %} au {{ bien.chauffage.energie }}{% if bien.chauffage.entretien %} dont l'entretien est assuré par {{ bien.chauffage.entretien }}{% endif %}.
{% endif %}

# Usage du bien
Le **PROMETTANT** déclare que le **BIEN** est actuellement à usage {{ bien.usage_actuel }}.
{% if bien.droit_usage_habitation and bien.droit_usage_habitation.reserve %}
Le **PROMETTANT** se réserve le droit d'usage et d'habitation du **BIEN** sa vie durant, dans les conditions définies ci-après.
{% endif %}

# ORIGINE DE PROPRIÉTÉ
Le **PROMETTANT** déclare être propriétaire des biens et droits immobiliers objet des présentes, en vertu des titres ci-après relatés.

{% for origine in origine_propriete %}
## Concernant {% if origine.lots_concernes | length > 1 %}les lots numéros {% else %}le lot numéro {% endif %}{{ origine.lots_concernes | join(", ") }}
### Origine immédiate

Le **PROMETTANT** est devenu propriétaire {{ origine.modalite_detention | default('en pleine propriété') }} des biens ci-dessus désignés par suite de {{ origine.origine_immediate.type | lower }} qu'il en a faite :

{% if origine.origine_immediate.cedants %}
{% for cedant in origine.origine_immediate.cedants %}
**De {{ cedant.civilite }} {{ cedant.prenoms | default(cedant.prenom) }} {{ cedant.nom | upper }}**{% if cedant.profession %}, {{ cedant.profession }}{% endif %}{% if cedant.adresse %}, demeurant à {{ cedant.adresse }}{% endif %}.
{% if cedant.date_naissance %}Né(e) à {{ cedant.lieu_naissance | default('[lieu de naissance]') }} le {{ cedant.date_naissance | format_date }}.{% endif %}

{% if cedant.situation_matrimoniale %}
{% if cedant.situation_matrimoniale.statut == 'marie' %}
Marié(e) sous le régime de {{ cedant.situation_matrimoniale.regime_matrimonial | default('la communauté légale') }}.
{% elif cedant.situation_matrimoniale.statut == 'celibataire' %}
Célibataire.
{% elif cedant.situation_matrimoniale.statut == 'divorce' %}
Divorcé(e).
{% elif cedant.situation_matrimoniale.statut == 'veuf' %}
Veuf(ve).
{% endif %}
{% endif %}
{% endfor %}
{% else %}
**De {{ origine.origine_immediate.vendeur_precedent | default('[Vendeur précédent à préciser]') }}**
{% endif %}

Suivant acte {{ origine.origine_immediate.type_libelle | default('de vente') | lower }} reçu par **{{ origine.origine_immediate.notaire }}**, notaire{% if origine.origine_immediate.ville_notaire %} à {{ origine.origine_immediate.ville_notaire }}{% endif %}, le **{{ origine.origine_immediate.date | format_date }}**.

{% if origine.origine_immediate.prix %}
Le prix a été payé {{ origine.origine_immediate.modalite_paiement | default('comptant') }} et quittancé audit acte.
{% endif %}

Cet acte a été publié au **service de la publicité foncière de {{ origine.origine_immediate.publication.service }}**{% if origine.origine_immediate.publication.date %} le {{ origine.origine_immediate.publication.date | format_date }}, volume {{ origine.origine_immediate.publication.volume }}, numéro {{ origine.origine_immediate.publication.numero }}{% endif %}.

{% if origine.origines_anterieures and origine.origines_anterieures | length > 0 %}
### Origine antérieure

L'origine de propriété antérieure est ci-après relatée telle qu'elle résulte de l'acte susvisé :

{% for origine_ant in origine.origines_anterieures %}
{% if origine_ant.type == 'acquisition' %}
{{ origine_ant.beneficiaire | default('Le propriétaire précédent') }} avait acquis le bien de {{ origine_ant.cedant }} suivant acte reçu par {{ origine_ant.notaire }}, notaire{% if origine_ant.ville_notaire %} à {{ origine_ant.ville_notaire }}{% endif %}, le {{ origine_ant.date | format_date }}.
{% if origine_ant.publication %}Publié au service de la publicité foncière de {{ origine_ant.publication.service }} le {{ origine_ant.publication.date | format_date }}.{% endif %}

{% elif origine_ant.type == 'succession' %}
Le bien était échu au propriétaire précédent par suite du décès de {{ origine_ant.defunt.civilite }} {{ origine_ant.defunt.nom }}, survenu le {{ origine_ant.defunt.date_deces | format_date }}{% if origine_ant.defunt.lieu_deces %} à {{ origine_ant.defunt.lieu_deces }}{% endif %}.
{% if origine_ant.acte_notoriete %}Aux termes d'un acte de notoriété reçu par {{ origine_ant.acte_notoriete.notaire }} le {{ origine_ant.acte_notoriete.date | format_date }}.{% endif %}

{% elif origine_ant.type == 'donation' %}
Le bien avait été donné au propriétaire précédent par {{ origine_ant.donateur }} suivant acte reçu par {{ origine_ant.notaire }} le {{ origine_ant.date | format_date }}.
{% if origine_ant.publication %}Publié au service de la publicité foncière de {{ origine_ant.publication.service }} le {{ origine_ant.publication.date | format_date }}.{% endif %}

{% else %}
{{ origine_ant.description | default('Origine antérieure non détaillée') }}
{% endif %}
{% endfor %}
{% endif %}

{% endfor %}

# Effet relatif
Les titres de propriété antérieurs, les pièces d'urbanisme ou autres, ne doivent pas révéler de servitudes, de charges, ni de vices non indiqués aux présentes pouvant grever l'immeuble et en diminuer sensiblement la valeur ou le rendre impropre à la destination que le **BENEFICIAIRE** entend lui donner. Le **PROMETTANT** devra justifier d'une origine de propriété régulière remontant à un titre translatif d'au moins trente ans.

{# ============================================================================
   SECTION VIAGER : SANTÉ DU PROMETTANT
   Articles 1974 et 1975 du Code civil — Nullité si décès dans les 20 jours
   ============================================================================ #}

{% include 'sections/section_sante_promettant.md' %}

# PRIX - CONDITIONS FINANCIERES DE LA VENTE EN VIAGER

## Évaluation du bien

{% if prix.valeur_venale %}
La **valeur vénale** du bien, déterminée en pleine propriété et libre d'occupation, est fixée d'un commun accord entre les parties à la somme de **{{ prix.valeur_venale_lettres | default(prix.valeur_venale | montant_en_lettres) | upper }}** soit **{{ prix.valeur_venale | format_nombre }} {{ prix.devise | default("EUR") }}**.
{% endif %}

{% if prix.valeur_economique %}
La **valeur économique** du bien, tenant compte de l'occupation par le crédirentier (droit d'usage et d'habitation réservé), est fixée à la somme de **{{ prix.valeur_economique_lettres | default(prix.valeur_economique | montant_en_lettres) | upper }}** soit **{{ prix.valeur_economique | format_nombre }} {{ prix.devise | default("EUR") }}**.
{% endif %}

{% if prix.valeur_venale and prix.valeur_economique %}
La **différence** entre la valeur vénale et la valeur économique, soit **{{ prix.difference_lettres | default(prix.difference | montant_en_lettres) | upper }}** ({{ prix.difference | format_nombre }} {{ prix.devise | default("EUR") }}), représente la valeur du droit d'usage et d'habitation réservé par le crédirentier.
{% endif %}

## Prix de la vente en viager

La vente est consentie et acceptée moyennant un prix global correspondant à la valeur économique du bien, payable de la manière suivante :

### Le Bouquet

{% if prix.bouquet and prix.bouquet.montant %}
Le **BENEFICIAIRE** (débirentier) versera au **PROMETTANT** (crédirentier), le jour de la constatation authentique de la réalisation de la promesse, un capital dit **« BOUQUET »** d'un montant de **{{ prix.bouquet.montant_lettres | default(prix.bouquet.montant | montant_en_lettres) | upper }}** soit **{{ prix.bouquet.montant | format_nombre }} {{ prix.devise | default("EUR") }}**.

Ce bouquet sera payable **comptant** le jour de la signature de l'acte authentique de vente, par virement bancaire sur le compte du notaire chargé de recevoir ledit acte.
{% else %}
La vente est consentie **sans bouquet**. Le prix sera exclusivement constitué de la rente viagère ci-après définie.
{% endif %}

### La Rente Viagère

{% if prix.rente_viagere and prix.rente_viagere.montant_mensuel %}
Le **BENEFICIAIRE** (débirentier) versera en outre au **PROMETTANT** (crédirentier) une **rente viagère** d'un montant de **{{ prix.rente_viagere.montant_mensuel_lettres | default(prix.rente_viagere.montant_mensuel | montant_en_lettres) | upper }}** soit **{{ prix.rente_viagere.montant_mensuel | format_nombre }} {{ prix.devise | default("EUR") }}** par mois.

Cette rente sera due et payable **{{ prix.rente_viagere.periodicite | default("mensuellement") }}**, le **{{ prix.rente_viagere.jour_versement | default(5) }}** de chaque mois, par virement bancaire permanent sur le compte du crédirentier.
{% if prix.rente_viagere.date_debut %}
La rente prendra effet le **{{ prix.rente_viagere.date_debut | format_date }}**.
{% else %}
La rente prendra effet à compter du jour de la signature de l'acte authentique.
{% endif %}

La rente est constituée sur la **tête du crédirentier** et s'éteindra à son décès, quelle que soit la date de celui-ci.

**Il est rappelé que, conformément à l'article 1978 du Code civil, le débirentier ne peut se libérer du paiement de la rente en offrant de rembourser le capital et en renonçant à la restitution des arrérages payés ; il est tenu de servir la rente pendant toute la vie du crédirentier.**
{% endif %}

### Récapitulatif du prix

| Composante | Montant |
| :---- | ----: |
{% if prix.bouquet and prix.bouquet.montant %}
| Bouquet (capital comptant) | {{ prix.bouquet.montant | format_nombre }} EUR |
{% endif %}
{% if prix.rente_viagere and prix.rente_viagere.montant_mensuel %}
| Rente viagère (mensuelle) | {{ prix.rente_viagere.montant_mensuel | format_nombre }} EUR/mois |
{% endif %}
{% if prix.valeur_venale %}
| Valeur vénale (pleine propriété) | {{ prix.valeur_venale | format_nombre }} EUR |
{% endif %}
{% if prix.valeur_economique %}
| Valeur économique (occupé) | {{ prix.valeur_economique | format_nombre }} EUR |
{% endif %}

# Frais
Les frais, droits et émoluments de la vente seront à la charge du **BENEFICIAIRE** (débirentier).

{% if negociation and negociation.existe %}
# Négociation
Les parties reconnaissent que le prix a été négocié par **{{ negociation.agent.nom }}** titulaire d'un mandat donné par **{{ negociation.agent.mandant }}** sous le numéro {{ negociation.agent.mandat_numero }} en date du {{ negociation.agent.mandat_date }} non encore expiré, ainsi déclaré.
En conséquence, **{{ negociation.a_charge_de }}** qui en a seul la charge aux termes du mandat, doit à l'agence une rémunération de **{{ negociation.honoraires | format_nombre }} EUR**, taxe sur la valeur ajoutée incluse.
Cette rémunération sera payée le jour de la constatation authentique de la réalisation des présentes.

{% if negociation.inclus_dans_prix %}
Etant ici précisé que le montant de la négociation est compris dans le bouquet indiqué ci-dessus.
{% endif %}
{% endif %}

{# ============================================================================
   SECTION VIAGER : DROIT D'USAGE ET D'HABITATION
   Réserve DUH, obligations crédirentier/débirentier, abandon
   ============================================================================ #}

{% if bien.droit_usage_habitation and bien.droit_usage_habitation.reserve %}
{% include 'sections/section_droit_usage_habitation.md' %}
{% endif %}

{# ============================================================================
   SECTION VIAGER : RENTE VIAGÈRE
   Conventions, indexation, rachat, aliénation
   ============================================================================ #}

{% if prix.rente_viagere %}
{% include 'sections/section_rente_viagere.md' %}
{% endif %}

{# ============================================================================
   SECTION VIAGER : GARANTIES
   Privilège du vendeur, clause pénale, clause résolutoire
   ============================================================================ #}

{% include 'sections/section_garanties_viager.md' %}

# Caractéristiques
Les parties conviennent entre elles d'établir les présentes sous la forme d'une promesse unilatérale dans les termes du second alinéa de l'article 1106 du Code civil. Dans la commune intention des parties, et pendant toute la durée du contrat, celle-ci obéira aux dispositions qui suivent.

# Information préalable
Les parties ont été informées par le rédacteur des présentes que la forme sous signature privée ne leur permet pas de faire publier un acte au service de la publicité foncière.
En conséquence, et dans cette hypothèse, si l'une d'entre elles refusait ou devenait incapable de réaliser ou de réitérer la convention par acte authentique, l'autre partie ne pourrait pas faire inscrire les présentes directement au fichier immobilier afin de conserver son droit et de le rendre opposable aux tiers, préalablement à toute décision de justice.
Les parties ainsi averties de cette situation déclarent vouloir opter expressément pour la conclusion entre elles d'un acte authentique.

# Délai
La promesse de vente est consentie pour une durée expirant :

---

le **{{ delais.expiration_promesse.date | format_date }}**, à {{ delais.expiration_promesse.heure }}.
---

En cas de carence du **PROMETTANT** pour la réalisation de la vente, ce dernier ne saurait se prévaloir à l'encontre du **BENEFICIAIRE** de l'expiration du délai ci-dessus fixé.

**Information des parties sur le rendez-vous de signature**

Les parties sont informées que la date mentionnée ci-dessus ne constitue pas la date précise du rendez-vous de signature de l'acte de vente. Il leur appartiendra de se rapprocher préalablement de leur notaire afin de fixer une date de signature.

# RÉALISATION
La réalisation de la promesse aura lieu par la signature de l'acte authentique constatant le caractère définitif de la vente, accompagnée :
* du versement du **bouquet** par virement sur le compte du notaire chargé de recevoir l'acte authentique,
* de la mise en place du **virement permanent** pour le service de la rente viagère,
* du versement de la provision sur frais d'acte de vente,
* et de manière générale de tous comptes et proratas.

# Rédacteur de l'acte authentique de vente
L'acte authentique constatant la réalisation de la vente sera reçu par {{ acte.notaire.civilite }} {{ acte.notaire.prenom }} {{ acte.notaire.nom }}, notaire soussigné{% if acte.notaire_beneficiaire %} avec la participation de {{ acte.notaire_beneficiaire.civilite }} {{ acte.notaire_beneficiaire.prenom }} {{ acte.notaire_beneficiaire.nom }}, notaire à {{ acte.notaire_beneficiaire.ville }}{% endif %}.
En toute hypothèse, le transfert de propriété est reporté au jour de la constatation de la vente en la forme authentique et du paiement du bouquet tel que convenu et des frais, même si l'échange de consentement nécessaire à la formation de la convention est antérieur.

# CARENCE
La carence s'entend ici du manquement fautif par l'une des parties, du fait de sa volonté ou de sa négligence, à une ou plusieurs de ses obligations aux présentes, ce manquement empêchant l'exécution de la vente.

**En l'absence de levée d'option ou de signature de l'acte de vente dans le délai**
Au cas où le **BENEFICIAIRE** n'aurait ni levé l'option ni signé l'acte de vente à l'intérieur du délai de réalisation, il sera de plein droit déchu du bénéfice de la promesse au terme dudit délai de réalisation sans qu'il soit besoin d'une mise en demeure de la part du **PROMETTANT**, qui disposera alors librement du **BIEN**.

# Force exécutoire de la promesse
Il est entendu entre les parties qu'en raison de l'acceptation par le **BENEFICIAIRE** de la promesse faite par le **PROMETTANT**, en tant que simple promesse, il s'est formé entre elles un contrat dans les termes de l'article 1124 du Code civil. En conséquence, et pendant toute la durée du contrat, celui-ci ne pourra être révoqué que par leur consentement mutuel.

* Le **PROMETTANT** a, pour sa part, définitivement consenti à la vente et qu'il est d'ores et déjà débiteur de l'obligation de transférer la propriété au profit du **BENEFICIAIRE** aux conditions des présentes. Le **PROMETTANT** ne peut plus, par suite, pendant toute la durée de la présente promesse, conférer une autre promesse à un tiers ni aucun droit réel ni charge quelconque sur le **BIEN**, consentir aucun bail, location ou prorogation de bail.
* Par le présent contrat de promesse, les parties conviennent que la formation du contrat de vente est exclusivement subordonnée au consentement du **BENEFICIAIRE**, indépendamment du comportement du **PROMETTANT**.
* Toute révocation ou rétractation unilatérale de la volonté du **PROMETTANT** sera de plein droit dépourvue de tout effet sur le contrat promis du fait de l'acceptation de la présente promesse en tant que telle par le **BENEFICIAIRE**.

# Propriété jouissance
Le **BENEFICIAIRE** sera propriétaire des **BIENS** objet de la promesse le jour de la constatation de la vente en la forme authentique.
{% if bien.droit_usage_habitation and bien.droit_usage_habitation.reserve %}
Le **PROMETTANT** conservera le droit d'usage et d'habitation du **BIEN** sa vie durant, conformément aux stipulations ci-dessus.
La jouissance du **BIEN** au profit du **BENEFICIAIRE** ne prendra effet qu'au décès du crédirentier ou à l'abandon du droit d'usage et d'habitation, dans les conditions définies aux présentes.
{% else %}
Le **BENEFICIAIRE** en aura la jouissance à compter du même jour par la prise de possession réelle, les **BIENS** devant être impérativement, à cette même date, libres de toute location ou occupation.
{% endif %}

# Réserves et conditions suspensives
Les effets des présentes sont soumis à la levée des réserves et à l'accomplissement des conditions suspensives suivantes.

## Réserves
### Réserve du droit de préemption
La promesse sera notifiée à tous les titulaires d'un droit de préemption institué en vertu de l'article L211-1 du Code de l'urbanisme ou de tout autre Code.
L'exercice de ce droit par son titulaire obligera le **PROMETTANT** aux mêmes charges et conditions convenues aux présentes.

## Conditions suspensives
Les présentes sont soumises à l'accomplissement de conditions suspensives indiquées ci-après.
Conformément aux dispositions de l'article 1304-6 du Code civil, à partir de cet accomplissement les obligations contractées produisent leurs effets.
La non réalisation d'une seule de ces conditions, pouvant être invoquée par les deux parties, entraîne la caducité des présentes, qui sont alors réputées n'avoir jamais existé.

### Conditions suspensives de droit commun
Les présentes sont soumises à l'accomplissement des conditions suspensives de droit commun stipulées en la faveur du **BENEFICIAIRE**, qui sera seul à pouvoir s'en prévaloir.
Les titres de propriété antérieurs, les pièces d'urbanisme ou autres, ne doivent pas révéler de servitudes, de charges, ni de vices non indiqués aux présentes pouvant grever l'immeuble et en diminuer sensiblement la valeur ou le rendre impropre à la destination que le **BENEFICIAIRE** entend donner.
L'état hypothécaire ne doit pas révéler de saisies ou d'inscriptions dont le solde des créances inscrites augmenté du coût des radiations à effectuer serait supérieur au prix disponible.

{% if condition_suspensive_pret and condition_suspensive_pret.existe %}
### Condition suspensive d'obtention de prêt
Le **BENEFICIAIRE** déclare avoir l'intention de recourir pour le paiement du bouquet, à un ou plusieurs prêts rentrant dans le champ d'application de l'article L 313-40 du Code de la consommation, et répondant aux caractéristiques suivantes :

Montant maximal de la somme empruntée : **{{ condition_suspensive_pret.montant_maximal | format_nombre }} euros**
Durée maximale de remboursement : **{{ condition_suspensive_pret.duree_maximale_annees }} ans.**
Taux nominal d'intérêt maximal : **{{ condition_suspensive_pret.taux_maximal }} % l'an (hors assurances)**

La condition suspensive sera réalisée en cas d'obtention par le **BENEFICIAIRE** d'une ou plusieurs offres écrites de prêt aux conditions sus-indiquées **au plus tard le {{ condition_suspensive_pret.date_limite | format_date }}**.
{% endif %}

### Condition suspensive relative à l'état de santé du crédirentier
Conformément à l'article 1975 du Code civil, la présente promesse est soumise à la condition suspensive que le crédirentier soit en vie au jour de la réitération par acte authentique et qu'il ne soit pas décédé dans les vingt jours de la signature des présentes d'une maladie dont il était atteint au jour de ladite signature.

# FISCALITE
## Régime fiscal de la vente
Le **PROMETTANT** et le **BENEFICIAIRE** indiquent ne pas agir aux présentes en qualité d'assujettis en tant que tels à la taxe sur la valeur ajoutée au sens de l'article 256 du Code général des impôts.

Les présentes seront soumises au tarif de droit commun en matière immobilière tel que prévu par l'article 1594D du Code général des impôts.

## Fiscalité de la rente viagère
Les parties sont informées que la rente viagère est soumise à l'impôt sur le revenu dans la catégorie des rentes viagères à titre onéreux, selon la fraction imposable déterminée en fonction de l'âge du crédirentier au moment de l'entrée en jouissance de la rente :
* Moins de 50 ans : 70% de la rente est imposable.
* De 50 à 59 ans : 50% de la rente est imposable.
* De 60 à 69 ans : 40% de la rente est imposable.
* 70 ans et plus : 30% de la rente est imposable.

{% if fiscalite and fiscalite.plus_value and fiscalite.plus_value.exoneration %}
Le **PROMETTANT** déclare que les présentes portent sur sa résidence principale.
Par suite, il bénéficiera de l'exonération de l'impôt sur les plus-values conformément aux dispositions de l'article 150 U II 1° du Code général des impôts.
{% endif %}

# ABSENCE DE FACULTE DE SUBSTITUTION
{% if faculte_substitution %}
Le **BENEFICIAIRE** pourra substituer toute personne physique ou morale dans le bénéfice de la présente promesse, sous réserve de l'accord du crédirentier.
{% else %}
Le **BENEFICIAIRE** ne pourra substituer aucune personne physique ou morale dans le bénéfice de la présente promesse.
{% endif %}

# Dispositions transitoires
## Obligation de garde du promettant
{% if bien.droit_usage_habitation and bien.droit_usage_habitation.reserve %}
Le **PROMETTANT**, bénéficiant du droit d'usage et d'habitation, conservera la jouissance et la garde du **BIEN** sa vie durant.
{% else %}
Entre la date des présentes et la date d'entrée en jouissance du **BENEFICIAIRE**, le **BIEN** demeurera sous la garde et possession du **PROMETTANT** qui s'y oblige.
{% endif %}

## Sinistre pendant la durée de validité de la promesse
Si un sinistre quelconque frappait le **BIEN** durant la durée de validité des présentes, les parties conviennent que le **BENEFICIAIRE** aura la faculté :

* Soit de renoncer purement et simplement à la vente et de se voir immédiatement remboursé de toute somme avancée par lui le cas échéant.
* Soit de maintenir l'acquisition du **BIEN** alors sinistré et de se voir attribuer les indemnités susceptibles d'être versées par la ou les compagnies d'assurances concernées.

# Condition de survie du crédirentier
La présente promesse de vente est consentie sous la condition suspensive implicite de la survie du crédirentier. En cas de décès du crédirentier avant la réitération de la vente par acte authentique, la présente promesse deviendra **caduque de plein droit**, conformément à l'article 1975 du Code civil.

# Conventions particulières – Visites – Information des parties
{% if conventions_particulieres %}
{% for convention in conventions_particulieres %}
## {{ convention.titre }}

{{ convention.texte }}

{% endfor %}
{% endif %}

## Visites préalables
Le **BENEFICIAIRE** déclare avoir visité le **BIEN** préalablement à la signature des présentes et l'avoir trouvé conforme à ses attentes.

Le **BENEFICIAIRE** reconnaît avoir été parfaitement informé de l'état du **BIEN**, de ses équipements, de son environnement et de la conformité des installations aux normes en vigueur, dans la limite des informations détenues par le **PROMETTANT** et des diagnostics réalisés.

# Paiement sur état - publicité foncière - information
L'acte est soumis au droit d'enregistrement sur état de CENT VINGT-CINQ EUROS (125,00 EUR).
Le **BENEFICIAIRE** dispense le notaire soussigné de faire publier l'acte au service de la publicité foncière{% if not publication or not publication.demandee %}, se contentant de requérir ultérieurement à cette publication, s'il le juge utile, à ses frais{% endif %}.

# POUVOIRS
Les parties confèrent à tout clerc ou collaborateur de l'office notarial dénommé en tête des présentes tous pouvoirs nécessaires à l'effet :

* de signer toutes demandes de pièces, demandes de renseignements, et lettres de purge de droit de préemption préalables à la vente ;
* de dresser et signer tous actes qui se révéleraient nécessaires en vue de l'accomplissement des formalités de publicité foncière.

# ELECTION DE DOMICILE
Pour l'exécution des présentes, les parties font élection de domicile en leur demeure ou siège social respectif.
En outre, et à défaut d'accord amiable entre les parties, toutes les contestations qui pourront résulter des présentes seront soumises au tribunal judiciaire de la situation du **BIEN**.

# FACULTE DE RETRACTATION
En vertu des dispositions de l'article L 271-1 du Code de la construction et de l'habitation, le **BIEN** étant à usage d'habitation et le **BENEFICIAIRE** étant un non-professionnel de l'immobilier, ce dernier bénéficie de la faculté de se rétracter.
A cet effet, une copie du présent acte avec ses annexes lui sera notifiée par lettre recommandée avec accusé de réception. Dans un délai de dix jours à compter du lendemain de la première présentation de la lettre de notification, le **BENEFICIAIRE** pourra exercer la faculté de rétractation, et ce par lettre recommandée avec accusé de réception ou exploit extrajudiciaire, à son choix exclusif.

Il est ici précisé au **BENEFICIAIRE** que :

* Dans l'hypothèse où il exercerait cette faculté de rétractation, celle-ci serait considérée comme définitive.
* Le délai de dix jours se compte de la manière suivante :
* Le premier jour commence le lendemain de la première présentation du courrier recommandé.
* Le dernier jour est le dixième jour suivant.
* En vertu de l'article 642 du Code de procédure civile, le délai expirant un samedi, un dimanche, un jour férié ou chômé, est prorogé jusqu'au premier jour ouvrable suivant.

# COMMUNICATION DES PIECES ET DOCUMENTS
Le **BENEFICIAIRE** pourra prendre connaissance de toutes les pièces et documents ci-dessus mentionnés dans le délai de rétractation auprès du notaire rédacteur des présentes.

# Médiation
Les parties sont informées qu'en cas de litige entre elles ou avec un tiers, elles pourront, préalablement à toute instance judiciaire, le soumettre à un médiateur qui sera désigné et missionné par le Centre de médiation notariale.

# Affirmation de sincérité
Les parties affirment, sous les peines édictées par l'article 1837 du Code général des impôts, que le présent acte exprime l'intégralité du prix ; elles reconnaissent avoir été informées par le rédacteur des présentes des sanctions fiscales et des peines correctionnelles encourues en cas d'inexactitude de cette affirmation.

# Mention sur la protection des données personnelles
L'Office notarial traite des données personnelles concernant les personnes mentionnées aux présentes, pour l'accomplissement des activités notariales, notamment de formalités d'actes.

# Certification d'identité
Le notaire soussigné certifie que l'identité complète des parties dénommées dans le présent document telle qu'elle est indiquée en tête des présentes à la suite de leur nom ou dénomination lui a été régulièrement justifiée.

# LISTE DES ANNEXES
Les annexes suivantes font partie intégrante de la présente promesse de vente en viager :

| N° | Désignation | Obligatoire | Observations |
| :---: | :---- | :---: | :---- |
| 1 | Plans cadastral et géoportail | Oui | Identification du bien |
{% if bien.superficie_habitable -%}
| 2 | Attestation de superficie habitable | Oui | Surface habitable |
{% endif -%}
{% if diagnostics and diagnostics.dpe -%}
| 3 | Diagnostic de performance énergétique (DPE) | Oui | Classe {{ diagnostics.dpe.classe_energie | default('NC') }} |
{% endif -%}
{% if diagnostics and (diagnostics.erp or diagnostics.etat_risques) -%}
| 4 | État des risques et pollutions (ERP) | Oui | Article L. 125-5 Code environnement |
{% endif -%}
{% if diagnostics and diagnostics.plomb -%}
| 5 | Constat de risque d'exposition au plomb (CREP) | {% if diagnostics.plomb.requis %}Oui{% else %}Non{% endif %} | Immeuble construit avant 1949 |
{% endif -%}
{% if diagnostics and diagnostics.amiante_parties_privatives -%}
| 6 | Diagnostic amiante | {% if diagnostics.amiante_parties_privatives.requis %}Oui{% else %}Non{% endif %} | Permis de construire avant 01/07/1997 |
{% endif -%}
{% if diagnostics and diagnostics.termites -%}
| 7 | État relatif aux termites | {% if diagnostics.termites.requis %}Oui{% else %}Non{% endif %} | Zone de protection |
{% endif -%}
{% if diagnostics and diagnostics.gaz -%}
| 8 | État installation intérieure de gaz | {% if diagnostics.gaz.requis %}Oui{% else %}Non{% endif %} | Installation > 15 ans |
{% endif -%}
{% if diagnostics and diagnostics.electricite -%}
| 9 | État installation intérieure d'électricité | {% if diagnostics.electricite.requis %}Oui{% else %}Non{% endif %} | Installation > 15 ans |
{% endif -%}
{% if diagnostics and diagnostics.assainissement -%}
| 10 | Diagnostic assainissement | {% if diagnostics.assainissement.requis %}Oui{% else %}Non{% endif %} | Assainissement non collectif |
{% endif -%}
| 11 | Certificat médical du crédirentier | Recommandé | Article 1975 Code civil |
| 12 | Note d'urbanisme | Oui | Situation du bien |
| 13 | Note de voirie | Oui | Desserte et accès |
| 14 | Barème viager (table de mortalité) | Oui | Calcul rente |

{% if annexes_supplementaires %}
**Annexes complémentaires :**
{% for annexe in annexes_supplementaires %}
| {{ annexe.numero }} | {{ annexe.designation }} | {{ "Oui" if annexe.obligatoire else "Non" }} | {{ annexe.observations | default('') }} |
{% endfor %}
{% endif %}

Le **BENEFICIAIRE** reconnaît avoir reçu l'ensemble des documents et annexes ci-dessus listés préalablement à la signature des présentes.

# Formalisme lié aux annexes
Les annexes, s'il en existe, font partie intégrante de la minute.
Si l'acte est établi sur support électronique, la signature du notaire en fin d'acte vaut également pour ses annexes.

**DONT ACTE sans renvoi**
Généré en l'office notarial et visualisé sur support électronique aux lieu, jour, mois et an indiqués en en-tête du présent acte.
Et lecture faite, les parties ont certifié exactes les déclarations les concernant, avant d'apposer leur signature manuscrite sur tablette numérique.

Le notaire, qui a recueilli l'image de leur signature, a lui-même apposé sa signature manuscrite, puis signé l'acte au moyen d'un procédé de signature électronique qualifié.
