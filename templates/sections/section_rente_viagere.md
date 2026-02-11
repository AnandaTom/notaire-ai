{# Section Rente Viagère — Viager #}
{# Activée si: prix.rente_viagere existe #}

# RENTE VIAGÈRE

## Conventions relatives à la rente

{% if prix.rente_viagere %}
La rente viagère sera servie au crédirentier dans les conditions suivantes :

- **Montant mensuel** : {{ prix.rente_viagere.montant_mensuel | format_nombre }} EUR ({{ prix.rente_viagere.montant_mensuel_lettres | default(prix.rente_viagere.montant_mensuel | montant_en_lettres) }}).
- **Périodicité** : {{ prix.rente_viagere.periodicite | default("mensuelle") }}.
- **Jour de versement** : le {{ prix.rente_viagere.jour_versement | default(5) }} de chaque mois.
- **Mode de paiement** : par virement automatique sur le compte du crédirentier.
{% if prix.rente_viagere.date_debut %}
- **Date de début** : {{ prix.rente_viagere.date_debut | format_date }}.
{% endif %}

Le versement de la rente s'effectuera par virement permanent du compte du débirentier vers le compte du crédirentier. Chaque quittance de rente régulièrement touchée vaudra certificat de vie, sans autre justification.

## Indexation de la rente

{% if prix.rente_viagere.indexation %}
La rente sera révisée **{{ prix.rente_viagere.indexation.frequence | default("annuellement") }}**, à la date anniversaire du contrat, en fonction de l'indice **{{ prix.rente_viagere.indexation.indice | default("INSEE des prix à la consommation (IPC), base 2015, hors tabac") }}**.

**Formule de révision :**

Nouveau montant = (Indice nouveau / Indice ancien) × Montant ancien

**Cas particuliers :**
- En cas de disparition de l'indice de référence, il sera fait application du coefficient de raccordement publié par l'INSEE.
- En l'absence de nouvel indice, les parties conviendront d'un indice de remplacement. À défaut d'accord, le montant de la rente sera maintenu à son dernier niveau.
{% endif %}

## Rachat de la rente

{% if prix.rente_viagere.rachat and prix.rente_viagere.rachat.possible %}
Le débirentier aura la **faculté de racheter la rente** en versant un capital à un organisme d'assurance ou établissement financier agréé, aux conditions suivantes :
- Le capital versé devra générer une rente au moins **équivalente** à la rente due.
- L'indexation de la rente de substitution devra être **identique** à celle prévue au présent contrat.
- Le crédirentier donnera alors **mainlevée** du privilège inscrit.

**Conséquences du rachat :**
- Dégagement du privilège du vendeur.
- Arrêt des renouvellements d'inscription.
- Désistement de tous droits d'action résolutoire liés au défaut de paiement de la rente.
{% else %}
Le rachat de la rente n'est **pas autorisé** sans l'accord préalable et exprès du crédirentier.
{% endif %}
{% endif %}

## Aliénation par le débirentier

En cas de revente du bien par le débirentier :
- Le crédirentier devra être informé conformément à l'article 1690 du Code civil.
- Une copie de l'acte authentique de vente sera remise sans frais au crédirentier.
- Tous les acquéreurs successifs seront **garants solidaires** du service de la rente viagère.
- Le transfert du privilège sera possible sous condition que la valeur du nouveau bien soit au moins égale à celle du bien vendu.
