## Les lots de copropriété suivants :

{% for lot in bien.lots %}

### Lot numéro {{ loop.index }}

**Numéro du lot** : <<<VAR_START>>>{{ lot.numero }}<<<VAR_END>>>

{% if lot.designation %}
**Désignation** : {{ lot.designation }}
{% endif %}

**Composition** :
{% if lot.composition %}
{{ lot.composition }}
{% else %}
- Type : <<<VAR_START>>>{{ lot.type }}<<<VAR_END>>>
- Situation : <<<VAR_START>>>{{ lot.situation }}<<<VAR_END>>>
{% if lot.etage %}- Étage : <<<VAR_START>>>{{ lot.etage }}<<<VAR_END>>>{% endif %}
{% if lot.nombre_pieces %}- Nombre de pièces : <<<VAR_START>>>{{ lot.nombre_pieces }}<<<VAR_END>>>{% endif %}
{% endif %}

{% if lot.surface_carrez %}
**Surface privative** : <<<VAR_START>>>{{ lot.surface_carrez }}<<<VAR_END>>> m² (loi Carrez)

{% if lot.attestation_mesurage %}
Attestation de mesurage établie le <<<VAR_START>>>{{ lot.attestation_mesurage.date | format_date }}<<<VAR_END>>> par <<<VAR_START>>>{{ lot.attestation_mesurage.professionnel }}<<<VAR_END>>>.
{% endif %}
{% endif %}

{% if lot.surface_totale %}
**Surface totale** : <<<VAR_START>>>{{ lot.surface_totale }}<<<VAR_END>>> m²
{% endif %}

**Quote-part des parties communes** : <<<VAR_START>>>{{ lot.tantiemes.quote_part }}<<<VAR_END>>> / <<<VAR_START>>>{{ lot.tantiemes.total }}<<<VAR_END>>>

{% if lot.tantiemes.detail %}
Soit :
- Tantièmes généraux : <<<VAR_START>>>{{ lot.tantiemes.generaux }}<<<VAR_END>>> / <<<VAR_START>>>{{ lot.tantiemes.total_generaux }}<<<VAR_END>>>
{% if lot.tantiemes.speciaux %}- Tantièmes spéciaux : <<<VAR_START>>>{{ lot.tantiemes.speciaux }}<<<VAR_END>>> / <<<VAR_START>>>{{ lot.tantiemes.total_speciaux }}<<<VAR_END>>>{% endif %}
{% endif %}

{% if lot.annexes %}
**Dépendances** :
{% for annexe in lot.annexes %}
- {{ annexe.type }} n° <<<VAR_START>>>{{ annexe.numero }}<<<VAR_END>>>{% if annexe.surface %} ({{ annexe.surface }} m²){% endif %}
{% endfor %}
{% endif %}

{% if lot.charges_annuelles %}
**Charges annuelles moyennes** : <<<VAR_START>>>{{ lot.charges_annuelles | format_nombre }}<<<VAR_END>>> EUR
{% endif %}

{% endfor %}

## Plans des lots

{% if bien.plans %}
Les plans des lots vendus sont annexés aux présentes.

{% for plan in bien.plans %}
**{{ plan.type }}** : {{ plan.description }}
- Date : <<<VAR_START>>>{{ plan.date | format_date }}<<<VAR_END>>>
- Auteur : <<<VAR_START>>>{{ plan.auteur }}<<<VAR_END>>>
{% if plan.echelle %}- Échelle : <<<VAR_START>>>{{ plan.echelle }}<<<VAR_END>>>{% endif %}

**Annexe n°{{ loop.index }}** : Plan {{ plan.type | lower }}
{% endfor %}

{% if bien.plans_conformite %}
Les acquéreurs déclarent avoir pris connaissance des plans et les acceptent.
{% endif %}
{% else %}
Les plans des lots seront fournis ultérieurement et annexés à l'acte authentique de vente.
{% endif %}

{% if bien.modificatifs_plans %}
## Modificatifs des plans

{% for modif in bien.modificatifs_plans %}
Modificatif n° <<<VAR_START>>>{{ modif.numero }}<<<VAR_END>>> établi le <<<VAR_START>>>{{ modif.date | format_date }}<<<VAR_END>>> par <<<VAR_START>>>{{ modif.auteur }}<<<VAR_END>>>.

Objet : {{ modif.objet }}

**Annexe** : Modificatif de plan n° {{ modif.numero }}
{% endfor %}
{% endif %}
