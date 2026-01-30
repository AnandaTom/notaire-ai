{# Section: DÉCLARATIONS DES PARTIES — Capacité et qualité #}
{# Applicable: Toutes catégories (copro, hors-copro, terrain) #}
{# Condition: Toujours présente (section fixe) #}

# Déclarations des parties sur leur capacité

Les parties, et le cas échéant leurs représentants, attestent que rien ne peut limiter leur capacité pour l'exécution des engagements qu'elles prennent aux présentes, et elles déclarent notamment :

* que leur état civil et leurs qualités indiqués en tête des présentes sont exacts,
* qu'elles ne sont pas en état de cessation de paiement, de rétablissement professionnel, de redressement ou liquidation judiciaire ou sous procédure de sauvegarde des entreprises,
* qu'elles n'ont pas été associées dans une société mise en liquidation judiciaire suivant jugement publié depuis moins de cinq ans et dans laquelle elles étaient tenues indéfiniment et solidairement ou seulement conjointement du passif social, le délai de cinq ans marquant la prescription des actions de droit commun et de celle en recouvrement à l'endroit des associés (BOI-REC-SOLID-20-10-20),
* qu'il n'a été formé aucune opposition au présent acte par un éventuel cogérant,
* qu'elles ne sont concernées :
* par aucune des mesures légales relatives aux personnes protégées qui ne seraient pas révélées aux présentes,
* par aucune des dispositions du Code de la consommation sur le règlement des situations de surendettement, sauf là aussi ce qui peut être spécifié aux présentes,
* et pour le **BENEFICIAIRE** spécialement qu'il n'est, ni à titre personnel, ni en tant qu'associé ou mandataire social, soumis à l'interdiction d'acquérir prévue par l'article 225-26 du Code pénal.

# Documents relatifs à la capacité et à la qualité des parties

Les pièces suivantes ont été portées à la connaissance du rédacteur des présentes à l'appui des déclarations des parties :

{% for promettant in promettants %}
**Concernant {{ promettant.civilite }} {{ promettant.nom }}**

* Carte nationale d'identité.
* Compte rendu de l'interrogation du site bodacc.fr.
{% if promettant.documents_supplementaires %}
{% for doc in promettant.documents_supplementaires %}
* {{ doc }}
{% endfor %}
{% endif %}

{% endfor %}
{% for beneficiaire in beneficiaires %}
**Concernant {{ beneficiaire.civilite }} {{ beneficiaire.nom }}**

* Carte nationale d'identité.
* Compte rendu de l'interrogation du site bodacc.fr.
{% if beneficiaire.documents_supplementaires %}
{% for doc in beneficiaire.documents_supplementaires %}
* {{ doc }}
{% endfor %}
{% endif %}

{% endfor %}

Ces documents ne révèlent aucun empêchement des parties à la signature des présentes.

# Présence - représentation

{% for promettant in promettants %}
- {{ promettant.civilite }} {{ promettant.nom }} est {% if promettant.civilite == "Madame" %}présente{% else %}présent{% endif %} à l'acte{% if promettant.represente_par %}, {% if promettant.civilite == "Madame" %}représentée{% else %}représenté{% endif %} par {{ promettant.represente_par }}{% endif %}.
{% endfor %}
{% for beneficiaire in beneficiaires %}
- {{ beneficiaire.civilite }} {{ beneficiaire.nom }} est {% if beneficiaire.civilite == "Madame" %}présente{% else %}présent{% endif %} à l'acte{% if beneficiaire.represente_par %}, {% if beneficiaire.civilite == "Madame" %}représentée{% else %}représenté{% endif %} par {{ beneficiaire.represente_par }}{% endif %}.
{% endfor %}
