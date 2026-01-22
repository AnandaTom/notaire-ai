## Assurance dommages-ouvrage

{% if dommages_ouvrage %}

{% if dommages_ouvrage.existe %}
### Police d'assurance dommages-ouvrage

Une assurance dommages-ouvrage a été souscrite conformément aux dispositions de l'article L. 242-1 du Code des assurances.

{% if dommages_ouvrage.assureur %}
- **Assureur** : <<<VAR_START>>>{{ dommages_ouvrage.assureur }}<<<VAR_END>>>
{% endif %}
{% if dommages_ouvrage.numero_police %}
- **Police n°** : <<<VAR_START>>>{{ dommages_ouvrage.numero_police }}<<<VAR_END>>>
{% endif %}
{% if dommages_ouvrage.date_souscription %}
- **Date de souscription** : <<<VAR_START>>>{{ dommages_ouvrage.date_souscription | format_date }}<<<VAR_END>>>
{% endif %}
{% if dommages_ouvrage.date_expiration %}
- **Date d'expiration** : <<<VAR_START>>>{{ dommages_ouvrage.date_expiration | format_date }}<<<VAR_END>>>
{% endif %}
{% if dommages_ouvrage.montant_garanti %}
- **Montant garanti** : <<<VAR_START>>>{{ dommages_ouvrage.montant_garanti | format_nombre }}<<<VAR_END>>> EUR
{% endif %}

{% if dommages_ouvrage.beneficiaire %}
Le bénéficiaire de cette assurance est : <<<VAR_START>>>{{ dommages_ouvrage.beneficiaire }}<<<VAR_END>>>.
{% endif %}

{% if dommages_ouvrage.transfert %}
### Transfert de l'assurance

L'assurance dommages-ouvrage sera transférée à l'ACQUEREUR conformément aux dispositions légales. L'ACQUEREUR bénéficiera de la garantie pour la durée restant à courir.

{% if dommages_ouvrage.transfert.modalites %}
Modalités de transfert : {{ dommages_ouvrage.transfert.modalites }}
{% endif %}
{% endif %}

{% if dommages_ouvrage.travaux_couverts %}
### Travaux couverts

Les travaux suivants sont couverts par l'assurance dommages-ouvrage :

{% for travail in dommages_ouvrage.travaux_couverts %}
- {{ travail.nature }}{% if travail.date %} (réalisés le <<<VAR_START>>>{{ travail.date | format_date }}<<<VAR_END>>>){% endif %}
{% endfor %}
{% endif %}

{% else %}
### Absence d'assurance dommages-ouvrage

Le VENDEUR déclare qu'aucune assurance dommages-ouvrage n'a été souscrite.

{% if dommages_ouvrage.motif_absence %}
Motif : {{ dommages_ouvrage.motif_absence }}
{% endif %}

{% if dommages_ouvrage.dispense %}
Le VENDEUR était dispensé de souscrire une assurance dommages-ouvrage en application de l'article L. 242-1 du Code des assurances (travaux réalisés par le propriétaire pour son propre compte).
{% endif %}

L'ACQUEREUR déclare avoir été informé de cette situation et en accepte les conséquences.
{% endif %}

{% else %}
Le VENDEUR déclare qu'aucune opération de construction soumise à l'obligation d'assurance dommages-ouvrage prévue par l'article L. 242-1 du Code des assurances n'a été réalisée.
{% endif %}

## Garantie décennale

{% if garanties %}

{% if garanties.decennale %}
### Couverture décennale

{% if garanties.decennale.applicable %}
Conformément aux dispositions des articles 1792 et suivants du Code civil, les travaux réalisés sont couverts par la garantie décennale.

{% if garanties.decennale.constructeur %}
- **Constructeur/Entrepreneur** : <<<VAR_START>>>{{ garanties.decennale.constructeur }}<<<VAR_END>>>
{% endif %}
{% if garanties.decennale.assureur %}
- **Assureur** : <<<VAR_START>>>{{ garanties.decennale.assureur }}<<<VAR_END>>>
{% endif %}
{% if garanties.decennale.numero_police %}
- **Police n°** : <<<VAR_START>>>{{ garanties.decennale.numero_police }}<<<VAR_END>>>
{% endif %}
{% if garanties.decennale.date_reception %}
- **Date de réception des travaux** : <<<VAR_START>>>{{ garanties.decennale.date_reception | format_date }}<<<VAR_END>>>
{% endif %}
{% if garanties.decennale.date_expiration %}
- **Date d'expiration** : <<<VAR_START>>>{{ garanties.decennale.date_expiration | format_date }}<<<VAR_END>>>
{% endif %}

{% if garanties.decennale.sinistres %}
### Sinistres déclarés

