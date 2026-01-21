## Réglementations spécifiques à la copropriété

{% if copropriete %}

### Immatriculation du syndicat des copropriétaires

{% if copropriete.immatriculation %}
Le syndicat des copropriétaires de l'immeuble est immatriculé au registre national des copropriétés sous le numéro <<<VAR_START>>>{{ copropriete.immatriculation.numero }}<<<VAR_END>>>.
{% endif %}

### Carnet d'entretien

{% if copropriete.carnet_entretien %}
Le carnet d'entretien de l'immeuble a été communiqué à l'ACQUÉREUR conformément à l'article L 721-2 du Code de la construction et de l'habitation.
{% endif %}

### Diagnostic technique global (DTG)

{% if copropriete.dtg %}
Un diagnostic technique global a été réalisé le <<<VAR_START>>>{{ copropriete.dtg.date }}<<<VAR_END>>>.
{% if copropriete.dtg.resultat %}
Conclusion : {{ copropriete.dtg.resultat }}
{% endif %}
{% else %}
Le syndicat des copropriétaires n'a pas fait réaliser de diagnostic technique global.
{% endif %}

### Plan pluriannuel de travaux (PPT)

{% if copropriete.ppt %}
Un plan pluriannuel de travaux a été adopté par l'assemblée générale du <<<VAR_START>>>{{ copropriete.ppt.date_adoption }}<<<VAR_END>>>.
{% else %}
Aucun plan pluriannuel de travaux n'a été adopté à ce jour.
{% endif %}

### Fiche synthétique de la copropriété

{% if copropriete.fiche_synthetique %}
La fiche synthétique de la copropriété prévue à l'article L 711-2 du Code de la construction et de l'habitation a été remise à l'ACQUÉREUR.
{% endif %}

### Emprunt collectif

{% if copropriete.emprunt_collectif %}
Le syndicat des copropriétaires a souscrit un emprunt collectif :
- Montant : <<<VAR_START>>>{{ copropriete.emprunt_collectif.montant | format_nombre }}<<<VAR_END>>>
- Objet : {{ copropriete.emprunt_collectif.objet }}
- Part du lot : <<<VAR_START>>>{{ copropriete.emprunt_collectif.part_lot | format_nombre }}<<<VAR_END>>>
{% else %}
Le syndicat des copropriétaires n'a pas souscrit d'emprunt collectif.
{% endif %}

### Fonds de travaux

{% if copropriete.fonds_travaux %}
Le fonds de travaux prévu à l'article 14-2 de la loi du 10 juillet 1965 a été constitué.
- Montant actuel : <<<VAR_START>>>{{ copropriete.fonds_travaux.montant | format_nombre }}<<<VAR_END>>>
- Quote-part du lot : <<<VAR_START>>>{{ copropriete.fonds_travaux.quote_part | format_nombre }}<<<VAR_END>>>
{% endif %}

### Garantie de superficie (Loi Carrez)

{% if bien.superficie_carrez %}
La superficie de la partie privative du lot est de <<<VAR_START>>>{{ bien.superficie_carrez }}<<<VAR_END>>> mètres carrés, conformément aux dispositions de la loi n° 96-1107 du 18 décembre 1996 (loi Carrez).

Cette superficie a été mesurée par <<<VAR_START>>>{{ bien.metreur | default("le vendeur") }}<<<VAR_END>>>.

**ATTENTION** : En cas d'erreur de mesurage supérieure à 5%, l'ACQUÉREUR pourra demander une diminution proportionnelle du prix dans un délai d'un an à compter de la signature de l'acte authentique.
{% endif %}

### Statut de la copropriété

#### Règlement de copropriété

{% if copropriete.reglement %}
Le règlement de copropriété a été établi aux termes d'un acte reçu par Maître <<<VAR_START>>>{{ copropriete.reglement.notaire }}<<<VAR_END>>>, notaire, le <<<VAR_START>>>{{ copropriete.reglement.date }}<<<VAR_END>>>, et publié au service de la publicité foncière de <<<VAR_START>>>{{ copropriete.reglement.spf }}<<<VAR_END>>>.
{% endif %}

{% if copropriete.modificatifs and copropriete.modificatifs|length > 0 %}
Ce règlement a été modifié par les actes suivants :
{% for modif in copropriete.modificatifs %}
- Acte du {{ modif.date }} - {{ modif.objet }}
{% endfor %}
{% endif %}

#### Syndic

{% if copropriete.syndic %}
La copropriété est gérée par :
- **Syndic** : <<<VAR_START>>>{{ copropriete.syndic.nom }}<<<VAR_END>>>
- **Adresse** : {{ copropriete.syndic.adresse }}
{% if copropriete.syndic.mandat_fin %}
- **Fin de mandat** : {{ copropriete.syndic.mandat_fin }}
{% endif %}
{% endif %}

#### Charges de copropriété

{% if copropriete.charges %}
Les charges de copropriété pour le lot vendu s'élèvent à :
- **Charges courantes** : <<<VAR_START>>>{{ copropriete.charges.courantes | format_nombre }}<<<VAR_END>>> par an
{% if copropriete.charges.exceptionnelles %}
- **Charges exceptionnelles votées** : <<<VAR_START>>>{{ copropriete.charges.exceptionnelles | format_nombre }}<<<VAR_END>>>
{% endif %}
{% endif %}

#### Travaux votés non encore appelés

{% if copropriete.travaux_votes %}
Des travaux ont été votés mais non encore appelés :
{% for travail in copropriete.travaux_votes %}
- {{ travail.nature }} : <<<VAR_START>>>{{ travail.montant | format_nombre }}<<<VAR_END>>> (quote-part du lot)
{% endfor %}
{% else %}
Aucun travaux voté n'est en attente d'appel de fonds.
{% endif %}

#### Assemblées générales

{% if copropriete.ag %}
{% if copropriete.ag.derniere %}
La dernière assemblée générale s'est tenue le <<<VAR_START>>>{{ copropriete.ag.derniere.date }}<<<VAR_END>>>.
{% endif %}
{% if copropriete.ag.prochaine %}
La prochaine assemblée générale est prévue le <<<VAR_START>>>{{ copropriete.ag.prochaine.date }}<<<VAR_END>>>.
{% endif %}
{% endif %}

#### Procédures en cours

{% if copropriete.procedures %}
Le syndicat des copropriétaires est partie aux procédures suivantes :
{% for proc in copropriete.procedures %}
- {{ proc.nature }} - Tribunal de {{ proc.juridiction }}
{% endfor %}
{% else %}
Le VENDEUR déclare qu'à sa connaissance, le syndicat des copropriétaires n'est partie à aucune procédure judiciaire en cours.
{% endif %}

#### Notifications

L'ACQUÉREUR devra notifier au syndic l'acquisition des lots dans les conditions prévues par l'article 6 du décret du 17 mars 1967.

{% endif %}
