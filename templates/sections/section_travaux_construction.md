## Existence de travaux

{% if travaux %}

{% if travaux.recents %}
### Travaux récents

Des travaux ont été réalisés sur le bien au cours des dix dernières années :

{% for travail in travaux.recents %}
- **{{ travail.nature }}** ({{ travail.date }})
  {% if travail.entreprise %}Entreprise : {{ travail.entreprise }}{% endif %}
  {% if travail.montant %}Montant : <<<VAR_START>>>{{ travail.montant | format_nombre }}<<<VAR_END>>> EUR{% endif %}
{% endfor %}
{% endif %}

{% if travaux.garantie_decennale %}
### Garantie décennale

{% if travaux.garantie_decennale.applicable %}
Les travaux sont couverts par la garantie décennale prévue aux articles 1792 et suivants du Code civil.

{% if travaux.garantie_decennale.assurance %}
- **Assureur** : <<<VAR_START>>>{{ travaux.garantie_decennale.assurance.compagnie }}<<<VAR_END>>>
- **Police n°** : <<<VAR_START>>>{{ travaux.garantie_decennale.assurance.numero }}<<<VAR_END>>>
- **Date d'expiration** : <<<VAR_START>>>{{ travaux.garantie_decennale.date_expiration }}<<<VAR_END>>>
{% endif %}

Le VENDEUR garantit que les travaux ont été réalisés conformément aux règles de l'art et aux normes en vigueur.
{% else %}
Aucun travaux soumis à la garantie décennale n'a été réalisé au cours des dix dernières années.
{% endif %}
{% endif %}

{% if travaux.dommages_ouvrage %}
### Assurance dommages-ouvrage

{% if travaux.dommages_ouvrage.existe %}
Une assurance dommages-ouvrage a été souscrite pour les travaux réalisés.

- **Assureur** : <<<VAR_START>>>{{ travaux.dommages_ouvrage.assureur }}<<<VAR_END>>>
- **Police n°** : <<<VAR_START>>>{{ travaux.dommages_ouvrage.numero_police }}<<<VAR_END>>>
{% else %}
Aucune assurance dommages-ouvrage n'a été souscrite, les travaux n'étant pas soumis à cette obligation.
{% endif %}
{% endif %}

{% else %}
Le VENDEUR déclare qu'aucune opération de construction ou de rénovation soumise aux garanties des articles 1792 et suivants du Code civil n'a été réalisée depuis dix ans.
{% endif %}

{% if travaux and travaux.article_1792 %}

### Rappel des articles 1792 et suivants du Code civil

**Article 1792 du Code civil** : Tout constructeur d'un ouvrage est responsable de plein droit, envers le maître ou l'acquéreur de l'ouvrage, des dommages, même résultant d'un vice du sol, qui compromettent la solidité de l'ouvrage ou qui, l'affectant dans l'un de ses éléments constitutifs ou l'un de ses éléments d'équipement, le rendent impropre à sa destination.

Une telle responsabilité n'a point lieu si le constructeur prouve que les dommages proviennent d'une cause étrangère.

**Article 1792-2** : La présomption de responsabilité établie par l'article 1792 s'étend également aux dommages qui affectent la solidité des éléments d'équipement d'un ouvrage, mais seulement lorsque ceux-ci font indissociablement corps avec les ouvrages de viabilité, de fondation, d'ossature, de clos ou de couvert.

**Article 1792-3** : Les autres éléments d'équipement de l'ouvrage font l'objet d'une garantie de bon fonctionnement d'une durée minimale de deux ans à compter de la réception.

{% endif %}
