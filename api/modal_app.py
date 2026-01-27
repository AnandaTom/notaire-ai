# -*- coding: utf-8 -*-
"""
Modal App - Déploiement serverless de NotaireAI

Ce fichier configure le déploiement sur Modal.com pour:
- Scaling automatique (0 → N instances)
- Multi-tenant (isolation par étude via Supabase RLS)
- Apprentissage continu (feedback centralisé)

Déploiement:
    modal deploy api/modal_app.py

Test local:
    modal serve api/modal_app.py

Endpoints déployés:
    https://notaire-ai--api.modal.run/agent/execute
    https://notaire-ai--api.modal.run/dossiers
    https://notaire-ai--api.modal.run/health
"""

import modal
from pathlib import Path

# =============================================================================
# Configuration Modal
# =============================================================================

# Image Docker avec les dépendances
image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "fastapi>=0.104.0",
    "uvicorn>=0.24.0",
    "python-docx>=1.1.0",
    "jinja2>=3.1.2",
    "pydantic>=2.5.0",
    "supabase>=2.0.0",
    "python-multipart>=0.0.6",
)

# Stub Modal
app = modal.App(
    name="notaire-ai",
    image=image,
    secrets=[
        modal.Secret.from_name("supabase-credentials"),  # SUPABASE_URL, SUPABASE_KEY
    ]
)

# Volume pour les fichiers générés (persistant)
volume = modal.Volume.from_name("notaire-ai-outputs", create_if_missing=True)

# =============================================================================
# Fonctions Modal
# =============================================================================

@app.function(
    volumes={"/outputs": volume},
    timeout=300,  # 5 minutes max par requête
    memory=1024,  # 1 GB RAM
    cpu=1.0,
    allow_concurrent_inputs=10,  # 10 requêtes simultanées par instance
    container_idle_timeout=60,  # Garde le container 60s après la dernière requête
)
@modal.asgi_app()
def fastapi_app():
    """Point d'entrée FastAPI sur Modal."""
    import sys
    import os

    # Ajouter le projet au path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))

    # Configurer les chemins pour Modal
    os.environ["NOTAIRE_OUTPUT_DIR"] = "/outputs"

    # Importer l'app FastAPI
    from api.main import app
    return app


@app.function(
    schedule=modal.Cron("0 2 * * *"),  # Tous les jours à 2h du matin
    timeout=600,
)
def daily_learning_job():
    """
    Job quotidien d'apprentissage continu.

    Analyse les logs et feedbacks pour:
    - Identifier les patterns fréquents
    - Améliorer les règles de parsing
    - Enrichir les catalogues
    """
    import os
    import json
    from datetime import datetime, timedelta

    print(f"[{datetime.now()}] Démarrage du job d'apprentissage...")

    try:
        from supabase import create_client

        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")

        if not url or not key:
            print("⚠️ Credentials Supabase manquants")
            return

        supabase = create_client(url, key)
        yesterday = (datetime.now() - timedelta(days=1)).isoformat()

        # 1. Analyser les exécutions à faible confiance
        low_confidence = supabase.table("audit_logs").select(
            "details"
        ).eq("action", "agent_execute").gte(
            "created_at", yesterday
        ).execute()

        patterns_a_ameliorer = []
        for log in low_confidence.data or []:
            details = log.get("details", {})
            if details.get("confiance", 1.0) < 0.7:
                patterns_a_ameliorer.append({
                    "demande": details.get("demande"),
                    "confiance": details.get("confiance"),
                    "intention": details.get("intention")
                })

        print(f"  Patterns à améliorer: {len(patterns_a_ameliorer)}")

        # 2. Analyser les corrections
        corrections = supabase.table("audit_logs").select(
            "details"
        ).like("action", "feedback_correction").gte(
            "created_at", yesterday
        ).execute()

        champs_corriges = {}
        for fb in corrections.data or []:
            champ = fb.get("details", {}).get("champ", "inconnu")
            champs_corriges[champ] = champs_corriges.get(champ, 0) + 1

        print(f"  Champs fréquemment corrigés: {champs_corriges}")

        # 3. Générer un rapport
        rapport = {
            "date": datetime.now().isoformat(),
            "patterns_a_ameliorer": len(patterns_a_ameliorer),
            "corrections_total": len(corrections.data or []),
            "champs_corriges": champs_corriges,
            "top_patterns": patterns_a_ameliorer[:10]
        }

        # Sauvegarder le rapport
        supabase.table("audit_logs").insert({
            "action": "daily_learning_report",
            "resource_type": "system",
            "details": rapport
        }).execute()

        print(f"[{datetime.now()}] Rapport généré avec succès")

    except Exception as e:
        print(f"❌ Erreur job apprentissage: {e}")

    print(f"[{datetime.now()}] Job d'apprentissage terminé")


