## Servitudes

{% if servitudes and servitudes.declarations %}
Le VENDEUR déclare :

{% if servitudes.declarations.aucune %}
qu'à sa connaissance, le bien n'est grevé d'aucune servitude autre que celles résultant de la situation des lieux et de la destination du père de famille, et qu'il n'existe aucune servitude conventionnelle susceptible de limiter l'usage ou la jouissance du bien.
{% endif %}

{% if servitudes.declarations.detail %}
{{ servitudes.declarations.detail }}
{% endif %}

{% if servitudes.liste and servitudes.liste|length > 0 %}
Les servitudes suivantes grèvent le bien :

{% for servitude in servitudes.liste %}
- **{{ servitude.type | capitalize }}** : {{ servitude.description }}
  {% if servitude.titre_constitutif %}(constituée par {{ servitude.titre_constitutif }}){% endif %}
{% endfor %}
{% endif %}

{% if servitudes.passives and servitudes.passives|length > 0 %}
Le bien bénéficie des servitudes actives suivantes :

{% for servitude in servitudes.passives %}
- **{{ servitude.type | capitalize }}** : {{ servitude.description }}
{% endfor %}
{% endif %}

{% else %}
Le VENDEUR déclare qu'à sa connaissance, le bien n'est grevé d'aucune servitude autre que celles résultant de la situation des lieux et de la destination du père de famille.
{% endif %}

{% if servitudes and servitudes.remarques %}

{{ servitudes.remarques }}
{% endif %}
