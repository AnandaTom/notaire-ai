{# ============================================================================
   CLAUSE: Condition suspensive de prêt - Standard
   ID: cs_pret_standard
   Catégorie: conditions_suspensives
   Type d'acte: promesse_vente, compromis
   Obligatoire: Non
   Variables requises: pret.montant, pret.duree_mois, pret.taux_maximum, pret.date_limite_obtention
   Source: Trame promesse unilatérale de vente lots de copropriété
   Date ajout: 2025-01-19
   ============================================================================ #}

La présente promesse est consentie sous la condition suspensive de l'obtention par le BENEFICIAIRE d'un ou plusieurs prêts d'un montant maximum de <<<VAR_START>>>{{ pret.montant | montant_en_lettres }}<<<VAR_END>>> (<<<VAR_START>>>{{ pret.montant | format_nombre }}<<<VAR_END>>> EUR), remboursable sur une durée minimale de <<<VAR_START>>>{{ pret.duree_mois }}<<<VAR_END>>> mois, au taux nominal maximum de <<<VAR_START>>>{{ pret.taux_maximum }}<<<VAR_END>>>% l'an, hors assurance.

Le BENEFICIAIRE s'engage à déposer au moins <<<VAR_START>>>{{ pret.nombre_demandes | default(2) }}<<<VAR_END>>> demandes de prêt dans les <<<VAR_START>>>{{ pret.delai_depot_jours | default(15) }}<<<VAR_END>>> jours suivant la signature des présentes.

La condition suspensive sera réalisée en cas d'obtention par le BENEFICIAIRE d'une ou plusieurs offres écrites de prêt aux conditions sus-indiquées au plus tard le <<<VAR_START>>>{{ pret.date_limite_obtention | format_date }}<<<VAR_END>>>.