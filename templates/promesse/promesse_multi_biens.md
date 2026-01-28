{# Template Promesse Multi-Biens - Vente de plusieurs propriétés distinctes #}
{# Source: Trame_promesse_A.docx #}
{# Bookmarks: 423 | Cas: Lot + cave + parking, indivision multi-parcelles #}

{% extends "promesse_base.md" %}

{% block type_promesse %}multi_biens{% endblock %}

{% block titre %}
# PROMESSE UNILATÉRALE DE VENTE

**Vente de plusieurs biens immobiliers**
{% endblock %}

{% block contenu_principal %}

{% include 'sections/promesse/entete_promesse.md' %}

{% include 'sections/promesse/identification_parties.md' %}

{# Support étendu des situations matrimoniales (22 variantes) #}
{% include 'sections/promesse/qualite_capacite_etendu.md' %}

{# ============================================= #}
{# DÉSIGNATION DES BIENS MULTIPLES              #}
{# Structure répétée pour chaque bien (max 3)   #}
{# ============================================= #}

## DÉSIGNATION DES BIENS

La présente promesse porte sur les biens immobiliers ci-après désignés:

{% for bien in biens %}
### BIEN N°{{ loop.index }}

#### Lieu de situation

| | |
|--|--|
| **Adresse** | <<<VAR_START>>>{{ bien.adresse }}<<<VAR_END>>> |
| **Code postal** | <<<VAR_START>>>{{ bien.code_postal }}<<<VAR_END>>> |
| **Ville** | <<<VAR_START>>>{{ bien.ville }}<<<VAR_END>>> |
| **Lieu-dit** | {{ bien.lieu_dit | default('-') }} |
{% if bien.batiment %}| **Bâtiment** | {{ bien.batiment }} |{% endif %}
{% if bien.escalier %}| **Escalier** | {{ bien.escalier }} |{% endif %}
{% if bien.etage %}| **Étage** | {{ bien.etage }} |{% endif %}

#### Références cadastrales

| Section | N° | Lieu-dit | Nature | Surface |
|---------|-----|----------|--------|---------|
{% for parcelle in bien.cadastre.parcelles %}
| {{ parcelle.section }} | {{ parcelle.numero }} | {{ parcelle.lieu_dit | default('-') }} | {{ parcelle.nature | default('Sol') }} | {{ parcelle.surface }} |
{% endfor %}

**Surface totale**: <<<VAR_START>>>{{ bien.cadastre.surface_totale }}<<<VAR_END>>>

{% if bien.copropriete %}
#### Copropriété

Ce bien fait partie de l'ensemble immobilier sis {{ bien.copropriete.adresse }}.

{% if bien.lots %}
**Lots de copropriété**:

| N° Lot | Nature | Étage | Tantièmes | Carrez |
|--------|--------|-------|-----------|--------|
{% for lot in bien.lots %}
| {{ lot.numero }} | {{ lot.nature }} | {{ lot.etage | default('-') }} | {{ lot.tantiemes }}/{{ bien.copropriete.tantiemes_totaux }} | {{ lot.carrez | default('-') }} m² |
{% endfor %}
{% endif %}

{% endif %}

---

{% endfor %}

{# ============================================= #}
{# MOBILIER (si applicable)                      #}
{# ============================================= #}
{% if mobilier and mobilier.existe %}

## MOBILIER VENDU

La vente comprend également les meubles ci-après:

| Désignation | État / Valeur |
|-------------|---------------|
{% for item in mobilier.liste %}
| {{ item.designation }} | {{ item.etat }}{% if item.valeur %} / {{ item.valeur }} EUR{% endif %} |
{% endfor %}

**Prix total du mobilier**: <<<VAR_START>>>{{ mobilier.prix_total | format_nombre }}<<<VAR_END>>> EUR

{% endif %}

{% include 'sections/promesse/origine_propriete_multi.md' %}

{% include 'sections/promesse/situation_locative.md' %}

{# Prix ventilé par bien #}
## PRIX

### Ventilation par bien

| Bien | Description | Prix |
|------|-------------|------|
{% for bien in biens %}
| Bien n°{{ loop.index }} | {{ bien.adresse }} | {{ bien.prix | format_nombre }} EUR |
{% endfor %}
{% if mobilier and mobilier.prix_total %}
| Mobilier | Liste annexée | {{ mobilier.prix_total | format_nombre }} EUR |
{% endif %}
| **TOTAL** | | **<<<VAR_START>>>{{ prix.montant | format_nombre }}<<<VAR_END>>> EUR** |

({{ prix.montant | nombre_en_lettres }} euros)

{% include 'sections/promesse/modalites_paiement.md' %}

{% if financement and financement.pret %}
{% include 'sections/promesse/condition_suspensive_pret.md' %}
{% endif %}

{# Condition de vente préalable (fréquent en multi-biens) #}
{% if conditions_suspensives and conditions_suspensives.vente_prealable %}
{% include 'sections/promesse/condition_suspensive_vente.md' %}
{% endif %}

{% if indemnite and indemnite.montant > 0 %}
{% include 'sections/promesse/indemnite_immobilisation.md' %}
{% endif %}

{# Faculté de substitution (fréquent pour investisseurs) #}
{% if substitution and substitution.autorisee %}
{% include 'sections/promesse/faculte_substitution.md' %}
{% endif %}

{% include 'sections/promesse/conditions_generales.md' %}

{% include 'sections/promesse/clause_penale.md' %}

{% include 'sections/promesse/diagnostics_standard.md' %}

{# Annexes étendues (29) #}
{% include 'sections/promesse/annexes_etendues.md' %}

{% include 'sections/promesse/signatures.md' %}

{% endblock %}
