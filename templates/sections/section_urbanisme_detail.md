## Urbanisme et réglementations

{% if urbanisme %}

### Plan Local d'Urbanisme (PLU)

{% if urbanisme.plu %}
Le bien est soumis aux dispositions du Plan Local d'Urbanisme (PLU) de la commune de <<<VAR_START>>>{{ bien.adresse.commune }}<<<VAR_END>>>.

{% if urbanisme.plu.zonage %}
**Zonage** : <<<VAR_START>>>{{ urbanisme.plu.zonage }}<<<VAR_END>>>
{% endif %}

{% if urbanisme.plu.coefficient_occupation_sols %}
**Coefficient d'occupation des sols (COS)** : <<<VAR_START>>>{{ urbanisme.plu.coefficient_occupation_sols }}<<<VAR_END>>>
{% endif %}

{% if urbanisme.plu.hauteur_maximale %}
**Hauteur maximale autorisée** : <<<VAR_START>>>{{ urbanisme.plu.hauteur_maximale }}<<<VAR_END>>> mètres
{% endif %}

{% if urbanisme.plu.emprise_sol %}
**Emprise au sol maximale** : <<<VAR_START>>>{{ urbanisme.plu.emprise_sol }}<<<VAR_END>>> %
{% endif %}

{% if urbanisme.plu.prospects %}
**Règles de prospect** : {{ urbanisme.plu.prospects }}
{% endif %}

{% if urbanisme.plu.destination %}
**Destination autorisée** : {{ urbanisme.plu.destination }}
{% endif %}

{% if urbanisme.plu.restrictions %}
**Restrictions particulières** :
{% for restriction in urbanisme.plu.restrictions %}
- {{ restriction }}
{% endfor %}
{% endif %}

{% if urbanisme.plu.date_approbation %}
Le PLU a été approuvé le <<<VAR_START>>>{{ urbanisme.plu.date_approbation }}<<<VAR_END>>>{% if urbanisme.plu.date_revision %} et révisé le <<<VAR_START>>>{{ urbanisme.plu.date_revision }}<<<VAR_END>>>{% endif %}.
{% endif %}

{% else %}
Le bien est soumis aux règles d'urbanisme applicables sur le territoire de la commune de <<<VAR_START>>>{{ bien.adresse.commune }}<<<VAR_END>>>.
{% endif %}

### Servitudes d'utilité publique

{% if urbanisme.servitudes_utilite_publique and urbanisme.servitudes_utilite_publique|length > 0 %}
Le bien est affecté par les servitudes d'utilité publique suivantes :

{% for servitude in urbanisme.servitudes_utilite_publique %}
{% if servitude.type %}
**{{ servitude.type | capitalize }}**
{% if servitude.reference %}
- Référence : <<<VAR_START>>>{{ servitude.reference }}<<<VAR_END>>>
{% endif %}
{% if servitude.description %}
- Description : {{ servitude.description }}
{% endif %}
{% if servitude.date_institution %}
- Date d'institution : <<<VAR_START>>>{{ servitude.date_institution }}<<<VAR_END>>>
{% endif %}
{% if servitude.autorite_competente %}
- Autorité compétente : <<<VAR_START>>>{{ servitude.autorite_competente }}<<<VAR_END>>>
{% endif %}
{% if servitude.impact %}
- Impact sur le bien : {{ servitude.impact }}
{% endif %}
{% endif %}

{% endfor %}
{% else %}
À la connaissance du VENDEUR, le bien n'est affecté par aucune servitude d'utilité publique.
{% endif %}

{% if urbanisme.servitudes_utilite_publique_remarques %}

{{ urbanisme.servitudes_utilite_publique_remarques }}
{% endif %}

### Risques naturels et technologiques

{% if urbanisme.risques %}

{% if urbanisme.risques.ppr %}
#### Plans de Prévention des Risques (PPR)

{% if urbanisme.risques.ppr.inondation %}
**Plan de Prévention des Risques d'Inondation (PPRI)**
{% if urbanisme.risques.ppr.inondation.zone %}
- Zone : <<<VAR_START>>>{{ urbanisme.risques.ppr.inondation.zone }}<<<VAR_END>>>
{% endif %}
{% if urbanisme.risques.ppr.inondation.prescriptions %}
- Prescriptions : {{ urbanisme.risques.ppr.inondation.prescriptions }}
{% endif %}
{% if urbanisme.risques.ppr.inondation.date_approbation %}
- Approuvé le : <<<VAR_START>>>{{ urbanisme.risques.ppr.inondation.date_approbation }}<<<VAR_END>>>
{% endif %}
{% endif %}

{% if urbanisme.risques.ppr.mouvement_terrain %}
**Plan de Prévention des Risques de Mouvements de Terrain**
{% if urbanisme.risques.ppr.mouvement_terrain.zone %}
- Zone : <<<VAR_START>>>{{ urbanisme.risques.ppr.mouvement_terrain.zone }}<<<VAR_END>>>
{% endif %}
{% if urbanisme.risques.ppr.mouvement_terrain.prescriptions %}
- Prescriptions : {{ urbanisme.risques.ppr.mouvement_terrain.prescriptions }}
{% endif %}
{% endif %}

