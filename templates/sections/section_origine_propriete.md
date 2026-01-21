# Origine de propriété

{% if origine_propriete %}
{% for origine in origine_propriete %}

**Concernant {{ origine.lots_designation }}**

### Origine immédiate

{% if origine.origine_immediate %}
Le VENDEUR est propriétaire {{ origine.origine_immediate.modalite_detention | default('en pleine propriété') }} {{ origine.origine_immediate.designation_lots }} par suite de {{ origine.origine_immediate.type_acquisition | lower }} qu'il en a faite de :

{% for cedant in origine.origine_immediate.cedants %}
**{{ cedant.civilite }} <<<VAR_START>>>{{ cedant.prenom }} {{ cedant.nom | upper }}<<<VAR_END>>>**, {{ cedant.profession }}, demeurant à <<<VAR_START>>>{{ cedant.adresse }}<<<VAR_END>>>

Né(e) à <<<VAR_START>>>{{ cedant.lieu_naissance }}<<<VAR_END>>> le <<<VAR_START>>>{{ cedant.date_naissance | format_date }}<<<VAR_END>>>

{% if cedant.situation_matrimoniale %}
{% if cedant.situation_matrimoniale.statut == 'marie' %}
Marié(e) à <<<VAR_START>>>{{ cedant.situation_matrimoniale.conjoint.civilite }} {{ cedant.situation_matrimoniale.conjoint.prenom }} {{ cedant.situation_matrimoniale.conjoint.nom | upper }}<<<VAR_END>>> à la mairie de <<<VAR_START>>>{{ cedant.situation_matrimoniale.lieu_mariage }}<<<VAR_END>>> le <<<VAR_START>>>{{ cedant.situation_matrimoniale.date_mariage | format_date }}<<<VAR_END>>>

{% if cedant.situation_matrimoniale.regime_matrimonial %}
Sous le régime de <<<VAR_START>>>{{ cedant.situation_matrimoniale.regime_matrimonial }}<<<VAR_END>>>{% if cedant.situation_matrimoniale.contrat_mariage %}, défini aux articles <<<VAR_START>>>{{ cedant.situation_matrimoniale.articles_code_civil }}<<<VAR_END>>> du Code civil, aux termes du contrat de mariage reçu par Maître <<<VAR_START>>>{{ cedant.situation_matrimoniale.notaire }}<<<VAR_END>>>, notaire à <<<VAR_START>>>{{ cedant.situation_matrimoniale.lieu }}<<<VAR_END>>>, le <<<VAR_START>>>{{ cedant.situation_matrimoniale.date_contrat | format_date }}<<<VAR_END>>>{% endif %}.

{% if cedant.situation_matrimoniale.modification %}
Ce régime matrimonial a fait l'objet d'une modification aux termes d'un acte reçu par Maître <<<VAR_START>>>{{ cedant.situation_matrimoniale.modification.notaire }}<<<VAR_END>>> le <<<VAR_START>>>{{ cedant.situation_matrimoniale.modification.date | format_date }}<<<VAR_END>>>.
{% else %}
Ce régime matrimonial n'a pas fait l'objet de modification.
{% endif %}
{% endif %}

{% elif cedant.situation_matrimoniale.statut == 'divorce' %}
Divorcé(e) de <<<VAR_START>>>{{ cedant.situation_matrimoniale.ex_conjoint.civilite }} {{ cedant.situation_matrimoniale.ex_conjoint.nom }}<<<VAR_END>>> suivant jugement rendu par le tribunal judiciaire de <<<VAR_START>>>{{ cedant.situation_matrimoniale.tribunal }}<<<VAR_END>>> le <<<VAR_START>>>{{ cedant.situation_matrimoniale.date_jugement | format_date }}<<<VAR_END>>>, et non remarié(e).

{% elif cedant.situation_matrimoniale.statut == 'veuf' %}
Veuf (veuve) de <<<VAR_START>>>{{ cedant.situation_matrimoniale.defunt_conjoint.civilite }} {{ cedant.situation_matrimoniale.defunt_conjoint.nom }}<<<VAR_END>>>, décédé(e) le <<<VAR_START>>>{{ cedant.situation_matrimoniale.date_deces | format_date }}<<<VAR_END>>>.

