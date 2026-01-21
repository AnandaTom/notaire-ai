## État du bien

{% if etat_bien %}

{% if etat_bien.description_generale %}
{{ etat_bien.description_generale }}
{% endif %}

{% if etat_bien.occupation %}
### Occupation

{% if etat_bien.occupation.statut == "libre" %}
Le bien est actuellement libre de toute occupation.
{% elif etat_bien.occupation.statut == "occupe" %}
Le bien est actuellement occupé par {{ etat_bien.occupation.occupant }}.
{% if etat_bien.occupation.bail %}
L'occupation fait l'objet d'un bail en date du {{ etat_bien.occupation.bail.date }}{% if etat_bien.occupation.bail.loyer %}, moyennant un loyer mensuel de <<<VAR_START>>>{{ etat_bien.occupation.bail.loyer | format_nombre }}<<<VAR_END>>> EUR{% endif %}.
{% endif %}
{% endif %}
{% endif %}

{% if etat_bien.travaux_recents and etat_bien.travaux_recents|length > 0 %}
### Travaux récents

Les travaux suivants ont été réalisés :

{% for travail in etat_bien.travaux_recents %}
- **{{ travail.nature }}** ({{ travail.date }}){% if travail.montant %} : <<<VAR_START>>>{{ travail.montant | format_nombre }}<<<VAR_END>>> EUR{% endif %}
  {% if travail.description %}{{ travail.description }}{% endif %}
{% endfor %}
{% endif %}

{% if etat_bien.vices_apparents %}
### Vices apparents déclarés

{{ etat_bien.vices_apparents }}
{% endif %}

{% if etat_bien.conformite %}
### Conformité

{% if etat_bien.conformite.electricite %}
- **Installation électrique** : {{ etat_bien.conformite.electricite }}
{% endif %}
{% if etat_bien.conformite.gaz %}
- **Installation gaz** : {{ etat_bien.conformite.gaz }}
{% endif %}
{% if etat_bien.conformite.assainissement %}
- **Assainissement** : {{ etat_bien.conformite.assainissement }}
{% endif %}
{% endif %}

{% if etat_bien.contenance_terrain %}
### Contenance du terrain d'assiette

{{ etat_bien.contenance_terrain }}
{% endif %}

{% else %}
Le bien est vendu dans l'état où il se trouve actuellement, sans garantie particulière quant à son état.
{% endif %}
