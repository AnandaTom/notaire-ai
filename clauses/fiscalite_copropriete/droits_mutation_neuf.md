{# ============================================================================
   CLAUSE: Droits de mutation réduits - Immeuble neuf
   ID: droits_mutation_neuf
   Catégorie: fiscalite_copropriete
   Type d'acte: vente
   Obligatoire: Non
   Variables requises: 
   Source: Ajout - droits mutation neuf
   Date ajout: 2025-01-19
   ============================================================================ #}

{%- if fiscalite.immeuble_neuf == true -%}

Le présent bien constitue un immeuble neuf au sens fiscal (achèvement depuis moins de 5 ans).

La vente est soumise à la TVA immobilière au taux de <<<VAR_START>>>{{ fiscalite.taux_tva | default(20) }}<<<VAR_END>>>%.

Les droits de mutation sont réduits au taux de 0,715% (au lieu de 5,80% pour l'ancien).

Le VENDEUR certifie que le bien n'a jamais été habité ou utilisé depuis son achèvement.

{%- endif -%}