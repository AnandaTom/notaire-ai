# -*- coding: utf-8 -*-
"""
API REST NotaireAI - Point d'entrée pour le front-end

Cette API expose l'agent autonome via HTTP pour:
- Multi-tenant (plusieurs études notariales)
- Apprentissage continu (feedback enrichit le système)
- Déploiement Modal (serverless)

Usage local:
    uvicorn api.main:app --reload --port 8000

Usage Modal:
    modal serve api.main

Endpoints:
    POST /agent/execute     - Exécuter une demande
    POST /agent/feedback    - Envoyer un feedback (apprentissage)
    GET  /dossiers          - Lister les dossiers
    GET  /dossiers/{id}     - Détail d'un dossier
    POST /dossiers          - Créer un dossier
    GET  /health            - Santé du service
"""

import os
import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager
from functools import lru_cache

from fastapi import FastAPI, HTTPException, Depends, Header, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field

# Ajouter le projet au path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import des modules NotaireAI
from execution.agent_autonome import AgentNotaire, ParseurDemandeNL, DemandeAnalysee
from execution.gestionnaires.orchestrateur import OrchestratorNotaire
from execution.chat_handler import ChatHandler, create_chat_router

# Import Supabase (optionnel - mode offline si non disponible)
SUPABASE_AVAILABLE = False
Client = None

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except (ImportError, AttributeError, Exception) as e:
    # Python 3.14+ peut avoir des problèmes avec certaines librairies
    print(f"⚠️ Supabase non disponible: {type(e).__name__}")
    SUPABASE_AVAILABLE = False


# =============================================================================
# Configuration Supabase
# =============================================================================

@lru_cache()
def get_supabase_client() -> Optional[Client]:
    """Crée un client Supabase (singleton)."""
    if not SUPABASE_AVAILABLE:
        return None

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")

    if not url or not key:
        return None

    try:
        return create_client(url, key)
    except Exception:
        return None


# =============================================================================
# Modèle d'authentification
# =============================================================================

class AuthContext(BaseModel):
    """Contexte d'authentification pour chaque requête."""
    etude_id: str
    etude_nom: str
    api_key_id: str
    permissions: Dict[str, bool]
    rate_limit_rpm: int = 60


# =============================================================================
# Modèles Pydantic
# =============================================================================

class DemandeAgent(BaseModel):
    """Demande à l'agent en langage naturel."""
    texte: str = Field(..., description="Demande en langage naturel", min_length=3)
    etude_id: Optional[str] = Field(None, description="ID de l'étude (optionnel, extrait du token)")
    options: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Options supplémentaires")


class ReponseAgent(BaseModel):
    """Réponse de l'agent."""
    succes: bool
    message: str
    intention: str

    # Données générées
    dossier_id: Optional[str] = None
    reference: Optional[str] = None
    fichier_genere: Optional[str] = None
    fichier_url: Optional[str] = None  # URL de téléchargement

    # Analyse
    analyse: Optional[Dict[str, Any]] = None

    # Résultats de recherche
    resultats: Optional[List[Dict[str, Any]]] = None

    # Métadonnées
    duree_ms: int = 0
    workflow_id: Optional[str] = None


class FeedbackRequest(BaseModel):
    """Feedback pour l'apprentissage continu."""
    dossier_id: str = Field(..., description="ID du dossier concerné")
    type_feedback: str = Field(..., description="Type: correction, validation, suggestion")

    # Contenu du feedback
    champ: Optional[str] = Field(None, description="Champ corrigé (ex: 'vendeur.nom')")
    valeur_originale: Optional[str] = None
    valeur_corrigee: Optional[str] = None

    # Nouvelle clause/pattern découvert
    nouvelle_clause: Optional[Dict[str, Any]] = None
    nouveau_pattern: Optional[str] = None

    # Note libre
    commentaire: Optional[str] = None


class FeedbackResponse(BaseModel):
    """Réponse au feedback."""
    succes: bool
    message: str
    apprentissage_id: Optional[str] = None
    impact: Optional[str] = None  # "global" ou "etude"


class DossierCreate(BaseModel):
    """Création d'un dossier."""
    type_acte: str = Field(..., description="Type: promesse_vente, vente, etc.")
    parties: List[Dict[str, Any]] = Field(..., description="Vendeurs et acquéreurs")
    biens: List[Dict[str, Any]] = Field(..., description="Biens immobiliers")
    donnees_metier: Optional[Dict[str, Any]] = Field(default_factory=dict)


class DossierResponse(BaseModel):
    """Réponse dossier."""
    id: str
    numero: str
    type_acte: str
    statut: str
    parties: List[Dict[str, Any]]
    biens: List[Dict[str, Any]]
    donnees_metier: Dict[str, Any]
    created_at: str
    updated_at: Optional[str] = None
    fichier_genere: Optional[str] = None


# =============================================================================
# Dépendances et Authentification
# =============================================================================

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# Cache en mémoire pour réduire les appels Supabase (TTL: 5 minutes)
_api_key_cache: Dict[str, tuple] = {}  # key_hash -> (auth_context, timestamp)
CACHE_TTL_SECONDS = 300


def _hash_api_key(api_key: str) -> str:
    """Hash SHA256 d'une clé API."""
    return hashlib.sha256(api_key.encode()).hexdigest()


def _get_key_prefix(api_key: str) -> str:
    """Extrait le préfixe d'une clé API (nai_xxxxxxxx)."""
    if api_key.startswith("nai_"):
        return api_key[:12]
    return api_key[:8]


