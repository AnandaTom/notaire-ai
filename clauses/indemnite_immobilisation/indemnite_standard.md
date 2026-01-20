{# ============================================================================
   CLAUSE: Indemnité d'immobilisation - Standard (10%)
   ID: indemnite_standard
   Catégorie: indemnite_immobilisation
   Type d'acte: promesse_vente
   Obligatoire: Oui
   Variables requises: indemnite.montant, indemnite.pourcentage, indemnite.mode_paiement, indemnite.delai_versement, indemnite.sequestre
   Source: Trame promesse unilatérale de vente
   Date ajout: 2025-01-19
   ============================================================================ #}

En considération de la promesse formelle conférée au BENEFICIAIRE par le PROMETTANT, les parties conviennent de fixer le montant de l'indemnité d'immobilisation à la somme forfaitaire de <<<VAR_START>>>{{ indemnite.montant | montant_en_lettres }}<<<VAR_END>>> (<<<VAR_START>>>{{ indemnite.montant | format_nombre }}<<<VAR_END>>> EUR), représentant <<<VAR_START>>>{{ indemnite.pourcentage }}<<<VAR_END>>>% du prix de vente.

Cette indemnité sera versée par <<<VAR_START>>>{{ indemnite.mode_paiement }}<<<VAR_END>>> dans les <<<VAR_START>>>{{ indemnite.delai_versement }}<<<VAR_END>>> jours suivant l'expiration du délai de rétractation, entre les mains de <<<VAR_START>>>{{ indemnite.sequestre }}<<<VAR_END>>>.

**Sort de l'indemnité :**
- En cas de réalisation de la vente : elle s'imputera sur le prix.
- En cas de non-réalisation du fait du BENEFICIAIRE (hors conditions suspensives) : elle restera acquise au PROMETTANT à titre d'indemnité forfaitaire.
- En cas de non-réalisation du fait du PROMETTANT ou de réalisation d'une condition suspensive : elle sera restituée au BENEFICIAIRE.