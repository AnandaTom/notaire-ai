## Performance énergétique

{% if diagnostics and diagnostics.dpe %}

### Diagnostic de Performance Énergétique (DPE)

{% if diagnostics.dpe.date_diagnostic %}
Diagnostic réalisé le <<<VAR_START>>>{{ diagnostics.dpe.date_diagnostic }}<<<VAR_END>>>{% if diagnostics.dpe.diagnostiqueur %} par <<<VAR_START>>>{{ diagnostics.dpe.diagnostiqueur }}<<<VAR_END>>>{% if diagnostics.dpe.numero_certification %}, certifié sous le numéro <<<VAR_START>>>{{ diagnostics.dpe.numero_certification }}<<<VAR_END>>>{% endif %}{% endif %}{% if diagnostics.dpe.numero_reference %}, sous la référence <<<VAR_START>>>{{ diagnostics.dpe.numero_reference }}<<<VAR_END>>>{% endif %}.
{% endif %}

{% if diagnostics.dpe.validite %}
**Validité du diagnostic** : jusqu'au <<<VAR_START>>>{{ diagnostics.dpe.validite }}<<<VAR_END>>>
{% endif %}

{% if diagnostics.dpe.classe_energie %}
### Classe énergétique

Le bien est classé **<<<VAR_START>>>{{ diagnostics.dpe.classe_energie }}<<<VAR_END>>>** sur l'échelle de performance énergétique (A = très performant, G = peu performant).

{% if diagnostics.dpe.consommation_annuelle %}
**Consommation énergétique annuelle** : <<<VAR_START>>>{{ diagnostics.dpe.consommation_annuelle }}<<<VAR_END>>> kWh/m²/an

{% if diagnostics.dpe.detail_consommation %}
Détail de la consommation :
{{ diagnostics.dpe.detail_consommation }}
{% endif %}
{% endif %}

{% endif %}

{% if diagnostics.dpe.classe_ges %}
### Émissions de gaz à effet de serre

Le bien est classé **<<<VAR_START>>>{{ diagnostics.dpe.classe_ges }}<<<VAR_END>>>** pour les émissions de gaz à effet de serre.

{% if diagnostics.dpe.emission_ges %}
**Émissions annuelles** : <<<VAR_START>>>{{ diagnostics.dpe.emission_ges }}<<<VAR_END>>> kg éqCO2/m²/an
{% endif %}

{% endif %}

{% if diagnostics.dpe.estimation_couts %}
### Estimation des coûts énergétiques

Les coûts annuels d'énergie du bien sont estimés entre <<<VAR_START>>>{{ diagnostics.dpe.estimation_couts.min | format_nombre }}<<<VAR_END>>> EUR et <<<VAR_START>>>{{ diagnostics.dpe.estimation_couts.max | format_nombre }}<<<VAR_END>>> EUR par an.

{% if diagnostics.dpe.estimation_couts.base_calcul %}
Cette estimation est établie sur la base des prix moyens des énergies indexés au <<<VAR_START>>>{{ diagnostics.dpe.estimation_couts.date_indexation }}<<<VAR_END>>>, selon la méthode de calcul <<<VAR_START>>>{{ diagnostics.dpe.estimation_couts.base_calcul }}<<<VAR_END>>>.
{% endif %}

{% if diagnostics.dpe.estimation_couts.avertissement %}
{{ diagnostics.dpe.estimation_couts.avertissement }}
{% else %}
Cette estimation ne constitue pas une valeur contractuelle mais un indicateur permettant d'évaluer la consommation d'énergie du bien.
{% endif %}

{% endif %}

{% if diagnostics.dpe.passoire_energetique %}
### AVERTISSEMENT - Passoire énergétique

Le bien est classé **{{ diagnostics.dpe.classe_energie }}** et constitue une "**passoire énergétique**" au sens de la législation en vigueur.

{% if diagnostics.dpe.obligations_location %}
**Obligations pour la location** :

{{ diagnostics.dpe.obligations_location }}
{% else %}
Conformément à la loi Climat et Résilience du 22 août 2021 :

- Les biens classés **G** ne peuvent plus être mis en location depuis le 1er janvier 2025
- Les biens classés **F** ne pourront plus être mis en location à compter du 1er janvier 2028
- Les biens classés **E** ne pourront plus être mis en location à compter du 1er janvier 2034

Ces interdictions s'appliquent sauf en cas de réalisation de travaux permettant d'atteindre au minimum la classe E.
{% endif %}

{% if diagnostics.dpe.interdiction_augmentation_loyer %}
**Interdiction d'augmentation du loyer** : Pour les biens classés F ou G, l'augmentation du loyer est interdite lors du renouvellement du bail ou de la relocation, sauf en cas de réalisation de travaux de rénovation énergétique permettant d'atteindre la classe E minimum.
{% endif %}

{% if diagnostics.dpe.gel_loyers_depuis %}
Le gel des loyers s'applique depuis le <<<VAR_START>>>{{ diagnostics.dpe.gel_loyers_depuis }}<<<VAR_END>>>.
{% endif %}

{% if diagnostics.dpe.audit_energetique_requis %}
**Audit énergétique obligatoire** : En raison du classement {{ diagnostics.dpe.classe_energie }}, un audit énergétique complet doit être annexé à la vente{% if diagnostics.dpe.audit_energetique.date %}. Cet audit a été réalisé le <<<VAR_START>>>{{ diagnostics.dpe.audit_energetique.date }}<<<VAR_END>>>{% if diagnostics.dpe.audit_energetique.auditeur %} par <<<VAR_START>>>{{ diagnostics.dpe.audit_energetique.auditeur }}<<<VAR_END>>>{% endif %}{% endif %}.
{% endif %}

