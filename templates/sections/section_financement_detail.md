## Fonds personnels

{% if paiement.fonds_personnels or indivision.acquereurs %}

{% if indivision and indivision.acquereurs %}
### Répartition des apports personnels

{% for acquereur in indivision.acquereurs %}
{% if acquereur.financement %}
#### {{ acquereur.civilite }} {{ acquereur.prenom }} {{ acquereur.nom | upper }}

{% if acquereur.financement.apport_personnel %}
**Apport personnel total** : <<<VAR_START>>>{{ acquereur.financement.apport_personnel | format_nombre }}<<<VAR_END>>> EUR
{% endif %}

{% if acquereur.financement.origine_fonds %}
**Provenance des fonds** :
{% for origine in acquereur.financement.origine_fonds %}
- {{ origine.source }} : <<<VAR_START>>>{{ origine.montant | format_nombre }}<<<VAR_END>>> EUR
  {% if origine.justificatif %}({{ origine.justificatif }}){% endif %}
{% endfor %}
{% endif %}

{% if acquereur.financement.epargne %}
**Épargne constituée** :
{% for epargne in acquereur.financement.epargne %}
- {{ epargne.type }} : <<<VAR_START>>>{{ epargne.montant | format_nombre }}<<<VAR_END>>> EUR
  {% if epargne.etablissement %}- Établissement : <<<VAR_START>>>{{ epargne.etablissement }}<<<VAR_END>>>{% endif %}
{% endfor %}
{% endif %}

{% if acquereur.financement.donation %}
**Donation** : <<<VAR_START>>>{{ acquereur.financement.donation.montant | format_nombre }}<<<VAR_END>>> EUR
- Donateur : <<<VAR_START>>>{{ acquereur.financement.donation.donateur.civilite }} {{ acquereur.financement.donation.donateur.prenom }} {{ acquereur.financement.donation.donateur.nom | upper }}<<<VAR_END>>> ({{ acquereur.financement.donation.donateur.lien }})
{% if acquereur.financement.donation.acte %}
- Acte notarié reçu par Maître <<<VAR_START>>>{{ acquereur.financement.donation.acte.notaire }}<<<VAR_END>>> le <<<VAR_START>>>{{ acquereur.financement.donation.acte.date | format_date }}<<<VAR_END>>> à <<<VAR_START>>>{{ acquereur.financement.donation.acte.lieu }}<<<VAR_END>>>
{% endif %}
{% endif %}

{% if acquereur.financement.vente_precedente %}
**Produit de vente précédente** : <<<VAR_START>>>{{ acquereur.financement.vente_precedente.montant | format_nombre }}<<<VAR_END>>> EUR
- Bien vendu : {{ acquereur.financement.vente_precedente.designation }}
- Date de vente : <<<VAR_START>>>{{ acquereur.financement.vente_precedente.date | format_date }}<<<VAR_END>>>
{% endif %}

