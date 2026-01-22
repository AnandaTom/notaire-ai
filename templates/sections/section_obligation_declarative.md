## Obligation declarative du proprietaire de bien a usage d'habitation

{% if obligation_declarative %}

Conformement aux dispositions de l'article 1649 quater-0 B bis du Code general des impots, le proprietaire d'un bien immobilier a usage d'habitation doit declarer a l'administration fiscale l'identite des occupants de ce bien.

{% if obligation_declarative.effectuee %}
Le VENDEUR declare avoir effectue cette declaration aupres de l'administration fiscale.

{% if obligation_declarative.date %}
**Date de declaration** : <<<VAR_START>>>{{ obligation_declarative.date }}<<<VAR_END>>>
{% endif %}
{% else %}
Le VENDEUR s'engage a effectuer cette declaration dans les delais legaux.
{% endif %}

L'ACQUEREUR est informe qu'il devra egalement proceder a cette declaration d'occupation dans le mois suivant la prise de possession du bien.

{% else %}
Conformement aux dispositions de l'article 1649 quater-0 B bis du Code general des impots, le proprietaire d'un bien immobilier a usage d'habitation doit declarer a l'administration fiscale l'identite des occupants de ce bien.

L'ACQUEREUR est informe qu'il devra proceder a cette declaration d'occupation dans le mois suivant la prise de possession du bien.
{% endif %}
