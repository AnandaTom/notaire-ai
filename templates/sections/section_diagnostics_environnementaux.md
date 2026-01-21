## Diagnostics environnementaux

### Etat des risques

{% if erp %}
Un état des risques et pollutions a été établi le <<<VAR_START>>>{{ erp.date }}<<<VAR_END>>> conformément aux dispositions des articles L 125-5 et R 125-23 à R 125-27 du Code de l'environnement.

{% if erp.risques_naturels and erp.risques_naturels|length > 0 %}
**Risques naturels identifiés** :
{% for risque in erp.risques_naturels %}
- {{ risque }}
{% endfor %}
{% endif %}

{% if erp.risques_technologiques and erp.risques_technologiques|length > 0 %}
**Risques technologiques identifiés** :
{% for risque in erp.risques_technologiques %}
- {{ risque }}
{% endfor %}
{% endif %}

{% if erp.pollution_sols %}
**Pollution des sols** : Le terrain d'assiette est situé dans un secteur d'information sur les sols.
{% endif %}

{% endif %}

### Absence de sinistres avec indemnisation

{% if sinistres %}
{% if sinistres.liste and sinistres.liste|length > 0 %}
Le VENDEUR déclare que le bien a fait l'objet des sinistres suivants ayant donné lieu à indemnisation au titre des catastrophes naturelles ou technologiques :
{% for sinistre in sinistres.liste %}
- {{ sinistre.type }} - {{ sinistre.date }} - Indemnisation : {{ sinistre.indemnisation }}
{% endfor %}
{% else %}
Le VENDEUR déclare qu'à sa connaissance, le bien n'a fait l'objet d'aucun sinistre ayant donné lieu à indemnisation au titre des articles L 125-5 ou L 128-2 du Code des assurances.
{% endif %}
{% else %}
Le VENDEUR déclare qu'à sa connaissance, le bien n'a fait l'objet d'aucun sinistre ayant donné lieu à indemnisation au titre des articles L 125-5 ou L 128-2 du Code des assurances.
{% endif %}
