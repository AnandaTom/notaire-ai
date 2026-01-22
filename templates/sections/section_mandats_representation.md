## POUVOIRS ET MANDATS

{% if pouvoirs %}

### Mandats conférés

{% if pouvoirs.mandats %}
Les mandats suivants ont été conférés pour la présente vente :

{% for mandat in pouvoirs.mandats %}
#### Mandat n{{ loop.index }}

- **Mandant** : <<<VAR_START>>>{{ mandat.mandant }}<<<VAR_END>>>
- **Mandataire** : <<<VAR_START>>>{{ mandat.mandataire }}<<<VAR_END>>>
{% if mandat.type %}- **Type de mandat** : {{ mandat.type }}{% endif %}
{% if mandat.date %}- **Date du mandat** : <<<VAR_START>>>{{ mandat.date | format_date }}<<<VAR_END>>>{% endif %}
{% if mandat.notaire_redacteur %}- **Notaire rédacteur** : <<<VAR_START>>>{{ mandat.notaire_redacteur }}<<<VAR_END>>>{% endif %}
{% if mandat.reference %}- **Référence** : <<<VAR_START>>>{{ mandat.reference }}<<<VAR_END>>>{% endif %}
{% if mandat.objet %}- **Objet** : {{ mandat.objet }}{% endif %}
{% if mandat.pouvoirs_conferes %}
- **Pouvoirs conférés** :
{% for pouvoir in mandat.pouvoirs_conferes %}
  - {{ pouvoir }}
{% endfor %}
{% endif %}
{% if mandat.duree_validite %}- **Durée de validité** : <<<VAR_START>>>{{ mandat.duree_validite }}<<<VAR_END>>>{% endif %}

{% endfor %}
{% endif %}

{% if pouvoirs.procurations %}
### Procurations

{% for procuration in pouvoirs.procurations %}
#### Procuration n{{ loop.index }}

- **Constituant** : <<<VAR_START>>>{{ procuration.constituant }}<<<VAR_END>>>
- **Procurateur** : <<<VAR_START>>>{{ procuration.procurateur }}<<<VAR_END>>>
{% if procuration.forme %}- **Forme** : {{ procuration.forme }}{% endif %}
{% if procuration.date %}- **Date** : <<<VAR_START>>>{{ procuration.date | format_date }}<<<VAR_END>>>{% endif %}
{% if procuration.lieu %}- **Lieu de signature** : <<<VAR_START>>>{{ procuration.lieu }}<<<VAR_END>>>{% endif %}
{% if procuration.notaire %}- **Notaire authentificateur** : <<<VAR_START>>>{{ procuration.notaire }}<<<VAR_END>>>{% endif %}
{% if procuration.reference_minute %}- **Référence minute** : <<<VAR_START>>>{{ procuration.reference_minute }}<<<VAR_END>>>{% endif %}
{% if procuration.etendue %}
- **Étendue des pouvoirs** :
{% for pouvoir in procuration.etendue %}
  - {{ pouvoir }}
{% endfor %}
{% endif %}
{% if procuration.restrictions %}
- **Restrictions** : {{ procuration.restrictions }}
{% endif %}

{% endfor %}
{% endif %}

{% if pouvoirs.verification %}
### Vérification des pouvoirs

Le notaire soussigné certifie avoir vérifié :
{% if pouvoirs.verification.identite %}- L'identité du mandataire{% endif %}
{% if pouvoirs.verification.capacite %}- La capacité du mandataire{% endif %}
{% if pouvoirs.verification.etendue %}- L'étendue des pouvoirs conférés{% endif %}
{% if pouvoirs.verification.validite %}- La validité du mandat à la date de la présente{% endif %}
{% if pouvoirs.verification.absence_revocation %}- L'absence de révocation du mandat{% endif %}
{% endif %}

{% else %}
Aucun mandat ni procuration n'a été établi pour la présente vente. Les parties comparaissent personnellement.
{% endif %}

## REPRÉSENTATION DES PARTIES

{% if representation %}

{% if representation.vendeur %}
### Représentation du vendeur

{% for rep in representation.vendeur %}
**{{ rep.partie_representee }}** est représenté(e) par :
- **Représentant** : <<<VAR_START>>>{{ rep.representant }}<<<VAR_END>>>
{% if rep.qualite %}- **Qualité** : {{ rep.qualite }}{% endif %}
{% if rep.titre %}- **En vertu de** : <<<VAR_START>>>{{ rep.titre }}<<<VAR_END>>>{% endif %}
{% if rep.date_titre %}- **Date du titre** : <<<VAR_START>>>{{ rep.date_titre | format_date }}<<<VAR_END>>>{% endif %}
{% if rep.autorite_delivrance %}- **Autorité de délivrance** : <<<VAR_START>>>{{ rep.autorite_delivrance }}<<<VAR_END>>>{% endif %}
{% if rep.justificatif %}- **Justificatif** : {{ rep.justificatif }}{% endif %}

