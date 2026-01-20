{# ============================================================================
   CLAUSE: Parties communes à jouissance privative
   ID: jouissance_privative
   Catégorie: reglement_copropriete
   Type d'acte: reglement_copropriete, modificatif_edd
   Obligatoire: Non
   Variables requises: parties_communes.jouissance_privative
   Source: Trame reglement copropriete EDD
   Date ajout: 2025-01-19
   ============================================================================ #}

{%- if parties_communes.jouissance_privative | length > 0 -%}

{% for jp in parties_communes.jouissance_privative %}
Le lot n° <<<VAR_START>>>{{ jp.lot_beneficiaire }}<<<VAR_END>>> bénéficie d'un droit de jouissance exclusif sur <<<VAR_START>>>{{ jp.designation }}<<<VAR_END>>>, partie commune de l'immeuble.

Ce droit de jouissance est perpétuel et ne peut être retiré au bénéficiaire sans son accord.

Le bénéficiaire a la charge exclusive de l'entretien courant de cette partie commune à jouissance privative.

Les grosses réparations et la reconstruction demeurent à la charge de la copropriété.
{% endfor %}

{%- endif -%}