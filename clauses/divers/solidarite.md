{# ============================================================================
   CLAUSE: Solidarité entre co-acquéreurs
   ID: solidarite
   Catégorie: divers
   Type d'acte: promesse_vente, compromis, vente
   Obligatoire: Oui
   Variables requises: 
   Source: Trame vente lots de copropriété
   Date ajout: 2025-01-19
   ============================================================================ #}

{%- if beneficiaires | length > 1 -%}

Les BENEFICIAIRES seront tenus solidairement et indivisiblement de l'exécution de toutes les obligations mises à leur charge aux présentes, tant envers le PROMETTANT qu'envers le notaire et les tiers.

Cette solidarité s'applique notamment au paiement du prix, des frais, et de toute indemnité qui pourrait être due.

{%- endif -%}