## Declarations fiscales du vendeur

### Identification fiscale

{% if declarations_fiscales and declarations_fiscales.vendeur %}

Le VENDEUR declare etre identifie aupres de l'administration fiscale sous le numero fiscal suivant : <<<VAR_START>>>{{ declarations_fiscales.vendeur.numero_fiscal }}<<<VAR_END>>>.

{% if declarations_fiscales.vendeur.domicile_fiscal %}
**Domicile fiscal** : <<<VAR_START>>>{{ declarations_fiscales.vendeur.domicile_fiscal }}<<<VAR_END>>>
{% endif %}

{% if declarations_fiscales.vendeur.resident_fiscal == false %}
Le VENDEUR declare ne pas etre resident fiscal francais.

{% if declarations_fiscales.vendeur.pays_residence %}
Pays de residence fiscale : <<<VAR_START>>>{{ declarations_fiscales.vendeur.pays_residence }}<<<VAR_END>>>
{% endif %}

En application des dispositions de l'article 244 bis A du Code general des impots, un prelevement sera effectue lors de la mutation.
{% endif %}

{% else %}
Le VENDEUR s'engage a communiquer son numero fiscal a l'office notarial avant la signature de l'acte authentique.
{% endif %}

### Situation au regard de l'impot sur le revenu

{% if declarations_fiscales and declarations_fiscales.impot_revenu %}

{% if declarations_fiscales.impot_revenu.regime %}
**Regime fiscal applicable** : <<<VAR_START>>>{{ declarations_fiscales.impot_revenu.regime }}<<<VAR_END>>>
{% endif %}

{% if declarations_fiscales.impot_revenu.revenus_fonciers %}
Le bien vendu a genere des revenus fonciers declares au titre de l'impot sur le revenu.

{% if declarations_fiscales.impot_revenu.revenus_fonciers.montant_annuel %}
Montant annuel declare : <<<VAR_START>>>{{ declarations_fiscales.impot_revenu.revenus_fonciers.montant_annuel | format_nombre }}<<<VAR_END>>> EUR
{% endif %}

{% if declarations_fiscales.impot_revenu.revenus_fonciers.regime_fiscal %}
Regime de declaration : <<<VAR_START>>>{{ declarations_fiscales.impot_revenu.revenus_fonciers.regime_fiscal }}<<<VAR_END>>> (micro-foncier ou regime reel)
{% endif %}
{% endif %}

{% if declarations_fiscales.impot_revenu.deficit_foncier %}
### Deficit foncier

Le VENDEUR declare avoir impute un deficit foncier sur son revenu global.

{% if declarations_fiscales.impot_revenu.deficit_foncier.montant %}
Montant du deficit impute : <<<VAR_START>>>{{ declarations_fiscales.impot_revenu.deficit_foncier.montant | format_nombre }}<<<VAR_END>>> EUR
{% endif %}

{% if declarations_fiscales.impot_revenu.deficit_foncier.annee %}
Annee d'imputation : <<<VAR_START>>>{{ declarations_fiscales.impot_revenu.deficit_foncier.annee }}<<<VAR_END>>>
{% endif %}

Le VENDEUR est informe que la vente du bien dans les trois ans suivant l'imputation du deficit peut entrainer la remise en cause de l'avantage fiscal obtenu, conformement a l'article 156-I-3 du Code general des impots.
{% endif %}

{% else %}
Le VENDEUR declare etre a jour de ses obligations declaratives au regard de l'impot sur le revenu.
{% endif %}

### Declaration de sincerite

Le VENDEUR declare sur l'honneur que les informations fiscales communiquees sont exactes et completes.

{% if declarations_fiscales and declarations_fiscales.attestation %}
Il certifie :
- Ne pas faire l'objet d'un controle fiscal en cours concernant le bien vendu
- Ne pas avoir connaissance de redressements fiscaux anterieurs lies a ce bien
{% if declarations_fiscales.attestation.controle_fiscal == true %}
**Exception** : Le VENDEUR declare faire l'objet d'un controle fiscal : <<<VAR_START>>>{{ declarations_fiscales.attestation.details_controle }}<<<VAR_END>>>
{% endif %}
{% endif %}

## TVA et droits de mutation

### Regime de TVA applicable

{% if tva %}

{% if tva.applicable %}
La presente mutation est soumise a la Taxe sur la Valeur Ajoutee (TVA).

**Fondement legal** : <<<VAR_START>>>{{ tva.fondement_legal | default("Article 257 du Code general des impots") }}<<<VAR_END>>>