Les sinistres suivants ont été déclarés au titre de la garantie décennale :

{% for sinistre in garanties.decennale.sinistres %}
- **{{ sinistre.nature }}** (déclaré le <<<VAR_START>>>{{ sinistre.date_declaration | format_date }}<<<VAR_END>>>)
  {% if sinistre.statut %}- Statut : {{ sinistre.statut }}{% endif %}
  {% if sinistre.indemnisation %}- Indemnisation : <<<VAR_START>>>{{ sinistre.indemnisation | format_nombre }}<<<VAR_END>>> EUR{% endif %}
{% endfor %}
{% endif %}

{% if garanties.decennale.reserves %}
### Réserves à la réception

Des réserves ont été émises lors de la réception des travaux :

{% for reserve in garanties.decennale.reserves %}
- {{ reserve.description }}{% if reserve.levee %} (réserve levée le <<<VAR_START>>>{{ reserve.date_levee | format_date }}<<<VAR_END>>>){% else %} (réserve non levée){% endif %}
{% endfor %}
{% endif %}

{% else %}
Aucun travaux soumis à la garantie décennale n'a été réalisé au cours des dix dernières années.
{% endif %}

{% endif %}

{% if garanties.biennale %}
### Garantie de bon fonctionnement (biennale)

{% if garanties.biennale.applicable %}
Conformément à l'article 1792-3 du Code civil, les éléments d'équipement dissociables bénéficient d'une garantie de bon fonctionnement de deux ans.

{% if garanties.biennale.date_reception %}
- **Date de réception** : <<<VAR_START>>>{{ garanties.biennale.date_reception | format_date }}<<<VAR_END>>>
{% endif %}
{% if garanties.biennale.date_expiration %}
- **Date d'expiration** : <<<VAR_START>>>{{ garanties.biennale.date_expiration | format_date }}<<<VAR_END>>>
{% endif %}

{% if garanties.biennale.equipements_couverts %}
Équipements couverts :
{% for equipement in garanties.biennale.equipements_couverts %}
- {{ equipement }}
{% endfor %}
{% endif %}
{% endif %}
{% endif %}

{% if garanties.parfait_achevement %}
### Garantie de parfait achèvement

{% if garanties.parfait_achevement.applicable %}
Conformément à l'article 1792-6 du Code civil, l'entrepreneur est tenu de réparer tous les désordres signalés dans l'année qui suit la réception.

{% if garanties.parfait_achevement.date_reception %}
- **Date de réception** : <<<VAR_START>>>{{ garanties.parfait_achevement.date_reception | format_date }}<<<VAR_END>>>
{% endif %}
{% if garanties.parfait_achevement.date_expiration %}
- **Date d'expiration** : <<<VAR_START>>>{{ garanties.parfait_achevement.date_expiration | format_date }}<<<VAR_END>>>
{% endif %}

{% if garanties.parfait_achevement.desordres_signales %}
Désordres signalés :
{% for desordre in garanties.parfait_achevement.desordres_signales %}
- {{ desordre.description }}{% if desordre.repare %} (réparé){% else %} (en attente de réparation){% endif %}
{% endfor %}
{% endif %}
{% endif %}
{% endif %}

{% else %}
Le VENDEUR déclare qu'aucun travaux soumis aux garanties légales des constructeurs (décennale, biennale, parfait achèvement) n'a été réalisé au cours des dix dernières années.
{% endif %}

## Assurance habitation

{% if assurances %}

{% if assurances.habitation %}
### Assurance multirisque habitation

{% if assurances.habitation.existe %}
Le VENDEUR déclare avoir souscrit une assurance multirisque habitation pour le bien vendu.

{% if assurances.habitation.compagnie %}
- **Compagnie** : <<<VAR_START>>>{{ assurances.habitation.compagnie }}<<<VAR_END>>>
{% endif %}
{% if assurances.habitation.numero_police %}
- **Police n°** : <<<VAR_START>>>{{ assurances.habitation.numero_police }}<<<VAR_END>>>
{% endif %}
{% if assurances.habitation.echeance %}
- **Échéance annuelle** : <<<VAR_START>>>{{ assurances.habitation.echeance }}<<<VAR_END>>>
{% endif %}
{% if assurances.habitation.prime_annuelle %}
- **Prime annuelle** : <<<VAR_START>>>{{ assurances.habitation.prime_annuelle | format_nombre }}<<<VAR_END>>> EUR
{% endif %}

{% if assurances.habitation.garanties_incluses %}
Garanties incluses :
{% for garantie in assurances.habitation.garanties_incluses %}
- {{ garantie }}
{% endfor %}
{% endif %}

