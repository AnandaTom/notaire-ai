## Diagnostics techniques

{% if diagnostics %}

{% if diagnostics.dpe %}
### Diagnostic de performance énergétique (DPE)

Le diagnostic de performance énergétique a été réalisé le <<<VAR_START>>>{{ diagnostics.dpe.date }}<<<VAR_END>>>{% if diagnostics.dpe.diagnostiqueur %} par <<<VAR_START>>>{{ diagnostics.dpe.diagnostiqueur }}<<<VAR_END>>>{% endif %}.

- **Classe énergétique** : <<<VAR_START>>>{{ diagnostics.dpe.classe_energie }}<<<VAR_END>>>
- **Classe GES** : <<<VAR_START>>>{{ diagnostics.dpe.classe_ges }}<<<VAR_END>>>
{% if diagnostics.dpe.consommation %}
- **Consommation énergétique annuelle** : <<<VAR_START>>>{{ diagnostics.dpe.consommation }}<<<VAR_END>>> kWh/m²/an
{% endif %}
{% if diagnostics.dpe.emissions_ges %}
- **Émissions de gaz à effet de serre** : <<<VAR_START>>>{{ diagnostics.dpe.emissions_ges }}<<<VAR_END>>> kg CO2/m²/an
{% endif %}

{% if diagnostics.dpe.classe_energie in ['F', 'G'] %}
**ATTENTION** : Le bien est classé en catégorie {{ diagnostics.dpe.classe_energie }}, considéré comme "passoire énergétique". Des obligations spécifiques s'appliquent concernant l'audit énergétique et les travaux de rénovation.
{% endif %}

{% if diagnostics.dpe.recommandations %}
**Recommandations** : {{ diagnostics.dpe.recommandations }}
{% endif %}
{% endif %}

{% if diagnostics.amiante %}
### Diagnostic amiante

{% if diagnostics.amiante.presence %}
Le diagnostic amiante révèle la présence de matériaux contenant de l'amiante :
{{ diagnostics.amiante.detail }}
{% else %}
Le diagnostic amiante réalisé le <<<VAR_START>>>{{ diagnostics.amiante.date }}<<<VAR_END>>> ne révèle pas la présence de matériaux contenant de l'amiante.
{% endif %}
{% endif %}

{% if diagnostics.plomb %}
### Constat de risque d'exposition au plomb (CREP)

{% if diagnostics.plomb.presence %}
Le constat révèle la présence de revêtements contenant du plomb :
{{ diagnostics.plomb.detail }}
{% else %}
Le constat de risque d'exposition au plomb réalisé le <<<VAR_START>>>{{ diagnostics.plomb.date }}<<<VAR_END>>> ne révèle pas la présence de revêtements contenant du plomb.
{% endif %}
{% endif %}

{% if diagnostics.termites %}
### État relatif à la présence de termites

{% if diagnostics.termites.presence %}
L'état relatif à la présence de termites révèle : <<<VAR_START>>>{{ diagnostics.termites.resultat }}<<<VAR_END>>>
{% else %}
L'état relatif à la présence de termites réalisé le <<<VAR_START>>>{{ diagnostics.termites.date }}<<<VAR_END>>> ne révèle pas la présence de termites.
{% endif %}
{% endif %}

{% if diagnostics.electricite %}
### Installation intérieure d'électricité

{{ diagnostics.electricite.resultat }}

{% if diagnostics.electricite.anomalies %}
**Anomalies détectées** : {{ diagnostics.electricite.anomalies }}
{% endif %}
{% endif %}

{% if diagnostics.gaz %}
### Installation intérieure de gaz

{{ diagnostics.gaz.resultat }}

{% if diagnostics.gaz.anomalies %}
**Anomalies détectées** : {{ diagnostics.gaz.anomalies }}
{% endif %}
{% endif %}

{% if diagnostics.assainissement %}
### Assainissement non collectif

{{ diagnostics.assainissement.resultat }}
{% endif %}

{% else %}
Les diagnostics techniques obligatoires ont été réalisés et sont annexés au présent acte.
{% endif %}