{% if tva.taux %}
**Taux applicable** : <<<VAR_START>>>{{ tva.taux }}<<<VAR_END>>> %
{% endif %}

{% if tva.base_calcul %}
**Base de calcul** : <<<VAR_START>>>{{ tva.base_calcul | format_nombre }}<<<VAR_END>>> EUR
{% endif %}

{% if tva.montant %}
**Montant de la TVA** : <<<VAR_START>>>{{ tva.montant | format_nombre }}<<<VAR_END>>> EUR
{% endif %}

{% if tva.sur_marge %}
### TVA sur la marge

La TVA est calculee sur la marge conformement a l'article 268 du Code general des impots.

{% if tva.marge %}
- Prix de cession : <<<VAR_START>>>{{ tva.prix_cession | format_nombre }}<<<VAR_END>>> EUR
- Prix d'acquisition : <<<VAR_START>>>{{ tva.prix_acquisition | format_nombre }}<<<VAR_END>>> EUR
- **Marge taxable** : <<<VAR_START>>>{{ tva.marge | format_nombre }}<<<VAR_END>>> EUR
- **TVA due** : <<<VAR_START>>>{{ tva.montant_tva_marge | format_nombre }}<<<VAR_END>>> EUR
{% endif %}
{% endif %}

{% if tva.option_tva %}
### Option pour la TVA

Le VENDEUR a exerce l'option pour l'assujettissement a la TVA conformement a l'article 260-5 bis du Code general des impots.

{% if tva.option_tva.date %}
Date d'exercice de l'option : <<<VAR_START>>>{{ tva.option_tva.date }}<<<VAR_END>>>
{% endif %}
{% endif %}

{% if tva.engagement_acquereur %}
### Engagement de l'acquereur

L'ACQUEREUR s'engage a soumettre le bien a la TVA pendant une duree minimale de <<<VAR_START>>>{{ tva.engagement_acquereur.duree | default("20") }}<<<VAR_END>>> ans, conformement aux dispositions de l'article 284 du Code general des impots.

A defaut de respect de cet engagement, la TVA initialement deduite devra etre reversee au Tresor public.
{% endif %}

{% else %}
La presente mutation n'est pas soumise a la TVA.

Le bien releve du regime des droits de mutation a titre onereux (DMTO).
{% endif %}

{% else %}
Le regime de TVA applicable sera determine lors de l'etablissement de l'acte authentique en fonction de la qualite du vendeur et de la nature du bien.
{% endif %}

### Droits de mutation a titre onereux

{% if fiscalite and fiscalite.droits_mutation %}

{% if fiscalite.droits_mutation.taux_global %}
**Taux global applicable** : <<<VAR_START>>>{{ fiscalite.droits_mutation.taux_global }}<<<VAR_END>>> %
{% endif %}

{% if fiscalite.droits_mutation.decomposition %}
Decomposition des droits :
- Taxe departementale : <<<VAR_START>>>{{ fiscalite.droits_mutation.decomposition.departementale | default("4.50") }}<<<VAR_END>>> %
- Taxe communale : <<<VAR_START>>>{{ fiscalite.droits_mutation.decomposition.communale | default("1.20") }}<<<VAR_END>>> %
- Prelevement pour frais d'assiette et de recouvrement : <<<VAR_START>>>{{ fiscalite.droits_mutation.decomposition.frais_assiette | default("2.37") }}<<<VAR_END>>> % sur le droit departemental
{% endif %}

{% if fiscalite.droits_mutation.base_taxable %}
**Base taxable** : <<<VAR_START>>>{{ fiscalite.droits_mutation.base_taxable | format_nombre }}<<<VAR_END>>> EUR
{% endif %}

{% if fiscalite.droits_mutation.montant_droits %}
**Montant des droits** : <<<VAR_START>>>{{ fiscalite.droits_mutation.montant_droits | format_nombre }}<<<VAR_END>>> EUR
{% endif %}

{% if fiscalite.droits_mutation.exoneration %}
### Exoneration de droits de mutation

La presente mutation beneficie d'une exoneration de droits de mutation :

- **Fondement** : <<<VAR_START>>>{{ fiscalite.droits_mutation.exoneration.fondement }}<<<VAR_END>>>
- **Nature** : <<<VAR_START>>>{{ fiscalite.droits_mutation.exoneration.nature }}<<<VAR_END>>>
{% if fiscalite.droits_mutation.exoneration.montant_economie %}
- **Economie realisee** : <<<VAR_START>>>{{ fiscalite.droits_mutation.exoneration.montant_economie | format_nombre }}<<<VAR_END>>> EUR
{% endif %}
{% endif %}