{% endif %}

{% if diagnostics.dpe.recommandations %}
### Recommandations de travaux d'amélioration énergétique

{% if diagnostics.dpe.recommandations_detaillees and diagnostics.dpe.recommandations_detaillees|length > 0 %}
Les travaux suivants sont recommandés pour améliorer la performance énergétique du bien :

{% for recommandation in diagnostics.dpe.recommandations_detaillees %}
**{{ loop.index }}. {{ recommandation.travaux }}**

{% if recommandation.description %}
{{ recommandation.description }}
{% endif %}

{% if recommandation.gain_energetique %}
- **Gain énergétique estimé** : {{ recommandation.gain_energetique }}
{% endif %}

{% if recommandation.cout_estime %}
- **Coût estimé** : <<<VAR_START>>>{{ recommandation.cout_estime | format_nombre }}<<<VAR_END>>> EUR{% if recommandation.cout_precision %} ({{ recommandation.cout_precision }}){% endif %}
{% endif %}

{% if recommandation.priorite %}
- **Priorité** : {{ recommandation.priorite }}
{% endif %}

{% if recommandation.aides_disponibles %}
- **Aides financières disponibles** : {{ recommandation.aides_disponibles }}
{% endif %}

{% endfor %}

{% else %}
{{ diagnostics.dpe.recommandations }}
{% endif %}

{% if diagnostics.dpe.scenario_renovation %}
**Scénario de rénovation globale** : {{ diagnostics.dpe.scenario_renovation }}
{% endif %}

{% endif %}

{% if diagnostics.dpe.caracteristiques_thermiques %}
### Caractéristiques thermiques du bien

{% if diagnostics.dpe.caracteristiques_thermiques.isolation %}
**Isolation** :
{% if diagnostics.dpe.caracteristiques_thermiques.isolation.murs %}
- Murs : {{ diagnostics.dpe.caracteristiques_thermiques.isolation.murs }}
{% endif %}
{% if diagnostics.dpe.caracteristiques_thermiques.isolation.toiture %}
- Toiture : {{ diagnostics.dpe.caracteristiques_thermiques.isolation.toiture }}
{% endif %}
{% if diagnostics.dpe.caracteristiques_thermiques.isolation.fenetres %}
- Fenêtres : {{ diagnostics.dpe.caracteristiques_thermiques.isolation.fenetres }}
{% endif %}
{% if diagnostics.dpe.caracteristiques_thermiques.isolation.plancher %}
- Plancher : {{ diagnostics.dpe.caracteristiques_thermiques.isolation.plancher }}
{% endif %}
{% endif %}

{% if diagnostics.dpe.caracteristiques_thermiques.chauffage %}
**Système de chauffage** : {{ diagnostics.dpe.caracteristiques_thermiques.chauffage }}{% if diagnostics.dpe.caracteristiques_thermiques.chauffage_energie %} (énergie : {{ diagnostics.dpe.caracteristiques_thermiques.chauffage_energie }}){% endif %}
{% endif %}

{% if diagnostics.dpe.caracteristiques_thermiques.eau_chaude %}
**Production d'eau chaude sanitaire** : {{ diagnostics.dpe.caracteristiques_thermiques.eau_chaude }}{% if diagnostics.dpe.caracteristiques_thermiques.eau_chaude_energie %} (énergie : {{ diagnostics.dpe.caracteristiques_thermiques.eau_chaude_energie }}){% endif %}
{% endif %}

{% if diagnostics.dpe.caracteristiques_thermiques.ventilation %}
**Système de ventilation** : {{ diagnostics.dpe.caracteristiques_thermiques.ventilation }}
{% endif %}

{% if diagnostics.dpe.caracteristiques_thermiques.climatisation %}
**Climatisation** : {{ diagnostics.dpe.caracteristiques_thermiques.climatisation }}
{% endif %}

{% if diagnostics.dpe.caracteristiques_thermiques.energies_renouvelables %}
**Énergies renouvelables** : {{ diagnostics.dpe.caracteristiques_thermiques.energies_renouvelables }}
{% endif %}

{% endif %}

{% if diagnostics.dpe.confort_ete %}
### Confort d'été

{% if diagnostics.dpe.confort_ete.evaluation %}
**Évaluation** : {{ diagnostics.dpe.confort_ete.evaluation }}
{% endif %}

{% if diagnostics.dpe.confort_ete.temperature_estimee %}
**Température intérieure estimée en période de forte chaleur** : {{ diagnostics.dpe.confort_ete.temperature_estimee }}
{% endif %}

{% if diagnostics.dpe.confort_ete.recommandations %}
{{ diagnostics.dpe.confort_ete.recommandations }}
{% endif %}

{% endif %}

{% if diagnostics.dpe.informations_complementaires %}
### Informations complémentaires

{{ diagnostics.dpe.informations_complementaires }}
{% endif %}

{% if diagnostics.dpe.methode_calcul %}
**Méthode de calcul utilisée** : {{ diagnostics.dpe.methode_calcul }}
{% endif %}

{% if diagnostics.dpe.version_logiciel %}
**Logiciel utilisé** : {{ diagnostics.dpe.version_logiciel }}
{% endif %}

{% else %}
Le Diagnostic de Performance Énergétique (DPE) sera annexé au présent acte conformément aux dispositions de l'article L. 126-26 du Code de la construction et de l'habitation.
{% endif %}
