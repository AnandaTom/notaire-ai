## NÉGOCIATION

{% if negociation %}
La présente vente a été négociée par l'intermédiaire de :
- **Agence** : <<<VAR_START>>>{{ negociation.agence }}<<<VAR_END>>>
- **Adresse** : {{ negociation.adresse }}
{% if negociation.honoraires %}
- **Honoraires** : <<<VAR_START>>>{{ negociation.honoraires | format_nombre }}<<<VAR_END>>> EUR {{ negociation.honoraires_charge }}
{% endif %}
{% if negociation.carte_professionnelle %}
- **Carte professionnelle** : {{ negociation.carte_professionnelle }}
{% endif %}
{% else %}
La présente vente a été conclue sans l'intermédiaire d'un agent immobilier.
{% endif %}
