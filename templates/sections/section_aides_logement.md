## Aides au logement

{% if aides %}

{% if aides.apl %}
### Aide personnalisée au logement (APL)

{% if aides.apl.applicable %}
**Éligibilité APL** : Le bien acquis est susceptible de permettre au locataire de bénéficier de l'aide personnalisée au logement conformément aux articles L. 351-2 et suivants du Code de la construction et de l'habitation.

{% if aides.apl.type %}
**Type d'APL applicable** : <<<VAR_START>>>{{ aides.apl.type }}<<<VAR_END>>>
{% endif %}

{% if aides.apl.conventionnement %}
#### Conventionnement

{% if aides.apl.conventionnement.type %}
**Convention** : <<<VAR_START>>>{{ aides.apl.conventionnement.type }}<<<VAR_END>>>
{% endif %}

{% if aides.apl.conventionnement.date_signature %}
**Date de signature de la convention** : <<<VAR_START>>>{{ aides.apl.conventionnement.date_signature }}<<<VAR_END>>>
{% endif %}

{% if aides.apl.conventionnement.numero %}
**Numéro de convention** : <<<VAR_START>>>{{ aides.apl.conventionnement.numero }}<<<VAR_END>>>
{% endif %}

{% if aides.apl.conventionnement.organisme %}
**Organisme conventionné** : <<<VAR_START>>>{{ aides.apl.conventionnement.organisme }}<<<VAR_END>>>
{% endif %}

{% if aides.apl.conventionnement.duree %}
**Durée de la convention** : <<<VAR_START>>>{{ aides.apl.conventionnement.duree }}<<<VAR_END>>> ans
{% endif %}
{% endif %}

{% if aides.apl.plafonds %}
#### Plafonds applicables

{% if aides.apl.plafonds.loyer_maximum %}
**Plafond de loyer mensuel** : <<<VAR_START>>>{{ aides.apl.plafonds.loyer_maximum | format_nombre }}<<<VAR_END>>> EUR
{% endif %}

{% if aides.apl.plafonds.ressources_locataire %}
**Plafonds de ressources du locataire** : Conformes au barème en vigueur pour la zone <<<VAR_START>>>{{ aides.apl.zone | default("à déterminer") }}<<<VAR_END>>>.
{% endif %}

{% if aides.apl.montant_maximum %}
**Montant maximum d'APL estimé** : <<<VAR_START>>>{{ aides.apl.montant_maximum | format_nombre }}<<<VAR_END>>> EUR par mois (sous réserve de la situation du locataire)
{% endif %}
{% endif %}

{% if aides.apl.obligations_proprietaire %}
#### Obligations du propriétaire

Le propriétaire bailleur s'engage à :

{% if aides.apl.obligations_proprietaire.respecter_convention %}
- Respecter les termes de la convention APL pendant toute sa durée ;
{% endif %}

{% if aides.apl.obligations_proprietaire.plafonds_loyers %}
- Appliquer les plafonds de loyers définis par la convention ;
{% endif %}

{% if aides.apl.obligations_proprietaire.normes_decence %}
- Maintenir le logement en état de décence conformément au décret n° 2002-120 du 30 janvier 2002 ;
{% endif %}

{% if aides.apl.obligations_proprietaire.notification_caf %}
- Notifier à la CAF tout changement de locataire ou modification des conditions de location ;
{% endif %}

{% if aides.apl.obligations_proprietaire.declaration_annuelle %}
- Établir une déclaration annuelle des loyers perçus.
{% endif %}

{% if aides.apl.sanctions %}
**Sanctions** : Le non-respect des obligations peut entraîner la résiliation de la convention et le remboursement des aides indûment perçues par les locataires.
{% endif %}
{% endif %}

{% else %}
Le bien n'est pas conventionné pour l'aide personnalisée au logement. Le locataire pourra néanmoins solliciter l'allocation de logement familiale (ALF) ou l'allocation de logement sociale (ALS) sous réserve de remplir les conditions d'attribution.
{% endif %}
{% endif %}

{% if aides.anah %}
### Agence nationale de l'habitat (ANAH)

{% if aides.anah.subventions %}
**Subventions ANAH** : Le propriétaire bénéficie ou peut bénéficier de subventions de l'Agence nationale de l'habitat conformément aux articles L. 321-1 et suivants du Code de la construction et de l'habitation.

{% if aides.anah.programme %}
**Programme** : <<<VAR_START>>>{{ aides.anah.programme }}<<<VAR_END>>>
{% endif %}

{% if aides.anah.travaux_subventionnes %}
#### Travaux subventionnés

{% if aides.anah.travaux_subventionnes.nature %}
**Nature des travaux** : <<<VAR_START>>>{{ aides.anah.travaux_subventionnes.nature }}<<<VAR_END>>>
{% endif %}

{% if aides.anah.travaux_subventionnes.montant_total %}
**Coût total des travaux** : <<<VAR_START>>>{{ aides.anah.travaux_subventionnes.montant_total | format_nombre }}<<<VAR_END>>> EUR
{% endif %}

