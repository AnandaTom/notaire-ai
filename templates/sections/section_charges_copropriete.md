## Convention des parties sur la repartition des charges et travaux

{% if charges_copropriete %}

Les parties conviennent de la repartition des charges de copropriete comme suit :

{% if charges_copropriete.repartition %}
{{ charges_copropriete.repartition }}
{% endif %}

{% if charges_copropriete.budget_previsionnel or charges_copropriete.appels_fonds %}
### Budget prévisionnel et charges

| Poste | Montant annuel | Observations |
| :---- | ----: | :---- |
{% if charges_copropriete.budget_previsionnel %}{% for poste in charges_copropriete.budget_previsionnel %}| {{ poste.libelle }} | {{ poste.montant | format_nombre }} EUR | {{ poste.observations | default("") }} |
{% endfor %}{% endif %}{% if charges_copropriete.total_annuel %}| **TOTAL charges annuelles** | **{{ charges_copropriete.total_annuel | format_nombre }} EUR** | |
{% endif %}{% if charges_copropriete.quote_part_vendeur %}| Quote-part du lot vendu | {{ charges_copropriete.quote_part_vendeur | format_nombre }} EUR | Dernier exercice approuvé |
{% endif %}

{% endif %}

{% if charges_copropriete.travaux_votes %}
### Travaux votés non encore appelés

| Travaux | Montant voté | Quote-part lot | Date AG |
| :---- | ----: | ----: | :---- |
{% for travail in charges_copropriete.travaux_votes %}| {{ travail.description }} | {{ travail.montant_total | format_nombre }} EUR | {{ travail.quote_part | format_nombre }} EUR | {{ travail.date_ag | default("-") }} |
{% endfor %}

{% endif %}

{% if charges_copropriete.appels_fonds %}
### Appels de fonds

{% for appel in charges_copropriete.appels_fonds %}
- {{ appel.description }} : <<<VAR_START>>>{{ appel.montant | format_nombre }}<<<VAR_END>>> EUR
{% endfor %}
{% endif %}

{% else %}
Les charges de copropriete sont reparties entre le VENDEUR et l'ACQUEREUR au prorata temporis a compter de la date de jouissance.

Le VENDEUR reste redevable des charges correspondant a la periode anterieure a l'entree en jouissance.
{% endif %}

## Convention des parties sur les procedures

{% if procedures_copropriete %}
{{ procedures_copropriete.detail }}
{% else %}
Le VENDEUR declare qu'aucune procedure judiciaire n'est en cours concernant la copropriete ou le lot vendu.
{% endif %}

## Reglement definitif des charges

{% if reglement_charges %}

{% if reglement_charges.effectue %}
Le reglement definitif des charges a ete effectue le <<<VAR_START>>>{{ reglement_charges.date }}<<<VAR_END>>>.
{% if reglement_charges.montant %}
Montant regle : <<<VAR_START>>>{{ reglement_charges.montant | format_nombre }}<<<VAR_END>>> EUR
{% endif %}
{% else %}
Le reglement definitif des charges interviendra apres approbation des comptes par l'assemblee generale.
{% endif %}

{% else %}
Le reglement definitif des charges interviendra selon les modalites prevues par le reglement de copropriete.
{% endif %}

## Solde de l'exercice anterieur

{% if solde_exercice %}
{% if solde_exercice.crediteur %}
Un solde crediteur de <<<VAR_START>>>{{ solde_exercice.montant | format_nombre }}<<<VAR_END>>> EUR est du au VENDEUR.
{% elif solde_exercice.debiteur %}
Un solde debiteur de <<<VAR_START>>>{{ solde_exercice.montant | format_nombre }}<<<VAR_END>>> EUR reste du par le VENDEUR.
{% else %}
Le solde de l'exercice anterieur est equilibre.
{% endif %}
{% else %}
Les comptes de l'exercice anterieur seront regles selon les modalites prevues par le reglement de copropriete.
{% endif %}

## Absence d'avances

{% if avances_copropriete %}
Le VENDEUR declare {% if avances_copropriete.existe %}avoir verse{% else %}ne pas avoir verse{% endif %} d'avances au titre de la copropriete.
{% if avances_copropriete.montant %}
Montant des avances : <<<VAR_START>>>{{ avances_copropriete.montant | format_nombre }}<<<VAR_END>>> EUR
{% endif %}
{% else %}
Le VENDEUR declare ne pas avoir verse d'avances au titre de la copropriete autres que celles mentionnees dans l'etat date.
{% endif %}
