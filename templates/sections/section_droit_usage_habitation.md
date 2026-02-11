{# Section Droit d'Usage et d'Habitation — Viager #}
{# Activée si: bien.droit_usage_habitation.reserve == true #}

# RÉSERVE DU DROIT D'USAGE ET D'HABITATION

Le **PROMETTANT** (CRÉDIRENTIER) se réserve, sa vie durant, le droit d'usage et d'habitation du bien objet des présentes.

## Caractéristiques du droit réservé

Ce droit est :
- **Personnel** : il ne bénéficie qu'au crédirentier exclusivement.
- **Incessible** : il ne peut être cédé à quelque titre que ce soit.
- **Non transmissible** : il ne se transmet pas aux héritiers.
- Le bien devra être **bourgeoisement habité** et ne pourra être affecté à un usage commercial.
- Le crédirentier ne pourra **louer** tout ou partie du bien, à peine de nullité du droit réservé.
{% if bien.droit_usage_habitation.restrictions and bien.droit_usage_habitation.restrictions.hebergement_service_autorise %}
- Toutefois, le crédirentier pourra héberger une personne à son service pour des raisons de santé ou de sécurité.
{% endif %}

## Obligations du crédirentier

Le crédirentier supportera, pendant toute la durée de son droit :
- La **taxe d'habitation** et taxes assimilées.
- L'**assurance contre les risques locatifs** et la responsabilité civile.
- Les **réparations courantes et locatives** (article 606 du Code civil a contrario).
- L'**entretien courant** du bien et de ses équipements.

Le bien devra être restitué libre de toute occupation après le décès du crédirentier ou l'abandon volontaire du droit.

## Obligations du débirentier

Le **BÉNÉFICIAIRE** (DÉBIRENTIER), en sa qualité de nu-propriétaire, supportera :
- Les **grosses réparations** au sens de l'article 606 du Code civil (gros murs, voûtes, toiture, poutres, murs de soutènement, clôtures).
- Le **maintien du bien en état d'habitabilité**.
- La **préservation de l'état général** du bien.

## Fin du droit d'usage et d'habitation

Le droit d'usage et d'habitation prendra fin :
- Au **décès** du crédirentier, ou
- Par **abandon volontaire** du droit par le crédirentier.

{% if bien.droit_usage_habitation.abandon and bien.droit_usage_habitation.abandon.possible %}
### Abandon du droit

Le crédirentier pourra abandonner son droit d'usage et d'habitation de manière **irrévocable**, sous réserve :
- D'un préavis de **{{ bien.droit_usage_habitation.abandon.preavis_jours | default(60) }} jours**.
- D'une notification par **lettre recommandée avec accusé de réception** ou par **acte extrajudiciaire**.

L'abandon prendra effet à la date à laquelle le bien sera complètement libéré par le crédirentier.

**Processus de libération :**
1. Organisation de la remise des clés.
2. Transmission des contrats de fournitures (eau, électricité, gaz).
3. Relevé des consommations.
4. Communication de la nouvelle adresse postale.

{% if bien.droit_usage_habitation.abandon.declenche_rente %}
L'abandon du droit d'usage et d'habitation déclenchera le versement de la rente viagère conformément aux conditions définies ci-après.
{% endif %}
{% endif %}
