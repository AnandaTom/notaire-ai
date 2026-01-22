{# Section: Contrat d'affichage et Absence d'opération de construction #}
{# Variables requises: contrat_affichage.*, construction_recente.* #}

## Contrat d'affichage

{% if contrat_affichage %}

{% if contrat_affichage.existe %}
Le VENDEUR déclare qu'un contrat d'affichage publicitaire a été consenti sur le bien vendu.

**Caractéristiques du contrat :**
{% if contrat_affichage.type %}
- **Type de contrat** : {{ contrat_affichage.type }}
{% endif %}
{% if contrat_affichage.duree %}
- **Durée** : {{ contrat_affichage.duree }}
{% endif %}
{% if contrat_affichage.loyer %}
- **Loyer annuel** : <<<VAR_START>>>{{ contrat_affichage.loyer | format_nombre }}<<<VAR_END>>> EUR
{% endif %}
{% if contrat_affichage.beneficiaire %}
- **Bénéficiaire** : {{ contrat_affichage.beneficiaire }}
{% endif %}
{% if contrat_affichage.date %}
- **Date du contrat** : {{ contrat_affichage.date }}
{% endif %}
{% if contrat_affichage.echeance %}
- **Date d'échéance** : {{ contrat_affichage.echeance }}
{% endif %}
{% if contrat_affichage.redevance %}
- **Redevance** : <<<VAR_START>>>{{ contrat_affichage.redevance | format_nombre }}<<<VAR_END>>> EUR
{% endif %}

{% if contrat_affichage.transfert %}
L'ACQUÉREUR est informé que ce contrat d'affichage lui sera transféré de plein droit à compter de la date de réalisation de la vente. Il s'engage à en respecter les termes et conditions jusqu'à son terme.
{% else %}
L'ACQUÉREUR déclare avoir été informé de l'existence de ce contrat et s'engage à en respecter les termes.
{% endif %}

{% else %}
Le VENDEUR déclare qu'aucun contrat d'affichage publicitaire n'a été consenti sur le bien vendu.
{% endif %}

{% else %}
Le VENDEUR déclare qu'aucun contrat d'affichage publicitaire n'a été consenti sur le bien vendu.
{% endif %}

### Absence d'opération de construction ou de rénovation depuis dix ans

{% if construction_recente %}

{% if construction_recente.existe %}
Le VENDEUR déclare que des travaux de construction ou de rénovation importante ont été réalisés sur le bien au cours des dix dernières années.

{% if construction_recente.details %}
**Détails des travaux réalisés :**

{{ construction_recente.details }}
{% endif %}

{% if construction_recente.date_achevement %}
**Date d'achèvement des travaux** : {{ construction_recente.date_achevement }}
{% endif %}

{% if construction_recente.entreprise %}
**Entreprise ayant réalisé les travaux** : {{ construction_recente.entreprise }}
{% endif %}

En conséquence, la garantie décennale prévue aux articles 1792 et suivants du Code civil est susceptible de couvrir d'éventuels désordres affectant le bien jusqu'à l'expiration du délai de dix ans à compter de la réception des travaux.

{% if construction_recente.garanties %}
Les garanties suivantes sont applicables :

{{ construction_recente.garanties }}
{% endif %}

{% if construction_recente.attestation_assurance %}
Une attestation d'assurance décennale est annexée au présent acte.
{% endif %}

{% else %}
Le VENDEUR déclare qu'aucune opération de construction ou de rénovation importante n'a été réalisée sur le bien depuis plus de dix ans.

En conséquence, aucune garantie décennale n'est susceptible de couvrir d'éventuels désordres affectant le bien.
{% endif %}

{% else %}
Le VENDEUR déclare qu'à sa connaissance, aucune opération de construction ou de rénovation importante n'a été réalisée sur le bien depuis plus de dix ans.

En conséquence, aucune garantie décennale n'est susceptible de couvrir d'éventuels désordres affectant le bien. L'ACQUÉREUR en prend acte et renonce à tout recours contre le VENDEUR de ce chef.
{% endif %}