{% if urbanisme.risques.ppr.technologique %}
**Plan de Prévention des Risques Technologiques (PPRT)**
{% if urbanisme.risques.ppr.technologique.zone %}
- Zone : <<<VAR_START>>>{{ urbanisme.risques.ppr.technologique.zone }}<<<VAR_END>>>
{% endif %}
{% if urbanisme.risques.ppr.technologique.installation_concernee %}
- Installation concernée : <<<VAR_START>>>{{ urbanisme.risques.ppr.technologique.installation_concernee }}<<<VAR_END>>>
{% endif %}
{% if urbanisme.risques.ppr.technologique.prescriptions %}
- Prescriptions : {{ urbanisme.risques.ppr.technologique.prescriptions }}
{% endif %}
{% endif %}

{% if urbanisme.risques.ppr.autres and urbanisme.risques.ppr.autres|length > 0 %}
**Autres PPR applicables**
{% for autre_ppr in urbanisme.risques.ppr.autres %}
- {{ autre_ppr.type }} : {{ autre_ppr.description }}
{% endfor %}
{% endif %}

{% else %}
Le bien n'est concerné par aucun Plan de Prévention des Risques.
{% endif %}

{% else %}
À la connaissance du VENDEUR, le bien n'est soumis à aucun risque naturel ou technologique particulier.
{% endif %}

### Droit de préemption urbain

{% if urbanisme.preemption %}
{% if urbanisme.preemption.applicable %}
Le bien est situé dans un périmètre soumis au droit de préemption urbain en application de l'article L. 211-1 du Code de l'urbanisme.

{% if urbanisme.preemption.titulaire %}
**Titulaire du droit de préemption** : <<<VAR_START>>>{{ urbanisme.preemption.titulaire }}<<<VAR_END>>>
{% endif %}

{% if urbanisme.preemption.zone %}
**Zone de préemption** : <<<VAR_START>>>{{ urbanisme.preemption.zone }}<<<VAR_END>>>
{% endif %}

{% if urbanisme.preemption.notification %}
La présente mutation sera notifiée à <<<VAR_START>>>{{ urbanisme.preemption.autorite_notifiee | default("la commune") }}<<<VAR_END>>> conformément aux dispositions des articles L. 213-2 et R. 213-6 du Code de l'urbanisme.

{% if urbanisme.preemption.notification.date %}
La notification a été effectuée le <<<VAR_START>>>{{ urbanisme.preemption.notification.date }}<<<VAR_END>>>.
{% endif %}

{% if urbanisme.preemption.notification.reference %}
Référence de notification : <<<VAR_START>>>{{ urbanisme.preemption.notification.reference }}<<<VAR_END>>>
{% endif %}
{% endif %}

{% if urbanisme.preemption.delai %}
Délai d'exercice : <<<VAR_START>>>{{ urbanisme.preemption.delai }}<<<VAR_END>>> mois à compter de la notification
{% endif %}

{% if urbanisme.preemption.renonciation %}
Par courrier en date du <<<VAR_START>>>{{ urbanisme.preemption.renonciation.date }}<<<VAR_END>>>, <<<VAR_START>>>{{ urbanisme.preemption.renonciation.autorite }}<<<VAR_END>>> a renoncé à l'exercice de son droit de préemption.
{% endif %}

{% else %}
Le bien n'est pas situé dans un périmètre soumis au droit de préemption urbain.
{% endif %}

{% if urbanisme.preemption.autres_preemptions and urbanisme.preemption.autres_preemptions|length > 0 %}

#### Autres droits de préemption

{% for preemption in urbanisme.preemption.autres_preemptions %}
**{{ preemption.type | capitalize }}**
{% if preemption.fondement %}
- Fondement : {{ preemption.fondement }}
{% endif %}
{% if preemption.titulaire %}
- Titulaire : <<<VAR_START>>>{{ preemption.titulaire }}<<<VAR_END>>>
{% endif %}
{% if preemption.statut %}
- Statut : {{ preemption.statut }}
{% endif %}
{% endfor %}
{% endif %}

{% else %}
Le bien n'est pas situé dans un périmètre soumis au droit de préemption urbain.
{% endif %}

{% if urbanisme.remarques %}

### Remarques particulières

{{ urbanisme.remarques }}
{% endif %}

{% else %}
Le bien est soumis aux règles d'urbanisme de droit commun applicables sur le territoire de la commune de <<<VAR_START>>>{{ bien.adresse.commune }}<<<VAR_END>>>.

L'acquéreur déclare avoir été informé de l'obligation de se renseigner auprès des services d'urbanisme de la commune pour toute modification ou construction sur le bien.
{% endif %}
