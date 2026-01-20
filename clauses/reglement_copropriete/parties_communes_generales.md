{# ============================================================================
   CLAUSE: Définition des parties communes générales
   ID: parties_communes_generales
   Catégorie: reglement_copropriete
   Type d'acte: reglement_copropriete, modificatif_edd
   Obligatoire: Oui
   Variables requises: immeuble.cadastre
   Source: Trame reglement copropriete EDD
   Date ajout: 2025-01-19
   ============================================================================ #}

Sont parties communes générales :

- Le sol de la parcelle cadastrée <<<VAR_START>>>{{ immeuble.cadastre[0].section }}<<<VAR_END>>> n° <<<VAR_START>>>{{ immeuble.cadastre[0].numero }}<<<VAR_END>>>
- Les cours, parcs et jardins
- Les voies d'accès et passages communs
- Le gros œuvre des bâtiments (fondations, murs porteurs, planchers structurels, toiture)
- Les façades et leurs revêtements
- Les halls d'entrée, vestibules et circulations communes
- Les escaliers et leurs cages
- Les locaux communs (local poubelles, local vélos, chaufferie)
- Les canalisations principales (eau, gaz, électricité, chauffage)
- Les antennes collectives et leurs câblages
- Tous éléments d'équipement commun