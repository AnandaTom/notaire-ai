## Diagnostics techniques

{% if diagnostics %}

Les diagnostics techniques suivants ont été réalisés conformément aux obligations légales en vigueur :

{% if diagnostics.dpe %}
### Diagnostic de Performance Énergétique (DPE)

{% if diagnostics.dpe.date_diagnostic %}
Diagnostic réalisé le <<<VAR_START>>>{{ diagnostics.dpe.date_diagnostic }}<<<VAR_END>>>{% if diagnostics.dpe.diagnostiqueur %} par <<<VAR_START>>>{{ diagnostics.dpe.diagnostiqueur }}<<<VAR_END>>>{% endif %}{% if diagnostics.dpe.numero_reference %}, sous la référence <<<VAR_START>>>{{ diagnostics.dpe.numero_reference }}<<<VAR_END>>>{% endif %}.
{% endif %}

{% if diagnostics.dpe.classe_energie %}
**Classe énergétique** : <<<VAR_START>>>{{ diagnostics.dpe.classe_energie }}<<<VAR_END>>>{% if diagnostics.dpe.consommation_annuelle %} (consommation énergétique annuelle : <<<VAR_START>>>{{ diagnostics.dpe.consommation_annuelle }}<<<VAR_END>>> kWh/m²/an){% endif %}
{% endif %}

{% if diagnostics.dpe.classe_ges %}
**Classe émissions de gaz à effet de serre** : <<<VAR_START>>>{{ diagnostics.dpe.classe_ges }}<<<VAR_END>>>{% if diagnostics.dpe.emission_ges %} (<<<VAR_START>>>{{ diagnostics.dpe.emission_ges }}<<<VAR_END>>> kg éqCO2/m²/an){% endif %}
{% endif %}

{% if diagnostics.dpe.estimation_couts %}
**Estimation des coûts annuels d'énergie** : entre <<<VAR_START>>>{{ diagnostics.dpe.estimation_couts.min | format_nombre }}<<<VAR_END>>> EUR et <<<VAR_START>>>{{ diagnostics.dpe.estimation_couts.max | format_nombre }}<<<VAR_END>>> EUR par an (prix moyens des énergies indexés au <<<VAR_START>>>{{ diagnostics.dpe.estimation_couts.date_indexation }}<<<VAR_END>>>).
{% endif %}

{% if diagnostics.dpe.recommandations %}
**Recommandations de travaux** :

{{ diagnostics.dpe.recommandations }}
{% endif %}

{% if diagnostics.dpe.passoire_energetique %}
**ATTENTION** : Le bien est classé {{ diagnostics.dpe.classe_energie }} et constitue une "passoire énergétique" au sens de la législation en vigueur.

{% if diagnostics.dpe.obligations_passoire %}
{{ diagnostics.dpe.obligations_passoire }}
{% else %}
Conformément à la loi Climat et Résilience, des obligations s'appliquent concernant la location et la vente de ce bien, notamment l'interdiction progressive de mise en location et l'obligation d'information renforcée des acquéreurs.
{% endif %}
{% endif %}

{% endif %}

{% if diagnostics.amiante %}
### Diagnostic Amiante

{% if diagnostics.amiante.date_diagnostic %}
Diagnostic réalisé le <<<VAR_START>>>{{ diagnostics.amiante.date_diagnostic }}<<<VAR_END>>>{% if diagnostics.amiante.diagnostiqueur %} par <<<VAR_START>>>{{ diagnostics.amiante.diagnostiqueur }}<<<VAR_END>>>{% endif %}{% if diagnostics.amiante.numero_reference %}, sous la référence <<<VAR_START>>>{{ diagnostics.amiante.numero_reference }}<<<VAR_END>>>{% endif %}.
{% endif %}

{% if diagnostics.amiante.presence == "oui" %}
**Résultat** : Présence d'amiante détectée

{% if diagnostics.amiante.zones_concernees and diagnostics.amiante.zones_concernees|length > 0 %}
**Zones concernées** :
{% for zone in diagnostics.amiante.zones_concernees %}
- {{ zone.localisation }}{% if zone.materiau %} ({{ zone.materiau }}){% endif %}{% if zone.etat %} - État : {{ zone.etat }}{% endif %}
{% endfor %}
{% endif %}

{% if diagnostics.amiante.recommandations %}
**Recommandations** : {{ diagnostics.amiante.recommandations }}
{% endif %}

{% elif diagnostics.amiante.presence == "non" %}
**Résultat** : Absence d'amiante
{% else %}
**Résultat** : {{ diagnostics.amiante.resultat }}
{% endif %}

{% endif %}

{% if diagnostics.plomb %}
### Constat de Risque d'Exposition au Plomb (CREP)

{% if diagnostics.plomb.date_diagnostic %}
Diagnostic réalisé le <<<VAR_START>>>{{ diagnostics.plomb.date_diagnostic }}<<<VAR_END>>>{% if diagnostics.plomb.diagnostiqueur %} par <<<VAR_START>>>{{ diagnostics.plomb.diagnostiqueur }}<<<VAR_END>>>{% endif %}{% if diagnostics.plomb.numero_reference %}, sous la référence <<<VAR_START>>>{{ diagnostics.plomb.numero_reference }}<<<VAR_END>>>{% endif %}.
{% endif %}

