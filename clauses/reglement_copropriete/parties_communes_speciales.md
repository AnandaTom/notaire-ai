{# ============================================================================
   CLAUSE: Parties communes spéciales par bâtiment
   ID: parties_communes_speciales
   Catégorie: reglement_copropriete
   Type d'acte: reglement_copropriete, modificatif_edd
   Obligatoire: Non
   Variables requises: immeuble.batiments
   Source: Trame reglement copropriete EDD - multi-bâtiments
   Date ajout: 2025-01-19
   ============================================================================ #}

{%- if immeuble.batiments | length > 1 -%}

{% for batiment in immeuble.batiments %}
Les parties communes spéciales « <<<VAR_START>>>{{ batiment.nom }}<<<VAR_END>>> » comprennent :
- Les fondations et gros œuvre propres au <<<VAR_START>>>{{ batiment.nom }}<<<VAR_END>>>
- Les éléments de clos et couvert (toiture, façades)
- Le hall d'entrée et les circulations du <<<VAR_START>>>{{ batiment.nom }}<<<VAR_END>>>
- Les escaliers et leur cage
- Les conduites générales desservant exclusivement le <<<VAR_START>>>{{ batiment.nom }}<<<VAR_END>>>
- L'éclairage des parties communes du <<<VAR_START>>>{{ batiment.nom }}<<<VAR_END>>>

Seuls les copropriétaires des lots situés dans le <<<VAR_START>>>{{ batiment.nom }}<<<VAR_END>>> participent aux charges afférentes à ces parties communes spéciales.
{% endfor %}

{%- endif -%}