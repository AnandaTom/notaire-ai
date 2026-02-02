{# ============================================================================
   PARTIE DÉVELOPPÉE - PROMESSE DE VENTE
   Version: 3.0.0 - 29 janvier 2026

   Sections spécifiques aux promesses unilatérales de vente.
   Basé sur l'analyse de 7 trames réelles (Principale + A, B, C, D, E, F).

   Contient :
   - Conclusion du contrat & Devoir d'information
   - Terminologie
   - Liste des meubles / Absence de meubles
   - Carence & Avenant éventuel
   - Conditions suspensives (prêt, vente préalable, urbanisme, préemption,
     hypothécaire, permis construire, déclaration travaux, conformité, absence prêt)
   - Délai de réalisation & Prorogation
   - Indemnité d'immobilisation / Clause pénale
   - Séquestre
   - Force exécutoire & Information rendez-vous signature
   - Ventilation du prix & Provision sur frais
   - Coût de l'opération et financement prévisionnel
   - Faculté de substitution / Absence de faculté
   - Propriété & Jouissance
   - Garantie hypothécaire & État du bien
   - Pouvoirs & Élection de domicile
   - Communication pièces & Faculté de rétractation
   - Réitération par acte authentique
   - État des meubles
   - Charges et conditions réglementaires
   - Absence construction/rénovation & APL
   - Équipements (15+ types: détecteur fumée, alarme, vidéo, broyeur,
     climatisation, chaudière, fibre, cheminée/poêle, citerne gaz,
     cuve fuel, cuve enterrée, ancienne cuve, panneaux PV,
     récupération eaux, puits/forages, piscines)
   - Ascenseurs
   - Domicile fiscal & Reprise ayants droit
   - Accès au bien & Division cadastrale & Bornage
   - Constitution de servitudes
   - Événement sanitaire (COVID)
   - Construction (conformité, RC décennale, géotechnique, réseaux,
     assurance-construction, DIUO, factures, contrat maison)
   - Diagnostics environnementaux détaillés (PPR, sismicité, sols, argiles)
   - Responsabilité environnementale & Déchets
   - Taxe terrain constructible
   - Anomalies diagnostics
   ============================================================================ #}

# EXPOSÉ

## CONCLUSION DU CONTRAT

Le **PROMETTANT** est propriétaire du **BIEN** ci-après désigné.

Il a fait connaître son intention de vendre ce **BIEN**.

Le **BÉNÉFICIAIRE** a manifesté son intention de l'acquérir.

C'est dans ces circonstances que les parties ont décidé de régulariser la présente promesse unilatérale de vente.

## DEVOIR D'INFORMATION RÉCIPROQUE

Les parties déclarent avoir été informées par le notaire soussigné de l'importance de leur devoir d'information réciproque, en application des articles 1112-1 et suivants du Code civil.

Chacune des parties s'engage à communiquer à l'autre toute information dont l'importance est déterminante pour le consentement de l'autre partie.

Le **PROMETTANT** déclare avoir communiqué au **BÉNÉFICIAIRE** toutes les informations relatives au **BIEN** dont il a connaissance et qui pourraient avoir une influence sur la décision du **BÉNÉFICIAIRE** d'acquérir ou non le **BIEN**.

## TERMINOLOGIE

Dans le présent acte, les termes suivants sont employés :

* **« PROMETTANT »** : désigne {% if promettants|length > 1 %}collectivement {% endif %}le(s) propriétaire(s) du **BIEN** qui s'engage(nt) irrévocablement à vendre ;

* **« BÉNÉFICIAIRE »** : désigne {% if beneficiaires|length > 1 %}collectivement {% endif %}la ou les personne(s) au profit de laquelle/desquelles la promesse est consentie et qui dispose(nt) d'une option d'achat ;

* **« BIEN »** : désigne l'ensemble immobilier objet de la présente promesse, tel que désigné ci-après ;

* **« PROMESSE »** : désigne le présent acte ;

* **« VENTE »** ou **« ACTE DE VENTE »** : désigne l'acte authentique à intervenir en cas de levée de l'option par le **BÉNÉFICIAIRE**.

# PROMESSE UNILATÉRALE DE VENTE

Ceci exposé, le **PROMETTANT** promet de vendre au **BÉNÉFICIAIRE**, qui accepte, le **BIEN** ci-après désigné, aux prix, charges et conditions ci-après énoncés.

Cette promesse est consentie sous les conditions et modalités suivantes.

# LISTE DES MEUBLES

{% if meubles and meubles.inclus and meubles.liste %}
Les meubles et objets mobiliers ci-après désignés sont compris dans la vente :

| Désignation des meubles | Valeur |
|-------------------------|--------|
{% for meuble in meubles.liste %}
| {{ meuble }} | - |
{% endfor %}

{% if meubles.valeur %}
Valeur totale estimée des meubles : {{ meubles.valeur | format_nombre }} €
{% endif %}

Ces meubles sont vendus en l'état où ils se trouvent, sans garantie.
{% else %}
Aucun meuble ou objet mobilier n'est compris dans la présente vente.
{% endif %}

## CARENCE

{% if carence %}
**En l'absence de levée d'option ou de signature de l'acte de vente** - En l'absence de levée d'option par le **BÉNÉFICIAIRE** ou à défaut de signature de l'acte de vente dans le délai ci-après fixé, la présente promesse sera **caduque de plein droit** sans qu'il soit besoin d'aucune mise en demeure ni d'aucune formalité judiciaire. Dans ce cas : le **PROMETTANT** reprendra sa pleine et entière liberté de disposer du **BIEN** ; l'indemnité d'immobilisation versée lui restera acquise à titre de dédommagement forfaitaire.

**En cas de levée d'option dans le délai** - Si le **BÉNÉFICIAIRE** lève l'option dans le délai imparti et si les conditions suspensives sont réalisées, la **VENTE** sera formée et les parties seront tenues de la réitérer par acte authentique.
{% else %}
À défaut de réalisation de la vente dans les délais convenus, les parties conviennent que la présente promesse deviendra caduque de plein droit, sans qu'il soit besoin d'aucune mise en demeure ni formalité judiciaire.
{% endif %}

## AVENANT ÉVENTUEL

{% if avenant_eventuel %}
Les parties pourront, d'un commun accord, modifier les termes de la présente promesse par avenant authentique.

Tout avenant devra être reçu par le notaire soussigné ou son successeur.

Les frais d'avenant seront à la charge de {{ avenant_eventuel.frais_charge | default("la partie qui en fera la demande") }}.
{% else %}
Toute modification de la présente promesse devra faire l'objet d'un avenant authentique reçu par le notaire soussigné.
{% endif %}

# PARTIE DÉVELOPPÉE

## CONDITIONS DE LA PROMESSE

### DÉLAI DE RÉALISATION

{% if delai_realisation %}
La présente promesse est consentie pour une durée de **{{ delai_realisation.duree | default('QUATRE') }} MOIS** à compter de ce jour.

{% if delai_realisation.date_butoir %}
La date butoir de réalisation est donc fixée au **{{ delai_realisation.date_butoir | format_date }}** au plus tard.
{% endif %}
{% else %}
La présente promesse est consentie pour une durée de **QUATRE MOIS** à compter de ce jour.
{% endif %}

Le **PROMETTANT** s'engage irrévocablement à vendre le **BIEN** aux prix, charges et conditions ci-dessus, pendant toute la durée de la promesse.

{% if delai_realisation and delai_realisation.prorogation %}
Ce délai pourra être prorogé par accord des parties constaté par acte authentique, à la demande de l'une ou l'autre des parties, sans que cette prorogation puisse excéder **{{ delai_realisation.prorogation_max | default('TROIS') }} MOIS** supplémentaires.
{% endif %}

{% if indemnite_immobilisation %}
### INDEMNITÉ D'IMMOBILISATION

En contrepartie de l'immobilisation du **BIEN** par le **PROMETTANT**, le **BÉNÉFICIAIRE** verse, à titre d'indemnité d'immobilisation, une somme de **{{ indemnite_immobilisation.montant_lettres | default("VINGT-DEUX MILLE CINQ CENTS EUROS") | upper }}** soit **{{ indemnite_immobilisation.montant | default(22500) | format_nombre }} {{ prix.devise | default("EUR") }}**, représentant **{{ indemnite_immobilisation.pourcentage | default(5) }} %** du prix de vente.

{% if indemnite_immobilisation.versement == "signature" %}
Cette somme est versée ce jour entre les mains du notaire soussigné, qui en donne quittance.
{% elif indemnite_immobilisation.versement == "differe" %}
Cette somme sera versée au plus tard le **{{ indemnite_immobilisation.date_versement | format_date }}** entre les mains du notaire soussigné.
{% elif indemnite_immobilisation.versement == "virement" %}
Cette somme sera versée par virement bancaire sur le compte séquestre du notaire soussigné dans les **{{ indemnite_immobilisation.delai_virement | default(5) }} jours** de ce jour.
{% endif %}

**Sort de l'indemnité d'immobilisation :**

* **En cas de réalisation de la vente** : cette somme s'imputera sur le prix de vente.

* **En cas de non-levée d'option** : le **BÉNÉFICIAIRE** devra lever l'option et régulariser l'acte de vente dans le délai ci-dessus fixé. À défaut, l'indemnité d'immobilisation restera acquise au **PROMETTANT** à titre de dédommagement forfaitaire du préjudice subi du fait de l'immobilisation du **BIEN**.

* **En cas de non-réalisation d'une condition suspensive** : si la vente ne se réalise pas en raison de la défaillance d'une condition suspensive, l'indemnité d'immobilisation sera restituée au **BÉNÉFICIAIRE**, sans intérêts ni indemnité.
{% endif %}

{% if sequestre %}
### SÉQUESTRE

**1. Constitution d'un mandataire commun** - Les parties constituent le notaire soussigné mandataire commun pour recevoir et conserver les sommes qui lui seront versées au titre de la présente promesse, notamment l'indemnité d'immobilisation.

**2. Mission du séquestre** - Le notaire soussigné, en sa qualité de séquestre, aura pour mission de : recevoir les sommes versées par le **BÉNÉFICIAIRE** ; les conserver jusqu'à la réalisation ou la caducité de la présente promesse ; les restituer ou les remettre à qui de droit selon les termes de la présente promesse.

**3. Difficultés entre les parties** - En cas de difficultés entre les parties sur l'attribution des sommes séquestrées, le notaire soussigné : conservera ces sommes jusqu'à ce qu'un accord intervienne entre les parties ; ou jusqu'à ce qu'une décision de justice passée en force de chose jugée lui soit notifiée. Le notaire soussigné ne pourra en aucun cas être tenu responsable des conséquences de ce différend.

**4. Acceptation** - Le notaire soussigné accepte cette mission de séquestre.

**5. Décharge** - Le notaire soussigné sera déchargé de sa mission de séquestre par la remise des fonds à qui de droit conformément aux stipulations de la présente promesse ou à la décision de justice intervenue.
{% endif %}

## Force exécutoire de la promesse

La présente promesse est établie en la forme authentique pour conférer aux parties la force exécutoire attachée aux actes notariés, conformément aux dispositions de l'article 3 de l'ordonnance n° 45-2590 du 2 novembre 1945.

En conséquence, à défaut pour l'une des parties de satisfaire à ses obligations, l'autre pourra poursuivre l'exécution forcée des présentes en vertu d'une copie exécutoire.

## Information des parties sur le rendez-vous de signature

Le notaire soussigné informera les parties de la date de signature de l'acte authentique de vente par tout moyen à sa convenance (courrier, courriel, téléphone) au moins **HUIT JOURS** à l'avance.

Les parties s'engagent à être disponibles à la date de convocation et à informer le notaire de toute impossibilité dans les plus brefs délais.

## Conséquences de la ventilation du prix

{% if prix.ventilation %}
Le prix ci-dessus est ventilé comme suit :

| Élément | Montant |
| :---- | ----: |
| Biens immobiliers | {{ prix.ventilation.immobilier | format_nombre }} EUR |
{% if prix.ventilation.meubles %}| Meubles meublants | {{ prix.ventilation.meubles | format_nombre }} EUR |
{% endif %}{% if prix.ventilation.autres %}| Autres éléments | {{ prix.ventilation.autres | format_nombre }} EUR |
{% endif %}| **TOTAL** | **{{ prix.montant | format_nombre }} EUR** |

Cette ventilation est retenue pour le calcul des droits d'enregistrement et des émoluments du notaire.

Les parties déclarent que cette ventilation correspond à la valeur réelle des différents éléments vendus.
{% else %}
Le prix de vente ci-dessus comprend les biens immobiliers décrits{% if meubles and meubles.inclus %} ainsi que les meubles meublants listés ci-avant{% endif %}.

Aucune ventilation particulière du prix n'est effectuée entre les différents éléments.
{% endif %}

{% if provision_frais %}
### PROVISION SUR FRAIS, TAXES ET HONORAIRES

{% if provision_frais.montant %}
Le **BÉNÉFICIAIRE** verse ce jour au notaire soussigné, à titre de provision sur les frais, droits et honoraires de la vente à intervenir, une somme de **{{ provision_frais.montant_lettres | upper }}** soit **{{ provision_frais.montant | format_nombre }} {{ prix.devise | default("EUR") }}**.
{% endif %}

{% if provision_frais.modalites == "virement" %}
Cette somme sera versée par virement bancaire dans les **{{ provision_frais.delai | default(15) }} jours** de ce jour.
{% endif %}

Cette provision sera imputée sur le montant définitif des frais lors de la réitération de la vente. Si la vente ne se réalise pas, cette provision sera restituée au **BÉNÉFICIAIRE**, déduction faite des frais et honoraires dus au titre de la présente promesse.
{% endif %}

{% if virement_coordonnees %}
### VIREMENT À EFFECTUER - COORDONNÉES DE L'OFFICE NOTARIAL

Les sommes dues au titre des présentes devront être versées par virement bancaire aux coordonnées suivantes :

{% if virement_coordonnees.banque %}
**Banque** : {{ virement_coordonnees.banque }}
{% endif %}
{% if virement_coordonnees.iban %}
**IBAN** : {{ virement_coordonnees.iban }}
{% endif %}
{% if virement_coordonnees.bic %}
**BIC** : {{ virement_coordonnees.bic }}
{% endif %}
{% if virement_coordonnees.titulaire %}
**Titulaire** : {{ virement_coordonnees.titulaire }}
{% endif %}
{% if virement_coordonnees.reference %}
**Référence** : {{ virement_coordonnees.reference }}
{% endif %}
{% endif %}

{% if conditions_suspensives %}
## CONDITIONS SUSPENSIVES

La présente promesse de vente est consentie sous les conditions suspensives suivantes, dont la réalisation conditionne la perfection de la vente :

{% if conditions_suspensives.pret and conditions_suspensives.pret.applicable %}
### Condition suspensive d'obtention de prêt

La réalisation de la présente promesse est subordonnée à l'obtention par le **BÉNÉFICIAIRE** d'un ou plusieurs prêts d'un montant en principal de **{{ conditions_suspensives.pret.montant_lettres | default("TROIS CENT SOIXANTE MILLE EUROS") | upper }}** soit **{{ conditions_suspensives.pret.montant | default(360000) | format_nombre }} {{ prix.devise | default("EUR") }}**, remboursable sur une durée de **{{ conditions_suspensives.pret.duree_mois | default(240) }} mois** au taux d'intérêt nominal maximum de **{{ conditions_suspensives.pret.taux_max | default(4.5) }} %** l'an (hors assurance).

{% if conditions_suspensives.pret.type == "immobilier" %}
Ce prêt est destiné au financement de l'acquisition du **BIEN** objet des présentes.
{% endif %}

**Obligations du BÉNÉFICIAIRE :**

Le **BÉNÉFICIAIRE** s'oblige :

* à déposer au moins une demande de prêt conforme aux caractéristiques ci-dessus auprès d'un établissement de crédit dans les **{{ conditions_suspensives.pret.delai_depot | default(15) }} jours** de la signature des présentes ;

* à justifier au **PROMETTANT** du dépôt de sa demande dans le même délai ;

* à faire ses meilleurs efforts pour obtenir le prêt sollicité ;

* à informer le **PROMETTANT** de la décision de l'établissement prêteur dès qu'il en aura connaissance.

**Délai de réalisation de la condition :**

Cette condition suspensive devra être réalisée au plus tard le **{{ conditions_suspensives.pret.date_butoir | format_date }}**, soit dans un délai de **{{ conditions_suspensives.pret.delai_jours | default(60) }} jours** à compter de ce jour.

**En cas de refus de prêt :**

Si le **BÉNÉFICIAIRE** justifie, par la production d'une ou plusieurs attestations de refus émanant d'établissements de crédit différents, n'avoir pu obtenir le prêt sollicité dans les conditions définies ci-dessus, la présente promesse sera caduque de plein droit et l'indemnité d'immobilisation lui sera restituée.

{% if conditions_suspensives.pret.declarations_promettant %}
**Déclarations du PROMETTANT :**

À ce sujet, le **PROMETTANT** déclare :
{% for declaration in conditions_suspensives.pret.declarations_promettant %}
* {{ declaration }}
{% endfor %}
{% endif %}

**En cas de non-justification :**

À défaut de justification dans les délais impartis, le **PROMETTANT** pourra, à son choix :
* soit considérer la condition comme réalisée et réitérer la vente,
* soit considérer la promesse comme caduque et conserver l'indemnité d'immobilisation.
{% endif %}

{% if conditions_suspensives.vente_prealable and conditions_suspensives.vente_prealable.applicable %}
### Condition suspensive de vente préalable

La réalisation de la présente promesse est subordonnée à la vente par le **BÉNÉFICIAIRE** du bien lui appartenant situé **{{ conditions_suspensives.vente_prealable.adresse_bien }}**.

Cette vente devra être conclue au plus tard le **{{ conditions_suspensives.vente_prealable.date_butoir | format_date }}**.

Le **BÉNÉFICIAIRE** s'engage :

* à mettre ce bien en vente dans les meilleurs délais ;
* à confier un mandat de vente à un ou plusieurs professionnels de l'immobilier ;
* à justifier de ses diligences auprès du **PROMETTANT** ;
* à informer le **PROMETTANT** de la conclusion de la vente dès que celle-ci sera intervenue.
{% endif %}

{% if conditions_suspensives.urbanisme and conditions_suspensives.urbanisme.applicable %}
### Condition suspensive d'urbanisme

La réalisation de la présente promesse est subordonnée à l'obtention d'un certificat d'urbanisme opérationnel confirmant que le **BIEN** peut faire l'objet de l'affectation projetée par le **BÉNÉFICIAIRE**, à savoir : {{ conditions_suspensives.urbanisme.projet }}.

Le **BÉNÉFICIAIRE** devra déposer sa demande de certificat d'urbanisme dans les **{{ conditions_suspensives.urbanisme.delai_depot | default(15) }} jours** de ce jour.

Cette condition devra être réalisée au plus tard le **{{ conditions_suspensives.urbanisme.date_butoir | format_date }}**.
{% endif %}

{% if conditions_suspensives.droit_preemption and conditions_suspensives.droit_preemption.applicable %}
### Condition suspensive de purge du droit de préemption

La réalisation de la présente promesse est subordonnée à la non-préemption du **BIEN** par le ou les titulaires d'un droit de préemption légal.

Le notaire soussigné se charge d'accomplir les formalités de purge de ce droit de préemption et d'en informer les parties du résultat.

{% if conditions_suspensives.droit_preemption.titulaires %}
Les titulaires du droit de préemption susceptibles d'être concernés sont :
{% for titulaire in conditions_suspensives.droit_preemption.titulaires %}
* {{ titulaire }}
{% endfor %}
{% endif %}

Le délai de préemption est de **{{ conditions_suspensives.droit_preemption.delai | default("DEUX") }} MOIS** à compter de la réception de la déclaration d'intention d'aliéner.
{% endif %}

{% if conditions_suspensives.etat_hypothecaire and conditions_suspensives.etat_hypothecaire.applicable %}
### Condition suspensive d'état hypothécaire

La réalisation de la présente promesse est subordonnée à l'obtention d'un état hypothécaire sur formalités ne révélant que les inscriptions connues des parties et mentionnées aux présentes.
{% endif %}

{% if conditions_suspensives.permis_construire and conditions_suspensives.permis_construire.applicable %}
### Condition suspensive d'obtention de permis de construire

La réalisation de la présente promesse est subordonnée à l'obtention par le **BÉNÉFICIAIRE** d'un permis de construire pour {{ conditions_suspensives.permis_construire.projet | default("le projet envisagé") }}.

Le **BÉNÉFICIAIRE** s'engage à déposer sa demande de permis de construire dans les **{{ conditions_suspensives.permis_construire.delai_depot | default(30) }} jours** de ce jour.

Cette condition devra être réalisée au plus tard le **{{ conditions_suspensives.permis_construire.date_butoir | format_date }}**.

{% if conditions_suspensives.permis_construire.affichage %}
**Modalités d'affichage du permis de construire** - L'affichage sur le terrain du permis de construire est assuré par les soins du bénéficiaire dudit permis de construire, conformément aux dispositions des articles R 424-15 et A 424-15 à A 424-19 du Code de l'urbanisme. Le panneau doit être installé de telle sorte que les renseignements qu'il contient demeurent lisibles de la voie publique, pendant toute la durée du chantier.
{% endif %}

{% if conditions_suspensives.permis_construire.transfert_possible %}
**Possibilité de transfert du permis de construire** - Au cas où le permis de construire serait obtenu et que les présentes ne puissent se réaliser, le **PROMETTANT** pourra exiger du **BÉNÉFICIAIRE** le transfert du permis de construire à son profit, ou à défaut, l'annulation dudit permis.
{% endif %}
{% endif %}

{% if conditions_suspensives.declaration_prealable_travaux and conditions_suspensives.declaration_prealable_travaux.applicable %}
### Condition suspensive d'obtention d'arrêté de non-opposition à déclaration préalable de travaux

Pour la réalisation des présentes, le **PROMETTANT** devra obtenir les arrêtés de non-opposition à déclaration de travaux portant sur {{ conditions_suspensives.declaration_prealable_travaux.objet | default("les travaux projetés") }}.

Cette condition devra être réalisée au plus tard le **{{ conditions_suspensives.declaration_prealable_travaux.date_butoir | format_date }}**.
{% endif %}

{% if conditions_suspensives.attestation_conformite and conditions_suspensives.attestation_conformite.applicable %}
### Condition suspensive d'obtention d'une attestation de non-contestation à la conformité

Pour la réalisation des présentes, le **PROMETTANT** devra obtenir{% if conditions_suspensives.attestation_conformite.delai %} dans un délai de **{{ conditions_suspensives.attestation_conformite.delai }}** à compter des présentes{% endif %} une attestation de non-contestation de la conformité des travaux réalisés, conformément aux dispositions des articles L 462-1 et suivants du Code de l'urbanisme.
{% endif %}

{% if conditions_suspensives.absence_pret %}
### Absence de prêt

Le **BÉNÉFICIAIRE** déclare qu'il n'entend pas contracter d'emprunt pour le financement de l'acquisition envisagée, le financement s'effectuant exclusivement au moyen de ses fonds personnels.

Si, contrairement à cette déclaration, il avait néanmoins recours à un tel prêt, il reconnaît avoir été informé qu'il ne pourrait se prévaloir des dispositions protectrices prévues par les articles L 312-15 et suivants du Code de la consommation en cas de non-obtention de ce prêt.
{% endif %}

{% if conditions_suspensives.autres %}
### Autres conditions suspensives

{% for condition in conditions_suspensives.autres %}
**{{ condition.titre }}**

{{ condition.description }}

{% if condition.date_butoir %}
Cette condition devra être réalisée au plus tard le **{{ condition.date_butoir | format_date }}**.
{% endif %}

{% endfor %}
{% endif %}

### Règles communes aux conditions suspensives

**Défaillance des conditions :**

Si l'une quelconque des conditions suspensives stipulées ci-dessus n'est pas réalisée dans le délai prévu, la présente promesse sera caduque de plein droit, sans indemnité de part ni d'autre, sauf stipulation contraire prévue ci-dessus.

L'indemnité d'immobilisation versée sera restituée au **BÉNÉFICIAIRE**.

**Renonciation :**

Le **BÉNÉFICIAIRE**, seul bénéficiaire des conditions suspensives stipulées dans son intérêt, pourra y renoncer expressément par notification écrite au **PROMETTANT** et au notaire soussigné.

**Réalisation des conditions :**

La justification de la réalisation des conditions suspensives devra être fournie au notaire soussigné par tout moyen.

{% endif %}

{% if clause_penale %}
## CLAUSE PÉNALE

En application des articles 1231-5 et suivants du Code civil :

**En cas d'inexécution par le PROMETTANT :**

Si le **PROMETTANT**, après levée de l'option par le **BÉNÉFICIAIRE** et réalisation des conditions suspensives, refuse de réitérer la vente ou de signer l'acte authentique, il devra verser au **BÉNÉFICIAIRE**, à titre de clause pénale, une somme égale à **{{ clause_penale.pourcentage_promettant | default(10) }} %** du prix de vente, soit **{{ (prix.montant * (clause_penale.pourcentage_promettant | default(10)) / 100) | format_nombre }} {{ prix.devise | default("EUR") }}**, outre la restitution de l'indemnité d'immobilisation.

Le **BÉNÉFICIAIRE** conserve en outre la faculté de poursuivre l'exécution forcée de la vente.

**En cas d'inexécution par le BÉNÉFICIAIRE :**

Si le **BÉNÉFICIAIRE**, après avoir levé l'option, refuse de réitérer la vente dans les délais convenus, le **PROMETTANT** pourra, à son choix :

* soit exiger l'exécution forcée de la vente ;
* soit considérer la promesse comme caduque et conserver l'indemnité d'immobilisation à titre de clause pénale, sans préjudice de tous dommages et intérêts complémentaires.
{% endif %}

{% if faculte_substitution and faculte_substitution.autorisee %}
## FACULTÉ DE SUBSTITUTION

Le **BÉNÉFICIAIRE** a la faculté de se substituer, pour la réitération de la vente, toute personne physique ou morale de son choix.

{% if faculte_substitution.conditions %}
Cette substitution devra être notifiée au **PROMETTANT** et au notaire soussigné au moins **{{ faculte_substitution.delai_notification | default(15) }} jours** avant la date prévue pour la réitération.
{% endif %}

**Effets de la substitution :**

En cas de substitution :

* le **BÉNÉFICIAIRE** initial restera garant solidaire de toutes les obligations du substitué envers le **PROMETTANT** ;
* le substitué devra remplir les mêmes conditions que le **BÉNÉFICIAIRE** initial pour l'obtention du prêt, le cas échéant ;
* l'indemnité d'immobilisation versée restera acquise à la présente promesse et sera imputée sur le prix de vente au profit du substitué.

{% if faculte_substitution.sci_constitution %}
La substitution pourra notamment intervenir au profit d'une société civile immobilière ou de toute autre structure juridique à constituer par le **BÉNÉFICIAIRE**, sous réserve de l'accord du ou des établissements prêteurs le cas échéant.
{% endif %}

{% elif faculte_substitution is defined and not faculte_substitution.autorisee %}
## ABSENCE DE FACULTÉ DE SUBSTITUTION

Le **BÉNÉFICIAIRE** n'a pas la faculté de se substituer un tiers pour la réitération de la vente.

Il ne pourra céder le bénéfice de la présente promesse, ni en tout ni en partie.
{% else %}
## ABSENCE DE FACULTÉ DE SUBSTITUTION

Sauf accord exprès et préalable du **PROMETTANT**, le **BÉNÉFICIAIRE** n'a pas la faculté de se substituer un tiers pour la réitération de la vente.
{% endif %}

{% if propriete_jouissance %}
## PROPRIÉTÉ - JOUISSANCE

**Propriété :**

Le **BÉNÉFICIAIRE** aura la propriété du **BIEN** à compter de la signature de l'acte authentique de vente.

**Jouissance :**

{% if propriete_jouissance.libre %}
Le **BÉNÉFICIAIRE** aura la jouissance du **BIEN** par la prise de possession réelle à compter de la signature de l'acte de vente, le **BIEN** étant alors libre de toute occupation.
{% elif propriete_jouissance.location %}
Le **BIEN** est actuellement donné en location. Le **BÉNÉFICIAIRE** sera subrogé dans les droits et obligations du **PROMETTANT** à l'égard du locataire à compter de la signature de l'acte de vente.

Le bail en cours est le suivant : {{ propriete_jouissance.location.description }}.
{% endif %}

{% if propriete_jouissance.visites_autorisees %}
**Visites avant jouissance :**

Le **PROMETTANT** autorise le **BÉNÉFICIAIRE** à visiter le **BIEN** avant la signature de l'acte authentique, après accord préalable sur la date et l'heure, et en sa présence ou celle de son mandataire.
{% endif %}
{% endif %}

## Garantie hypothecaire

Le **PROMETTANT** s'engage à rapporter mainlevée et radiation de toutes inscriptions hypothécaires ou privilèges grevant le **BIEN** au plus tard le jour de la signature de l'acte authentique de vente.

Les frais de mainlevée et de radiation seront à la charge du **PROMETTANT**.

{% if hypotheques %}
À ce jour, le **BIEN** est grevé des inscriptions suivantes :
{% for hyp in hypotheques %}
* {{ hyp.nature }} au profit de {{ hyp.beneficiaire }} pour un montant de {{ hyp.montant | format_nombre }} €, inscrite le {{ hyp.date_inscription | format_date }}
{% endfor %}
{% else %}
Le **PROMETTANT** déclare que le **BIEN** est libre de toute inscription hypothécaire ou privilège, sous réserve de l'état hypothécaire à produire.
{% endif %}

{% if etat_bien %}
## ÉTAT DU BIEN

Le **BIEN** sera vendu dans l'état où il se trouvera au jour de l'entrée en jouissance, sans aucune garantie de la part du **PROMETTANT** pour raison de vices apparents ou cachés, le **BÉNÉFICIAIRE** déclarant avoir personnellement visité le **BIEN** et en connaître parfaitement l'état.

{% if etat_bien.travaux_promettant %}
**Travaux à la charge du PROMETTANT :**

Le **PROMETTANT** s'engage à réaliser, avant la signature de l'acte authentique, les travaux suivants :
{% for travail in etat_bien.travaux_promettant %}
* {{ travail }}
{% endfor %}
{% endif %}

{% if etat_bien.reserves %}
**Réserves du PROMETTANT :**

Le **PROMETTANT** fait les réserves suivantes :
{% for reserve in etat_bien.reserves %}
* {{ reserve }}
{% endfor %}
{% endif %}
{% endif %}

{% if restrictions_usage %}
## RESTRICTIONS D'USAGE

Le bien objet des présentes est soumis aux restrictions d'usage suivantes :

{% for restriction in restrictions_usage %}
**{{ restriction.type | default("Restriction") }}**

{{ restriction.description }}

{% if restriction.origine %}
*Origine : {{ restriction.origine }}*
{% endif %}
{% endfor %}

Le **BÉNÉFICIAIRE** déclare avoir été pleinement informé de ces restrictions et les accepter.
{% endif %}

## POUVOIRS

Le **BÉNÉFICIAIRE** confère tous pouvoirs au porteur d'une copie exécutoire ou d'un extrait des présentes pour accomplir toutes formalités et faire toutes déclarations nécessaires à la publicité des présentes.

Le **PROMETTANT** consent à ce que la présente promesse soit publiée au fichier immobilier.

## ÉLECTION DE DOMICILE

Pour l'exécution des présentes et de leurs suites, les parties élisent domicile en leurs demeures respectives ci-dessus indiquées.

Toutes notifications ou significations seront valablement faites aux adresses indiquées en tête des présentes, sauf changement notifié par lettre recommandée avec accusé de réception.

{% if communication_pieces %}
## COMMUNICATION DES PIÈCES ET DOCUMENTS

Les parties s'engagent à communiquer au notaire soussigné, dans les meilleurs délais et au plus tard **{{ communication_pieces.delai | default("QUINZE") }} jours** avant la date de signature de l'acte de vente, tous les documents et informations nécessaires à l'établissement de cet acte.

Le **PROMETTANT** s'engage notamment à fournir :
* les titres de propriété ;
* le règlement de copropriété et ses modificatifs ;
* les procès-verbaux des assemblées générales des trois dernières années ;
* le carnet d'entretien de l'immeuble ;
* les diagnostics techniques obligatoires ;
* tout document nécessaire à l'établissement de l'acte de vente.

Le **BÉNÉFICIAIRE** s'engage notamment à fournir :
* les justificatifs de son identité et de sa situation matrimoniale ;
* les offres de prêt acceptées le cas échéant ;
* tout document demandé par le notaire.
{% endif %}

## FACULTÉ DE RÉTRACTATION

Conformément aux dispositions de l'article L. 271-1 du Code de la construction et de l'habitation, le **BÉNÉFICIAIRE** non professionnel de l'immobilier dispose d'un délai de **DIX JOURS** pour exercer sa faculté de rétractation.

Ce délai court à compter du lendemain de la première présentation de la lettre lui notifiant le présent acte ou de la remise directe contre récépissé.

**Modalités d'exercice :**

Pour exercer cette faculté, le **BÉNÉFICIAIRE** devra notifier sa rétractation au **PROMETTANT** par lettre recommandée avec demande d'avis de réception ou par tout autre moyen présentant des garanties équivalentes pour la détermination de la date de réception ou de remise.

**Effets de la rétractation :**

En cas de rétractation dans le délai légal :
* la présente promesse sera considérée comme n'ayant jamais été conclue ;
* toutes les sommes versées par le **BÉNÉFICIAIRE** lui seront restituées dans un délai de **VINGT ET UN JOURS** à compter du lendemain de la date de rétractation ;
* aucune indemnité ne sera due de part et d'autre.

{% if retractation_notification %}
**Notification :**

Le présent acte sera notifié au **BÉNÉFICIAIRE** par {{ retractation_notification.mode | default("lettre recommandée avec accusé de réception") }}, le délai de rétractation ne commençant à courir qu'à compter de cette notification.
{% endif %}

## RÉITÉRATION PAR ACTE AUTHENTIQUE

Les parties s'engagent à réitérer la présente promesse par acte authentique dès que toutes les conditions suspensives seront réalisées et au plus tard à la date butoir fixée ci-dessus.

Le notaire soussigné se chargera de convoquer les parties à la signature de l'acte authentique de vente.

**Lieu de signature :**

L'acte authentique de vente sera reçu en l'office du notaire soussigné{% if acte.notaire_beneficiaire %}, ou en celui de {{ acte.notaire_beneficiaire.civilite }} {{ acte.notaire_beneficiaire.prenom }} {{ acte.notaire_beneficiaire.nom }}, notaire assistant le **BÉNÉFICIAIRE**{% endif %}.

**Pièces à fournir :**

Les parties devront fournir au notaire toutes les pièces nécessaires à l'établissement de l'acte de vente dans les meilleurs délais et au plus tard **QUINZE jours** avant la date de signature prévue.

**Convocation :**

Le notaire soussigné convoquera les parties par tout moyen à sa convenance (courrier simple, recommandé, courriel) au moins **HUIT jours** avant la date prévue pour la signature.

## Etat des meubles

{% if meubles and meubles.inclus and meubles.liste %}
Les meubles et objets mobiliers compris dans la vente sont ceux existant dans les lieux et désignés ci-dessus. Ils sont vendus en l'état où ils se trouvent, sans garantie de leur bon fonctionnement.

Le **BÉNÉFICIAIRE** déclare les avoir examinés et les accepter en l'état.
{% else %}
Il est précisé qu'aucun meuble ni objet mobilier n'est compris dans la présente vente. Le **BIEN** sera livré vide de tout mobilier.
{% endif %}

# CHARGES ET CONDITIONS résultant DE L'APPLICATION de réglementationS PARTICULIÈRE

La vente à intervenir sera soumise aux charges et conditions résultant de l'application des réglementations particulières ci-après exposées.

## Absence d'opération de construction ou de rénovation depuis dix ans

{% if travaux_recents and travaux_recents.existe %}
Le **PROMETTANT** déclare que des travaux ont été réalisés sur le **BIEN** au cours des dix dernières années :
{% for travail in travaux_recents.liste %}
* {{ travail.description }} - réalisés par {{ travail.entreprise }}{% if travail.assurance_decennale %} - couverts par une garantie décennale{% endif %}
{% endfor %}

{% if travaux_recents.liste | selectattr("assurance_decennale", "equalto", true) | list | length > 0 %}
Le **PROMETTANT** déclare que les travaux ci-dessus couverts par une garantie décennale bénéficient toujours de cette garantie, laquelle sera transmise au **BÉNÉFICIAIRE**.
{% endif %}
{% else %}
Le **PROMETTANT** déclare qu'aucune opération de construction, de rénovation ou d'extension n'a été réalisée sur le **BIEN** au cours des dix dernières années.

En conséquence, aucune garantie décennale n'est en cours pour le **BIEN**.
{% endif %}

## Aide personnalisée au logement

{% if apl and apl.conventionnement %}
Le **PROMETTANT** déclare que le **BIEN** fait l'objet d'un conventionnement APL avec l'État, conclu le {{ apl.date_convention | format_date }}, arrivant à échéance le {{ apl.date_echeance | format_date }}.

Le **BÉNÉFICIAIRE** sera subrogé dans les droits et obligations résultant de cette convention.
{% else %}
Le **PROMETTANT** déclare que le **BIEN** ne fait l'objet d'aucun conventionnement au titre de l'aide personnalisée au logement (APL).
{% endif %}

# Équipements du BIEN

## Détecteur de fumée

{% if bien.equipements and bien.equipements.detecteur_fumee %}
Le **BIEN** est équipé d'un ou plusieurs détecteurs de fumée conformes à la norme NF EN 14604, comme l'exige la loi n° 2010-238 du 9 mars 2010.

Le **PROMETTANT** déclare que ces détecteurs sont en état de fonctionnement.
{% else %}
Le **PROMETTANT** s'engage à faire installer un détecteur de fumée conforme à la norme NF EN 14604 avant la signature de l'acte de vente, conformément à la loi n° 2010-238 du 9 mars 2010.
{% endif %}

**Alarme** - {% if bien.equipements and bien.equipements.alarme %}Le **BIEN** est équipé d'un système d'alarme intrusion. Le **BÉNÉFICIAIRE** pourra reprendre tout contrat d'entretien éventuel à sa charge s'il le souhaite.{% else %}Le **BIEN** n'est pas équipé d'un système d'alarme.{% endif %}

**Vidéosurveillance** - {% if bien.equipements and bien.equipements.videosurveillance %}Le **BIEN** est équipé d'un système de vidéosurveillance. Le **PROMETTANT** déclare que ce système est conforme à la réglementation en vigueur, notamment en ce qui concerne la déclaration à la CNIL.{% else %}Le **BIEN** n'est pas équipé d'un système de vidéosurveillance.{% endif %}

**Broyeur** - {% if bien.equipements and bien.equipements.wc_broyeur %}Le **BIEN** est équipé d'un broyeur sanitaire. Le **PROMETTANT** déclare que cet équipement est en état de fonctionnement. Le **BÉNÉFICIAIRE** est informé des contraintes d'entretien spécifiques à ce type d'équipement.{% else %}Le **BIEN** n'est pas équipé d'un broyeur sanitaire.{% endif %}

**Climatisation** - {% if bien.equipements and bien.equipements.climatisation %}Le **BIEN** est équipé d'un système de climatisation. Le **PROMETTANT** déclare que ce système est en état de fonctionnement et que les contrôles obligatoires ont été réalisés.{% else %}Le **BIEN** n'est pas équipé d'un système de climatisation.{% endif %}

{% if bien.equipements and bien.equipements.chaudiere is defined %}
**Chaudière – Contrôle – Information** - {% if bien.equipements.chaudiere %}Le **BIEN** est équipé d'une chaudière{% if bien.equipements.chaudiere_type %} de type {{ bien.equipements.chaudiere_type }}{% endif %}. Le **PROMETTANT** déclare que cette chaudière a fait l'objet de l'entretien annuel obligatoire. La facture du dernier entretien sera transmise au **BÉNÉFICIAIRE** au plus tard à la réitération des présentes.{% else %}Le **BIEN** n'est pas équipé d'une chaudière.{% endif %}
{% endif %}

{% if bien.equipements and bien.equipements.fibre_optique is defined %}
**Fibre optique** - {% if bien.equipements.fibre_optique %}Le **BIEN** est raccordé à la fibre optique. Le **PROMETTANT** déclare que l'installation est en état de fonctionnement.{% else %}Le **BIEN** n'est pas raccordé à la fibre optique.{% endif %}
{% endif %}

{% if bien.equipements and bien.equipements.cheminee is defined %}
**Cheminée / Poêle** - {% if bien.equipements.cheminee %}Le **BIEN** est équipé d'un{{ " " + bien.equipements.cheminee_type if bien.equipements.cheminee_type else " poêle ou d'une cheminée" }}{% if bien.equipements.cheminee_date_installation %} installé(e) {{ bien.equipements.cheminee_date_installation }}{% endif %}. Le **PROMETTANT** déclare qu'il est à ce jour en bon état de fonctionnement. La facture du dernier ramonage{% if bien.equipements.cheminee_date_ramonage %} (effectué le {{ bien.equipements.cheminee_date_ramonage | format_date }}){% endif %} sera transmise par le **PROMETTANT** au plus tard à la réitération des présentes.{% else %}Le **BIEN** n'est pas équipé de cheminée ni de poêle.{% endif %}
{% endif %}

{% if bien.equipements and bien.equipements.citerne_gaz is defined %}
**Citerne de gaz** - {% if bien.equipements.citerne_gaz %}Le **BIEN** est équipé d'une citerne de gaz{% if bien.equipements.citerne_gaz_propriete == "locative" %} en location auprès de {{ bien.equipements.citerne_gaz_fournisseur | default("son fournisseur") }}. Le contrat sera transféré au **BÉNÉFICIAIRE**{% else %} appartenant au **PROMETTANT**{% endif %}.{% else %}Le **PROMETTANT** déclare que l'immeuble n'est pas équipé d'une citerne de gaz.{% endif %}
{% endif %}

{% if bien.equipements and bien.equipements.cuve_fuel is defined %}
**Cuve à fuel** - {% if bien.equipements.cuve_fuel %}Le **BIEN** est équipé d'une cuve à fuel{% if bien.equipements.cuve_fuel_enterree %} enterrée{% endif %}{% if bien.equipements.cuve_fuel_capacite %} d'une capacité de {{ bien.equipements.cuve_fuel_capacite }} litres{% endif %}. Le **PROMETTANT** déclare que cette cuve est conforme à la réglementation en vigueur.{% else %}Le **PROMETTANT** déclare que l'immeuble n'est pas équipé d'une cuve à fuel.{% endif %}
{% endif %}

{% if bien.equipements and bien.equipements.cuve_enterree is defined %}
**Cuve enterrée** - {% if bien.equipements.cuve_enterree %}Le **BIEN** est équipé d'une cuve enterrée{% if bien.equipements.cuve_enterree_usage %} utilisée pour {{ bien.equipements.cuve_enterree_usage }}{% endif %}. Le **PROMETTANT** déclare que cette cuve est conforme à la réglementation en vigueur et qu'elle a fait l'objet des contrôles obligatoires.{% else %}Le **PROMETTANT** déclare que l'immeuble n'est pas équipé d'une cuve enterrée.{% endif %}
{% endif %}

{% if bien.equipements and bien.equipements.ancienne_cuve is defined %}
**Ancienne cuve** - {% if bien.equipements.ancienne_cuve %}Le **PROMETTANT** déclare que l'immeuble est équipé d'une ancienne cuve enterrée{% if bien.equipements.ancienne_cuve_neutralisee %}, qui a été neutralisée conformément à la réglementation{% else %}. Le **PROMETTANT** s'engage à procéder à sa neutralisation avant la réitération{% endif %}.{% else %}Le **PROMETTANT** déclare que l'immeuble n'est pas équipé d'une ancienne cuve enterrée sur le terrain.{% endif %}
{% endif %}

{% if bien.equipements and bien.equipements.panneaux_photovoltaiques is defined %}
**Panneaux photovoltaïques** - {% if bien.equipements.panneaux_photovoltaiques %}Le **BIEN** est équipé de panneaux photovoltaïques{% if bien.equipements.pv_puissance %} d'une puissance de {{ bien.equipements.pv_puissance }}{% endif %}{% if bien.equipements.pv_contrat_rachat %}, avec un contrat de rachat d'électricité auprès de {{ bien.equipements.pv_fournisseur | default("EDF OA") }}{% endif %}. Le **PROMETTANT** transmettra au **BÉNÉFICIAIRE** l'ensemble des documents relatifs à cette installation.{% else %}Le **PROMETTANT** déclare que le **BIEN** n'est pas équipé de panneaux photovoltaïques.{% endif %}
{% endif %}

{% if bien.equipements and bien.equipements.recuperation_eaux is defined %}
**Dispositif de récupération des eaux de pluie** - {% if bien.equipements.recuperation_eaux %}Le **BIEN** est équipé d'un système de récupération et de distribution d'eaux de pluie{% if bien.equipements.recuperation_eaux_description %} ({{ bien.equipements.recuperation_eaux_description }}){% endif %}. Le **PROMETTANT** déclare que cette installation est conforme à l'arrêté du 21 août 2008 et a fait l'objet des déclarations obligatoires en mairie.{% else %}Le **PROMETTANT** déclare que le **BIEN** n'est pas équipé d'un système de récupération et de distribution d'eaux de pluie.{% endif %}
{% endif %}

{% if bien.equipements and bien.equipements.puits_forages is defined %}
**Puits et forages domestiques** - {% if bien.equipements.puits_forages %}Le **PROMETTANT** déclare que l'immeuble est équipé d'un {{ bien.equipements.puits_forages_type | default("puits") }}{% if bien.equipements.puits_forages_usage %} utilisé pour {{ bien.equipements.puits_forages_usage }}{% endif %}. Les parties sont informées que la loi sur l'eau et les milieux aquatiques fait obligation de déclarer en mairie les puits et forages domestiques existants. Est assimilé à un usage domestique de l'eau tout prélèvement inférieur ou égal à 1 000 m³ d'eau par an. Les services de distribution d'eau potable ont la possibilité de contrôler l'ouvrage de prélèvement, les réseaux intérieurs et les ouvrages de récupération des eaux de pluie.{% else %}Le **PROMETTANT** déclare que l'immeuble n'est pas équipé de puits ou de forage domestique.{% endif %}
{% endif %}

{% if bien.equipements and bien.equipements.piscine is defined %}
**Sécurité des piscines** - {% if bien.equipements.piscine %}Les parties déclarent qu'il existe une piscine{% if bien.equipements.piscine_type %} ({{ bien.equipements.piscine_type }}){% endif %}. Elles sont informées des dispositions de l'article L 134-10 du Code de la construction et de l'habitation, aux termes desquelles les piscines enterrées non closes privatives, neuves ou existantes, à usage individuel ou à usage collectif, sont pourvues d'au moins un des dispositifs de sécurité normalisés visant à prévenir le risque de noyade : barrière de protection (NF P 90-306), couverture de sécurité (NF P 90-308), abri (NF P 90-309) ou alarme (NF P 90-307). {% if bien.equipements.piscine_dispositif_securite %}Le dispositif en place est : {{ bien.equipements.piscine_dispositif_securite }}.{% endif %}{% else %}Les parties déclarent qu'il n'existe pas de piscine.{% endif %}
{% endif %}

## Règlementation - Ascenseurs

{% if copropriete and copropriete.ascenseurs %}
L'immeuble est pourvu d'un ou plusieurs ascenseurs soumis aux dispositions du décret n° 2004-964 du 9 septembre 2004 et de ses textes d'application.

**Sécurité** - Le **PROMETTANT** déclare que les travaux de mise en sécurité prescrits par la réglementation ont été réalisés ou sont programmés conformément aux échéances réglementaires.

**Contrôle technique** - L'ascenseur fait l'objet des contrôles techniques périodiques obligatoires conformément aux articles R. 125-2-1 et suivants du Code de la construction et de l'habitation. Le dernier contrôle technique a été effectué{% if copropriete.ascenseurs.date_dernier_controle %} le {{ copropriete.ascenseurs.date_dernier_controle | format_date }}{% endif %}.

**Contrat d'entretien et de maintenance** - L'ascenseur fait l'objet d'un contrat d'entretien conformément aux articles R. 125-2 et suivants du Code de la construction et de l'habitation{% if copropriete.ascenseurs.prestataire_entretien %}, conclu avec {{ copropriete.ascenseurs.prestataire_entretien }}{% endif %}.
{% else %}
L'immeuble n'est pas pourvu d'ascenseur. Sans objet pour la sécurité, le contrôle technique et le contrat d'entretien.
{% endif %}

## Domicile fiscal

{% if promettants %}
{% for promettant in promettants %}
{% if promettant.resident_fiscal %}
{{ promettant.civilite }} {{ promettant.nom }} {{ promettant.prenoms }} déclare avoir son domicile fiscal en France.
{% else %}
{{ promettant.civilite }} {{ promettant.nom }} {{ promettant.prenoms }} déclare avoir son domicile fiscal hors de France.
{% endif %}
{% endfor %}
{% endif %}

## Reprise d'engagement par les ayants droit du promettant

En cas de décès du **PROMETTANT** avant la réitération de la vente par acte authentique, ses ayants droit seront tenus de reprendre l'engagement résultant de la présente promesse.

La présente promesse conservera tous ses effets à l'égard des héritiers et ayants droit du **PROMETTANT**, lesquels seront tenus solidairement de toutes les obligations qui en découlent.

{# ============================================================================
   SECTIONS ENRICHIES - TRAMES D, E, F (v1.6.0 - Janvier 2026)
   Ajout de sections pour maisons, terrains et construction
   ============================================================================ #}

{% if bien.acces %}
## Accès au bien

Le **PROMETTANT** déclare que l'accès au **BIEN** vendu s'effectue {{ bien.acces.description | default("par la voie publique") }}.

{% if bien.acces.servitude_passage %}
Cet accès s'effectue par le biais d'une servitude de passage{% if bien.acces.servitude_passage_details %} {{ bien.acces.servitude_passage_details }}{% endif %}.
{% endif %}

{% if bien.acces.second_acces %}
Le **PROMETTANT** déclare avoir également créé un second accès {{ bien.acces.second_acces_description }}.
{% endif %}

Le **BÉNÉFICIAIRE** atteste avoir pu vérifier les modalités d'accès.
{% endif %}

{% if bien.division_cadastrale %}
## Division cadastrale à effectuer

{% if bien.division_cadastrale.a_effectuer %}
Il est ici précisé que la parcelle ci-dessus cadastrée section {{ bien.division_cadastrale.section }} numéro {{ bien.division_cadastrale.numero }} est d'une contenance totale de {{ bien.division_cadastrale.contenance_totale }}. La vente ne porte que sur une partie de cette parcelle d'une contenance de {{ bien.division_cadastrale.contenance_vendue }}.

Un document modificatif du parcellaire sera établi aux frais du **PROMETTANT** par tout géomètre-expert de son choix. Cette division s'effectuera conformément au plan établi et approuvé par les parties, lequel est annexé.
{% endif %}

{% if bien.division_cadastrale.declaration_prealable %}
## DÉCLARATION PRÉALABLE DE DIVISION CADASTRALE

Conformément aux dispositions de l'article L 442-3 du Code de l'Urbanisme, la division cadastrale a fait l'objet d'une déclaration préalable.

{% if bien.division_cadastrale.arrete_non_opposition %}
Un arrêté de non-opposition à cette déclaration préalable a été délivré par {{ bien.division_cadastrale.autorite_delivrance | default("la Mairie") }}, le {{ bien.division_cadastrale.date_arrete | format_date }}.

Le **PROMETTANT** déclare avoir procédé à l'affichage dudit arrêté de non-opposition à déclaration préalable sur le **BIEN**, objet des présentes.
{% endif %}

Le **PROMETTANT** déclare, sous son entière responsabilité, que cet arrêté de non-opposition à déclaration préalable n'a fait l'objet d'aucun retrait administratif ni d'aucun recours de tiers.
{% endif %}
{% endif %}

{% if bien.bornage %}
## OBLIGATION D'INFORMATION SUR LE BORNAGE

{% if bien.bornage.a_effectuer %}
En application des dispositions de l'article L 115-4 du Code de l'urbanisme, la destination envisagée sur le terrain objet des présentes nécessite un bornage qui sera réalisé avant la réitération de la vente. Les frais de bornage seront à la charge {{ bien.bornage.frais_charge | default("du PROMETTANT") }}.
{% else %}
Le terrain a fait l'objet d'un bornage{% if bien.bornage.date %} en date du {{ bien.bornage.date | format_date }}{% endif %}{% if bien.bornage.geometre %} par {{ bien.bornage.geometre }}{% endif %}.
{% endif %}
{% endif %}

{% if bien.constitution_servitudes %}
## CONSTITUTION DE SERVITUDES

Sous réserve de la constatation authentique de la réalisation des présentes, il est convenu entre les parties ce qui suit :

{% for servitude in bien.constitution_servitudes %}
**{{ servitude.type | default("Servitude") }}**

{% if servitude.description %}
{{ servitude.description }}
{% endif %}

{% if servitude.fonds_servant %}
Fonds servant : {{ servitude.fonds_servant }}
{% endif %}
{% if servitude.fonds_dominant %}
Fonds dominant : {{ servitude.fonds_dominant }}
{% endif %}

{% endfor %}
{% endif %}

{% if evenement_sanitaire %}
## Prise en compte d'un évènement sanitaire

Les parties attestent être instruites de l'impact d'une crise sanitaire à l'image de celle de la Covid-19 en ce qui concerne l'éventuelle paralysie de l'activité juridique et administrative pouvant résulter de mesures d'urgence sanitaire.

Si une telle crise venait à se reproduire pendant le délai de réalisation des présentes, et que des dispositions d'origine légale ou réglementaire venaient à suspendre, prolonger, reporter ou aménager les délais contractuels et/ou légaux applicables aux présentes, les parties conviennent que les délais seront ajustés en conséquence.
{% endif %}

{% if cout_operation %}
## COÛT DE L'OPÉRATION ET FINANCEMENT PRÉVISIONNEL

À titre indicatif, le coût de l'opération et le financement prévisionnel sont les suivants :

| | |
| :---- | ----: |
| Prix de vente | {{ prix.montant | format_nombre }} {{ prix.devise | default("EUR") }} |
{% if cout_operation.frais_notaire %}| Frais de notaire estimés | {{ cout_operation.frais_notaire | format_nombre }} {{ prix.devise | default("EUR") }} |{% endif %}
{% if cout_operation.frais_agence %}| Frais d'agence | {{ cout_operation.frais_agence | format_nombre }} {{ prix.devise | default("EUR") }} |{% endif %}
{% if cout_operation.frais_pret %}| Frais de prêt estimés | {{ cout_operation.frais_pret | format_nombre }} {{ prix.devise | default("EUR") }} |{% endif %}
| **Coût total estimé** | **{{ cout_operation.total | format_nombre }} {{ prix.devise | default("EUR") }}** |
| | |
| **FINANCEMENT** | |
{% if cout_operation.apport_personnel %}| Apport personnel | {{ cout_operation.apport_personnel | format_nombre }} {{ prix.devise | default("EUR") }} |{% endif %}
{% if cout_operation.fonds_empruntes %}| Fonds empruntés | {{ cout_operation.fonds_empruntes | format_nombre }} {{ prix.devise | default("EUR") }} |{% endif %}
{% endif %}

{% if construction %}
## Dispositions relatives à la construction

{% if construction.absence_certification_conformite %}
**Absence de certification de la conformité** - La construction de l'immeuble n'a pas fait l'objet de la délivrance ni d'un certificat de conformité ni d'une attestation de non-contestation de la conformité. Le propriétaire déclare avoir fait édifier l'immeuble en respectant la totalité des prescriptions édictées par les autorisations d'urbanisme. Les parties sont averties des sanctions résultant de l'absence de certificat de conformité (sanctions pénales, civiles et administratives conformément à l'article L 480-14 du Code de l'urbanisme).
{% endif %}

{% if construction.assurances_rc_decennale %}
**Assurances de responsabilité civile décennale des entreprises** - Le **BÉNÉFICIAIRE** bénéficie de la garantie accordée dans le cadre de la responsabilité décennale prévue par l'article 1792 du Code civil. La garantie décennale est obligatoire pour toutes les entreprises impliquées dans la réalisation de gros ouvrages ou d'éléments d'équipement indissociables. Elle est due dans deux cas : un vice compromet la solidité de l'ouvrage ou le rend impropre à sa destination (articles 1792 et 1792-1 du Code civil) ; un vice affecte un élément d'équipement indissociable de l'ouvrage (article 1792-2 du Code civil). Le délai de garantie expire dix ans après la réception de l'ouvrage.
{% endif %}

{% if construction.etude_geotechnique %}
**Étude géotechnique** - Conformément aux articles L 132-5 et suivants du Code de la construction et de l'habitation, {% if construction.etude_geotechnique.fournie %}une étude géotechnique préalable est fournie par le **PROMETTANT** et annexée aux présentes.{% elif construction.etude_geotechnique.non_requise %}la parcelle de terrain à bâtir ne se trouvant pas dans une zone moyenne ou forte exposée au phénomène de mouvement de terrain différentiel lié au retrait-gonflement des argiles, la fourniture de l'étude géotechnique préalable n'est pas requise.{% else %}en cas de vente d'un terrain non bâti constructible, une étude géotechnique préalable devra être fournie par le vendeur et annexée à l'acte de vente.{% endif %}
{% endif %}

{% if construction.raccordement_reseaux %}
**Raccordement aux réseaux** - Les frais de raccordement aux réseaux de distribution, notamment d'eau{% if construction.raccordement_reseaux.eau %} (existant){% endif %} et d'électricité{% if construction.raccordement_reseaux.electricite %} (existant){% endif %}, de la construction à édifier seront entièrement à la charge du **BÉNÉFICIAIRE**.
{% endif %}

{% if construction.assurance_construction %}
**Assurance-construction** - Le **BÉNÉFICIAIRE** reconnaît avoir été averti par le notaire soussigné de l'obligation qui est faite par les dispositions de l'article L 242-1 du Code des assurances de souscrire une assurance « dommages-ouvrage » avant l'ouverture du chantier. Il devra effectuer toutes les démarches nécessaires pour bénéficier de ce type d'assurance et se faire remettre par la compagnie un justificatif de cette assurance.
{% endif %}

{% if construction.diuo %}
**Dossier d'intervention ultérieure sur l'ouvrage** - Le notaire soussigné a informé le **BÉNÉFICIAIRE** qu'un dossier d'intervention ultérieure sur l'ouvrage (DIUO) tel que visé par l'article R. 4532-95 du Code du travail doit être constitué pour tout ouvrage de construction et remis par le constructeur.{% if construction.diuo.non_obligatoire %} Toutefois, ce dossier n'est pas obligatoire lorsque la construction est affectée à l'usage personnel du maître d'ouvrage.{% endif %}
{% endif %}

{% if construction.conservation_factures %}
**Conservation des factures des travaux** - Le notaire rappelle au **BÉNÉFICIAIRE** la nécessité de conserver les factures des travaux et achats de matériaux, ainsi que les plans de l'immeuble tel que construit, le DIUO, les procès-verbaux de réception et les attestations d'assurance des constructeurs, afin de pouvoir les transmettre aux propriétaires successifs de l'immeuble.
{% endif %}

{% if construction.contrat_construction_maison %}
**Contrat de construction d'une maison individuelle** - Le rédacteur des présentes rappelle au **BÉNÉFICIAIRE** l'obligation faite à son constructeur de lui remettre lors de la signature du contrat une notice descriptive conforme à un modèle type, ainsi qu'une notice d'information destinée à l'informer de ses droits et obligations en application de la loi n° 90-1129 du 19 décembre 1990.
{% endif %}
{% endif %}

{% if diagnostics_environnementaux_detail %}
## Diagnostics environnementaux détaillés

{% if diagnostics_environnementaux_detail.ppr_naturels is defined %}
**Plan de prévention des risques naturels** - {% if diagnostics_environnementaux_detail.ppr_naturels.existe %}L'immeuble est situé dans le périmètre d'un plan de prévention des risques naturels approuvé{% if diagnostics_environnementaux_detail.ppr_naturels.date_approbation %} en date du {{ diagnostics_environnementaux_detail.ppr_naturels.date_approbation | format_date }}{% endif %}. Le risque naturel pris en considération est lié à : {{ diagnostics_environnementaux_detail.ppr_naturels.risque | default("inondation") }}.{% if diagnostics_environnementaux_detail.ppr_naturels.prescriptions_travaux %} L'immeuble est concerné par des prescriptions de travaux dans le règlement de ce plan.{% endif %}{% else %}L'immeuble n'est pas situé dans le périmètre d'un plan de prévention des risques naturels.{% endif %}
{% endif %}

{% if diagnostics_environnementaux_detail.ppr_miniers is defined %}
**Plan de prévention des risques miniers** - {% if diagnostics_environnementaux_detail.ppr_miniers.existe %}L'immeuble est situé dans le périmètre d'un plan de prévention des risques miniers.{% else %}L'immeuble n'est pas situé dans le périmètre d'un plan de prévention des risques miniers.{% endif %}
{% endif %}

{% if diagnostics_environnementaux_detail.ppr_technologiques is defined %}
**Plan de prévention des risques technologiques** - {% if diagnostics_environnementaux_detail.ppr_technologiques.existe %}L'immeuble est situé dans le périmètre d'un plan de prévention des risques technologiques.{% else %}L'immeuble n'est pas situé dans le périmètre d'un plan de prévention des risques technologiques.{% endif %}
{% endif %}

{% if diagnostics_environnementaux_detail.sismicite is defined %}
**Sismicité** - L'immeuble est situé dans une zone {{ diagnostics_environnementaux_detail.sismicite.zone | default("1") }} ({{ diagnostics_environnementaux_detail.sismicite.niveau | default("très faible") }}).
{% endif %}

{% if diagnostics_environnementaux_detail.secteur_information_sols is defined %}
**Secteur d'information sur les sols** - {% if diagnostics_environnementaux_detail.secteur_information_sols.existe %}L'immeuble est situé dans un secteur d'information sur les sols en application de l'article L. 125-6 du Code de l'environnement.{% else %}L'immeuble n'est pas situé dans un secteur d'information sur les sols.{% endif %}
{% endif %}

{% if diagnostics_environnementaux_detail.alea_argiles is defined %}
**Aléa – Retrait gonflement des argiles** - L'immeuble est concerné par la cartographie des zones exposées au phénomène de mouvement de terrain différentiel consécutif à la sécheresse et à la réhydratation des sols argileux. La carte identifie quatre catégories : exposition forte, moyenne, faible et résiduelle. En l'espèce, l'immeuble se trouve dans une zone d'exposition {{ diagnostics_environnementaux_detail.alea_argiles.niveau | default("faible") }}.
{% endif %}
{% endif %}

{% if situation_environnementale_detail %}
{% if situation_environnementale_detail.responsabilite %}
## Responsabilité environnementale

Toute atteinte non négligeable aux éléments ou aux fonctions des écosystèmes ou aux bénéfices collectifs tirés par l'homme de l'environnement est susceptible d'engager la responsabilité environnementale du propriétaire conformément aux dispositions des articles L 160-1 et suivants du Code de l'environnement.
{% endif %}

{% if situation_environnementale_detail.elimination_dechets %}
## Obligation générale d'élimination des déchets

Le propriétaire doit supporter le coût de la gestion jusqu'à l'élimination des déchets, qu'ils soient les siens, ceux de ses locataires ou ceux des précédents occupants. Conformément à l'article L 541-1-1 du Code de l'environnement, le déchet désigne « toute substance ou tout objet, ou plus généralement tout bien meuble, dont le détenteur se défait ou dont il a l'intention ou l'obligation de se défaire ».

Selon les dispositions de l'article L 541-2 du Code de l'environnement, tout producteur ou détenteur de déchets est tenu d'en assurer ou d'en faire assurer la gestion. L'élimination des déchets comporte les opérations de collecte, transport, stockage, tri et traitement nécessaires à la récupération des éléments et matériaux réutilisables ou de l'énergie, ainsi que le dépôt ou le rejet dans le milieu naturel de tous les autres produits dans des conditions propres à éviter les nuisances.
{% endif %}
{% endif %}

{% if taxe_terrain_constructible %}
## Taxe sur la cession de terrain devenu constructible

{% if taxe_terrain_constructible.article_1529 is defined %}
**Taxe prévue par l'article 1529 du Code général des impôts** - {% if taxe_terrain_constructible.article_1529.due %}Conformément aux dispositions de l'article 1529 du Code général des impôts, une taxe forfaitaire est due sur la cession de terrains nus devenus constructibles.{% else %}Cette taxe n'est pas due, le terrain étant classé en zone constructible depuis plus de dix-huit ans.{% endif %}
{% endif %}

{% if taxe_terrain_constructible.article_1605_nonies is defined %}
**Taxe prévue par l'article 1605 nonies du Code général des impôts** - {% if taxe_terrain_constructible.article_1605_nonies.due %}La taxe prévue par l'article 1605 nonies du Code général des impôts est applicable à la présente cession.{% else %}Le terrain étant classé en zone constructible depuis plus de dix-huit ans, la taxe prévue par l'article 1605 nonies du Code général des impôts n'est pas applicable.{% endif %}
{% endif %}
{% endif %}

{% if anomalies_diagnostics %}
## Information du bénéficiaire sur les anomalies révélées par les diagnostics

Le **BÉNÉFICIAIRE** déclare avoir pris connaissance, préalablement à la signature, des anomalies révélées par les diagnostics techniques immobiliers obligatoires joints aux présentes.

Le **BÉNÉFICIAIRE** déclare avoir été informé par le notaire soussigné, préalablement à la signature des présentes, notamment :
* des conséquences de ces anomalies au regard du contrat d'assurance qui sera souscrit pour la couverture de l'immeuble en question ;
* de la nécessité, soit de faire effectuer par un professionnel compétent les travaux permettant de remédier à ces anomalies, soit d'en aviser la compagnie d'assurance préalablement à la signature du contrat d'assurance ;
* qu'à défaut, le **BÉNÉFICIAIRE** pourrait perdre tout droit à garantie et toute indemnité en cas de sinistre même sans rapport avec les anomalies relevées.
{% endif %}

{# ============================================================================
   SECTIONS AVANCÉES PROMESSE DE VENTE (v1.5.1)
   Ajout de sections détaillées pour améliorer la conformité
   ============================================================================ #}

{# Condition suspensive - Vente d'un bien préalable (version détaillée) #}
{% if conditions_suspensives and conditions_suspensives.vente_bien_prealable and conditions_suspensives.vente_bien_prealable.existe %}
{% include 'sections/section_condition_vente_prealable.md' %}
{% endif %}

{# Faculté de substitution - Version complète #}
{% if faculte_substitution is defined %}
{% include 'sections/section_faculte_substitution.md' %}
{% endif %}

{# Indemnité d'immobilisation - Version détaillée avec tous les cas #}
{% if indemnite_immobilisation and indemnite_immobilisation.version_detaillee %}
{% include 'sections/section_indemnite_immobilisation_detaillee.md' %}
{% endif %}

{# Prorogation de la promesse #}
{% if delais and delais.prorogation %}
{% include 'sections/section_prorogation.md' %}
{% endif %}

{# Clause pénale réciproque #}
{% if clause_penale and clause_penale.applicable %}
{% include 'sections/section_clause_penale.md' %}
{% endif %}

{# ============================================================================
   INCLUSION DE LA PARTIE DÉVELOPPÉE COMMUNE
   Contient : garanties, diagnostics, copropriété, fiscalité, origine, etc.
   ============================================================================ #}

{% include 'sections/partie_developpee.md' %}
