{# ============================================================================
   CLAUSE: Condition suspensive de prêt avec PTZ
   ID: cs_pret_ptz
   Catégorie: conditions_suspensives
   Type d'acte: promesse_vente, compromis
   Obligatoire: Non
   Variables requises: pret_principal.montant, ptz.montant, pret.date_limite_obtention
   Source: Ajout notaire - dossier primo-accédant
   Date ajout: 2025-01-19
   ============================================================================ #}

La présente promesse est consentie sous la condition suspensive de l'obtention par le BENEFICIAIRE :
- D'un prêt principal d'un montant maximum de <<<VAR_START>>>{{ pret_principal.montant | montant_en_lettres }}<<<VAR_END>>> (<<<VAR_START>>>{{ pret_principal.montant | format_nombre }}<<<VAR_END>>> EUR),
- D'un prêt à taux zéro (PTZ) d'un montant maximum de <<<VAR_START>>>{{ ptz.montant | montant_en_lettres }}<<<VAR_END>>> (<<<VAR_START>>>{{ ptz.montant | format_nombre }}<<<VAR_END>>> EUR).

La condition suspensive sera réalisée en cas d'obtention de ces prêts au plus tard le <<<VAR_START>>>{{ pret.date_limite_obtention | format_date }}<<<VAR_END>>>.