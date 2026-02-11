# Intégration Viager v2.0.0 - Frontend

> Guide complet pour intégrer le support viager dans le chat Payos

**Date**: 11/02/2026
**Version Backend**: v2.0.0
**Fichiers créés**: 4 nouveaux composants

---

## 📦 Fichiers Créés

| Fichier | Type | Description |
|---------|------|-------------|
| `lib/api/promesse.ts` | API Client | Client TypeScript pour tous les endpoints promesse v2.0.0 |
| `components/ViagerBadge.tsx` | Composant UI | Badge d'affichage de la détection viager |
| `hooks/useViagerDetection.ts` | Hook React | Hook de détection automatique + validation + questions |
| `components/ChatWithViager.tsx` | Exemple | Exemple complet d'intégration dans un chat |

---

## 🚀 Quick Start (3 étapes)

### 1. Installer les Dépendances (si nécessaire)

Les composants utilisent uniquement React standard + TypeScript. Aucune dépendance supplémentaire requise.

### 2. Utiliser le Hook dans Votre Chat

```typescript
// Dans votre composant Chat principal
import { useViagerDetection } from '@/hooks/useViagerDetection';
import ViagerBadge from '@/components/ViagerBadge';

export default function MonChat() {
  const [donnees, setDonnees] = useState({});

  // Hook viager avec auto-détection
  const {
    detection,
    isViager,
    questionsViager,
    checkViagerRequired,
    getViagerWarnings,
  } = useViagerDetection(donnees, {
    autoDetect: true,
    validateOnChange: true,
  });

  return (
    <div>
      {/* Badge viager */}
      {detection && <ViagerBadge detection={detection} />}

      {/* Votre chat existant */}
      <MonChatExistant />

      {/* Questions viager conditionnelles */}
      {isViager && questionsViager.length > 0 && (
        <QuestionsViager questions={questionsViager} />
      )}
    </div>
  );
}
```

### 3. Tester

```bash
cd frontend
npm run dev

# Ouvrir http://localhost:3000
# Taper: "Je veux vendre ma maison en viager pour 150000€"
# → Badge viager s'affiche automatiquement
# → Questions viager chargées
```

---

## 📖 Guide Détaillé

### API Client (`lib/api/promesse.ts`)

**Endpoints disponibles** :

```typescript
// Détection 3 niveaux (catégorie + type + sous-type)
const detection = await detecterType(donnees);
// → { sous_type: 'viager', confiance: 95, marqueurs_detectes: [...] }

// Validation avec règles métier viager
const validation = await validerPromesse(donnees);
// → { valide: true, erreurs: [], warnings: [...] }

// Questions filtrées par sous-type
const questions = await getQuestions('COPROPRIETE', 'viager', '15_viager');
// → { sections: [{ id: '15_viager', questions: [...] }] }

// Workflow complet
const workflow = await startWorkflow('promesse_vente', 'viager');
await submitAnswers(workflow.workflow_id, reponses);
const doc = await generateDocument(workflow.workflow_id);
```

**Stream SSE pour progression** :

```typescript
const eventSource = streamGeneration(workflowId, (data) => {
  console.log('Progression:', data.progression); // 0-100
  console.log('Étape:', data.etape); // "assemblage", "export"
});
```

---

### Hook useViagerDetection

**Configuration** :

```typescript
const {
  // État détection
  detection,        // DetectionResult | null
  isDetecting,      // boolean
  detectionError,   // string | null
  detectType,       // () => Promise<void> - Détection manuelle

  // Questions conditionnelles
  questionsViager,  // Section[] - Questions section 15_viager
  isLoadingQuestions, // boolean

  // Validation
  validation,       // ValidationResult | null
  isValidating,     // boolean
  validateData,     // () => Promise<void>

  // Helpers
  checkViagerRequired, // () => { valid: boolean, missing: string[] }
  getViagerWarnings,   // () => string[]

  // Computed
  isViager,         // boolean - Raccourci detection?.sous_type === 'viager'
  isCreation,       // boolean - Raccourci detection?.sous_type === 'creation'
  sousType,         // string | undefined
  confiance,        // number - 0-100
} = useViagerDetection(donnees, {
  autoDetect: true,         // Détection auto après 3 champs remplis
  validateOnChange: true,   // Validation temps réel
});
```

