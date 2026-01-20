{# ============================================================================
   CLAUSE: Application de la TVA sur marge
   ID: tva_marge
   Catégorie: fiscalite_copropriete
   Type d'acte: vente
   Obligatoire: Non
   Variables requises: 
   Source: Ajout - TVA marge
   Date ajout: 2025-01-19
   ============================================================================ #}

{%- if fiscalite.tva_marge == true -%}

Le VENDEUR déclare que le présent bien a été acquis sans TVA déductible ou avec une TVA non récupérable.

En application de l'article 268 du Code général des impôts, la TVA sera calculée sur la marge, c'est-à-dire sur la différence entre le prix de vente et le prix d'acquisition, après abattement.

Le VENDEUR certifie être en mesure de justifier du prix d'acquisition auprès de l'administration fiscale.

{%- endif -%}