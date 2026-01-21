## État des risques et pollutions

{% if risques %}

### État des Risques et Pollutions (ERP)

Conformément aux dispositions des articles L. 125-5 et suivants du Code de l'environnement, un État des Risques et Pollutions (ERP) a été établi.

{% if risques.erp %}
{% if risques.erp.date %}
**Date de l'état** : <<<VAR_START>>>{{ risques.erp.date }}<<<VAR_END>>>
{% endif %}

{% if risques.erp.reference %}
**Référence du document** : <<<VAR_START>>>{{ risques.erp.reference }}<<<VAR_END>>>
{% endif %}

{% if risques.erp.validite %}
Cet état est valable jusqu'au <<<VAR_START>>>{{ risques.erp.validite }}<<<VAR_END>>> (validité de 6 mois).
{% endif %}

{% if risques.erp.zone_sismicite %}
**Zone de sismicité** : <<<VAR_START>>>{{ risques.erp.zone_sismicite }}<<<VAR_END>>>
{% endif %}

{% if risques.erp.zone_radon %}
**Zonage du potentiel radon** : <<<VAR_START>>>{{ risques.erp.zone_radon }}<<<VAR_END>>>
{% endif %}

{% if risques.erp.exposition_bruit %}
**Exposition au bruit des aéroports** : {% if risques.erp.exposition_bruit.applicable %}Oui - <<<VAR_START>>>{{ risques.erp.exposition_bruit.plan }}<<<VAR_END>>>{% else %}Non{% endif %}
{% endif %}

{% else %}
Un État des Risques et Pollutions sera annexé au présent acte.
{% endif %}

### Risques naturels

{% if risques.naturels %}
{% if risques.naturels.inondation %}
#### Risque d'inondation

{% if risques.naturels.inondation.expose %}
Le bien est situé dans une zone exposée au risque d'inondation.

{% if risques.naturels.inondation.type %}
**Type d'inondation** : <<<VAR_START>>>{{ risques.naturels.inondation.type }}<<<VAR_END>>>
{% endif %}

{% if risques.naturels.inondation.aleas %}
**Niveau d'aléa** : <<<VAR_START>>>{{ risques.naturels.inondation.aleas }}<<<VAR_END>>>
{% endif %}

{% if risques.naturels.inondation.sinistres and risques.naturels.inondation.sinistres|length > 0 %}
**Sinistres indemnisés** :
{% for sinistre in risques.naturels.inondation.sinistres %}
{% if sinistre.date %}
- Date : <<<VAR_START>>>{{ sinistre.date }}<<<VAR_END>>>{% if sinistre.reconnaissance_catastrophe %} (reconnu catastrophe naturelle le <<<VAR_START>>>{{ sinistre.reconnaissance_catastrophe }}<<<VAR_END>>>){% endif %}
{% if sinistre.description %}
  Description : <<<VAR_START>>>{{ sinistre.description }}<<<VAR_END>>>
{% endif %}
{% if sinistre.montant_indemnise %}
  Montant indemnisé : <<<VAR_START>>>{{ sinistre.montant_indemnise | format_nombre }}<<<VAR_END>>> EUR
{% endif %}
{% endif %}
{% endfor %}
{% endif %}

{% if risques.naturels.inondation.travaux_protection %}
**Travaux de protection réalisés** : <<<VAR_START>>>{{ risques.naturels.inondation.travaux_protection }}<<<VAR_END>>>
{% endif %}

{% else %}
Le bien n'est pas exposé à un risque d'inondation connu.
{% endif %}
{% endif %}

{% if risques.naturels.mouvement_terrain %}
#### Risque de mouvement de terrain

{% if risques.naturels.mouvement_terrain.expose %}
Le bien est situé dans une zone exposée au risque de mouvement de terrain.

{% if risques.naturels.mouvement_terrain.type %}
**Type de mouvement** : <<<VAR_START>>>{{ risques.naturels.mouvement_terrain.type }}<<<VAR_END>>>
{% endif %}

{% if risques.naturels.mouvement_terrain.cavites %}
**Présence de cavités souterraines** : {% if risques.naturels.mouvement_terrain.cavites.connues %}Oui{% if risques.naturels.mouvement_terrain.cavites.type %} (<<<VAR_START>>>{{ risques.naturels.mouvement_terrain.cavites.type }}<<<VAR_END>>>){% endif %}{% else %}Non{% endif %}
{% endif %}

{% else %}
Le bien n'est pas exposé à un risque de mouvement de terrain connu.
{% endif %}
{% endif %}

{% if risques.naturels.seisme %}
#### Risque sismique

{% if risques.naturels.seisme.zone %}
**Zone de sismicité** : <<<VAR_START>>>{{ risques.naturels.seisme.zone }}<<<VAR_END>>>