{% endfor %}
{% endif %}

{% if representation.acquereur %}
### Représentation de l'acquéreur

{% for rep in representation.acquereur %}
**{{ rep.partie_representee }}** est représenté(e) par :
- **Représentant** : <<<VAR_START>>>{{ rep.representant }}<<<VAR_END>>>
{% if rep.qualite %}- **Qualité** : {{ rep.qualite }}{% endif %}
{% if rep.titre %}- **En vertu de** : <<<VAR_START>>>{{ rep.titre }}<<<VAR_END>>>{% endif %}
{% if rep.date_titre %}- **Date du titre** : <<<VAR_START>>>{{ rep.date_titre | format_date }}<<<VAR_END>>>{% endif %}
{% if rep.autorite_delivrance %}- **Autorité de délivrance** : <<<VAR_START>>>{{ rep.autorite_delivrance }}<<<VAR_END>>>{% endif %}
{% if rep.justificatif %}- **Justificatif** : {{ rep.justificatif }}{% endif %}

{% endfor %}
{% endif %}

{% if representation.mineurs %}
### Représentation des mineurs

{% for mineur in representation.mineurs %}
Le mineur **<<<VAR_START>>>{{ mineur.nom_mineur }}<<<VAR_END>>>**, né(e) le <<<VAR_START>>>{{ mineur.date_naissance | format_date }}<<<VAR_END>>>, est représenté(e) par :
- **Représentant légal** : <<<VAR_START>>>{{ mineur.representant }}<<<VAR_END>>>
- **Qualité** : {{ mineur.qualite_representant }}
{% if mineur.autorisation_juge %}
- **Autorisation du juge des tutelles** : <<<VAR_START>>>{{ mineur.autorisation_juge.date | format_date }}<<<VAR_END>>>
  - Tribunal : <<<VAR_START>>>{{ mineur.autorisation_juge.tribunal }}<<<VAR_END>>>
  - Référence : <<<VAR_START>>>{{ mineur.autorisation_juge.reference }}<<<VAR_END>>>
{% endif %}
{% if mineur.conseil_famille %}
- **Délibération du conseil de famille** : <<<VAR_START>>>{{ mineur.conseil_famille.date | format_date }}<<<VAR_END>>>
  - Référence : <<<VAR_START>>>{{ mineur.conseil_famille.reference }}<<<VAR_END>>>
{% endif %}

{% endfor %}
{% endif %}

{% if representation.majeurs_proteges %}
### Représentation des majeurs protégés

{% for majeur in representation.majeurs_proteges %}
**<<<VAR_START>>>{{ majeur.nom_protege }}<<<VAR_END>>>**, placé(e) sous régime de {{ majeur.regime_protection }}, est représenté(e) par :
- **{{ majeur.qualite_representant }}** : <<<VAR_START>>>{{ majeur.representant }}<<<VAR_END>>>
{% if majeur.jugement %}
- **Jugement de mise sous protection** :
  - Date : <<<VAR_START>>>{{ majeur.jugement.date | format_date }}<<<VAR_END>>>
  - Tribunal : <<<VAR_START>>>{{ majeur.jugement.tribunal }}<<<VAR_END>>>
  - Référence : <<<VAR_START>>>{{ majeur.jugement.reference }}<<<VAR_END>>>
{% endif %}
{% if majeur.autorisation_juge %}
- **Autorisation du juge des tutelles** : <<<VAR_START>>>{{ majeur.autorisation_juge.date | format_date }}<<<VAR_END>>>
  - Référence : <<<VAR_START>>>{{ majeur.autorisation_juge.reference }}<<<VAR_END>>>
{% endif %}

{% endfor %}
{% endif %}

{% if representation.personnes_morales %}
### Représentation des personnes morales

{% for pm in representation.personnes_morales %}
La société **<<<VAR_START>>>{{ pm.denomination }}<<<VAR_END>>>** est représentée par :
- **Représentant** : <<<VAR_START>>>{{ pm.representant }}<<<VAR_END>>>
- **Qualité** : {{ pm.qualite }}
{% if pm.pouvoirs %}- **Pouvoirs** : {{ pm.pouvoirs }}{% endif %}
{% if pm.kbis %}
- **Extrait Kbis** : délivré le <<<VAR_START>>>{{ pm.kbis.date | format_date }}<<<VAR_END>>> par le Greffe de <<<VAR_START>>>{{ pm.kbis.greffe }}<<<VAR_END>>>
{% endif %}
{% if pm.deliberation %}
- **Délibération autorisant la vente** :
  - Organe : {{ pm.deliberation.organe }}
  - Date : <<<VAR_START>>>{{ pm.deliberation.date | format_date }}<<<VAR_END>>>
{% endif %}

