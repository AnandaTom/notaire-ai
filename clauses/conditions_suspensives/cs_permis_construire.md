{# ============================================================================
   CLAUSE: Condition suspensive d'obtention de permis de construire
   ID: cs_permis_construire
   Catégorie: conditions_suspensives
   Type d'acte: promesse_vente, compromis
   Obligatoire: Non
   Variables requises: projet.description, projet.date_limite
   Source: Ajout - terrain à bâtir
   Date ajout: 2025-01-19
   ============================================================================ #}

Les présentes sont consenties sous la condition suspensive de l'obtention par le BENEFICIAIRE d'un permis de construire pour la réalisation de <<<VAR_START>>>{{ projet.description }}<<<VAR_END>>>.

La demande de permis de construire devra être déposée dans les <<<VAR_START>>>{{ projet.delai_depot_jours | default(30) }}<<<VAR_END>>> jours suivant la signature des présentes.

La condition sera réputée réalisée par l'obtention d'un permis de construire définitif (c'est-à-dire purgé de tout recours) au plus tard le <<<VAR_START>>>{{ projet.date_limite | format_date }}<<<VAR_END>>>.