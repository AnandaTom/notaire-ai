{{ acte.numero_repertoire }}
{{ acte.reference_interne }}

**Le {{ acte.date.jour }} {{ acte.date.mois | mois_en_lettres }} {{ acte.date.annee }}**
**PROMESSE UNILATERALE DE VENTE**
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

**A RECU le présent acte contenant PROMESSE DE VENTE à la requête de :**

# **PROMETTANT**

{% for promettant in promettants %}
{{ promettant.civilite }} {{ promettant.prenoms }} {{ promettant.nom }}, {{ promettant.profession }}, demeurant à {{ promettant.adresse }}, {{ promettant.code_postal }} {{ promettant.ville }}.
{% if promettant.civilite == "Madame" %}Née{% else %}Né{% endif %} à {{ promettant.lieu_naissance }} le {{ promettant.date_naissance | format_date }}.
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
**Coordonnées :**
{{ promettant.civilite }} {{ promettant.nom }}
{% if promettant.coordonnees.telephone %}Téléphone mobile : {{ promettant.coordonnees.telephone }}{% endif %}
{% if promettant.coordonnees.courriel %}Courriel : {{ promettant.coordonnees.courriel }}{% endif %}
{% endif %}

{% endfor %}

# **BENEFICIAIRE**

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
**Coordonnées :**
{{ beneficiaire.civilite }} {{ beneficiaire.nom }}
{% if beneficiaire.coordonnees.telephone %}Téléphone mobile : {{ beneficiaire.coordonnees.telephone }}{% endif %}
{% if beneficiaire.coordonnees.courriel %}Courriel : {{ beneficiaire.coordonnees.courriel }}{% endif %}
{% endif %}

{% endfor %}

# **Quotités acquises**

{% if quotites_a_determiner %}
{% for beneficiaire in beneficiaires %}{{ beneficiaire.civilite }} {{ beneficiaire.nom }}{% if not loop.last %} et {% endif %}{% endfor %} feront l'acquisition de la pleine propriété indivise du **BIEN** dans des quotités à déterminer au plus tard lors de la réitération des présentes.
{% else %}
{% for quotite in quotites_beneficiaires %}
{{ beneficiaires[quotite.personne_index].civilite }} {{ beneficiaires[quotite.personne_index].nom }} acquerra {{ quotite.quotite }} en {{ quotite.type_propriete | replace("_", " ") }}.
{% endfor %}
{% endif %}

# **Déclarations des parties sur leur capacité**

Les parties, et le cas échéant leurs représentants, attestent que rien ne peut limiter leur capacité pour l'exécution des engagements qu'elles prennent aux présentes, et elles déclarent notamment :

* que leur état civil et leurs qualités indiqués en tête des présentes sont exacts,
* qu'elles ne sont pas en état de cessation de paiement, de rétablissement professionnel, de redressement ou liquidation judiciaire ou sous procédure de sauvegarde des entreprises,
* qu'elles n'ont pas été associées dans une société mise en liquidation judiciaire suivant jugement publié depuis moins de cinq ans et dans laquelle elles étaient tenues indéfiniment et solidairement ou seulement conjointement du passif social, le délai de cinq ans marquant la prescription des actions de droit commun et de celle en recouvrement à l'endroit des associés (BOI-REC-SOLID-20-10-20),
* qu'il n'a été formé aucune opposition au présent acte par un éventuel cogérant,
* qu'elles ne sont concernées :
* par aucune des mesures légales relatives aux personnes protégées qui ne seraient pas révélées aux présentes,
* par aucune des dispositions du Code de la consommation sur le règlement des situations de surendettement, sauf là aussi ce qui peut être spécifié aux présentes,
* et pour le **BENEFICIAIRE** spécialement qu'il n'est, ni à titre personnel, ni en tant qu'associé ou mandataire social, soumis à l'interdiction d'acquérir prévue par l'article 225-26 du Code pénal.

# **Documents relatifs à la capacité et à la qualité des parties**

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

# **Présence - représentation**

{% for promettant in promettants %}
- {{ promettant.civilite }} {{ promettant.nom }} est {% if promettant.civilite == "Madame" %}présente{% else %}présent{% endif %} à l'acte.
{% endfor %}
{% for beneficiaire in beneficiaires %}
- {{ beneficiaire.civilite }} {{ beneficiaire.nom }} est {% if beneficiaire.civilite == "Madame" %}présente{% else %}présent{% endif %} à l'acte.
{% endfor %}

# **CONCLUSION DU CONTRAT**

Les parties déclarent que les dispositions de ce contrat ont été, en respect des règles impératives de l'article 1104 du Code civil, négociées de bonne foi. Elles affirment qu'il reflète l'équilibre voulu par chacune d'elles.

# **DEVOIR D'INFORMATION RECIPROQUE**

En application de l'article 1112-1 du Code civil qui impose aux parties un devoir précontractuel d'information, qui ne saurait toutefois porter sur le prix, le **PROMETTANT** déclare avoir porté à la connaissance du **BENEFICIAIRE** l'ensemble des informations dont il dispose ayant un lien direct et nécessaire avec le contenu du présent contrat et dont l'importance pourrait être déterminante de son consentement.
Ce devoir s'applique à toute information sur les caractéristiques juridiques, matérielles et environnementales relatives au bien, ainsi qu'à son usage, dont il a personnellement connaissance par lui-même et par des tiers, sans que ces informations puissent être limitées dans le temps.
Le **PROMETTANT** reconnaît être informé qu'un manquement à ce devoir serait sanctionné par la mise en œuvre de sa responsabilité, avec possibilité d'annulation du contrat s'il a vicié le consentement du **BENEFICIAIRE**.
Pareillement, le **BENEFICIAIRE** déclare avoir rempli les mêmes engagements, tout manquement pouvant être sanctionné comme indiqué ci-dessus.
Le devoir d'information est donc réciproque.
En outre, conformément aux dispositions de l'article 1602 du Code civil, le **PROMETTANT** est tenu d'expliquer clairement ce à quoi il s'oblige, tout pacte obscur ou ambigu s'interprétant contre lui.
Les **PARTIES** attestent que les informations déterminantes connues d'elles, données et reçues, sont rapportées aux présentes.

# **OBJET DU CONTRAT** **PROMESSE UNILATERALE DE VENTE**

Le **PROMETTANT** confère au **BENEFICIAIRE** la faculté d'acquérir, les **BIENS** ci-dessous identifiés.
Le **PROMETTANT** prend cet engagement pour lui-même ou ses ayants droit même protégés.
Le **BENEFICIAIRE** accepte la présente promesse de vente en tant que promesse, mais se réserve la faculté d'en demander ou non la réalisation.

# **TERMINOLOGIE**

Pour la compréhension de certains termes aux présentes, il est préalablement expliqué ce qui suit :
**-** Le **"PROMETTANT"** et le **"BENEFICIAIRE"** désigneront respectivement le ou les promettants et le ou les bénéficiaires, qui, en cas de pluralité, contracteront les obligations respectivement mises à leur charge solidairement entre eux, sans que cette solidarité soit rappelée chaque fois,
**-** Les **"BIENS"** désigneront les biens et droits immobiliers objet de la présente promesse de vente, l'**"ENSEMBLE IMMOBILIER"** désignera l'immeuble dans lequel se trouvent les **"BIENS"**.
**-** Les **"MEUBLES"** désigneront les meubles et objets mobiliers, s'il en existe.

# **Identification du bien**

## **Désignation**

**Dans un ensemble immobilier soumis au régime de la copropriété situé à {{ bien.adresse.ville }} ({{ bien.adresse.departement }}) {{ bien.adresse.code_postal }} {{ bien.adresse.numero }} {{ bien.adresse.voie }}.**

{{ bien.description_ensemble }}

Figurant ainsi au cadastre :

| Section | N° | Lieudit | Surface |
| :---- | :---- | :---- | :---- |
{% for parcelle in bien.cadastre %}
| {{ parcelle.section }} | {{ parcelle.numero }} | {{ parcelle.lieudit }} | {{ parcelle.surface }} |
{% endfor %}

Un extrait de plan cadastral est annexé.
Un extrait de plan Géoportail avec vue aérienne est annexé.

**Annexe n°1 : Plans cadastral et géoportail**

{% if bien.division_cadastrale %}
**Rappel de division cadastrale**

La parcelle, sise sur la commune de {{ bien.adresse.ville }} ({{ bien.adresse.code_postal }}), originairement cadastrée {{ bien.division_cadastrale.parcelle_origine }} a fait l'objet d'une division en plusieurs parcelles de moindre importance.
De cette division sont issues les parcelles cadastrées {{ bien.division_cadastrale.parcelles_issues | join(", ") }}.
Le document modificatif du parcellaire cadastral, créant cette division, a fait l'objet d'une publication au service de la publicité foncière de {{ bien.division_cadastrale.publication.service }}, le {{ bien.division_cadastrale.publication.date }}, volume {{ bien.division_cadastrale.publication.volume }}, numéro {{ bien.division_cadastrale.publication.numero }}.
{% endif %}

### **Les lots de copropriété suivants :**

{% for lot in bien.lots %}
**Lot numéro {{ lot.numero_lettres | default(lot.numero | nombre_en_lettres) }} ({{ lot.numero }})**
{% if lot.type == "appartement" %}
Soit, un appartement de type "{{ lot.type_appartement }}", situé au {{ lot.etage }}, escalier {{ lot.escalier }}{% if lot.orientation %}, {{ lot.orientation }}{% endif %}, comprenant: {{ lot.description }}.
{% elif lot.type == "cave" %}
Soit une cave, située au {{ lot.etage }}, escalier {{ lot.escalier }}, portant le numéro {{ lot.numero_cave }}.
{% elif lot.type == "parking" %}
Un emplacement de parking privé portant le numéro {{ lot.numero_parking }} au plan de masse.
{% else %}
{{ lot.description }}
{% endif %}
Et les {{ lot.tantiemes.valeur | nombre_en_lettres }} {{ lot.tantiemes.base_unite }} ({{ lot.tantiemes.valeur }} /{{ lot.tantiemes.base }} {{ lot.tantiemes.base_unite }}) des {{ lot.tantiemes.type }}.

{% endfor %}

Tel que le **BIEN** existe, avec tous droits y attachés, sans aucune exception ni réserve.

### **Plans des lots**

Demeurent annexées aux présentes :
- Une copie du plan de l'étage courant ;
{% for lot in bien.lots %}
{% if lot.type == "parking" %}
- Une copie du plan de masse faisant apparaître le lot de stationnement, numéro {{ lot.numero_lettres | default(lot.numero | nombre_en_lettres) | upper }} ({{ lot.numero }}) ;{% if bien.lots_irregularites and bien.lots_irregularites.parking %} Etant ici précisé que l'emplacement de stationnement numéroté « {{ bien.lots_irregularites.parking.numero_officiel }} » n'est pas celui utilisé par le **PROMETTANT**. **Les parties déclarent que l'emplacement de stationnement utilisé est le numéro « {{ bien.lots_irregularites.parking.numero_utilise }} » au plan de masse.**{% endif %}
{% elif lot.type == "cave" %}
- Une copie du plan des sous-sol, faisant apparaître l'emplacement du lot de cave numéro {{ lot.numero_lettres | default(lot.numero | nombre_en_lettres) | upper }} ({{ lot.numero }}).{% if bien.lots_irregularites and bien.lots_irregularites.cave %} Etant ici précisé que la cave numérotée « {{ bien.lots_irregularites.cave.numero_officiel }} » n'est pas celle utilisée par le **PROMETTANT**. **Les parties déclarent que la cave utilisée est le numéro « {{ bien.lots_irregularites.cave.numero_utilise }} » au plan demeuré annexé.**{% endif %}
{% endif %}
{% endfor %}

**Annexe n°2 : Plans des lots et plan de masse**

## **Mention de la superficie de la partie privative – Application**

La superficie de la partie privative des lots de copropriété soumis aux dispositions de l'article 46 de la loi du 10 juillet 1965, est de **{{ bien.superficie_carrez.superficie_m2 }} m².**

Ainsi qu'il résulte d'une attestation établie le {{ bien.superficie_carrez.date_mesurage | format_date }} par le cabinet {{ bien.superficie_carrez.diagnostiqueur }}, demeurant annexée aux présentes.

Les parties ont été informées de la possibilité pour le **BENEFICIAIRE** d'agir en révision du prix, si la superficie réelle est inférieure de plus d'un vingtième à celle exprimée aux présentes.
La révision du prix consistera en une diminution de la valeur du lot concerné proportionnelle à la moindre mesure.
L'action en diminution, si elle est recevable, devra être intentée par le **BENEFICIAIRE** dans un délai d'un an à compter de la date de l'acte authentique constatant la réalisation des présentes, et ce à peine de déchéance.
Ces dispositions ne sont pas applicables aux caves, garages, emplacements de stationnement ni aux lots ou fractions de lots d'une superficie inférieure à 8 mètres carrés.

**Annexe n°3 : Diagnostic carrez**

## **État descriptif de division – Règlement de copropriété**

L'ensemble immobilier sus-désigné a fait l'objet d'un état descriptif de division et règlement de copropriété établi aux termes d'un acte reçu par {{ copropriete.reglement.notaire_origine }} le {{ copropriete.reglement.date_origine }} publié au service de la publicité foncière de {{ copropriete.reglement.publication }}.

{% for modificatif in copropriete.reglement.modificatifs %}
L'état descriptif de division - règlement de copropriété a été modifié aux termes d'un acte reçu par {{ modificatif.notaire }} le {{ modificatif.date }}, publié au service de la publicité foncière de {{ modificatif.publication }}.
{% endfor %}

<!-- SECTION: meubles | CONDITIONNEL: meubles.inclus -->
{% if meubles and meubles.inclus %}
# **MEUBLES ET OBJETS MOBILIERS**

Les parties déclarent que la promesse comprendra le mobilier suivant{% if not meubles.valeur %} non valorisé{% endif %} :

{% for meuble in meubles.liste %}
- {{ meuble }}
{% endfor %}
{% if meubles.valeur %}

La valeur de ces meubles est fixée à {{ meubles.valeur | montant_en_lettres }} ({{ meubles.valeur | format_nombre }} EUR).
{% endif %}
{% else %}
# **ABSENCE DE MEUBLES ET OBJETS MOBILIERS**

