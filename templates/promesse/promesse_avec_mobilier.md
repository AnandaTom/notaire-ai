{# Template Promesse avec Mobilier - Liste des meubles vendus + diagnostics tableau #}
{# Source: Trame_promesse_C.docx #}
{# Bookmarks: 312 | Cas: Vente meublée, appartement avec équipements #}

{% extends "promesse_base.md" %}

{% block type_promesse %}avec_mobilier{% endblock %}

{% block titre %}
# PROMESSE UNILATÉRALE DE VENTE

**Vente d'un lot de copropriété avec mobilier**
{% endblock %}

{% block contenu_principal %}

{% include 'sections/promesse/entete_promesse.md' %}

{% include 'sections/promesse/identification_parties.md' %}

{% include 'sections/promesse/qualite_capacite.md' %}

{% include 'sections/promesse/designation_bien.md' %}

{% if bien.copropriete %}
{% include 'sections/promesse/copropriete.md' %}
{% endif %}

{% if bien.lots %}
{# Version réduite: max 9 lots #}
{% include 'sections/promesse/lots_copropriete_reduit.md' %}
{% endif %}

{# ============================================= #}
{# MOBILIER VENDU - Section spécifique Trame C  #}
{# ============================================= #}
{% if mobilier and mobilier.existe %}

## MOBILIER VENDU

La présente vente comprend également les meubles et objets mobiliers ci-après désignés, dont le BÉNÉFICIAIRE déclare avoir pris connaissance:

| Désignation | État / Valeur |
|-------------|---------------|
{% for item in mobilier.liste %}
| {{ item.designation }} | {{ item.etat }} {% if item.valeur %}/ {{ item.valeur | format_nombre }} EUR{% endif %} |
{% endfor %}

**Prix total du mobilier**: <<<VAR_START>>>{{ mobilier.prix_total | format_nombre }}<<<VAR_END>>> EUR

Ce montant est inclus dans le prix global ci-après stipulé.

Le PROMETTANT garantit que les meubles ci-dessus sont sa propriété exclusive et qu'ils sont libres de tout gage ou privilège.

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

{# ============================================= #}
{# DIAGNOSTICS EN TABLEAU - Spécifique Trame C  #}
{# ============================================= #}

## DOSSIER DE DIAGNOSTICS TECHNIQUES

Les diagnostics techniques obligatoires sont récapitulés dans le tableau ci-après:

| Diagnostic | Réalisé | Date | Validité |
|------------|---------|------|----------|
{% if diagnostics %}
| DPE | {% if diagnostics.dpe %}Oui{% else %}Non{% endif %} | {{ diagnostics.dpe.date | default('-') }} | {{ diagnostics.dpe.validite | default('-') }} |
| Amiante | {% if diagnostics.amiante %}Oui{% else %}Non{% endif %} | {{ diagnostics.amiante.date | default('-') }} | {{ diagnostics.amiante.validite | default('-') }} |
| Plomb (CREP) | {% if diagnostics.plomb %}Oui{% else %}Non{% endif %} | {{ diagnostics.plomb.date | default('-') }} | {{ diagnostics.plomb.validite | default('-') }} |
| Électricité | {% if diagnostics.electricite %}Oui{% else %}Non{% endif %} | {{ diagnostics.electricite.date | default('-') }} | {{ diagnostics.electricite.validite | default('-') }} |
| Gaz | {% if diagnostics.gaz %}Oui{% else %}Non{% endif %} | {{ diagnostics.gaz.date | default('-') }} | {{ diagnostics.gaz.validite | default('-') }} |
| Termites | {% if diagnostics.termites %}Oui{% else %}Non{% endif %} | {{ diagnostics.termites.date | default('-') }} | {{ diagnostics.termites.validite | default('-') }} |
| ERP | {% if diagnostics.erp %}Oui{% else %}Non{% endif %} | {{ diagnostics.erp.date | default('-') }} | {{ diagnostics.erp.validite | default('-') }} |
| Assainissement | {% if diagnostics.assainissement %}Oui{% else %}Non{% endif %} | {{ diagnostics.assainissement.date | default('-') }} | {{ diagnostics.assainissement.validite | default('-') }} |
| Bruit | {% if diagnostics.bruit %}Oui{% else %}Non{% endif %} | {{ diagnostics.bruit.date | default('-') }} | {{ diagnostics.bruit.validite | default('-') }} |
| Carrez | {% if diagnostics.carrez %}Oui{% else %}Non{% endif %} | {{ diagnostics.carrez.date | default('-') }} | {{ diagnostics.carrez.validite | default('-') }} |
{% endif %}

Le BÉNÉFICIAIRE reconnaît avoir reçu copie de l'ensemble des diagnostics mentionnés.

{# Annexes réduites (13) #}
{% include 'sections/promesse/annexes_standard.md' %}

{% include 'sections/promesse/signatures.md' %}

{% endblock %}
