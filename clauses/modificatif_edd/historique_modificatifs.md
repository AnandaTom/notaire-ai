{# ============================================================================
   CLAUSE: Historique des modificatifs antérieurs
   ID: historique_modificatifs
   Catégorie: modificatif_edd
   Type d'acte: modificatif_edd
   Obligatoire: Oui
   Variables requises: edd_origine, historique_modificatifs
   Source: Trame modificatif EDD
   Date ajout: 2025-01-19
   ============================================================================ #}

Le règlement de copropriété et l'état descriptif de division ont été établis par acte reçu le <<<VAR_START>>>{{ edd_origine.date | format_date }}<<<VAR_END>>> par <<<VAR_START>>>{{ edd_origine.notaire }}<<<VAR_END>>>, publié au service de publicité foncière de <<<VAR_START>>>{{ edd_origine.publication_spf.service }}<<<VAR_END>>> le <<<VAR_START>>>{{ edd_origine.publication_spf.date | format_date }}<<<VAR_END>>>, volume <<<VAR_START>>>{{ edd_origine.publication_spf.volume }}<<<VAR_END>>>, numéro <<<VAR_START>>>{{ edd_origine.publication_spf.numero }}<<<VAR_END>>>.

{% if historique_modificatifs | length > 0 %}
Ils ont été modifiés par :
{% for modif in historique_modificatifs %}
- Acte reçu le <<<VAR_START>>>{{ modif.date | format_date }}<<<VAR_END>>> par <<<VAR_START>>>{{ modif.notaire }}<<<VAR_END>>>, publié le <<<VAR_START>>>{{ modif.publication_spf.date | format_date }}<<<VAR_END>>>, volume <<<VAR_START>>>{{ modif.publication_spf.volume }}<<<VAR_END>>>, n° <<<VAR_START>>>{{ modif.publication_spf.numero }}<<<VAR_END>>>, ayant pour objet : <<<VAR_START>>>{{ modif.objet }}<<<VAR_END>>>.
{% endfor %}
{% endif %}