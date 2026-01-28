{# ============================================================================
   SECTION PLUS-VALUE IMMOBILIERE

   Utilisation: {% include 'sections/section_plus_value.md' %}
   Condition: {% if plus_value %}

   Variables requises:
   - plus_value.exoneration: true/false
   - plus_value.motif_exoneration: "residence_principale", "premiere_cession", etc.
   - plus_value.montant_brut: Montant brut de la plus-value
   - plus_value.abattements: Détail des abattements
   - plus_value.montant_impot: Montant de l'impôt
   ============================================================================ #}

### PLUS-VALUE IMMOBILIERE

#### Déclarations du vendeur

Le vendeur déclare que le bien vendu {% if plus_value.exoneration %}**EST EXONERE**{% else %}**N'EST PAS EXONERE**{% endif %} de l'impôt sur la plus-value immobilière.

{% if plus_value.exoneration %}

##### Motif d'exonération

{% if plus_value.motif_exoneration == "residence_principale" %}
Le bien objet des présentes constitue la **résidence principale** du vendeur au jour de la cession.

Le vendeur déclare que :
- Il occupait le bien à titre de résidence principale de manière habituelle et effective au jour de la cession ;
- Le bien n'a pas été mis en location, même temporairement, depuis qu'il l'occupe à titre principal ;
- {% if plus_value.delai_revente %}Il a mis le bien en vente dans un délai normal depuis qu'il a cessé de l'occuper (délai de {{ plus_value.delai_revente }} mois).{% endif %}

{% elif plus_value.motif_exoneration == "premiere_cession" %}
Il s'agit de la **première cession d'un logement autre que la résidence principale**, le vendeur déclarant :
- Ne pas avoir été propriétaire de sa résidence principale au cours des quatre années précédant la cession ;
- Remployer le prix de cession dans l'acquisition de sa résidence principale dans un délai de vingt-quatre mois.

{% elif plus_value.motif_exoneration == "detention_plus_30_ans" %}
Le bien est détenu depuis **plus de trente ans** (date d'acquisition : {{ plus_value.date_acquisition | default("") }}).

L'exonération est totale pour les plus-values de cession de biens détenus depuis plus de trente ans (article 150 VC du CGI).

{% elif plus_value.motif_exoneration == "retraite_invalidite" %}
Le vendeur bénéficie de l'exonération au titre de sa qualité de **personne retraitée ou invalide** :
- Titulaire d'une pension de retraite ou d'une carte d'invalidité ;
- Revenus fiscaux de référence de l'avant-dernière année inférieurs au seuil légal.

{% elif plus_value.motif_exoneration == "expropriation" %}
La cession résulte d'une **expropriation pour cause d'utilité publique** et le vendeur s'engage à remployer le prix dans les douze mois.

{% elif plus_value.motif_exoneration == "prix_inferieur_15000" %}
Le prix de cession est **inférieur à 15 000 euros**.

{% else %}
Motif d'exonération : {{ plus_value.motif_exoneration | default("Non précisé") }}
{% endif %}

{% else %}

##### Calcul de la plus-value

Le vendeur reconnaît avoir été informé des modalités de calcul de la plus-value immobilière :

| Élément | Montant |
|---------|---------|
| Prix d'acquisition | {{ plus_value.prix_acquisition | default(0) | format_nombre }} euros |
{% if plus_value.frais_acquisition %}| Frais d'acquisition (forfait 7,5% ou réel) | {{ plus_value.frais_acquisition | default(0) | format_nombre }} euros |{% endif %}
{% if plus_value.travaux %}| Travaux (forfait 15% ou réel) | {{ plus_value.travaux | default(0) | format_nombre }} euros |{% endif %}
| **Prix de revient** | {{ plus_value.prix_revient | default(0) | format_nombre }} euros |
| Prix de cession | {{ prix.montant | default(0) | format_nombre }} euros |
| **Plus-value brute** | {{ plus_value.montant_brut | default(0) | format_nombre }} euros |

##### Abattements pour durée de détention

Durée de détention : **{{ plus_value.duree_detention | default(0) }} ans** (acquisition le {{ plus_value.date_acquisition | default("") }})

{% if plus_value.abattements %}
| Type d'abattement | Taux | Montant |
|-------------------|------|---------|
{% if plus_value.abattements.impot_revenu %}| Abattement IR (6% par an de la 6ème à la 21ème année, 4% la 22ème) | {{ plus_value.abattements.taux_ir | default(0) }}% | {{ plus_value.abattements.impot_revenu | default(0) | format_nombre }} euros |{% endif %}
{% if plus_value.abattements.prelevements_sociaux %}| Abattement PS (1,65% par an de la 6ème à la 21ème année, 1,60% la 22ème, 9% au-delà) | {{ plus_value.abattements.taux_ps | default(0) }}% | {{ plus_value.abattements.prelevements_sociaux | default(0) | format_nombre }} euros |{% endif %}
{% endif %}

##### Imposition

| Impôt | Base imposable | Taux | Montant |
|-------|----------------|------|---------|
| Impôt sur le revenu | {{ plus_value.base_ir | default(0) | format_nombre }} euros | 19% | {{ plus_value.impot_ir | default(0) | format_nombre }} euros |
| Prélèvements sociaux | {{ plus_value.base_ps | default(0) | format_nombre }} euros | 17,2% | {{ plus_value.impot_ps | default(0) | format_nombre }} euros |
{% if plus_value.surtaxe %}| Surtaxe (PV > 50 000 euros) | {{ plus_value.base_surtaxe | default(0) | format_nombre }} euros | {{ plus_value.taux_surtaxe | default(0) }}% | {{ plus_value.surtaxe | default(0) | format_nombre }} euros |{% endif %}
| **TOTAL À PAYER** | | | **{{ plus_value.montant_impot | default(0) | format_nombre }} euros** |

##### Paiement de l'impôt

{% if plus_value.paiement_par_notaire %}
L'impôt sur la plus-value, soit la somme de **{{ plus_value.montant_impot | default(0) | format_nombre }} euros**, sera acquitté par le notaire soussigné pour le compte du vendeur, par prélèvement sur le prix de vente.

Le notaire établira la déclaration de plus-value n° 2048-IMM et procédera au versement de l'impôt à la recette des non-résidents ou au service des impôts compétent.
{% else %}
Le vendeur s'engage à déclarer et payer l'impôt sur la plus-value selon les modalités légales.
{% endif %}

{% endif %}

{% if plus_value.declarations_complementaires %}
##### Déclarations complémentaires

{{ plus_value.declarations_complementaires }}
{% endif %}

{% if plus_value.observations %}
##### Observations

{{ plus_value.observations }}
{% endif %}

---
