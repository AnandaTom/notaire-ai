## Garantie contre le risque d'éviction

### Principe de la garantie

Conformément aux dispositions des articles 1626 et suivants du Code civil, le VENDEUR est tenu de garantir l'ACQUEREUR contre l'éviction qu'il pourrait souffrir dans la propriété ou la jouissance de la chose vendue.

La garantie d'éviction comprend deux obligations principales :
1. La garantie du fait personnel du vendeur
2. La garantie du fait des tiers

### Garantie du fait personnel du vendeur

Le VENDEUR s'oblige à ne rien faire qui puisse troubler l'ACQUEREUR dans la propriété ou la jouissance du bien vendu.

En conséquence, le VENDEUR s'interdit :
- De revendiquer tout droit ou servitude sur le bien vendu
- De céder à un tiers des droits qui diminueraient la jouissance de l'ACQUEREUR
- De contester la vente ou d'exercer une action en rescision ou en nullité

### Garantie du fait des tiers

Le VENDEUR garantit l'ACQUEREUR contre toute éviction procédant du fait d'un tiers.

Cette garantie couvre :
- Les revendications en propriété formées par des tiers
- Les servitudes non déclarées qui diminuent la valeur ou l'usage du bien
- Les vices du titre qui rendent impossible la propriété paisible

{% if garanties.eviction %}

### Étendue de la garantie

{% if garanties.eviction.etendue == 'totale' %}
La garantie d'éviction est consentie dans toute son étendue légale, sans limitation ni restriction.
{% elif garanties.eviction.etendue == 'partielle' %}
La garantie d'éviction est limitée aux cas suivants : <<<VAR_START>>>{{ garanties.eviction.limitations }}<<<VAR_END>>>.
{% elif garanties.eviction.etendue == 'supprimee' %}
Les parties conviennent expressément, en application de l'article 1628 du Code civil, de supprimer la garantie d'éviction.

L'ACQUEREUR reconnaît avoir été informé de la portée de cette clause et en accepte les conséquences.
{% endif %}

{% if garanties.eviction.exceptions %}
### Exceptions à la garantie

Le VENDEUR ne sera pas tenu de garantir l'éviction dans les cas suivants :
{% for exception in garanties.eviction.exceptions %}
- {{ exception }}
{% endfor %}
{% endif %}

{% endif %}

### Conséquences de l'éviction

En cas d'éviction totale, conformément à l'article 1629 du Code civil, le VENDEUR sera tenu de restituer à l'ACQUEREUR :
1. Le prix de la vente
2. Les frais et loyaux coûts du contrat
3. Les frais de réparations ou d'améliorations qui ont augmenté la valeur du bien
4. Des dommages-intérêts pour le préjudice subi

En cas d'éviction partielle, l'ACQUEREUR pourra choisir entre :
- La résolution de la vente si la partie évincée est substantielle
- Une réduction du prix proportionnelle à la partie évincée

## Garantie de jouissance

### Obligation de délivrance conforme

Conformément aux articles 1603 et suivants du Code civil, le VENDEUR est tenu de délivrer à l'ACQUEREUR un bien conforme à la description qui en a été faite et exempt de vices cachés.

### Garantie de jouissance paisible

Le VENDEUR garantit à l'ACQUEREUR la jouissance paisible et utile du bien vendu.

Cette garantie comprend :

#### 1. Absence de troubles de droit

Le VENDEUR garantit l'absence de :
- Servitudes non déclarées qui diminueraient la jouissance du bien
- Droits réels détenus par des tiers (usufruit, usage, habitation non déclarés)
- Privilèges ou hypothèques non révélés

{% if garanties.jouissance and garanties.jouissance.servitudes_declarees %}
**Servitudes déclarées** :
{% for servitude in garanties.jouissance.servitudes_declarees %}
- {{ servitude.type }} : {{ servitude.description }}
  {% if servitude.titre %}- Titre : {{ servitude.titre }}{% endif %}
  {% if servitude.beneficiaire %}- Bénéficiaire : <<<VAR_START>>>{{ servitude.beneficiaire }}<<<VAR_END>>>{% endif %}
{% endfor %}

L'ACQUEREUR déclare avoir été informé de ces servitudes et les accepter.
{% endif %}

#### 2. Absence de troubles de fait

Le VENDEUR garantit l'absence de :
- Occupants sans droit ni titre
- Empiétements sur le bien vendu
- Nuisances anormales causées par le vendeur ou provenant de ses biens

{% if garanties.jouissance and garanties.jouissance.occupation %}
**État d'occupation** : <<<VAR_START>>>{{ garanties.jouissance.occupation.etat }}<<<VAR_END>>>

{% if garanties.jouissance.occupation.etat == 'occupe' %}
Le bien est actuellement occupé par : <<<VAR_START>>>{{ garanties.jouissance.occupation.occupant }}<<<VAR_END>>>

- Titre d'occupation : {{ garanties.jouissance.occupation.titre }}
{% if garanties.jouissance.occupation.bail %}
- Bail en cours : du <<<VAR_START>>>{{ garanties.jouissance.occupation.bail.date_debut | format_date }}<<<VAR_END>>> au <<<VAR_START>>>{{ garanties.jouissance.occupation.bail.date_fin | format_date }}<<<VAR_END>>>
- Loyer mensuel : <<<VAR_START>>>{{ garanties.jouissance.occupation.bail.loyer | format_nombre }}<<<VAR_END>>> EUR
{% endif %}

