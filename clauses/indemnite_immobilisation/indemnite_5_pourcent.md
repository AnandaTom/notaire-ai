{# ============================================================================
   CLAUSE: Indemnité d'immobilisation - 5%
   ID: indemnite_5_pourcent
   Catégorie: indemnite_immobilisation
   Type d'acte: promesse_vente
   Obligatoire: Non
   Variables requises: indemnite.montant, indemnite.motif_reduction
   Source: Ajout - cas particulier
   Date ajout: 2025-01-19
   ============================================================================ #}

En considération de la promesse formelle conférée au BENEFICIAIRE, les parties conviennent exceptionnellement de fixer le montant de l'indemnité d'immobilisation à la somme de <<<VAR_START>>>{{ indemnite.montant | montant_en_lettres }}<<<VAR_END>>> (<<<VAR_START>>>{{ indemnite.montant | format_nombre }}<<<VAR_END>>> EUR), représentant 5% du prix de vente.

Le PROMETTANT accepte ce montant réduit compte tenu de <<<VAR_START>>>{{ indemnite.motif_reduction }}<<<VAR_END>>>.

Les autres dispositions relatives à l'indemnité restent inchangées.