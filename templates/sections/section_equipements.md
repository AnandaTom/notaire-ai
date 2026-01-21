## Équipements

{% if equipements %}

{% if equipements.chauffage %}
### Chauffage

{% if equipements.chauffage.type %}
- **Type** : {{ equipements.chauffage.type | capitalize }}
{% endif %}
{% if equipements.chauffage.energie %}
- **Énergie** : {{ equipements.chauffage.energie | capitalize }}
{% endif %}
{% if equipements.chauffage.individuel != None %}
- **Mode** : {{ "Individuel" if equipements.chauffage.individuel else "Collectif" }}
{% endif %}
{% if equipements.chauffage.description %}
- {{ equipements.chauffage.description }}
{% endif %}
{% endif %}

{% if equipements.eau %}
### Eau

{% if equipements.eau.froide %}
- **Eau froide** : {{ equipements.eau.froide }}
{% endif %}
{% if equipements.eau.chaude %}
- **Eau chaude** : {{ equipements.eau.chaude }}
{% endif %}
{% if equipements.eau.compteur_individuel != None %}
- {{ "Compteur individuel" if equipements.eau.compteur_individuel else "Compteur collectif" }}
{% endif %}
{% endif %}

{% if equipements.electricite %}
### Électricité

{{ equipements.electricite }}
{% endif %}

{% if equipements.gaz %}
### Gaz

{{ equipements.gaz }}
{% endif %}

{% if equipements.assainissement %}
### Assainissement

{{ equipements.assainissement }}
{% endif %}

{% if equipements.ventilation %}
### Ventilation

{{ equipements.ventilation }}
{% endif %}

{% if equipements.telecommunications %}
### Télécommunications

{{ equipements.telecommunications }}
{% endif %}

{% if equipements.securite and equipements.securite|length > 0 %}
### Sécurité

{% for element in equipements.securite %}
- {{ element }}
{% endfor %}
{% endif %}

{% if equipements.confort and equipements.confort|length > 0 %}
### Équipements de confort

{% for element in equipements.confort %}
- {{ element }}
{% endfor %}
{% endif %}

{% if equipements.divers %}
### Divers

{{ equipements.divers }}
{% endif %}

{% else %}
Le bien dispose des équipements conformes à son usage et à sa destination.
{% endif %}

{% if equipements and equipements.remarques %}

{{ equipements.remarques }}
{% endif %}