L'ACQUEREUR déclare avoir été informé de cette occupation et l'accepter.
{% else %}
Le bien est libre de toute occupation.
{% endif %}
{% endif %}

#### 3. Conformité aux règles d'urbanisme et de construction

Le VENDEUR garantit que le bien vendu est conforme aux règles d'urbanisme applicables et que toutes les autorisations nécessaires ont été obtenues.

{% if garanties.jouissance and garanties.jouissance.conformite %}
**Déclaration de conformité** :
{% if garanties.jouissance.conformite.urbanisme %}
- Conformité urbanisme : <<<VAR_START>>>{{ garanties.jouissance.conformite.urbanisme.statut }}<<<VAR_END>>>
  {% if garanties.jouissance.conformite.urbanisme.certificat %}Certificat de conformité du <<<VAR_START>>>{{ garanties.jouissance.conformite.urbanisme.date | format_date }}<<<VAR_END>>>{% endif %}
{% endif %}

{% if garanties.jouissance.conformite.construction %}
- Conformité construction : <<<VAR_START>>>{{ garanties.jouissance.conformite.construction.statut }}<<<VAR_END>>>
  {% if garanties.jouissance.conformite.construction.reception %}Procès-verbal de réception du <<<VAR_START>>>{{ garanties.jouissance.conformite.construction.date | format_date }}<<<VAR_END>>>{% endif %}
{% endif %}
{% endif %}

### Limitation de garantie

{% if garanties.jouissance and garanties.jouissance.limitations %}
Les parties conviennent des limitations suivantes à la garantie de jouissance :
{% for limitation in garanties.jouissance.limitations %}
- {{ limitation }}
{% endfor %}

L'ACQUEREUR reconnaît avoir été informé de ces limitations et en accepte les conséquences.
{% else %}
La garantie de jouissance est consentie sans limitation dans toute son étendue légale.
{% endif %}

## Garantie hypothécaire

### Purge des inscriptions

Le VENDEUR déclare que le bien vendu est, à sa connaissance, libre de toute inscription de privilège ou d'hypothèque, à l'exception de celles dont la mainlevée sera donnée lors de l'acte authentique de vente.

{% if garanties.hypotheque and garanties.hypotheque.inscriptions_existantes %}

### Inscriptions existantes

Les inscriptions suivantes grèvent actuellement le bien :

{% for inscription in garanties.hypotheque.inscriptions_existantes %}
#### Inscription n° {{ loop.index }}

- **Type** : {{ inscription.type }}
- **Bénéficiaire** : <<<VAR_START>>>{{ inscription.beneficiaire }}<<<VAR_END>>>
- **Montant** : <<<VAR_START>>>{{ inscription.montant | format_nombre }}<<<VAR_END>>> EUR
{% if inscription.date_inscription %}- **Date d'inscription** : <<<VAR_START>>>{{ inscription.date_inscription | format_date }}<<<VAR_END>>>{% endif %}
{% if inscription.publication %}- **Publication** : Service de <<<VAR_START>>>{{ inscription.publication.service }}<<<VAR_END>>>, volume <<<VAR_START>>>{{ inscription.publication.volume }}<<<VAR_END>>>, numéro <<<VAR_START>>>{{ inscription.publication.numero }}<<<VAR_END>>>{% endif %}

**Mainlevée** : {% if inscription.mainlevee %}Mainlevée consentie le <<<VAR_START>>>{{ inscription.mainlevee.date | format_date }}<<<VAR_END>>>{% else %}Sera consentie lors de la signature de l'acte authentique{% endif %}

{% endfor %}

{% endif %}

### Garantie du vendeur

Le VENDEUR garantit que toutes les inscriptions existantes seront radiées ou que mainlevée en sera donnée au plus tard lors de la signature de l'acte authentique de vente.

Le VENDEUR s'engage à fournir tous les documents nécessaires à l'obtention des mainlevées.

### Conséquences du défaut de mainlevée

À défaut de mainlevée des inscriptions à la date de signature de l'acte authentique, l'ACQUEREUR pourra :
- Soit exiger la résolution de la vente
- Soit accepter la vente sous réserve de la radiation ultérieure des inscriptions, avec consignation d'une somme suffisante pour en garantir le paiement

### Droit de suite

Conformément à l'article 2461 du Code civil, le créancier hypothécaire conserve un droit de suite sur le bien en cas de non-paiement de la dette garantie, même après la vente.

{% if garanties.hypotheque and garanties.hypotheque.purge_legale %}
### Purge légale des hypothèques

L'ACQUEREUR pourra, s'il le souhaite, procéder à la purge légale des hypothèques conformément aux dispositions des articles 2475 et suivants du Code civil.

Cette procédure permettra de libérer définitivement le bien de toute hypothèque antérieure à la vente.
{% endif %}

### Garantie nouvelle

{% if garanties.hypotheque and garanties.hypotheque.nouvelle_inscription %}
Pour garantir le remboursement du prêt consenti pour financer la présente acquisition, une nouvelle inscription {{ garanties.hypotheque.nouvelle_inscription.type }} sera prise sur le bien vendu.

- **Montant** : <<<VAR_START>>>{{ garanties.hypotheque.nouvelle_inscription.montant | format_nombre }}<<<VAR_END>>> EUR
- **Bénéficiaire** : <<<VAR_START>>>{{ garanties.hypotheque.nouvelle_inscription.beneficiaire }}<<<VAR_END>>>
- **Durée** : <<<VAR_START>>>{{ garanties.hypotheque.nouvelle_inscription.duree }}<<<VAR_END>>> ans
{% endif %}