{% elif cedant.situation_matrimoniale.statut == 'celibataire' %}
Célibataire.

{% endif %}

{% if cedant.situation_matrimoniale.pacs %}
{% if cedant.situation_matrimoniale.pacs.conclu %}
Ayant conclu un pacte civil de solidarité avec <<<VAR_START>>>{{ cedant.situation_matrimoniale.pacs.partenaire.civilite }} {{ cedant.situation_matrimoniale.pacs.partenaire.prenom }} {{ cedant.situation_matrimoniale.pacs.partenaire.nom | upper }}<<<VAR_END>>> le <<<VAR_START>>>{{ cedant.situation_matrimoniale.pacs.date | format_date }}<<<VAR_END>>>{% if cedant.situation_matrimoniale.pacs.regime %}, sous le régime de <<<VAR_START>>>{{ cedant.situation_matrimoniale.pacs.regime }}<<<VAR_END>>>{% endif %}.
{% else %}
Non lié(e) par un pacte civil de solidarité.
{% endif %}
{% endif %}
{% endif %}

De nationalité <<<VAR_START>>>{{ cedant.nationalite }}<<<VAR_END>>>.

{% if cedant.resident_fiscal %}
Résident au sens de la réglementation fiscale.
{% else %}
Non-résident au sens de la réglementation fiscale.
{% endif %}

{% endfor %}

Suivant acte {{ origine.origine_immediate.type_libelle | lower }} reçu par Maître <<<VAR_START>>>{{ origine.origine_immediate.notaire }}<<<VAR_END>>>, notaire à <<<VAR_START>>>{{ origine.origine_immediate.lieu }}<<<VAR_END>>>, le <<<VAR_START>>>{{ origine.origine_immediate.date | format_date }}<<<VAR_END>>>.

{% if origine.origine_immediate.prix %}
Le prix a été payé <<<VAR_START>>>{{ origine.origine_immediate.modalite_paiement | default('comptant') }}<<<VAR_END>>> et quittancé audit acte.
{% endif %}

Cet acte a été publié au service de la publicité foncière de <<<VAR_START>>>{{ origine.origine_immediate.publication.service }}<<<VAR_END>>> le <<<VAR_START>>>{{ origine.origine_immediate.publication.date | format_date }}<<<VAR_END>>>, volume <<<VAR_START>>>{{ origine.origine_immediate.publication.volume }}<<<VAR_END>>>, numéro <<<VAR_START>>>{{ origine.origine_immediate.publication.numero }}<<<VAR_END>>>.

{% if origine.origine_immediate.etat_publication %}
L'état délivré sur cette publication <<<VAR_START>>>{% if origine.origine_immediate.etat_presente %}a été présenté{% else %}n'a pas été présenté{% endif %}<<<VAR_END>>> au notaire soussigné.
{% endif %}

{% if origine.origine_immediate.inscriptions %}
### Inscriptions grevant le bien

Le bien est grevé des inscriptions suivantes :

{% for inscription in origine.origine_immediate.inscriptions %}
- **{{ inscription.type }}** : {{ inscription.description }}
  - Bénéficiaire : <<<VAR_START>>>{{ inscription.beneficiaire }}<<<VAR_END>>>
  - Date : <<<VAR_START>>>{{ inscription.date | format_date }}<<<VAR_END>>>
  {% if inscription.montant %}- Montant : <<<VAR_START>>>{{ inscription.montant | format_nombre }}<<<VAR_END>>> EUR{% endif %}
  {% if inscription.publication %}- Publié le <<<VAR_START>>>{{ inscription.publication.date | format_date }}<<<VAR_END>>>, volume <<<VAR_START>>>{{ inscription.publication.volume }}<<<VAR_END>>>, numéro <<<VAR_START>>>{{ inscription.publication.numero }}<<<VAR_END>>>{% endif %}
{% endfor %}
{% endif %}

{% endif %}

### Origine antérieure

{% if origine.origines_anterieures %}
L'origine de propriété antérieure est ci-après relatée telle qu'elle résulte de l'acte {{ origine.origine_immediate.type_libelle | lower }} du <<<VAR_START>>>{{ origine.origine_immediate.date | format_date }}<<<VAR_END>>> susvisé :

{% for origine_ant in origine.origines_anterieures %}

