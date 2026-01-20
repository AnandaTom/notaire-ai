{# ============================================================================
   CLAUSE: Convention sur les travaux votés
   ID: convention_travaux
   Catégorie: copropriete
   Type d'acte: promesse_vente, compromis, vente
   Obligatoire: Oui
   Variables requises: acte.date
   Source: Trame promesse unilatérale de vente
   Date ajout: 2025-01-19
   ============================================================================ #}

Les parties conviennent de la répartition suivante des travaux votés en assemblée générale :

**Principe :** Les travaux votés restent à la charge du copropriétaire qui avait cette qualité au jour du vote.

**Application :**
- Travaux votés avant le <<<VAR_START>>>{{ acte.date | format_date }}<<<VAR_END>>> : à la charge du PROMETTANT
- Travaux votés à compter du <<<VAR_START>>>{{ acte.date | format_date }}<<<VAR_END>>> : à la charge du BENEFICIAIRE

Cette convention est inopposable au syndicat des copropriétaires qui pourra réclamer les fonds au copropriétaire inscrit au moment de l'appel.