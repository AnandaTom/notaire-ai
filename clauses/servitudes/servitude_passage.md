{# ============================================================================
   CLAUSE: Servitude de passage existante
   ID: servitude_passage
   Catégorie: servitudes
   Type d'acte: promesse_vente, compromis, vente
   Obligatoire: Non
   Variables requises: servitude.beneficiaire, servitude.fonds_dominant_adresse, servitude.origine
   Source: Ajout - bien avec servitude
   Date ajout: 2025-01-19
   ============================================================================ #}

{%- if servitudes.passage == true -%}

Le PROMETTANT déclare que le bien est grevé d'une servitude de passage au profit du fonds appartenant à <<<VAR_START>>>{{ servitude.beneficiaire }}<<<VAR_END>>> situé <<<VAR_START>>>{{ servitude.fonds_dominant_adresse }}<<<VAR_END>>>.

Cette servitude a été établie par <<<VAR_START>>>{{ servitude.origine }}<<<VAR_END>>> et publiée au service de la publicité foncière de <<<VAR_START>>>{{ servitude.publication.service }}<<<VAR_END>>> le <<<VAR_START>>>{{ servitude.publication.date }}<<<VAR_END>>>.

Le BENEFICIAIRE déclare avoir parfaite connaissance de cette servitude et l'accepter.

{%- endif -%}