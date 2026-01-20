{# ============================================================================
   CLAUSE: Réunion de plusieurs lots en un seul
   ID: reunion_lots
   Catégorie: modificatif_edd
   Type d'acte: modificatif_edd
   Obligatoire: Non
   Variables requises: modifications
   Source: Trame modificatif EDD
   Date ajout: 2025-01-19
   ============================================================================ #}

{%- if modifications[0].type == 'reunion_lots' -%}

Les lots n° {% for modif in modifications if modif.type == 'suppression_lot' %}<<<VAR_START>>>{{ modif.lot_numero }}<<<VAR_END>>>{% if not loop.last %}, {% endif %}{% endfor %} sont supprimés de l'état descriptif de division.

En remplacement, il est créé :

{% for modif in modifications if modif.type == 'creation_lot' %}
**Lot n° <<<VAR_START>>>{{ modif.lot_numero }}<<<VAR_END>>>** : <<<VAR_START>>>{{ modif.description }}<<<VAR_END>>>
Tantièmes de copropriété : <<<VAR_START>>>{{ modif.tantiemes }}<<<VAR_END>>>/1000

{% endfor %}

Les tantièmes du nouveau lot correspondent à la somme des tantièmes des lots réunis.

{%- endif -%}