{% else %}
Les droits de mutation seront calcules et percus par le service de la publicite fonciere lors de l'accomplissement des formalites.

Le taux de droit commun applicable dans le departement est generalement de **5,81%** (taux maximal).
{% endif %}

## Regime fiscal applicable

### Qualification fiscale de la mutation

{% if fiscalite %}

{% if fiscalite.qualification %}
La presente mutation est qualifiee fiscalement de : <<<VAR_START>>>{{ fiscalite.qualification }}<<<VAR_END>>>
{% endif %}

{% if fiscalite.regime %}
**Regime applicable** : <<<VAR_START>>>{{ fiscalite.regime }}<<<VAR_END>>>
{% endif %}

{% if fiscalite.textes_applicables %}
### Textes de reference

{% for texte in fiscalite.textes_applicables %}
- {{ texte }}
{% endfor %}
{% endif %}

{% if fiscalite.rescrit %}
### Rescrit fiscal

Un rescrit fiscal a ete obtenu aupres de l'administration concernant cette operation :

- **Reference** : <<<VAR_START>>>{{ fiscalite.rescrit.reference }}<<<VAR_END>>>
- **Date** : <<<VAR_START>>>{{ fiscalite.rescrit.date }}<<<VAR_END>>>
- **Objet** : <<<VAR_START>>>{{ fiscalite.rescrit.objet }}<<<VAR_END>>>
{% if fiscalite.rescrit.conclusion %}
- **Conclusion** : <<<VAR_START>>>{{ fiscalite.rescrit.conclusion }}<<<VAR_END>>>
{% endif %}
{% endif %}

{% else %}
Le regime fiscal applicable sera determine en fonction des caracteristiques de la mutation et de la qualite des parties.
{% endif %}

### Obligations declaratives

{% if declarations_fiscales and declarations_fiscales.obligations %}

Les parties sont informees des obligations declaratives suivantes :

{% for obligation in declarations_fiscales.obligations %}
- **{{ obligation.intitule }}** : {{ obligation.description }}
  {% if obligation.delai %}Delai : <<<VAR_START>>>{{ obligation.delai }}<<<VAR_END>>>{% endif %}
  {% if obligation.formulaire %}Formulaire : <<<VAR_START>>>{{ obligation.formulaire }}<<<VAR_END>>>{% endif %}
{% endfor %}

{% else %}
Les parties sont informees qu'elles devront respecter les obligations declaratives prevues par la legislation fiscale en vigueur.

Le notaire soussigne effectuera les formalites d'enregistrement et de publication aupres du service de la publicite fonciere.
{% endif %}

### Frais d'acte

{% if fiscalite and fiscalite.frais_acte %}
Les frais d'acte sont a la charge de <<<VAR_START>>>{{ fiscalite.frais_acte.debiteur | default("l'ACQUEREUR") }}<<<VAR_END>>>, conformement a l'usage.

{% if fiscalite.frais_acte.estimation %}
**Estimation des frais** : <<<VAR_START>>>{{ fiscalite.frais_acte.estimation | format_nombre }}<<<VAR_END>>> EUR (sous reserve des calculs definitifs)

Decomposition :
{% if fiscalite.frais_acte.droits_mutation %}
- Droits de mutation : <<<VAR_START>>>{{ fiscalite.frais_acte.droits_mutation | format_nombre }}<<<VAR_END>>> EUR
{% endif %}
{% if fiscalite.frais_acte.emoluments %}
- Emoluments du notaire : <<<VAR_START>>>{{ fiscalite.frais_acte.emoluments | format_nombre }}<<<VAR_END>>> EUR
{% endif %}
{% if fiscalite.frais_acte.debours %}
- Debours : <<<VAR_START>>>{{ fiscalite.frais_acte.debours | format_nombre }}<<<VAR_END>>> EUR
{% endif %}
{% if fiscalite.frais_acte.contribution_securite %}
- Contribution de securite immobiliere : <<<VAR_START>>>{{ fiscalite.frais_acte.contribution_securite | format_nombre }}<<<VAR_END>>> EUR
{% endif %}
{% endif %}
{% else %}
Les frais d'acte sont a la charge de l'ACQUEREUR, conformement a l'usage.

Le montant definitif des frais sera communique par l'office notarial apres etablissement du decompte.
{% endif %}

## Plus-values immobilieres

### Regime d'imposition des plus-values

{% if plus_value %}

{% if plus_value.exoneration %}
### Exoneration de plus-value

