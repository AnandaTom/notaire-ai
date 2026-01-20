{# ============================================================================
   CLAUSE: Plus-value imposable
   ID: plus_value_imposition
   Catégorie: fiscalite
   Type d'acte: vente
   Obligatoire: Oui
   Variables requises: 
   Source: Trame vente lots de copropriété
   Date ajout: 2025-01-19
   ============================================================================ #}

{%- if fiscalite.plus_value.exoneration == false -%}

Le VENDEUR reconnaît être informé que la plus-value réalisée à l'occasion de la présente vente est susceptible d'être soumise à l'impôt sur le revenu et aux prélèvements sociaux.

Le notaire soussigné procédera au calcul de cette plus-value et effectuera les déclarations et le versement de l'impôt correspondant, par prélèvement sur le prix de vente.

Le VENDEUR autorise expressément ce prélèvement.

{%- endif -%}