Les parties déclarent qu'aucun meuble ou objet mobilier n'est inclus dans la présente promesse.
{% endif %}

**Déclaration désignation – environnement du bien - voisinage**

Les parties déclarent que la description du **BIEN** telle qu'elle vient d'être indiquée correspond précisément à celle actuelle.
Etant ici précisé que la désignation des lieux correspond à la déclaration faite par les parties et n'a, à aucun moment, été vérifiée par la notaire soussigné, qui ne peut être tenu responsable d'une inexactitude dans les caractéristiques et éléments déclarés.

Le **BENEFICIAIRE** déclare avoir visité les lieux préalablement aux présentes et, accepte expressément la désignation telle qu'elle figure ci-dessus.
Le **BENEFICIAIRE** déclare avoir été informé de la nécessité de s'informer préalablement à la signature des présentes sur la situation, le voisinage et l'environnement du **BIEN** et, sur toutes éventuelles modifications à venir de l'environnement du **BIEN**.
Le **BENEFICIAIRE** déclare être informé que les démarches effectuées par le Notaire soussigné ne portent que le **BIEN** objet des présentes et non sur son environnement.
Le **BENEFICIAIRE** déclare s'être renseigné préalablement sur la situation et l'environnement de ce **BIEN**.

**Observations concernant la surface et les limites**

Le **BIEN** est désigné par ses références cadastrales **et figure sur le plan cadastral annexé**.
La contenance cadastrale est généralement obtenue par mesures graphiques relevées sur le plan cadastral à partir des limites y figurant ;
Cette contenance et ces limites n'ont qu'une valeur indicative, le cadastre n'étant pas un document à caractère juridique mais un document à caractère fiscal servant essentiellement au calcul de l'impôt.

{% if bien.equipements %}
**Déclarations diverses**

Le **PROMETTANT** déclare qu'à sa connaissance le bien est équipé ou n'est pas équipé des éléments suivants :

|  |  | OUI | NON | NE SAIT PAS |
| :---: | :---- | :---: | :---: | :---: |
| **1** | Détecteur de fumée | {% if bien.equipements.detecteur_fumee %}X{% endif %} | {% if bien.equipements.detecteur_fumee == false %}X{% endif %} |  |
| **2*** | Cheminée privative à foyer ouvert | {% if bien.equipements.cheminee_foyer_ouvert %}X{% endif %} | {% if bien.equipements.cheminee_foyer_ouvert == false %}X{% endif %} |  |
| **3*** | Cheminée privative à foyer fermé / poêle | {% if bien.equipements.cheminee_foyer_ferme %}X{% endif %} | {% if bien.equipements.cheminee_foyer_ferme == false %}X{% endif %} |  |
| **4*** | Chaudière individuelle | {% if bien.equipements.chaudiere_individuelle %}X{% endif %} | {% if bien.equipements.chaudiere_individuelle == false %}X{% endif %} |  |
|  | Chaudière Collective | {% if bien.equipements.chaudiere_collective %}X{% endif %} | {% if bien.equipements.chaudiere_collective == false %}X{% endif %} |  |
| **5* / 6*** | Cuve à fioul ou Cuve à gaz privative | {% if bien.equipements.cuve_fioul or bien.equipements.cuve_gaz %}X{% endif %} | {% if bien.equipements.cuve_fioul == false and bien.equipements.cuve_gaz == false %}X{% endif %} |  |
| **8*** | Pompe à chaleur ou Climatisation privative | {% if bien.equipements.pompe_chaleur or bien.equipements.climatisation %}X{% endif %} | {% if bien.equipements.pompe_chaleur == false and bien.equipements.climatisation == false %}X{% endif %} |  |
| **9* / 10*** | Panneaux photovoltaïques privatifs | {% if bien.equipements.panneaux_photovoltaiques %}X{% endif %} | {% if bien.equipements.panneaux_photovoltaiques == false %}X{% endif %} |  |
| **11*** | Source ou Récupération des eaux de pluies | {% if bien.equipements.recuperation_eaux_pluie %}X{% endif %} | {% if bien.equipements.recuperation_eaux_pluie == false %}X{% endif %} |  |
| **12*/13*** | Puits ou forage privatif | {% if bien.equipements.puits_forage %}X{% endif %} | {% if bien.equipements.puits_forage == false %}X{% endif %} |  |
| **14*** | WC type broyeur ou chimique | {% if bien.equipements.wc_broyeur %}X{% endif %} | {% if bien.equipements.wc_broyeur == false %}X{% endif %} |  |
| **15*** | Vidéosurveillance privative | {% if bien.equipements.videosurveillance %}X{% endif %} | {% if bien.equipements.videosurveillance == false %}X{% endif %} |  |
| **16*** | Alarme privative | {% if bien.equipements.alarme %}X{% endif %} | {% if bien.equipements.alarme == false %}X{% endif %} |  |
| **17** | Bien raccordé à la Fibre | {% if bien.equipements.fibre %}X{% endif %} | {% if bien.equipements.fibre == false %}X{% endif %} |  |
| **18** | Point de recharge pour véhicule électrique | {% if bien.equipements.recharge_vehicule_electrique %}X{% endif %} | {% if bien.equipements.recharge_vehicule_electrique == false %}X{% endif %} |  |
| **19*** | Coffre-fort inséré dans un mur | {% if bien.equipements.coffre_fort_mural %}X{% endif %} | {% if bien.equipements.coffre_fort_mural == false %}X{% endif %} |  |
| **22 / 23** | Piscine enterrée / hors-sol | {% if bien.equipements.piscine %}X{% endif %} | {% if bien.equipements.piscine == false %}X{% endif %} |  |
| **24** | Loggia fermée par une baie vitrée | {% if bien.equipements.loggia_fermee %}X{% endif %} | {% if bien.equipements.loggia_fermee == false %}X{% endif %} |  |

Le **BENEFICIAIRE,** informé de cette situation, déclare prendre le **BIEN** en l'état.
{% endif %}

{% if bien.chauffage %}
**Système de chauffage**

Le **PROMETTANT** déclare que le système de chauffage est {{ bien.chauffage.type }} {% if bien.chauffage.collectif %}collective{% else %}individuelle{% endif %} au {{ bien.chauffage.energie }}{% if bien.chauffage.entretien %} dont l'entretien est assuré par {{ bien.chauffage.entretien }}{% endif %}.
{% endif %}

# **Usage du bien**

Le **PROMETTANT** déclare que le **BIEN** est actuellement à usage {{ bien.usage_actuel }}.
Le **BENEFICIAIRE** entend conserver cet usage{% if bien.usage_futur == "residence_principale" %} et vouloir en faire sa résidence principale{% endif %}.

Le **BENEFICIAIRE** déclare ne pas envisager d'opération de modification du **BIEN** qui nécessiterait soit un arrêté de non-opposition à déclaration préalable de travaux soit un permis de construire, et dont l'obtention préalable à la vente serait pour lui constitutive d'une condition suspensive.

# **ORIGINE DE PROPRIÉTÉ**

Le **PROMETTANT** déclare être propriétaire des biens et droits immobiliers objet des présentes, en vertu des titres ci-après relatés.

{% for origine in origine_propriete %}
## **Concernant {% if origine.lots_concernes | length > 1 %}les lots numéros {% else %}le lot numéro {% endif %}{{ origine.lots_concernes | join(", ") }}**

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

{% if origine.origine_immediate.inscriptions %}
### Inscriptions grevant le bien

Le bien est grevé des inscriptions suivantes :

{% for inscription in origine.origine_immediate.inscriptions %}
* **{{ inscription.type }}** : {{ inscription.description }}
  - Bénéficiaire : {{ inscription.beneficiaire }}
  - Date : {{ inscription.date | format_date }}
  {% if inscription.montant %}- Montant : {{ inscription.montant | format_nombre }} EUR{% endif %}
{% endfor %}

Le **PROMETTANT** s'engage à faire radier ou réduire toutes inscriptions grevant le bien, pour ce qui pourrait rester dû, de sorte que celui-ci soit libre de toutes inscriptions le jour de la réitération par acte authentique.
{% endif %}

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
{% if origine_ant.attestation_propriete %}Attestation de propriété reçue par {{ origine_ant.attestation_propriete.notaire }} le {{ origine_ant.attestation_propriete.date | format_date }}.{% endif %}

{% elif origine_ant.type == 'licitation' or origine_ant.type == 'partage' %}
Le bien a été attribué au propriétaire précédent par suite de {{ origine_ant.type }} suivant acte reçu par {{ origine_ant.notaire }} le {{ origine_ant.date | format_date }}.
{% if origine_ant.publication %}Publié au service de la publicité foncière de {{ origine_ant.publication.service }} le {{ origine_ant.publication.date | format_date }}.{% endif %}

{% elif origine_ant.type == 'donation' %}
Le bien avait été donné au propriétaire précédent par {{ origine_ant.donateur }} suivant acte reçu par {{ origine_ant.notaire }} le {{ origine_ant.date | format_date }}.
{% if origine_ant.publication %}Publié au service de la publicité foncière de {{ origine_ant.publication.service }} le {{ origine_ant.publication.date | format_date }}.{% endif %}

{% else %}
{{ origine_ant.description | default('Origine antérieure non détaillée') }}
{% endif %}
{% endfor %}
{% endif %}

{% if origine.titre_originaire %}
### Titre originaire

ORIGINAIREMENT, lesdits biens et droits immobiliers appartenaient à {{ origine.titre_originaire.proprietaire }} par suite de {{ origine.titre_originaire.mode_acquisition }}.

{% if origine.titre_originaire.details %}{{ origine.titre_originaire.details }}{% endif %}

{% if origine.titre_originaire.acte %}
Suivant acte reçu par {{ origine.titre_originaire.acte.notaire }}, notaire{% if origine.titre_originaire.acte.lieu %} à {{ origine.titre_originaire.acte.lieu }}{% endif %}, le {{ origine.titre_originaire.acte.date | format_date }}.
{% if origine.titre_originaire.acte.publication %}Publié au service de la publicité foncière de {{ origine.titre_originaire.acte.publication.service }} le {{ origine.titre_originaire.acte.publication.date | format_date }}.{% endif %}
{% endif %}
{% endif %}

{% endfor %}

# **Effet relatif**

Les titres de propriété antérieurs, les pièces d'urbanisme ou autres, ne doivent pas révéler de servitudes, de charges, ni de vices non indiqués aux présentes pouvant grever l'immeuble et en diminuer sensiblement la valeur ou le rendre impropre à la destination que le **BENEFICIAIRE** entend lui donner. Le **PROMETTANT** devra justifier d'une origine de propriété régulière remontant à un titre translatif d'au moins trente ans.

# **Caractéristiques**

Les parties conviennent entre elles d'établir les présentes sous la forme d'une promesse unilatérale dans les termes du second alinéa de l'article 1106 du Code civil. Dans la commune intention des parties, et pendant toute la durée du contrat, celle-ci obéira aux dispositions qui suivent.

# **Information préalable**

Les parties ont été informées par le rédacteur des présentes que la forme sous signature privée ne leur permet pas de faire publier un acte au service de la publicité foncière.
En conséquence, et dans cette hypothèse, si l'une d'entre elles refusait ou devenait incapable de réaliser ou de réitérer la convention par acte authentique, l'autre partie ne pourrait pas faire inscrire les présentes directement au fichier immobilier afin de conserver son droit et de le rendre opposable aux tiers, préalablement à toute décision de justice.
Les parties ainsi averties de cette situation déclarent vouloir opter expressément pour la conclusion entre elles d'un acte authentique.

# **Délai**

La promesse de vente est consentie pour une durée expirant :

---

le **{{ delais.expiration_promesse.date | format_date }}**, à {{ delais.expiration_promesse.heure }}.
---

En cas de carence du **PROMETTANT** pour la réalisation de la vente, ce dernier ne saurait se prévaloir à l'encontre du **BENEFICIAIRE** de l'expiration du délai ci-dessus fixé.

**Information des parties sur le rendez-vous de signature**

Les parties sont informées que la date mentionnée ci-dessus ne constitue pas la date précise du rendez-vous de signature de l'acte de vente. Il leur appartiendra de se rapprocher préalablement de leur notaire afin de fixer une date de signature.
Par conséquent, leur attention est attirée sur les risques encourus en prenant des engagements personnels tels que donner congé à son bailleur, réserver définitivement un déménageur, commander des travaux, commander et faire livrer du mobilier, réinvestir le prix de vente et dont l'exécution serait basée sur la signature de l'acte de vente à cette date précise.

# **RÉALISATION**

La réalisation de la promesse aura lieu :

* Soit par la signature de l'acte authentique constatant le caractère définitif de la vente, accompagnée du versement par virement sur le compte du notaire chargé de recevoir l'acte authentique de vente d'une somme correspondant :
* au prix stipulé payable comptant déduction faite de l'indemnité d'immobilisation éventuellement versée en exécution des présentes,
* à la provision sur frais d'acte de vente et de prêt éventuel,
* à l'éventuelle commission d'intermédiaire,
* et de manière générale de tous comptes et proratas.
* Soit par la levée d'option faite par le **BENEFICIAIRE** à l'intérieur de ce délai, suivie de la signature de l'acte authentique de vente dans le délai visé ci-dessus. Si la levée d'option a lieu alors que des conditions suspensives sont encore pendantes, elle n'impliquera pas renonciation à celles-ci, sauf volonté contraire exprimée par le **BENEFICIAIRE**. Cette levée d'option sera effectuée par le **BENEFICIAIRE** auprès du notaire rédacteur de l'acte de vente par tous moyens et toutes formes ; elle devra être accompagnée, pour être recevable, du versement par virement sur le compte dudit notaire d'une somme correspondant :
* au montant de l'apport personnel déduction faite de l'indemnité d'immobilisation éventuellement versée en exécution des présentes (étant précisé que, pour la partie du prix payé au moyen d'un emprunt, il convient de justifier de la disponibilité des fonds ou d'une offre de prêt acceptée),
* à la provision sur frais d'acte de vente et de prêt éventuel,
* à l'éventuelle commission d'intermédiaire.
* et pour les fonds d'emprunt, de la justification de la disponibilité effective de ces fonds, cette justification résultant soit d'un dossier de prêt transmis par l'établissement prêteur, soit d'une attestation de l'organisme prêteur.

