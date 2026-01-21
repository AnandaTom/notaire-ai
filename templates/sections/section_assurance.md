## Assurance

{% if assurance %}

{% if assurance.multirisque_habitation %}
### Assurance multirisque habitation

{{ assurance.multirisque_habitation.description }}

{% if assurance.multirisque_habitation.compagnie %}
- **Compagnie** : {{ assurance.multirisque_habitation.compagnie }}
{% endif %}
{% if assurance.multirisque_habitation.numero_police %}
- **Numéro de police** : {{ assurance.multirisque_habitation.numero_police }}
{% endif %}
{% if assurance.multirisque_habitation.echeance %}
- **Échéance** : {{ assurance.multirisque_habitation.echeance }}
{% endif %}

{% if assurance.multirisque_habitation.transfert %}
Le contrat d'assurance pourra être transféré à l'ACQUÉREUR conformément aux dispositions légales.
{% else %}
L'ACQUÉREUR devra souscrire sa propre assurance multirisque habitation.
{% endif %}
{% endif %}

{% if assurance.copropriete %}
### Assurance de la copropriété

L'immeuble est assuré au titre de la copropriété auprès de <<<VAR_START>>>{{ assurance.copropriete.compagnie }}<<<VAR_END>>>{% if assurance.copropriete.numero_police %}, police numéro <<<VAR_START>>>{{ assurance.copropriete.numero_police }}<<<VAR_END>>>{% endif %}.

Cette assurance couvre les parties communes et la responsabilité civile de la copropriété.
{% endif %}

{% if assurance.pno %}
### Assurance propriétaire non occupant (PNO)

{% if assurance.pno.existe %}
{{ assurance.pno.description }}
{% else %}
Le VENDEUR déclare ne pas avoir souscrit d'assurance propriétaire non occupant.
{% endif %}
{% endif %}

{% else %}
L'ACQUÉREUR est informé de son obligation de souscrire une assurance multirisque habitation couvrant sa responsabilité civile et les dommages au bien.

L'immeuble en copropriété fait l'objet d'une assurance collective souscrite par le syndic, conformément aux dispositions de la loi du 10 juillet 1965.
{% endif %}

{% if assurance and assurance.remarques %}

{{ assurance.remarques }}
{% endif %}
