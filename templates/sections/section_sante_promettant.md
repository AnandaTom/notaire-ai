{# Section Santé du Promettant — Viager (Articles 1974-1975 Code civil) #}
{# Activée si: prix.type_vente == "viager" #}

# SANTÉ DU PROMETTANT – AVERTISSEMENT

Le **PROMETTANT** (ci-après dénommé le **CRÉDIRENTIER**) déclare :

{% if promettants[0].sante and promettants[0].sante.certificat_medical and promettants[0].sante.certificat_medical.existe %}
- Qu'un certificat médical a été établi le {{ promettants[0].sante.certificat_medical.date | format_date }}{% if promettants[0].sante.certificat_medical.medecin %} par {{ promettants[0].sante.certificat_medical.medecin }}{% endif %}, attestant que le promettant est en état de santé normal pour son âge.
{% else %}
- Qu'il ne produit pas de certificat médical, mais déclare être en état de santé normal pour son âge.
{% endif %}

**AVERTISSEMENT** (Articles 1974 et 1975 du Code civil) :

Conformément à l'article 1975 du Code civil, le contrat de rente viagère sera **nul** si, au moment de sa conclusion, le crédirentier était atteint d'une maladie dont il est décédé dans les vingt jours de la date du contrat.

Les parties déclarent avoir été parfaitement informées de cette disposition légale et de ses conséquences.

{% if promettants[0].sante and promettants[0].sante.declaration_sante %}
Le **PROMETTANT** déclare en outre :
{% if not promettants[0].sante.declaration_sante.maladies_graves %}
- Ne pas être atteint de maladie grave connue à ce jour.
{% endif %}
{% if not promettants[0].sante.declaration_sante.hospitalisation_recente %}
- Ne pas avoir été hospitalisé récemment.
{% endif %}
{% endif %}
