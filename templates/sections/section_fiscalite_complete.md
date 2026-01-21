## Contribution de sécurité immobilière

La contribution de sécurité immobilière, prévue par l'article 879 du Code général des impôts, est exigible sur la formalité fusionnée de publicité foncière.

{% if fiscalite.contribution_securite_immobiliere %}
**Montant de la contribution** : <<<VAR_START>>>{{ fiscalite.contribution_securite_immobiliere.montant | format_nombre }}<<<VAR_END>>> EUR

{% if fiscalite.contribution_securite_immobiliere.base_calcul %}
**Base de calcul** : <<<VAR_START>>>{{ fiscalite.contribution_securite_immobiliere.base_calcul | format_nombre }}<<<VAR_END>>> EUR

**Taux applicable** : <<<VAR_START>>>{{ fiscalite.contribution_securite_immobiliere.taux }}<<<VAR_END>>> %
{% endif %}

{% if fiscalite.contribution_securite_immobiliere.paiement %}
La contribution sera acquittée par <<<VAR_START>>>{{ fiscalite.contribution_securite_immobiliere.debiteur | default("l'ACQUEREUR") }}<<<VAR_END>>>.
{% endif %}
{% else %}
Le montant de la contribution sera déterminé par le service de la publicité foncière lors de l'accomplissement de la formalité.

Conformément aux dispositions de l'article 879 du Code général des impôts, le taux applicable est de **0,10%** de la valeur vénale ou déclarée des biens ou droits transmis.
{% endif %}

### Exonérations et réductions

{% if fiscalite.contribution_securite_immobiliere.exoneration %}
Le présent acte bénéficie d'une exonération de contribution de sécurité immobilière en application de <<<VAR_START>>>{{ fiscalite.contribution_securite_immobiliere.exoneration.fondement }}<<<VAR_END>>>.
{% elif fiscalite.contribution_securite_immobiliere.reduction %}
Le présent acte bénéficie d'une réduction de contribution de sécurité immobilière :
- Fondement : <<<VAR_START>>>{{ fiscalite.contribution_securite_immobiliere.reduction.fondement }}<<<VAR_END>>>
- Taux réduit : <<<VAR_START>>>{{ fiscalite.contribution_securite_immobiliere.reduction.taux }}<<<VAR_END>>> %
{% else %}
Aucune exonération ou réduction n'est applicable au présent acte.
{% endif %}

## Droits de mutation

### Droits d'enregistrement

Conformément aux dispositions des articles 683 et suivants du Code général des impôts, la présente mutation est soumise aux droits d'enregistrement.

{% if fiscalite.droits_mutation %}
**Régime fiscal applicable** : <<<VAR_START>>>{{ fiscalite.droits_mutation.regime }}<<<VAR_END>>>

{% if fiscalite.droits_mutation.regime == 'droit_commun' %}
#### Droit commun

**Taux global** : <<<VAR_START>>>{{ fiscalite.droits_mutation.taux_global }}<<<VAR_END>>> %

Décomposition :
- Droit départemental : <<<VAR_START>>>{{ fiscalite.droits_mutation.taux_departemental | default(4.50) }}<<<VAR_END>>> %
- Droit communal : <<<VAR_START>>>{{ fiscalite.droits_mutation.taux_communal | default(1.20) }}<<<VAR_END>>> %
- Prélèvement pour frais d'assiette : <<<VAR_START>>>{{ fiscalite.droits_mutation.prelevement | default(2.37) }}<<<VAR_END>>> %

**Base de calcul** : <<<VAR_START>>>{{ fiscalite.droits_mutation.base_calcul | format_nombre }}<<<VAR_END>>> EUR

**Montant des droits** : <<<VAR_START>>>{{ fiscalite.droits_mutation.montant | format_nombre }}<<<VAR_END>>> EUR

{% elif fiscalite.droits_mutation.regime == 'tva' %}
#### Régime de la TVA

Le bien relève du régime de la TVA en application de <<<VAR_START>>>{{ fiscalite.droits_mutation.fondement_tva }}<<<VAR_END>>>.

**Taux de TVA applicable** : <<<VAR_START>>>{{ fiscalite.droits_mutation.taux_tva }}<<<VAR_END>>> %

{% if fiscalite.droits_mutation.tva_sur_marge %}
##### TVA sur marge

La TVA est applicable sur la marge conformément à l'article 268 du Code général des impôts.

- Prix de vente : <<<VAR_START>>>{{ prix.montant | format_nombre }}<<<VAR_END>>> EUR
- Prix d'acquisition par le vendeur : <<<VAR_START>>>{{ fiscalite.droits_mutation.prix_acquisition | format_nombre }}<<<VAR_END>>> EUR
- **Marge taxable** : <<<VAR_START>>>{{ fiscalite.droits_mutation.marge | format_nombre }}<<<VAR_END>>> EUR
- **Montant de TVA** : <<<VAR_START>>>{{ fiscalite.droits_mutation.montant_tva | format_nombre }}<<<VAR_END>>> EUR
{% else %}
**Base de calcul TVA** : <<<VAR_START>>>{{ fiscalite.droits_mutation.base_calcul_tva | format_nombre }}<<<VAR_END>>> EUR

**Montant de TVA** : <<<VAR_START>>>{{ fiscalite.droits_mutation.montant_tva | format_nombre }}<<<VAR_END>>> EUR
{% endif %}

**Droit d'enregistrement réduit** : <<<VAR_START>>>{{ fiscalite.droits_mutation.droit_reduit }}<<<VAR_END>>> EUR (taxe de publicité foncière)

{% endif %}

### Paiement des droits

Les droits de mutation seront acquittés par <<<VAR_START>>>{{ fiscalite.droits_mutation.debiteur | default("l'ACQUEREUR") }}<<<VAR_END>>>.

{% if fiscalite.droits_mutation.modalites_paiement %}
Modalités : {{ fiscalite.droits_mutation.modalites_paiement }}
{% endif %}

{% else %}
Les droits de mutation seront calculés et acquittés lors de l'enregistrement de l'acte.

Le taux applicable dans le département de <<<VAR_START>>>{{ bien.adresse.departement }}<<<VAR_END>>> est de **{{ fiscalite.taux_departemental_par_defaut | default("5.81") }}%** (droit commun).
{% endif %}

### Déclaration de valeur

Conformément à l'article 27 du décret n° 55-22 du 4 janvier 1955, les parties déclarent que la valeur vénale réelle des biens transmis s'élève à <<<VAR_START>>>{{ prix.montant | format_nombre }}<<<VAR_END>>> EUR.

Cette déclaration servira de base au calcul des droits de mutation.

{% if fiscalite.abattements %}
### Abattements fiscaux

{% for abattement in fiscalite.abattements %}
**{{ abattement.type }}**
- Fondement : <<<VAR_START>>>{{ abattement.fondement }}<<<VAR_END>>>
- Montant : <<<VAR_START>>>{{ abattement.montant | format_nombre }}<<<VAR_END>>> EUR
- Impact : {{ abattement.description }}
{% endfor %}
{% endif %}
