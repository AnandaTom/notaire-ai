## Déclaration d'usage et obligations légales

{% if obligations %}

{% if obligations.declaration_usage %}
### Déclaration d'usage du bien

{% if obligations.declaration_usage.fait %}
**Déclaration effectuée** : Le VENDEUR déclare que le bien vendu a été occupé de la manière suivante :

{% if obligations.declaration_usage.type_occupation %}
**Type d'occupation** : <<<VAR_START>>>{{ obligations.declaration_usage.type_occupation }}<<<VAR_END>>>

{% if obligations.declaration_usage.type_occupation == 'residence_principale' %}
Le bien constituait la résidence principale du VENDEUR.

{% if obligations.declaration_usage.duree_occupation %}
**Durée d'occupation** : <<<VAR_START>>>{{ obligations.declaration_usage.duree_occupation }}<<<VAR_END>>> ans
{% endif %}

{% if obligations.declaration_usage.date_debut_occupation %}
**Date de début d'occupation** : <<<VAR_START>>>{{ obligations.declaration_usage.date_debut_occupation }}<<<VAR_END>>>
{% endif %}

{% if obligations.declaration_usage.date_fin_occupation %}
**Date de fin d'occupation** : <<<VAR_START>>>{{ obligations.declaration_usage.date_fin_occupation }}<<<VAR_END>>>
{% endif %}

{% elif obligations.declaration_usage.type_occupation == 'location' %}
Le bien était loué à usage d'habitation.

{% if obligations.declaration_usage.dernier_locataire %}
**Dernier locataire** : <<<VAR_START>>>{{ obligations.declaration_usage.dernier_locataire.nom }}<<<VAR_END>>>
{% endif %}

{% if obligations.declaration_usage.date_fin_bail %}
**Date de fin du bail** : <<<VAR_START>>>{{ obligations.declaration_usage.date_fin_bail }}<<<VAR_END>>>
{% endif %}

{% if obligations.declaration_usage.type_bail %}
**Type de bail** : <<<VAR_START>>>{{ obligations.declaration_usage.type_bail }}<<<VAR_END>>>
{% endif %}

{% if obligations.declaration_usage.loyer_mensuel %}
**Dernier loyer mensuel** : <<<VAR_START>>>{{ obligations.declaration_usage.loyer_mensuel | format_nombre }}<<<VAR_END>>> EUR hors charges
{% endif %}

{% elif obligations.declaration_usage.type_occupation == 'vacant' %}
Le bien est actuellement vacant.

{% if obligations.declaration_usage.date_vacance %}
**Date de début de vacance** : <<<VAR_START>>>{{ obligations.declaration_usage.date_vacance }}<<<VAR_END>>>
{% endif %}

{% if obligations.declaration_usage.motif_vacance %}
**Motif de vacance** : <<<VAR_START>>>{{ obligations.declaration_usage.motif_vacance }}<<<VAR_END>>>
{% endif %}

{% elif obligations.declaration_usage.type_occupation == 'residence_secondaire' %}
Le bien constituait une résidence secondaire.

{% if obligations.declaration_usage.frequence_occupation %}
**Fréquence d'occupation** : <<<VAR_START>>>{{ obligations.declaration_usage.frequence_occupation }}<<<VAR_END>>>
{% endif %}

{% endif %}
{% endif %}

{% if obligations.declaration_usage.destination_acquereur %}
**Destination déclarée par l'ACQUEREUR** : <<<VAR_START>>>{{ obligations.declaration_usage.destination_acquereur }}<<<VAR_END>>>

{% if obligations.declaration_usage.destination_acquereur == 'location' %}
L'ACQUEREUR déclare avoir l'intention de louer le bien.

{% if obligations.declaration_usage.date_mise_location_prevue %}
**Date de mise en location prévue** : <<<VAR_START>>>{{ obligations.declaration_usage.date_mise_location_prevue }}<<<VAR_END>>>
{% endif %}

{% elif obligations.declaration_usage.destination_acquereur == 'residence_principale' %}
L'ACQUEREUR déclare avoir l'intention d'occuper le bien comme résidence principale.

{% if obligations.declaration_usage.date_emmenagement_prevue %}
**Date d'emménagement prévue** : <<<VAR_START>>>{{ obligations.declaration_usage.date_emmenagement_prevue }}<<<VAR_END>>>
{% endif %}

{% endif %}
{% endif %}