{% if aides.anah.travaux_subventionnes.montant_subvention %}
**Montant de la subvention ANAH** : <<<VAR_START>>>{{ aides.anah.travaux_subventionnes.montant_subvention | format_nombre }}<<<VAR_END>>> EUR

{% if aides.anah.travaux_subventionnes.taux_subvention %}
Soit <<<VAR_START>>>{{ aides.anah.travaux_subventionnes.taux_subvention }}<<<VAR_END>>> % du montant des travaux
{% endif %}
{% endif %}

{% if aides.anah.travaux_subventionnes.date_decision %}
**Décision d'attribution** : Décision n° <<<VAR_START>>>{{ aides.anah.travaux_subventionnes.numero_decision }}<<<VAR_END>>> en date du <<<VAR_START>>>{{ aides.anah.travaux_subventionnes.date_decision }}<<<VAR_END>>>
{% endif %}

{% if aides.anah.travaux_subventionnes.delai_realisation %}
**Délai de réalisation des travaux** : <<<VAR_START>>>{{ aides.anah.travaux_subventionnes.delai_realisation }}<<<VAR_END>>> mois à compter de la notification
{% endif %}
{% endif %}

{% if aides.anah.engagement_location %}
#### Engagement de location

En contrepartie de la subvention ANAH, le propriétaire s'engage à :

{% if aides.anah.engagement_location.duree %}
- Louer le bien pendant une durée minimale de <<<VAR_START>>>{{ aides.anah.engagement_location.duree }}<<<VAR_END>>> ans ;
{% endif %}

{% if aides.anah.engagement_location.type_locataire %}
- Louer à <<<VAR_START>>>{{ aides.anah.engagement_location.type_locataire }}<<<VAR_END>>> ;
{% endif %}

{% if aides.anah.engagement_location.plafond_loyer %}
- Respecter un plafond de loyer de <<<VAR_START>>>{{ aides.anah.engagement_location.plafond_loyer | format_nombre }}<<<VAR_END>>> EUR/m² ;
{% endif %}

{% if aides.anah.engagement_location.plafond_ressources %}
- Respecter les plafonds de ressources des locataires définis par l'ANAH pour la zone <<<VAR_START>>>{{ aides.anah.zone | default("à déterminer") }}<<<VAR_END>>>.
{% endif %}

{% if aides.anah.engagement_location.date_debut %}
**Date de début de l'engagement** : <<<VAR_START>>>{{ aides.anah.engagement_location.date_debut }}<<<VAR_END>>>
{% endif %}
{% endif %}

{% if aides.anah.obligations %}
#### Obligations du propriétaire

Le propriétaire s'engage à :

{% if aides.anah.obligations.realiser_travaux %}
- Réaliser les travaux conformément au projet validé par l'ANAH ;
{% endif %}

{% if aides.anah.obligations.justificatifs %}
- Fournir tous les justificatifs de réalisation des travaux (factures, attestations) ;
{% endif %}

{% if aides.anah.obligations.declaration_achevement %}
- Déclarer l'achèvement des travaux dans les délais impartis ;
{% endif %}

{% if aides.anah.obligations.controles %}
- Accepter les contrôles de l'ANAH pendant la durée de l'engagement ;
{% endif %}

{% if aides.anah.obligations.location_rapide %}
- Mettre le logement en location dans un délai maximum de <<<VAR_START>>>{{ aides.anah.obligations.delai_location | default("1 an") }}<<<VAR_END>>> après l'achèvement des travaux.
{% endif %}

{% if aides.anah.sanctions %}
**Sanctions** : Le non-respect des engagements entraîne le remboursement de la subvention avec intérêts et pénalités conformément à l'article L. 321-6 du Code de la construction et de l'habitation.
{% endif %}
{% endif %}

{% if aides.anah.cumul_autres_aides %}
#### Cumul avec d'autres aides

{% if aides.anah.cumul_autres_aides.possible %}
La subvention ANAH est cumulable avec :
{% if aides.anah.cumul_autres_aides.liste %}
{% for aide in aides.anah.cumul_autres_aides.liste %}
- <<<VAR_START>>>{{ aide }}<<<VAR_END>>>
{% endfor %}
{% endif %}
{% else %}
La subvention ANAH n'est pas cumulable avec d'autres dispositifs fiscaux pour ce bien.
{% endif %}
{% endif %}

{% else %}
Le propriétaire n'a pas sollicité de subvention auprès de l'Agence nationale de l'habitat pour ce bien.

