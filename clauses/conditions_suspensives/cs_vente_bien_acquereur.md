{# ============================================================================
   CLAUSE: Condition suspensive de vente d'un bien par l'acquéreur
   ID: cs_vente_bien_acquereur
   Catégorie: conditions_suspensives
   Type d'acte: promesse_vente, compromis
   Obligatoire: Non
   Variables requises: bien_a_vendre.adresse, condition.date_limite
   Source: Ajout notaire - vente en cascade
   Date ajout: 2025-01-19
   ============================================================================ #}

Les présentes sont consenties sous la condition suspensive de la vente par le BENEFICIAIRE du bien lui appartenant situé <<<VAR_START>>>{{ bien_a_vendre.adresse }}<<<VAR_END>>>.

Cette condition sera réputée réalisée par la signature de l'acte authentique de vente dudit bien au plus tard le <<<VAR_START>>>{{ condition.date_limite | format_date }}<<<VAR_END>>>.

A défaut de réalisation de cette condition dans le délai imparti, les présentes seront caduques de plein droit.