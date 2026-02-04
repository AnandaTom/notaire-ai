{# Section: SÉQUESTRE — Dépôt de garantie / consignation #}
{# Applicable: Toutes catégories (copro, hors-copro, terrain) #}
{# Condition: sequestre ou indemnite_immobilisation #}

{% if sequestre or indemnite_immobilisation %}
# SÉQUESTRE

{% if sequestre and sequestre.depositaire %}
Le séquestre des fonds est confié à {{ sequestre.depositaire }}{% if sequestre.qualite %}, {{ sequestre.qualite }}{% endif %}.
{% else %}
Le séquestre des fonds est confié au notaire rédacteur des présentes, constitué séquestre et dépositaire.
{% endif %}

{% if indemnite_immobilisation %}
## Dépôt de garantie

Le **BENEFICIAIRE** s'oblige à verser, à titre de dépôt de garantie, la somme de **{{ indemnite_immobilisation.montant | montant_en_lettres }}** ({{ indemnite_immobilisation.montant | format_nombre }} EUR){% if indemnite_immobilisation.pourcentage %}, soit {{ indemnite_immobilisation.pourcentage }}% du prix de vente{% endif %}.

Ce versement devra être effectué par virement bancaire au plus tard dans le délai de {{ indemnite_immobilisation.delai_versement | default("QUINZE (15) jours") }} suivant {% if indemnite_immobilisation.point_depart %}{{ indemnite_immobilisation.point_depart }}{% else %}l'expiration du délai de rétractation{% endif %}.

À cet effet, avec l'accord des parties, cette somme sera versée en la comptabilité du notaire rédacteur des présentes{% if acte and acte.notaire %} au sein de la {{ acte.notaire.societe }} susnommée{% endif %}, constitué séquestre et dépositaire du dépôt de garantie ci-dessus prévu. L'encaissement par lui du virement vaudra acceptation de sa mission de tiers séquestre.

De convention expresse entre les parties, cette somme sera affectée à titre de nantissement conformément aux dispositions des articles 2355 et suivants du Code civil entre les mains du **SÉQUESTRE** en qualité de tiers dépositaire, par le **PROMETTANT** au profit du **BENEFICIAIRE** qui accepte, à la garantie de la restitution éventuelle de la somme versée.

**Faute pour le BENEFICIAIRE de satisfaire à cette obligation de versement dans le délai ci-dessus, sans qu'il soit nécessaire d'effectuer une mise en demeure par le PROMETTANT, ce dernier sera libéré, si bon lui semble, de son engagement de vendre par le seul fait de la constatation de l'absence de virement total ou partiel du dépôt de garantie dans le délai susvisé, la présente clause étant une clause résolutoire de plein droit des présentes.**

Les parties reconnaissent être informées :
* **qu'il est possible de faire virer par l'établissement bancaire du BENEFICIAIRE la somme due au titre du dépôt de garantie en mentionnant les noms et références de l'office notarial destinataire du virement, étant précisé que la date du crédit au compte de l'office notarial fera foi entre les parties,**
* **que la responsabilité de l'Office Notarial destinataire du virement ne pourra en aucun cas être engagée en cas de non-respect par le BENEFICIAIRE de son obligation, et que**
* **passé le délai limite octroyé au BENEFICIAIRE pour effectuer le virement du dépôt de garantie, le PROMETTANT devra s'assurer auprès de l'office notarial destinataire de ce virement, la confirmation que celui-ci a bien été effectué.**
{% endif %}

## Récapitulatif du séquestre

| Élément | Détail |
| :---- | :---- |
{% if indemnite_immobilisation %}| Montant du dépôt de garantie | {{ indemnite_immobilisation.montant | format_nombre }} EUR{% if indemnite_immobilisation.pourcentage %} ({{ indemnite_immobilisation.pourcentage }}% du prix){% endif %} |
{% endif %}| Dépositaire | {{ sequestre.depositaire | default("Notaire rédacteur des présentes") }} |
{% if sequestre and sequestre.qualite %}| Qualité | {{ sequestre.qualite }} |
{% endif %}{% if indemnite_immobilisation %}| Délai de versement | {{ indemnite_immobilisation.delai_versement | default("QUINZE (15) jours") }} |
| Point de départ | {{ indemnite_immobilisation.point_depart | default("Expiration du délai de rétractation") }} |
{% endif %}| Mode de versement | Virement bancaire |

## Mission du séquestre

La mission du séquestre sera la suivante :

1° Il remettra cette somme au **PROMETTANT** pour imputation sur le prix convenu, en cas de réalisation de la vente, objet de la promesse de vente.

2° Il restituera cette somme au **BENEFICIAIRE** si la promesse est frappée de caducité faute de réalisation dans le délai convenu, en cas de résolution provoquée par l'exercice de la faculté de rétractation ou résultant de la mise en œuvre d'une des conditions stipulées au profit du **PROMETTANT**, telle que la clause résolutoire ci-dessus prévue.

3° Il remettra également cette somme au **BENEFICIAIRE** dans tous les cas où la non-réalisation de la vente résulterait de la défaillance de l'une quelconque des conditions suspensives ci-dessous stipulées et auxquelles le **BENEFICIAIRE** n'aurait pas renoncé.

4° Il remettra cette somme au **PROMETTANT** au cas où, la présente promesse n'étant frappée ni de caducité ni de résolution pour l'un des motifs indiqués ci-dessus, le **BENEFICIAIRE** n'aurait pas levé l'option dans les délais et conditions prévus.

Toutefois cette mission ne pourra s'exécuter que d'un commun accord entre les parties ou en vertu d'une décision judiciaire passée en force de chose jugée.

En cas d'opposition ou de difficulté, le séquestre devra verser la somme dont il est dépositaire à la Caisse des Dépôts et Consignations avec indication de l'affectation ci-dessus stipulée.

Ces paiements, restitution ou consignation, selon le cas, vaudront au séquestre pleine et entière décharge de sa mission.

{% if sequestre.compte_bancaire %}
## Coordonnées bancaires du séquestre

| Élément | Valeur |
| :---- | :---- |
{% if sequestre.compte_bancaire.banque %}| Banque | {{ sequestre.compte_bancaire.banque }} |
{% endif %}{% if sequestre.compte_bancaire.iban %}| IBAN | {{ sequestre.compte_bancaire.iban }} |
{% endif %}{% if sequestre.compte_bancaire.bic %}| BIC | {{ sequestre.compte_bancaire.bic }} |
{% endif %}{% if sequestre.compte_bancaire.titulaire %}| Titulaire | {{ sequestre.compte_bancaire.titulaire }} |
{% endif %}
{% endif %}

{% endif %}
