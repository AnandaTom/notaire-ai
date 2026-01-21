## Notification de la mutation au syndic – Article 20 loi 10 juillet 1965

Conformément aux dispositions de l'article 20 de la loi du 10 juillet 1965, le notaire soussigné notifiera au syndic de la copropriété la présente mutation dans les meilleurs délais.

{% if copropriete and copropriete.syndic %}
Cette notification sera adressée à :
- **{{ copropriete.syndic.nom }}**
- {{ copropriete.syndic.adresse }}
{% endif %}

Le syndic disposera d'un délai de quinze jours pour former opposition au versement des fonds.