{% if assurances.habitation.transfert %}
### Transfert du contrat

Le contrat d'assurance pourra être transféré à l'ACQUEREUR conformément aux dispositions de l'article L. 121-10 du Code des assurances.

{% if assurances.habitation.transfert.modalites %}
Modalités : {{ assurances.habitation.transfert.modalites }}
{% endif %}
{% else %}
L'ACQUEREUR devra souscrire sa propre assurance multirisque habitation à compter de la prise de possession du bien.
{% endif %}

{% else %}
Le VENDEUR déclare ne pas avoir souscrit d'assurance multirisque habitation.

L'ACQUEREUR est informé de son obligation de souscrire une assurance multirisque habitation couvrant sa responsabilité civile et les dommages au bien.
{% endif %}
{% endif %}

{% if assurances.copropriete %}
### Assurance de la copropriété

L'immeuble est assuré au titre de la copropriété conformément aux dispositions de l'article 9-1 de la loi du 10 juillet 1965.

{% if assurances.copropriete.compagnie %}
- **Compagnie** : <<<VAR_START>>>{{ assurances.copropriete.compagnie }}<<<VAR_END>>>
{% endif %}
{% if assurances.copropriete.numero_police %}
- **Police n°** : <<<VAR_START>>>{{ assurances.copropriete.numero_police }}<<<VAR_END>>>
{% endif %}
{% if assurances.copropriete.echeance %}
- **Échéance** : <<<VAR_START>>>{{ assurances.copropriete.echeance }}<<<VAR_END>>>
{% endif %}

Cette assurance couvre les parties communes et la responsabilité civile de la copropriété.

{% if assurances.copropriete.garanties %}
Garanties spécifiques :
{% for garantie in assurances.copropriete.garanties %}
- {{ garantie }}
{% endfor %}
{% endif %}
{% endif %}

{% if assurances.pno %}
### Assurance propriétaire non occupant (PNO)

{% if assurances.pno.existe %}
Le VENDEUR déclare avoir souscrit une assurance propriétaire non occupant.

{% if assurances.pno.compagnie %}
- **Compagnie** : <<<VAR_START>>>{{ assurances.pno.compagnie }}<<<VAR_END>>>
{% endif %}
{% if assurances.pno.numero_police %}
- **Police n°** : <<<VAR_START>>>{{ assurances.pno.numero_police }}<<<VAR_END>>>
{% endif %}

{% if assurances.pno.transfert %}
Ce contrat pourra être transféré à l'ACQUEREUR s'il destine le bien à la location.
{% endif %}
{% else %}
Le VENDEUR déclare ne pas avoir souscrit d'assurance propriétaire non occupant.
{% endif %}
{% endif %}

{% else %}
L'ACQUEREUR est informé de son obligation de souscrire une assurance multirisque habitation couvrant sa responsabilité civile et les dommages au bien.

L'immeuble en copropriété fait l'objet d'une assurance collective souscrite par le syndic, conformément aux dispositions de la loi du 10 juillet 1965.
{% endif %}

## Garanties diverses

{% if garanties %}

{% if garanties.vices_caches %}
### Garantie des vices cachés

{% if garanties.vices_caches.clause_exoneration %}
Conformément aux dispositions de l'article 1643 du Code civil, le VENDEUR est exonéré de la garantie des vices cachés.

L'ACQUEREUR prend le bien dans son état actuel, tel qu'il l'a vu et visité, sans aucune garantie de la part du VENDEUR quant aux vices cachés qui pourraient l'affecter.

{% if garanties.vices_caches.exceptions %}
Cette clause ne s'applique pas aux cas suivants :
{% for exception in garanties.vices_caches.exceptions %}
- {{ exception }}
{% endfor %}
{% endif %}

{% if garanties.vices_caches.vices_declares %}
Le VENDEUR déclare avoir connaissance des vices suivants :
{% for vice in garanties.vices_caches.vices_declares %}
- {{ vice.description }}{% if vice.date_constatation %} (constaté le <<<VAR_START>>>{{ vice.date_constatation | format_date }}<<<VAR_END>>>){% endif %}
{% endfor %}

L'ACQUEREUR reconnaît avoir été informé de ces vices et les accepter.
{% endif %}

{% else %}
Conformément aux dispositions des articles 1641 et suivants du Code civil, le VENDEUR est tenu de la garantie des vices cachés qui rendraient le bien impropre à l'usage auquel on le destine ou qui diminueraient tellement cet usage que l'ACQUEREUR ne l'aurait pas acquis ou n'en aurait donné qu'un moindre prix s'il les avait connus.
{% endif %}
{% endif %}

{% if garanties.superficie %}
### Garantie de superficie (Loi Carrez)

