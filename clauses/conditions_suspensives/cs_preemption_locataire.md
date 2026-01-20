{# ============================================================================
   CLAUSE: Réserve du droit de préemption du locataire
   ID: cs_preemption_locataire
   Catégorie: conditions_suspensives
   Type d'acte: promesse_vente, compromis
   Obligatoire: Oui
   Variables requises: locataire.nom
   Source: Ajout - bien loué
   Date ajout: 2025-01-19
   ============================================================================ #}

{%- if bien.loue == true -%}

Le PROMETTANT déclare que le bien est actuellement donné en location à <<<VAR_START>>>{{ locataire.nom }}<<<VAR_END>>>.

Conformément aux dispositions de l'article 15-II de la loi du 6 juillet 1989, le locataire bénéficie d'un droit de préemption.

Le PROMETTANT s'engage à notifier au locataire son intention de vendre dans les formes légales. Les présentes sont consenties sous réserve de la non-exercice de ce droit par le locataire dans le délai légal.

{%- endif -%}