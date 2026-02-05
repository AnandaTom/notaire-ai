# Registre des Traitements de Données Personnelles

> **Article 30 du RGPD** - Document obligatoire
>
> Responsable de traitement : Chaque étude notariale cliente
> Sous-traitant technique : Notomai (Tom Randeau - Agence IA Automatisation)
>
> Date de création : 24 janvier 2026
> Dernière mise à jour : 24 janvier 2026
> Version : 1.0

---

## 1. Identification du Responsable de Traitement

| Champ | Valeur |
|-------|--------|
| **Dénomination** | Chaque étude notariale utilisant NotaireAI |
| **Statut** | Officier public ministériel |
| **DPO mutualisé** | ADNOV (Association pour le Développement du Notariat) |
| **Contact DPO** | dpo@adnov.fr |

### Sous-traitant technique

| Champ | Valeur |
|-------|--------|
| **Dénomination** | Notomai - Agence IA Automatisation |
| **Représentant** | Tom Randeau, Co-Founder |
| **Adresse** | 2B chemin des Garennes, 69260 Charbonnières-les-Bains |
| **Contact** | contact@notomai.fr |
| **DPA signé** | Oui - Supabase (Ref: MS59U-GUISY-UMPBD-VCVJH, 24/01/2026) |

---

## 2. Traitements de Données Personnelles

### 2.1 Gestion des clients de l'étude

| Champ | Description |
|-------|-------------|
| **Finalité** | Gestion de la relation client et suivi des dossiers notariaux |
| **Base légale** | Exécution d'un contrat (Art. 6.1.b) + Obligation légale (Art. 6.1.c) |
| **Catégories de personnes** | Clients de l'étude (vendeurs, acquéreurs, héritiers, etc.) |
| **Catégories de données** | Identité, coordonnées, situation matrimoniale, données patrimoniales |
| **Destinataires** | Notaire, clercs habilités, administrations (cadastre, SPF) |
| **Transferts hors UE** | Non (Supabase région eu-central-1) |
| **Durée de conservation** | 30 ans (obligation légale de conservation des minutes) |
| **Mesures de sécurité** | Chiffrement AES-256, RLS, hachage des noms |

**Données collectées (table `clients`) :**

| Donnée | Type | Obligatoire | Sensible |
|--------|------|-------------|----------|
| Nom | Texte | Oui | Non |
| Prénoms | Texte | Oui | Non |
| Date de naissance | Date | Oui | Non |
| Lieu de naissance | Texte | Oui | Non |
| Nationalité | Texte | Oui | Non |
| Adresse | Texte | Oui | Non |
| Email | Texte | Non | Non |
| Téléphone | Texte | Non | Non |
| Profession | Texte | Non | Non |
| Situation matrimoniale | Texte | Oui | Non |
| Numéro pièce d'identité | Texte | Oui | Non |
| nom_hash | Hash SHA-256 | Auto | Non |

---

### 2.2 Gestion des dossiers notariaux

| Champ | Description |
|-------|-------------|
| **Finalité** | Création et suivi des actes authentiques |
| **Base légale** | Mission de service public (Art. 6.1.e) + Obligation légale (Art. 6.1.c) |
| **Catégories de personnes** | Parties aux actes (vendeurs, acquéreurs, héritiers, etc.) |
| **Catégories de données** | Données du dossier, montants, biens immobiliers |
| **Destinataires** | Notaire, clercs habilités, parties, administrations |
| **Transferts hors UE** | Non |
| **Durée de conservation** | 75 ans pour minutes + 30 ans pour annexes |
| **Mesures de sécurité** | Chiffrement, RLS par étude, audit trail |

**Données collectées (table `dossiers`) :**

| Donnée | Type | Obligatoire | Sensible |
|--------|------|-------------|----------|
| Numéro de dossier | Texte | Oui | Non |
| Type d'acte | Enum | Oui | Non |
| Statut | Enum | Oui | Non |
| Parties | JSONB | Oui | Non |
| Données métier | JSONB chiffré | Oui | Oui |
| Date de création | Timestamp | Auto | Non |

---

### 2.3 Journalisation et audit

