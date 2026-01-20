{# ============================================================================
   CLAUSE: Déclaration régime Pinel
   ID: regime_fiscal_pinel
   Catégorie: fiscalite
   Type d'acte: promesse_vente, vente
   Obligatoire: Oui
   Variables requises: pinel.duree_engagement, pinel.date_debut, pinel.date_fin
   Source: Ajout - bien sous régime Pinel
   Date ajout: 2025-01-19
   ============================================================================ #}

{%- if fiscalite.regime_fiscal == 'pinel' -%}

Le PROMETTANT déclare avoir souscrit au dispositif fiscal prévu par l'article 199 novovicies du Code général des impôts (dispositif « Pinel »).

Il s'est engagé à louer le bien pendant une durée de <<<VAR_START>>>{{ pinel.duree_engagement }}<<<VAR_END>>> ans à compter du <<<VAR_START>>>{{ pinel.date_debut }}<<<VAR_END>>>.

Le PROMETTANT déclare que cet engagement de location prendra fin le <<<VAR_START>>>{{ pinel.date_fin }}<<<VAR_END>>> et que la présente vente n'interviendra qu'après cette date.

{% if pinel.reprise_avantage_fiscal %}
Le PROMETTANT est informé qu'une cession avant le terme de l'engagement entraînerait la reprise de l'avantage fiscal.
{% endif %}

{%- endif -%}