{# ============================================================================
   CLAUSE: Exonération plus-value - Résidence principale
   ID: plus_value_exoneration_rp
   Catégorie: fiscalite
   Type d'acte: vente
   Obligatoire: Oui
   Variables requises: 
   Source: Trame vente lots de copropriété
   Date ajout: 2025-01-19
   ============================================================================ #}

{%- if fiscalite.plus_value.motif_exoneration == 'residence_principale' -%}

Le VENDEUR déclare que le bien constitue sa résidence principale au sens des dispositions de l'article 150 U-II-1° du Code général des impôts.

En conséquence, la plus-value réalisée à l'occasion de la présente vente bénéficie de l'exonération totale prévue par ce texte.

Le VENDEUR s'engage à fournir tout justificatif utile à l'administration fiscale en cas de contrôle.

{%- endif -%}