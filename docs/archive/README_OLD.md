# Agent AI - Création & Modification d'Actes Notariaux

Un système d'automatisation basé sur une architecture à 3 couches pour la création et modification d'actes notariaux.

## Architecture

Ce projet utilise une architecture à 3 couches qui sépare les préoccupations pour maximiser la fiabilité :

### Couche 1 : Directives (Quoi faire)
- SOPs écrites en Markdown, stockées dans `directives/`
- Définissent les objectifs, entrées, outils/scripts à utiliser, sorties et cas limites
- Instructions en langage naturel

### Couche 2 : Orchestration (Prise de décision)
- Géré par l'IA (Claude/Gemini)
- Routage intelligent entre les directives et l'exécution
- Gestion des erreurs et auto-amélioration

### Couche 3 : Exécution (Faire le travail)
- Scripts Python déterministes dans `execution/`
- Gèrent les appels API, traitement de données, opérations sur fichiers
- Fiables, testables, rapides

## Structure des Répertoires

```
.
├── directives/          # Instructions en Markdown (SOPs)
├── execution/          # Scripts Python déterministes
├── .tmp/              # Fichiers intermédiaires temporaires (non versionnés)
├── .env               # Variables d'environnement (non versionné)
├── .env.template      # Template pour les variables d'environnement
├── credentials.json   # Credentials Google OAuth (non versionné)
├── token.json        # Token Google OAuth (non versionné)
└── requirements.txt  # Dépendances Python
```

## Installation

### Prérequis
- Python 3.14 ou supérieur
- pip (gestionnaire de paquets Python)
- Compte Google Cloud (pour les APIs Google Sheets/Slides)

### Étapes d'installation

1. **Cloner le dépôt** (si ce n'est pas déjà fait)

2. **Installer les dépendances Python**
```bash
python -m pip install -r requirements.txt
```

3. **Configurer les variables d'environnement**
```bash
# Copier le template
cp .env.template .env

# Éditer .env avec vos vraies valeurs
# Ouvrir .env dans votre éditeur et remplir les clés API
```

4. **Configurer Google Cloud APIs** (si nécessaire)
   - Aller sur [Google Cloud Console](https://console.cloud.google.com/)
   - Créer un nouveau projet
   - Activer les APIs Google Sheets et Google Slides
   - Créer des credentials OAuth 2.0
   - Télécharger le fichier `credentials.json` et le placer à la racine du projet

5. **Vérifier l'installation**
```bash
# Lister les répertoires créés
ls -la

# Vérifier que Python et pip fonctionnent
python --version
python -m pip --version
```

## Utilisation

### Principe de fonctionnement

1. L'IA lit les directives dans `directives/`
2. L'IA appelle les scripts d'exécution appropriés dans `execution/`
3. Les fichiers temporaires sont stockés dans `.tmp/`
4. Les livrables finaux sont stockés dans Google Sheets/Slides ou autres services cloud

### Auto-amélioration (Self-annealing)

Lorsqu'une erreur survient :
1. L'IA corrige le problème
2. Met à jour l'outil/script
3. Teste la correction
4. Met à jour la directive avec les nouvelles connaissances
5. Le système est maintenant plus robuste

## Bonnes Pratiques

- **Fichiers locaux** : Uniquement pour le traitement. Tout dans `.tmp/` peut être supprimé et régénéré
- **Livrables** : Toujours dans le cloud (Google Sheets, Slides, etc.)
- **Scripts** : Vérifier d'abord si un script existe dans `execution/` avant d'en créer un nouveau
- **Directives** : Documents vivants - les mettre à jour au fur et à mesure de l'apprentissage

## Mise à jour

Pour mettre à jour les dépendances Python :
```bash
python -m pip install --upgrade -r requirements.txt
```

## Support

Pour toute question ou problème, consulter [CLAUDE.md](CLAUDE.md) pour les instructions détaillées de l'architecture.
