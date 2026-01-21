## Syndic de l'immeuble

{% if copropriete and copropriete.syndic %}

La copropriété est actuellement gérée par :
- **Syndic** : <<<VAR_START>>>{{ copropriete.syndic.nom }}<<<VAR_END>>>
- **Adresse** : {{ copropriete.syndic.adresse }}
{% if copropriete.syndic.telephone %}
- **Telephone** : {{ copropriete.syndic.telephone }}
{% endif %}
{% if copropriete.syndic.email %}
- **Email** : {{ copropriete.syndic.email }}
{% endif %}

{% if copropriete.syndic.mandat_debut and copropriete.syndic.mandat_fin %}
Le mandat du syndic court du {{ copropriete.syndic.mandat_debut }} au {{ copropriete.syndic.mandat_fin }}.
{% endif %}

{% endif %}

### Etat contenant diverses informations sur la copropriété

{% if copropriete %}

Conformement aux dispositions de l'article L 721-2 du Code de la construction et de l'habitation, le VENDEUR a remis a l'ACQUEREUR un etat contenant les informations suivantes :

{% if copropriete.fiche_synthetique %}
- La fiche synthetique de la copropriete
{% endif %}
{% if copropriete.reglement %}
- Le reglement de copropriete et l'etat descriptif de division
{% endif %}
{% if copropriete.carnet_entretien %}
- Le carnet d'entretien de l'immeuble
{% endif %}
- Les proces-verbaux des trois dernieres assemblees generales
- Le montant des charges courantes du budget previsionnel
- Les sommes susceptibles d'etre dues au syndicat par l'acquereur

{% endif %}

### Absence de convocation à une assemblée générale entre l'avant-contrat et la vente

{% if copropriete and copropriete.ag %}

{% if copropriete.ag.convocation_recue %}
Le VENDEUR declare avoir recu une convocation a une assemblee generale entre la signature de l'avant-contrat et celle du present acte.
L'ordre du jour de cette assemblee a ete communique a l'ACQUEREUR.
{% else %}
Le VENDEUR declare n'avoir recu aucune convocation a une assemblee generale entre la signature de l'avant-contrat et celle du present acte.
{% endif %}

{% endif %}
