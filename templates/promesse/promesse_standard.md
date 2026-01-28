{# Template Promesse Standard - 1 bien en copropriété simple #}
{# Source: Trame promesse unilatérale de vente lots de copropriété.docx (ORIGINAL) #}
{# Bookmarks: 298 | Cas: 1 vendeur → 1 acquéreur, pas de mobilier #}

{% extends "promesse_base.md" %}

{% block type_promesse %}standard{% endblock %}

{% block titre %}
# PROMESSE UNILATÉRALE DE VENTE

**Vente d'un lot de copropriété**
{% endblock %}

{# Inclure les sections standard #}
{% block contenu_principal %}

{% include 'sections/promesse/entete_promesse.md' %}

{% include 'sections/promesse/identification_parties.md' %}

{% include 'sections/promesse/qualite_capacite.md' %}

{% include 'sections/promesse/designation_bien.md' %}

{% if bien.copropriete %}
{% include 'sections/promesse/copropriete.md' %}
{% endif %}

{% if bien.lots %}
{% include 'sections/promesse/lots_copropriete.md' %}
{% endif %}

{% include 'sections/promesse/origine_propriete.md' %}

{% include 'sections/promesse/situation_locative.md' %}

{% include 'sections/promesse/prix_paiement.md' %}

{% if financement and financement.pret %}
{% include 'sections/promesse/condition_suspensive_pret.md' %}
{% endif %}

{% if indemnite and indemnite.montant > 0 %}
{% include 'sections/promesse/indemnite_immobilisation.md' %}
{% endif %}

{% include 'sections/promesse/conditions_generales.md' %}

{% include 'sections/promesse/clause_penale.md' %}

{% include 'sections/promesse/diagnostics_standard.md' %}

{% include 'sections/promesse/annexes_standard.md' %}

{% include 'sections/promesse/signatures.md' %}

{% endblock %}
