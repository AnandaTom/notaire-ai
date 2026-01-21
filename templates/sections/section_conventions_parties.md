## Convention des parties sur la répartition des charges et travaux

{% if conventions_parties %}

Les parties conviennent de la répartition suivante des charges et travaux :

{% if conventions_parties.charges %}
### Charges de copropriété

{{ conventions_parties.charges }}
{% endif %}

{% if conventions_parties.travaux %}
### Travaux votés ou en cours

{{ conventions_parties.travaux }}
{% endif %}

{% else %}
Les parties conviennent que les charges et travaux seront répartis conformément aux dispositions légales et réglementaires en vigueur.
{% endif %}

## Convention des parties sur les procédures

{% if conventions_parties and conventions_parties.procedures %}
{{ conventions_parties.procedures }}
{% else %}
Les parties déclarent n'avoir connaissance d'aucune procédure en cours susceptible d'affecter le bien vendu.
{% endif %}

## Consultation de bases de données environnementales

Le notaire soussigné déclare avoir consulté les bases de données suivantes :
- BASOL : Base de données sur les sites et sols pollués
- BASIAS : Base des anciens sites industriels et activités de service
- Géorisques : Base de données des risques naturels et technologiques

{% if consultation_bases %}
{% if consultation_bases.basol %}
**BASOL** : {{ consultation_bases.basol }}
{% endif %}
{% if consultation_bases.basias %}
**BASIAS** : {{ consultation_bases.basias }}
{% endif %}
{% if consultation_bases.georisques %}
**Géorisques** : {{ consultation_bases.georisques }}
{% endif %}
{% else %}
Ces consultations n'ont pas révélé d'élément particulier concernant le bien vendu.
{% endif %}