{% endif %}{# Fin {% if acquereur.financement %} #}
{% endfor %}

### Total des fonds personnels

**Montant total** : <<<VAR_START>>>{{ paiement.fonds_personnels | format_nombre }}<<<VAR_END>>> EUR

Soit <<<VAR_START>>>{{ (paiement.fonds_personnels / prix.montant * 100) | round(2) }}<<<VAR_END>>>% du prix d'acquisition.

{% else %}
L'ACQUEREUR déclare disposer de fonds personnels à hauteur de <<<VAR_START>>>{{ paiement.fonds_personnels | format_nombre }}<<<VAR_END>>> EUR pour financer l'acquisition.

{% if paiement.origine_fonds_personnels %}
**Origine des fonds** : {{ paiement.origine_fonds_personnels }}
{% endif %}
{% endif %}

{% else %}
L'ACQUEREUR ne finance pas l'acquisition par des fonds personnels.
{% endif %}

## Fonds empruntés

{% if paiement.fonds_empruntes and paiement.fonds_empruntes > 0 %}

### Montant total emprunté

**Fonds empruntés** : <<<VAR_START>>>{{ paiement.fonds_empruntes | format_nombre }}<<<VAR_END>>> EUR

Soit <<<VAR_START>>>{{ (paiement.fonds_empruntes / prix.montant * 100) | round(2) }}<<<VAR_END>>>% du prix d'acquisition.

{% if paiement.prets %}

### Détail des prêts

{% for pret in paiement.prets %}

#### Prêt n° {{ loop.index }}{% if pret.type %} - {{ pret.type }}{% endif %}

**Établissement prêteur** : <<<VAR_START>>>{{ pret.etablissement.nom }}<<<VAR_END>>>
{% if pret.etablissement.forme_juridique %}- Forme juridique : {{ pret.etablissement.forme_juridique }}{% endif %}
{% if pret.etablissement.siege %}- Siège : <<<VAR_START>>>{{ pret.etablissement.siege }}<<<VAR_END>>>{% endif %}
{% if pret.etablissement.siren %}- SIREN : <<<VAR_START>>>{{ pret.etablissement.siren }}<<<VAR_END>>>{% endif %}
{% if pret.etablissement.rcs %}- RCS : <<<VAR_START>>>{{ pret.etablissement.rcs }}<<<VAR_END>>>{% endif %}

**Caractéristiques du prêt** :
- Montant emprunté : <<<VAR_START>>>{{ pret.montant | format_nombre }}<<<VAR_END>>> EUR
- Durée : <<<VAR_START>>>{{ pret.duree_mois }}<<<VAR_END>>> mois (<<<VAR_START>>>{{ (pret.duree_mois / 12) | round(1) }}<<<VAR_END>>> ans)
- Taux nominal : <<<VAR_START>>>{{ pret.taux_nominal }}<<<VAR_END>>> % l'an
{% if pret.taux_effectif_global %}- Taux effectif global (TEG) : <<<VAR_START>>>{{ pret.taux_effectif_global }}<<<VAR_END>>> %{% endif %}
{% if pret.type_taux %}- Type de taux : {{ pret.type_taux }}{% endif %}

**Mensualité** : <<<VAR_START>>>{{ pret.mensualite | format_nombre }}<<<VAR_END>>> EUR

{% if pret.assurance %}
**Assurance emprunteur** :
- Taux : <<<VAR_START>>>{{ pret.assurance.taux }}<<<VAR_END>>> %
- Coût mensuel : <<<VAR_START>>>{{ pret.assurance.cout_mensuel | format_nombre }}<<<VAR_END>>> EUR
- Assureur : <<<VAR_START>>>{{ pret.assurance.organisme }}<<<VAR_END>>>
{% endif %}

{% if pret.garantie %}
**Garantie du prêt** :
- Type : {{ pret.garantie.type }}
{% if pret.garantie.type == 'hypotheque' %}
- Inscription d'hypothèque pour un montant de <<<VAR_START>>>{{ pret.garantie.montant_inscription | format_nombre }}<<<VAR_END>>> EUR
- Rang : <<<VAR_START>>>{{ pret.garantie.rang }}<<<VAR_END>>>
{% elif pret.garantie.type == 'privilege_preteur_deniers' %}
- Privilège de prêteur de deniers
- Montant de l'inscription : <<<VAR_START>>>{{ pret.garantie.montant_inscription | format_nombre }}<<<VAR_END>>> EUR
{% elif pret.garantie.type == 'caution' %}
- Organisme de caution : <<<VAR_START>>>{{ pret.garantie.organisme }}<<<VAR_END>>>
- Montant cautionné : <<<VAR_START>>>{{ pret.garantie.montant | format_nombre }}<<<VAR_END>>> EUR
{% endif %}
{% endif %}

{% if pret.offre_pret %}
**Offre de prêt** :
- Date d'émission : <<<VAR_START>>>{{ pret.offre_pret.date_emission | format_date }}<<<VAR_END>>>
- Date d'acceptation : <<<VAR_START>>>{{ pret.offre_pret.date_acceptation | format_date }}<<<VAR_END>>>
{% if pret.offre_pret.reference %}- Référence : <<<VAR_START>>>{{ pret.offre_pret.reference }}<<<VAR_END>>>{% endif %}
{% endif %}

{% if pret.deblocage %}
**Déblocage des fonds** :
- Modalités : {{ pret.deblocage.modalites }}
{% if pret.deblocage.date_prevue %}- Date prévue : <<<VAR_START>>>{{ pret.deblocage.date_prevue | format_date }}<<<VAR_END>>>{% endif %}
{% endif %}

{% endfor %}

{% endif %}

### Déclaration d'affectation des fonds

Conformément aux dispositions de l'article 2422 du Code civil, l'ACQUEREUR déclare que les fonds empruntés seront affectés au paiement du prix de vente du bien présentement vendu.

{% if paiement.acte_pret %}
Les prêts ci-dessus ont été consentis aux termes {% if paiement.prets | length > 1 %}des actes{% else %}de l'acte{% endif %} reçu{% if paiement.prets | length > 1 %}s{% endif %} par :

{% for pret in paiement.prets %}
{% if pret.acte_pret %}
- Maître <<<VAR_START>>>{{ pret.acte_pret.notaire }}<<<VAR_END>>>, notaire à <<<VAR_START>>>{{ pret.acte_pret.lieu }}<<<VAR_END>>>, le <<<VAR_START>>>{{ pret.acte_pret.date | format_date }}<<<VAR_END>>>
{% endif %}
{% endfor %}
{% endif %}

### Privilège de prêteur de deniers / Hypothèque légale

{% if paiement.privilege_preteur_deniers %}
Aux termes de l'acte de prêt susvisé, l'ACQUEREUR s'est engagé auprès du PRETEUR à employer la somme de <<<VAR_START>>>{{ paiement.fonds_empruntes | format_nombre }}<<<VAR_END>>> EUR provenant du prêt au paiement à due concurrence du prix ci-dessus stipulé.

L'ACQUEREUR déclare avoir effectué le paiement ci-dessus à due concurrence de la somme lui provenant de ce prêt. Il fait cette déclaration pour constater l'origine des fonds conformément à l'engagement qu'il a pris envers le PRETEUR.

En garantie du remboursement du prêt consenti, une inscription de privilège de prêteur de deniers sera prise sur le bien présentement vendu pour un montant de <<<VAR_START>>>{{ paiement.privilege_preteur_deniers.montant | format_nombre }}<<<VAR_END>>> EUR.
{% endif %}

{% else %}
L'acquisition n'est pas financée par emprunt. Le prix sera payé comptant au moyen de fonds personnels.
{% endif %}

{% if paiement.plan_financement_total %}
### Récapitulatif du plan de financement

| Source de financement | Montant | % du prix |
|----------------------|---------|-----------|
{% if paiement.fonds_personnels > 0 %}| Fonds personnels | <<<VAR_START>>>{{ paiement.fonds_personnels | format_nombre }}<<<VAR_END>>> EUR | <<<VAR_START>>>{{ (paiement.fonds_personnels / prix.montant * 100) | round(1) }}<<<VAR_END>>>% |{% endif %}
{% if paiement.fonds_empruntes > 0 %}| Fonds empruntés | <<<VAR_START>>>{{ paiement.fonds_empruntes | format_nombre }}<<<VAR_END>>> EUR | <<<VAR_START>>>{{ (paiement.fonds_empruntes / prix.montant * 100) | round(1) }}<<<VAR_END>>>% |{% endif %}
{% if paiement.aides %}| Aides | <<<VAR_START>>>{{ paiement.aides_total | format_nombre }}<<<VAR_END>>> EUR | <<<VAR_START>>>{{ (paiement.aides_total / prix.montant * 100) | round(1) }}<<<VAR_END>>>% |{% endif %}
| **TOTAL** | **<<<VAR_START>>>{{ prix.montant | format_nombre }}<<<VAR_END>>> EUR** | **100%** |
{% endif %}
