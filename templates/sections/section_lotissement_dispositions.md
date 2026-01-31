{# Section: DISPOSITIONS LOTISSEMENT — Spécifique terrain à bâtir / lotissement #}
{# Applicable: Catégorie terrain_a_batir uniquement #}
{# Condition: bien.lotissement #}
{# Source: PUV GUNTZER GAUTIER (document original anonymisé) + Trame D #}

{% if bien.lotissement %}
# DISPOSITIONS RELATIVES AU LOTISSEMENT

## Permis d'aménager

Le terrain objet des présentes fait partie du lotissement dénommé **"{{ bien.lotissement.nom }}"**, autorisé par {{ bien.lotissement.autorite | default("arrêté de Monsieur le Maire") }} de {{ bien.lotissement.commune | default(bien.adresse.ville) }}{% if bien.lotissement.date_permis %} en date du {{ bien.lotissement.date_permis | format_date }}{% endif %}{% if bien.lotissement.numero_permis %}, sous le numéro {{ bien.lotissement.numero_permis }}{% endif %}.

{% if bien.lotissement.lotisseur %}
Le lotisseur est {{ bien.lotissement.lotisseur }}.
{% endif %}

{% if bien.lotissement.parcelles %}
### Parcelles du lotissement

| Lot | Section | N° parcelle | Surface | Affectation |
| :---- | :---- | :---- | ----: | :---- |
{% for parcelle in bien.lotissement.parcelles %}| {{ parcelle.lot | default("-") }} | {{ parcelle.section | default("-") }} | {{ parcelle.numero | default("-") }} | {{ parcelle.surface | default("-") }} m² | {{ parcelle.affectation | default("À bâtir") }} |
{% endfor %}

{% endif %}

{% if bien.lotissement.date_reception %}
Le procès-verbal de réception des travaux a été établi le {{ bien.lotissement.date_reception | format_date }}.
{% endif %}

## Cahier des charges du lotissement

{% if bien.lotissement.cahier_charges %}
Un cahier des charges du lotissement a été établi{% if bien.lotissement.cahier_charges.auteur %} par {{ bien.lotissement.cahier_charges.auteur }}{% endif %}{% if bien.lotissement.cahier_charges.date %} le {{ bien.lotissement.cahier_charges.date | format_date }}{% endif %}{% if bien.lotissement.cahier_charges.publication %}, publié au service de la publicité foncière de {{ bien.lotissement.cahier_charges.publication }}{% endif %}.

Le **BENEFICIAIRE** déclare avoir pris connaissance du cahier des charges du lotissement et s'engage à en respecter l'intégralité des prescriptions, et notamment :
{% if bien.lotissement.cahier_charges.prescriptions %}
{% for prescription in bien.lotissement.cahier_charges.prescriptions %}
* {{ prescription }}
{% endfor %}
{% else %}
* Les prescriptions architecturales et urbanistiques ;
* Les prescriptions relatives aux clôtures et plantations ;
* Les prescriptions relatives aux servitudes de passage et de réseaux.
{% endif %}

**Annexe : Cahier des charges du lotissement**
{% else %}
Le **PROMETTANT** s'engage à remettre le cahier des charges du lotissement au **BENEFICIAIRE** avant la réitération.
{% endif %}

{% if bien.lotissement.reglement %}
## Règlement du lotissement

Le lotissement est soumis à un règlement{% if bien.lotissement.reglement.date %} établi le {{ bien.lotissement.reglement.date | format_date }}{% endif %}, dont le **BENEFICIAIRE** déclare avoir pris connaissance.

{% if bien.lotissement.reglement.prescriptions_principales %}
Les prescriptions principales sont les suivantes :
{% for presc in bien.lotissement.reglement.prescriptions_principales %}
* {{ presc }}
{% endfor %}
{% endif %}
{% endif %}

{% if bien.lotissement.asl %}
## Association Syndicale Libre (ASL)

Il existe une Association Syndicale Libre (ASL){% if bien.lotissement.asl.nom %} dénommée **"{{ bien.lotissement.asl.nom }}"**{% endif %}, ayant pour objet {{ bien.lotissement.asl.objet | default("la gestion et l'entretien des équipements communs du lotissement") }}.

{% if bien.lotissement.asl.cotisation %}
La cotisation annuelle est de {{ bien.lotissement.asl.cotisation | format_nombre }} EUR.
{% endif %}

Le **BENEFICIAIRE** est informé qu'il deviendra membre de droit de cette association et sera tenu au paiement des charges y afférentes.
{% endif %}

## Viabilisation du terrain

{% if bien.viabilisation %}
Le terrain est {% if bien.viabilisation.viabilise %}viabilisé{% else %}non viabilisé{% endif %}.

{% if bien.viabilisation.raccordements %}
**État des raccordements** :

| Réseau | Statut | Distance {% if bien.viabilisation.raccordements[0].cout is defined %}| Coût estimé {% endif %}|
| :---- | :---- | :---- {% if bien.viabilisation.raccordements[0].cout is defined %}| :---- {% endif %}|
{% for raccord in bien.viabilisation.raccordements %}
| {{ raccord.reseau }} | {{ raccord.statut | default("À vérifier") }} | {{ raccord.distance | default("-") }} {% if raccord.cout is defined %}| {{ raccord.cout | format_nombre }} EUR {% endif %}|
{% endfor %}
{% endif %}

{% if not bien.viabilisation.viabilise and bien.viabilisation.cout_estimatif %}
**Coût estimatif total de viabilisation** : {{ bien.viabilisation.cout_estimatif | format_nombre }} EUR
{% endif %}
{% else %}
Le **PROMETTANT** déclare que le terrain est viabilisé et raccordé aux réseaux publics (eau, électricité, assainissement).
{% endif %}

## Constructibilité

{% if bien.constructibilite %}
{% if bien.constructibilite.cu_reference %}
Un certificat d'urbanisme {{ bien.constructibilite.cu_type | default("opérationnel") }} a été délivré le {{ bien.constructibilite.cu_date | format_date }}{% if bien.constructibilite.cu_commune %} par {{ bien.constructibilite.cu_commune }}{% endif %} sous la référence {{ bien.constructibilite.cu_reference }}.

{% if bien.constructibilite.cu_validite %}
Ce certificat est valable jusqu'au {{ bien.constructibilite.cu_validite | format_date }}.
{% endif %}
{% endif %}

{% if bien.constructibilite.zone_plu %}
Le terrain se situe en zone **{{ bien.constructibilite.zone_plu }}** du Plan Local d'Urbanisme{% if bien.constructibilite.plu_commune %} de {{ bien.constructibilite.plu_commune }}{% endif %}.
{% endif %}

{% if bien.constructibilite.shon_max %}
La surface de plancher maximale autorisée est de {{ bien.constructibilite.shon_max }} m².
{% endif %}

{% if bien.constructibilite.contraintes %}
**Contraintes identifiées** :
{% for contrainte in bien.constructibilite.contraintes %}
* {{ contrainte }}
{% endfor %}
{% endif %}

**Annexe : Certificat d'urbanisme**
{% endif %}

## Bornage

{% if bien.bornage %}
Un procès-verbal de bornage a été dressé par {{ bien.bornage.geometre }}{% if bien.bornage.date %}, en date du {{ bien.bornage.date | format_date }}{% endif %}{% if bien.bornage.reference %}, sous la référence {{ bien.bornage.reference }}{% endif %}.

La surface bornée est de **{{ bien.bornage.surface | default(bien.surface_terrain) }} m²**.

{% if bien.bornage.bornes %}
Les bornes ont été posées aux {{ bien.bornage.bornes | length }} angles de la parcelle.
{% endif %}

**Annexe : Procès-verbal de bornage**
{% else %}
Conformément à l'article L. 115-4 du Code de l'urbanisme, le terrain faisant partie d'un lotissement, un bornage sera réalisé aux frais du **PROMETTANT** avant la réitération authentique.
{% endif %}

{% endif %}
