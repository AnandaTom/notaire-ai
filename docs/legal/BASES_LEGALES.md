# Bases Légales des Traitements - Notomai

> **Article 6 du RGPD** - Licéité du traitement
>
> Chaque traitement de données personnelles doit reposer sur l'une des six bases légales prévues par le RGPD.
>
> Date : 24 janvier 2026

---

## 1. Les Six Bases Légales du RGPD

| Base légale | Article | Applicable au notariat |
|-------------|---------|------------------------|
| Consentement | 6.1.a | Rarement (actes non obligatoires) |
| Exécution d'un contrat | 6.1.b | **Oui** - Mandat confié au notaire |
| Obligation légale | 6.1.c | **Oui** - Nombreuses obligations |
| Intérêts vitaux | 6.1.d | Non applicable |
| Mission de service public | 6.1.e | **Oui** - Officier public |
| Intérêt légitime | 6.1.f | Oui - Sécurité, statistiques |

---

## 2. Bases Légales par Traitement

### 2.1 Gestion des dossiers clients

| Traitement | Base légale | Justification |
|------------|-------------|---------------|
| Collecte identité parties | **6.1.c** Obligation légale | Art. 5 Décret 71-941 : mention obligatoire |
| Vérification identité | **6.1.c** Obligation légale | Lutte anti-blanchiment (Art. L.561-5 CMF) |
| Rédaction de l'acte | **6.1.b** Contrat + **6.1.e** Service public | Mandat du client + mission d'officier public |
| Conservation des minutes | **6.1.c** Obligation légale | Art. 29 Loi 25 ventôse an XI (75 ans) |
| Transmission au SPF | **6.1.c** Obligation légale | Art. 32 Décret 55-22 |

### 2.2 Formalités administratives

| Traitement | Base légale | Justification |
|------------|-------------|---------------|
| Enregistrement fiscal | **6.1.c** Obligation légale | Art. 657 CGI |
| Publicité foncière | **6.1.c** Obligation légale | Art. 28 Décret 55-22 |
| Cadastre | **6.1.c** Obligation légale | Mise à jour obligatoire |
| Fichier FICOBA | **6.1.c** Obligation légale | Art. L.564-1 CMF |

### 2.3 Vérifications légales

| Traitement | Base légale | Justification |
|------------|-------------|---------------|
| Consultation BODACC | **6.1.c** Obligation légale | Vérification procédures collectives |
| Hypothèques | **6.1.c** Obligation légale | Purge des privilèges |
| État civil | **6.1.c** Obligation légale | Vérification capacité juridique |
| RCS/RNCS | **6.1.c** Obligation légale | Vérification personnes morales |

### 2.4 Sécurité et traçabilité

| Traitement | Base légale | Justification |
|------------|-------------|---------------|
| Journalisation (audit logs) | **6.1.f** Intérêt légitime | Sécurité du traitement (Art. 32) |
| Authentification API | **6.1.f** Intérêt légitime | Protection des données |
| Sauvegarde | **6.1.c** + **6.1.f** | Conservation + Sécurité |
| Détection d'intrusion | **6.1.f** Intérêt légitime | Sécurité informatique |

### 2.5 Gestion des droits RGPD

| Traitement | Base légale | Justification |
|------------|-------------|---------------|
| Enregistrement demandes | **6.1.c** Obligation légale | Art. 12-22 RGPD |
| Réponse aux demandes | **6.1.c** Obligation légale | Art. 12-22 RGPD |
| Archivage demandes | **6.1.f** Intérêt légitime | Preuve de conformité |

---

## 3. Textes de Référence

### 3.1 Réglementation notariale

| Texte | Contenu |
|-------|---------|
| Loi 25 ventôse an XI | Statut des notaires, conservation des minutes |
| Décret 71-941 | Statut du notariat |
| Règlement national du notariat | Règles professionnelles |
| Art. 1317 Code civil | Définition de l'acte authentique |

### 3.2 Obligations de conservation

| Document | Durée | Texte |
|----------|-------|-------|
| Minutes | 75 ans | Art. 29 Loi 25 ventôse an XI |
| Annexes | 30 ans | Règlement national |
| Comptabilité | 10 ans | Art. L.123-22 Code commerce |
| Documents fiscaux | 6 ans | Art. L.102 B LPF |

### 3.3 Lutte anti-blanchiment

| Obligation | Texte |
|------------|-------|
| Identification client | Art. L.561-5 CMF |
| Vigilance renforcée | Art. L.561-10-2 CMF |
| Déclaration TRACFIN | Art. L.561-15 CMF |
| Conservation 5 ans | Art. L.561-12 CMF |

