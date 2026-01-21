## Contrat d'affichage

{% if contrat_affichage %}

{% if contrat_affichage.existe %}
Le VENDEUR déclare qu'un contrat d'affichage publicitaire a été consenti sur le bien vendu :
- **Beneficiaire** : {{ contrat_affichage.beneficiaire }}
- **Date** : {{ contrat_affichage.date }}
- **Duree** : {{ contrat_affichage.duree }}
{% if contrat_affichage.redevance %}
- **Redevance annuelle** : <<<VAR_START>>>{{ contrat_affichage.redevance | format_nombre }}<<<VAR_END>>> EUR
{% endif %}

L'ACQUÉREUR déclare avoir été informé de l'existence de ce contrat et s'engage à en respecter les termes.
{% else %}
Le VENDEUR déclare qu'aucun contrat d'affichage publicitaire n'a été consenti sur le bien vendu.
{% endif %}

{% else %}
Le VENDEUR déclare qu'aucun contrat d'affichage publicitaire n'a été consenti sur le bien vendu.
{% endif %}