L'attention du **BENEFICIAIRE** est particulièrement attirée sur les points suivants :

* L'obligation de paiement par virement et non par chèque même s'il est de banque résulte des dispositions de l'article L 112-6-1 du Code monétaire et financier.
* Il lui sera imposé de fournir une attestation émanant de la banque qui aura émis le virement et justifiant de l'origine des fonds sauf si ces fonds résultent d'un ou plusieurs prêts constatés dans l'acte authentique de vente ou dans un acte authentique séparé.

# **Rédacteur de l'acte authentique de vente**

L'acte authentique constatant la réalisation de la vente sera reçu par {{ acte.notaire.civilite }} {{ acte.notaire.prenom }} {{ acte.notaire.nom }}, notaire soussigné{% if acte.notaire_beneficiaire %} avec la participation de {{ acte.notaire_beneficiaire.civilite }} {{ acte.notaire_beneficiaire.prenom }} {{ acte.notaire_beneficiaire.nom }}, notaire à {{ acte.notaire_beneficiaire.ville }}{% endif %}.
En toute hypothèse, le transfert de propriété est reporté au jour de la constatation de la vente en la forme authentique et du paiement du prix tel que convenu et des frais, même si l'échange de consentement nécessaire à la formation de la convention est antérieur.

**AVENANT EVENTUEL**

Les parties conviennent expressément, que pour le cas où un avenant deviendrait nécessaire concernant des modifications dans leur convention ou sa prorogation (report de la date de signature de l'acte authentique ou de levée d'option par exemple), cet avenant pourra être rédigé sous forme d'acte sous seing privé, sous forme d'un acte authentique, ou pourra résulter de tout document attestant de leur volonté respective comme un simple mail ou courrier.

# **CARENCE**

La carence s'entend ici du manquement fautif par l'une des parties, du fait de sa volonté ou de sa négligence, à une ou plusieurs de ses obligations aux présentes, ce manquement empêchant l'exécution de la vente.

**En l'absence de levée d'option ou de signature de l'acte de vente dans le délai**
Au cas où le **BENEFICIAIRE** n'aurait ni levé l'option ni signé l'acte de vente à l'intérieur du délai de réalisation, il sera de plein droit déchu du bénéfice de la promesse au terme dudit délai de réalisation sans qu'il soit besoin d'une mise en demeure de la part du **PROMETTANT**, qui disposera alors librement du **BIEN** nonobstant toute manifestation ultérieure de la volonté du **BENEFICIAIRE** de l'acquérir.

**En cas de levée d'option dans le délai**
Si le **BENEFICIAIRE** a valablement levé l'option dans le délai de réalisation ci-dessus, accompagné du paiement du prix et des frais, mais que l'acte de vente n'est pas intervenu dans les quinze jours de celle-ci, alors la partie la plus diligente mettra l'autre partie en demeure, par acte d'huissier, d'avoir à comparaître en l'étude du notaire chargé de recevoir l'acte de vente à l'effet de signer cet acte.

Si, malgré la mise en demeure effectuée dans les conditions ci-dessus indiquées, l'une des parties refusait ou s'abstenait de régulariser l'acte de vente le jour indiqué dans la mise en demeure, il sera procédé à ladite date à l'établissement d'un procès-verbal, dans les termes duquel il sera constaté le défaut du **PROMETTANT** ou du **BENEFICIAIRE**. Ce procès-verbal devra être établi, si chacune des parties a son propre notaire, par le notaire du **PROMETTANT** en cas de défaut du **BENEFICIAIRE** et par le notaire du **BENEFICIAIRE** en cas de défaut du **PROMETTANT**.

En cas de défaut du **PROMETTANT**, le **BENEFICIAIRE** pourra à son choix dans le procès-verbal :

* Soit faire part de son intention de poursuivre l'exécution de la vente, indépendamment de son droit de réclamer une juste indemnisation.
* Soit encore faire constater que la vente n'est pas exécutée, cette constatation résultant du défaut prononcé contre le **PROMETTANT** dans le procès-verbal, et déclarer sa volonté de considérer la vente comme résolue de plein droit. Le **BENEFICIAIRE** reprendra alors purement et simplement sa liberté indépendamment de son droit de réclamer une juste indemnisation de son préjudice.

En cas de défaut du **BENEFICIAIRE** qui ne viendrait ou ne voudrait pas signer la vente malgré la levée d'option, le **PROMETTANT** pourra à son choix dans le procès-verbal :

* Soit faire part de son intention de poursuivre l'exécution de la vente.
* Soit encore faire constater que la vente n'est pas exécutée, cette constatation résultant du défaut prononcé contre le **BENEFICIAIRE** dans le procès-verbal, et déclarer sa volonté de considérer la vente comme résolue de plein droit. Le **PROMETTANT** reprendra alors purement et simplement sa liberté indépendamment de son droit de réclamer le versement de la pénalité compensatoire ci-après visée dans l'acte au titre de l'indemnisation de son préjudice.

# **Force exécutoire de la promesse**

Il est entendu entre les parties qu'en raison de l'acceptation par le **BENEFICIAIRE** de la promesse faite par le **PROMETTANT**, en tant que simple promesse, il s'est formé entre elles un contrat dans les termes de l'article 1124 du Code civil. En conséquence, et pendant toute la durée du contrat, celui-ci ne pourra être révoqué que par leur consentement mutuel. Il en résulte notamment que :

* Le **PROMETTANT** a, pour sa part, définitivement consenti à la vente et qu'il est d'ores et déjà débiteur de l'obligation de transférer la propriété au profit du **BENEFICIAIRE** aux conditions des présentes. Le **PROMETTANT** ne peut plus, par suite, pendant toute la durée de la présente promesse, conférer une autre promesse à un tiers ni aucun droit réel ni charge quelconque sur le **BIEN**, consentir aucun bail, location ou prorogation de bail. Il ne pourra non plus apporter aucune modification matérielle, si ce n'est avec le consentement du **BENEFICIAIRE**, ni détérioration au **BIEN**. Il en ira de même si la charge ou la détérioration n'était pas le fait direct du **PROMETTANT**. Le non-respect de cette obligation entraînera l'extinction des présentes si bon semble au **BENEFICIAIRE**.
* Par le présent contrat de promesse, les parties conviennent que la formation du contrat de vente est exclusivement subordonnée au consentement du **BENEFICIAIRE**, indépendamment du comportement du **PROMETTANT**.
* Toute révocation ou rétractation unilatérale de la volonté du **PROMETTANT** sera de plein droit dépourvue de tout effet sur le contrat promis du fait de l'acceptation de la présente promesse en tant que telle par le **BENEFICIAIRE**. En outre, le **PROMETTANT** ne pourra pas se prévaloir des dispositions de l'article 1590 du Code civil en offrant de restituer le double de la somme le cas échéant versée au titre de l'indemnité d'immobilisation.
* En tant que de besoin, le **PROMETTANT** se soumet à l'exécution en nature prévue par l'article 1221 du Code civil si le **BENEFICIAIRE** venait à la demander. Le tout sauf si ce mode d'exécution est soit devenu impossible soit d'une disproportion manifeste entre son coût pour le débiteur de bonne foi et son intérêt pour le créancier.

# **Propriété jouissance**

Le **BENEFICIAIRE** sera propriétaire des **BIENS** objet de la promesse le jour de la constatation de la vente en la forme authentique et il en aura la jouissance à compter du même jour par la prise de possession réelle, les **BIENS** devant être impérativement, à cette même date, libres de toute location ou occupation.
Le **PROMETTANT** déclare que les **BIENS** n'ont pas, avant ce jour, fait l'objet d'un congé pouvant donner lieu à l'exercice d'un droit de préemption.

# **PRIX - CONDITIONS FINANCIERES**

# **PRIX**

La vente, en cas de réalisation, aura lieu moyennant le prix de **{{ prix.montant | montant_en_lettres | upper }} ({{ prix.montant | format_nombre }} {{ prix.devise | default("EUR") }})**, qui sera payable comptant le jour de la constatation authentique de la réalisation de la promesse.

# **Frais**

Les frais, droits et émoluments de la vente seront à la charge du **BENEFICIAIRE**.

<!-- SECTION: negociation | CONDITIONNEL: negociation.existe -->
{% if negociation and negociation.existe %}
# **Négociation**

Les parties reconnaissent que le prix a été négocié par **{{ negociation.agent.nom }}** titulaire d'un mandat donné par **{{ negociation.agent.mandant }}** sous le numéro {{ negociation.agent.mandat_numero }} en date du {{ negociation.agent.mandat_date }} non encore expiré, ainsi déclaré.
En conséquence, **{{ negociation.a_charge_de }}** qui en a seul la charge aux termes du mandat, doit à l'agence une rémunération de **{{ negociation.honoraires | format_nombre }} EUR**, taxe sur la valeur ajoutée incluse.
Cette rémunération sera payée le jour de la constatation authentique de la réalisation des présentes.

{% if negociation.inclus_dans_prix %}
Etant ici précisé que le montant de la négociation est compris dans le prix indiqué ci-dessus.
{% endif %}
{% endif %}

**COUT DE L'OPERATION ET FINANCEMENT PREVISIONNEL**

A titre indicatif, le coût et le financement de l'opération sont les suivants :

| Prix  | {{ prix.montant | format_nombre }} EUR |
| :---- | ----: |
| Frais de la vente | ... |
{% if negociation and negociation.existe %}
| Frais de négociation | {% if negociation.inclus_dans_prix %}néant (inclus){% else %}{{ negociation.honoraires | format_nombre }} EUR{% endif %} |
{% endif %}
| **Ensemble** | **...** |
|  |  |
| FINANCEMENT |  |
{% if financement.fonds_empruntes %}
| Fonds empruntés | {{ financement.fonds_empruntes | format_nombre }} EUR |
{% endif %}
{% if financement.fonds_personnels %}
| Fonds personnels | {{ financement.fonds_personnels | format_nombre }} EUR |
{% endif %}
|  |  |
| **Ensemble**  | **...** |

# **Indemnité d'immobilisation**

En considération de la promesse formelle conférée au **BENEFICIAIRE** par le **PROMETTANT**, dans les conditions ci-dessus prévues, les parties conviennent de fixer le montant de l'indemnité d'immobilisation à la somme forfaitaire de **{{ indemnite_immobilisation.montant | montant_en_lettres }}** (représentant {{ indemnite_immobilisation.pourcentage }}% du prix de vente) et indépendamment de la durée de la promesse de vente.
Pour la bonne compréhension des présentes, il est ici précisé que cette indemnité d'immobilisation constituant le seul prix de l'exclusivité conférée au **BENEFICIAIRE**, ne pourra être modifiée par le juge, les dispositions de l'article 1231-5 du Code civil lui étant inapplicable.

**A-** Sur laquelle somme, le **BÉNÉFICIAIRE** s'engage à verser **à titre de dépôt de garantie la somme de {{ indemnite_immobilisation.depot_garantie | montant_en_lettres }}** par virement bancaire, en la comptabilité du notaire rédacteur des présentes au sein de la {{ acte.notaire.societe }}, {{ acte.notaire.adresse }}, {{ acte.notaire.ville }} ({{ acte.notaire.code_postal }}) susnommée, **au plus tard dans les {{ delais.delai_depot_garantie_jours | default(15) | nombre_en_lettres | upper }} ({{ delais.delai_depot_garantie_jours | default(15) }}) JOURS des présentes**, à défaut ladite promesse sera caduque sans indemnité de part et d'autre, si bon semble au **PROMETTANT**, par un simple courriel adressé au notaire soussigné, rédacteur des présentes.

À cet effet, avec l'accord des parties, elle sera versée en la comptabilité du notaire rédacteur des présentes au sein de la {{ acte.notaire.societe }} susnommée, constitué séquestre et dépositaire du dépôt de garantie ci-dessus prévu. L'encaissement par lui du virement vaudra acceptation de sa mission de tiers séquestre.
De convention expresse entre les parties, cette somme sera affectée à titre de nantissement conformément aux dispositions des articles 2355 et suivants du Code civil entre les mains du **SEQUESTRE** en qualité de tiers dépositaire, par le **PROMETTANT** au profit du **BENEFICIAIRE** qui accepte, à la garantie de la restitution éventuelle de la somme versée.

**Faute pour le BENEFICIAIRE de satisfaire à cette obligation de versement dans le délai ci-dessus, sans qu'il soit nécessaire d'effectuer une mise en demeure par le PROMETTANT, ce dernier sera libéré, si bon lui semble, de son engagement de vendre par le seul fait de la constatation de l'absence de virement total ou partiel du dépôt de garantie dans le délai susvisé, la présente clause étant une clause résolutoire de plein droit des présentes.**

A cet égard, les parties reconnaissent avoir été informées par le notaire soussigné que, savoir :

* **la responsabilité de l'Office Notarial destinataire du virement ne pourra en aucun cas être engagée en cas de non-respect par le BENEFICIAIRE de son obligation, et que**
* **passé le délai limite octroyé au BENEFICIAIRE pour effectuer le virement du dépôt de garantie, le PROMETTANT devra s'assurer auprès de l'office notarial destinataire de ce virement, la confirmation que celui-ci a bien été effectué.**

La mission du séquestre sera la suivante :
1°- Il remettra cette somme au **PROMETTANT** pour imputation sur le prix convenu, en cas de réalisation de la vente, objet de la promesse de vente.
2°- Il remettra cette somme au **BENEFICIAIRE** dans le cas où celui-ci mettrait en jeu son droit de rétractation, s'il en bénéficie. Conformément aux dispositions prévues par l'article L.271-1 du Code de la construction et de l'habitation, le **SEQUESTRE** les restituera dans un délai de vingt et un jours à compter du lendemain de la date de rétractation, sur présentation de la copie de la notification de rétractation et de l'avis de réception (première présentation) ou du récépissé du **PROMETTANT**.
3°- Il remettra également cette somme au **BENEFICIAIRE** dans tous les cas où la non-réalisation de la vente résulterait de la défaillance de l'une quelconque des conditions suspensives ci-dessous stipulées et auxquelles le **BENEFICIAIRE** n'aurait pas renoncé.
4°- Il remettra cette somme au **PROMETTANT** au cas où, la présente promesse n'étant frappée ni de caducité ni de résolution pour l'un des motifs indiqués ci-dessus, le **BENEFICIAIRE** n'aurait pas levé l'option dans les délais et conditions prévus.