La plus-value realisee lors de la presente vente est exoneree d'imposition.

**Motif d'exoneration** : <<<VAR_START>>>{{ plus_value.exoneration.motif }}<<<VAR_END>>>

{% if plus_value.exoneration.motif == 'residence_principale' %}
Conformement aux dispositions du 1 du II de l'article 150 U du Code general des impots, la plus-value realisee lors de la cession de la residence principale du cedant est exoneree d'impot sur le revenu et de prelevements sociaux.

Le VENDEUR declare sur l'honneur que le bien vendu constitue sa residence principale au jour de la cession.
{% elif plus_value.exoneration.motif == 'detention_22_ans' %}
Conformement aux dispositions de l'article 150 VC du Code general des impots, la plus-value est totalement exoneree d'impot sur le revenu apres 22 ans de detention.

Duree de detention : <<<VAR_START>>>{{ plus_value.duree_detention }}<<<VAR_END>>> ans
{% elif plus_value.exoneration.motif == 'detention_30_ans' %}
Conformement aux dispositions de l'article 150 VC du Code general des impots, la plus-value est totalement exoneree de prelevements sociaux apres 30 ans de detention.

Duree de detention : <<<VAR_START>>>{{ plus_value.duree_detention }}<<<VAR_END>>> ans
{% elif plus_value.exoneration.motif == 'premiere_cession' %}
Conformement aux dispositions du 1 bis du II de l'article 150 U du Code general des impots, le VENDEUR beneficie de l'exoneration accordee lors de la premiere cession d'un logement autre que la residence principale sous condition de remploi.
{% elif plus_value.exoneration.motif == 'prix_inferieur_15000' %}
Conformement aux dispositions du III de l'article 150 U du Code general des impots, les cessions dont le prix est inferieur ou egal a 15 000 EUR sont exonerees.
{% else %}
Fondement : <<<VAR_START>>>{{ plus_value.exoneration.fondement }}<<<VAR_END>>>
{% endif %}

{% else %}
### Calcul de la plus-value imposable

{% if plus_value.prix_acquisition %}
**Prix d'acquisition** : <<<VAR_START>>>{{ plus_value.prix_acquisition | format_nombre }}<<<VAR_END>>> EUR
{% endif %}

{% if plus_value.date_acquisition %}
**Date d'acquisition** : <<<VAR_START>>>{{ plus_value.date_acquisition }}<<<VAR_END>>>
{% endif %}

{% if plus_value.duree_detention %}
**Duree de detention** : <<<VAR_START>>>{{ plus_value.duree_detention }}<<<VAR_END>>> ans
{% endif %}

{% if plus_value.frais_acquisition %}
**Frais d'acquisition** :
{% if plus_value.frais_acquisition.mode == 'forfait' %}
Majoration forfaitaire de 7,5% : <<<VAR_START>>>{{ plus_value.frais_acquisition.montant | format_nombre }}<<<VAR_END>>> EUR
{% else %}
Frais reels justifies : <<<VAR_START>>>{{ plus_value.frais_acquisition.montant | format_nombre }}<<<VAR_END>>> EUR
{% endif %}
{% endif %}

{% if plus_value.travaux %}
**Travaux** :
{% if plus_value.travaux.mode == 'forfait' %}
Majoration forfaitaire de 15% (detention > 5 ans) : <<<VAR_START>>>{{ plus_value.travaux.montant | format_nombre }}<<<VAR_END>>> EUR
{% else %}
Travaux reels justifies : <<<VAR_START>>>{{ plus_value.travaux.montant | format_nombre }}<<<VAR_END>>> EUR
{% endif %}
{% endif %}

{% if plus_value.prix_acquisition_corrige %}
**Prix d'acquisition corrige** : <<<VAR_START>>>{{ plus_value.prix_acquisition_corrige | format_nombre }}<<<VAR_END>>> EUR
{% endif %}

{% if plus_value.plus_value_brute %}
**Plus-value brute** : <<<VAR_START>>>{{ plus_value.plus_value_brute | format_nombre }}<<<VAR_END>>> EUR
{% endif %}

### Abattements pour duree de detention

{% if plus_value.abattement_ir %}
**Abattement impot sur le revenu** : <<<VAR_START>>>{{ plus_value.abattement_ir.taux }}<<<VAR_END>>> % (soit <<<VAR_START>>>{{ plus_value.abattement_ir.montant | format_nombre }}<<<VAR_END>>> EUR)
{% endif %}

