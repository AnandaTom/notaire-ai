## Urbanisme

{% if urbanisme %}

{% if urbanisme.plu %}
### Plan local d'urbanisme (PLU)

Le bien est situé en zone <<<VAR_START>>>{{ urbanisme.plu.zonage }}<<<VAR_END>>> du Plan Local d'Urbanisme.

{% if urbanisme.plu.coefficient_occupation %}
- **Coefficient d'occupation des sols** : <<<VAR_START>>>{{ urbanisme.plu.coefficient_occupation }}<<<VAR_END>>>
{% endif %}

{% if urbanisme.plu.hauteur_maximale %}
- **Hauteur maximale autorisée** : <<<VAR_START>>>{{ urbanisme.plu.hauteur_maximale }}<<<VAR_END>>> mètres
{% endif %}

{% if urbanisme.plu.emprise_sol %}
- **Emprise au sol maximale** : <<<VAR_START>>>{{ urbanisme.plu.emprise_sol }}<<<VAR_END>>> %
{% endif %}

{% if urbanisme.plu.usage_autorise %}
L'usage actuel du bien ({{ bien.usage_actuel }}) est conforme au zonage PLU.
{% endif %}
{% endif %}

{% if urbanisme.servitudes_utilite_publique and urbanisme.servitudes_utilite_publique|length > 0 %}
### Servitudes d'utilité publique

Le bien est grevé des servitudes d'utilité publique suivantes :

{% for servitude in urbanisme.servitudes_utilite_publique %}
- **{{ servitude.type | capitalize }}** : {{ servitude.description }}
  {% if servitude.reference %}(Référence : {{ servitude.reference }}){% endif %}
{% endfor %}
{% endif %}

{% if urbanisme.droit_preemption %}
### Droit de préemption urbain

{% if urbanisme.droit_preemption.applicable %}
Le bien est situé dans un périmètre soumis au droit de préemption urbain.

La déclaration d'intention d'aliéner (DIA) a été déposée.
{% if urbanisme.droit_preemption.renonciation %}
La collectivité a renoncé à exercer son droit de préemption.
{% endif %}
{% else %}
Le bien n'est pas situé dans un périmètre soumis au droit de préemption urbain.
{% endif %}
{% endif %}

{% else %}
Le bien est conforme aux règles d'urbanisme en vigueur.
{% endif %}
