## Impôts et taxes

### Impôts locaux

{% if impots and impots.taxe_fonciere %}
**Taxe foncière** : Le montant de la taxe foncière pour l'année en cours s'élève à <<<VAR_START>>>{{ impots.taxe_fonciere.montant | format_nombre }}<<<VAR_END>>> EUR.
{% if impots.taxe_fonciere.prorata %}

L'ACQUÉREUR règle ce jour au VENDEUR qui le reconnaît, à la comptabilité de l'office notarial, le prorata de taxe foncière {% if impots.taxe_fonciere.taxe_ordures %}et de taxe d'enlèvement des ordures ménagères{% endif %}, déterminé par convention entre les parties sur le montant de la dernière imposition.
{% endif %}
{% else %}
L'ACQUÉREUR règle ce jour au VENDEUR qui le reconnaît, à la comptabilité de l'office notarial, les proratas de taxes foncières et, le cas échéant, de taxes d'enlèvement des ordures ménagères, déterminés par convention entre les parties sur le montant de la dernière imposition.
{% endif %}

{% if impots and impots.taxe_habitation %}
**Taxe d'habitation** : {% if impots.taxe_habitation.applicable %}Le montant de la taxe d'habitation pour l'année en cours s'élève à <<<VAR_START>>>{{ impots.taxe_habitation.montant | format_nombre }}<<<VAR_END>>> EUR.{% else %}Non applicable - Résidence principale exonérée.{% endif %}
{% endif %}

{% if impots and impots.remarques %}

{{ impots.remarques }}
{% endif %}