async def verify_api_key(
    request: Request,
    api_key: Optional[str] = Depends(api_key_header)
) -> AuthContext:
    """
    Vérifie la clé API contre Supabase et retourne le contexte d'authentification.

    La clé API est vérifiée:
    1. D'abord dans le cache en mémoire
    2. Sinon dans Supabase agent_api_keys

    Format de clé attendu: nai_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
    """
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="Clé API manquante. Utilisez le header X-API-Key."
        )

    # Vérifier le format
    if len(api_key) < 20:
        raise HTTPException(status_code=401, detail="Format de clé API invalide")

    key_hash = _hash_api_key(api_key)
    key_prefix = _get_key_prefix(api_key)
    now = datetime.now().timestamp()

    # 1. Vérifier le cache
    if key_hash in _api_key_cache:
        cached_auth, cached_time = _api_key_cache[key_hash]
        if now - cached_time < CACHE_TTL_SECONDS:
            return cached_auth

    # 2. Vérifier dans Supabase
    supabase = get_supabase_client()

    if supabase:
        try:
            # Rechercher la clé par hash
            result = supabase.table("agent_api_keys").select(
                "id, etude_id, name, permissions, rate_limit_rpm, expires_at, revoked_at, etudes(nom)"
            ).eq("key_hash", key_hash).eq("key_prefix", key_prefix).execute()

            if not result.data:
                raise HTTPException(status_code=401, detail="Clé API invalide")

            key_data = result.data[0]

            # Vérifier si la clé est révoquée
            if key_data.get("revoked_at"):
                raise HTTPException(status_code=401, detail="Clé API révoquée")

            # Vérifier l'expiration
            if key_data.get("expires_at"):
                expires = datetime.fromisoformat(key_data["expires_at"].replace("Z", "+00:00"))
                if expires < datetime.now(expires.tzinfo):
                    raise HTTPException(status_code=401, detail="Clé API expirée")

            # Construire le contexte d'authentification
            auth_context = AuthContext(
                etude_id=key_data["etude_id"],
                etude_nom=key_data.get("etudes", {}).get("nom", "Étude inconnue"),
                api_key_id=key_data["id"],
                permissions=key_data.get("permissions", {"read": True, "write": True, "delete": False}),
                rate_limit_rpm=key_data.get("rate_limit_rpm", 60)
            )

            # Mettre en cache
            _api_key_cache[key_hash] = (auth_context, now)

            # Mettre à jour last_used_at en arrière-plan
            try:
                supabase.table("agent_api_keys").update({
                    "last_used_at": datetime.now().isoformat(),
                    "total_requests": key_data.get("total_requests", 0) + 1
                }).eq("id", key_data["id"]).execute()
            except Exception:
                pass  # Non-bloquant

            return auth_context

        except HTTPException:
            raise
        except Exception as e:
            # Fallback en mode dégradé
            print(f"⚠️ Erreur Supabase auth: {e}")

    # 3. Mode offline/dégradé - accepter avec contexte limité
    # Utile pour le développement local
    if os.getenv("NOTOMAI_DEV_MODE") == "1":
        return AuthContext(
            etude_id="dev-etude-id",
            etude_nom="Mode Développement",
            api_key_id="dev-key",
            permissions={"read": True, "write": True, "delete": False},
            rate_limit_rpm=1000
        )

    raise HTTPException(
        status_code=503,
        detail="Service d'authentification indisponible"
    )


async def get_etude_id(auth: AuthContext = Depends(verify_api_key)) -> str:
    """Extrait l'ID de l'étude du contexte d'auth."""
    return auth.etude_id


async def require_write_permission(auth: AuthContext = Depends(verify_api_key)) -> AuthContext:
    """Vérifie que la clé a les permissions d'écriture."""
    if not auth.permissions.get("write", False):
        raise HTTPException(status_code=403, detail="Permission d'écriture requise")
    return auth


async def require_delete_permission(auth: AuthContext = Depends(verify_api_key)) -> AuthContext:
    """Vérifie que la clé a les permissions de suppression."""
    if not auth.permissions.get("delete", False):
        raise HTTPException(status_code=403, detail="Permission de suppression requise")
    return auth


# =============================================================================
# Application FastAPI
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle de l'application."""
    # Startup
    print("🚀 NotaireAI API démarrée")
    yield
    # Shutdown
    print("👋 NotaireAI API arrêtée")


app = FastAPI(
    title="NotaireAI API",
    description="API REST pour l'agent autonome de génération d'actes notariaux",
    version="1.0.0",
    lifespan=lifespan
)

# CORS pour le front-end
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En prod: restreindre aux domaines autorisés
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router du chatbot
try:
    chat_router = create_chat_router()
    app.include_router(chat_router)
except Exception as e:
    print(f"⚠️ Chat router non disponible: {e}")


# =============================================================================
# Endpoints Agent
# =============================================================================