Toutefois cette mission ne pourra s'exécuter que d'un commun accord entre les parties ou en vertu d'une décision judiciaire passée en force de chose jugée.
En cas d'opposition ou de difficulté, le séquestre devra verser la somme dont il est dépositaire à la Caisse des Dépôts et Consignations avec indication de l'affectation ci-dessus stipulée.
Ces paiements, restitution ou consignation, selon le cas, vaudront au séquestre pleine et entière décharge de sa mission.

{% if indemnite_immobilisation.surplus %}
**B- Quant au surplus de l'indemnité d'immobilisation**, soit la somme de **{{ indemnite_immobilisation.surplus | montant_en_lettres }}** le **BENEFICIAIRE** s'oblige à le verser au **PROMETTANT** au plus tard dans le délai de QUINZE (15) jours de l'expiration du délai offert au **BENEFICIAIRE** pour lever l'option, pour le cas où le **BENEFICIAIRE**, toutes les conditions suspensives ayant été réalisées, ne signerait pas l'acte de vente de son seul fait.
{% endif %}

Le **BENEFICIAIRE** déclare effectuer le paiement du dépôt de garantie au moyen de ses fonds propres.

**CLAUSE PENALE - INEXECUTION PAR LE PROMETTANT**
En cas d'aliénation à un tiers du bien objet de la présente promesse, comme pour le cas où, toutes les conditions suspensives ci-après étant remplies, le **PROMETTANT** ne régulariserait pas l'acte authentique de vente en violation des obligations ci-dessus contractées,
Ce dernier sera redevable envers le **BENEFICIAIRE** de dommages et intérêts fixés à titre de clause pénale à la somme de **{{ clause_penale.pourcentage | default(10) | nombre_en_lettres | upper }} POUR CENT ({{ clause_penale.pourcentage | default(10) }} %)** du montant du prix de vente.
La présente clause pénale ne peut priver, dans la même hypothèse, le **BENEFICIAIRE** de poursuivre le **PROMETTANT** en exécution forcée de la vente ainsi qu'il a été prévu ci-dessus.

# **Réserves et conditions suspensives**

Les effets des présentes sont soumis à la levée des réserves et à l'accomplissement des conditions suspensives suivantes.

## **Réserves**

### **Réserve du droit de préemption**

La promesse sera notifiée à tous les titulaires d'un droit de préemption institué en vertu de l'article L211-1 du Code de l'urbanisme ou de tout autre Code.
L'exercice de ce droit par son titulaire obligera le **PROMETTANT** aux mêmes charges et conditions convenues aux présentes.
Par cet exercice les présentes ne produiront pas leurs effets entre les parties et ce même en cas d'annulation de la préemption ou de renonciation ultérieure à l'exercice de ce droit de la part de son bénéficiaire.

## **Conditions suspensives**

Les présentes sont soumises à l'accomplissement de conditions suspensives indiquées ci-après.
Conformément aux dispositions de l'article 1304-6 du Code civil, à partir de cet accomplissement les obligations contractées produisent leurs effets.
La non réalisation d'une seule de ces conditions, pouvant être invoquée par les deux parties, entraîne la caducité des présentes, qui sont alors réputées n'avoir jamais existé.
Toute condition suspensive est réputée accomplie, lorsque sa réalisation est empêchée par la partie qui y avait intérêt.
Conformément aux dispositions de l'article 1304-4 du Code civil, la partie en faveur de laquelle est stipulée exclusivement une condition suspensive est libre d'y renoncer tant que celle-ci n'est pas accomplie ou n'a pas défailli.
Dans ce cas, cette renonciation doit intervenir par courrier recommandé, adressé au notaire qui la représente dans le délai prévu pour sa réalisation.

En toutes hypothèses, jusqu'à la réitération authentique des présentes, le **PROMETTANT** conserve l'administration, les revenus et la gestion des risques portant sur le **BIEN**.

### **Conditions suspensives de droit commun**

Les présentes sont soumises à l'accomplissement des conditions suspensives de droit commun stipulées en la faveur du **BENEFICIAIRE**, qui sera seul à pouvoir s'en prévaloir.
Les titres de propriété antérieurs, les pièces d'urbanisme ou autres, ne doivent pas révéler de servitudes, de charges, ni de vices non indiqués aux présentes pouvant grever l'immeuble et en diminuer sensiblement la valeur ou le rendre impropre à la destination que le **BENEFICIAIRE** entend donner. Le **PROMETTANT** devra justifier d'une origine de propriété régulière remontant à un titre translatif d'au moins trente ans.
L'état hypothécaire ne doit pas révéler de saisies ou d'inscriptions dont le solde des créances inscrites augmenté du coût des radiations à effectuer serait supérieur au prix disponible.

### **Conditions suspensives particulières**

<!-- SECTION: condition_suspensive_pret | CONDITIONNEL: condition_suspensive_pret.existe -->
{% if condition_suspensive_pret and condition_suspensive_pret.existe %}
#### **Condition suspensive d'obtention de prêt**

Le **BENEFICIAIRE** déclare avoir l'intention de recourir pour le paiement du prix de cette acquisition, à un ou plusieurs prêts rentrant dans le champ d'application de l'article L 313-40 du Code de la consommation, et répondant aux caractéristiques suivantes :

Montant maximal de la somme empruntée : **{{ condition_suspensive_pret.montant_maximal | format_nombre }} euros**
Durée maximale de remboursement : **{{ condition_suspensive_pret.duree_maximale_annees }} ans.**
Taux nominal d'intérêt maximal : **{{ condition_suspensive_pret.taux_maximal }} % l'an (hors assurances)**

Toute demande non conforme aux stipulations contractuelles, notamment quant au montant emprunté, au taux et à la durée de l'emprunt, entraînera la réalisation fictive de la condition au sens du premier alinéa de l'article 1304-3 du Code civil.

Etant précisé que l'indication d'un montant maximal de prêt ne peut contraindre le **BENEFICIAIRE** à accepter toute offre d'un montant inférieur.

La condition suspensive sera réalisée en cas d'obtention par le **BENEFICIAIRE** d'une ou plusieurs offres écrites de prêt aux conditions sus-indiquées **au plus tard le {{ condition_suspensive_pret.date_limite | format_date }}**.

La durée de validité de cette condition suspensive ne peut être inférieure à un mois à compter de la date de signature de l'acte (article L 313-41 du Code de la consommation).
Le **BENEFICIAIRE** déclare qu'à sa connaissance :

* Il n'existe pas d'empêchement à l'octroi de ces prêts qui seront sollicités.
* Il n'existe pas d'obstacle à la mise en place d'une assurance décès-invalidité.
* Il déclare avoir connaissance des dispositions de l'alinéa premier de l'article 1304-3 du Code civil qui dispose que :

*"La condition suspensive est réputée accomplie si celui qui y avait intérêt en a empêché l'accomplissement."*

L'obtention ou la non-obtention de l'offre de prêt, demandé aux conditions ci-dessus, devra être notifiée par le **BENEFICIAIRE** au **PROMETTANT** et au notaire.
A défaut de cette notification, le **PROMETTANT** aura, à compter du lendemain de la date indiquée ci-dessus, la faculté de mettre le **BENEFICIAIRE** en demeure de lui justifier sous huitaine de la réalisation ou de la défaillance de la condition.
Cette demande devra être faite par lettre recommandée avec avis de réception à son adresse, avec une copie en lettre simple pour le notaire.
Passé ce délai de huit jours décompté du jour de la première présentation, sans que le **BENEFICIAIRE** ait apporté la preuve de la remise d'une offre écrite conforme, la condition sera censée défaillie et les présentes seront donc caduques de plein droit. Dans ce cas, le **BENEFICIAIRE** pourra recouvrer les fonds déposés, le cas échéant, en garantie de l'exécution des présentes en justifiant qu'il a accompli les démarches nécessaires pour l'obtention du prêt, et que la condition n'est pas défaillie de son fait. A défaut, ces fonds resteront acquis au **PROMETTANT**.

Jusqu'à l'expiration du délai de huit jours susvisé, le **BENEFICIAIRE** pourra renoncer au bénéfice de la condition suspensive légale de l'article L 313-41 du Code de la consommation, soit en acceptant des offres de prêt à des conditions moins favorables que celles ci-dessus exprimées, et en notifiant ces offre et acceptation au **PROMETTANT**, soit en exprimant une intention contraire à celle ci-dessus exprimée, c'est-à-dire de ne plus faire appel à un emprunt et en doublant cette volonté nouvelle de la mention manuscrite voulue par l'article L 313-42 de ce Code ; cette volonté nouvelle et la mention feraient, dans cette hypothèse, l'objet d'un écrit notifié au **PROMETTANT**.

**Refus de prêt – justification**

Le **BENEFICIAIRE** s'engage, en cas de non-obtention du financement demandé, à justifier de {{ condition_suspensive_pret.nombre_refus_requis | default(2) | nombre_en_lettres }} refus de prêt répondant aux caractéristiques ci-dessus. En conséquence, le **BENEFICIAIRE** s'engage à déposer {{ condition_suspensive_pret.nombre_refus_requis | default(2) | nombre_en_lettres }} demandes de prêt.
{% endif %}

# **Conditions et déclarations générales**

## **Garantie contre le risque d'éviction**

Le **PROMETTANT** garantira le **BENEFICIAIRE** contre le risque d'éviction conformément aux dispositions de l'article 1626 du Code civil.

A ce sujet le **PROMETTANT** déclare :

* qu'il n'existe à ce jour aucune action ou litige en cours pouvant porter atteinte au droit de propriété,
* qu'il n'y a eu aucun empiètement sur le fonds voisin,
* que le **BIEN** ne fait l'objet d'aucune injonction de travaux,
* que le **BIEN** n'a pas fait de sa part l'objet de travaux modifiant l'aspect extérieur de l'immeuble ou les parties communes qui n'auraient pas été régulièrement autorisés par l'assemblée des copropriétaires et les services de l'urbanisme,
* qu'il n'a pas modifié la destination du **BIEN** en contravention des dispositions du règlement de copropriété,
* que le **BIEN** n'a pas été modifié de son fait par une annexion ou une utilisation irrégulière privative de parties communes,
* qu'il n'a conféré à personne d'autre que le **BENEFICIAIRE** un droit quelconque sur le **BIEN** pouvant empêcher la vente,
* subroger le **BENEFICIAIRE** dans tous ses droits et actions relatifs au **BIEN**.

## **Garantie de jouissance**

Le **PROMETTANT** déclare qu'il n'a pas délivré de congé à un ancien locataire lui permettant d'exercer un droit de préemption.

## **Garantie hypothécaire**

Le **PROMETTANT** s'obligera, s'il existe un ou plusieurs créanciers hypothécaires inscrits, à régler l'intégralité des sommes pouvant leur être encore dues, à rapporter à ses frais les certificats de radiation des inscriptions.

## **Servitudes**

Le **BENEFICIAIRE** profitera ou supportera les servitudes ou les droits de jouissance spéciale, s'il en existe.

Le **PROMETTANT** déclare :

* ne pas avoir créé ou laissé créer de servitude ou de droit de jouissance spéciale qui ne seraient pas relatés aux présentes,
* qu'à sa connaissance, il n'existe pas d'autres servitudes ou droits de jouissance spéciale que celles ou ceux résultant, le cas échéant, de l'acte, de la situation naturelle et environnementale des lieux, de l'urbanisme et du règlement de copropriété et de ses modificatifs,
* ne pas avoir connaissance de faits ou actes tels qu'ils seraient de nature à remettre en cause l'exercice de servitude relatée aux présentes.

## **Etat du bien**

Le **BENEFICIAIRE** prendra le **BIEN** dans l'état où il se trouve à ce jour, tel qu'il l'a vu et visité, le **PROMETTANT** s'interdisant formellement d'y apporter des modifications matérielles ou juridiques.
Il déclare que la désignation du **BIEN** figurant aux présentes correspond à ce qu'il a pu constater lors de ses visites.

II n'aura aucun recours contre le **PROMETTANT** pour quelque cause que ce soit notamment en raison :

* des vices apparents,
* des vices cachés.

S'agissant des vices cachés, il est précisé que cette exonération de garantie ne s'applique pas :

* si le **PROMETTANT** a la qualité de professionnel de l'immobilier ou de la construction, sauf si le **BENEFICIAIRE** a également cette qualité,
* ou s'il est prouvé par le **BENEFICIAIRE**, dans le délai légal, que les vices cachés étaient en réalité connus du **PROMETTANT**.

Toutefois, le **PROMETTANT** est avisé que, s'agissant des travaux qu'il a pu exécuter par lui-même, la jurisprudence tend à écarter toute efficacité de la clause d'exonération de garantie des vices cachés.

## **Contenance du terrain d'assiette**

Le **PROMETTANT** ne confère aucune garantie de contenance du terrain d'assiette de l'ensemble immobilier.

## **Impôts et taxes**

### **Impôts locaux**

Le **PROMETTANT** déclare être à jour des mises en recouvrement des impôts locaux.
Le **BENEFICIAIRE** sera redevable à compter du jour de la signature de l'acte authentique des impôts et contributions.
La taxe d'habitation, si elle est exigible, est due pour l'année entière par l'occupant au premier jour du mois de janvier.
La taxe foncière, ainsi que la taxe d'enlèvement des ordures ménagères si elle est due, seront réparties entre le **PROMETTANT** et le **BENEFICIAIRE** en fonction du temps pendant lequel chacun aura été propriétaire au cours de l'année de la constatation de la réalisation des présentes.

Le **BENEFICIAIRE** règlera directement au **PROMETTANT**, le jour de la signature de l'acte authentique de vente, le prorata de taxe foncière et, le cas échéant, de taxe d'enlèvement des ordures ménagères, déterminé par convention entre les parties sur le montant de la dernière imposition.
Ce règlement sera définitif entre les parties, éteignant toute créance ou dette l'une vis-à-vis de l'autre à ce sujet, quelle que soit la modification éventuelle de la taxe foncière pour l'année en cours.