{% endfor %}
{% endif %}

{% else %}
Les parties comparaissent personnellement à l'acte et ne sont pas représentées.
{% endif %}

## DÉLÉGATIONS

{% if mandats %}

{% if mandats.delegation_signature %}
### Délégation de signature

{% for delegation in mandats.delegation_signature %}
#### Délégation n{{ loop.index }}

- **Délégant** : <<<VAR_START>>>{{ delegation.delegant }}<<<VAR_END>>>
- **Délégataire** : <<<VAR_START>>>{{ delegation.delegataire }}<<<VAR_END>>>
{% if delegation.objet %}- **Objet** : {{ delegation.objet }}{% endif %}
{% if delegation.date %}- **Date** : <<<VAR_START>>>{{ delegation.date | format_date }}<<<VAR_END>>>{% endif %}
{% if delegation.validite %}- **Validité** : {{ delegation.validite }}{% endif %}
{% if delegation.conditions %}
- **Conditions** :
{% for condition in delegation.conditions %}
  - {{ condition }}
{% endfor %}
{% endif %}

{% endfor %}
{% endif %}

{% if mandats.delegation_paiement %}
### Délégation de paiement

{% for delegation in mandats.delegation_paiement %}
#### Délégation de paiement n{{ loop.index }}

- **Délégant (débiteur initial)** : <<<VAR_START>>>{{ delegation.delegant }}<<<VAR_END>>>
- **Délégué (nouveau débiteur)** : <<<VAR_START>>>{{ delegation.delegue }}<<<VAR_END>>>
- **Délégataire (créancier)** : <<<VAR_START>>>{{ delegation.delegataire }}<<<VAR_END>>>
{% if delegation.montant %}- **Montant** : <<<VAR_START>>>{{ delegation.montant | format_nombre }}<<<VAR_END>>> EUR{% endif %}
{% if delegation.nature_dette %}- **Nature de la dette** : {{ delegation.nature_dette }}{% endif %}
{% if delegation.type %}
- **Type de délégation** : {{ delegation.type }}
{% if delegation.type == 'parfaite' %}
Le délégataire a expressément accepté de libérer le délégant de son obligation.
{% elif delegation.type == 'imparfaite' %}
Le délégant reste tenu solidairement avec le délégué envers le délégataire.
{% endif %}
{% endif %}

{% endfor %}
{% endif %}

{% if mandats.delegation_pouvoirs %}
### Délégation de pouvoirs

{% for delegation in mandats.delegation_pouvoirs %}
#### Délégation de pouvoirs n{{ loop.index }}

- **Délégant** : <<<VAR_START>>>{{ delegation.delegant }}<<<VAR_END>>>
- **Délégataire** : <<<VAR_START>>>{{ delegation.delegataire }}<<<VAR_END>>>
{% if delegation.date_delegation %}- **Date de la délégation** : <<<VAR_START>>>{{ delegation.date_delegation | format_date }}<<<VAR_END>>>{% endif %}
{% if delegation.pouvoirs_delegues %}
- **Pouvoirs délégués** :
{% for pouvoir in delegation.pouvoirs_delegues %}
  - {{ pouvoir }}
{% endfor %}
{% endif %}
{% if delegation.limites %}
- **Limites de la délégation** : {{ delegation.limites }}
{% endif %}
{% if delegation.duree %}- **Durée** : <<<VAR_START>>>{{ delegation.duree }}<<<VAR_END>>>{% endif %}
{% if delegation.revocable %}- **Caractère révocable** : {{ delegation.revocable }}{% endif %}

{% endfor %}
{% endif %}

{% if mandats.subdelegation %}
### Subdélégation

{% if mandats.subdelegation.autorisee %}
Le mandataire est autorisé à subdéléguer ses pouvoirs dans les conditions suivantes :
{% if mandats.subdelegation.conditions %}
{% for condition in mandats.subdelegation.conditions %}
- {{ condition }}
{% endfor %}
{% endif %}
{% else %}
Le mandataire n'est pas autorisé à subdéléguer ses pouvoirs.
{% endif %}
{% endif %}

{% else %}
Aucune délégation n'a été consentie dans le cadre de la présente vente.
{% endif %}

{% if mandats and mandats.extinction %}
## Extinction des mandats et délégations

{% if mandats.extinction.cause %}
### Cause d'extinction

{{ mandats.extinction.cause }}
{% endif %}

{% if mandats.extinction.date %}
### Date d'effet

Les mandats et délégations prendront fin le <<<VAR_START>>>{{ mandats.extinction.date | format_date }}<<<VAR_END>>>.
{% endif %}

{% if mandats.extinction.conditions %}
### Conditions d'extinction

{% for condition in mandats.extinction.conditions %}
- {{ condition }}
{% endfor %}
{% endif %}
{% endif %}
