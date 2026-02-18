# Procedure de Gestion des Incidents de Securite

> **Article 33 et 34 du RGPD** - Notification des violations de donnees
>
> Date de creation : 18 fevrier 2026
> Derniere mise a jour : 18 fevrier 2026
> Version : 1.0

---

## 1. Qu'est-ce qu'un incident de securite ?

Un incident de securite (ou "violation de donnees") est tout evenement qui entraine :

| Type | Exemples |
|------|----------|
| **Acces non autorise** | Quelqu'un accede a des dossiers qui ne sont pas les siens |
| **Fuite de donnees** | Des donnees clients se retrouvent sur internet ou chez un tiers |
| **Perte de donnees** | Des dossiers sont supprimes ou inaccessibles |
| **Modification non autorisee** | Des donnees sont modifiees sans autorisation |

---

## 2. Qui doit etre prevenu et dans quel delai ?

### Chaine d'alerte

```
Decouverte de l'incident
        |
        v (Immediat - dans l'heure)
[1] Equipe technique Notomai
    contact@notomai.fr
    Tom Randeau (co-fondateur)
        |
        v (Sous 24h)
[2] Etude(s) notariale(s) concernee(s)
    Le notaire responsable de traitement
        |
        v (Sous 72h maximum - obligation legale)
[3] CNIL (si risque pour les personnes)
    https://notifications.cnil.fr/notifications/
        |
        v (Dans les meilleurs delais)
[4] Personnes concernees (si risque eleve)
    Clients dont les donnees ont ete compromises
```

### Delais legaux (RGPD Article 33)

| Action | Delai | Qui |
|--------|-------|-----|
| Alerte interne | Immediat (< 1h) | Celui qui decouvre |
| Notification au notaire (responsable de traitement) | < 24h | Notomai |
| Notification a la CNIL | **< 72h** apres decouverte | Le notaire (aide par Notomai) |
| Notification aux personnes concernees | Sans delai excessif | Le notaire (aide par Notomai) |

---

## 3. Etapes de gestion d'un incident

### Etape 1 : CONTENIR (immediat)

- [ ] Identifier la source de l'incident
- [ ] Couper l'acces si possible (revoquer cle API, bloquer IP, suspendre compte)
- [ ] Sauvegarder les logs et preuves (ne rien supprimer)
- [ ] Documenter l'heure exacte de decouverte

### Etape 2 : EVALUER (sous 4h)

- [ ] Quelles donnees sont concernees ? (noms, adresses, donnees financieres)
- [ ] Combien de personnes sont touchees ?
- [ ] Quels types d'actes sont concernes ?
- [ ] Le risque pour les personnes est-il eleve ?

**Grille d'evaluation du risque :**

| Critere | Risque faible | Risque eleve |
|---------|--------------|--------------|
| Donnees concernees | Logs techniques, metadata | Noms, adresses, patrimoine |
| Nombre de personnes | < 10 | > 10 |
| Donnees chiffrees ? | Oui | Non |
| Acces exploitable ? | Non (tentative bloquee) | Oui (donnees exfiltrees) |

### Etape 3 : NOTIFIER (sous 72h)

**Si risque pour les personnes → notifier la CNIL :**

1. Se rendre sur https://notifications.cnil.fr/notifications/
2. Remplir le formulaire avec :
   - Nature de la violation (confidentialite, integrite, disponibilite)
   - Categories de donnees concernees
   - Nombre approximatif de personnes
   - Consequences probables
   - Mesures prises pour remedier

**Si risque eleve → notifier les personnes concernees :**

Envoyer un courrier ou email contenant :
- La nature de la violation
- Les consequences probables
- Les mesures prises
- Les recommandations (changer mot de passe, surveiller comptes)
- Le contact du DPO : dpo@adnov.fr

### Etape 4 : REMEDIER

- [ ] Corriger la faille technique
- [ ] Renforcer les controles d'acces
- [ ] Mettre a jour les logs et l'audit trail
- [ ] Tester la correction

### Etape 5 : DOCUMENTER

- [ ] Rediger un rapport d'incident complet
- [ ] Mettre a jour le registre des violations (section 7 ci-dessous)
- [ ] Identifier les ameliorations preventives
- [ ] Planifier les mesures correctives

