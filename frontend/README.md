# Notomai Frontend

Application web frontend pour Notomai - Assistant Notarial Intelligent.

## Structure

```
frontend/
├── index.html              # Page d'accueil / landing page
├── pages/
│   ├── chat.html           # Interface chatbot principale
│   └── login.html          # Page de connexion
├── assets/
│   ├── css/
│   │   └── styles.css      # Styles CSS communs
│   ├── js/
│   │   └── app.js          # JavaScript applicatif
│   └── images/             # Images et logos
└── README.md               # Cette documentation
```

## Demarrage rapide

### Test local

```bash
# Depuis la racine du projet
cd frontend
python -m http.server 8080

# Ouvrir http://localhost:8080
```

### Pages disponibles

| Page | URL | Description |
|------|-----|-------------|
| Accueil | `/` | Landing page avec presentation |
| Chat | `/pages/chat.html` | Interface chatbot principale |
| Login | `/pages/login.html` | Page de connexion Supabase |

## Fonctionnalites

### Mode Demo

Sans authentification Supabase, l'application fonctionne en **mode demo** :
- Utilisateur par defaut : Me Charlotte Diaz
- Reponses simulees du chatbot
- Pas de sauvegarde des conversations

### Mode Production

Avec un utilisateur Supabase authentifie :
- Donnees utilisateur reelles depuis la base
- Sauvegarde des conversations
- Feedback enregistre pour amelioration continue
- Connexion a l'API Modal pour les reponses IA

## Technologies

- **HTML5** / **CSS3** : Structure et styles
- **JavaScript ES6+** : Logique applicative
- **Supabase** : Authentification et base de donnees
- **Modal** : Backend serverless (a configurer)

## Configuration

### Supabase

Les credentials Supabase sont configures dans `assets/js/app.js` :

```javascript
const SUPABASE_URL = 'https://xxx.supabase.co';
const SUPABASE_ANON_KEY = 'eyJ...';
```

### Endpoint Modal

Pour activer les reponses IA reelles :

```javascript
// Dans assets/js/app.js
const MODAL_ENDPOINT = 'https://notaire-ai--chat.modal.run';
```

## Conventions

### Styles CSS

- Variables CSS dans `:root` pour coherence
- Nomenclature BEM simplifiee
- Responsive mobile-first

### JavaScript

- Fonctions globales pour simplicite (pas de modules)
- State centralise dans l'objet `state`
- Gestion d'erreurs avec fallback mode demo

## Prochaines etapes

- [ ] Deployer sur Vercel/Netlify
- [ ] Configurer l'endpoint Modal
- [ ] Ajouter page "Mes dossiers"
- [ ] Ajouter page "Clients"
- [ ] Integrer historique des conversations