{% if risques.naturels.seisme.prescriptions %}
Prescriptions particulières : <<<VAR_START>>>{{ risques.naturels.seisme.prescriptions }}<<<VAR_END>>>
{% endif %}
{% endif %}
{% endif %}

{% if risques.naturels.autres and risques.naturels.autres|length > 0 %}
#### Autres risques naturels

{% for risque in risques.naturels.autres %}
{% if risque.type %}
**{{ risque.type | capitalize }}**
{% if risque.description %}
- Description : <<<VAR_START>>>{{ risque.description }}<<<VAR_END>>>
{% endif %}
{% if risque.niveau_aleas %}
- Niveau d'aléa : <<<VAR_START>>>{{ risque.niveau_aleas }}<<<VAR_END>>>
{% endif %}
{% endif %}
{% endfor %}
{% endif %}

{% else %}
À la connaissance du VENDEUR, le bien n'est exposé à aucun risque naturel particulier.
{% endif %}

### Risques technologiques

{% if risques.technologiques %}
{% if risques.technologiques.icpe %}
#### Installations Classées pour la Protection de l'Environnement (ICPE)

{% if risques.technologiques.icpe.proximite %}
Le bien est situé à proximité d'installations classées :

{% for installation in risques.technologiques.icpe.liste %}
{% if installation.nom %}
**{{ installation.nom }}**
{% if installation.distance %}
- Distance : <<<VAR_START>>>{{ installation.distance }}<<<VAR_END>>> mètres
{% endif %}
{% if installation.regime %}
- Régime : <<<VAR_START>>>{{ installation.regime }}<<<VAR_END>>>
{% endif %}
{% if installation.activite %}
- Activité : <<<VAR_START>>>{{ installation.activite }}<<<VAR_END>>>
{% endif %}
{% endif %}
{% endfor %}

{% else %}
Le bien n'est pas situé à proximité d'installations classées.
{% endif %}
{% endif %}

{% if risques.technologiques.seveso %}
#### Sites SEVESO

{% if risques.technologiques.seveso.proximite %}
Le bien est situé à proximité d'un site SEVESO :

{% if risques.technologiques.seveso.nom %}
**Nom de l'installation** : <<<VAR_START>>>{{ risques.technologiques.seveso.nom }}<<<VAR_END>>>
{% endif %}

{% if risques.technologiques.seveso.seuil %}
**Seuil** : <<<VAR_START>>>{{ risques.technologiques.seveso.seuil }}<<<VAR_END>>>
{% endif %}

{% if risques.technologiques.seveso.distance %}
**Distance** : <<<VAR_START>>>{{ risques.technologiques.seveso.distance }}<<<VAR_END>>> mètres
{% endif %}

{% else %}
Le bien n'est pas situé à proximité d'un site SEVESO.
{% endif %}
{% endif %}

{% else %}
À la connaissance du VENDEUR, le bien n'est exposé à aucun risque technologique particulier.
{% endif %}

### Pollution des sols

{% if risques.pollution %}
#### Inventaires BASIAS et BASOL

{% if risques.pollution.basias %}
**Base BASIAS (inventaire historique)**

{% if risques.pollution.basias.present %}
Le bien ou sa parcelle figure dans l'inventaire BASIAS des sites industriels et activités de service.

{% if risques.pollution.basias.reference %}
**Référence BASIAS** : <<<VAR_START>>>{{ risques.pollution.basias.reference }}<<<VAR_END>>>
{% endif %}

{% if risques.pollution.basias.activite %}
**Activité recensée** : <<<VAR_START>>>{{ risques.pollution.basias.activite }}<<<VAR_END>>>
{% endif %}

{% if risques.pollution.basias.periode %}
**Période d'activité** : <<<VAR_START>>>{{ risques.pollution.basias.periode }}<<<VAR_END>>>
{% endif %}

{% if risques.pollution.basias.commentaire %}
<<<VAR_START>>>{{ risques.pollution.basias.commentaire }}<<<VAR_END>>>
{% endif %}

{% else %}
Le bien ne figure pas dans l'inventaire BASIAS.
{% endif %}
{% endif %}

{% if risques.pollution.basol %}
**Base BASOL (sites et sols pollués)**

{% if risques.pollution.basol.present %}
Le bien ou sa parcelle figure dans l'inventaire BASOL des sites et sols pollués appelant une action des pouvoirs publics.

{% if risques.pollution.basol.reference %}
**Référence BASOL** : <<<VAR_START>>>{{ risques.pollution.basol.reference }}<<<VAR_END>>>
{% endif %}

{% if risques.pollution.basol.origine %}
**Origine de la pollution** : <<<VAR_START>>>{{ risques.pollution.basol.origine }}<<<VAR_END>>>
{% endif %}

