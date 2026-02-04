{# Section: ÉVÉNEMENT SANITAIRE — Clause COVID / force majeure #}
{# Applicable: Toutes catégories (copro, hors-copro, terrain) #}
{# Condition: evenement_sanitaire #}
{# Source: PUV GUNTZER GAUTIER (document original anonymisé) #}

{% if evenement_sanitaire and evenement_sanitaire.applicable %}
# Prise en compte d'un événement sanitaire

{% if evenement_sanitaire.type %}
Compte tenu de {{ evenement_sanitaire.type | default("la situation sanitaire") }}{% if evenement_sanitaire.reference_texte %} et des dispositions {{ evenement_sanitaire.reference_texte }}{% endif %}, les parties conviennent des dispositions suivantes :
{% else %}
Les parties conviennent que tout événement sanitaire exceptionnel (pandémie, épidémie, mesures gouvernementales de confinement ou de restriction) pourra affecter l'exécution des présentes dans les conditions suivantes :
{% endif %}

## Prorogation des délais

{% if evenement_sanitaire.prorogation %}
En cas de survenance d'un événement sanitaire rendant impossible ou excessivement difficile l'accomplissement des formalités prévues aux présentes, les délais stipulés seront prorogés d'une durée égale à celle de l'empêchement, majorée de {{ evenement_sanitaire.prorogation.delai_supplementaire | default("QUINZE (15) jours") }}.

{% if evenement_sanitaire.prorogation.delai_maximum %}
La prorogation ne pourra toutefois excéder {{ evenement_sanitaire.prorogation.delai_maximum }}.
{% endif %}
{% else %}
En cas de survenance d'un tel événement, les délais stipulés aux présentes seront automatiquement prorogés d'une durée égale à celle de l'empêchement, sans que cette prorogation puisse excéder six (6) mois.
{% endif %}

## Impact sur les conditions suspensives

Les conditions suspensives seront réputées prorogées dans les mêmes conditions que les délais principaux.

{% if evenement_sanitaire.notification %}
La partie invoquant l'événement sanitaire devra en informer l'autre partie par tout moyen écrit dans un délai de {{ evenement_sanitaire.notification.delai | default("HUIT (8) jours") }} à compter de la survenance de l'événement.
{% endif %}

{% if evenement_sanitaire.resolution %}
## Résolution

Si l'événement sanitaire devait se prolonger au-delà de {{ evenement_sanitaire.resolution.delai_max | default("six (6) mois") }} à compter de la date des présentes, chacune des parties pourra demander la résolution des présentes sans indemnité, le dépôt de garantie étant alors restitué au **BENEFICIAIRE**.
{% endif %}

{% endif %}