---

## 4. Contacts d'urgence

| Qui | Contact | Role |
|-----|---------|------|
| **Tom Randeau** | contact@notomai.fr | Co-fondateur, responsable technique |
| **Augustin** | (a completer) | Backend / Infrastructure |
| **Paul** | (a completer) | Frontend / Integration |
| **DPO notariat** | dpo@adnov.fr | Delegue a la protection des donnees |
| **CNIL** | https://notifications.cnil.fr | Autorite de controle |
| **Supabase Support** | support@supabase.io | Sous-traitant hebergement |

---

## 5. Modele de notification CNIL

### Informations a fournir (formulaire CNIL)

```
1. Nature de la violation :
   [ ] Confidentialite (acces non autorise)
   [ ] Integrite (modification non autorisee)
   [ ] Disponibilite (perte ou destruction)

2. Date et heure de la decouverte :
   ____/____/________ a ____h____

3. Nombre de personnes concernees :
   Approximatif : ________
   Exact (si connu) : ________

4. Categories de personnes :
   [ ] Clients d'etude notariale
   [ ] Collaborateurs d'etude
   [ ] Autres : ________

5. Categories de donnees :
   [ ] Identite (nom, prenom, date de naissance)
   [ ] Coordonnees (adresse, email, telephone)
   [ ] Donnees patrimoniales (biens, prix, situation financiere)
   [ ] Situation matrimoniale
   [ ] Donnees bancaires
   [ ] Pieces d'identite

6. Consequences probables :
   ________________________________________

7. Mesures prises pour remedier :
   ________________________________________

8. Mesures prises pour attenuer les effets :
   ________________________________________
```

---

## 6. Scenarios types et reactions

### Scenario A : Cle API compromise

| Etape | Action |
|-------|--------|
| 1 | Revoquer immediatement la cle dans Supabase Dashboard |
| 2 | Generer une nouvelle cle |
| 3 | Verifier les logs d'acces (table audit_logs) pour la cle compromise |
| 4 | Si des donnees ont ete accedees : notifier le notaire + evaluer CNIL |

### Scenario B : Erreur de cloisonnement (un notaire voit les dossiers d'un autre)

| Etape | Action |
|-------|--------|
| 1 | Desactiver temporairement la vue ou l'endpoint concerne |
| 2 | Corriger la politique RLS dans Supabase |
| 3 | Identifier quelles donnees ont ete visibles et par qui |
| 4 | Notifier les deux etudes concernees |
| 5 | Si donnees effectivement consultees : evaluer notification CNIL |

### Scenario C : Supabase indisponible

| Etape | Action |
|-------|--------|
| 1 | Verifier le status Supabase : https://status.supabase.com |
| 2 | Si panne > 4h : activer le mode hors-ligne si disponible |
| 3 | Informer les etudes clientes de l'indisponibilite |
| 4 | Pas de notification CNIL necessaire (pas de fuite) |

### Scenario D : Fuite de fichier .env ou secrets

| Etape | Action |
|-------|--------|
| 1 | Rotation IMMEDIATE de toutes les cles (Supabase, Anthropic, Modal) |
| 2 | Verifier les logs pour acces non autorises |
| 3 | Si secrets sur GitHub public : contacter GitHub pour suppression du commit |
| 4 | Evaluer si des donnees ont pu etre accedees |

---

## 7. Registre des violations

> Obligation Article 33.5 RGPD : tenir un registre de toutes les violations

| Date | Nature | Donnees | Personnes | CNIL notifiee | Mesures | Statut |
|------|--------|---------|-----------|---------------|---------|--------|
| (aucun incident a ce jour) | - | - | - | - | - | - |

---

## 8. Revision de cette procedure

| Version | Date | Modification | Auteur |
|---------|------|--------------|--------|
| 1.0 | 18/02/2026 | Creation initiale | Augustin (Notomai) |

**Prochaine revision prevue** : 18/08/2026 (tous les 6 mois)

---

*Document etabli conformement aux Articles 33 et 34 du Reglement (UE) 2016/679 (RGPD)*