{% if risques.pollution.basol.statut %}
**Statut du site** : <<<VAR_START>>>{{ risques.pollution.basol.statut }}<<<VAR_END>>>
{% endif %}

{% if risques.pollution.basol.mesures %}
**Mesures prises ou à prendre** : <<<VAR_START>>>{{ risques.pollution.basol.mesures }}<<<VAR_END>>>
{% endif %}

{% else %}
Le bien ne figure pas dans l'inventaire BASOL.
{% endif %}
{% endif %}

{% if risques.pollution.diagnostic_pollution %}
#### Diagnostic de pollution

Un diagnostic de pollution des sols a été réalisé.

{% if risques.pollution.diagnostic_pollution.date %}
**Date du diagnostic** : <<<VAR_START>>>{{ risques.pollution.diagnostic_pollution.date }}<<<VAR_END>>>
{% endif %}

{% if risques.pollution.diagnostic_pollution.operateur %}
**Opérateur** : <<<VAR_START>>>{{ risques.pollution.diagnostic_pollution.operateur }}<<<VAR_END>>>
{% endif %}

{% if risques.pollution.diagnostic_pollution.conclusion %}
**Conclusion** : <<<VAR_START>>>{{ risques.pollution.diagnostic_pollution.conclusion }}<<<VAR_END>>>
{% endif %}

{% if risques.pollution.diagnostic_pollution.polluants_detectes and risques.pollution.diagnostic_pollution.polluants_detectes|length > 0 %}
**Polluants détectés** :
{% for polluant in risques.pollution.diagnostic_pollution.polluants_detectes %}
{% if polluant.nom %}
- <<<VAR_START>>>{{ polluant.nom }}<<<VAR_END>>>{% if polluant.concentration %} : <<<VAR_START>>>{{ polluant.concentration }}<<<VAR_END>>>{% endif %}
{% endif %}
{% endfor %}
{% endif %}

{% if risques.pollution.diagnostic_pollution.recommandations %}
**Recommandations** : <<<VAR_START>>>{{ risques.pollution.diagnostic_pollution.recommandations }}<<<VAR_END>>>
{% endif %}
{% endif %}

{% else %}
À la connaissance du VENDEUR, le bien n'est pas concerné par une pollution des sols.

Le bien ne figure ni dans l'inventaire BASIAS, ni dans l'inventaire BASOL.
{% endif %}

### Obligations d'information de l'acquéreur

{% if risques.obligations_information %}
Conformément aux articles L. 125-5, L. 125-7 et R. 125-23 à R. 125-27 du Code de l'environnement :

{% if risques.obligations_information.erp_remis %}
{% if risques.obligations_information.erp_remis_date %}
1. L'État des Risques et Pollutions a été remis à l'acquéreur le <<<VAR_START>>>{{ risques.obligations_information.erp_remis_date }}<<<VAR_END>>>
{% else %}
1. L'État des Risques et Pollutions a été remis à l'acquéreur
{% endif %}
{% else %}
1. L'État des Risques et Pollutions sera remis à l'acquéreur préalablement à la signature du présent acte
{% endif %}

{% if risques.obligations_information.sinistres_declares %}
2. Le VENDEUR déclare que le bien a subi des sinistres ayant donné lieu à indemnisation au titre d'une catastrophe naturelle ou technologique (voir détails ci-dessus)
{% else %}
2. Le VENDEUR déclare que, à sa connaissance, le bien n'a pas subi de sinistres ayant donné lieu à indemnisation au titre d'une catastrophe naturelle ou technologique
{% endif %}

{% if risques.obligations_information.information_sols %}
3. Une Information sur la Pollution des Sols (IPS) {% if risques.pollution and risques.pollution.basias and risques.pollution.basias.present %}a été annexée{% else %}n'est pas requise{% endif %}
{% endif %}

L'ACQUEREUR reconnaît avoir été parfaitement informé de l'ensemble des risques et pollutions affectant le bien.
{% else %}
Conformément aux dispositions du Code de l'environnement, le VENDEUR a remis à l'ACQUEREUR l'État des Risques et Pollutions et l'a informé des sinistres éventuels survenus pendant la période de détention du bien.

L'ACQUEREUR reconnaît avoir été parfaitement informé.
{% endif %}

{% if risques.remarques %}

### Remarques particulières

<<<VAR_START>>>{{ risques.remarques }}<<<VAR_END>>>
{% endif %}

{% else %}
Conformément à la réglementation en vigueur, un État des Risques et Pollutions (ERP) sera annexé au présent acte.

Le VENDEUR déclare que, à sa connaissance, le bien n'a pas subi de sinistres ayant donné lieu à indemnisation au titre d'une catastrophe naturelle ou technologique.

L'ACQUEREUR reconnaît avoir été informé de l'obligation de se renseigner sur les risques naturels et technologiques affectant le bien auprès des autorités compétentes.
{% endif %}