### **Avantage fiscal lié à un engagement de location**

Le **PROMETTANT** déclare ne pas souscrire actuellement à l'un des régimes fiscaux lui permettant de bénéficier de la déduction des amortissements en échange de l'obligation de louer à certaines conditions.

### **Agence nationale de l'habitat**

Le **PROMETTANT** déclare ne pas avoir conclu de convention avec l'agence nationale de l'habitat.

### **Obligation déclarative du propriétaire de bien à usage d'habitation**

Conformément à la loi de finances n° 2019-1479 du 28 décembre 2019, une nouvelle obligation déclarative, en vigueur à partir du 1er janvier 2023, a été mise en place à l'égard des propriétaires de biens immobiliers à usage d'habitation, afin de pouvoir déterminer ceux qui sont encore redevables de la taxe d'habitation (pour les résidences secondaires ou logements locatifs) ou de la taxe sur les logements vacants.
Ainsi, à compter du 1er janvier et jusqu'au 30 juin inclus de chaque année, tous les propriétaires, particuliers ou personnes morales, d'une résidence principale ou secondaire ou d'un bien locatif ou vacant, doivent impérativement déclarer à l'administration fiscale :

* s'ils occupent leur logement à titre de résidence principale ou secondaire, ou s'il est vacant,
* lorsque le **BIEN** est occupé par un tiers, l'identité des occupants et la période d'occupation.

Cette obligation déclarative concerne aussi bien les propriétaires indivis, que les usufruitiers ou les sociétés civiles immobilières, et son non-respect est passible de l'octroi d'une amende d'un montant forfaitaire de 150 euros.
Cette déclaration peut s'opérer :

* via le service en ligne "Gérer mes biens immobiliers", accessible depuis le portail impots.gouv.fr,
* ou via les autres moyens mis à disposition par l'administration.

## **Contrats de distribution et de fourniture**

Le **BENEFICIAIRE** fera son affaire personnelle, dès son entrée en jouissance, de la continuation ou de la résiliation de tous contrats de distribution et de fourniture souscrits par le **PROMETTANT**.
Les parties déclarent avoir été averties de la nécessité d'établir entre elles un relevé des compteurs faisant l'objet d'un comptage individuel.
Le **PROMETTANT** déclare être à jour des factures mises en recouvrement liées à ses contrats de distribution et de fourniture.

## **Assurance**

Le **BENEFICIAIRE**, tout en étant informé de l'obligation immédiate de souscription, ne continuera pas les polices d'assurance actuelles garantissant le **BIEN** et confèrera à cet effet mandat au **PROMETTANT**, qui accepte, de résilier les contrats lorsqu'il avertira son assureur de la signature de l'acte authentique.
L'ensemble immobilier dans lequel se trouve le **BIEN** étant assuré par une police souscrite par le syndicat des copropriétaires, le **BENEFICIAIRE** devra se conformer à toutes les décisions du syndicat la concernant.
Il est rappelé au **BENEFICIAIRE** l'obligation pour chaque copropriétaire de s'assurer contre les risques de responsabilité civile dont il doit répondre en sa qualité soit de copropriétaire occupant, soit de copropriétaire non-occupant.

## **Contrat d'affichage**

Le **PROMETTANT** déclare qu'il n'a pas été conclu de contrat d'affichage.

# **DISPOSITIONS RELATIVES A L'URBANISME**

## **Urbanisme**

{% if urbanisme and urbanisme.note_urbanisme %}
#### **Note d'urbanisme**

La commune a répondu le {{ urbanisme.note_urbanisme.date }} à une demande de note d'urbanisme. Cette réponse est annexée.
**Annexe n°4 : Note d'urbanisme**

Le **BENEFICIAIRE** s'oblige à faire son affaire personnelle de l'exécution des charges et prescriptions, du respect des servitudes publiques et autres limitations administratives au droit de propriété mentionnées sur cette note.

{% if urbanisme.note_urbanisme.observations %}
La note d'urbanisme révèle :
{% for observation in urbanisme.note_urbanisme.observations %}
- {{ observation }}
{% endfor %}
{% endif %}
{% endif %}

{% if urbanisme and urbanisme.note_voirie %}
#### **Note de voirie**

Une note de renseignements de voirie annexée a été délivrée par l'autorité compétente le {{ urbanisme.note_voirie.date }}. {{ urbanisme.note_voirie.resultat }}
**Annexe n°5 : Note de voirie**
{% endif %}

{% if urbanisme and urbanisme.certificat_non_peril %}
#### **Certificat de non-péril**

Il résulte d'un certificat délivré par l'autorité compétente le {{ urbanisme.certificat_non_peril.date }}, annexé, que l'immeuble {{ urbanisme.certificat_non_peril.resultat }}

**Annexe n°6 : Certificat de non-péril**
{% endif %}

# **Dispositions relatives à la construction**

<!-- SECTION: travaux_recents | CONDITIONNEL: travaux_recents.existe -->
{% if travaux_recents and travaux_recents.existe %}
## **Existence de travaux**

Le **PROMETTANT** déclare être informé des dispositions des articles L 241-1 et L 242-1 du Code des assurances imposant à tout propriétaire de souscrire avant toute ouverture de chantier de construction et/ou travaux de gros œuvre ou de second œuvre, une assurance garantissant le paiement des travaux de réparation des dommages relevant de la garantie décennale, ainsi qu'une assurance couvrant sa responsabilité au cas où il interviendrait dans la construction en tant que concepteur, entrepreneur ou maître d'œuvre.

Depuis son acquisition, le **PROMETTANT** déclare que les travaux ci-après indiqués ont été effectués :
{% for travail in travaux_recents.liste %}
- **{{ travail.description }}** suivant facture{% if travail.date_facture %} du {{ travail.date_facture }}{% endif %} de {{ travail.entreprise }}{% if travail.adresse_entreprise %} - {{ travail.adresse_entreprise }}{% endif %}.{% if travail.assurance_decennale %} L'assurance décennale de cette entreprise est fournie.{% endif %}
{% endfor %}

**Annexe n°7 : Factures et décennale susvisés**

Les travaux, compte tenu de la description faite par le **PROMETTANT**, ne nécessitaient pas de déclaration préalable.

Le **PROMETTANT** déclare **{% if travaux_recents.assurance_dommages_ouvrage %}qu'une police d'assurance dommages ouvrage a été souscrite{% else %}qu'aucune police d'assurance dommages ouvrage{% endif %}** ni d'assurance de responsabilité décennale "constructeurs non réalisateur" n'a été souscrite pour la réalisation des rénovations.
Les parties reconnaissent avoir reçu du notaire soussigné toutes explications utiles concernant les conséquences pouvant résulter des garanties et responsabilité du vendeur attachées à ces constructions, et de l'absence de souscription de telles polices d'assurances.
{% else %}
## **Absence d'opération de construction ou de rénovation depuis dix ans**

Le **PROMETTANT** déclare qu'à sa connaissance :

1. aucune construction ou rénovation n'a été effectuée dans les dix dernières années,
2. aucun élément constitutif d'ouvrage ou équipement indissociable de l'ouvrage au sens de l'article 1792 du Code civil n'a été réalisé dans ce délai.
{% endif %}

# **Diagnostics**

## **Dossier de diagnostics techniques**

Pour l'information des parties a été dressé ci-après le tableau du dossier de diagnostics techniques tel que prévu par les articles L 271-4 à L 271-6 du Code de la construction et de l'habitation.

Conformément aux dispositions de l'article L 271-6 du Code de la construction et de l'habitation, le dossier de diagnostic technique a été établi par **{{ diagnostics.diagnostiqueur.nom }}**, diagnostiqueur immobilier certifié par un organisme spécialisé accrédité.

## **Diagnostics techniques**

{% if diagnostics.plomb %}
### **Plomb**

{% if diagnostics.plomb.requis %}
Un constat de risque d'exposition au plomb établi le {{ diagnostics.plomb.date }} est annexé. {{ diagnostics.plomb.resultat }}
{% else %}
L'**ENSEMBLE** **IMMOBILIER** a été construit depuis le 1er janvier 1949, en conséquence il n'entre pas dans le champ d'application des dispositions des articles L 1334-5 et suivants du Code de la santé publique relatifs à la lutte contre la présence de plomb.
{% endif %}
{% endif %}

{% if diagnostics.amiante_parties_privatives %}
### **Amiante**

**Pour les parties privatives**
Un état établi par {{ diagnostics.amiante_parties_privatives.diagnostiqueur }} le {{ diagnostics.amiante_parties_privatives.date }}, accompagné de la certification de compétence, est annexé.
**{{ diagnostics.amiante_parties_privatives.resultat }}**

**Annexe n°8 : Diagnostic amiante parties privatives**

{% if diagnostics.amiante_parties_communes %}
**Pour les parties communes**
Un diagnostic technique a été établi par {{ diagnostics.amiante_parties_communes.diagnostiqueur }} le {{ diagnostics.amiante_parties_communes.date }}.
Les conclusions sont les suivantes : ***"{{ diagnostics.amiante_parties_communes.resultat }}"***

**Annexe n°9 : Diagnostic amiante parties communes**
{% endif %}
{% endif %}

{% if diagnostics.termites %}
### **Termites**

{% if diagnostics.termites.zone_concernee %}
Un état relatif à la présence de termites établi le {{ diagnostics.termites.date }} est annexé. {{ diagnostics.termites.resultat }}
{% else %}
Le **PROMETTANT** déclare :

* qu'à sa connaissance le **BIEN** n'est pas infesté par les termites ;
* qu'il n'a lui-même procédé ni fait procéder par une entreprise à un traitement curatif contre les termites ;
* qu'il n'a reçu du maire aucune injonction de rechercher des termites ou de procéder à des travaux préventifs ou d'éradication ;
* que le **BIEN** n'est pas situé dans une zone contaminée par les termites.
{% endif %}
{% endif %}

{% if diagnostics.merules %}
### **Mérules**

{% if diagnostics.merules.zone_concernee %}
Le **BIEN** se trouve dans une zone de présence d'un risque de mérule délimitée par un arrêté préfectoral.
{% else %}
Le **BIEN** ne se trouve pas actuellement dans une zone de présence d'un risque de mérule délimitée par un arrêté préfectoral.
Le **PROMETTANT** déclare ne pas avoir constaté l'existence de zones de condensation interne, de moisissures ou encore de présence d'effritements ou de déformation dans le bois ou l'existence de filaments blancs à l'aspect cotonneux.
{% endif %}
{% endif %}

{% if diagnostics.gaz %}
### **Contrôle de l'installation de gaz**

{% if diagnostics.gaz.requis %}
Le **BIEN** dispose d'une installation intérieure de gaz de plus de quinze ans.
Le **PROMETTANT** a fait établir un état de celle-ci le {{ diagnostics.gaz.date }}, annexé.
Les conclusions sont les suivantes : ***"{{ diagnostics.gaz.resultat }}"***

**Annexe n°10 : Etat de l'installation intérieure de gaz**
{% else %}
Les parties déclarent que le **BIEN** ne possède pas d'installation intérieure de gaz.
{% endif %}
{% endif %}

{% if diagnostics.electricite %}
### **Contrôle de l'installation intérieure d'électricité**

{% if diagnostics.electricite.requis %}
Le **BIEN** dispose d'une installation intérieure électrique au moins pour partie de plus de quinze ans.
Le **PROMETTANT** a fait établir un état de celle-ci par {{ diagnostics.electricite.diagnostiqueur }} le {{ diagnostics.electricite.date }}, annexé.

**Annexe n°10 : Etat de l'installation intérieure d'électricité**

Les conclusions sont les suivantes : ***"{{ diagnostics.electricite.resultat }}"***
Il est rappelé au **BENEFICIAIRE** qu'en cas d'accidents électriques consécutifs aux anomalies pouvant être révélées par l'état annexé, sa responsabilité pourrait être engagée tant civilement que pénalement.
{% endif %}
{% endif %}

{% if diagnostics.dpe %}
### **Diagnostic de performance énergétique**

Un diagnostic établi par {{ diagnostics.dpe.diagnostiqueur }} le {{ diagnostics.dpe.date }}, est annexé.

**Annexe n°11 : Diagnostic de performances énergétiques**

Les conclusions sont les suivantes :

* Consommation énergétique : **{{ diagnostics.dpe.consommation_energie }} kWhep/m².an (Classe {{ diagnostics.dpe.classe_energie }})**
* Émissions de gaz à effet de serre : **{{ diagnostics.dpe.emission_ges }} kg éqCO2/m².an (Classe {{ diagnostics.dpe.classe_ges }})**
* Numéro d'enregistrement ADEME : {{ diagnostics.dpe.numero_ademe }}
{% endif %}

{% if diagnostics.carnet_logement or diagnostics.carnet_information_logement %}
### **Carnet d'information du logement**

Conformément aux dispositions des articles L 126-35-2 à L 126-35-11 et R 126-32 à R 126-34 du Code de la construction et de l'habitation, le carnet d'information du logement {% if diagnostics.carnet_information_logement and diagnostics.carnet_information_logement.existe %}a été établi et est communiqué{% else %}sera établi et communiqué{% endif %} au **BENEFICIAIRE**.

Le **PROMETTANT** s'engage à transmettre au **BENEFICIAIRE** une copie de ce carnet d'information au plus tard à la date de signature de l'acte authentique de vente.

Le nouveau propriétaire est informé qu'il devra mettre à jour ce carnet en cas d'extension du logement, de travaux d'amélioration ou de modification affectant les parties communes ou privatives.

**Annexe n°13 : Carnet d'information du logement**
{% endif %}

{% if diagnostics.audit_energetique %}
### **Audit énergétique**

Le **BIEN** objet des présentes relevant de la loi n° 65-557 du 10 juillet 1965 fixant le statut de la copropriété des immeubles bâtis, un audit énergétique <<<VAR_START>>>{% if diagnostics.audit_energetique.existe %}a été réalisé{% else %}n'est pas requis{% endif %}<<<VAR_END>>>.

