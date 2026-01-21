{# ============================================================================
   TEMPLATE: ACTE DE VENTE - LOTS DE COPROPRIÉTÉ
   Version: 1.2.0
   Description: Template Jinja2 pour la génération d'actes de vente de lots
                de copropriété. Préserve la syntaxe juridique exacte.
   Format: Conforme au format notarial standard (Word original)
   Note: Utilise HTML pour le positionnement précis (indentations, centrage)
   ============================================================================ #}
<div class="header-ref">
{{ acte.numero_repertoire }}<br/>
{{ acte.reference_interne }}
</div>

<div class="header-titre">
<strong>{{ acte.date.en_lettres | capitalize }}</strong><br/>
<strong>VENTE</strong><br/>
<strong>Par {% for v in vendeurs %}{{ v.civilite }} {{ v.nom }}{% if not loop.last %} et {% endif %}{% endfor %}</strong><br/>
<strong>Au profit de {% for a in acquereurs %}{{ a.civilite }} {{ a.nom }}{% if not loop.last %} et {% endif %}{% endfor %}</strong><br/>
<strong>***************************************************************</strong>
</div>

<div class="header-notaire">
<strong>L'AN {{ acte.date.annee_lettres|upper }},</strong><br/>
<strong>LE {{ acte.date.jour_mois_lettres|upper }}</strong><br/>
<strong>A {{ acte.notaire.ville|upper }} ({{ acte.notaire.departement }}), {{ acte.notaire.adresse }}, au siège de l'Office Notarial, ci-après nommé,</strong><br/>
<strong>{{ acte.notaire.civilite }} {{ acte.notaire.prenom }} {{ acte.notaire.nom|upper }}, Notaire de la société par actions simplifiée dénommée « <u>{{ acte.notaire.societe }}</u> » dont le siège social est situé à {{ acte.notaire.ville|upper }} ({{ acte.notaire.departement }}), {{ acte.notaire.adresse }},</strong> <strong>identifié sous le numéro CRPCEN {{ acte.notaire.crpcen }},</strong>
</div>

{% if acte.notaire_assistant %}
<div class="header-notaire">
<strong>Avec la participation de {{ acte.notaire_assistant.civilite }} {{ acte.notaire_assistant.prenom }} {{ acte.notaire_assistant.nom|upper }}, notaire à {{ acte.notaire_assistant.ville }}, assistant l'ACQUEREUR,</strong>
</div>
{% endif %}

<div class="header-notaire">
<strong>A REÇU LA <u>PRESENTE</u> VENTE à la requête des parties ci-après identifiées.</strong>
</div>

Cet acte comprend deux parties pour répondre aux exigences de la publicité foncière, néanmoins l'ensemble de l'acte et de ses annexes forme un contrat indissociable et unique.
**La première partie dite "partie normalisée"** constitue le document hypothécaire normalisé et contient toutes les énonciations nécessaires tant à la publication au fichier immobilier qu'à la détermination de l'assiette et au contrôle du calcul de tous impôts, droits et taxes.
**La seconde partie dite "partie développée"** comporte des informations, dispositions et conventions sans incidence sur le fichier immobilier.

# PARTIE NORMALISEE

# IDENTIFICATION DES PARTIES

#### VENDEUR

{% for vendeur in vendeurs %}
<div class="personne">
{{ vendeur.civilite }} {{ vendeur.prenoms }} {{ vendeur.nom }}{% if vendeur.nom_naissance %} née {{ vendeur.nom_naissance }}{% endif %}, {{ vendeur.profession }}, demeurant à {{ vendeur.adresse }} {{ vendeur.code_postal }} {{ vendeur.ville }}<br/>
{{ "Née" if vendeur.civilite == "Madame" else "Né" }} à {{ vendeur.lieu_naissance }} le {{ vendeur.date_naissance | format_date }}.<br/>
{% if vendeur.situation_matrimoniale.statut == "celibataire" -%}
Célibataire.<br/>
Non {{ "liée" if vendeur.civilite == "Madame" else "lié" }} par un pacte civil de solidarité.<br/>
{% elif vendeur.situation_matrimoniale.statut == "marie" -%}
{{ "Mariée" if vendeur.civilite == "Madame" else "Marié" }} avec {{ vendeur.situation_matrimoniale.conjoint.civilite }} {{ vendeur.situation_matrimoniale.conjoint.prenoms }} {{ vendeur.situation_matrimoniale.conjoint.nom }} sous le régime de {{ vendeur.situation_matrimoniale.regime_matrimonial_libelle }} aux termes du contrat de mariage reçu par {{ vendeur.situation_matrimoniale.contrat_mariage.notaire }}, notaire à {{ vendeur.situation_matrimoniale.contrat_mariage.lieu }}, le {{ vendeur.situation_matrimoniale.contrat_mariage.date | format_date }}.<br/>
Ce régime matrimonial n'a pas fait l'objet de modification.<br/>
{% elif vendeur.situation_matrimoniale.statut == "pacse" -%}
{{ "Liée" if vendeur.civilite == "Madame" else "Lié" }} par un pacte civil de solidarité avec {{ vendeur.situation_matrimoniale.conjoint.civilite }} {{ vendeur.situation_matrimoniale.conjoint.prenoms }} {{ vendeur.situation_matrimoniale.conjoint.nom }} sous le régime de {{ vendeur.situation_matrimoniale.pacs.regime_libelle }}, enregistré {{ vendeur.situation_matrimoniale.pacs.lieu_enregistrement }} le {{ vendeur.situation_matrimoniale.pacs.date | format_date }}.<br/>
Contrat non modifié depuis lors.<br/>
{% elif vendeur.situation_matrimoniale.statut == "divorce" -%}
{{ "Divorcée" if vendeur.civilite == "Madame" else "Divorcé" }} de {{ vendeur.situation_matrimoniale.ex_conjoint.civilite }} {{ vendeur.situation_matrimoniale.ex_conjoint.nom }} suivant jugement rendu par le tribunal judiciaire de {{ vendeur.situation_matrimoniale.jugement_divorce.lieu }} le {{ vendeur.situation_matrimoniale.jugement_divorce.date | format_date }}, et non {{ "remariée" if vendeur.civilite == "Madame" else "remarié" }}.<br/>
Non {{ "liée" if vendeur.civilite == "Madame" else "lié" }} par un pacte civil de solidarité.<br/>
{% elif vendeur.situation_matrimoniale.statut == "veuf" -%}
{{ "Veuve" if vendeur.civilite == "Madame" else "Veuf" }} de {{ vendeur.situation_matrimoniale.defunt_conjoint.civilite }} {{ vendeur.situation_matrimoniale.defunt_conjoint.nom }}.<br/>
Non {{ "remariée" if vendeur.civilite == "Madame" else "remarié" }}.<br/>
Non {{ "liée" if vendeur.civilite == "Madame" else "lié" }} par un pacte civil de solidarité.<br/>
{% endif -%}
De nationalité {{ vendeur.nationalite }}.<br/>
{{ "Résidente" if vendeur.civilite == "Madame" else "Résident" }} au sens de la réglementation fiscale.
</div>

{% endfor %}

#### ACQUEREUR

{% for acquereur in acquereurs %}
<div class="personne">
{{ acquereur.civilite }} {{ acquereur.prenoms }} {{ acquereur.nom }}{% if acquereur.nom_naissance %} née {{ acquereur.nom_naissance }}{% endif %}, {{ acquereur.profession }}, demeurant à {{ acquereur.adresse }} {{ acquereur.code_postal }} {{ acquereur.ville }}<br/>
{{ "Née" if acquereur.civilite == "Madame" else "Né" }} à {{ acquereur.lieu_naissance }} le {{ acquereur.date_naissance | format_date }}.<br/>
{% if acquereur.situation_matrimoniale.statut == "celibataire" -%}
Célibataire.<br/>
Non {{ "liée" if acquereur.civilite == "Madame" else "lié" }} par un pacte civil de solidarité.<br/>
{% elif acquereur.situation_matrimoniale.statut == "marie" -%}
{{ "Mariée" if acquereur.civilite == "Madame" else "Marié" }} avec {{ acquereur.situation_matrimoniale.conjoint.civilite }} {{ acquereur.situation_matrimoniale.conjoint.prenoms }} {{ acquereur.situation_matrimoniale.conjoint.nom }} sous le régime de {{ acquereur.situation_matrimoniale.regime_matrimonial_libelle }} aux termes du contrat de mariage reçu par {{ acquereur.situation_matrimoniale.contrat_mariage.notaire }}, notaire à {{ acquereur.situation_matrimoniale.contrat_mariage.lieu }}, le {{ acquereur.situation_matrimoniale.contrat_mariage.date | format_date }}.<br/>
Ce régime matrimonial n'a pas fait l'objet de modification.<br/>
{% elif acquereur.situation_matrimoniale.statut == "pacse" -%}
{{ "Liée" if acquereur.civilite == "Madame" else "Lié" }} par un pacte civil de solidarité avec {{ acquereur.situation_matrimoniale.conjoint.civilite }} {{ acquereur.situation_matrimoniale.conjoint.prenoms }} {{ acquereur.situation_matrimoniale.conjoint.nom }} sous le régime de {{ acquereur.situation_matrimoniale.pacs.regime_libelle }}, enregistré {{ acquereur.situation_matrimoniale.pacs.lieu_enregistrement }} le {{ acquereur.situation_matrimoniale.pacs.date | format_date }}.<br/>
Contrat non modifié depuis lors.<br/>
{% elif acquereur.situation_matrimoniale.statut == "divorce" -%}
{{ "Divorcée" if acquereur.civilite == "Madame" else "Divorcé" }} de {{ acquereur.situation_matrimoniale.ex_conjoint.civilite }} {{ acquereur.situation_matrimoniale.ex_conjoint.nom }} suivant jugement rendu par le tribunal judiciaire de {{ acquereur.situation_matrimoniale.jugement_divorce.lieu }} le {{ acquereur.situation_matrimoniale.jugement_divorce.date | format_date }}, et non {{ "remariée" if acquereur.civilite == "Madame" else "remarié" }}.<br/>
Non {{ "liée" if acquereur.civilite == "Madame" else "lié" }} par un pacte civil de solidarité.<br/>
{% elif acquereur.situation_matrimoniale.statut == "veuf" -%}
{{ "Veuve" if acquereur.civilite == "Madame" else "Veuf" }} de {{ acquereur.situation_matrimoniale.defunt_conjoint.civilite }} {{ acquereur.situation_matrimoniale.defunt_conjoint.nom }}.<br/>
Non {{ "remariée" if acquereur.civilite == "Madame" else "remarié" }}.<br/>
Non {{ "liée" if acquereur.civilite == "Madame" else "lié" }} par un pacte civil de solidarité.<br/>
{% endif -%}
De nationalité {{ acquereur.nationalite }}.<br/>
{{ "Résidente" if acquereur.civilite == "Madame" else "Résident" }} au sens de la réglementation fiscale.
</div>

{% endfor %}

# QUOTITÉS VENDUES

{% for quotite in quotites_vendues %}
{{ vendeurs[quotite.personne_index].civilite }} {{ vendeurs[quotite.personne_index].prenoms }} {{ vendeurs[quotite.personne_index].nom }} {{ quotite.type_propriete_libelle }} des **BIENS** objet de la vente à concurrence de **{{ quotite.quotite }}.**
{% endfor %}

# QUOTITÉS ACQUISES

{% for quotite in quotites_acquises %}
{{ acquereurs[quotite.personne_index].civilite }} {{ acquereurs[quotite.personne_index].prenoms }} {{ acquereurs[quotite.personne_index].nom }} acquiert {{ quotite.type_propriete_libelle }} des **BIENS** objet de la vente à concurrence de **{{ quotite.quotite }}.**
{% endfor %}

# PRÉSENCE - REPRÉSENTATION

{% for vendeur in vendeurs %}
\- {{ vendeur.civilite }} {{ vendeur.prenoms }} {{ vendeur.nom }} est {{ "présente" if vendeur.civilite == "Madame" else "présent" }} à l'acte.
{% endfor %}
{% for acquereur in acquereurs %}
\- {{ acquereur.civilite }} {{ acquereur.prenoms }} {{ acquereur.nom }} est {{ "présente" if acquereur.civilite == "Madame" else "présent" }} à l'acte.
{% endfor %}

# DÉCLARATIONS DES PARTIES SUR LEUR CAPACITÉ

Les parties, et le cas échéant leurs représentants, attestent que rien ne peut limiter leur capacité pour l'exécution des engagements qu'elles prennent aux présentes, et elles déclarent notamment :

* que leur état civil et leurs qualités indiqués en tête des présentes sont exacts,

* qu'elles ne sont pas en état de cessation de paiement, de rétablissement professionnel, de redressement ou liquidation judiciaire ou sous procédure de sauvegarde des entreprises,

* qu'elles n'ont pas été associées dans une société mise en liquidation judiciaire suivant jugement publié depuis moins de cinq ans et dans laquelle elles étaient tenues indéfiniment et solidairement ou seulement conjointement du passif social, le délai de cinq ans marquant la prescription des actions de droit commun et de celle en recouvrement à l'endroit des associés (BOI-REC-SOLID-20-10-20),

* qu'il n'a été formé aucune opposition au présent acte par un éventuel cogérant,

* qu'elles ne sont concernées :

* par aucune des mesures légales relatives aux personnes protégées qui ne seraient pas révélées aux présentes,

* par aucune des dispositions du Code de la consommation sur le règlement des situations de surendettement, sauf là aussi ce qui peut être spécifié aux présentes,

* et pour l'acquéreur spécialement qu'il n'est, ni à titre personnel, ni en tant qu'associé ou mandataire social, soumis à l'interdiction d'acquérir prévue par l'article 225-26 du Code pénal.

# DOCUMENTS RELATIFS À LA CAPACITÉ ET À LA QUALITÉ DES PARTIES

Les pièces suivantes ont été produites à l'appui des déclarations des parties sur leur capacité :

{% for vendeur in vendeurs %}
**Concernant {{ vendeur.civilite }} {{ vendeur.prenoms }} {{ vendeur.nom }}**

* Extrait d'acte de naissance.

* Carte nationale d'identité.

* Compte rendu de l'interrogation du site bodacc.fr.

* Compte rendu de la consultation du Registre national des gels des avoirs

* Compte rendu de consultation de la base DOWJONES.

{% endfor %}
{% for acquereur in acquereurs %}
**Concernant {{ acquereur.civilite }} {{ acquereur.prenoms }} {{ acquereur.nom }}**

* Extrait d'acte de naissance.

* Carte nationale d'identité.

* Compte rendu de l'interrogation du site bodacc.fr.

* Compte rendu de la consultation du Registre national des gels des avoirs

* Compte rendu de consultation de la base DOWJONES.

{% endfor %}

Ces documents ne révèlent aucun empêchement des parties à la signature des présentes.

# TERMINOLOGIE

Le vocable employé au présent acte est le suivant :

* Le mot "**VENDEUR**" désigne le ou les vendeurs, présents ou représentés. En cas de pluralité, les vendeurs contracteront les obligations mises à leur charge aux termes des présentes solidairement entre eux, sans que cette solidarité soit nécessairement rappelée à chaque fois.

* Le mot "**ACQUEREUR**" désigne le ou les acquéreurs, présents ou représentés. En cas de pluralité, les acquéreurs contracteront les obligations mises à leur charge aux termes des présentes solidairement entre eux, sans que cette solidarité soit nécessairement rappelée à chaque fois.

* Les mots "**LES PARTIES**" désignent ensemble le **VENDEUR** et l'**ACQUEREUR**.

* Le mot "**ENSEMBLE IMMOBILIER**" désigne l'immeuble dont dépendent les **BIENS** objet des présentes.

* Les mots "**BIENS**" ou "**BIEN**" ou "**LOTS**" désigneront indifféremment le ou les lots de copropriété objet des présentes.

* Les mots "**biens mobiliers**" ou "**mobilier**", désigneront indifféremment, s'il en existe, les meubles et objets mobiliers se trouvant dans le ou les lots de copropriété et vendus avec ceux-ci.

* Le mot "annexe" désigne tout document annexé. Les annexes forment un tout indissociable avec l'acte. Il est précisé que les pièces mentionnées comme étant annexées sont des copies numérisées.

**CECI EXPOSE, il est passé à la vente objet des présentes.**

# NATURE ET QUOTITÉ DES DROITS IMMOBILIERS

Le **VENDEUR** vend pour sa totalité en pleine propriété à l'**ACQUEREUR**, qui accepte, le **BIEN** dont la désignation suit.

# IDENTIFICATION DU BIEN

**Désignation**

**Dans un ensemble immobilier situé à {{ bien.adresse.ville|upper }} ({{ bien.adresse.departement|upper }}) ({{ bien.adresse.code_postal }}) {{ bien.adresse.numero }} {{ bien.adresse.voie }}.**
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

La parcelle, sise sur la commune de {{ bien.adresse.ville|upper }} ({{ bien.adresse.code_postal }}), originairement cadastrée section {{ bien.division_cadastrale.parcelle_origine }} a fait l'objet d'une division en plusieurs parcelles de moindre importance.
De cette division sont issues les parcelles cadastrées section {{ bien.division_cadastrale.parcelles_issues|join(' et ') }}.
Le document modificatif du parcellaire cadastral, créant cette division, a fait l'objet d'une publication au service de la publicité foncière de {{ bien.division_cadastrale.service_publication }}, le {{ bien.division_cadastrale.date_publication }}, volume {{ bien.division_cadastrale.volume }}, numéro {{ bien.division_cadastrale.numero }}.
{% endif %}

**Les lots de copropriété suivants :**

{% for lot in bien.lots %}
**Lot numéro {{ lot.numero_lettres }} ({{ lot.numero }})**
{% if lot.type == "appartement" %}
Soit, un appartement de type "{{ lot.type_appartement }}", situé au {{ lot.etage }}, escalier {{ lot.escalier }}, {{ lot.orientation }}, comprenant: {{ lot.description }}.
{% elif lot.type == "cave" %}
Soit une cave, située au {{ lot.etage }}, escalier {{ lot.escalier }}, portant le numéro {{ lot.numero_cave }}.
{% elif lot.type == "parking" %}
Un emplacement de parking privé portant le numéro {{ lot.numero_parking }} au plan de masse.
{% else %}
{{ lot.description }}
{% endif %}
Et les {{ lot.tantiemes.valeur_lettres }} ({{ lot.tantiemes.valeur }} /{{ lot.tantiemes.base }} {{ lot.tantiemes.base_unite }}) des {{ lot.tantiemes.type }}.

{% endfor %}

Tel que le **BIEN** existe, avec tous droits y attachés, sans aucune exception ni réserve.

**Plans des lots**

Demeurent annexées aux présentes :
{% for lot in bien.lots %}
\- Une copie du plan {% if lot.type == "appartement" %}de l'étage courant{% elif lot.type == "cave" %}des sous-sols{% elif lot.type == "parking" %}de masse{% endif %} faisant apparaître le lot {{ lot.type }} numéro {{ lot.numero_lettres|upper }} ({{ lot.numero }}){% if lot.observations_plan %} ; {{ lot.observations_plan }}{% endif %}
{% endfor %}

**Annexe n°2 : Plans des lots et plan de masse**

## DÉCLARATION DÉSIGNATION – ENVIRONNEMENT DU BIEN - VOISINAGE

Les parties déclarent que la description du **BIEN** telle qu'elle vient d'être indiquée correspond précisément à celle actuelle.
Etant ici précisé que la désignation des lieux correspond à la déclaration faite par les parties et n'a, à aucun moment, été vérifiée par le notaire soussigné, qui ne peut être tenu responsable d'une inexactitude dans les caractéristiques et éléments déclarés.

L'**ACQUEREUR** déclare avoir visité les lieux préalablement à la signature de l'avant contrat et aux présentes et, accepte expressément la désignation telle qu'elle figure ci-dessus.
L'**ACQUEREUR** déclare avoir été informé de la nécessité de s'informer préalablement à la signature de l'avant contrat sur la situation, le voisinage et l'environnement du **BIEN** et, sur toutes éventuelles modifications à venir de l'environnement du **BIEN**.
L'**ACQUEREUR** déclare être informé que les démarches effectuées par le Notaire soussigné ne portent que le **BIEN** objet des présentes et non sur son environnement.
L'**ACQUEREUR** déclare s'être renseigné préalablement sur la situation et l'environnement de ce **BIEN**.

## Mention de la superficie de la partie privative – Application

La superficie de la partie privative des lots de copropriété soumis aux dispositions de l'article 46 de la loi du 10 juillet 1965, est de **{{ bien.superficie_carrez.superficie_m2 }} M²** pour le lot numéro {{ bien.superficie_carrez.lot_concerne|upper }}.
Le tout ainsi qu'il est développé ci-après.

## État descriptif de division – Règlement de copropriété

L'ensemble immobilier sus désigné a fait l'objet d'un état descriptif de division et règlement de copropriété établi aux termes d'un acte reçu par {{ copropriete.reglement.notaire_origine }}, le {{ copropriete.reglement.date_origine }} publié au service de la publicité foncière de {{ copropriete.reglement.publication }}.

{% for modificatif in copropriete.reglement.modificatifs %}
L'état descriptif de division \- règlement de copropriété a été modifié aux termes d'un acte reçu par {{ modificatif.notaire }}, le {{ modificatif.date | format_date }}, publié au service de la publicité foncière de {{ modificatif.publication }}.
{% endfor %}

<!-- SECTION: meubles_mobilier | CONDITIONNEL: meubles.inclus == true -->
{% if meubles.inclus %}
# IDENTIFICATION DES MEUBLES

Le **VENDEUR** vend à l'**ACQUEREUR**, qui accepte, les meubles ci-après {% if not meubles.valeur %}non valorisés {% endif %}dont la liste, établie contradictoirement entre eux, est la suivante :

{% for meuble in meubles.liste %}
- {{ meuble }}
{% endfor %}
{% endif %}

## EQUIPEMENTS

Le **VENDEUR** informe l'**ACQUEREUR** de l'existence des équipements, dont la liste figure en partie développée.

# USAGE DU BIEN

Le **VENDEUR** déclare que le **BIEN** est actuellement à usage {{ bien.usage_actuel_libelle }}.
L'**ACQUEREUR** entend {% if bien.usage_futur == "inchange" %}conserver cet usage{% else %}le destiner à un usage {{ bien.usage_futur_libelle }}{% endif %}.

# EFFETS RELATIFS

{% for origine in origine_propriete %}
**Concernant {{ "le lot numéro" if origine.lots_concernes|length == 1 else "les lots numéros" }} {{ origine.lots_concernes|join(' et ') }}**
{{ origine.origine_immediate.type_libelle }} suivant acte reçu par {{ origine.origine_immediate.notaire }}, le {{ origine.origine_immediate.date | format_date }}, publié au service de la publicité foncière de {{ origine.origine_immediate.publication.service }} le {{ origine.origine_immediate.publication.date | format_date }}, volume {{ origine.origine_immediate.publication.volume }}, numéro {{ origine.origine_immediate.publication.numero }}.

{% endfor %}

# CHARGES ET CONDITIONS LIEES AU CALCUL DE L'IMPOT

Les charges et conditions ne donnant pas lieu à taxation figurent en partie développée de l'acte.

Les frais de la vente et ceux qui en seront la suite et la conséquence sont à la charge exclusive de l'**ACQUEREUR** qui s'y oblige.

# PROPRIÉTÉ JOUISSANCE

L'**ACQUEREUR** est propriétaire du **BIEN** à compter de ce jour.
{% if jouissance.jouissance_anticipee %}
L'entrée en jouissance a eu lieu par la prise de possession réelle le {{ jouissance.date_jouissance | format_date }} ainsi qu'il résulte d'une convention d'entrée en jouissance anticipée en date du {{ jouissance.convention_occupation.date | format_date }}, dont une copie demeure jointe et annexée après mention.

**Annexe 2 bis : Convention d'occupation précaire**
{% else %}
L'entrée en jouissance aura lieu ce jour par la prise de possession réelle.
{% endif %}

# PRIX

La vente est conclue moyennant le prix de **{{ prix.montant_lettres|upper }} ({{ prix.montant|format_nombre }} {{ prix.devise }})**.
Le paiement de ce prix a lieu de la manière indiquée ci-après.

# PAIEMENT DU PRIX

L'**ACQUEREUR** a payé le prix comptant ce jour ainsi qu'il résulte de la comptabilité de l'office notarial dénommé en tête des présentes au **VENDEUR**, qui le reconnaît et lui en consent quittance sans réserve.
**DONT QUITTANCE**

{% if paiement.fonds_empruntes > 0 %}
# DECLARATION D'ORIGINE DES FONDS

L'**ACQUEREUR** déclare que sur la somme ci-dessus payée, celle de **{{ paiement.fonds_empruntes_lettres|upper }} ({{ paiement.fonds_empruntes|format_nombre }} {{ prix.devise }})** provient de fonds empruntés à cet effet suivant acte reçu par {{ paiement.prets[0].acte_pret.notaire }}, le {{ paiement.prets[0].acte_pret.date | format_date }}.

Auprès de la **{{ paiement.prets[0].etablissement.nom|upper }}**, {{ paiement.prets[0].etablissement.forme_juridique }} dont le siège est à {{ paiement.prets[0].etablissement.siege }}, identifiée au SIREN sous le numéro {{ paiement.prets[0].etablissement.siren }} et immatriculée au Registre du Commerce et des Sociétés de {{ paiement.prets[0].etablissement.rcs }}
{% for pret in paiement.prets %}
Prêt {{ pret.reference }} d'un montant de {{ pret.montant_lettres|upper }} ({{ pret.montant|format_nombre }} {{ prix.devise }}), remboursable en {{ pret.duree_mois }} mois, au taux de {{ pret.taux }} %.
Le paiement de la première échéance aura lieu le {{ pret.date_premiere_echeance }} et celui de la dernière échéance le {{ pret.date_derniere_echeance }}.
Date de péremption de l'inscription : {{ pret.date_peremption_inscription }}.

{% endfor %}

# PRÊT ORIGINE DES FONDS - HYPOTHÈQUE LÉGALE SPÉCIALE DU PRÊTEUR DE DENIERS

Aux termes de l'acte susvisé l'**ACQUEREUR** s'est engagé auprès du **PRETEUR** à employer la somme de **{{ paiement.fonds_empruntes_lettres }} ({{ paiement.fonds_empruntes|format_nombre }} {{ prix.devise }})** provenant du prêt au paiement à due concurrence du prix ci-dessus stipulé.
L'**ACQUEREUR** déclare avoir effectué le paiement ci-dessus à due concurrence de la somme de {{ paiement.fonds_empruntes_lettres }} ({{ paiement.fonds_empruntes|format_nombre }} {{ prix.devise }}) lui provenant de ce prêt. Il fait cette déclaration pour constater l'origine des fonds conformément à l'engagement qu'il a pris ci-dessus envers le **PRETEUR**.
Par suite des stipulations et déclarations respectivement contenues dans l'acte de prêt précité et dans le présent acte de vente, tous deux passés en la forme authentique, le **PRETEUR** se trouve investi par l'article 2402 2° du Code civil, lequel garantit le principal du prêt, les intérêts dont il est productif et ses accessoires.
L'hypothèque bénéficiant au **PRETEUR** sera conservée par l'inscription qui sera prise à son profit.
L'inscription sera requise pour une durée qui cessera d'avoir effet faute d'avoir été renouvelée en temps utile, à l'expiration d'un délai d'une année à partir de la date de la dernière échéance de l'obligation garantie.
{% endif %}

# FORMALITÉ FUSIONNÉE

L'acte sera soumis à la formalité fusionnée, dans le mois de sa date, au service de la publicité foncière de {{ publication.service_publicite_fonciere }}.

# DECLARATIONS FISCALES

## Impôt sur la plus-value

**L'immeuble est entré dans le patrimoine de {% for v in vendeurs %}{{ v.civilite }} {{ v.prenoms }} {{ v.nom }}{% if not loop.last %} et {% endif %}{% endfor %}**

{% for origine in origine_propriete %}
**Concernant {{ "le lot numéro" if origine.lots_concernes|length == 1 else "les lots numéros" }} {{ origine.lots_concernes|join(' et ') }}**
{{ origine.origine_immediate.type_libelle }} suivant acte reçu par {{ origine.origine_immediate.notaire }}, le {{ origine.origine_immediate.date | format_date }}
Cet acte a été publié au service de la publicité foncière de {{ origine.origine_immediate.publication.service }}, le {{ origine.origine_immediate.publication.date | format_date }} volume {{ origine.origine_immediate.publication.volume }}, numéro {{ origine.origine_immediate.publication.numero }}.

{% endfor %}

{% if fiscalite and fiscalite.plus_value and fiscalite.plus_value.exoneration %}
**Exonération de l'impôt sur les plus-values immobilières en vertu de l'article 150 U II 1° du Code général des impôts**
Le **VENDEUR** déclare que les présentes portent sur sa résidence principale, c'est-à-dire sa résidence effective et habituelle.
Par suite, il bénéficie de l'exonération de l'impôt sur les plus-values conformément aux dispositions de l'article 150 U II 1° du Code général des impôts.
Il s'engage à produire tout élément précis et circonstancié quant à l'effectivité de l'utilisation du **BIEN** comme résidence principale, et ce si l'administration venait à lui demander des éléments de preuve.
Précision étant ici faite que la présente vente a pour le vendeur un caractère occasionnel. À défaut, celui-ci pourrait se voir refuser, par l'administration, le bénéfice de l'exonération visée ci-dessus.
En conséquence, le notaire est dispensé de déposer l'imprimé 2048-IMM-SD.
{% endif %}

## Domicile fiscal

Pour le contrôle de l'impôt, le **VENDEUR** déclare être effectivement domicilié à l'adresse susvisée, et s'engage à signaler au centre tout changement d'adresse.

{% if fiscalite and fiscalite.centre_impots_vendeur %}
**Quant au centre des finances publiques du VENDEUR**
{% for v in vendeurs %}{{ v.civilite }} {{ v.prenoms }} {{ v.nom }}{% if not loop.last %} et {% endif %}{% endfor %} {{ "dépendent" if vendeurs|length > 1 else "dépend" }} actuellement du centre des finances publiques de {{ fiscalite.centre_impots_vendeur.nom }} \- {{ fiscalite.centre_impots_vendeur.adresse }}.
{% endif %}

## Impôt sur la mutation

Le **VENDEUR** et l'**ACQUEREUR** indiquent ne pas agir aux présentes en qualité d'assujettis en tant que tels à la taxe sur la valeur ajoutée au sens de l'article 256 du Code général des impôts.

Les présentes seront soumises au tarif de droit commun en matière immobilière tel que prévu par [l'article 1594D du Code général des impôts](http://www.legifrance.gouv.fr/WAspad/UnArticleDeCode?code=CGIMPO00.rcv&art=1594/D).

{% if fiscalite.droits_mutation.primo_accedant %}
En vertu des dispositions du II-A de l'article 116 de la loi du 14 février 2025 (LF 2025), le conseil départemental du {{ bien.adresse.departement }}, dont dépend le lieu de situation de l'immeuble objet des présentes, a par une délibération en date du 21 février 2025, notifiée aux services fiscaux, relevé le taux prévu à l'article 1594 D.
Par exception, les primo-accédants au sens du I de l'article L 31-10-3 du Code de la construction et de l'habitation sont exemptés de cette augmentation pour l'acquisition d'un bien destiné à l'usage de leur résidence principale.

L'**ACQUEREUR** :

* reconnait avoir été informé de l'existence de ce régime de faveur et de la définition de la notion de « primo-accédant » au sens de l'article susvisé,

* **déclare entrer dans le cadre d'une première acquisition, telle que définie au I de l'article L 31-10-3 du code précité, destinée à l'usage de sa résidence principale.**

En conséquence, le taux relevé par le conseil départemental ne s'applique pas aux présentes.
{% endif %}

L'assiette des droits est de **{{ prix.montant_lettres|upper }} ({{ prix.montant|format_nombre }} {{ prix.devise }}).**

**Droits**

|  |  |  |  | Mt à payer  |
| :---- | :---- | :---- | :---- | ----: |
| *Taxe départementale* {{ fiscalite.droits_mutation.assiette|format_nombre }} |  x |  {{ fiscalite.droits_mutation.taux_departemental }} % |  \= |  {{ (fiscalite.droits_mutation.assiette * fiscalite.droits_mutation.taux_departemental / 100)|format_nombre }} |
| *Taxe communale* {{ fiscalite.droits_mutation.assiette|format_nombre }} |  x |  {{ fiscalite.droits_mutation.taux_communal }} % |  \= |  {{ (fiscalite.droits_mutation.assiette * fiscalite.droits_mutation.taux_communal / 100)|format_nombre }} |
|  |  |  |  |  |
| *Frais d'assiette* {{ (fiscalite.droits_mutation.assiette * fiscalite.droits_mutation.taux_departemental / 100)|format_nombre }} |  x |  2,37 % |  \= |  {{ (fiscalite.droits_mutation.assiette * fiscalite.droits_mutation.taux_departemental / 100 * 0.0237)|round|int }},00 |
|  |  |  |  **TOTAL** |  **{{ fiscalite.droits_mutation.total|format_nombre }}** |



**Contribution de sécurité immobilière**

En fonction des dispositions de l'acte à publier au fichier immobilier, la contribution de sécurité immobilière représentant la taxe au profit de l'État telle que fixée par l'article 879 du Code général des impôts s'élève à la somme :

| Type de contribution | Assiette (€) | Taux | Montant (€) |
| ----- | :---: | :---: | :---: |
| Contribution proportionnelle taux plein  | {{ fiscalite.droits_mutation.assiette|format_nombre }} | 0,10% | {{ (fiscalite.droits_mutation.assiette * 0.001)|format_nombre }} |

# FIN DE PARTIE NORMALISEE

# PARTIE DÉVELOPPÉE

{# ============================================================================
   La suite du template contient la PARTIE DÉVELOPPÉE
   avec toutes les sections détaillées (garanties, diagnostics, copropriété, etc.)

   Pour des raisons de longueur, cette partie sera dans un fichier séparé
   ou générée par le script d'assemblage à partir des clauses modulaires.
   ============================================================================ #}

{% include 'sections/partie_developpee.md' %}

**DONT ACTE sans renvoi**
Généré en l'office notarial et visualisé sur support électronique aux lieu, jour, mois et an indiqués en en-tête du présent acte.
Et lecture faite, les parties ont certifié exactes les déclarations les concernant, avant d'apposer leur signature manuscrite sur tablette numérique.

Le notaire, qui a recueilli l'image de leur signature, a lui-même apposé sa signature manuscrite, puis signé l'acte au moyen d'un procédé de signature électronique qualifié.
