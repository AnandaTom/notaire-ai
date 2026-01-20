{# ============================================================================
   CLAUSE: Servitude de cour commune
   ID: cour_commune
   Catégorie: servitudes_copropriete
   Type d'acte: reglement_copropriete, vente
   Obligatoire: Non
   Variables requises: servitude.fonds_beneficiaire_adresse
   Source: Ajout - cour commune
   Date ajout: 2025-01-19
   ============================================================================ #}

Une servitude de cour commune a été établie au profit de l'immeuble voisin situé <<<VAR_START>>>{{ servitude.fonds_beneficiaire_adresse }}<<<VAR_END>>>.

Cette servitude interdit toute construction à moins de <<<VAR_START>>>{{ servitude.distance_minimum | default(3) }}<<<VAR_END>>> mètres de la limite séparative.

Elle a été constituée par acte reçu le <<<VAR_START>>>{{ servitude.date_constitution }}<<<VAR_END>>> et publiée au service de publicité foncière.

Le bénéficiaire de cette servitude participe aux charges d'entretien de la cour dans la proportion définie à l'acte constitutif.