{% if diagnostics.audit_energetique.existe %}
**Annexe n°14 : Audit énergétique**
{% endif %}
{% endif %}

### **Zone de bruit - Plan d'exposition au bruit des aérodromes**

{% if diagnostics.zone_bruit and diagnostics.zone_bruit.concerne %}
Le bien est situé dans le périmètre d'un plan d'exposition au bruit des aérodromes.

**Annexe n°15 : Plan d'exposition au bruit**
{% elif diagnostics.zone_bruit_aeroport and diagnostics.zone_bruit_aeroport.dans_zone %}
Le bien est situé dans le périmètre d'un plan d'exposition au bruit des aérodromes.

**Annexe n°15 : Plan d'exposition au bruit**
{% else %}
Le bien **n'est pas** situé dans le périmètre d'un plan d'exposition au bruit des aérodromes.
{% endif %}

### **Information du bénéficiaire sur les éléments d'équipement**

Le **BENEFICIAIRE** est informé que les désordres affectant les éléments d'équipement qu'ils soient individuels ou communs demeurent soumis aux garanties visées aux articles 1792 et suivants, articles 1646-1 et 1648 al. 1er du Code civil ainsi qu'à l'article L 111-13 du Code de la construction et de l'habitation.

Toutefois, s'agissant des éléments installés en remplacement ou par adjonction à l'existant, cette garantie ne s'applique qu'à ces seuls éléments dont l'installation ou le remplacement sont par ailleurs soumis au régime de garantie décennale de l'article 1792 du Code civil.

La garantie décennale s'applique au professionnel qui a réalisé les travaux d'installation, lequel en garantit le maître d'ouvrage, personne pour le compte de laquelle les travaux sont exécutés (article 1792-1 du Code civil).

Le **PROMETTANT** fournira au **BENEFICIAIRE**, lors de la réitération de la vente, la documentation technique afférente à ces équipements, ainsi que les garanties et assurances y attachées.
{% endif %}

{% if diagnostics.radon %}
### **Radon**

{% if diagnostics.radon.zone == 3 %}
La commune se trouve **en zone 3 (potentiel significatif)**, l'obligation d'information s'impose.
{% else %}
La commune se trouvant **en zone {{ diagnostics.radon.zone }} ({{ diagnostics.radon.zone_libelle }})**, l'obligation d'information n'est pas nécessaire, ainsi qu'il résulte de l'état des risques ci-annexé.
{% endif %}
{% endif %}

{% if diagnostics.assainissement %}
### **Assainissement**

En ce qui concerne l'installation de l'ensemble immobilier dont dépendent les biens objet des présentes :

{% if diagnostics.assainissement.type == "collectif" %}
Le **PROMETTANT** déclare que l'**ENSEMBLE IMMOBILIER** est raccordé à un réseau d'assainissement collectif.

Aux termes des dispositions des articles L 1331-4 et L 1331-6 de ce Code, les parties sont informées des obligations suivantes :

* Les immeubles non raccordés au réseau public de collecte doivent être dotés d'une installation d'assainissement non collectif dont le propriétaire assure l'entretien régulier et qu'il fait périodiquement contrôler par un service public d'assainissement non collectif.
* En cas de vente d'un immeuble non raccordé, le propriétaire doit fournir l'attestation de contrôle de l'installation d'assainissement non collectif.
{% elif diagnostics.assainissement.type == "non_collectif" %}
Le **PROMETTANT** informe le **BENEFICIAIRE** qu'à sa connaissance les ouvrages permettant l'assainissement des eaux usées domestiques sont conformes à la réglementation.

**Annexe n°16 : Diagnostic assainissement non collectif**

Le **PROMETTANT** informe le **BENEFICIAIRE**, qu'à sa connaissance, les ouvrages permettant l'assainissement des eaux usées du bien objet des présentes sont conformes.
{% endif %}
{% endif %}

{% if diagnostics.etat_risques %}
### **Etat des risques**

Un état des risques en date du {{ diagnostics.etat_risques.date }} est annexé.

**Annexe n°12 : Etat des risques**

**{% if diagnostics.etat_risques.sinistres_indemnises %}Existence{% else %}Absence{% endif %} de sinistres avec indemnisation**
Le **PROMETTANT** déclare qu'à sa connaissance l'immeuble {% if diagnostics.etat_risques.sinistres_indemnises %}a{% else %}n'a pas{% endif %} subi de sinistres ayant donné lieu au versement d'une indemnité en application de l'article L 125-2 ou de l'article L 128-2 du Code des assurances.
{% endif %}

# **Situation environnementale**

## **État des Risques et Pollutions (ERP)**

Conformément aux dispositions des articles L. 125-5 et R. 125-23 à R. 125-27 du Code de l'environnement, un État des Risques et Pollutions (ERP) a été établi.

{% if diagnostics.erp %}
**Date d'établissement** : {{ diagnostics.erp.date | default('[Date à compléter]') }}

{% if diagnostics.erp.zone_sismicite %}
**Zone de sismicité** : {{ diagnostics.erp.zone_sismicite }} ({% if diagnostics.erp.zone_sismicite == 1 %}très faible{% elif diagnostics.erp.zone_sismicite == 2 %}faible{% elif diagnostics.erp.zone_sismicite == 3 %}modérée{% elif diagnostics.erp.zone_sismicite == 4 %}moyenne{% elif diagnostics.erp.zone_sismicite == 5 %}forte{% endif %})
{% endif %}

{% if diagnostics.erp.radon %}
**Potentiel radon** : Catégorie {{ diagnostics.erp.radon }} ({% if diagnostics.erp.radon == 1 %}faible{% elif diagnostics.erp.radon == 2 %}moyen{% elif diagnostics.erp.radon == 3 %}significatif{% endif %})
{% endif %}

{% if diagnostics.erp.ppr %}
**Plan de Prévention des Risques (PPR)** : {{ diagnostics.erp.ppr }}
{% else %}
Le bien {% if diagnostics.erp.ppr_applicable %}est{% else %}n'est pas{% endif %} situé dans le périmètre d'un Plan de Prévention des Risques.
{% endif %}

{% if diagnostics.erp.inondation %}
**Risque inondation** : {% if diagnostics.erp.inondation.present %}Zone inondable{% if diagnostics.erp.inondation.type %} - {{ diagnostics.erp.inondation.type }}{% endif %}{% else %}Non concerné{% endif %}
{% endif %}

{% if diagnostics.erp.mouvement_terrain %}
**Risque mouvement de terrain** : {% if diagnostics.erp.mouvement_terrain.present %}Zone à risque{% if diagnostics.erp.mouvement_terrain.type %} - {{ diagnostics.erp.mouvement_terrain.type }}{% endif %}{% else %}Non concerné{% endif %}
{% endif %}

{% if diagnostics.erp.retrait_gonflement_argile %}
**Retrait-gonflement des argiles** : Aléa {% if diagnostics.erp.retrait_gonflement_argile == 1 %}faible{% elif diagnostics.erp.retrait_gonflement_argile == 2 %}moyen{% elif diagnostics.erp.retrait_gonflement_argile == 3 %}fort{% else %}{{ diagnostics.erp.retrait_gonflement_argile }}{% endif %}
{% endif %}

Cet état est valable six mois à compter de sa date d'établissement.
{% else %}
L'État des Risques et Pollutions sera établi préalablement à la réitération des présentes.
{% endif %}

## **Consultation de bases de données environnementales**

Les bases de données suivantes ont été consultées :

* La base de données relative aux anciens sites industriels et activités de service (BASIAS).
* La base de données relative aux sites et sols pollués ou potentiellement pollués appelant une action des pouvoirs publics, à titre préventif ou curatif (BASOL).
* La base de données sur les secteurs d'information sur les sols (SIS).
* Le géoportail de l'urbanisme.
* Géorisques.
* ERRIAL (l'état des risques réglementés pour l'information des acquéreurs et des locataires).

### **Inventaire BASIAS**

{% if situation_environnementale and situation_environnementale.basias %}
{% if situation_environnementale.basias.present %}
Le terrain d'assiette du bien figure dans l'inventaire BASIAS des anciens sites industriels et activités de service.

{% if situation_environnementale.basias.reference %}**Référence BASIAS** : {{ situation_environnementale.basias.reference }}{% endif %}
{% if situation_environnementale.basias.activite %}**Activité recensée** : {{ situation_environnementale.basias.activite }}{% endif %}
{% if situation_environnementale.basias.periode %}**Période d'activité** : {{ situation_environnementale.basias.periode }}{% endif %}
{% if situation_environnementale.basias.commentaire %}{{ situation_environnementale.basias.commentaire }}{% endif %}
{% else %}
Le terrain d'assiette du bien ne figure pas dans l'inventaire BASIAS.
{% endif %}
{% else %}
Le terrain d'assiette du bien ne figure pas dans l'inventaire BASIAS.
{% endif %}

### **Inventaire BASOL**

{% if situation_environnementale and situation_environnementale.basol %}
{% if situation_environnementale.basol.present %}
Le terrain d'assiette du bien figure dans l'inventaire BASOL des sites et sols pollués appelant une action des pouvoirs publics.

{% if situation_environnementale.basol.reference %}**Référence BASOL** : {{ situation_environnementale.basol.reference }}{% endif %}
{% if situation_environnementale.basol.origine %}**Origine de la pollution** : {{ situation_environnementale.basol.origine }}{% endif %}
{% if situation_environnementale.basol.statut %}**Statut du site** : {{ situation_environnementale.basol.statut }}{% endif %}
{% if situation_environnementale.basol.mesures %}**Mesures prises ou à prendre** : {{ situation_environnementale.basol.mesures }}{% endif %}
{% else %}
Le terrain d'assiette du bien ne figure pas dans l'inventaire BASOL.
{% endif %}
{% else %}
Le terrain d'assiette du bien ne figure pas dans l'inventaire BASOL.
{% endif %}

### **Secteur d'Information sur les Sols (SIS)**

{% if situation_environnementale and situation_environnementale.sis %}
{% if situation_environnementale.sis.present %}
Le bien est situé dans un Secteur d'Information sur les Sols (SIS) au sens de l'article L. 125-6 du Code de l'environnement.

{% if situation_environnementale.sis.reference %}**Référence SIS** : {{ situation_environnementale.sis.reference }}{% endif %}
{% if situation_environnementale.sis.description %}**Description** : {{ situation_environnementale.sis.description }}{% endif %}
{% if situation_environnementale.sis.usage_restrictions %}**Restrictions d'usage** : {{ situation_environnementale.sis.usage_restrictions }}{% endif %}

Conformément à la réglementation en vigueur, le **BENEFICIAIRE** a été informé de cette inscription et de ses conséquences éventuelles sur l'usage du bien.
{% else %}
Le bien n'est pas situé dans un Secteur d'Information sur les Sols (SIS).
{% endif %}
{% else %}
Le bien n'est pas situé dans un Secteur d'Information sur les Sols (SIS).
{% endif %}

### **Sites identifiés**

{% if situation_environnementale and situation_environnementale.sites_identifies %}
Les consultations ont révélé {{ situation_environnementale.sites_identifies | length }} site(s) d'activités recensé(s) :

{% for site in situation_environnementale.sites_identifies %}
* **Site {{ loop.index }}** : {{ site.nom }} - Activité: {{ site.activite }} - État: {{ site.etat }}
{% endfor %}
{% else %}
Les consultations n'ont révélé aucun site d'activités recensé à proximité immédiate du bien.
{% endif %}

## **Sinistres avec indemnisation**

{% if situation_environnementale and situation_environnementale.sinistres %}
{% if situation_environnementale.sinistres.declares %}
Le **PROMETTANT** déclare que le bien a fait l'objet d'un ou plusieurs sinistres ayant donné lieu à indemnisation au titre des catastrophes naturelles ou technologiques en application des articles L. 125-5 ou L. 128-2 du Code des assurances :

{% for sinistre in situation_environnementale.sinistres.liste %}
* **{{ sinistre.date }}** : {{ sinistre.type }} {% if sinistre.montant_indemnise %}- Indemnisé : {{ sinistre.montant_indemnise | format_nombre }} EUR{% endif %}
{% endfor %}
{% else %}
Le **PROMETTANT** déclare qu'à sa connaissance, le bien n'a fait l'objet d'aucun sinistre ayant donné lieu à indemnisation au titre des catastrophes naturelles ou technologiques.
{% endif %}
{% else %}
Le **PROMETTANT** déclare qu'à sa connaissance, le bien n'a fait l'objet d'aucun sinistre ayant donné lieu à indemnisation au titre des catastrophes naturelles ou technologiques en application des articles L. 125-5 ou L. 128-2 du Code des assurances.
{% endif %}

Le **BENEFICIAIRE** reconnaît avoir été parfaitement informé de l'ensemble des risques environnementaux et des sinistres éventuellement survenus sur le bien.

# **Règlementations spécifiques à la copropriété**

## **Immatriculation du syndicat des copropriétaires**

Le syndicat des copropriétaires est immatriculé sous le numéro **{{ copropriete.immatriculation }}**.

**Annexe n°14 : Attestation de mise à jour annuelle**

## **Carnet d'entretien de l'ensemble immobilier**

Un carnet d'entretien de l'ensemble immobilier doit être tenu par le syndic.

**Annexe n°15 : Carnet d'entretien**

## **Diagnostic technique global**

Le promettant déclare **{% if copropriete.diagnostic_technique_global %}qu'il existe{% else %}qu'il n'existe pas{% endif %}** de diagnostic technique global.

## **Plan pluriannuel de travaux**

Le promettant déclare **{% if copropriete.plan_pluriannuel_travaux %}qu'il existe{% else %}qu'il n'existe pas{% endif %}** de plan pluriannuel de travaux.

{% if copropriete.fiche_synthetique %}
## **Fiche synthétique**

La fiche synthétique **a été établie** le {{ copropriete.fiche_synthetique.date }} dont une copie est annexée.

**Annexe n°16 : Fiche synthétique**
{% endif %}

{% if copropriete.emprunt_collectif and not copropriete.emprunt_collectif.existe %}
## **Emprunt collectif**

**L'état délivré par le syndic ne révèle pas l'existence d'un emprunt collectif.**
{% endif %}