@app.function(
    schedule=modal.Cron("0 3 * * 0"),  # Tous les dimanches à 3h
    timeout=1800,
)
def weekly_catalog_sync():
    """
    Synchronisation hebdomadaire des catalogues.

    Propage les nouvelles clauses validées à tous les notaires.
    """
    import os
    import json
    from datetime import datetime
    from pathlib import Path

    print(f"[{datetime.now()}] Synchronisation des catalogues...")

    try:
        # Charger le catalogue local
        project_root = Path(__file__).parent.parent
        catalog_path = project_root / "schemas" / "clauses_catalogue.json"

        if not catalog_path.exists():
            print("  Catalogue non trouvé")
            return

        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        clauses = catalog.get("clauses", [])

        # Compter les clauses par statut
        stats = {"en_revision": 0, "active": 0, "validee": 0}
        nouvelles_validees = []

        for clause in clauses:
            statut = clause.get("statut", "active")
            stats[statut] = stats.get(statut, 0) + 1

            # Les clauses en_revision depuis plus de 7 jours et avec validation manuelle
            # deviennent actives (simulation - en prod ce serait basé sur review)
            if statut == "validee":
                clause["statut"] = "active"
                nouvelles_validees.append(clause.get("nom", "Sans nom"))

        print(f"  Stats clauses: {stats}")
        print(f"  Clauses nouvellement actives: {len(nouvelles_validees)}")

        # Sauvegarder le catalogue mis à jour
        catalog["derniere_sync"] = datetime.now().isoformat()
        catalog_path.write_text(
            json.dumps(catalog, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

        # Logger dans Supabase
        from supabase import create_client

        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")

        if url and key:
            supabase = create_client(url, key)
            supabase.table("audit_logs").insert({
                "action": "weekly_catalog_sync",
                "resource_type": "system",
                "details": {
                    "date": datetime.now().isoformat(),
                    "stats": stats,
                    "nouvelles_actives": nouvelles_validees
                }
            }).execute()

    except Exception as e:
        print(f"❌ Erreur sync catalogue: {e}")

    print(f"[{datetime.now()}] Synchronisation terminée")


# =============================================================================
# Fonctions utilitaires exposées
# =============================================================================

@app.function(timeout=120)
def generate_deed(
    etude_id: str,
    type_acte: str,
    donnees: dict,
    output_name: str
) -> dict:
    """
    Génère un acte notarial (appelable depuis d'autres services).

    Args:
        etude_id: ID de l'étude
        type_acte: Type d'acte (promesse_vente, vente, etc.)
        donnees: Données complètes de l'acte
        output_name: Nom du fichier de sortie

    Returns:
        dict avec le chemin du fichier et les métadonnées
    """
    import sys
    from pathlib import Path

    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))

    from execution.orchestrateur_notaire import OrchestratorNotaire

    output_path = f"/outputs/{etude_id}/{output_name}"

    orch = OrchestratorNotaire(verbose=False)
    result = orch.generer_acte_complet(type_acte, donnees, output_path)

    return {
        "succes": result.statut == "succes",
        "fichier": output_path if result.statut == "succes" else None,
        "workflow_id": result.workflow_id,
        "duree_ms": result.duree_totale_ms,
        "score_conformite": result.score_conformite,
        "erreurs": result.erreurs
    }


@app.function(timeout=60)
def parse_request(texte: str) -> dict:
    """
    Parse une demande en langage naturel (appelable depuis d'autres services).

    Args:
        texte: Demande en langage naturel

    Returns:
        dict avec l'analyse détaillée
    """
    import sys
    from pathlib import Path

    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))

    from execution.agent_autonome import ParseurDemandeNL

    parseur = ParseurDemandeNL()
    analyse = parseur.analyser(texte)

    return {
        "intention": analyse.intention.value,
        "type_acte": analyse.type_acte.value,
        "confiance": analyse.confiance,
        "vendeur": analyse.vendeur,
        "acquereur": analyse.acquereur,
        "bien": analyse.bien,
        "prix": analyse.prix,
        "reference_dossier": analyse.reference_dossier,
        "modifications": analyse.modifications,
        "champs_manquants": analyse.champs_manquants
    }


# =============================================================================
# CLI Modal
# =============================================================================

@app.local_entrypoint()
def main():
    """Point d'entrée local pour tests."""
    print("NotaireAI Modal App")
    print("=" * 40)
    print()
    print("Commandes disponibles:")
    print("  modal serve api/modal_app.py   # Test local")
    print("  modal deploy api/modal_app.py  # Déploiement")
    print()
    print("Une fois déployé, l'API sera accessible à:")
    print("  https://notaire-ai--fastapi-app.modal.run/")
    print()

    # Test du parsing
    result = parse_request.remote("Crée une promesse Martin→Dupont, 450000€")
    print("Test parsing:")
    print(f"  Intention: {result['intention']}")
    print(f"  Confiance: {result['confiance']:.0%}")
