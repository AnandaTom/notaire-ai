## Contrats de distribution et de fourniture

{% if contrats_fourniture and contrats_fourniture.liste and contrats_fourniture.liste|length > 0 %}
Les contrats de distribution et de fourniture suivants sont en cours :

{% for contrat in contrats_fourniture.liste %}
- **{{ contrat.type | capitalize }}** : {{ contrat.description }}
  {% if contrat.fournisseur %}Fournisseur : {{ contrat.fournisseur }}{% endif %}
  {% if contrat.transfert %}Le contrat sera transféré à l'acquéreur à la date de la vente.{% endif %}
{% endfor %}
{% else %}
Le VENDEUR déclare qu'il n'existe aucun contrat de distribution ou de fourniture en cours, à l'exception des contrats usuels d'eau, d'électricité et de télécommunications qui seront transférés ou résiliés selon les modalités habituelles.
{% endif %}

{% if contrats_fourniture and contrats_fourniture.energie %}
### Contrats d'énergie

{% if contrats_fourniture.energie.electricite %}
**Électricité** : {{ contrats_fourniture.energie.electricite }}
{% endif %}

{% if contrats_fourniture.energie.gaz %}
**Gaz** : {{ contrats_fourniture.energie.gaz }}
{% endif %}

{% if contrats_fourniture.energie.chauffage %}
**Chauffage collectif** : {{ contrats_fourniture.energie.chauffage }}
{% endif %}
{% endif %}

{% if contrats_fourniture and contrats_fourniture.remarques %}

{{ contrats_fourniture.remarques }}
{% endif %}