| Champ | Description |
|-------|-------------|
| **Finalité** | Traçabilité des actions, sécurité, conformité RGPD |
| **Base légale** | Intérêt légitime (Art. 6.1.f) + Obligation légale |
| **Catégories de personnes** | Utilisateurs du système (notaires, clercs) |
| **Catégories de données** | Actions effectuées, horodatage, adresse IP |
| **Destinataires** | Administrateurs système, auditeurs |
| **Transferts hors UE** | Non |
| **Durée de conservation** | 5 ans |
| **Mesures de sécurité** | Table en append-only, protection contre modification |

**Données collectées (table `audit_logs`) :**

| Donnée | Type | Obligatoire |
|--------|------|-------------|
| Action | Texte | Oui |
| Resource type | Texte | Oui |
| Resource ID | UUID | Non |
| Etude ID | UUID | Oui |
| User ID | UUID | Non |
| IP Address | Inet | Non |
| User Agent | Texte | Non |
| Timestamp | Timestamp | Auto |
| Details | JSONB | Non |

---

### 2.4 Gestion des demandes RGPD

| Champ | Description |
|-------|-------------|
| **Finalité** | Gestion des droits des personnes concernées |
| **Base légale** | Obligation légale (Art. 6.1.c) - RGPD Art. 15-22 |
| **Catégories de personnes** | Personnes exerçant leurs droits RGPD |
| **Catégories de données** | Identité du demandeur, type de demande, statut |
| **Destinataires** | DPO, responsable de traitement |
| **Transferts hors UE** | Non |
| **Durée de conservation** | 3 ans après traitement |
| **Mesures de sécurité** | Accès restreint, traçabilité |

**Types de demandes supportées :**

| Droit RGPD | Délai légal | Implémenté |
|------------|-------------|------------|
| Accès (Art. 15) | 1 mois | ✅ |
| Rectification (Art. 16) | 1 mois | ✅ |
| Effacement (Art. 17) | 1 mois | ✅ (avec limites légales) |
| Portabilité (Art. 20) | 1 mois | ✅ |
| Opposition (Art. 21) | Immédiat | ✅ |

---

### 2.5 Authentification des agents

| Champ | Description |
|-------|-------------|
| **Finalité** | Contrôle d'accès et sécurité multi-tenant |
| **Base légale** | Intérêt légitime (sécurité du traitement) |
| **Catégories de personnes** | Agents IA par étude |
| **Catégories de données** | Clé API (hashée), permissions, logs d'utilisation |
| **Destinataires** | Système d'authentification |
| **Transferts hors UE** | Non |
| **Durée de conservation** | Durée du contrat + 1 an |
| **Mesures de sécurité** | Hash SHA-256, rate limiting, révocation possible |

---

## 3. Mesures de Sécurité Techniques et Organisationnelles

### 3.1 Mesures techniques

| Mesure | Détail | Statut |
|--------|--------|--------|
| **Chiffrement au repos** | AES-256 (Supabase) | ✅ Actif |
| **Chiffrement en transit** | TLS 1.3 | ✅ Actif |
| **Isolation des données** | Row-Level Security par etude_id | ✅ Actif |
| **Hachage des identifiants** | SHA-256 pour recherche nom | ✅ Actif |
| **Authentification forte** | Clés API hashées + rate limiting | ✅ Actif |
| **Journalisation** | Audit logs complets | ✅ Actif |
| **Sauvegarde** | Automatique Supabase (PITR 7 jours) | ✅ Actif |
| **Pseudonymisation** | Fonction `anonymize_client()` | ✅ Disponible |

### 3.2 Mesures organisationnelles

| Mesure | Détail | Statut |
|--------|--------|--------|
| **DPA sous-traitant** | Signé avec Supabase (24/01/2026) | ✅ |
| **Politique d'accès** | Un agent = une étude | ✅ |
| **Formation** | Guide de déploiement sécurisé | ✅ |
| **Gestion des incidents** | Procédure de notification 72h | ⚠️ À documenter |
| **Audit régulier** | Vérification des accès | ⚠️ À planifier |

---

## 4. Transferts de Données

### 4.1 Sous-traitants

