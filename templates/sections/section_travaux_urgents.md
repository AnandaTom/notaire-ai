## Travaux urgents décidés par le syndic (article 18 de la loi du 10 juillet 1965)

{% if copropriete and copropriete.travaux_urgents %}
Le syndic a fait procéder aux travaux urgents suivants :
{% for travail in copropriete.travaux_urgents %}
- {{ travail.nature }} ({{ travail.date }}) : <<<VAR_START>>>{{ travail.montant | format_nombre }}<<<VAR_END>>> EUR
{% endfor %}
{% else %}
Le VENDEUR déclare qu'aucun travaux urgent n'a été décidé par le syndic depuis son acquisition.
{% endif %}
