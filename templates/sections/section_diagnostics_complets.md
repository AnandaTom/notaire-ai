## Diagnostics techniques

{% if diagnostics %}

{% if diagnostics.dpe %}
### Diagnostic de performance énergétique (DPE)

Le diagnostic de performance énergétique a été réalisé le <<<VAR_START>>>{{ diagnostics.dpe.date }}<<<VAR_END>>>{% if diagnostics.dpe.diagnostiqueur %} par <<<VAR_START>>>{{ diagnostics.dpe.diagnostiqueur.nom }}<<<VAR_END>>>{% endif %}.

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

{% if diagnostics.merules %}
### Mérules

{% if diagnostics.merules.zone_delimitee %}
La commune est située dans une zone délimitée par arrêté préfectoral comme présentant un risque de mérule.
{% else %}
La commune n'est pas située dans une zone délimitée comme présentant un risque de mérule.
{% endif %}
{% endif %}

{% if diagnostics.electricite %}
### Installation intérieure d'électricité

{{ diagnostics.electricite.resultat }}

{% if diagnostics.electricite.anomalies %}
**Anomalies détectées** : {{ diagnostics.electricite.anomalies }}
{% endif %}
{% endif %}

{% if diagnostics.gaz and diagnostics.gaz.resultat %}
### Installation intérieure de gaz

{{ diagnostics.gaz.resultat }}

{% if diagnostics.gaz.anomalies %}
**Anomalies détectées** : {{ diagnostics.gaz.anomalies }}
{% endif %}
{% elif diagnostics.gaz and diagnostics.gaz.applicable is sameas false %}
Le bien n'est pas équipé d'une installation intérieure de gaz. Le diagnostic gaz n'est pas requis.
{% endif %}

{% if diagnostics.assainissement %}
### Assainissement non collectif

{{ diagnostics.assainissement.resultat }}
{% endif %}

{% if diagnostics.carnet_logement %}
### Carnet d'information du logement

Le carnet d'information du logement prévu aux articles L 126-35-2 à L 126-35-11 du Code de la construction et de l'habitation a été établi et est remis à l'ACQUÉREUR.
{% endif %}

{% if diagnostics.audit_energetique %}
### Audit énergétique

{% if diagnostics.dpe.classe_energie in ['F', 'G'] %}
Conformément à l'article L 126-28-1 du Code de la construction et de l'habitation, un audit énergétique a été réalisé le <<<VAR_START>>>{{ diagnostics.audit_energetique.date }}<<<VAR_END>>>.
{{ diagnostics.audit_energetique.resultat }}
{% endif %}
{% endif %}

{% if diagnostics.bruit %}
### Zone de bruit - Plan d'exposition au bruit

{% if diagnostics.bruit.zone %}
Le bien est situé dans la zone <<<VAR_START>>>{{ diagnostics.bruit.zone }}<<<VAR_END>>> du plan d'exposition au bruit de l'aérodrome de <<<VAR_START>>>{{ diagnostics.bruit.aerodrome }}<<<VAR_END>>>.
{% else %}
Le bien n'est pas situé dans une zone du plan d'exposition au bruit d'un aérodrome.
{% endif %}
{% endif %}

{% if diagnostics.radon %}
### Radon

La commune est classée en zone <<<VAR_START>>>{{ diagnostics.radon.zone }}<<<VAR_END>>> pour le potentiel radon (arrêté du 27 juin 2018).
{% if diagnostics.radon.zone == 3 %}
**ATTENTION** : La commune est en zone 3 (potentiel radon significatif). Des mesures de concentration en radon sont recommandées.
{% endif %}
{% endif %}

{% if diagnostics.dpe and diagnostics.amiante %}
### Tableau récapitulatif des diagnostics

| Diagnostic | Date | Diagnostiqueur | Validité | Résultat |
| :---- | :---- | :---- | :---- | :---- |
{% if diagnostics.dpe %}| DPE | {{ diagnostics.dpe.date }} | {{ diagnostics.dpe.diagnostiqueur.nom | default("-") }} | {{ diagnostics.dpe.validite | default("10 ans") }} | Classe {{ diagnostics.dpe.classe_energie | default("?") }} |
{% endif %}{% if diagnostics.amiante %}| Amiante | {{ diagnostics.amiante.date }} | {{ diagnostics.amiante.diagnostiqueur | default("-") }} | {{ diagnostics.amiante.validite | default("Illimitée si négatif") }} | {{ "Présence" if diagnostics.amiante.presence else "Négatif" }} |
{% endif %}{% if diagnostics.plomb %}| CREP (plomb) | {{ diagnostics.plomb.date }} | {{ diagnostics.plomb.diagnostiqueur | default("-") }} | {{ diagnostics.plomb.validite | default("Illimitée si négatif") }} | {{ "Présence" if diagnostics.plomb.presence else "Négatif" }} |
{% endif %}{% if diagnostics.termites %}| Termites | {{ diagnostics.termites.date }} | {{ diagnostics.termites.diagnostiqueur | default("-") }} | {{ diagnostics.termites.validite | default("6 mois") }} | {{ "Présence" if diagnostics.termites.presence else "Négatif" }} |
{% endif %}{% if diagnostics.electricite %}| Électricité | {{ diagnostics.electricite.date | default("-") }} | {{ diagnostics.electricite.diagnostiqueur | default("-") }} | {{ diagnostics.electricite.validite | default("3 ans") }} | {{ diagnostics.electricite.resultat | default("-") }} |
{% endif %}{% if diagnostics.gaz and diagnostics.gaz.resultat %}| Gaz | {{ diagnostics.gaz.date | default("-") }} | {{ diagnostics.gaz.diagnostiqueur | default("-") }} | {{ diagnostics.gaz.validite | default("3 ans") }} | {{ diagnostics.gaz.resultat | default("-") }} |
{% endif %}{% if diagnostics.assainissement %}| Assainissement | {{ diagnostics.assainissement.date | default("-") }} | {{ diagnostics.assainissement.diagnostiqueur | default("-") }} | {{ diagnostics.assainissement.validite | default("3 ans") }} | {{ diagnostics.assainissement.resultat | default("-") }} |
{% endif %}{% if diagnostics.bruit %}| Bruit | {{ diagnostics.bruit.date | default("-") }} | - | - | Zone {{ diagnostics.bruit.zone | default("-") }} |
{% endif %}{% if diagnostics.radon %}| Radon | - | - | - | Zone {{ diagnostics.radon.zone | default("-") }} |
{% endif %}

{% endif %}

{% else %}
Les diagnostics techniques obligatoires ont été réalisés et sont annexés au présent acte.
{% endif %}