| Sous-traitant | Pays | Données | Garanties |
|---------------|------|---------|-----------|
| Supabase Inc. | USA (stockage EU) | Toutes | DPA signé, SCCs, région eu-central-1 |
| Anthropic | USA | **Conversations chatbot incluant potentiellement des données personnelles** (noms, adresses, situation matrimoniale, patrimoine) transmises via l'API Claude pour assistance à la rédaction | DPA Anthropic, zero data retention policy (données non utilisées pour entraînement), pas de stockage au-delà de 30 jours. **ACTION REQUISE** : implémenter l'anonymisation des messages avant envoi (module `ChatAnonymizer` disponible) ou obtenir les SCCs spécifiques d'Anthropic. |

> **⚠️ AVERTISSEMENT CONFORMITE** (ajouté le 05/02/2026) : Le chatbot frontend (`frontend/app/api/chat/route.ts`) transmet actuellement l'intégralité des conversations à l'API Anthropic, y compris les données personnelles saisies par le notaire. Un module d'anonymisation (`execution/security/chat_anonymizer.py`) existe mais n'est pas encore intégré au flux. Cette intégration est **prioritaire** avant toute utilisation avec des données réelles de clients.

### 4.2 Destinataires institutionnels

| Destinataire | Base légale | Données |
|--------------|-------------|---------|
| Service de publicité foncière | Obligation légale | Actes de mutation |
| Cadastre | Obligation légale | Modifications foncières |
| DGFIP | Obligation légale | Déclarations fiscales |
| CRPCEN | Obligation légale | Cotisations retraite |

---

## 5. Droits des Personnes Concernées

### 5.1 Procédure d'exercice des droits

1. **Réception** : Le notaire reçoit la demande par tout moyen
2. **Vérification** : Identité du demandeur vérifiée
3. **Enregistrement** : Table `rgpd_requests` via l'interface
4. **Traitement** : Selon le type de demande
5. **Réponse** : Sous 1 mois (prolongeable 2 mois si complexe)
6. **Archivage** : Conservation 3 ans

### 5.2 Limitations légales

Le droit à l'effacement (Art. 17) est limité par :
- **Obligation de conservation** : Minutes notariales (75 ans)
- **Exercice de droits en justice** : Conservation pour preuve
- **Mission de service public** : Authenticité des actes

→ Seule l'**anonymisation** est possible après les délais légaux.

---

## 6. Analyse d'Impact (AIPD)

### 6.1 Nécessité d'une AIPD

Une AIPD est **requise** car le traitement :
- ✅ Concerne des données à grande échelle
- ✅ Est effectué pour le compte d'un officier public
- ✅ Utilise des technologies innovantes (IA)

### 6.2 Synthèse de l'AIPD

| Critère | Évaluation | Mesures |
|---------|------------|---------|
| Nécessité | Justifiée (efficacité notariale) | - |
| Proportionnalité | Données strictement nécessaires | Minimisation des données |
| Risques personnes | Modéré | Chiffrement, RLS, audit |
| Risques sécurité | Faible | Architecture sécurisée |

**Risques résiduels acceptables** : Oui, avec les mesures en place.

---

## 7. Historique des Modifications

| Date | Version | Modification | Auteur |
|------|---------|--------------|--------|
| 24/01/2026 | 1.0 | Création initiale | Tom Randeau |

---

## 8. Annexes

### A. Schéma des flux de données

```
┌──────────────┐     ┌─────────────────┐     ┌──────────────────┐
│   Notaire    │────▶│   NotaireAI     │────▶│    Supabase      │
│   (Client)   │     │   (Agent IA)    │     │   (eu-central-1) │
└──────────────┘     └─────────────────┘     └──────────────────┘
       │                     │                        │
       │  Données client     │  Requêtes chiffrées   │  Stockage AES-256
       │  (TLS 1.3)          │  (HTTPS)              │  RLS par étude
       ▼                     ▼                        ▼
┌──────────────┐     ┌─────────────────┐     ┌──────────────────┐
│  Documents   │     │   Audit Logs    │     │   Backups PITR   │
│  DOCX/PDF    │     │   (traçabilité) │     │   (7 jours)      │
└──────────────┘     └─────────────────┘     └──────────────────┘
```

### B. Contact DPO

Pour toute question relative à la protection des données :
- **DPO notariat** : ADNOV - 95 Avenue des Logissons, 13770 VENELLES - dpo@groupeadsn.fr
- **Support technique** : Notomai - contact@notomai.fr

---

*Document généré conformément à l'Article 30 du Règlement (UE) 2016/679 (RGPD)*
