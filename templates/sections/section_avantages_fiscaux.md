## Avantages fiscaux

{% if avantages_fiscaux %}

### Dispositif fiscal applicable

{% if avantages_fiscaux.type %}
**Dispositif** : <<<VAR_START>>>{{ avantages_fiscaux.type }}<<<VAR_END>>>

{% if avantages_fiscaux.type == 'pinel' %}
#### Dispositif Pinel

Le bien acquis bénéficie du dispositif de défiscalisation Pinel prévu aux articles 199 novovicies du Code général des impôts.

{% if avantages_fiscaux.duree_engagement %}
**Durée d'engagement de location** : <<<VAR_START>>>{{ avantages_fiscaux.duree_engagement }}<<<VAR_END>>> ans

{% if avantages_fiscaux.taux_reduction %}
**Taux de réduction d'impôt** : <<<VAR_START>>>{{ avantages_fiscaux.taux_reduction }}<<<VAR_END>>> %
{% endif %}

{% if avantages_fiscaux.montant_reduction_annuelle %}
**Montant annuel de réduction d'impôt** : <<<VAR_START>>>{{ avantages_fiscaux.montant_reduction_annuelle | format_nombre }}<<<VAR_END>>> EUR
{% endif %}
{% endif %}

{% if avantages_fiscaux.plafond_loyer %}
**Plafond de loyer mensuel applicable** : <<<VAR_START>>>{{ avantages_fiscaux.plafond_loyer | format_nombre }}<<<VAR_END>>> EUR/m²
{% endif %}

{% if avantages_fiscaux.plafond_ressources %}
**Conditions de ressources des locataires** : Le locataire devra respecter les plafonds de ressources définis à l'article 2 terdecies D de l'annexe III du Code général des impôts pour la zone <<<VAR_START>>>{{ avantages_fiscaux.zone_pinel | default("à déterminer") }}<<<VAR_END>>>.
{% endif %}

**Engagement de l'ACQUEREUR** :

L'ACQUEREUR s'engage à :
- Louer le bien nu à usage d'habitation principale pendant la durée d'engagement ;
- Respecter les plafonds de loyers et de ressources des locataires ;
- Déclarer annuellement les revenus fonciers conformément aux dispositions fiscales.

{% elif avantages_fiscaux.type == 'denormandie' %}
#### Dispositif Denormandie

Le bien acquis bénéficie du dispositif de défiscalisation Denormandie prévu à l'article 199 novovicies du Code général des impôts dans sa version applicable aux logements anciens avec travaux.

{% if avantages_fiscaux.duree_engagement %}
**Durée d'engagement de location** : <<<VAR_START>>>{{ avantages_fiscaux.duree_engagement }}<<<VAR_END>>> ans
{% endif %}

{% if avantages_fiscaux.montant_travaux %}
**Montant des travaux d'amélioration** : <<<VAR_START>>>{{ avantages_fiscaux.montant_travaux | format_nombre }}<<<VAR_END>>> EUR

{% if avantages_fiscaux.pourcentage_travaux %}
Soit <<<VAR_START>>>{{ avantages_fiscaux.pourcentage_travaux }}<<<VAR_END>>> % du coût total de l'opération (minimum légal : 25%)
{% endif %}
{% endif %}

{% if avantages_fiscaux.plafond_loyer %}
**Plafond de loyer mensuel applicable** : <<<VAR_START>>>{{ avantages_fiscaux.plafond_loyer | format_nombre }}<<<VAR_END>>> EUR/m²
{% endif %}

**Engagement de l'ACQUEREUR** :

L'ACQUEREUR s'engage à :
- Réaliser les travaux d'amélioration dans un délai maximum de 3 ans ;
- Louer le bien nu à usage d'habitation principale pendant la durée d'engagement ;
- Respecter les plafonds de loyers et de ressources des locataires.

{% elif avantages_fiscaux.type == 'malraux' %}
#### Dispositif Malraux

Le bien acquis bénéficie du dispositif de défiscalisation Malraux prévu à l'article 199 tervicies du Code général des impôts.

{% if avantages_fiscaux.secteur_sauvegarde %}
**Secteur de protection** : <<<VAR_START>>>{{ avantages_fiscaux.secteur_sauvegarde }}<<<VAR_END>>>

{% if avantages_fiscaux.taux_reduction %}
**Taux de réduction d'impôt** : <<<VAR_START>>>{{ avantages_fiscaux.taux_reduction }}<<<VAR_END>>> %
{% endif %}
{% endif %}

{% if avantages_fiscaux.montant_travaux %}
**Montant des travaux de restauration** : <<<VAR_START>>>{{ avantages_fiscaux.montant_travaux | format_nombre }}<<<VAR_END>>> EUR
{% endif %}