---

## 4. Analyse par Type de Données

### 4.1 Données d'identification

```
Nom, prénoms, date/lieu naissance, nationalité
```

| Base légale | Texte | Analyse |
|-------------|-------|---------|
| **6.1.c** Obligation légale | Art. 5 Décret 71-941 | Mention obligatoire dans tout acte |
| **6.1.e** Service public | Art. 1317 Code civil | Authenticité de l'acte |

**Conclusion** : Ces données sont **strictement nécessaires** et ne peuvent être refusées sans empêcher l'acte.

### 4.2 Situation matrimoniale

```
Régime matrimonial, nom du conjoint
```

| Base légale | Texte | Analyse |
|-------------|-------|---------|
| **6.1.c** Obligation légale | Art. 1404, 1424 Code civil | Protection du conjoint |
| **6.1.b** Contrat | Mandat notarial | Conseil juridique approprié |

**Conclusion** : Information nécessaire pour déterminer qui doit intervenir à l'acte.

### 4.3 Données bancaires

```
IBAN, références prêt
```

| Base légale | Texte | Analyse |
|-------------|-------|---------|
| **6.1.b** Contrat | Mandat notarial | Règlement du prix |
| **6.1.c** Obligation légale | Art. L.112-6 CMF | Traçabilité des fonds |

**Conclusion** : Données collectées uniquement pour l'exécution de l'opération.

### 4.4 Données patrimoniales

```
Désignation bien, prix, conditions
```

| Base légale | Texte | Analyse |
|-------------|-------|---------|
| **6.1.b** Contrat | Mandat notarial | Objet de la prestation |
| **6.1.c** Obligation légale | Art. 4 Décret 55-22 | Publicité foncière |

---

## 5. Limitations des Droits RGPD

Le notariat bénéficie de **limitations légales** aux droits RGPD :

### 5.1 Droit à l'effacement (Art. 17.3)

**Non applicable** pour :
- Minutes notariales → Conservation 75 ans obligatoire
- Actes servant de preuve → Jusqu'à prescription
- Missions de service public → Authenticité

### 5.2 Droit d'opposition (Art. 21)

**Limité** car le traitement repose sur :
- L'obligation légale (6.1.c) → Pas d'opposition possible
- La mission de service public (6.1.e) → Opposition limitée

### 5.3 Droit à la portabilité (Art. 20)

**Applicable uniquement** aux données :
- Traitées sur base du contrat (6.1.b)
- Fournies par la personne
- Traitées de manière automatisée

---

## 6. Balance des Intérêts (Art. 6.1.f)

Pour les traitements basés sur l'intérêt légitime, une balance a été effectuée :

### 6.1 Journalisation / Audit

| Critère | Analyse |
|---------|---------|
| **Intérêt du responsable** | Fort - Sécurité, conformité, preuve |
| **Impact sur la personne** | Faible - Données techniques uniquement |
| **Attentes raisonnables** | Oui - Normal pour un système informatique |
| **Garanties** | Conservation limitée (5 ans), accès restreint |

**Conclusion** : Intérêt légitime validé.

### 6.2 Statistiques anonymisées

| Critère | Analyse |
|---------|---------|
| **Intérêt du responsable** | Modéré - Amélioration du service |
| **Impact sur la personne** | Nul - Données anonymisées |
| **Attentes raisonnables** | Oui - Pratique courante |
| **Garanties** | Anonymisation irréversible |

**Conclusion** : Intérêt légitime validé.

---

## 7. Synthèse par Table Supabase

| Table | Base légale principale | Justification |
|-------|------------------------|---------------|
| `etudes` | 6.1.b Contrat | Relation commerciale |
| `clients` | 6.1.c Obligation + 6.1.e Service public | Acte authentique |
| `dossiers` | 6.1.b Contrat + 6.1.c Obligation | Prestation + conservation |
| `audit_logs` | 6.1.f Intérêt légitime | Sécurité |
| `rgpd_requests` | 6.1.c Obligation | Conformité RGPD |
| `agent_api_keys` | 6.1.f Intérêt légitime | Sécurité |

---

## 8. Références Documentaires

### 8.1 CNIL

- Guide de la CNIL pour les notaires (2019)
- Délibération 2018-303 du 11 octobre 2018

### 8.2 CSN (Conseil Supérieur du Notariat)

- Charte du numérique notarial
- Recommandations RGPD du notariat

### 8.3 ADNOV

- Kit RGPD pour les notaires
- Fiches pratiques protection des données

---

*Document établi conformément à l'article 6 du Règlement (UE) 2016/679 et aux obligations spécifiques du notariat français.*
