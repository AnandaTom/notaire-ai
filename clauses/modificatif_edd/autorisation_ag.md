{# ============================================================================
   CLAUSE: Autorisation de l'assemblée générale
   ID: autorisation_ag
   Catégorie: modificatif_edd
   Type d'acte: modificatif_edd
   Obligatoire: Oui
   Variables requises: assemblee_generale.date, assemblee_generale.resolution_numero, assemblee_generale.objet, assemblee_generale.majorite_requise, assemblee_generale.vote
   Source: Trame modificatif EDD
   Date ajout: 2025-01-19
   ============================================================================ #}

L'assemblée générale des copropriétaires de l'immeuble susvisé, réunie le <<<VAR_START>>>{{ assemblee_generale.date | format_date }}<<<VAR_END>>>, a adopté la résolution n° <<<VAR_START>>>{{ assemblee_generale.resolution_numero }}<<<VAR_END>>> ainsi libellée :

« <<<VAR_START>>>{{ assemblee_generale.objet }}<<<VAR_END>>> »

Cette résolution a été adoptée à la majorité de l'<<<VAR_START>>>{{ assemblee_generale.majorite_requise }}<<<VAR_END>>> de la loi du 10 juillet 1965, avec :
- Voix POUR : <<<VAR_START>>>{{ assemblee_generale.vote.pour }}<<<VAR_END>>> tantièmes
- Voix CONTRE : <<<VAR_START>>>{{ assemblee_generale.vote.contre }}<<<VAR_END>>> tantièmes
- ABSTENTIONS : <<<VAR_START>>>{{ assemblee_generale.vote.abstention }}<<<VAR_END>>> tantièmes

Cette résolution étant devenue définitive, le syndic est habilité à faire procéder à la publication du présent acte modificatif.