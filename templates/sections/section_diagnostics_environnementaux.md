## Diagnostics environnementaux

### État des risques et pollutions (ERP)

{% if diagnostics and diagnostics.erp %}
Conformément aux dispositions des articles L. 125-5 et R. 125-23 à R. 125-27 du Code de l'environnement, un État des Risques et Pollutions (ERP) a été établi.

{% if diagnostics.erp.date %}
**Date d'établissement** : <<<VAR_START>>>{{ diagnostics.erp.date }}<<<VAR_END>>>
{% else %}
**Date d'établissement** : [Date à compléter]
{% endif %}

{% if diagnostics.erp.zone_sismicite %}
**Zone de sismicité** : <<<VAR_START>>>{{ diagnostics.erp.zone_sismicite }}<<<VAR_END>>>
{% else %}
**Zone de sismicité** : [Zone à préciser selon le zonage réglementaire (1 à 5)]
{% endif %}

{% if diagnostics.erp.radon %}
**Potentiel radon** : <<<VAR_START>>>{{ diagnostics.erp.radon }}<<<VAR_END>>>
{% else %}
**Potentiel radon** : [Catégorie à préciser (1, 2 ou 3)]
{% endif %}

{% if diagnostics.erp.ppr %}
**Plan de Prévention des Risques (PPR) applicable** : <<<VAR_START>>>{{ diagnostics.erp.ppr }}<<<VAR_END>>>
{% else %}
Le bien {% if diagnostics.erp.ppr_applicable %}est{% else %}n'est pas{% endif %} situé dans le périmètre d'un Plan de Prévention des Risques.
{% endif %}

{% if diagnostics.erp.reference %}
**Référence du document** : <<<VAR_START>>>{{ diagnostics.erp.reference }}<<<VAR_END>>>
{% endif %}

{% if diagnostics.erp.validite %}
Cet état est valable jusqu'au <<<VAR_START>>>{{ diagnostics.erp.validite }}<<<VAR_END>>> (durée de validité de six mois).
{% endif %}

{% if diagnostics.erp.remarques %}
**Remarques** : <<<VAR_START>>>{{ diagnostics.erp.remarques }}<<<VAR_END>>>
{% endif %}

{% else %}
Conformément aux dispositions des articles L. 125-5 et R. 125-23 à R. 125-27 du Code de l'environnement, un État des Risques et Pollutions (ERP) sera établi et annexé au présent acte.

**Date d'établissement** : [Date à compléter]

**Zone de sismicité** : [Zone à préciser selon le zonage réglementaire (1 à 5)]

**Potentiel radon** : [Catégorie à préciser (1, 2 ou 3)]

