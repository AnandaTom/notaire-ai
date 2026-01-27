{# ============================================================================
   PARTIE DÉVELOPPÉE - PROMESSE DE VENTE
   Sections spécifiques aux promesses unilatérales de vente
   Version: 1.0.0 - 26 janvier 2026

   Cette section PRÉCÈDE la partie développée commune et contient :
   - Conditions suspensives
   - Délai de réalisation
   - Indemnité d'immobilisation
   - Faculté de substitution
   - Clauses pénales
   ============================================================================ #}

# PARTIE DÉVELOPPÉE

## CONDITIONS DE LA PROMESSE

### DÉLAI DE RÉALISATION

La présente promesse est consentie pour une durée de **{{ delai_realisation.duree | default('QUATRE') }} MOIS** à compter de ce jour.

{% if delai_realisation.date_butoir %}
La date butoir de réalisation est donc fixée au **{{ delai_realisation.date_butoir | format_date }}** au plus tard.
{% endif %}

Le **PROMETTANT** s'engage irrévocablement à vendre le **BIEN** aux prix, charges et conditions ci-dessus, pendant toute la durée de la promesse.

{% if delai_realisation.prorogation %}
Ce délai pourra être prorogé par accord des parties constaté par acte authentique.
{% endif %}

### INDEMNITÉ D'IMMOBILISATION

En contrepartie de l'immobilisation du **BIEN** par le **PROMETTANT**, le **BÉNÉFICIAIRE** verse, à titre d'indemnité d'immobilisation, une somme de **{{ indemnite_immobilisation.montant_lettres | default("VINGT-DEUX MILLE CINQ CENTS EUROS") | upper }}** soit **{{ indemnite_immobilisation.montant | default(22500) | format_nombre }} {{ prix.devise | default("EUR") }}**, représentant **{{ indemnite_immobilisation.pourcentage | default(5) }} %** du prix de vente.

{% if indemnite_immobilisation.versement == "signature" %}
Cette somme est versée ce jour entre les mains du notaire soussigné, qui en donne quittance.
{% elif indemnite_immobilisation.versement == "differe" %}
Cette somme sera versée au plus tard le **{{ indemnite_immobilisation.date_versement | format_date }}** entre les mains du notaire soussigné.
{% endif %}

{% if indemnite_immobilisation.sequestre %}
Le notaire soussigné conservera cette somme à titre de séquestre jusqu'à la réalisation ou la caducité de la promesse.
{% endif %}

**Sort de l'indemnité d'immobilisation :**

* **En cas de réalisation de la vente** : cette somme s'imputera sur le prix de vente.

* **En cas de levée d'option** : le **BÉNÉFICIAIRE** devra lever l'option et régulariser l'acte de vente dans le délai ci-dessus fixé. A défaut, l'indemnité d'immobilisation restera acquise au **PROMETTANT** à titre de dédommagement forfaitaire du préjudice subi du fait de l'immobilisation du **BIEN**.

* **En cas de non-réalisation d'une condition suspensive** : si la vente ne se réalise pas en raison de la défaillance d'une condition suspensive, l'indemnité d'immobilisation sera restituée au **BÉNÉFICIAIRE**.

{% if conditions_suspensives %}
## CONDITIONS SUSPENSIVES

La présente promesse de vente est consentie sous les conditions suspensives suivantes, dont la réalisation conditionne la perfection de la vente :

{% if conditions_suspensives.pret and conditions_suspensives.pret.applicable %}
### Condition suspensive d'obtention de prêt

La réalisation de la présente promesse est subordonnée à l'obtention par le **BÉNÉFICIAIRE** d'un ou plusieurs prêts d'un montant en principal de **{{ conditions_suspensives.pret.montant_lettres | default("TROIS CENT SOIXANTE MILLE EUROS") | upper }}** soit **{{ conditions_suspensives.pret.montant | default(360000) | format_nombre }} {{ prix.devise | default("EUR") }}**, remboursable sur une durée de **{{ conditions_suspensives.pret.duree_mois | default(240) }} mois** au taux d'intérêt maximum de **{{ conditions_suspensives.pret.taux_max | default(4.5) }} %** l'an (hors assurance).

{% if conditions_suspensives.pret.type == "immobilier" %}
Ce prêt est destiné au financement de l'acquisition du **BIEN** objet des présentes.
{% endif %}

**Obligations du BÉNÉFICIAIRE :**

Le **BÉNÉFICIAIRE** s'oblige :

* à déposer sa demande de prêt auprès d'un établissement de crédit dans les **{{ conditions_suspensives.pret.delai_depot | default(15) }} jours** de la signature des présentes ;

* à justifier au **PROMETTANT** du dépôt de sa demande dans le même délai ;

* à faire ses meilleurs efforts pour obtenir le prêt sollicité ;

* à informer le **PROMETTANT** de la décision de l'établissement prêteur dès qu'il en aura connaissance.

**Délai de réalisation de la condition :**

Cette condition suspensive devra être réalisée au plus tard le **{{ conditions_suspensives.pret.date_butoir | format_date }}**, soit dans un délai de **{{ conditions_suspensives.pret.delai_jours | default(60) }} jours** à compter de ce jour.

**En cas de refus de prêt :**

Si le **BÉNÉFICIAIRE** justifie, par la production d'une ou plusieurs attestations de refus émanant d'établissements de crédit différents, n'avoir pu obtenir le prêt sollicité dans les conditions définies ci-dessus, la présente promesse sera caduque de plein droit et l'indemnité d'immobilisation lui sera restituée.

**En cas de non-justification :**

À défaut de justification dans les délais impartis, le **PROMETTANT** pourra, à son choix :
* soit considérer la condition comme réalisée et réitérer la vente,
* soit considérer la promesse comme caduque et conserver l'indemnité d'immobilisation.
{% endif %}

{% if conditions_suspensives.vente_prealable and conditions_suspensives.vente_prealable.applicable %}
### Condition suspensive de vente préalable

La réalisation de la présente promesse est subordonnée à la vente par le **BÉNÉFICIAIRE** du bien lui appartenant situé **{{ conditions_suspensives.vente_prealable.adresse_bien }}**.

Cette vente devra être conclue au plus tard le **{{ conditions_suspensives.vente_prealable.date_butoir | format_date }}**.

Le **BÉNÉFICIAIRE** s'engage :

* à mettre ce bien en vente dans les meilleurs délais ;
* à confier un mandat de vente à un ou plusieurs professionnels de l'immobilier ;
* à justifier de ses diligences auprès du **PROMETTANT** ;
* à informer le **PROMETTANT** de la conclusion de la vente dès que celle-ci sera intervenue.
{% endif %}

{% if conditions_suspensives.urbanisme and conditions_suspensives.urbanisme.applicable %}
### Condition suspensive d'urbanisme

La réalisation de la présente promesse est subordonnée à l'obtention d'un certificat d'urbanisme confirmant que le **BIEN** peut faire l'objet de l'affectation projetée par le **BÉNÉFICIAIRE**, à savoir : {{ conditions_suspensives.urbanisme.projet }}.

Le **BÉNÉFICIAIRE** devra déposer sa demande de certificat d'urbanisme dans les **{{ conditions_suspensives.urbanisme.delai_depot | default(15) }} jours** de ce jour.
{% endif %}

{% if conditions_suspensives.droit_preemption and conditions_suspensives.droit_preemption.applicable %}
### Condition suspensive de purge du droit de préemption

La réalisation de la présente promesse est subordonnée à la non-préemption du **BIEN** par le ou les titulaires d'un droit de préemption légal.

Le notaire soussigné se charge d'accomplir les formalités de purge de ce droit de préemption et d'en informer les parties du résultat.

{% if conditions_suspensives.droit_preemption.titulaires %}
Les titulaires du droit de préemption sont :
{% for titulaire in conditions_suspensives.droit_preemption.titulaires %}
* {{ titulaire }}
{% endfor %}
{% endif %}
{% endif %}

{% if conditions_suspensives.etat_hypothecaire and conditions_suspensives.etat_hypothecaire.applicable %}
### Condition suspensive d'état hypothécaire

La réalisation de la présente promesse est subordonnée à l'obtention d'un état hypothécaire sur formalités ne révélant que les inscriptions connues des parties.
{% endif %}

{% if conditions_suspensives.autres %}
### Autres conditions suspensives

{% for condition in conditions_suspensives.autres %}
**{{ condition.titre }}**

{{ condition.description }}

{% if condition.delai %}
Cette condition devra être réalisée au plus tard le **{{ condition.date_butoir | format_date }}**.
{% endif %}

{% endfor %}
{% endif %}

### Règles communes aux conditions suspensives

**Défaillance des conditions :**

Si l'une quelconque des conditions suspensives stipulées ci-dessus n'est pas réalisée dans le délai prévu, la présente promesse sera caduque de plein droit, sans indemnité de part ni d'autre, sauf stipulation contraire prévue ci-dessus.

L'indemnité d'immobilisation versée sera restituée au **BÉNÉFICIAIRE**.

**Renonciation :**

Le **BÉNÉFICIAIRE**, seul bénéficiaire des conditions suspensives, pourra y renoncer expressément.

**Réalisation des conditions :**

La justification de la réalisation des conditions suspensives devra être fournie au notaire soussigné.

{% endif %}

{% if faculte_substitution and faculte_substitution.autorisee %}
## FACULTÉ DE SUBSTITUTION

Le **BÉNÉFICIAIRE** a la faculté de se substituer, pour la réitération de la vente, toute personne physique ou morale de son choix.

{% if faculte_substitution.conditions %}
Cette substitution devra être notifiée au **PROMETTANT** au moins **{{ faculte_substitution.delai_notification | default(15) }} jours** avant la date prévue pour la réitération.
{% endif %}

**Effets de la substitution :**

En cas de substitution :

* le **BÉNÉFICIAIRE** restera garant solidaire des obligations du substitué envers le **PROMETTANT** ;
* le substitué devra remplir les mêmes conditions que le **BÉNÉFICIAIRE** pour l'obtention du prêt, le cas échéant ;
* l'indemnité d'immobilisation versée restera acquise à la présente promesse.

{% if faculte_substitution.sci_constitution %}
La substitution pourra notamment intervenir au profit d'une société civile immobilière à constituer par le **BÉNÉFICIAIRE**.
{% endif %}
{% endif %}

{% if clause_penale %}
## CLAUSE PÉNALE

**En cas d'inexécution par le PROMETTANT :**

Si le **PROMETTANT**, après levée de l'option par le **BÉNÉFICIAIRE** et réalisation des conditions suspensives, refuse de réitérer la vente, il devra verser au **BÉNÉFICIAIRE**, à titre de clause pénale, une somme égale à **{{ clause_penale.pourcentage_promettant | default(10) }} %** du prix de vente, soit **{{ (prix.montant * clause_penale.pourcentage_promettant / 100) | default(45000) | format_nombre }} {{ prix.devise | default("EUR") }}**, outre la restitution de l'indemnité d'immobilisation.

**En cas d'inexécution par le BÉNÉFICIAIRE :**

Si le **BÉNÉFICIAIRE**, après avoir levé l'option, refuse de réitérer la vente dans les délais convenus, le **PROMETTANT** pourra, à son choix :

* soit exiger l'exécution forcée de la vente ;
* soit considérer la promesse comme caduque et conserver l'indemnité d'immobilisation à titre de clause pénale.
{% endif %}

## RÉITÉRATION PAR ACTE AUTHENTIQUE

Les parties s'engagent à réitérer la présente promesse par acte authentique dès que toutes les conditions suspensives seront réalisées et au plus tard à la date butoir fixée ci-dessus.

Le notaire soussigné se chargera de convoquer les parties à la signature de l'acte authentique de vente.

**Lieu de signature :**

L'acte authentique de vente sera reçu en l'office du notaire soussigné{% if acte.notaire_beneficiaire %}, ou en celui de {{ acte.notaire_beneficiaire.civilite }} {{ acte.notaire_beneficiaire.nom }}, notaire du **BÉNÉFICIAIRE**{% endif %}.

**Pièces à fournir :**

Les parties devront fournir au notaire toutes les pièces nécessaires à l'établissement de l'acte de vente dans les meilleurs délais et au plus tard **15 jours** avant la date de signature prévue.

{# ============================================================================
   INCLUSION DE LA PARTIE DÉVELOPPÉE COMMUNE
   Contient : garanties, diagnostics, copropriété, fiscalité, etc.
   ============================================================================ #}

{% include 'sections/partie_developpee.md' %}