{% if garanties.superficie.applicable %}
La superficie de la partie privative du lot est de <<<VAR_START>>>{{ garanties.superficie.surface }}<<<VAR_END>>> m2.

{% if garanties.superficie.mesurage %}
Ce mesurage a été effectué par <<<VAR_START>>>{{ garanties.superficie.mesurage.auteur }}<<<VAR_END>>> le <<<VAR_START>>>{{ garanties.superficie.mesurage.date | format_date }}<<<VAR_END>>>.
{% endif %}

Conformément à l'article 46 de la loi du 10 juillet 1965, si la superficie réelle est inférieure de plus de 5% à celle indiquée, l'ACQUEREUR pourra demander une diminution du prix proportionnelle à la moindre mesure.
{% endif %}
{% endif %}

{% if garanties.conformite_installations %}
### Garantie de conformité des installations

{% if garanties.conformite_installations.electrique %}
**Installation électrique** :
- État : <<<VAR_START>>>{{ garanties.conformite_installations.electrique.etat }}<<<VAR_END>>>
{% if garanties.conformite_installations.electrique.date_diagnostic %}- Diagnostic du <<<VAR_START>>>{{ garanties.conformite_installations.electrique.date_diagnostic | format_date }}<<<VAR_END>>>{% endif %}
{% if garanties.conformite_installations.electrique.anomalies %}- Anomalies : {{ garanties.conformite_installations.electrique.anomalies }}{% endif %}
{% endif %}

{% if garanties.conformite_installations.gaz %}
**Installation gaz** :
- État : <<<VAR_START>>>{{ garanties.conformite_installations.gaz.etat }}<<<VAR_END>>>
{% if garanties.conformite_installations.gaz.date_diagnostic %}- Diagnostic du <<<VAR_START>>>{{ garanties.conformite_installations.gaz.date_diagnostic | format_date }}<<<VAR_END>>>{% endif %}
{% if garanties.conformite_installations.gaz.anomalies %}- Anomalies : {{ garanties.conformite_installations.gaz.anomalies }}{% endif %}
{% endif %}

{% if garanties.conformite_installations.assainissement %}
**Assainissement** :
- Type : <<<VAR_START>>>{{ garanties.conformite_installations.assainissement.type }}<<<VAR_END>>>
{% if garanties.conformite_installations.assainissement.conformite %}- Conformité : <<<VAR_START>>>{{ garanties.conformite_installations.assainissement.conformite }}<<<VAR_END>>>{% endif %}
{% if garanties.conformite_installations.assainissement.date_controle %}- Contrôle du <<<VAR_START>>>{{ garanties.conformite_installations.assainissement.date_controle | format_date }}<<<VAR_END>>>{% endif %}
{% endif %}
{% endif %}

{% if garanties.contractuelles %}
### Garanties contractuelles spécifiques

Les parties conviennent des garanties complémentaires suivantes :

{% for garantie in garanties.contractuelles %}
#### {{ garantie.nom }}

{{ garantie.description }}

{% if garantie.duree %}
- **Durée** : <<<VAR_START>>>{{ garantie.duree }}<<<VAR_END>>>
{% endif %}
{% if garantie.etendue %}
- **Étendue** : {{ garantie.etendue }}
{% endif %}
{% if garantie.plafond %}
- **Plafond** : <<<VAR_START>>>{{ garantie.plafond | format_nombre }}<<<VAR_END>>> EUR
{% endif %}
{% endfor %}
{% endif %}

{% if garanties.fabricant %}
### Garanties fabricant

Les équipements suivants bénéficient de garanties fabricant en cours de validité :

{% for equipement in garanties.fabricant %}
- **{{ equipement.nom }}**
  {% if equipement.marque %}- Marque : {{ equipement.marque }}{% endif %}
  {% if equipement.date_achat %}- Date d'achat : <<<VAR_START>>>{{ equipement.date_achat | format_date }}<<<VAR_END>>>{% endif %}
  {% if equipement.date_expiration_garantie %}- Garantie jusqu'au : <<<VAR_START>>>{{ equipement.date_expiration_garantie | format_date }}<<<VAR_END>>>{% endif %}
{% endfor %}
{% endif %}

{% else %}
Le VENDEUR ne consent aucune garantie particulière en sus des garanties légales prévues par le Code civil.

L'ACQUEREUR prend le bien dans son état actuel, tel qu'il l'a vu et visité.
{% endif %}

{% if assurances and assurances.remarques %}

### Observations particulières

{{ assurances.remarques }}
{% endif %}

{% if garanties and garanties.remarques %}

### Observations sur les garanties

{{ garanties.remarques }}
{% endif %}