{% if copropriete.fonds_travaux and copropriete.fonds_travaux.existe %}
## **Fonds de travaux**

**L'immeuble entre dans le champ d'application de l'obligation de créer un fonds de travaux.**
{% endif %}

## **Statut de la copropriété**

### **Syndic de copropriété**

Le syndic est **{{ copropriete.syndic.nom }} – {{ copropriete.syndic.adresse }} – {{ copropriete.syndic.code_postal }} {{ copropriete.syndic.ville }}**

### **Respect du règlement de copropriété**

Le **BENEFICIAIRE** devra respecter les stipulations du règlement de copropriété, de ses modificatifs éventuels visés ci-dessus, ainsi que les dispositions des lois et décrets postérieurs régissant la copropriété.

{% if copropriete.derniere_ag %}
**Assemblée générale**

Date de la dernière assemblée : **{{ copropriete.derniere_ag }}**

Les copies dématérialisées des procès-verbaux des assemblées générales des trois dernières années sont annexées.

**Annexe n°17 : Procès-verbaux des assemblées générales des trois dernières années**
{% endif %}

### **Convention des parties sur les charges de copropriété**

Le **PROMETTANT** paiera au syndic de la copropriété toutes les charges mises en recouvrement par ce dernier au jour de l'entrée en jouissance.
Le **BENEFICIAIRE** supportera les charges de copropriété à compter du jour de l'entrée en jouissance.

### **Convention des parties sur les travaux**

**Le PROMETTANT conservera à sa charge le paiement des travaux votés par l'assemblée des copropriétaires jusqu'à ce jour, que ces travaux soient exécutés ou non, le BENEFICIAIRE supportant seul le coût des travaux qui seront votés postérieurement à ce jour.**

**Annexe n°18 : Pré état-daté**

### **Répartition des budgets de la copropriété**

Les charges de copropriété se répartissent selon les modalités définies dans le règlement de copropriété et ses annexes.

{% if copropriete.budgets %}
Les budgets actuels de la copropriété sont les suivants :

* Budget prévisionnel annuel : <<<VAR_START>>>{{ copropriete.budgets.previsionnel | montant_en_lettres }} euros<<<VAR_END>>>
* Travaux votés non encore appelés : <<<VAR_START>>>{{ copropriete.budgets.travaux_votes | montant_en_lettres }} euros<<<VAR_END>>>
{% endif %}

### **Convention des parties sur les procédures**

Le **BENEFICIAIRE** sera subrogé dans tous les droits et obligations du **PROMETTANT** découlant des procédures en cours impliquant le syndicat des copropriétaires.

{% if copropriete.procedures_en_cours %}
Les procédures suivantes sont en cours :

{% for procedure in copropriete.procedures_en_cours %}
* <<<VAR_START>>>{{ procedure.nature }}<<<VAR_END>>> - Instance: <<<VAR_START>>>{{ procedure.juridiction }}<<<VAR_END>>> - Référence: <<<VAR_START>>>{{ procedure.reference }}<<<VAR_END>>>
{% endfor %}
{% else %}
Aucune procédure en cours n'a été portée à la connaissance du **PROMETTANT**.
{% endif %}

### **Travaux urgents décidés par le syndic (article 18 de la loi du 10 juillet 1965)**

Au cas où, avant la signature de l'acte de vente, le syndic fait procéder de sa propre initiative à des travaux urgents nécessaires à la sauvegarde de l'immeuble, le coût de ces travaux sera supporté selon la répartition prévue par le règlement de copropriété.

### **Convention de règlement entre les parties**

Le **BENEFICIAIRE** versera au **PROMETTANT**, le jour de la constatation authentique de la vente, outre le prix de vente proprement dit, une somme égale au montant des charges de copropriété et de toutes impositions restant dues au jour de la prise de jouissance au prorata des tantièmes de copropriété afférents au bien vendu.

Par suite, les parties conviennent d'effectuer directement entre elles le remboursement des provisions versées au syndic par le **PROMETTANT** pour l'année en cours.

En outre, dans l'hypothèse où l'état du syndic qui sera annexé à l'acte authentique ferait apparaître une dette du **PROMETTANT** envers la copropriété supérieure au montant de la provision à régulariser, le **BENEFICIAIRE** versera le complément directement au syndic.

### **Information financière sur la copropriété**

Les informations financières suivantes sont annexées :

* Le montant des charges courantes du budget prévisionnel et des charges hors budget prévisionnel payées par le **PROMETTANT** au titre des deux exercices comptables précédant la vente.
* Les sommes susceptibles d'être dues au syndicat des copropriétaires par l'acquéreur.
* Les sommes qui resteraient dues par le **PROMETTANT** au syndicat.

{% if copropriete.informations_financieres %}
**Montants déclarés** :

* Charges année N-1 : <<<VAR_START>>>{{ copropriete.informations_financieres.charges_n_1 | montant_en_lettres }} euros<<<VAR_END>>>
* Charges année N-2 : <<<VAR_START>>>{{ copropriete.informations_financieres.charges_n_2 | montant_en_lettres }} euros<<<VAR_END>>>
* Sommes dues par le vendeur : <<<VAR_START>>>{{ copropriete.informations_financieres.sommes_dues | montant_en_lettres }} euros<<<VAR_END>>>
{% endif %}

### **Décomptes et conventions**

Une copie du pré-état délivré par le syndic est annexée aux présentes.

**Annexe n°19 : Pré état-daté (copie)**

Etant précisé que les sommes indiquées dans ledit document le sont sous réserve de l'apurement des comptes de l'exercice en cours et des régularisations à intervenir ultérieurement.

## **Information du bénéficiaire sur sa situation**

En application de l'article 20 II de la loi n° 65-557 du 10 juillet 1965, le **BENEFICIAIRE** déclare, tenant compte de la situation qui sera la sienne à la réalisation de la vente :

{% if beneficiaire_situation and beneficiaire_situation.deja_proprietaire %}
* Il est déjà propriétaire de lots dans l'ensemble immobilier dont il s'agit mais est à jour de ses obligations et n'a pas été mis en demeure de payer par le syndic.
{% else %}
* Il n'est pas déjà propriétaire d'un lot dans l'ensemble immobilier dont il s'agit.
{% endif %}

# **FISCALITE**

## **Régime fiscal de la vente**

Le **PROMETTANT** et le **BENEFICIAIRE** indiquent ne pas agir aux présentes en qualité d'assujettis en tant que tels à la taxe sur la valeur ajoutée au sens de l'article 256 du Code général des impôts.

Les présentes seront soumises au tarif de droit commun en matière immobilière tel que prévu par l'article 1594D du Code général des impôts.

{% if fiscalite and fiscalite.primo_accedant %}
Le **BENEFICIAIRE** :

* reconnait avoir été informé de l'existence de ce régime de faveur et de la définition de la notion de « primo-accédant » au sens de l'article L 31-10-3 du Code de la construction et de l'habitation,
* **déclare entrer dans le cadre d'une première acquisition, telle que définie au I de l'article L 31-10-3 du code précité, destinée à l'usage de sa résidence principale.**

En conséquence, le taux relevé par le conseil départemental ne s'appliquera pas à l'acte authentique de réitération des présentes.
{% endif %}

# **Plus-values**

{% for origine in origine_propriete %}
**Concernant {% if origine.lots_concernes | length > 1 %}les lots numéros {% else %}le lot numéro {% endif %}{{ origine.lots_concernes | join(", ") }}**
{{ origine.origine_immediate.type | capitalize }} suivant acte reçu par {{ origine.origine_immediate.notaire }} le {{ origine.origine_immediate.date }}, publié au service de la publicité foncière de {{ origine.origine_immediate.publication.service }}.

{% endfor %}

{% if fiscalite and fiscalite.plus_value and fiscalite.plus_value.exoneration %}
Le **PROMETTANT** déclare que les présentes portent sur sa résidence principale, c'est-à-dire sa résidence effective et habituelle.
Il s'engage à produire tout élément précis et circonstancié quant à l'effectivité de l'utilisation du **BIEN** comme résidence principale, et ce si l'administration venait à lui demander des éléments de preuve.
Par suite, il bénéficiera de l'exonération de l'impôt sur les plus-values conformément aux dispositions de l'article 150 U II 1° du Code général des impôts.
{% endif %}

# **ABSENCE DE FACULTE DE SUBSTITUTION**

{% if faculte_substitution %}
Le **BENEFICIAIRE** pourra substituer toute personne physique ou morale dans le bénéfice de la présente promesse.
{% else %}
Le **BENEFICIAIRE** ne pourra substituer aucune personne physique ou morale dans le bénéfice de la présente promesse.
{% endif %}

# **Dispositions transitoires**

## **Obligation de garde du promettant**

Entre la date des présentes et la date d'entrée en jouissance du **BENEFICIAIRE**, le **BIEN**, et le cas échéant les **MEUBLES**, tels qu'ils sont sus-désignés demeureront sous la garde et possession du **PROMETTANT** qui s'y oblige.

### **Eléments d'équipement**

Le **PROMETTANT** s'engage à laisser dans le **BIEN** tout ce qui est immeuble par destination ainsi que, sans que cette liste soit limitative et sous la seule réserve que les éléments ci-après désignés existent :

* les plaques de cheminées scellées, les inserts ;
* les supports de tringles à rideau, s'ils sont scellés dans le mur ;
* les trumeaux scellés, les dessus de radiateurs scellés, les moquettes ;
* les poignées de porte telles qu'elles existaient lors de la visite ;
* les pommeaux ou boules d'escalier ;
* les portes, planches et équipements de rangement des placards ;
* les arbres, arbustes, rosiers, plantes et fleurs en terre si jardin privatif ;
* l'équipement sanitaire et l'équipement de chauffage et de conditionnement d'air ;
* les éléments d'éclairage fixés au mur et/ou plafonds, à l'exception des appliques et luminaires ;
* l'équipement électrique ;
* les convecteurs électriques ;
* le câblage et les prises informatiques ;
* tous les carreaux et vitrages sans cassures ni fêlures ;
* les volets, persiennes, stores-bannes et leurs motorisations.

### **Entretien, réparation**

Jusqu'à l'entrée en jouissance du **BENEFICIAIRE**, le **PROMETTANT** s'engage à :

* ne pas apporter de modification quelconque ;
* délivrer le **BIEN** dans son état actuel ;
* conserver ses assurances ;
* maintenir en bon état de fonctionnement les équipements du **BIEN** ;
* laisser les fils électriques d'éclairage suffisamment longs et équipés de leurs douilles et ampoules ou spots ou néons ;
* entretenir le **BIEN** et ses abords ;
* mettre hors-gel les installations en saison froide ;
* réparer les dégâts survenus depuis la visite.

## **Sinistre pendant la durée de validité de la promesse**

Si un sinistre quelconque frappait le **BIEN** durant la durée de validité des présentes, les parties conviennent que le **BENEFICIAIRE** aura la faculté :

* Soit de renoncer purement et simplement à la vente et de se voir immédiatement remboursé de toute somme avancée par lui le cas échéant.
* Soit de maintenir l'acquisition du **BIEN** alors sinistré totalement ou partiellement et de se voir attribuer les indemnités susceptibles d'être versées par la ou les compagnies d'assurances concernées.

# **Condition de survie du bénéficiaire**

{% if condition_survie and condition_survie.applicable %}
Les parties conviennent expressément que la présente promesse de vente comporte une condition de survie du **BENEFICIAIRE** jusqu'à la date de réalisation de la vente.

En conséquence, si le **BENEFICIAIRE** venait à décéder avant la réitération de la vente par acte authentique, la présente promesse deviendrait caduque de plein droit, sans indemnité de part et d'autre.

Dans cette hypothèse :
* L'indemnité d'immobilisation éventuellement versée serait restituée aux ayants droit du **BENEFICIAIRE**.
* Le **PROMETTANT** retrouverait sa pleine et entière liberté de disposer du **BIEN**.

{% if condition_survie.heritiers_substitution %}
Par dérogation à ce qui précède, les parties conviennent que les héritiers du **BENEFICIAIRE** pourront, s'ils le souhaitent, se substituer à ce dernier pour la réalisation de la vente, dans un délai de {{ condition_survie.delai_substitution | default(30) }} jours à compter du décès. Cette faculté devra être exercée par notification au **PROMETTANT** et au notaire rédacteur.
{% endif %}
{% else %}
Les parties conviennent que la présente promesse de vente ne comporte pas de condition de survie. En cas de décès du **BENEFICIAIRE** avant la réitération de la vente, ses héritiers seront tenus de poursuivre l'exécution de la promesse ou d'en subir les conséquences telles que prévues aux présentes.
{% endif %}

# **Conventions particulières – Visites – Information des parties**

{% if conventions_particulieres %}
{% for convention in conventions_particulieres %}
## {{ convention.titre }}

{{ convention.texte }}

{% endfor %}
{% endif %}

## **Visites préalables**

Le **BENEFICIAIRE** déclare avoir visité le **BIEN** préalablement à la signature des présentes et l'avoir trouvé conforme à ses attentes.

{% if visites and visites.nombre > 1 %}
Le **BENEFICIAIRE** déclare avoir effectué {{ visites.nombre | nombre_en_lettres }} ({{ visites.nombre }}) visites du **BIEN**, respectivement les {{ visites.dates | join(', ') }}.
{% endif %}

Le **BENEFICIAIRE** reconnaît avoir été parfaitement informé de l'état du **BIEN**, de ses équipements, de son environnement et de la conformité des installations aux normes en vigueur, dans la limite des informations détenues par le **PROMETTANT** et des diagnostics réalisés.

## **Information sur les diagnostics et risques**

Les parties reconnaissent avoir été parfaitement informées de l'ensemble des dispositions légales applicables à la présente promesse de vente, notamment :

* Les dispositions relatives aux diagnostics techniques obligatoires (DPE, plomb, amiante, termites, gaz, électricité, ERP, etc.).
* Les dispositions relatives à la garantie des vices cachés.
* Les dispositions relatives au droit de rétractation de l'acquéreur non professionnel.
* Les dispositions relatives aux conditions suspensives légales et conventionnelles.

## **Information sur le marché immobilier**