{% else %}
Le VENDEUR déclare que le bien est vendu dans l'état où il se trouve, sans précision particulière quant à son usage antérieur.
{% endif %}
{% endif %}

{% if obligations.loi_anti_squat %}
### Protection contre l'occupation illicite (Loi anti-squat)

Conformément à l'article 38 de la loi n° 2020-1525 du 7 décembre 2020 (loi dite "anti-squat"), le VENDEUR informe l'ACQUEREUR des dispositions relatives à la protection contre l'occupation illicite de domicile.

{% if obligations.loi_anti_squat.information_donnee %}
**Information donnée** : L'ACQUEREUR déclare avoir été informé de la possibilité de :

- Déposer plainte pour violation de domicile (article 226-4 du Code pénal) en cas d'occupation sans droit ni titre ;
- Saisir le préfet pour obtenir la mise en demeure de l'occupant de quitter les lieux dans un délai de 24 heures ;
- Engager une procédure d'expulsion accélérée devant le juge des référés.

{% if obligations.loi_anti_squat.delai_intervention %}
**Délai d'intervention du préfet** : <<<VAR_START>>>{{ obligations.loi_anti_squat.delai_intervention }}<<<VAR_END>>> heures maximum après la mise en demeure
{% endif %}
{% endif %}

{% if obligations.loi_anti_squat.mesures_prevention %}
#### Mesures de prévention recommandées

Il est recommandé à l'ACQUEREUR de :

{% if obligations.loi_anti_squat.mesures_prevention.surveillance %}
- Assurer une surveillance régulière du bien s'il reste vacant ;
{% endif %}

{% if obligations.loi_anti_squat.mesures_prevention.securisation %}
- Sécuriser les accès (portes, fenêtres, grilles) ;
{% endif %}

{% if obligations.loi_anti_squat.mesures_prevention.voisinage %}
- Informer le voisinage et le syndic en cas de vacance prolongée ;
{% endif %}

{% if obligations.loi_anti_squat.mesures_prevention.assurance %}
- Vérifier la couverture d'assurance en cas de vacance.
{% endif %}
{% endif %}

{% if obligations.loi_anti_squat.historique %}
**Historique du bien** : Le VENDEUR déclare que le bien <<<VAR_START>>>{{ obligations.loi_anti_squat.historique.statut }}<<<VAR_END>>> fait l'objet d'une occupation illicite au cours des <<<VAR_START>>>{{ obligations.loi_anti_squat.historique.periode }}<<<VAR_END>>> dernières années.

{% if obligations.loi_anti_squat.historique.incident %}
Un incident d'occupation illicite a eu lieu :
- Date : <<<VAR_START>>>{{ obligations.loi_anti_squat.historique.incident.date }}<<<VAR_END>>>
- Durée : <<<VAR_START>>>{{ obligations.loi_anti_squat.historique.incident.duree }}<<<VAR_END>>>
- Résolution : <<<VAR_START>>>{{ obligations.loi_anti_squat.historique.incident.resolution }}<<<VAR_END>>>
{% endif %}
{% endif %}
{% endif %}

{% if obligations.fichier_locataires %}
### Fichier des locataires

{% if obligations.fichier_locataires.applicable %}
Conformément à l'article 4-2 de la loi n° 89-462 du 6 juillet 1989, le bailleur peut constituer un fichier des locataires.

{% if obligations.fichier_locataires.constitue %}
**Fichier constitué** : Le VENDEUR a constitué un fichier de gestion locative conforme au Règlement Général sur la Protection des Données (RGPD).

{% if obligations.fichier_locataires.declaration_cnil %}
**Déclaration CNIL** : <<<VAR_START>>>{{ obligations.fichier_locataires.declaration_cnil.statut }}<<<VAR_END>>>

{% if obligations.fichier_locataires.declaration_cnil.numero %}
Numéro de déclaration : <<<VAR_START>>>{{ obligations.fichier_locataires.declaration_cnil.numero }}<<<VAR_END>>>
{% endif %}

{% if obligations.fichier_locataires.declaration_cnil.date %}
Date de déclaration : <<<VAR_START>>>{{ obligations.fichier_locataires.declaration_cnil.date }}<<<VAR_END>>>
{% endif %}
{% endif %}

