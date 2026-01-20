{# ============================================================================
   CLAUSE: Réserve du droit de préemption urbain
   ID: cs_preemption_urbain
   Catégorie: conditions_suspensives
   Type d'acte: promesse_vente, compromis, vente
   Obligatoire: Oui
   Variables requises: bien.adresse.ville
   Source: Trame vente lots de copropriété
   Date ajout: 2025-01-19
   ============================================================================ #}

{%- if bien.zone_dpu == true -%}

Les présentes sont consenties sous réserve de l'exercice éventuel par la commune de <<<VAR_START>>>{{ bien.adresse.ville }}<<<VAR_END>>> ou son délégataire de son droit de préemption urbain.

La déclaration d'intention d'aliéner sera adressée au titulaire du droit de préemption dans les plus brefs délais.

A défaut de réponse dans le délai légal de deux mois, le titulaire du droit de préemption sera réputé avoir renoncé à l'exercice de son droit.

{%- endif -%}