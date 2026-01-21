## Situation environnementale

{% if situation_environnementale %}

### Installations classées

{% if situation_environnementale.icpe %}
{% if situation_environnementale.icpe.presence %}
Le bien est situé à proximité d'installations classées pour la protection de l'environnement (ICPE) :
{{ situation_environnementale.icpe.details }}
{% else %}
Le VENDEUR déclare qu'à sa connaissance, le bien n'est pas situé dans le périmètre d'une installation classée pour la protection de l'environnement.
{% endif %}
{% endif %}

### Sites et sols pollués

{% if situation_environnementale.sols_pollues %}
{% if situation_environnementale.sols_pollues.concerne %}
Le bien est référencé dans la base de données BASOL/BASIAS des sites et sols pollués.
{% else %}
Le bien n'est pas référencé dans les bases de données BASOL et BASIAS des sites et sols pollués.
{% endif %}
{% endif %}

### Nuisances sonores

{% if situation_environnementale.bruit %}
{% if situation_environnementale.bruit.zone %}
Le bien est situé dans une zone de bruit au sens du plan d'exposition au bruit.
{% endif %}
{% endif %}

{% else %}
Le VENDEUR déclare n'avoir connaissance d'aucune situation environnementale particulière affectant le bien.
{% endif %}
