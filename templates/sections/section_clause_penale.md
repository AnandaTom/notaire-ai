{# ============================================================================
   SECTION CLAUSE PENALE

   Utilisation: {% include 'sections/section_clause_penale.md' %}
   Condition: {% if clause_penale %}

   Variables requises:
   - clause_penale.applicable: true/false
   - clause_penale.montant_promettant: Montant si carence promettant
   - clause_penale.montant_beneficiaire: Montant si carence bénéficiaire
   - clause_penale.pourcentage: Pourcentage du prix (alternatif au montant)
   ============================================================================ #}

### CLAUSE PENALE

{% if clause_penale and clause_penale.applicable %}

Les parties conviennent expressément des clauses pénales suivantes, conformément aux dispositions des articles 1231-5 et suivants du Code civil :

**Inexécution par le PROMETTANT** - Si le PROMETTANT, par sa faute exclusive, refuse de régulariser la vente par acte authentique alors que le BENEFICIAIRE a valablement levé l'option et que toutes les conditions suspensives sont réalisées, le PROMETTANT sera tenu de payer au BENEFICIAIRE, à titre de clause pénale, une somme de **{{ clause_penale.montant_promettant | default(clause_penale.montant | default(0)) | format_nombre }} euros**{% if clause_penale.pourcentage_promettant %} (soit {{ clause_penale.pourcentage_promettant }}% du prix de vente){% endif %}. Cette somme est due indépendamment de toute action en exécution forcée ou en dommages et intérêts complémentaires.

**Inexécution par le BENEFICIAIRE** - Si le BENEFICIAIRE, par sa faute exclusive et après avoir levé l'option, refuse de régulariser la vente alors que toutes les conditions suspensives sont réalisées, le BENEFICIAIRE sera tenu de payer au PROMETTANT, à titre de clause pénale, une somme de **{{ clause_penale.montant_beneficiaire | default(clause_penale.montant | default(0)) | format_nombre }} euros**{% if clause_penale.pourcentage_beneficiaire %} (soit {{ clause_penale.pourcentage_beneficiaire }}% du prix de vente){% endif %}.

{% if indemnite_immobilisation and indemnite_immobilisation.montant %}
{% if clause_penale.cumul_indemnite %}
Cette clause pénale s'ajoute à l'indemnité d'immobilisation qui restera acquise au PROMETTANT.
{% else %}
Cette clause pénale se substitue à l'indemnité d'immobilisation ; le PROMETTANT conservera l'indemnité d'immobilisation à titre de clause pénale, sans pouvoir prétendre à une somme complémentaire.
{% endif %}
{% endif %}

**Mise en œuvre** - La clause pénale ne pourra être mise en œuvre qu'après mise en demeure par lettre recommandée avec accusé de réception restée infructueuse pendant un délai de {{ clause_penale.delai_mise_en_demeure | default(15) }} jours. Conformément à l'article 1231-5 du Code civil, le juge peut modérer ou augmenter la pénalité si elle est manifestement excessive ou dérisoire.

{% else %}

Les parties n'ont pas souhaité stipuler de clause pénale au sens des articles 1231-5 et suivants du Code civil. En cas d'inexécution par l'une des parties, l'autre ne pourra prétendre qu'aux dommages et intérêts de droit commun.

{% endif %}