Le **BENEFICIAIRE** reconnaît avoir été informé que le notaire rédacteur ne saurait se porter garant de la valeur vénale du **BIEN**, ni de l'évolution future du marché immobilier. Le prix convenu entre les parties résulte de leur libre négociation.

## **Exclusivité**

{% if exclusivite %}
Le **PROMETTANT** s'engage, pendant toute la durée de validité de la présente promesse, à ne pas :
* Vendre, promettre de vendre ou consentir une quelconque option d'achat sur le **BIEN** à toute autre personne.
* Retirer du marché ou modifier de quelque manière que ce soit les caractéristiques du **BIEN** telles que décrites aux présentes.
{% else %}
La présente promesse ne comporte pas de clause d'exclusivité particulière.
{% endif %}

# **PROVISION SUR LES FRAIS DE LA VENTE**

{% if provision_frais %}
A titre de provision sur frais, le **BENEFICIAIRE** versera **dans les {{ delais.delai_provision_frais_jours | default(15) | nombre_en_lettres | upper }} ({{ delais.delai_provision_frais_jours | default(15) }}) JOURS des présentes** au compte de l'office notarial dénommé en tête des présentes, la somme de **{{ provision_frais | montant_en_lettres }}**.
{% endif %}

# **Paiement sur état - publicité foncière - information**

L'acte est soumis au droit d'enregistrement sur état de CENT VINGT-CINQ EUROS (125,00 EUR).
Le **BENEFICIAIRE** dispense le notaire soussigné de faire publier l'acte au service de la publicité foncière{% if not publication.demandee %}, se contentant de requérir ultérieurement à cette publication, s'il le juge utile, à ses frais{% endif %}.

# **POUVOIRS**

Les parties confèrent à tout clerc ou collaborateur de l'office notarial dénommé en tête des présentes tous pouvoirs nécessaires à l'effet :

* de signer toutes demandes de pièces, demandes de renseignements, et lettres de purge de droit de préemption préalables à la vente ;
* de dresser et signer tous actes qui se révéleraient nécessaires en vue de l'accomplissement des formalités de publicité foncière.

# **ELECTION DE DOMICILE**

Pour l'exécution des présentes, les parties font élection de domicile en leur demeure ou siège social respectif.
En outre, et à défaut d'accord amiable entre les parties, toutes les contestations qui pourront résulter des présentes seront soumises au tribunal judiciaire de la situation du **BIEN**.

# **FACULTE DE RETRACTATION**

En vertu des dispositions de l'article L 271-1 du Code de la construction et de l'habitation, le **BIEN** étant à usage d'habitation et le **BENEFICIAIRE** étant un non-professionnel de l'immobilier, ce dernier bénéficie de la faculté de se rétracter.
A cet effet, une copie du présent acte avec ses annexes lui sera notifiée par lettre recommandée avec accusé de réception. Dans un délai de dix jours à compter du lendemain de la première présentation de la lettre de notification, le **BENEFICIAIRE** pourra exercer la faculté de rétractation, et ce par lettre recommandée avec accusé de réception ou exploit extrajudiciaire, à son choix exclusif.

Il est ici précisé au **BENEFICIAIRE** que :

* Dans l'hypothèse où il exercerait cette faculté de rétractation, celle-ci serait considérée comme définitive.
* Le délai de dix jours pour l'envoi de ce courrier se compte de la manière suivante :
* Le premier jour commence le lendemain de la première présentation du courrier recommandé.
* Le dernier jour est le dixième jour suivant.
* Un jour commence à zéro heure et se termine à vingt-quatre heures.
* Le courrier recommandé de rétraction ou l'acte extrajudiciaire doit être envoyé au plus tard le dernier jour du délai.
* En vertu de l'article 642 du Code de procédure civile, le délai expirant un samedi, un dimanche, un jour férié ou chômé, est prorogé jusqu'au premier jour ouvrable suivant.
* En cas de pluralité de bénéficiaires, il est expressément convenu que la rétractation d'un seul d'entre eux emportera automatiquement résolution des présentes.

# **COMMUNICATION DES PIECES ET DOCUMENTS**

Le **BENEFICIAIRE** pourra prendre connaissance de toutes les pièces et documents ci-dessus mentionnés dans le délai de rétractation auprès du notaire rédacteur des présentes.

## **Notification par envoi électronique**

Le **BENEFICIAIRE** donne son accord pour que toute notification lui soit faite par lettre recommandée par voie électronique permettant d'établir de manière certaine la date de réception.

Il bénéficie en contrepartie de la faculté d'effectuer, dans le cadre des présentes, toute notification par lettre recommandée électronique.

Le **BENEFICIAIRE** reconnait et garantit qu'il dispose de la maîtrise exclusive de la boîte aux lettres électronique dont l'adresse est indiquée ci-après et qu'il s'assurera de consulter régulièrement ladite boîte.

Afin de procéder à l'envoi de documents par lettre recommandée électronique, les parties déclarent élire domicile aux adresses électroniques suivantes :

{% for promettant in promettants %}
* **{{ promettant.civilite }} {{ promettant.nom }}** : <<<VAR_START>>>{{ promettant.coordonnees.courriel }}<<<VAR_END>>>
{% endfor %}

{% for beneficiaire in beneficiaires %}
* **{{ beneficiaire.civilite }} {{ beneficiaire.nom }}** : <<<VAR_START>>>{{ beneficiaire.coordonnees.courriel }}<<<VAR_END>>>
{% endfor %}

# **Envoi electronique**

Chacune des parties donne son accord pour que l'envoi d'une lettre recommandée, lorsque la loi permet une telle modalité d'envoi, soit réalisé par lettre recommandée électronique selon le dispositif légal de l'article L. 100 du Code des postes et des communications électroniques.

Elle reconnait et garantit qu'elle dispose de la maîtrise exclusive de la boîte aux lettres électronique dont l'adresse est indiquée ci-après et qu'elle s'assurera de consulter régulièrement.

Il est précisé que le prestataire chargé de la remise est AR24. Ce prestataire est soumis aux dispositions des articles L. 100 et R. 53-1 à R. 53-3 du Code des postes et des communications électroniques.

Chacune des parties déclare faire élection de domicile électronique à l'adresse déjà mentionnée ci-dessus.

# **ADRESSES electroniqueS**

Afin de procéder à l'envoi de documents par voie électronique, les parties confirment les adresses électroniques suivantes :

{% for promettant in promettants %}
* **{{ promettant.civilite }} {{ promettant.nom }}** : <<<VAR_START>>>{{ promettant.coordonnees.courriel }}<<<VAR_END>>>
{% endfor %}

{% for beneficiaire in beneficiaires %}
* **{{ beneficiaire.civilite }} {{ beneficiaire.nom }}** : <<<VAR_START>>>{{ beneficiaire.coordonnees.courriel }}<<<VAR_END>>>
{% endfor %}

# **NOTIFICATIONS – POUVOIRS RECIPROQUES**

Les bénéficiaires se donnent pouvoir réciproquement et à l'effet de signer tout avenant ou rectification au présent contrat que les circonstances ultérieures pourraient rendre nécessaire.

# **Médiation**

Les parties sont informées qu'en cas de litige entre elles ou avec un tiers, elles pourront, préalablement à toute instance judiciaire, le soumettre à un médiateur qui sera désigné et missionné par le Centre de médiation notariale.

# **Affirmation de sincérité**

Les parties affirment, sous les peines édictées par l'article 1837 du Code général des impôts, que le présent acte exprime l'intégralité du prix ; elles reconnaissent avoir été informées par le rédacteur des présentes des sanctions fiscales et des peines correctionnelles encourues en cas d'inexactitude de cette affirmation.

# **Renonciation à l'imprévision**

Les parties écartent de leur contrat les dispositions de l'article 1195 du Code civil permettant la révision du contrat pour imprévision.

# **Mention sur la protection des données personnelles**

L'Office notarial traite des données personnelles concernant les personnes mentionnées aux présentes, pour l'accomplissement des activités notariales, notamment de formalités d'actes.

# **Certification d'identité**

Le notaire soussigné certifie que l'identité complète des parties dénommées dans le présent document telle qu'elle est indiquée en tête des présentes à la suite de leur nom ou dénomination lui a été régulièrement justifiée.

# **LISTE DES ANNEXES**

Les annexes suivantes font partie intégrante de la présente promesse de vente :

| N° | Désignation | Obligatoire | Observations |
| :---: | :---- | :---: | :---- |
| 1 | Plans cadastral et géoportail | Oui | Identification du bien |
| 2 | Plans des lots et plan de masse | Oui | Description des lots |
| 3 | Attestation de mesurage Carrez | Oui | Article 46 loi du 10 juillet 1965 |
{% if diagnostics.dpe %}| 4 | Diagnostic de performance énergétique (DPE) | Oui | Classe {{ diagnostics.dpe.classe_energie | default('NC') }} |{% endif %}
{% if diagnostics.erp or diagnostics.etat_risques %}| 5 | État des risques et pollutions (ERP) | Oui | Article L. 125-5 Code environnement |{% endif %}
{% if diagnostics.plomb %}| 6 | Constat de risque d'exposition au plomb (CREP) | {% if diagnostics.plomb.requis %}Oui{% else %}Non{% endif %} | Immeuble construit avant 1949 |{% endif %}
{% if diagnostics.amiante_parties_privatives %}| 7 | Diagnostic amiante parties privatives | {% if diagnostics.amiante_parties_privatives.requis %}Oui{% else %}Non{% endif %} | Permis de construire avant 01/07/1997 |{% endif %}
{% if diagnostics.amiante_parties_communes %}| 8 | Diagnostic amiante parties communes | {% if diagnostics.amiante_parties_communes.requis %}Oui{% else %}Non{% endif %} | DTA copropriété |{% endif %}
{% if diagnostics.termites %}| 9 | État relatif aux termites | {% if diagnostics.termites.requis %}Oui{% else %}Non{% endif %} | Zone de protection |{% endif %}
{% if diagnostics.gaz %}| 10 | État de l'installation intérieure de gaz | {% if diagnostics.gaz.requis %}Oui{% else %}Non{% endif %} | Installation > 15 ans |{% endif %}
{% if diagnostics.electricite %}| 11 | État de l'installation intérieure d'électricité | {% if diagnostics.electricite.requis %}Oui{% else %}Non{% endif %} | Installation > 15 ans |{% endif %}
{% if diagnostics.assainissement %}| 12 | Diagnostic assainissement | {% if diagnostics.assainissement.requis %}Oui{% else %}Non{% endif %} | Assainissement non collectif |{% endif %}
{% if diagnostics.audit_energetique and diagnostics.audit_energetique.requis %}| 13 | Audit énergétique | Oui | Classe F ou G |{% endif %}
{% if diagnostics.zone_bruit_aeroport and diagnostics.zone_bruit_aeroport.dans_zone %}| 14 | Plan d'exposition au bruit des aérodromes | Oui | Zone concernée |{% endif %}
{% if diagnostics.carnet_information_logement and diagnostics.carnet_information_logement.existe %}| 15 | Carnet d'information du logement | Non | Remis si existant |{% endif %}
| 16 | Note d'urbanisme | Oui | Situation du bien |
| 17 | Note de voirie | Oui | Desserte et accès |
{% if urbanisme.certificat_non_peril %}| 18 | Certificat de non-péril | Oui | État de l'immeuble |{% endif %}
| 19 | Règlement de copropriété et ses modificatifs | Oui | Applicable au bien |
| 20 | État descriptif de division | Oui | Identification des lots |
{% if copropriete.immatriculation %}| 21 | Attestation d'immatriculation au RNC | Oui | N° {{ copropriete.immatriculation }} |{% endif %}
{% if copropriete.carnet_entretien %}| 22 | Carnet d'entretien de l'immeuble | Oui | Article L. 721-2 CCH |{% endif %}
{% if copropriete.fiche_synthetique %}| 23 | Fiche synthétique de la copropriété | Oui | Article L. 711-2 CCH |{% endif %}
{% if copropriete.derniere_ag %}| 24 | Procès-verbaux des AG (3 dernières années) | Oui | Information acquéreur |{% endif %}
| 25 | Pré état-daté | Oui | Article 10-1 loi du 10 juillet 1965 |
{% if copropriete.diagnostic_technique_global and copropriete.diagnostic_technique_global.existe %}| 26 | Diagnostic technique global (DTG) | Oui | Article L. 731-1 CCH |{% endif %}
{% if copropriete.plan_pluriannuel_travaux and copropriete.plan_pluriannuel_travaux.existe %}| 27 | Plan pluriannuel de travaux (PPT) | Oui | Si adopté |{% endif %}
{% if travaux and travaux.travaux_realises %}| 28 | Factures et attestations décennales | Oui | Travaux des 10 dernières années |{% endif %}
{% if negociation and negociation.avec_agent %}| 29 | Mandat de négociation | Oui | Agent immobilier |{% endif %}
{% if conditions_suspensives and conditions_suspensives.pret and conditions_suspensives.pret.applicable %}| 30 | Justificatifs de financement prévisionnel | Non | Information préalable |{% endif %}

{% if annexes_supplementaires %}
**Annexes complémentaires :**
{% for annexe in annexes_supplementaires %}
| {{ annexe.numero }} | {{ annexe.designation }} | {{ "Oui" if annexe.obligatoire else "Non" }} | {{ annexe.observations | default('') }} |
{% endfor %}
{% endif %}

Le **BENEFICIAIRE** reconnaît avoir reçu l'ensemble des documents et annexes ci-dessus listés préalablement à la signature des présentes. Ces documents lui ont été remis ou mis à disposition sur l'espace sécurisé mis à sa disposition par l'office notarial.

# **Formalisme lié aux annexes**

Les annexes, s'il en existe, font partie intégrante de la minute.
Si l'acte est établi sur support électronique, la signature du notaire en fin d'acte vaut également pour ses annexes.

**DONT ACTE sans renvoi**
Généré en l'office notarial et visualisé sur support électronique aux lieu, jour, mois et an indiqués en en-tête du présent acte.
Et lecture faite, les parties ont certifié exactes les déclarations les concernant, avant d'apposer leur signature manuscrite sur tablette numérique.

Le notaire, qui a recueilli l'image de leur signature, a lui-même apposé sa signature manuscrite, puis signé l'acte au moyen d'un procédé de signature électronique qualifié.