**{{ origine_ant.titre }}**

{% if origine_ant.type == 'acquisition' %}
Les biens et droits immobiliers objet des présentes appartenaient au VENDEUR par suite de l'acquisition qu'il en a faite de :

{% for cedant in origine_ant.cedants %}
**{{ cedant.civilite }} <<<VAR_START>>>{{ cedant.prenom }} {{ cedant.nom | upper }}<<<VAR_END>>>**, {{ cedant.profession }}, demeurant à <<<VAR_START>>>{{ cedant.adresse }}<<<VAR_END>>>

Né(e) à <<<VAR_START>>>{{ cedant.lieu_naissance }}<<<VAR_END>>> le <<<VAR_START>>>{{ cedant.date_naissance | format_date }}<<<VAR_END>>>

{% if cedant.situation_matrimoniale %}
{{ cedant.situation_matrimoniale.description }}
{% endif %}
{% endfor %}

Suivant acte reçu par Maître <<<VAR_START>>>{{ origine_ant.notaire }}<<<VAR_END>>>, notaire à <<<VAR_START>>>{{ origine_ant.lieu }}<<<VAR_END>>>, le <<<VAR_START>>>{{ origine_ant.date | format_date }}<<<VAR_END>>>.

{% if origine_ant.publication %}
Cet acte a été publié au service de la publicité foncière de <<<VAR_START>>>{{ origine_ant.publication.service }}<<<VAR_END>>> le <<<VAR_START>>>{{ origine_ant.publication.date | format_date }}<<<VAR_END>>>, volume <<<VAR_START>>>{{ origine_ant.publication.volume }}<<<VAR_END>>>, numéro <<<VAR_START>>>{{ origine_ant.publication.numero }}<<<VAR_END>>>.
{% endif %}

{% elif origine_ant.type == 'succession' %}
Les biens et droits immobiliers objet des présentes appartiennent au VENDEUR par suite du décès de :

**{{ origine_ant.defunt.civilite }} <<<VAR_START>>>{{ origine_ant.defunt.prenom }} {{ origine_ant.defunt.defunt.nom | upper }}<<<VAR_END>>>**, en son vivant {{ origine_ant.defunt.profession }}, demeurant à <<<VAR_START>>>{{ origine_ant.defunt.adresse }}<<<VAR_END>>>

Né(e) à <<<VAR_START>>>{{ origine_ant.defunt.lieu_naissance }}<<<VAR_END>>> le <<<VAR_START>>>{{ origine_ant.defunt.date_naissance | format_date }}<<<VAR_END>>>

Décédé(e) à <<<VAR_START>>>{{ origine_ant.defunt.lieu_deces }}<<<VAR_END>>> le <<<VAR_START>>>{{ origine_ant.defunt.date_deces | format_date }}<<<VAR_END>>>

Laissant pour recueillir sa succession :

{% for heritier in origine_ant.heritiers %}
{{ loop.index }}°) **{{ heritier.civilite }} <<<VAR_START>>>{{ heritier.prenom }} {{ heritier.nom | upper }}<<<VAR_END>>>**, né(e) à <<<VAR_START>>>{{ heritier.lieu_naissance }}<<<VAR_END>>> le <<<VAR_START>>>{{ heritier.date_naissance | format_date }}<<<VAR_END>>>

{{ heritier.lien_parente }}

{% endfor %}

Habiles à se dire et porter héritiers ensemble pour le tout ou chacun divisément pour <<<VAR_START>>>{{ origine_ant.quotite_heritiers }}<<<VAR_END>>>.

{% if origine_ant.acte_notoriete %}
L'acte de notoriété constatant cette dévolution a été reçu par Maître <<<VAR_START>>>{{ origine_ant.acte_notoriete.notaire }}<<<VAR_END>>>, notaire à <<<VAR_START>>>{{ origine_ant.acte_notoriete.lieu }}<<<VAR_END>>>, le <<<VAR_START>>>{{ origine_ant.acte_notoriete.date | format_date }}<<<VAR_END>>>.
{% endif %}