{% if diagnostics.plomb.presence == "oui" %}
**Résultat** : Présence de plomb détectée{% if diagnostics.plomb.surface_concernee %} sur <<<VAR_START>>>{{ diagnostics.plomb.surface_concernee }}<<<VAR_END>>> m²{% endif %}

{% if diagnostics.plomb.localisations and diagnostics.plomb.localisations|length > 0 %}
**Localisations** :
{% for localisation in diagnostics.plomb.localisations %}
- {{ localisation.zone }}{% if localisation.concentration %} (concentration : {{ localisation.concentration }}){% endif %}
{% endfor %}
{% endif %}

{% if diagnostics.plomb.recommandations %}
**Recommandations** : {{ diagnostics.plomb.recommandations }}
{% endif %}

{% elif diagnostics.plomb.presence == "non" %}
**Résultat** : Absence de plomb
{% else %}
**Résultat** : {{ diagnostics.plomb.resultat }}
{% endif %}

{% endif %}

{% if diagnostics.termites %}
### État relatif à la présence de termites

{% if diagnostics.termites.date_diagnostic %}
Diagnostic réalisé le <<<VAR_START>>>{{ diagnostics.termites.date_diagnostic }}<<<VAR_END>>>{% if diagnostics.termites.diagnostiqueur %} par <<<VAR_START>>>{{ diagnostics.termites.diagnostiqueur }}<<<VAR_END>>>{% endif %}{% if diagnostics.termites.numero_reference %}, sous la référence <<<VAR_START>>>{{ diagnostics.termites.numero_reference }}<<<VAR_END>>>{% endif %}.
{% endif %}

{% if diagnostics.termites.resultat == "presence" %}
**Résultat** : Présence de termites ou traces d'infestation

{% if diagnostics.termites.zones_infestees and diagnostics.termites.zones_infestees|length > 0 %}
**Zones infestées** :
{% for zone in diagnostics.termites.zones_infestees %}
- {{ zone.localisation }}{% if zone.description %} - {{ zone.description }}{% endif %}
{% endfor %}
{% endif %}

{% if diagnostics.termites.traitement_requis %}
**Traitement requis** : {{ diagnostics.termites.traitement_requis }}
{% endif %}

{% elif diagnostics.termites.resultat == "absence" %}
**Résultat** : Absence de termites
{% else %}
**Résultat** : {{ diagnostics.termites.resultat }}
{% endif %}

{% if diagnostics.termites.autres_parasites %}
**Autres parasites détectés** : {{ diagnostics.termites.autres_parasites }}
{% endif %}

{% endif %}

{% if diagnostics.gaz %}
### État de l'installation intérieure de gaz

{% if diagnostics.gaz.date_diagnostic %}
Diagnostic réalisé le <<<VAR_START>>>{{ diagnostics.gaz.date_diagnostic }}<<<VAR_END>>>{% if diagnostics.gaz.diagnostiqueur %} par <<<VAR_START>>>{{ diagnostics.gaz.diagnostiqueur }}<<<VAR_END>>>{% endif %}{% if diagnostics.gaz.numero_reference %}, sous la référence <<<VAR_START>>>{{ diagnostics.gaz.numero_reference }}<<<VAR_END>>>{% endif %}.
{% endif %}

{% if diagnostics.gaz.conformite == "conforme" %}
**Résultat** : Installation conforme
{% elif diagnostics.gaz.conformite == "non_conforme" %}
**Résultat** : Installation non conforme

{% if diagnostics.gaz.anomalies and diagnostics.gaz.anomalies|length > 0 %}
**Anomalies détectées** :
{% for anomalie in diagnostics.gaz.anomalies %}
- {{ anomalie.type }}{% if anomalie.localisation %} ({{ anomalie.localisation }}){% endif %}{% if anomalie.gravite %} - Gravité : {{ anomalie.gravite }}{% endif %}
{% endfor %}
{% endif %}

{% if diagnostics.gaz.travaux_requis %}
**Travaux requis** : {{ diagnostics.gaz.travaux_requis }}
{% endif %}

{% else %}
**Résultat** : {{ diagnostics.gaz.resultat }}
{% endif %}

{% endif %}

{% if diagnostics.electricite %}
### État de l'installation intérieure d'électricité

{% if diagnostics.electricite.date_diagnostic %}
Diagnostic réalisé le <<<VAR_START>>>{{ diagnostics.electricite.date_diagnostic }}<<<VAR_END>>>{% if diagnostics.electricite.diagnostiqueur %} par <<<VAR_START>>>{{ diagnostics.electricite.diagnostiqueur }}<<<VAR_END>>>{% endif %}{% if diagnostics.electricite.numero_reference %}, sous la référence <<<VAR_START>>>{{ diagnostics.electricite.numero_reference }}<<<VAR_END>>>{% endif %}.
{% endif %}

{% if diagnostics.electricite.conformite == "conforme" %}
**Résultat** : Installation conforme
{% elif diagnostics.electricite.conformite == "non_conforme" %}
**Résultat** : Installation non conforme