{% if avantages_fiscaux.autorisation_travaux %}
**Autorisation de travaux** : Travaux autorisés par arrêté préfectoral en date du <<<VAR_START>>>{{ avantages_fiscaux.date_autorisation }}<<<VAR_END>>>
{% endif %}

**Engagement de l'ACQUEREUR** :

L'ACQUEREUR s'engage à :
- Réaliser les travaux conformément à l'autorisation délivrée ;
- Louer le bien nu pendant 9 ans minimum ;
- Respecter les prescriptions architecturales applicables au secteur.

{% endif %}
{% endif %}

{% if avantages_fiscaux.ptz %}
### Prêt à Taux Zéro (PTZ)

{% if avantages_fiscaux.ptz.eligible %}
**Éligibilité au PTZ** : Le bien acquis est éligible au Prêt à Taux Zéro conformément aux articles L. 31-10-1 et suivants du Code de la construction et de l'habitation.

{% if avantages_fiscaux.ptz.zone %}
**Zone PTZ** : <<<VAR_START>>>{{ avantages_fiscaux.ptz.zone }}<<<VAR_END>>>
{% endif %}

{% if avantages_fiscaux.ptz.montant_maximum %}
**Montant maximum du PTZ** : <<<VAR_START>>>{{ avantages_fiscaux.ptz.montant_maximum | format_nombre }}<<<VAR_END>>> EUR
{% endif %}

{% if avantages_fiscaux.ptz.conditions %}
**Conditions d'obtention** :
- Acquisition de la résidence principale ;
- Respect des plafonds de ressources ;
{% if avantages_fiscaux.ptz.primo_accedant %}
- Primo-accédant (aucune propriété de résidence principale au cours des 2 dernières années).
{% endif %}
{% endif %}

{% if avantages_fiscaux.ptz.obtenu %}
L'ACQUEREUR a obtenu un accord de principe pour un PTZ d'un montant de <<<VAR_START>>>{{ avantages_fiscaux.ptz.montant_obtenu | format_nombre }}<<<VAR_END>>> EUR auprès de <<<VAR_START>>>{{ avantages_fiscaux.ptz.organisme }}<<<VAR_END>>>.
{% endif %}
{% endif %}
{% endif %}

{% if avantages_fiscaux.obligations_declaratives %}
### Obligations déclaratives

L'ACQUEREUR devra :

{% if avantages_fiscaux.obligations_declaratives.declaration_revenus_fonciers %}
- Déclarer annuellement les revenus fonciers perçus sur le formulaire n° 2044 (régime réel) ou 2042 (micro-foncier) ;
{% endif %}

{% if avantages_fiscaux.obligations_declaratives.engagement_location %}
- Joindre à la déclaration de revenus l'engagement de location selon le modèle fourni par l'administration fiscale ;
{% endif %}

{% if avantages_fiscaux.obligations_declaratives.justificatifs %}
- Conserver tous les justificatifs de location (baux, quittances, avis d'imposition du locataire) pendant la durée de l'engagement et jusqu'à la fin de la prescription fiscale ;
{% endif %}

{% if avantages_fiscaux.obligations_declaratives.attestation_annuelle %}
- Fournir une attestation annuelle de respect des conditions du dispositif fiscal.
{% endif %}

{% if avantages_fiscaux.sanctions_non_respect %}
**Sanctions en cas de non-respect** : Le non-respect des engagements entraîne la reprise des avantages fiscaux obtenus, assortie des intérêts de retard et d'éventuelles pénalités fiscales conformément à l'article 1729 du Code général des impôts.
{% endif %}
{% endif %}

{% if avantages_fiscaux.centre_impots %}
### Centre des impôts compétent

{% if avantages_fiscaux.centre_impots.nom %}
**Service des impôts des particuliers** : <<<VAR_START>>>{{ avantages_fiscaux.centre_impots.nom }}<<<VAR_END>>>

{% if avantages_fiscaux.centre_impots.adresse %}
**Adresse** : <<<VAR_START>>>{{ avantages_fiscaux.centre_impots.adresse }}<<<VAR_END>>>
{% endif %}

{% if avantages_fiscaux.centre_impots.contact %}
**Contact** : <<<VAR_START>>>{{ avantages_fiscaux.centre_impots.contact }}<<<VAR_END>>>
{% endif %}
{% endif %}
{% endif %}

{% else %}
Le bien acquis ne bénéficie d'aucun dispositif de défiscalisation particulier.

L'ACQUEREUR déclare être informé des différents dispositifs d'aide fiscale à l'investissement locatif (Pinel, Denormandie, Malraux) et de leurs conditions d'application.
{% endif %}