{% if origine_ant.attestation_propriete %}
L'attestation de propriété a été reçue par Maître <<<VAR_START>>>{{ origine_ant.attestation_propriete.notaire }}<<<VAR_END>>>, notaire à <<<VAR_START>>>{{ origine_ant.attestation_propriete.lieu }}<<<VAR_END>>>, le <<<VAR_START>>>{{ origine_ant.attestation_propriete.date | format_date }}<<<VAR_END>>>.

{% if origine_ant.attestation_propriete.publication %}
Une copie authentique de cet acte a été publiée au service de la publicité foncière de <<<VAR_START>>>{{ origine_ant.attestation_propriete.publication.service }}<<<VAR_END>>> le <<<VAR_START>>>{{ origine_ant.attestation_propriete.publication.date | format_date }}<<<VAR_END>>>.
{% endif %}
{% endif %}

{% elif origine_ant.type == 'licitation' %}
{{ origine_ant.beneficiaire.civilite }} <<<VAR_START>>>{{ origine_ant.beneficiaire.prenom }} {{ origine_ant.beneficiaire.nom | upper }}<<<VAR_END>>> est resté(e) seul(e) attributaire du bien par suite de l'acquisition à titre de licitation faisant cesser l'indivision qu'il/elle a faite de la quote-part appartenant à :

{% for coindivisaire in origine_ant.coindivisaires %}
**{{ coindivisaire.civilite }} <<<VAR_START>>>{{ coindivisaire.prenom }} {{ coindivisaire.nom | upper }}<<<VAR_END>>>**, {{ coindivisaire.profession }}, demeurant à <<<VAR_START>>>{{ coindivisaire.adresse }}<<<VAR_END>>>

Né(e) à <<<VAR_START>>>{{ coindivisaire.lieu_naissance }}<<<VAR_END>>> le <<<VAR_START>>>{{ coindivisaire.date_naissance | format_date }}<<<VAR_END>>>
{% endfor %}

Suivant acte reçu par Maître <<<VAR_START>>>{{ origine_ant.notaire }}<<<VAR_END>>>, notaire à <<<VAR_START>>>{{ origine_ant.lieu }}<<<VAR_END>>>, le <<<VAR_START>>>{{ origine_ant.date | format_date }}<<<VAR_END>>>.

{% if origine_ant.publication %}
Une copie authentique a été publiée au service de la publicité foncière de <<<VAR_START>>>{{ origine_ant.publication.service }}<<<VAR_END>>> le <<<VAR_START>>>{{ origine_ant.publication.date | format_date }}<<<VAR_END>>>, volume <<<VAR_START>>>{{ origine_ant.publication.volume }}<<<VAR_END>>>, numéro <<<VAR_START>>>{{ origine_ant.publication.numero }}<<<VAR_END>>>.
{% endif %}

{% endif %}

{% endfor %}
{% endif %}

### Titre originaire

{% if origine.titre_originaire %}
ORIGINAIREMENT, lesdits biens et droits immobiliers appartenaient à <<<VAR_START>>>{{ origine.titre_originaire.proprietaire }}<<<VAR_END>>> par suite de <<<VAR_START>>>{{ origine.titre_originaire.mode_acquisition }}<<<VAR_END>>>.

{% if origine.titre_originaire.details %}
{{ origine.titre_originaire.details }}
{% endif %}

{% if origine.titre_originaire.acte %}
Suivant acte reçu par Maître <<<VAR_START>>>{{ origine.titre_originaire.acte.notaire }}<<<VAR_END>>>, notaire à <<<VAR_START>>>{{ origine.titre_originaire.acte.lieu }}<<<VAR_END>>>, le <<<VAR_START>>>{{ origine.titre_originaire.acte.date | format_date }}<<<VAR_END>>>.

{% if origine.titre_originaire.acte.publication %}
Cet acte a été publié au service de la publicité foncière de <<<VAR_START>>>{{ origine.titre_originaire.acte.publication.service }}<<<VAR_END>>> le <<<VAR_START>>>{{ origine.titre_originaire.acte.publication.date | format_date }}<<<VAR_END>>>, volume <<<VAR_START>>>{{ origine.titre_originaire.acte.publication.volume }}<<<VAR_END>>>, numéro <<<VAR_START>>>{{ origine.titre_originaire.acte.publication.numero }}<<<VAR_END>>>.
{% endif %}
{% endif %}
{% endif %}

{% endfor %}
{% endif %}
