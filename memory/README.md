# memory/

Dossier de memoire persistante pour les agents IA (Claude, Gemini, etc.).

Ces fichiers sont consultes automatiquement a chaque session pour eviter de
repeter les memes erreurs et garder le contexte entre sessions.

| Fichier | Role | Equivalent prompt |
|---------|------|-------------------|
| `PROJECT_STATE.md` | Fonctionnalites : done / en cours / a faire | Etat du projet |
| `CODE_MAP.md` | Stack tech, endpoints, fichiers, LOC, patterns | Architecture |
| `ISSUES.md` | Tracker des problemes — ouverts/fermes, severite, attribution | Erreurs connues |
| `JOURNAL.md` | Journal quotidien — ce qui a ete fait, modifie, decouvert, rate | Changelog |
| `CONVENTIONS.md` | Regles de code, naming, workflow Git, patterns a suivre | Conventions |
| `CHECKLIST.md` | Regles de verification avant d'affirmer, modifier, commiter | (bonus) |

**Regle** : ces fichiers sont mis a jour a chaque session de travail.
