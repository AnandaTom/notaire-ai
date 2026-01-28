{# ============================================================================
   SECTION AGENT IMMOBILIER / NEGOCIATEUR

   Utilisation: {% include 'sections/section_agent_immobilier.md' %}
   Condition: {% if agent_immobilier and agent_immobilier.actif %}

   Variables requises:
   - agent_immobilier.nom: Nom de l'agence
   - agent_immobilier.adresse: Adresse de l'agence
   - agent_immobilier.carte_professionnelle: N° carte T ou G
   - agent_immobilier.honoraires: Montant des honoraires
   - agent_immobilier.a_charge_de: "vendeur" ou "acquereur"
   ============================================================================ #}

### INTERVENTION D'UN AGENT IMMOBILIER

Les parties déclarent que la présente vente a été négociée par l'intermédiaire de :

**{{ agent_immobilier.nom | default("AGENCE IMMOBILIERE") }}**
{{ agent_immobilier.adresse | default("") }}
{% if agent_immobilier.siret %}SIRET : {{ agent_immobilier.siret }}{% endif %}

Titulaire de la carte professionnelle n° {{ agent_immobilier.carte_professionnelle | default("CPI XXXX XXXX XXXX") }}, délivrée par la CCI de {{ agent_immobilier.cci | default("") }}, garantie par {{ agent_immobilier.garant | default("la Caisse de Garantie GALIAN") }}.

{% if agent_immobilier.mandat %}
#### Mandat

{% if agent_immobilier.mandat.type == "exclusif" %}
Mandat exclusif de vente n° {{ agent_immobilier.mandat.numero | default("") }} en date du {{ agent_immobilier.mandat.date | default("") }}.
{% else %}
Mandat simple de vente n° {{ agent_immobilier.mandat.numero | default("") }} en date du {{ agent_immobilier.mandat.date | default("") }}.
{% endif %}
{% endif %}

#### Honoraires de négociation

Les honoraires de l'agent immobilier s'élèvent à la somme de **{{ agent_immobilier.honoraires.montant | default(0) | format_nombre }} euros** ({{ agent_immobilier.honoraires.montant | default(0) | montant_en_lettres }}).

{% if agent_immobilier.honoraires.tva %}
Soit {{ agent_immobilier.honoraires.montant_ht | default(0) | format_nombre }} euros HT, TVA au taux de {{ agent_immobilier.honoraires.taux_tva | default(20) }}% : {{ agent_immobilier.honoraires.montant_tva | default(0) | format_nombre }} euros.
{% endif %}

{% if agent_immobilier.a_charge_de == "vendeur" %}
Ces honoraires sont **à la charge du VENDEUR** et seront prélevés sur le prix de vente.
{% elif agent_immobilier.a_charge_de == "acquereur" %}
Ces honoraires sont **à la charge de l'ACQUEREUR** et s'ajoutent au prix de vente ci-dessus indiqué.

Le prix total pour l'acquéreur s'élève donc à :
- Prix du bien : {{ prix.montant | default(0) | format_nombre }} euros
- Honoraires agence : {{ agent_immobilier.honoraires.montant | default(0) | format_nombre }} euros
- **TOTAL : {{ (prix.montant | default(0) + agent_immobilier.honoraires.montant | default(0)) | format_nombre }} euros**
{% else %}
Ces honoraires sont répartis entre les parties selon les modalités suivantes :
- À la charge du vendeur : {{ agent_immobilier.honoraires.part_vendeur | default(0) | format_nombre }} euros
- À la charge de l'acquéreur : {{ agent_immobilier.honoraires.part_acquereur | default(0) | format_nombre }} euros
{% endif %}

{% if agent_immobilier.paiement %}
#### Modalités de paiement

{% if agent_immobilier.paiement.sequestre %}
Les honoraires seront prélevés sur le séquestre détenu par le notaire soussigné.
{% else %}
Les honoraires seront réglés directement à l'agent immobilier au jour de la signature de l'acte authentique.
{% endif %}
{% endif %}

{% if agent_immobilier.declaration_independance %}
#### Déclaration d'indépendance

L'agent immobilier déclare n'avoir aucun lien d'intérêt direct ou indirect avec l'une ou l'autre des parties à la présente vente, autre que celui résultant du mandat de vente confié par le vendeur.
{% endif %}

{% if agent_immobilier.observations %}
#### Observations

{{ agent_immobilier.observations }}
{% endif %}

---