@app.post("/agent/execute", response_model=ReponseAgent, tags=["Agent"])
async def execute_agent(
    demande: DemandeAgent,
    background_tasks: BackgroundTasks,
    auth: AuthContext = Depends(require_write_permission)
):
    """
    Exécute une demande en langage naturel.

    Requiert une clé API valide avec permissions d'écriture.

    Exemples:
    - "Crée une promesse Martin→Dupont, appart 67m² Paris, 450000€"
    - "Modifie le prix à 460000€ dans le dossier 2026-001"
    - "Liste les actes récents"
    """
    import time
    debut = time.time()

    try:
        # Créer l'agent avec contexte d'étude
        agent = AgentNotaire()

        # Parser la demande
        parseur = ParseurDemandeNL()
        analyse = parseur.analyser(demande.texte)

        # Exécuter
        resultat = agent.executer(demande.texte)

        duree = int((time.time() - debut) * 1000)

        # Construire l'URL du fichier si généré
        fichier_url = None
        if resultat.fichier_genere:
            # En prod: générer une URL signée depuis Supabase Storage
            fichier_url = f"/files/{Path(resultat.fichier_genere).name}"

        # Logger pour apprentissage (asynchrone)
        background_tasks.add_task(
            log_execution,
            etude_id=auth.etude_id,
            etude_nom=auth.etude_nom,
            demande=demande.texte,
            analyse=analyse,
            resultat=resultat,
            duree_ms=duree
        )

        # Sauvegarder le dossier dans Supabase si généré
        if resultat.succes and resultat.dossier_id:
            background_tasks.add_task(
                sync_dossier_to_supabase,
                etude_id=auth.etude_id,
                dossier_id=resultat.dossier_id,
                type_acte=analyse.type_acte.value,
                fichier=resultat.fichier_genere
            )

        return ReponseAgent(
            succes=resultat.succes,
            message=resultat.message,
            intention=resultat.intention.value,
            dossier_id=resultat.dossier_id,
            reference=resultat.reference,
            fichier_genere=resultat.fichier_genere,
            fichier_url=fichier_url,
            analyse={
                "intention": analyse.intention.value,
                "type_acte": analyse.type_acte.value,
                "confiance": analyse.confiance,
                "vendeur": analyse.vendeur,
                "acquereur": analyse.acquereur,
                "bien": analyse.bien,
                "prix": analyse.prix,
                "champs_manquants": analyse.champs_manquants,
                "etude": auth.etude_nom
            },
            resultats=resultat.resultats_recherche or None,
            duree_ms=duree,
            workflow_id=resultat.workflow_id
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agent/feedback", response_model=FeedbackResponse, tags=["Agent"])
async def submit_feedback(
    feedback: FeedbackRequest,
    background_tasks: BackgroundTasks,
    auth: AuthContext = Depends(verify_api_key)
):
    """
    Soumet un feedback pour l'apprentissage continu.

    Types de feedback:
    - correction: L'agent a fait une erreur
    - validation: L'acte généré est correct
    - suggestion: Nouvelle clause ou pattern à ajouter

    Impact:
    - Les corrections et validations améliorent le modèle local de l'étude
    - Les nouvelles clauses validées sont partagées globalement
    """
    try:
        apprentissage_id = f"FB-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        impact = "etude"  # Par défaut, impact local

        # Traiter le feedback en arrière-plan
        background_tasks.add_task(
            process_feedback,
            feedback=feedback,
            etude_id=auth.etude_id,
            etude_nom=auth.etude_nom,
            apprentissage_id=apprentissage_id
        )

        # Si c'est une nouvelle clause, impact global
        if feedback.nouvelle_clause:
            impact = "global"

        return FeedbackResponse(
            succes=True,
            message="Feedback enregistré pour apprentissage",
            apprentissage_id=apprentissage_id,
            impact=impact
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Endpoints Dossiers
# =============================================================================

@app.get("/dossiers", response_model=List[DossierResponse], tags=["Dossiers"])
async def list_dossiers(
    auth: AuthContext = Depends(verify_api_key),
    limit: int = 20,
    offset: int = 0,
    type_acte: Optional[str] = None,
    statut: Optional[str] = None
):
    """
    Liste les dossiers de l'étude.

    Filtres optionnels:
    - type_acte: promesse_vente, vente, reglement_copropriete, etc.
    - statut: brouillon, en_cours, termine, archive
    """
    supabase = get_supabase_client()

    if supabase:
        try:
            query = supabase.table("dossiers").select("*").eq(
                "etude_id", auth.etude_id
            ).is_("deleted_at", "null").order(
                "created_at", desc=True
            ).range(offset, offset + limit - 1)

            if type_acte:
                query = query.eq("type_acte", type_acte)
            if statut:
                query = query.eq("statut", statut)

            result = query.execute()

            return [
                DossierResponse(
                    id=d["id"],
                    numero=d["numero"],
                    type_acte=d["type_acte"],
                    statut=d["statut"],
                    parties=d.get("parties", []),
                    biens=d.get("biens", []),
                    donnees_metier=d.get("donnees_metier", {}),
                    created_at=d["created_at"],
                    updated_at=d.get("updated_at"),
                    fichier_genere=d.get("donnees_metier", {}).get("fichier_genere")
                )
                for d in result.data
            ]

        except Exception as e:
            print(f"⚠️ Erreur Supabase dossiers: {e}")

    return []


@app.get("/dossiers/{dossier_id}", response_model=DossierResponse, tags=["Dossiers"])
async def get_dossier(
    dossier_id: str,
    auth: AuthContext = Depends(verify_api_key)
):
    """Récupère un dossier par son ID ou numéro."""
    supabase = get_supabase_client()

    if supabase:
        try:
            # Essayer par ID d'abord, puis par numéro
            result = supabase.table("dossiers").select("*").eq(
                "etude_id", auth.etude_id
            ).or_(f"id.eq.{dossier_id},numero.eq.{dossier_id}").execute()

            if result.data:
                d = result.data[0]
                return DossierResponse(
                    id=d["id"],
                    numero=d["numero"],
                    type_acte=d["type_acte"],
                    statut=d["statut"],
                    parties=d.get("parties", []),
                    biens=d.get("biens", []),
                    donnees_metier=d.get("donnees_metier", {}),
                    created_at=d["created_at"],
                    updated_at=d.get("updated_at"),
                    fichier_genere=d.get("donnees_metier", {}).get("fichier_genere")
                )

        except Exception as e:
            print(f"⚠️ Erreur Supabase dossier: {e}")

    raise HTTPException(status_code=404, detail="Dossier non trouvé")


@app.post("/dossiers", response_model=DossierResponse, tags=["Dossiers"])
async def create_dossier(
    dossier: DossierCreate,
    auth: AuthContext = Depends(require_write_permission)
):
    """Crée un nouveau dossier."""
    numero = f"{datetime.now().strftime('%Y')}-{datetime.now().strftime('%m%d%H%M%S')}"

    supabase = get_supabase_client()

    if supabase:
        try:
            result = supabase.table("dossiers").insert({
                "etude_id": auth.etude_id,
                "numero": numero,
                "type_acte": dossier.type_acte,
                "statut": "brouillon",
                "parties": dossier.parties,
                "biens": dossier.biens,
                "donnees_metier": dossier.donnees_metier
            }).execute()

            if result.data:
                d = result.data[0]
                return DossierResponse(
                    id=d["id"],
                    numero=d["numero"],
                    type_acte=d["type_acte"],
                    statut=d["statut"],
                    parties=d.get("parties", []),
                    biens=d.get("biens", []),
                    donnees_metier=d.get("donnees_metier", {}),
                    created_at=d["created_at"]
                )

        except Exception as e:
            print(f"⚠️ Erreur Supabase création: {e}")
            raise HTTPException(status_code=500, detail=f"Erreur création dossier: {e}")

    # Mode offline
    return DossierResponse(
        id="offline-uuid",
        numero=numero,
        type_acte=dossier.type_acte,
        statut="brouillon",
        parties=dossier.parties,
        biens=dossier.biens,
        donnees_metier=dossier.donnees_metier,
        created_at=datetime.now().isoformat()
    )


@app.patch("/dossiers/{dossier_id}", response_model=DossierResponse, tags=["Dossiers"])
async def update_dossier(
    dossier_id: str,
    updates: Dict[str, Any],
    auth: AuthContext = Depends(require_write_permission)
):
    """Met à jour un dossier existant."""
    supabase = get_supabase_client()

    if not supabase:
        raise HTTPException(status_code=503, detail="Service Supabase indisponible")

    try:
        # Vérifier que le dossier appartient à l'étude
        check = supabase.table("dossiers").select("id").eq(
            "id", dossier_id
        ).eq("etude_id", auth.etude_id).execute()

        if not check.data:
            raise HTTPException(status_code=404, detail="Dossier non trouvé")

        # Mise à jour
        updates["updated_at"] = datetime.now().isoformat()
        result = supabase.table("dossiers").update(updates).eq("id", dossier_id).execute()

        if result.data:
            d = result.data[0]
            return DossierResponse(
                id=d["id"],
                numero=d["numero"],
                type_acte=d["type_acte"],
                statut=d["statut"],
                parties=d.get("parties", []),
                biens=d.get("biens", []),
                donnees_metier=d.get("donnees_metier", {}),
                created_at=d["created_at"],
                updated_at=d.get("updated_at")
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur mise à jour: {e}")


@app.delete("/dossiers/{dossier_id}", tags=["Dossiers"])
async def delete_dossier(
    dossier_id: str,
    auth: AuthContext = Depends(require_delete_permission)
):
    """Supprime un dossier (soft delete)."""
    supabase = get_supabase_client()

    if not supabase:
        raise HTTPException(status_code=503, detail="Service Supabase indisponible")

    try:
        # Soft delete
        result = supabase.table("dossiers").update({
            "deleted_at": datetime.now().isoformat()
        }).eq("id", dossier_id).eq("etude_id", auth.etude_id).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Dossier non trouvé")

        return {"succes": True, "message": "Dossier supprimé"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur suppression: {e}")


# =============================================================================
# Endpoints Système
# =============================================================================

@app.get("/health", tags=["Système"])
async def health_check():
    """Vérifie la santé du service (endpoint public)."""
    supabase = get_supabase_client()
    supabase_status = "offline"

    if supabase:
        try:
            # Test de connexion
            supabase.table("etudes").select("id").limit(1).execute()
            supabase_status = "ok"
        except Exception:
            supabase_status = "error"

    return {
        "status": "healthy" if supabase_status == "ok" else "degraded",
        "version": "1.1.0",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "agent": "ok",
            "orchestrateur": "ok",
            "supabase": supabase_status
        }
    }


@app.get("/stats", tags=["Système"])
async def get_stats(auth: AuthContext = Depends(verify_api_key)):
    """Statistiques d'utilisation pour l'étude."""
    supabase = get_supabase_client()

    stats = {
        "total_actes_generes": 0,
        "actes_aujourd_hui": 0,
        "temps_moyen_generation_ms": 0,
        "taux_succes": 0.0,
        "feedbacks_recus": 0,
        "etude": auth.etude_nom
    }

    if supabase:
        try:
            # Compter les dossiers de l'étude
            dossiers = supabase.table("dossiers").select(
                "id", count="exact"
            ).eq("etude_id", auth.etude_id).execute()

            stats["total_actes_generes"] = dossiers.count or 0

            # Compter les dossiers du jour
            today = datetime.now().strftime("%Y-%m-%d")
            dossiers_today = supabase.table("dossiers").select(
                "id", count="exact"
            ).eq("etude_id", auth.etude_id).gte(
                "created_at", f"{today}T00:00:00"
            ).execute()

            stats["actes_aujourd_hui"] = dossiers_today.count or 0

            # Compter les feedbacks (via audit_logs)
            feedbacks = supabase.table("audit_logs").select(
                "id", count="exact"
            ).eq("etude_id", auth.etude_id).like(
                "action", "feedback_%"
            ).execute()

            stats["feedbacks_recus"] = feedbacks.count or 0

        except Exception as e:
            print(f"⚠️ Erreur stats: {e}")

    return stats


@app.get("/me", tags=["Système"])
async def get_current_etude(auth: AuthContext = Depends(verify_api_key)):
    """Retourne les informations de l'étude authentifiée."""
    return {
        "etude_id": auth.etude_id,
        "etude_nom": auth.etude_nom,
        "permissions": auth.permissions,
        "rate_limit_rpm": auth.rate_limit_rpm
    }


# =============================================================================
# Endpoints Clauses Intelligentes (Promesse de Vente)
# =============================================================================

@app.get("/clauses/sections", tags=["Clauses"])
async def lister_sections_clauses(
    type_sections: Optional[str] = None,
    auth: AuthContext = Depends(verify_api_key)
):
    """
    Liste les sections disponibles pour la promesse de vente.

    - **type_sections**: fixes, variables, ou None pour toutes

    Retourne les sections avec leurs conditions et priorités.
    """
    try:
        from execution.gestionnaires.gestionnaire_clauses import GestionnaireClausesIntelligent

        gestionnaire = GestionnaireClausesIntelligent()
        catalogue = gestionnaire.catalogue

        result = {"fixes": [], "variables": []}

        # Sections fixes
        if not type_sections or type_sections == "fixes":
            sections_fixes = catalogue.get("sections_fixes", {}).get("sections", [])
            result["fixes"] = [
                {
                    "id": s.get("id"),
                    "titre": s.get("titre"),
                    "niveau": s.get("niveau"),
                    "obligatoire": True
                }
                for s in sections_fixes
            ]

        # Sections variables
        if not type_sections or type_sections == "variables":
            sections_vars = catalogue.get("sections_variables", {}).get("sections", [])
            result["variables"] = [
                {
                    "id": s.get("id"),
                    "titre": s.get("titre"),
                    "condition": s.get("condition"),
                    "description": s.get("description"),
                    "priorite": s.get("priorite", "moyenne")
                }
                for s in sections_vars
            ]

        return {
            "total_fixes": len(result["fixes"]),
            "total_variables": len(result["variables"]),
            "sections": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur chargement sections: {e}")


@app.get("/clauses/profils", tags=["Clauses"])
async def lister_profils_clauses(auth: AuthContext = Depends(verify_api_key)):
    """
    Liste les profils pré-configurés pour la génération de promesses.

    Profils disponibles:
    - standard_simple: 1 vendeur → 1 acquéreur
    - standard_couple: 2 vendeurs → 2 acquéreurs
    - complexe_investisseur: Avec vente préalable, séquestre
    - sans_pret: Paiement comptant
    """
    try:
        from execution.gestionnaires.gestionnaire_clauses import GestionnaireClausesIntelligent

        gestionnaire = GestionnaireClausesIntelligent()
        profils = gestionnaire.catalogue.get("profils_type", {}).get("profils", [])

        return {
            "count": len(profils),
            "profils": profils
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur chargement profils: {e}")


@app.post("/clauses/analyser", tags=["Clauses"])
async def analyser_donnees_clauses(
    donnees: Dict[str, Any],
    profil: Optional[str] = None,
    auth: AuthContext = Depends(verify_api_key)
):
    """
    Analyse les données d'un dossier et sélectionne les sections appropriées.

    - **donnees**: Données du dossier (vendeurs, acquéreurs, bien, etc.)
    - **profil**: Profil pré-configuré optionnel

    Retourne la liste des sections à inclure avec leurs conditions évaluées.
    """
    try:
        from execution.gestionnaires.gestionnaire_clauses import GestionnaireClausesIntelligent

        gestionnaire = GestionnaireClausesIntelligent()
        resultat = gestionnaire.selectionner_sections(donnees, profil)

        return {
            "profil_utilise": profil,
            "sections_selectionnees": resultat.get("sections_actives", []),
            "sections_exclues": resultat.get("sections_exclues", []),
            "total_actives": len(resultat.get("sections_actives", [])),
            "total_exclues": len(resultat.get("sections_exclues", []))
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur analyse: {e}")


@app.post("/clauses/feedback", tags=["Clauses"])
async def soumettre_feedback_clause(
    action: str,
    cible: str,
    contenu: Optional[str] = None,
    raison: str = "",
    background_tasks: BackgroundTasks = None,
    auth: AuthContext = Depends(require_write_permission)
):
    """
    Soumet un feedback pour améliorer le catalogue de clauses.

    - **action**: ajouter, modifier, supprimer
    - **cible**: ID de la section concernée
    - **contenu**: Nouveau contenu (pour ajouter/modifier)
    - **raison**: Justification du changement

    Le feedback est enregistré et pourra être approuvé par un admin.
    """
    try:
        from execution.gestionnaires.gestionnaire_clauses import (
            GestionnaireClausesIntelligent,
            FeedbackNotaire
        )

        gestionnaire = GestionnaireClausesIntelligent()

        feedback = FeedbackNotaire(
            action=action,
            cible=cible,
            contenu=contenu,
            raison=raison,
            source_notaire=auth.etude_nom,
            dossier_reference=None,
            approuve=False  # Nécessite validation admin
        )

        resultat = gestionnaire.enregistrer_feedback(feedback)

        # Logger dans Supabase aussi
        if background_tasks:
            background_tasks.add_task(
                log_clause_feedback,
                etude_id=auth.etude_id,
                feedback_id=resultat.get("feedback_id"),
                action=action,
                cible=cible,
                contenu=contenu,
                raison=raison
            )

        return {
            "succes": True,
            "feedback_id": resultat.get("feedback_id"),
            "message": f"Feedback '{action}' sur '{cible}' enregistré",
            "statut": "en_attente_validation"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur feedback: {e}")


@app.get("/clauses/suggestions", tags=["Clauses"])
async def obtenir_suggestions_clauses(
    contexte: str,
    auth: AuthContext = Depends(verify_api_key)
):
    """
    Propose des suggestions de clauses basées sur le contexte.

    - **contexte**: Description textuelle (ex: "vente avec prêt bancaire")

    Retourne les sections les plus pertinentes pour ce contexte.
    """
    try:
        from execution.gestionnaires.gestionnaire_clauses import GestionnaireClausesIntelligent

        gestionnaire = GestionnaireClausesIntelligent()
        sections = gestionnaire.catalogue.get("sections_variables", {}).get("sections", [])

        suggestions = []
        contexte_lower = contexte.lower()

        for section in sections:
            titre = section.get("titre", "").lower()
            description = section.get("description", "").lower()

            # Score simple basé sur les mots-clés
            score = sum(
                2 if mot in titre else 1 if mot in description else 0
                for mot in contexte_lower.split()
            )

            if score > 0:
                suggestions.append({
                    "section_id": section.get("id"),
                    "titre": section.get("titre"),
                    "description": section.get("description"),
                    "score": score,
                    "condition": section.get("condition")
                })

        # Trier par score décroissant
        suggestions.sort(key=lambda x: x["score"], reverse=True)

        return {
            "contexte": contexte,
            "suggestions": suggestions[:5]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur suggestions: {e}")


async def log_clause_feedback(
    etude_id: str,
    feedback_id: str,
    action: str,
    cible: str,
    contenu: Optional[str],
    raison: str
):
    """Log le feedback de clause dans Supabase."""
    supabase = get_supabase_client()

    if supabase:
        try:
            supabase.table("audit_logs").insert({
                "etude_id": etude_id,
                "action": f"clause_feedback_{action}",
                "resource_type": "clause",
                "resource_id": cible,
                "details": {
                    "feedback_id": feedback_id,
                    "action": action,
                    "cible": cible,
                    "contenu": contenu,
                    "raison": raison,
                    "timestamp": datetime.now().isoformat()
                }
            }).execute()
        except Exception:
            pass


# =============================================================================
# Endpoints Génération de Promesses
# =============================================================================

@app.post("/promesses/generer", tags=["Promesses"])
async def generer_promesse(
    donnees: Dict[str, Any],
    type_force: Optional[str] = None,
    profil: Optional[str] = None,
    auth: AuthContext = Depends(require_write_permission)
):
    """
    Génère une promesse de vente.

    - **donnees**: Données complètes (promettants, bénéficiaires, bien, prix, etc.)
    - **type_force**: Forcer un type (standard, premium, avec_mobilier, multi_biens)
    - **profil**: Utiliser un profil prédéfini

    Détecte automatiquement le type si non spécifié.
    """
    try:
        from execution.gestionnaires.gestionnaire_promesses import GestionnairePromesses, TypePromesse

        supabase = get_supabase_client()
        gestionnaire = GestionnairePromesses(supabase_client=supabase)

        # Appliquer profil si spécifié
        if profil:
            donnees = gestionnaire.appliquer_profil(donnees, profil)

        # Forcer le type si spécifié
        type_promesse = TypePromesse(type_force) if type_force else None

        # Générer
        resultat = gestionnaire.generer(donnees, type_promesse)

        return {
            "succes": resultat.succes,
            "type_promesse": resultat.type_promesse.value,
            "fichier_md": resultat.fichier_md,
            "fichier_docx": resultat.fichier_docx,
            "sections_incluses": resultat.sections_incluses,
            "duree_generation": resultat.duree_generation,
            "erreurs": resultat.erreurs,
            "warnings": resultat.warnings,
            "metadata": resultat.metadata
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur génération promesse: {e}")


@app.post("/promesses/detecter-type", tags=["Promesses"])
async def detecter_type_promesse(
    donnees: Dict[str, Any],
    auth: AuthContext = Depends(verify_api_key)
):
    """
    Détecte automatiquement le type de promesse approprié.

    Analyse les données et retourne:
    - Le type recommandé (standard, premium, avec_mobilier, multi_biens)
    - La raison de la détection
    - Le score de confiance
    - Les sections recommandées
    """
    try:
        from execution.gestionnaires.gestionnaire_promesses import GestionnairePromesses

        gestionnaire = GestionnairePromesses()
        resultat = gestionnaire.detecter_type(donnees)

        return {
            "type_promesse": resultat.type_promesse.value,
            "raison": resultat.raison,
            "confiance": resultat.confiance,
            "sections_recommandees": resultat.sections_recommandees,
            "warnings": resultat.warnings
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur détection: {e}")


@app.post("/promesses/valider", tags=["Promesses"])
async def valider_donnees_promesse(
    donnees: Dict[str, Any],
    type_promesse: Optional[str] = None,
    auth: AuthContext = Depends(verify_api_key)
):
    """
    Valide les données avant génération.

    Retourne les erreurs, warnings et suggestions d'amélioration.
    """
    try:
        from execution.gestionnaires.gestionnaire_promesses import GestionnairePromesses, TypePromesse

        gestionnaire = GestionnairePromesses()
        type_enum = TypePromesse(type_promesse) if type_promesse else None

        resultat = gestionnaire.valider(donnees, type_enum)

        return {
            "valide": resultat.valide,
            "erreurs": resultat.erreurs,
            "warnings": resultat.warnings,
            "champs_manquants": resultat.champs_manquants,
            "suggestions": resultat.suggestions
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur validation: {e}")


@app.get("/promesses/profils", tags=["Promesses"])
async def lister_profils_promesse(auth: AuthContext = Depends(verify_api_key)):
    """
    Liste les profils prédéfinis disponibles.

    Profils:
    - particulier_simple: 1 vendeur → 1 acquéreur, standard
    - particulier_meuble: Avec liste de mobilier
    - agence_premium: Documentation complète, diagnostics exhaustifs
    - investisseur_multi: Plusieurs biens, faculté substitution
    - sans_pret: Achat comptant
    """
    try:
        from execution.gestionnaires.gestionnaire_promesses import GestionnairePromesses

        gestionnaire = GestionnairePromesses()
        profils = gestionnaire.get_profils_disponibles()

        return {
            "count": len(profils),
            "profils": profils
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur chargement profils: {e}")


@app.get("/promesses/types", tags=["Promesses"])
async def lister_types_promesse(auth: AuthContext = Depends(verify_api_key)):
    """
    Liste les types de promesse disponibles avec leurs caractéristiques.
    """
    try:
        from execution.gestionnaires.gestionnaire_promesses import GestionnairePromesses

        gestionnaire = GestionnairePromesses()
        types_info = gestionnaire.catalogue.get("types_promesse", {})

        return {
            "count": len(types_info),
            "types": [
                {
                    "id": tid,
                    "nom": tdata.get("nom"),
                    "description": tdata.get("description"),
                    "cas_usage": tdata.get("cas_usage", []),
                    "bookmarks": tdata.get("bookmarks")
                }
                for tid, tdata in types_info.items()
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur chargement types: {e}")


# =============================================================================
# Endpoints Titres de Propriété
# =============================================================================

@app.get("/titres", tags=["Titres"])
async def lister_titres(
    limit: int = 20,
    offset: int = 0,
    auth: AuthContext = Depends(verify_api_key)
):
    """
    Liste les titres de propriété de l'étude.
    """
    supabase = get_supabase_client()
    if not supabase:
        raise HTTPException(status_code=503, detail="Supabase non disponible")

    try:
        response = supabase.table("titres_propriete")\
            .select("id, reference, proprietaires, bien, created_at")\
            .eq("etude_id", auth.etude_id)\
            .order("created_at", desc=True)\
            .range(offset, offset + limit - 1)\
            .execute()

        return {
            "count": len(response.data),
            "titres": response.data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur listing titres: {e}")


@app.get("/titres/{titre_id}", tags=["Titres"])
async def get_titre(
    titre_id: str,
    auth: AuthContext = Depends(verify_api_key)
):
    """
    Récupère un titre de propriété par son ID.
    """
    supabase = get_supabase_client()
    if not supabase:
        raise HTTPException(status_code=503, detail="Supabase non disponible")

    try:
        response = supabase.table("titres_propriete")\
            .select("*")\
            .eq("id", titre_id)\
            .eq("etude_id", auth.etude_id)\
            .single()\
            .execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Titre non trouvé")

        return response.data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur récupération titre: {e}")


@app.get("/titres/recherche/adresse", tags=["Titres"])
async def rechercher_titre_adresse(
    adresse: str,
    auth: AuthContext = Depends(verify_api_key)
):
    """
    Recherche des titres par adresse (recherche floue).
    """
    try:
        from execution.gestionnaires.gestionnaire_promesses import GestionnairePromesses

        supabase = get_supabase_client()
        gestionnaire = GestionnairePromesses(supabase_client=supabase)

        resultats = gestionnaire.rechercher_titre_par_adresse(adresse)

        return {
            "query": adresse,
            "count": len(resultats),
            "resultats": resultats
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur recherche: {e}")


@app.get("/titres/recherche/proprietaire", tags=["Titres"])
async def rechercher_titre_proprietaire(
    nom: str,
    auth: AuthContext = Depends(verify_api_key)
):
    """
    Recherche des titres par nom de propriétaire.
    """
    try:
        from execution.gestionnaires.gestionnaire_promesses import GestionnairePromesses

        supabase = get_supabase_client()
        gestionnaire = GestionnairePromesses(supabase_client=supabase)

        resultats = gestionnaire.rechercher_titre_par_proprietaire(nom)

        return {
            "query": nom,
            "count": len(resultats),
            "resultats": resultats
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur recherche: {e}")


@app.post("/titres/{titre_id}/vers-promesse", tags=["Titres"])
async def convertir_titre_en_promesse(
    titre_id: str,
    beneficiaires: List[Dict[str, Any]],
    prix: Dict[str, Any],
    financement: Optional[Dict[str, Any]] = None,
    options: Optional[Dict[str, Any]] = None,
    auth: AuthContext = Depends(require_write_permission)
):
    """
    Génère une promesse à partir d'un titre de propriété existant.

    - **titre_id**: ID du titre source
    - **beneficiaires**: Liste des bénéficiaires
    - **prix**: Informations de prix
    - **financement**: Financement optionnel (prêt, etc.)
    - **options**: Options supplémentaires (mobilier, conditions, etc.)
    """
    try:
        from execution.gestionnaires.gestionnaire_promesses import GestionnairePromesses

        supabase = get_supabase_client()
        gestionnaire = GestionnairePromesses(supabase_client=supabase)

        # Charger le titre
        titre_response = supabase.table("titres_propriete")\
            .select("*")\
            .eq("id", titre_id)\
            .eq("etude_id", auth.etude_id)\
            .single()\
            .execute()

        if not titre_response.data:
            raise HTTPException(status_code=404, detail="Titre non trouvé")

        titre_data = titre_response.data

        # Générer la promesse
        donnees, resultat = gestionnaire.generer_depuis_titre(
            titre_data=titre_data,
            beneficiaires=beneficiaires,
            prix=prix,
            financement=financement,
            options=options
        )

        return {
            "succes": resultat.succes,
            "type_promesse": resultat.type_promesse.value,
            "fichier_docx": resultat.fichier_docx,
            "donnees_generees": donnees,
            "erreurs": resultat.erreurs,
            "warnings": resultat.warnings
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur conversion: {e}")


# =============================================================================
# Fonctions d'arrière-plan (apprentissage continu)
# =============================================================================

async def log_execution(
    etude_id: str,
    etude_nom: str,
    demande: str,
    analyse: DemandeAnalysee,
    resultat: Any,
    duree_ms: int
):
    """Log l'exécution pour analyse et apprentissage."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "etude_id": etude_id,
        "etude_nom": etude_nom,
        "demande": demande,
        "intention": analyse.intention.value,
        "type_acte": analyse.type_acte.value,
        "confiance": analyse.confiance,
        "succes": resultat.succes,
        "duree_ms": duree_ms,
        "dossier_id": resultat.dossier_id,
        "fichier_genere": resultat.fichier_genere
    }

    # Sauvegarder localement
    logs_dir = PROJECT_ROOT / ".tmp" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    log_file = logs_dir / f"executions_{datetime.now().strftime('%Y%m%d')}.jsonl"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

    # Sauvegarder dans Supabase audit_logs
    supabase = get_supabase_client()
    if supabase:
        try:
            supabase.table("audit_logs").insert({
                "etude_id": etude_id,
                "action": "agent_execute",
                "resource_type": "acte",
                "details": log_entry
            }).execute()
        except Exception:
            pass  # Non-bloquant

    # Analyser les patterns fréquents pour amélioration
    if analyse.confiance < 0.7:
        # Pattern mal reconnu - à améliorer
        await flag_for_improvement(demande, analyse, etude_id)


async def sync_dossier_to_supabase(
    etude_id: str,
    dossier_id: str,
    type_acte: str,
    fichier: Optional[str]
):
    """Synchronise un dossier généré vers Supabase."""
    supabase = get_supabase_client()

    if not supabase:
        return

    try:
        # Vérifier si le dossier existe
        existing = supabase.table("dossiers").select("id").eq(
            "numero", dossier_id
        ).eq("etude_id", etude_id).execute()

        donnees_metier = {"fichier_genere": fichier} if fichier else {}

        if existing.data:
            # Mettre à jour
            supabase.table("dossiers").update({
                "statut": "termine",
                "donnees_metier": donnees_metier,
                "updated_at": datetime.now().isoformat()
            }).eq("id", existing.data[0]["id"]).execute()
        else:
            # Créer
            supabase.table("dossiers").insert({
                "etude_id": etude_id,
                "numero": dossier_id,
                "type_acte": type_acte,
                "statut": "termine",
                "donnees_metier": donnees_metier
            }).execute()

    except Exception as e:
        print(f"⚠️ Erreur sync Supabase: {e}")


async def process_feedback(
    feedback: FeedbackRequest,
    etude_id: str,
    etude_nom: str,
    apprentissage_id: str
):
    """Traite le feedback pour l'apprentissage continu."""

    # 1. Logger le feedback localement
    feedback_dir = PROJECT_ROOT / ".tmp" / "feedbacks"
    feedback_dir.mkdir(parents=True, exist_ok=True)

    feedback_entry = {
        "id": apprentissage_id,
        "timestamp": datetime.now().isoformat(),
        "etude_id": etude_id,
        "etude_nom": etude_nom,
        "dossier_id": feedback.dossier_id,
        "type": feedback.type_feedback,
        "champ": feedback.champ,
        "valeur_originale": feedback.valeur_originale,
        "valeur_corrigee": feedback.valeur_corrigee,
        "nouvelle_clause": feedback.nouvelle_clause,
        "nouveau_pattern": feedback.nouveau_pattern,
        "commentaire": feedback.commentaire
    }

    feedback_file = feedback_dir / f"feedbacks_{datetime.now().strftime('%Y%m%d')}.jsonl"
    with open(feedback_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(feedback_entry, ensure_ascii=False) + "\n")

    # 2. Logger dans Supabase audit_logs
    supabase = get_supabase_client()
    if supabase:
        try:
            supabase.table("audit_logs").insert({
                "etude_id": etude_id,
                "action": f"feedback_{feedback.type_feedback}",
                "resource_type": "feedback",
                "resource_id": feedback.dossier_id if feedback.dossier_id else None,
                "details": feedback_entry
            }).execute()
        except Exception:
            pass

    # 3. Si nouvelle clause → ajouter au catalogue
    if feedback.nouvelle_clause:
        await add_clause_to_catalog(feedback.nouvelle_clause, etude_id, etude_nom)

    # 4. Si nouveau pattern → améliorer le parseur
    if feedback.nouveau_pattern:
        await add_pattern_to_parser(feedback.nouveau_pattern, feedback.type_feedback)

    # 5. Si correction fréquente → ajuster les règles
    if feedback.type_feedback == "correction":
        await analyze_correction_patterns(feedback)


async def flag_for_improvement(demande: str, analyse: DemandeAnalysee, etude_id: str):
    """Marque une demande comme nécessitant amélioration."""
    improve_dir = PROJECT_ROOT / ".tmp" / "improvements"
    improve_dir.mkdir(parents=True, exist_ok=True)

    entry = {
        "timestamp": datetime.now().isoformat(),
        "etude_id": etude_id,
        "demande": demande,
        "intention_detectee": analyse.intention.value,
        "confiance": analyse.confiance,
        "champs_manquants": analyse.champs_manquants
    }

    improve_file = improve_dir / "low_confidence.jsonl"
    with open(improve_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


async def add_clause_to_catalog(clause: Dict[str, Any], etude_id: str, etude_nom: str):
    """Ajoute une nouvelle clause au catalogue (en révision)."""
    catalog_path = PROJECT_ROOT / "schemas" / "clauses_catalogue.json"

    if catalog_path.exists():
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    else:
        catalog = {"clauses": []}

    # Ajouter la nouvelle clause avec métadonnées
    clause["source"] = f"Feedback {etude_nom} ({etude_id})"
    clause["date_ajout"] = datetime.now().strftime("%Y-%m-%d")
    clause["statut"] = "en_revision"  # Nécessite validation manuelle avant global

    catalog["clauses"].append(clause)

    catalog_path.write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    # Log de la nouvelle clause pour revue manuelle
    print(f"📝 Nouvelle clause ajoutée depuis {etude_nom}: {clause.get('nom', 'Sans nom')}")


async def add_pattern_to_parser(pattern: str, context: str):
    """Ajoute un nouveau pattern au parseur."""
    patterns_dir = PROJECT_ROOT / ".tmp" / "new_patterns"
    patterns_dir.mkdir(parents=True, exist_ok=True)

    entry = {
        "timestamp": datetime.now().isoformat(),
        "pattern": pattern,
        "context": context,
        "statut": "pending"  # À intégrer manuellement
    }

    patterns_file = patterns_dir / "new_patterns.jsonl"
    with open(patterns_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


async def analyze_correction_patterns(feedback: FeedbackRequest):
    """Analyse les patterns de correction pour amélioration."""
    # TODO: Implémenter l'analyse statistique des corrections
    # Si un même champ est souvent corrigé → ajuster la logique
    pass


# =============================================================================
# Point d'entrée Modal
# =============================================================================

# Pour Modal, décommenter et configurer:
#
# import modal
#
# stub = modal.Stub("notaire-ai")
#
# @stub.function(
#     image=modal.Image.debian_slim().pip_install("fastapi", "uvicorn", "python-docx", "jinja2"),
#     secret=modal.Secret.from_name("supabase-credentials"),
#     gpu=None,  # CPU suffisant
#     timeout=300
# )
# @modal.asgi_app()
# def fastapi_app():
#     return app


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
