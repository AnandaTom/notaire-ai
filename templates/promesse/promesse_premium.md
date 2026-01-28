{# Template Promesse Premium - Diagnostics exhaustifs, localisation détaillée #}
{# Source: Trame_promesse_B.docx #}
{# Bookmarks: 359 | Cas: Agences, transactions professionnelles #}

{% extends "promesse_base.md" %}

{% block type_promesse %}premium{% endblock %}

{% block titre %}
# PROMESSE UNILATÉRALE DE VENTE

**Vente d'un lot de copropriété - Version Premium**
{% endblock %}

{% block contenu_principal %}

{% include 'sections/promesse/entete_promesse.md' %}

{% include 'sections/promesse/identification_parties.md' %}

{# Support étendu des situations matrimoniales (24 variantes) #}
{% include 'sections/promesse/qualite_capacite_etendu.md' %}

{% include 'sections/promesse/designation_bien.md' %}

{# Localisation détaillée sur 7 lignes (spécifique premium) #}
{% if bien.localisation_detaillee %}
{% include 'sections/promesse/localisation_detaillee.md' %}
{% endif %}

{% if bien.copropriete %}
{% include 'sections/promesse/copropriete.md' %}
{% endif %}

{% if bien.lots %}
{% include 'sections/promesse/lots_copropriete.md' %}
{% endif %}

{% include 'sections/promesse/origine_propriete.md' %}

{% include 'sections/promesse/situation_locative.md' %}

{% include 'sections/promesse/prix_paiement.md' %}

{# Agent immobilier (fréquent en premium) #}
{% if agent_immobilier and agent_immobilier.intervient %}
{% include 'sections/promesse/mandat_agent.md' %}
{% endif %}

{% if financement and financement.pret %}
{% include 'sections/promesse/condition_suspensive_pret.md' %}
{% endif %}

{% if conditions_suspensives and conditions_suspensives.vente_prealable %}
{% include 'sections/promesse/condition_suspensive_vente.md' %}
{% endif %}

{% if conditions_suspensives and conditions_suspensives.urbanisme %}
{% include 'sections/promesse/condition_suspensive_urbanisme.md' %}
{% endif %}

{% if indemnite and indemnite.montant > 0 %}
{% include 'sections/promesse/indemnite_immobilisation.md' %}
{% endif %}

{% if sequestre and sequestre.montant > 0 %}
{% include 'sections/promesse/sequestre.md' %}
{% endif %}

{% include 'sections/promesse/conditions_generales.md' %}

{% include 'sections/promesse/clause_penale.md' %}

{# Diagnostics exhaustifs (7 types) - spécifique premium #}
{% include 'sections/promesse/diagnostics_exhaustifs.md' %}

{# Annexes complètes (32) #}
{% include 'sections/promesse/annexes_completes.md' %}

{% include 'sections/promesse/signatures.md' %}

{% endblock %}
