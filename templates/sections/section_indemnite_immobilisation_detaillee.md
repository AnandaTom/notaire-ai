{# ============================================================================
   SECTION INDEMNITE D'IMMOBILISATION - VERSION DETAILLEE

   Utilisation: {% include 'sections/section_indemnite_immobilisation_detaillee.md' %}
   Condition: {% if indemnite_immobilisation %}

   Variables requises:
   - indemnite_immobilisation.montant: Montant en euros
   - indemnite_immobilisation.pourcentage: Pourcentage du prix (ex: 10)
   - indemnite_immobilisation.sequestre: "notaire" ou "agent"
   - indemnite_immobilisation.mode_paiement: "virement", "cheque", etc.
   - indemnite_immobilisation.date_versement: Date limite de versement
   ============================================================================ #}

### INDEMNITE D'IMMOBILISATION

En contrepartie de l'immobilisation du bien pendant la durée de la présente promesse, le BENEFICIAIRE s'oblige à verser au PROMETTANT, à titre d'indemnité d'immobilisation, une somme de **{{ indemnite_immobilisation.montant | default(0) | format_nombre }} euros** ({{ indemnite_immobilisation.montant | default(0) | montant_en_lettres }}){% if indemnite_immobilisation.pourcentage %}, soit **{{ indemnite_immobilisation.pourcentage }}%** du prix de vente convenu{% endif %}.

{% if indemnite_immobilisation.mode_paiement == "virement" %}
Cette somme sera versée **par virement bancaire** au compte séquestre du notaire soussigné (IBAN : {{ notaire.iban | default("[IBAN à compléter]") }}).
{% elif indemnite_immobilisation.mode_paiement == "cheque" %}
Cette somme sera versée **par chèque de banque** libellé à l'ordre de « {{ notaire.nom | default("Maître [NOM]") }}, Notaire - Compte Séquestre ».
{% else %}
Cette somme sera versée selon les modalités convenues entre les parties.
{% endif %}

**Date limite de versement :** {{ indemnite_immobilisation.date_versement | default("dans les 8 jours suivant la signature des présentes") }}.

{% if indemnite_immobilisation.verse_ce_jour %}
Le BENEFICIAIRE déclare avoir versé ce jour ladite somme entre les mains du notaire soussigné, qui le reconnaît.
{% endif %}

{% if indemnite_immobilisation.sequestre == "notaire" %}
Cette somme sera conservée par le notaire soussigné, qui en sera **séquestre** jusqu'à la réalisation ou la caducité de la présente promesse, conformément aux dispositions de l'article 1956 du Code civil. Le notaire séquestre ne pourra se dessaisir de cette somme que pour l'imputer sur le prix de vente, pour la restituer au BENEFICIAIRE ou la verser au PROMETTANT dans les cas prévus ci-après, sur accord exprès des deux parties, ou sur décision de justice définitive.
{% elif indemnite_immobilisation.sequestre == "agent" %}
Cette somme sera conservée par {{ agent_immobilier.nom | default("l'agent immobilier") }}, agent immobilier, qui en sera **séquestre** jusqu'à la réalisation ou la caducité de la présente promesse.
{% endif %}

**Sort de l'indemnité :**

**A)** *En cas de réalisation de la vente* : l'indemnité d'immobilisation s'imputera sur le prix de vente et viendra en déduction du solde à payer lors de la signature de l'acte authentique.

**B)** *En cas de rétractation dans le délai légal* : conformément à l'article L271-1 du Code de la construction et de l'habitation, si le BENEFICIAIRE exerce son droit de rétractation dans le délai de dix jours, l'indemnité lui sera intégralement restituée dans un délai de vingt et un jours. Toute clause contraire est réputée non écrite.

**C)** *En cas de non-réalisation d'une condition suspensive* : si l'une des conditions suspensives ne se réalise pas sans faute du BENEFICIAIRE, l'indemnité lui sera intégralement restituée dans un délai de {{ indemnite_immobilisation.delai_restitution | default(15) }} jours.

**D)** *En cas de carence du BENEFICIAIRE* : si le BENEFICIAIRE, par sa faute, ne lève pas l'option ou ne réitère pas la vente alors que toutes les conditions sont réalisées, l'indemnité sera acquise de plein droit au PROMETTANT à titre de dédommagement forfaitaire et définitif.

**E)** *En cas de carence du PROMETTANT* : si le PROMETTANT refuse de réitérer la vente alors que le BENEFICIAIRE a valablement levé l'option, l'indemnité sera restituée au BENEFICIAIRE qui pourra en outre poursuivre l'exécution forcée ou réclamer des dommages et intérêts.

{% if indemnite_immobilisation.interets and indemnite_immobilisation.interets.applicable %}
L'indemnité d'immobilisation produira intérêts au taux légal à compter de {{ indemnite_immobilisation.interets.date_debut | default("la date de versement") }}.
{% endif %}