{% if obligations.fichier_locataires.donnees_conservees %}
**Données conservées** :
{% for donnee in obligations.fichier_locataires.donnees_conservees %}
- <<<VAR_START>>>{{ donnee }}<<<VAR_END>>>
{% endfor %}
{% endif %}

{% if obligations.fichier_locataires.duree_conservation %}
**Durée de conservation des données** : <<<VAR_START>>>{{ obligations.fichier_locataires.duree_conservation }}<<<VAR_END>>> ans après la fin du bail
{% endif %}

{% if obligations.fichier_locataires.transfert_acquereur %}
**Transfert à l'ACQUEREUR** : Le fichier locataire <<<VAR_START>>>{{ obligations.fichier_locataires.transfert_acquereur.statut }}<<<VAR_END>>> transféré à l'ACQUEREUR.

{% if obligations.fichier_locataires.transfert_acquereur.statut == 'sera' %}
L'ACQUEREUR s'engage à :
- Informer les locataires concernés du transfert de leurs données personnelles ;
- Respecter les obligations du RGPD en matière de protection des données ;
- Permettre aux locataires d'exercer leurs droits (accès, rectification, suppression) ;
- Conserver les données uniquement pour la durée nécessaire à la gestion locative.
{% endif %}
{% endif %}

{% else %}
Le VENDEUR n'a pas constitué de fichier locataire pour ce bien.

L'ACQUEREUR, s'il souhaite mettre le bien en location, devra respecter les obligations du RGPD en cas de constitution d'un fichier de gestion locative.
{% endif %}
{% endif %}
{% endif %}

{% if obligations.informations_complementaires %}
### Informations complémentaires

{% if obligations.informations_complementaires.reglementation_location %}
#### Réglementation de la location (si applicable)

{% if obligations.informations_complementaires.reglementation_location.zone_tendue %}
**Zone tendue** : Le bien est situé dans une zone tendue au sens du décret n° 2013-392 du 10 mai 2013.

Conséquences :
- Encadrement de l'évolution des loyers lors du renouvellement du bail ;
- Délai de préavis réduit à 1 mois pour le locataire ;
- Obligation de proposer le renouvellement du bail 6 mois avant son terme.
{% endif %}

{% if obligations.informations_complementaires.reglementation_location.encadrement_loyers %}
**Encadrement des loyers** : Le bien est situé dans une zone soumise à l'encadrement des loyers.

{% if obligations.informations_complementaires.reglementation_location.loyer_reference %}
- Loyer de référence : <<<VAR_START>>>{{ obligations.informations_complementaires.reglementation_location.loyer_reference | format_nombre }}<<<VAR_END>>> EUR/m²
{% endif %}

{% if obligations.informations_complementaires.reglementation_location.loyer_reference_majore %}
- Loyer de référence majoré : <<<VAR_START>>>{{ obligations.informations_complementaires.reglementation_location.loyer_reference_majore | format_nombre }}<<<VAR_END>>> EUR/m²
{% endif %}
{% endif %}
{% endif %}

{% if obligations.informations_complementaires.dpe_location %}
#### Performance énergétique et location

{% if obligations.informations_complementaires.dpe_location.classe_interdite %}
Attention : Conformément à la loi n° 2021-1104 du 22 août 2021 (loi Climat et Résilience), les logements classés <<<VAR_START>>>{{ obligations.informations_complementaires.dpe_location.classe_actuelle }}<<<VAR_END>>> au DPE seront progressivement interdits à la location :

{% if obligations.informations_complementaires.dpe_location.date_interdiction %}
- Date d'interdiction : <<<VAR_START>>>{{ obligations.informations_complementaires.dpe_location.date_interdiction }}<<<VAR_END>>>
{% endif %}

{% if obligations.informations_complementaires.dpe_location.travaux_necessaires %}
**Travaux nécessaires pour mise en conformité** : <<<VAR_START>>>{{ obligations.informations_complementaires.dpe_location.travaux_necessaires }}<<<VAR_END>>>
{% endif %}
{% endif %}
{% endif %}
{% endif %}

{% else %}
Le VENDEUR déclare que le bien est vendu sans obligation particulière liée à son usage futur.

L'ACQUEREUR déclare être informé des obligations légales en matière de :
- Déclaration d'usage du bien ;
- Protection contre l'occupation illicite (loi anti-squat) ;
- Protection des données personnelles (RGPD) en cas de location ;
- Réglementations spécifiques à la location (zones tendues, encadrement des loyers, performance énergétique).
{% endif %}