Le bien [est / n'est pas] situé dans le périmètre d'un Plan de Prévention des Risques (PPR).
{% endif %}

### Situation environnementale

{% if diagnostics and diagnostics.environnement %}

#### Inventaire BASIAS (Base des Anciens Sites Industriels et Activités de Service)

{% if diagnostics.environnement.basias %}
{% if diagnostics.environnement.basias.present %}
Le terrain d'assiette du bien figure dans l'inventaire BASIAS des anciens sites industriels et activités de service.

{% if diagnostics.environnement.basias.reference %}
**Référence BASIAS** : <<<VAR_START>>>{{ diagnostics.environnement.basias.reference }}<<<VAR_END>>>
{% endif %}

{% if diagnostics.environnement.basias.activite %}
**Activité recensée** : <<<VAR_START>>>{{ diagnostics.environnement.basias.activite }}<<<VAR_END>>>
{% endif %}

{% if diagnostics.environnement.basias.periode %}
**Période d'activité** : <<<VAR_START>>>{{ diagnostics.environnement.basias.periode }}<<<VAR_END>>>
{% endif %}

{% if diagnostics.environnement.basias.commentaire %}
<<<VAR_START>>>{{ diagnostics.environnement.basias.commentaire }}<<<VAR_END>>>
{% endif %}

{% else %}
Le terrain d'assiette du bien ne figure pas dans l'inventaire BASIAS.
{% endif %}
{% else %}
Aucune information relative à l'inscription du terrain dans l'inventaire BASIAS n'a été fournie.
{% endif %}

#### Inventaire BASOL (Base de données des Sites et Sols Pollués)

{% if diagnostics.environnement.basol %}
{% if diagnostics.environnement.basol.present %}
Le terrain d'assiette du bien figure dans l'inventaire BASOL des sites et sols pollués appelant une action des pouvoirs publics.

{% if diagnostics.environnement.basol.reference %}
**Référence BASOL** : <<<VAR_START>>>{{ diagnostics.environnement.basol.reference }}<<<VAR_END>>>
{% endif %}

{% if diagnostics.environnement.basol.origine %}
**Origine de la pollution** : <<<VAR_START>>>{{ diagnostics.environnement.basol.origine }}<<<VAR_END>>>
{% endif %}

{% if diagnostics.environnement.basol.statut %}
**Statut du site** : <<<VAR_START>>>{{ diagnostics.environnement.basol.statut }}<<<VAR_END>>>
{% endif %}

{% if diagnostics.environnement.basol.mesures %}
**Mesures prises ou à prendre** : <<<VAR_START>>>{{ diagnostics.environnement.basol.mesures }}<<<VAR_END>>>
{% endif %}

{% else %}
Le terrain d'assiette du bien ne figure pas dans l'inventaire BASOL.
{% endif %}
{% else %}
Aucune information relative à l'inscription du terrain dans l'inventaire BASOL n'a été fournie.
{% endif %}

#### Secteur d'Information sur les Sols (SIS)

{% if diagnostics.environnement.sis %}
{% if diagnostics.environnement.sis.present %}
Le bien est situé dans un Secteur d'Information sur les Sols (SIS) au sens de l'article L. 125-6 du Code de l'environnement.

{% if diagnostics.environnement.sis.reference %}
**Référence SIS** : <<<VAR_START>>>{{ diagnostics.environnement.sis.reference }}<<<VAR_END>>>
{% endif %}

{% if diagnostics.environnement.sis.description %}
**Description** : <<<VAR_START>>>{{ diagnostics.environnement.sis.description }}<<<VAR_END>>>
{% endif %}

{% if diagnostics.environnement.sis.usage_restrictions %}
**Restrictions d'usage** : <<<VAR_START>>>{{ diagnostics.environnement.sis.usage_restrictions }}<<<VAR_END>>>
{% endif %}

Conformément à la réglementation en vigueur, l'ACQUEREUR a été informé de cette inscription et de ses conséquences éventuelles sur l'usage du bien.

{% else %}
Le bien n'est pas situé dans un Secteur d'Information sur les Sols (SIS).
{% endif %}
{% else %}
Aucune information relative à l'inscription du terrain dans un Secteur d'Information sur les Sols n'a été fournie.
{% endif %}

{% if diagnostics.environnement.remarques %}
**Remarques complémentaires** : <<<VAR_START>>>{{ diagnostics.environnement.remarques }}<<<VAR_END>>>
{% endif %}

{% else %}
#### Inventaire BASIAS (Base des Anciens Sites Industriels et Activités de Service)

Le terrain d'assiette du bien [figure / ne figure pas] dans l'inventaire BASIAS des anciens sites industriels et activités de service.

#### Inventaire BASOL (Base de données des Sites et Sols Pollués)

Le terrain d'assiette du bien [figure / ne figure pas] dans l'inventaire BASOL des sites et sols pollués.

#### Secteur d'Information sur les Sols (SIS)

Le bien [est / n'est pas] situé dans un Secteur d'Information sur les Sols (SIS) au sens de l'article L. 125-6 du Code de l'environnement.
{% endif %}

### Absence de sinistres avec indemnisation

{% if diagnostics and diagnostics.sinistres %}

#### Déclaration au titre des catastrophes naturelles (Cat-Nat)

{% if diagnostics.sinistres.cat_nat %}
{% if diagnostics.sinistres.cat_nat.declare %}
Le VENDEUR déclare que le bien a fait l'objet d'un ou plusieurs sinistres ayant donné lieu à indemnisation au titre des catastrophes naturelles ou technologiques en application des articles L. 125-5 ou L. 128-2 du Code des assurances.

{% if diagnostics.sinistres.cat_nat.liste and diagnostics.sinistres.cat_nat.liste|length > 0 %}
**Liste des sinistres indemnisés** :

{% for sinistre in diagnostics.sinistres.cat_nat.liste %}
- **Date du sinistre** : <<<VAR_START>>>{{ sinistre.date }}<<<VAR_END>>>
{% if sinistre.type %}
  - Type : <<<VAR_START>>>{{ sinistre.type }}<<<VAR_END>>>
{% endif %}
{% if sinistre.description %}
  - Description : <<<VAR_START>>>{{ sinistre.description }}<<<VAR_END>>>
{% endif %}
{% if sinistre.montant_indemnise %}
  - Montant indemnisé : <<<VAR_START>>>{{ sinistre.montant_indemnise | format_nombre }}<<<VAR_END>>> EUR
{% endif %}
{% if sinistre.arrete_reference %}
  - Arrêté de reconnaissance : <<<VAR_START>>>{{ sinistre.arrete_reference }}<<<VAR_END>>>
{% endif %}
{% endfor %}
{% endif %}

{% else %}
Le VENDEUR déclare qu'à sa connaissance, le bien n'a fait l'objet d'aucun sinistre ayant donné lieu à indemnisation au titre des catastrophes naturelles ou technologiques en application des articles L. 125-5 ou L. 128-2 du Code des assurances.
{% endif %}
{% else %}
Le VENDEUR déclare qu'à sa connaissance, le bien n'a fait l'objet d'aucun sinistre ayant donné lieu à indemnisation au titre des catastrophes naturelles ou technologiques en application des articles L. 125-5 ou L. 128-2 du Code des assurances.
{% endif %}

#### Arrêtés de catastrophe naturelle

{% if diagnostics.sinistres.arretes %}
{% if diagnostics.sinistres.arretes.liste and diagnostics.sinistres.arretes.liste|length > 0 %}
La commune sur laquelle est situé le bien a fait l'objet des arrêtés de catastrophe naturelle suivants :

{% for arrete in diagnostics.sinistres.arretes.liste %}
- **Arrêté du <<<VAR_START>>>{{ arrete.date }}<<<VAR_END>>>**
{% if arrete.reference %}
  - Référence : <<<VAR_START>>>{{ arrete.reference }}<<<VAR_END>>>
{% endif %}
{% if arrete.type_catastrophe %}
  - Type de catastrophe : <<<VAR_START>>>{{ arrete.type_catastrophe }}<<<VAR_END>>>
{% endif %}
{% if arrete.periode_sinistre %}
  - Période concernée : <<<VAR_START>>>{{ arrete.periode_sinistre }}<<<VAR_END>>>
{% endif %}
{% if arrete.jo_publication %}
  - Publication au JO : <<<VAR_START>>>{{ arrete.jo_publication }}<<<VAR_END>>>
{% endif %}
{% endfor %}

{% else %}
Aucun arrêté de catastrophe naturelle concernant la commune n'a été porté à la connaissance des parties.
{% endif %}
{% else %}
Aucune information relative aux arrêtés de catastrophe naturelle concernant la commune n'a été fournie.
{% endif %}

{% if diagnostics.sinistres.remarques %}
**Remarques complémentaires** : <<<VAR_START>>>{{ diagnostics.sinistres.remarques }}<<<VAR_END>>>
{% endif %}

{% else %}
#### Déclaration au titre des catastrophes naturelles (Cat-Nat)

Le VENDEUR déclare qu'à sa connaissance, le bien n'a fait l'objet d'aucun sinistre ayant donné lieu à indemnisation au titre des catastrophes naturelles ou technologiques en application des articles L. 125-5 ou L. 128-2 du Code des assurances.

#### Arrêtés de catastrophe naturelle

[Information à compléter concernant les arrêtés de catastrophe naturelle publiés pour la commune]
{% endif %}

L'ACQUEREUR reconnaît avoir été parfaitement informé de l'ensemble des risques environnementaux et des sinistres éventuellement survenus sur le bien.
