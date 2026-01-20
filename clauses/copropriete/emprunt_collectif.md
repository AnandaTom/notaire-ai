{# ============================================================================
   CLAUSE: Emprunt collectif - Information
   ID: emprunt_collectif
   Catégorie: copropriete
   Type d'acte: promesse_vente, compromis, vente
   Obligatoire: Oui
   Variables requises: emprunt.etablissement, emprunt.montant_total, emprunt.quote_part, emprunt.solde_quote_part
   Source: Ajout - copropriété avec emprunt collectif
   Date ajout: 2025-01-19
   ============================================================================ #}

{%- if copropriete.emprunt_collectif.existe == true -%}

Le PROMETTANT informe le BENEFICIAIRE qu'un emprunt collectif a été souscrit par le syndicat des copropriétaires.

**Caractéristiques de l'emprunt :**
- Établissement prêteur : <<<VAR_START>>>{{ emprunt.etablissement }}<<<VAR_END>>>
- Montant total : <<<VAR_START>>>{{ emprunt.montant_total | format_nombre }}<<<VAR_END>>> EUR
- Quote-part du lot : <<<VAR_START>>>{{ emprunt.quote_part | format_nombre }}<<<VAR_END>>> EUR
- Solde restant dû (quote-part) : <<<VAR_START>>>{{ emprunt.solde_quote_part | format_nombre }}<<<VAR_END>>> EUR
- Échéance finale : <<<VAR_START>>>{{ emprunt.date_fin }}<<<VAR_END>>>

Conformément à l'article 26-6 de la loi du 10 juillet 1965, le BENEFICIAIRE sera tenu de rembourser les annuités restant dues à compter de la vente.

{%- endif -%}