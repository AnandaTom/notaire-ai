## Règlement définitif des charges

{% if copropriete and copropriete.reglement_charges %}
Le règlement définitif des charges de l'exercice {{ copropriete.reglement_charges.exercice }} a été approuvé par l'assemblée générale du {{ copropriete.reglement_charges.date_ag }}.
{% if copropriete.reglement_charges.solde %}
Le solde {{ "créditeur" if copropriete.reglement_charges.solde > 0 else "débiteur" }} s'élève à <<<VAR_START>>>{{ copropriete.reglement_charges.solde | abs | format_nombre }}<<<VAR_END>>> EUR.
{% endif %}
{% else %}
Le règlement définitif des charges de l'exercice antérieur a été approuvé. Aucun solde n'est dû.
{% endif %}

## Solde de l'exercice antérieur

{% if copropriete and copropriete.solde_anterieur %}
{{ copropriete.solde_anterieur }}
{% else %}
Les comptes de l'exercice antérieur ont été soldés.
{% endif %}

## Absence d'avances

{% if copropriete and copropriete.avances %}
Des avances ont été versées au syndicat des copropriétaires pour un montant de <<<VAR_START>>>{{ copropriete.avances.montant | format_nombre }}<<<VAR_END>>> EUR.
{% else %}
Le VENDEUR déclare n'avoir versé aucune avance au syndicat des copropriétaires.
{% endif %}