{% if aides.anah.eligible %}
Le bien pourrait être éligible aux aides de l'ANAH sous réserve du respect des conditions d'attribution (travaux d'amélioration, engagement de location, respect des plafonds).
{% endif %}
{% endif %}
{% endif %}

{% if aides.contact %}
### Contacts et informations

{% if aides.contact.caf %}
**Caisse d'Allocations Familiales** : <<<VAR_START>>>{{ aides.contact.caf.nom }}<<<VAR_END>>>
{% if aides.contact.caf.telephone %}
Téléphone : <<<VAR_START>>>{{ aides.contact.caf.telephone }}<<<VAR_END>>>
{% endif %}
{% if aides.contact.caf.site_web %}
Site web : <<<VAR_START>>>{{ aides.contact.caf.site_web }}<<<VAR_END>>>
{% endif %}
{% endif %}

{% if aides.contact.anah %}
**Délégation locale ANAH** : <<<VAR_START>>>{{ aides.contact.anah.nom }}<<<VAR_END>>>
{% if aides.contact.anah.telephone %}
Téléphone : <<<VAR_START>>>{{ aides.contact.anah.telephone }}<<<VAR_END>>>
{% endif %}
{% if aides.contact.anah.email %}
Email : <<<VAR_START>>>{{ aides.contact.anah.email }}<<<VAR_END>>>
{% endif %}
{% endif %}
{% endif %}

{% else %}
Le bien acquis ne bénéficie d'aucune aide au logement spécifique (APL, ANAH).

L'ACQUEREUR déclare être informé de l'existence de ces dispositifs et des conditions pour en bénéficier ultérieurement.
{% endif %}

## Obligation declarative du proprietaire de bien a usage d'habitation

{% if aides and aides.declaration_occupation %}

### Article 1649 quater-0 B bis du Code general des impots

Conformement aux dispositions de l'article 1649 quater-0 B bis du Code general des impots, tout proprietaire d'un local affecte a l'habitation est tenu de declarer a l'administration fiscale, avant le 1er juillet de chaque annee, les informations relatives a la nature de l'occupation de ce local au 1er janvier.

{% if aides.declaration_occupation.effectuee %}
**Declaration effectuee** : <<<VAR_START>>>{{ "OUI" }}<<<VAR_END>>>

{% if aides.declaration_occupation.date %}
**Date de la derniere declaration** : <<<VAR_START>>>{{ aides.declaration_occupation.date }}<<<VAR_END>>>
{% endif %}

{% if aides.declaration_occupation.type_occupation %}
**Nature de l'occupation declaree** : <<<VAR_START>>>{{ aides.declaration_occupation.type_occupation }}<<<VAR_END>>>
{% endif %}

{% if aides.declaration_occupation.identite_occupant %}
**Identite de l'occupant** : <<<VAR_START>>>{{ aides.declaration_occupation.identite_occupant }}<<<VAR_END>>>
{% endif %}

{% if aides.declaration_occupation.montant_loyer %}
**Montant du loyer mensuel declare** : <<<VAR_START>>>{{ aides.declaration_occupation.montant_loyer | format_nombre }}<<<VAR_END>>> EUR
{% endif %}

{% else %}
**Declaration effectuee** : <<<VAR_START>>>{{ "NON" }}<<<VAR_END>>>

Le VENDEUR s'engage a regulariser cette declaration avant la signature de l'acte authentique ou a informer l'ACQUEREUR des consequences fiscales eventuelles.
{% endif %}

### Obligations de l'acquereur

L'ACQUEREUR est informe qu'il devra, a compter de la prise de possession du bien :

- Effectuer la declaration d'occupation via le service en ligne "Gerer mes biens immobiliers" sur impots.gouv.fr ;
- Mettre a jour cette declaration chaque annee avant le 1er juillet ;
- Declarer tout changement dans la situation d'occupation du bien (changement de locataire, mise en location, occupation personnelle, vacance).

{% if aides.declaration_occupation.sanctions %}
### Sanctions

Le defaut de declaration ou la declaration inexacte est passible d'une amende de <<<VAR_START>>>{{ aides.declaration_occupation.montant_amende | default("150") }}<<<VAR_END>>> EUR par local, conformement aux dispositions fiscales en vigueur.
{% endif %}

{% else %}
### Article 1649 quater-0 B bis du Code general des impots

Conformement aux dispositions de l'article 1649 quater-0 B bis du Code general des impots, tout proprietaire d'un local affecte a l'habitation est tenu de declarer a l'administration fiscale, avant le 1er juillet de chaque annee, les informations relatives a la nature de l'occupation de ce local au 1er janvier.

Le VENDEUR declare avoir satisfait a cette obligation declarative pour l'annee en cours.

### Obligations de l'acquereur

L'ACQUEREUR est informe qu'il devra, a compter de la prise de possession du bien :

- Effectuer la declaration d'occupation via le service en ligne "Gerer mes biens immobiliers" sur impots.gouv.fr ;
- Mettre a jour cette declaration chaque annee avant le 1er juillet ;
- Declarer tout changement dans la situation d'occupation du bien (changement de locataire, mise en location, occupation personnelle, vacance).

Le defaut de declaration ou la declaration inexacte est passible d'une amende de 150 EUR par local, conformement aux dispositions fiscales en vigueur.
{% endif %}