{% if plus_value.abattement_ps %}
**Abattement prelevements sociaux** : <<<VAR_START>>>{{ plus_value.abattement_ps.taux }}<<<VAR_END>>> % (soit <<<VAR_START>>>{{ plus_value.abattement_ps.montant | format_nombre }}<<<VAR_END>>> EUR)
{% endif %}

{% if plus_value.plus_value_imposable_ir %}
**Plus-value imposable (IR)** : <<<VAR_START>>>{{ plus_value.plus_value_imposable_ir | format_nombre }}<<<VAR_END>>> EUR
{% endif %}

{% if plus_value.plus_value_imposable_ps %}
**Plus-value imposable (PS)** : <<<VAR_START>>>{{ plus_value.plus_value_imposable_ps | format_nombre }}<<<VAR_END>>> EUR
{% endif %}

### Impot du

{% if plus_value.impot_revenu %}
**Impot sur le revenu (19%)** : <<<VAR_START>>>{{ plus_value.impot_revenu | format_nombre }}<<<VAR_END>>> EUR
{% endif %}

{% if plus_value.prelevements_sociaux %}
**Prelevements sociaux (17,2%)** : <<<VAR_START>>>{{ plus_value.prelevements_sociaux | format_nombre }}<<<VAR_END>>> EUR
{% endif %}

{% if plus_value.surtaxe %}
**Surtaxe plus-values elevees** : <<<VAR_START>>>{{ plus_value.surtaxe | format_nombre }}<<<VAR_END>>> EUR
(Applicable lorsque la plus-value imposable excede 50 000 EUR)
{% endif %}

{% if plus_value.total_impot %}
**TOTAL A PAYER** : <<<VAR_START>>>{{ plus_value.total_impot | format_nombre }}<<<VAR_END>>> EUR
{% endif %}

### Paiement de l'impot

{% if plus_value.prelevement %}
Le notaire soussigne est charge de prelever le montant de l'impot sur le prix de vente et de le verser au Tresor public dans les conditions prevues par l'article 150 VG du Code general des impots.

{% if plus_value.prelevement.effectue %}
**Prelevement effectue** : <<<VAR_START>>>{{ plus_value.prelevement.montant | format_nombre }}<<<VAR_END>>> EUR
{% endif %}
{% else %}
Le montant de l'impot sur la plus-value sera preleve par le notaire sur le prix de vente et verse au Tresor public.
{% endif %}

{% endif %}

{% else %}
### Information du vendeur

Le VENDEUR est informe qu'en cas de realisation d'une plus-value lors de la presente vente, celle-ci est susceptible d'etre soumise a l'impot sur le revenu au taux de 19% et aux prelevements sociaux au taux de 17,2%.

Des exonerations sont prevues par la loi, notamment :
- Cession de la residence principale
- Cession apres 22 ans de detention (IR) et 30 ans (PS)
- Premiere cession d'un logement autre que la residence principale sous condition de remploi
- Cession dont le prix est inferieur ou egal a 15 000 EUR

Le calcul de la plus-value et de l'impot eventuellement du sera effectue par le notaire soussigne lors de l'etablissement de l'acte authentique.
{% endif %}

### Declarations du vendeur relatives a la plus-value

{% if declarations_fiscales and declarations_fiscales.plus_value %}

Le VENDEUR declare :

{% if declarations_fiscales.plus_value.residence_principale != None %}
- {% if declarations_fiscales.plus_value.residence_principale %}Le bien constitue sa residence principale au jour de la cession{% else %}Le bien ne constitue pas sa residence principale{% endif %}
{% endif %}

{% if declarations_fiscales.plus_value.propriete_partielle %}
- Etre proprietaire de <<<VAR_START>>>{{ declarations_fiscales.plus_value.quote_part }}<<<VAR_END>>> du bien vendu
{% endif %}

{% if declarations_fiscales.plus_value.demembrement %}
- Le bien fait l'objet d'un demembrement de propriete : <<<VAR_START>>>{{ declarations_fiscales.plus_value.demembrement.nature }}<<<VAR_END>>>
{% endif %}

{% if declarations_fiscales.plus_value.exoneration_partielle %}
- Beneficier d'une exoneration partielle : <<<VAR_START>>>{{ declarations_fiscales.plus_value.exoneration_partielle.motif }}<<<VAR_END>>>
{% endif %}

{% else %}
Le VENDEUR devra fournir au notaire tous les elements necessaires au calcul de la plus-value eventuelle, notamment :
- La date et le prix d'acquisition du bien
- Les justificatifs des travaux realises (le cas echeant)
- Sa situation au regard de la residence principale
{% endif %}