{% if diagnostics.electricite.anomalies and diagnostics.electricite.anomalies|length > 0 %}
**Anomalies détectées** :
{% for anomalie in diagnostics.electricite.anomalies %}
- {{ anomalie.type }}{% if anomalie.localisation %} ({{ anomalie.localisation }}){% endif %}{% if anomalie.gravite %} - Gravité : {{ anomalie.gravite }}{% endif %}
{% endfor %}
{% endif %}

{% if diagnostics.electricite.travaux_requis %}
**Travaux requis** : {{ diagnostics.electricite.travaux_requis }}
{% endif %}

{% else %}
**Résultat** : {{ diagnostics.electricite.resultat }}
{% endif %}

{% endif %}

{% if diagnostics.assainissement %}
### État de l'installation d'assainissement non collectif

{% if diagnostics.assainissement.date_diagnostic %}
Diagnostic réalisé le <<<VAR_START>>>{{ diagnostics.assainissement.date_diagnostic }}<<<VAR_END>>>{% if diagnostics.assainissement.diagnostiqueur %} par <<<VAR_START>>>{{ diagnostics.assainissement.diagnostiqueur }}<<<VAR_END>>>{% endif %}{% if diagnostics.assainissement.numero_reference %}, sous la référence <<<VAR_START>>>{{ diagnostics.assainissement.numero_reference }}<<<VAR_END>>>{% endif %}.
{% endif %}

{% if diagnostics.assainissement.conformite == "conforme" %}
**Résultat** : Installation conforme
{% elif diagnostics.assainissement.conformite == "non_conforme" %}
**Résultat** : Installation non conforme

{% if diagnostics.assainissement.defauts %}
**Défauts constatés** : {{ diagnostics.assainissement.defauts }}
{% endif %}

{% if diagnostics.assainissement.travaux_requis %}
**Travaux requis** : {{ diagnostics.assainissement.travaux_requis }}
{% endif %}

{% else %}
**Résultat** : {{ diagnostics.assainissement.resultat }}
{% endif %}

{% if diagnostics.assainissement.type_installation %}
**Type d'installation** : {{ diagnostics.assainissement.type_installation }}
{% endif %}

{% endif %}

{% if diagnostics.erp %}
### État des risques et pollutions (ERP)

{% if diagnostics.erp.date_diagnostic %}
État établi le <<<VAR_START>>>{{ diagnostics.erp.date_diagnostic }}<<<VAR_END>>>{% if diagnostics.erp.numero_reference %}, sous la référence <<<VAR_START>>>{{ diagnostics.erp.numero_reference }}<<<VAR_END>>>{% endif %}.
{% endif %}

{% if diagnostics.erp.zones_risques and diagnostics.erp.zones_risques|length > 0 %}
**Risques identifiés** :
{% for risque in diagnostics.erp.zones_risques %}
- {{ risque.type }}{% if risque.description %} : {{ risque.description }}{% endif %}
{% endfor %}
{% endif %}

{% if diagnostics.erp.sinistres_indemnises %}
**Sinistres indemnisés** : {{ diagnostics.erp.sinistres_indemnises }}
{% endif %}

{% endif %}

{% if diagnostics.mesurage_loi_carrez %}
### Mesurage Loi Carrez

{% if diagnostics.mesurage_loi_carrez.date_mesurage %}
Mesurage réalisé le <<<VAR_START>>>{{ diagnostics.mesurage_loi_carrez.date_mesurage }}<<<VAR_END>>>{% if diagnostics.mesurage_loi_carrez.mesureur %} par <<<VAR_START>>>{{ diagnostics.mesurage_loi_carrez.mesureur }}<<<VAR_END>>>{% endif %}{% if diagnostics.mesurage_loi_carrez.numero_reference %}, sous la référence <<<VAR_START>>>{{ diagnostics.mesurage_loi_carrez.numero_reference }}<<<VAR_END>>>{% endif %}.
{% endif %}

{% if diagnostics.mesurage_loi_carrez.surface_privative %}
**Surface privative** : <<<VAR_START>>>{{ diagnostics.mesurage_loi_carrez.surface_privative }}<<<VAR_END>>> m²
{% endif %}

{% if diagnostics.mesurage_loi_carrez.details %}
{{ diagnostics.mesurage_loi_carrez.details }}
{% endif %}

{% endif %}

{% if diagnostics.autres %}
### Autres diagnostics

{{ diagnostics.autres }}
{% endif %}

{% if diagnostics.validite_globale %}
**Validité des diagnostics** : {{ diagnostics.validite_globale }}
{% endif %}

{% if diagnostics.dossier_technique %}
L'ensemble des diagnostics techniques sont regroupés dans un dossier de diagnostic technique (DDT) remis à l'acquéreur{% if diagnostics.dossier_technique.date_remise %} le <<<VAR_START>>>{{ diagnostics.dossier_technique.date_remise }}<<<VAR_END>>>{% endif %}.
{% endif %}

{% else %}
Les diagnostics techniques obligatoires seront annexés au présent acte conformément à la réglementation en vigueur.
{% endif %}
