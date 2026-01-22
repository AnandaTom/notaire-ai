## Consultation de bases de donnees environnementales

{% if consultation_bases %}

Le notaire soussigne a procede aux consultations suivantes :

{% if consultation_bases.georisques %}
### Base Georisques

La base Georisques a ete consultee le <<<VAR_START>>>{{ consultation_bases.georisques.date }}<<<VAR_END>>>.
{% if consultation_bases.georisques.resultat %}
Resultat : {{ consultation_bases.georisques.resultat }}
{% endif %}
{% endif %}

{% if consultation_bases.cadastre %}
### Cadastre

Le plan cadastral a ete consulte via le portail cadastre.gouv.fr.
{% endif %}

{% if consultation_bases.pprt %}
### Plan de Prevention des Risques Technologiques (PPRT)

{% if consultation_bases.pprt.applicable %}
Le bien est situe dans le perimetre d'un PPRT.
{% else %}
Le bien n'est pas situe dans le perimetre d'un PPRT.
{% endif %}
{% endif %}

{% else %}
Le notaire soussigne a procede aux consultations des bases de donnees environnementales disponibles (Georisques, cadastre). Les resultats de ces consultations sont integres dans l'Etat des Risques et Pollutions (ERP) annexe au present acte.
{% endif %}