**Détection automatique** :
- Se déclenche dès que 3 champs sont remplis
- Debounce 1s (évite trop d'appels API)
- Détecte viager via 6 marqueurs (bouquet, rente, type_vente, DUH, modalités, etc.)

**Validation temps réel** :
- Se déclenche uniquement si viager détecté
- Debounce 500ms
- Vérifie champs obligatoires : bouquet, rente
- Génère warnings : certificat médical, indexation, DUH

---

### Composant ViagerBadge

**Affichage** :

```tsx
<ViagerBadge detection={detection} className="mb-4" />
```

**Rendu** :
- Badge coloré selon sous-type (bleu=viager, jaune=création, vert=lotissement)
- Icône emoji (🏡 viager, 🏗️ création, etc.)
- Confiance en %
- Marqueurs détectés (repliable)
- Pour viager : 4 badges (Bouquet, DUH, Certificat, Privilège)

---

### Exemple Complet (`ChatWithViager.tsx`)

**Fonctionnalités implémentées** :
1. ✅ Détection automatique viager
2. ✅ Badge avec confiance
3. ✅ Questions viager conditionnelles (section 15)
4. ✅ Champs requis manquants
5. ✅ Warnings recommandations
6. ✅ Parsing NL basique (à améliorer avec `/agent/execute`)

**À personnaliser** :
- `parseMessage()` : Parsing NL → utiliser `/agent/execute` pour un vrai parsing
- `generateResponse()` : Logique de réponse → intégrer votre système de Q&R
- Styling : Adapter aux couleurs/styles de votre chat

---

## 🎨 UI/UX Recommendations

### Badge Viager

**Quand l'afficher** :
- Dès que `detection.sous_type` existe
- En haut du chat, avant les messages
- Persistant pendant toute la session

**Animations** :
- Fade-in lors de l'apparition
- Pulse sur l'icône pendant `isDetecting`

### Questions Conditionnelles

**Affichage progressif** :
- Afficher 3-5 questions à la fois
- Bouton "Afficher plus" si > 5 questions
- Scroll automatique vers la nouvelle question

**Validation inline** :
- ✅ Vert si valide
- ❌ Rouge + message d'erreur si invalide
- ⚠️ Orange pour warnings

### Champs Requis

**Affichage** :
- Liste des champs manquants
- Clic sur un champ → scroll vers la question correspondante
- Badge "3 champs manquants" dans la barre de navigation

---

## 🧪 Tests

### Test Manuel

```bash
# 1. Lancer le frontend
npm run dev

# 2. Scénario viager complet
User: "Je veux vendre ma maison en viager"
→ Vérifie: Badge viager apparaît

User: "Le bouquet est de 50000 euros"
→ Vérifie: Champ bouquet rempli, warning rente manquante

User: "La rente est de 1200 euros par mois"
→ Vérifie: Validation réussie, questions viager activées

User: "Le vendeur a 78 ans"
→ Vérifie: Âge renseigné, warning certificat médical

User: "Un certificat médical a été fourni"
→ Vérifie: Tous warnings résolus, prêt à générer
```

### Test Automatisé (Jest)

```typescript
// __tests__/useViagerDetection.test.ts
import { renderHook, waitFor } from '@testing-library/react';
import { useViagerDetection } from '@/hooks/useViagerDetection';

test('détecte le viager automatiquement', async () => {
  const donnees = {
    prix: { type_vente: 'viager', bouquet: { montant: 50000 } },
    bien: { nature: 'maison' },
  };

  const { result } = renderHook(() => useViagerDetection(donnees));

  await waitFor(() => {
    expect(result.current.isViager).toBe(true);
    expect(result.current.confiance).toBeGreaterThan(70);
  });
});
```

---

## 🐛 Troubleshooting

### Le badge ne s'affiche pas

**Cause** : Pas assez de données (< 3 champs)

**Solution** :
```typescript
// Forcer la détection manuelle
const { detectType } = useViagerDetection(donnees, { autoDetect: false });
useEffect(() => {
  if (Object.keys(donnees).length >= 3) {
    detectType();
  }
}, [donnees]);
```

### Questions viager ne chargent pas

**Cause** : Endpoint `/questions/promesse` ne retourne pas section `15_viager`

**Debug** :
```typescript
const questions = await getQuestions('COPROPRIETE', 'viager');
console.log('Sections:', questions.sections.map(s => s.id));
// Doit contenir '15_viager'
```

**Solution** : Vérifier que le backend v2.0.0 est déployé sur Modal

### CORS Error

**Cause** : Frontend local + backend Modal

**Solution** :
```typescript
// .env.local
NEXT_PUBLIC_API_URL=https://notaire-ai--fastapi-app.modal.run
```

### Type Errors

**Solution** : Installer les types
```bash
npm install --save-dev @types/react @types/node
```

---

## 📊 Métriques de Succès

| Métrique | Target | Comment Mesurer |
|----------|--------|-----------------|
| **Taux de détection** | >90% | Analytics: viager détecté / promesses créées |
| **Confiance moyenne** | >85% | Moyenne `detection.confiance` |
| **Temps de détection** | <2s | Performance API `/promesses/detecter-type` |
| **Questions activées** | 100% | Vérifier `questionsViager.length === 19` |
| **Validation réussie** | >95% | Analytics: `validation.valide === true` |

---

## 🔗 Ressources

- **[INTEGRATION_CHAT_VIAGER_V2.md](../docs/INTEGRATION_CHAT_VIAGER_V2.md)** - Guide complet backend + frontend
- **[API Documentation](../api/main.py)** - Endpoints Modal
- **[Schéma Viager v4.1.0](../schemas/variables_promesse_vente.json)** - Structure données
- **[Questions Viager v3.2.0](../schemas/questions_promesse_vente.json)** - Section 15
- **[Template Viager](../templates/promesse_viager.md)** - Template Jinja2

---

## 🎯 Next Steps

### Court Terme (1-2 jours)
- [ ] Intégrer les 4 fichiers dans votre codebase
- [ ] Adapter le styling à votre design system
- [ ] Tester avec des données réelles

### Moyen Terme (1 semaine)
- [ ] Améliorer le parsing NL (utiliser `/agent/execute`)
- [ ] Ajouter analytics (détections, conversions)
- [ ] Tests automatisés E2E

### Long Terme (2+ semaines)
- [ ] Support création copropriété (sous-type `creation`)
- [ ] Support lotissement (sous-type `lotissement`)
- [ ] Preview temps réel du document

---

**Dernière mise à jour** : 11/02/2026
**Auteur** : Claude Code
**Version** : 1.0.0
