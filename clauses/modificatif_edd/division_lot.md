{# ============================================================================
   CLAUSE: Division d'un lot en plusieurs
   ID: division_lot
   Catégorie: modificatif_edd
   Type d'acte: modificatif_edd
   Obligatoire: Non
   Variables requises: modifications
   Source: Trame modificatif EDD
   Date ajout: 2025-01-19
   ============================================================================ #}

{%- if modifications[0].type == 'division_lot' -%}

{% for modif in modifications if modif.type == 'suppression_lot' %}
Le lot n° <<<VAR_START>>>{{ modif.lot_numero }}<<<VAR_END>>> (<<<VAR_START>>>{{ modif.description }}<<<VAR_END>>>) est supprimé de l'état descriptif de division.
{% endfor %}

En remplacement, il est créé les lots suivants :

{% for modif in modifications if modif.type == 'creation_lot' %}
**Lot n° <<<VAR_START>>>{{ modif.lot_numero }}<<<VAR_END>>>** : <<<VAR_START>>>{{ modif.description }}<<<VAR_END>>>
Tantièmes de copropriété : <<<VAR_START>>>{{ modif.tantiemes }}<<<VAR_END>>>/1000

{% endfor %}

La somme des tantièmes des nouveaux lots est égale aux tantièmes du lot supprimé.

{%- endif -%}