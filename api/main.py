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
import time
import collections
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager
from functools import lru_cache

import re
from fastapi import FastAPI, HTTPException, Depends, Header, BackgroundTasks, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field

import logging
logger = logging.getLogger(__name__)


# =============================================================================
# Utilitaires de sécurité
# =============================================================================

def sanitize_identifier(value: str) -> str:
    """Nettoie un identifiant pour éviter les injections dans les requêtes Supabase."""
    if not value or not isinstance(value, str):
        return ""
    # N'autorise que alphanumérique, tirets et underscores
    cleaned = re.sub(r'[^a-zA-Z0-9\-_.]', '', value)
    if len(cleaned) > 200:
        cleaned = cleaned[:200]
    return cleaned


def escape_like_pattern(pattern: str) -> str:
    """Échappe les caractères spéciaux dans un pattern LIKE/ILIKE."""
    if not pattern or not isinstance(pattern, str):
        return ""
    return pattern.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')


# =============================================================================
# Rate Limiter en memoire (par cle API)
# =============================================================================

class RateLimiter:
    """
    Limite le nombre de requetes par cle API par fenetre de temps.
    Utilise un algorithme de fenetre glissante en memoire.
    """

    def __init__(self, default_rpm: int = 60, window_seconds: int = 60):
        self._default_rpm = default_rpm
        self._window = window_seconds
        # {api_key_id: deque de timestamps}
        self._requests: Dict[str, collections.deque] = {}

    def check(self, key_id: str, limit_rpm: int = None) -> bool:
        """
        Verifie si la requete est autorisee.
        Retourne True si OK, False si limite depassee.
        """
        now = time.monotonic()
        limit = limit_rpm or self._default_rpm
        cutoff = now - self._window

        if key_id not in self._requests:
            self._requests[key_id] = collections.deque()

        q = self._requests[key_id]

        # Purger les anciennes requetes
        while q and q[0] < cutoff:
            q.popleft()

        if len(q) >= limit:
            return False

        q.append(now)
        return True

    def cleanup(self):
        """Nettoie les entrees perimees (appeler periodiquement)."""
        now = time.monotonic()
        cutoff = now - self._window
        empty_keys = []
        for key_id, q in self._requests.items():
            while q and q[0] < cutoff:
                q.popleft()
            if not q:
                empty_keys.append(key_id)
        for k in empty_keys:
            del self._requests[k]


rate_limiter = RateLimiter(default_rpm=60)


# Ajouter le projet au path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import des modules NotaireAI
from execution.agent_autonome import AgentNotaire, ParseurDemandeNL, DemandeAnalysee
from execution.gestionnaires.orchestrateur import OrchestratorNotaire
from execution.chat_handler import ChatHandler, create_chat_router
from execution.security.signed_urls import verify_signed_url

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
            # Rate limiting
            if not rate_limiter.check(cached_auth.api_key_id, cached_auth.rate_limit_rpm):
                raise HTTPException(
                    status_code=429,
                    detail=f"Limite de requetes depassee ({cached_auth.rate_limit_rpm}/min). Reessayez dans quelques secondes."
                )
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

            # Rate limiting
            if not rate_limiter.check(auth_context.api_key_id, auth_context.rate_limit_rpm):
                raise HTTPException(
                    status_code=429,
                    detail=f"Limite de requetes depassee ({auth_context.rate_limit_rpm}/min). Reessayez dans quelques secondes."
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
    # UNIQUEMENT en local (jamais sur Modal/production/staging)
    is_production = os.getenv("MODAL_ENVIRONMENT") or os.getenv("PRODUCTION") or os.getenv("RAILWAY_ENVIRONMENT")
    if os.getenv("NOTOMAI_DEV_MODE") == "1" and not is_production:
        print("[WARN] Mode developpement actif - authentification desactivee (local uniquement)")
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
    """Lifecycle de l'application avec health checks."""
    # Startup
    print("🚀 NotaireAI API démarrée")

    # Health check Supabase
    supabase = get_supabase_client()
    if supabase:
        try:
            # Test connexion avec une requête simple
            result = supabase.table("etudes").select("id").limit(1).execute()
            print("✅ Supabase connecté")
        except Exception as e:
            logger.warning(f"⚠️ Supabase non accessible au démarrage: {e}")
            print(f"⚠️ Supabase: {e}")
    else:
        print("⚠️ Supabase non configuré (SUPABASE_URL/KEY manquants)")

    yield

    # Shutdown
    print("👋 NotaireAI API arrêtée")


app = FastAPI(
    title="NotaireAI API",
    description="API REST pour l'agent autonome de génération d'actes notariaux",
    version="1.0.0",
    lifespan=lifespan
)

# CORS pour le front-end - domaines autorisés uniquement
ALLOWED_ORIGINS = [
    "https://notomai.fr",
    "https://www.notomai.fr",
    "https://anandatom.github.io",
    "https://notaire-ai--fastapi-app.modal.run",
    "https://notomai--notaire-ai-fastapi-app.modal.run",
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-API-Key"],
    max_age=3600,
)

# Router du chatbot
try:
    chat_router = create_chat_router()
    app.include_router(chat_router)
except Exception as e:
    print(f"⚠️ Chat router non disponible: {e}")

# Router des agents Opus 4.6
try:
    from api.agents import router as agents_router
    app.include_router(agents_router)
    print("✅ Agents Opus 4.6 router chargé")
except Exception as e:
    print(f"⚠️ Agents router non disponible: {e}")


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
        logger.error(f"Erreur interne: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Une erreur interne est survenue")


@app.post("/agent/execute-stream", tags=["Agent"])
async def execute_streaming(
    request: Request,
    auth: AuthContext = Depends(require_write_permission)
):
    """
    Exécute une demande avec streaming SSE.

    Envoie des événements progressifs pendant la génération :
    - event: status → {"etape": "...", "message": "..."}
    - event: result → résultat complet
    - event: error → {"message": "..."}
    """
    import asyncio

    body = await request.json()
    demande = body.get("demande", body.get("texte", ""))

    async def event_generator():
        import time

        yield {
            "event": "status",
            "data": json.dumps({"etape": "reception", "message": "Demande reçue..."})
        }

        yield {
            "event": "status",
            "data": json.dumps({"etape": "analyse", "message": "Analyse de la demande..."})
        }

        try:
            debut = time.time()
            agent = AgentNotaire()
            parseur = ParseurDemandeNL()
            analyse = parseur.analyser(demande)

            yield {
                "event": "status",
                "data": json.dumps({
                    "etape": "generation",
                    "message": f"Génération en cours ({analyse.type_acte.value})..."
                })
            }

            resultat = agent.executer(demande)
            duree = int((time.time() - debut) * 1000)

            fichier_url = None
            if resultat.fichier_genere:
                fichier_url = f"/files/{Path(resultat.fichier_genere).name}"

            yield {
                "event": "result",
                "data": json.dumps({
                    "succes": resultat.succes,
                    "message": resultat.message,
                    "intention": resultat.intention.value,
                    "fichier_genere": resultat.fichier_genere,
                    "fichier_url": fichier_url,
                    "duree_ms": duree,
                })
            }

        except Exception as e:
            logger.error(f"Erreur streaming: {e}", exc_info=True)
            yield {
                "event": "error",
                "data": json.dumps({"message": str(e)})
            }

    try:
        from sse_starlette.sse import EventSourceResponse
        return EventSourceResponse(event_generator())
    except ImportError:
        # Fallback si sse-starlette n'est pas installé
        raise HTTPException(
            status_code=501,
            detail="Streaming SSE non disponible. Installer: pip install sse-starlette"
        )


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
        logger.error(f"Erreur interne: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Une erreur interne est survenue")


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
    safe_id = sanitize_identifier(dossier_id)
    if not safe_id:
        raise HTTPException(status_code=400, detail="Identifiant de dossier invalide")

    if supabase:
        try:
            # Essayer par ID d'abord, puis par numéro (inputs sanitisés)
            result = supabase.table("dossiers").select("*").eq(
                "etude_id", auth.etude_id
            ).eq("id", safe_id).execute()

            if not result.data:
                result = supabase.table("dossiers").select("*").eq(
                    "etude_id", auth.etude_id
                ).eq("numero", safe_id).execute()

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
            logger.error(f"Erreur création dossier: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erreur lors de la création du dossier")

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
        logger.error(f"Erreur mise à jour: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erreur lors de la mise à jour")


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
        logger.error(f"Erreur suppression: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erreur lors de la suppression")


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


@app.get("/files/{filename}", tags=["Fichiers"])
async def download_file(filename: str, auth: AuthContext = Depends(verify_api_key)):
    """Télécharge un fichier généré (DOCX/PDF)."""
    output_dir = os.getenv("NOTAIRE_OUTPUT_DIR", "outputs")
    file_path = os.path.join(output_dir, filename)

    # Sécurité : empêcher path traversal
    real_path = os.path.realpath(file_path)
    real_output = os.path.realpath(output_dir)
    if not real_path.startswith(real_output):
        raise HTTPException(status_code=403, detail="Accès refusé")

    if not os.path.isfile(real_path):
        raise HTTPException(status_code=404, detail=f"Fichier non trouvé: {filename}")

    # Détection du type MIME selon l'extension
    ext = os.path.splitext(filename)[1].lower()
    media_types = {
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".pdf": "application/pdf",
        ".json": "application/json",
        ".md": "text/markdown",
    }
    media_type = media_types.get(ext, "application/octet-stream")

    return FileResponse(
        path=real_path,
        filename=filename,
        media_type=media_type
    )


@app.get("/download/{filename}", tags=["Fichiers"])
async def download_file_secure(
    filename: str,
    token: str = Query(..., description="Signature HMAC-SHA256"),
    expires: int = Query(..., description="Timestamp Unix d'expiration")
):
    """Télécharge un fichier généré avec URL signée.

    Sécurité:
    - Token HMAC-SHA256 vérifié
    - Expiration automatique (1h par défaut)
    - Comparaison timing-safe contre attaques temporelles

    Returns:
        FileResponse avec le document demandé

    Raises:
        403: Lien invalide ou expiré
        404: Fichier non trouvé
    """
    # Vérifier la signature HMAC
    is_valid, error_msg = verify_signed_url(filename, token, expires)
    if not is_valid:
        logger.warning(f"[DOWNLOAD] Accès refusé pour {filename}: {error_msg}")
        raise HTTPException(status_code=403, detail=error_msg)
    # Chercher dans plusieurs répertoires possibles
    output_dirs = [
        os.getenv("NOTAIRE_OUTPUT_DIR", "outputs"),
        "/outputs",  # Volume Modal
        ".tmp/promesses_generees",
        "/root/project/.tmp/promesses_generees",
    ]

    real_path = None
    for output_dir in output_dirs:
        file_path = os.path.join(output_dir, filename)
        candidate = os.path.realpath(file_path)
        real_base = os.path.realpath(output_dir)
        # Sécurité : vérifier que le fichier est dans un répertoire autorisé (path traversal)
        if os.path.isfile(candidate) and candidate.startswith(real_base + os.sep):
            real_path = candidate
            break

    if not real_path:
        raise HTTPException(status_code=404, detail=f"Fichier non trouvé: {filename}")

    # Détection du type MIME selon l'extension
    ext = os.path.splitext(filename)[1].lower()
    media_types = {
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".pdf": "application/pdf",
        ".json": "application/json",
        ".md": "text/markdown",
    }
    media_type = media_types.get(ext, "application/octet-stream")

    return FileResponse(
        path=real_path,
        filename=filename,
        media_type=media_type
    )


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
        logger.error(f"Erreur chargement sections: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erreur lors du chargement")


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
        logger.error(f"Erreur chargement profils: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erreur lors du chargement")


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
        logger.error(f"Erreur analyse: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erreur lors de l'analyse")


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
        logger.error(f"Erreur feedback: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erreur lors de l'enregistrement du feedback")


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
        logger.error(f"Erreur suggestions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erreur lors de la recherche de suggestions")


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

    Détecte automatiquement le type et sous-type (viager, creation, etc.) si non spécifié.
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
            "categorie_bien": resultat.categorie_bien.value if hasattr(resultat, 'categorie_bien') else None,
            "sous_type": resultat.metadata.get("sous_type") if resultat.metadata else None,
            "fichier_md": resultat.fichier_md,
            "fichier_docx": resultat.fichier_docx,
            "sections_incluses": resultat.sections_incluses,
            "duree_generation": resultat.duree_generation,
            "erreurs": resultat.erreurs,
            "warnings": resultat.warnings,
            "metadata": resultat.metadata
        }

    except Exception as e:
        logger.error(f"Erreur génération promesse: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erreur lors de la génération")


@app.post("/promesses/detecter-type", tags=["Promesses"])
async def detecter_type_promesse(
    donnees: Dict[str, Any],
    auth: AuthContext = Depends(verify_api_key)
):
    """
    Détecte automatiquement le type de promesse approprié (3 niveaux v2.0.0).

    Analyse les données et retourne:
    - Le type recommandé (standard, premium, avec_mobilier, multi_biens)
    - La catégorie de bien (copropriete, hors_copropriete, terrain_a_batir)
    - Le sous-type conditionnel (viager, creation, lotissement, etc.)
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
            "categorie_bien": resultat.categorie_bien.value,
            "sous_type": resultat.sous_type,
            "raison": resultat.raison,
            "confiance": resultat.confiance,
            "sections_recommandees": resultat.sections_recommandees,
            "warnings": resultat.warnings
        }

    except Exception as e:
        logger.error(f"Erreur détection: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erreur lors de la détection")


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
        logger.error(f"Erreur validation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erreur lors de la validation")


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
        logger.error(f"Erreur chargement profils: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erreur lors du chargement")


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
        logger.error(f"Erreur chargement types: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erreur lors du chargement")


# =============================================================================
# Endpoints Questions & Réponses (Q&R) - Collecte interactive
# =============================================================================

# Import CollecteurInteractif (optionnel, graceful fallback)
COLLECTEUR_DISPONIBLE = False
try:
    from execution.agent_autonome import CollecteurInteractif
    COLLECTEUR_DISPONIBLE = True
except ImportError:
    logger.warning("CollecteurInteractif non disponible")


class AnswerSubmission(BaseModel):
    """Soumission de réponses Q&R."""
    dossier_id: str = Field(..., description="ID du dossier / session Q&R")
    answers: Dict[str, Any] = Field(..., description="Dict {question_id ou variable: valeur}")


class PrefillRequest(BaseModel):
    """Pré-remplissage de données."""
    categorie_bien: str = Field("copropriete", description="copropriete, hors_copropriete, terrain_a_batir")
    titre_data: Optional[Dict[str, Any]] = Field(None, description="Données extraites d'un titre")
    beneficiaires: Optional[List[Dict[str, Any]]] = Field(None, description="Liste des bénéficiaires")
    prix: Optional[Dict[str, Any]] = Field(None, description="Données de prix")
    donnees: Optional[Dict[str, Any]] = Field(None, description="Données libres à pré-remplir")


def _get_or_create_collecteur(
    dossier_id: str,
    categorie_bien: str = "copropriete",
    prefill: Optional[Dict[str, Any]] = None,
) -> 'CollecteurInteractif':
    """Charge ou crée une session de collecte Q&R."""
    # Essayer de charger une session existante
    collecteur = CollecteurInteractif.load_state(dossier_id)
    if collecteur:
        return collecteur

    # Créer une nouvelle session avec pré-remplissage
    prefill_data = prefill or {}
    # Injecter la catégorie dans les métadonnées
    if '_metadata' not in prefill_data:
        prefill_data['_metadata'] = {}
    prefill_data['_metadata']['categorie_bien'] = categorie_bien

    collecteur = CollecteurInteractif('promesse_vente', prefill=prefill_data)
    # Sauvegarder immédiatement
    collecteur.save_state(dossier_id)
    return collecteur


@app.get("/questions/promesse", tags=["Questions"])
async def get_questions(
    categorie: str = "copropriete",
    section: Optional[str] = None,
    sous_type: Optional[str] = None,
    dossier_id: Optional[str] = None,
    auth: AuthContext = Depends(verify_api_key),
):
    """
    Retourne les questions de promesse filtrées par catégorie, section et sous-type.

    - **categorie**: copropriete, hors_copropriete, terrain_a_batir
    - **section**: Clé de section optionnelle (ex: 2_promettant, 15_viager)
    - **sous_type**: Sous-type conditionnel (viager, creation, lotissement, etc.)
      Si sous_type=viager, inclut automatiquement la section 15_viager
    - **dossier_id**: ID de session existante pour récupérer les valeurs déjà saisies
    """
    if not COLLECTEUR_DISPONIBLE:
        raise HTTPException(status_code=503, detail="Module Q&R non disponible")

    try:
        # Charger ou créer le collecteur
        if dossier_id:
            collecteur = _get_or_create_collecteur(dossier_id, categorie)
        else:
            prefill = {'_metadata': {'categorie_bien': categorie}}
            collecteur = CollecteurInteractif('promesse_vente', prefill=prefill)

        if section:
            # Questions d'une section spécifique
            questions = collecteur.get_questions_for_section(section)
            return {
                "section": section,
                "categorie": categorie,
                "sous_type": sous_type,
                "questions": questions,
                "count": len(questions),
            }
        else:
            # Liste des sections avec statut
            sections = collecteur.get_sections_list()

            # Si sous_type=viager, signaler que section 15_viager est active
            viager_active = sous_type == "viager"

            return {
                "categorie": categorie,
                "sous_type": sous_type,
                "sections": sections,
                "count": len(sections),
                "viager_questions_active": viager_active,
            }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erreur Q&R questions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erreur lors du chargement des questions")


@app.post("/questions/promesse/answer", tags=["Questions"])
async def submit_answers(
    submission: AnswerSubmission,
    background_tasks: BackgroundTasks,
    auth: AuthContext = Depends(require_write_permission),
):
    """
    Soumet des réponses pour des questions de promesse.

    - **dossier_id**: ID du dossier / session
    - **answers**: Dict {question_id ou chemin_variable: valeur}

    Retourne les questions suivantes non répondues et la progression.
    """
    if not COLLECTEUR_DISPONIBLE:
        raise HTTPException(status_code=503, detail="Module Q&R non disponible")

    dossier_id = sanitize_identifier(submission.dossier_id)
    if not dossier_id:
        raise HTTPException(status_code=400, detail="dossier_id invalide")

    try:
        collecteur = _get_or_create_collecteur(dossier_id)

        # Soumettre les réponses
        result = collecteur.submit_answers(submission.answers)

        # Sauvegarder l'état
        collecteur.save_state(dossier_id)

        # Progression mise à jour
        progress = collecteur.get_progress()

        # Log en arrière-plan
        background_tasks.add_task(
            _log_qr_activity, auth.etude_id, dossier_id,
            "answer", len(submission.answers)
        )

        return {
            "succes": result['accepted'] > 0,
            "accepted": result['accepted'],
            "errors": result['errors'],
            "progress": progress,
        }

    except Exception as e:
        logger.error(f"Erreur Q&R answer: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erreur lors de la soumission")


@app.get("/questions/promesse/progress/{dossier_id}", tags=["Questions"])
async def get_progress(
    dossier_id: str,
    auth: AuthContext = Depends(verify_api_key),
):
    """
    Retourne la progression de collecte pour un dossier.

    - **dossier_id**: ID du dossier / session Q&R
    """
    if not COLLECTEUR_DISPONIBLE:
        raise HTTPException(status_code=503, detail="Module Q&R non disponible")

    dossier_id = sanitize_identifier(dossier_id)
    if not dossier_id:
        raise HTTPException(status_code=400, detail="dossier_id invalide")

    try:
        collecteur = CollecteurInteractif.load_state(dossier_id)
        if not collecteur:
            raise HTTPException(status_code=404, detail="Session Q&R non trouvée")

        progress = collecteur.get_progress()
        return {
            "dossier_id": dossier_id,
            "donnees": collecteur.donnees,
            **progress,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur Q&R progress: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erreur lors du chargement")


@app.post("/questions/promesse/prefill", tags=["Questions"])
async def prefill_questions(
    request: PrefillRequest,
    auth: AuthContext = Depends(require_write_permission),
):
    """
    Pré-remplit les données d'une session Q&R depuis des données existantes.

    Crée une nouvelle session avec les données pré-remplies et retourne
    le taux de couverture et les champs manquants.
    """
    if not COLLECTEUR_DISPONIBLE:
        raise HTTPException(status_code=503, detail="Module Q&R non disponible")

    try:
        # Construire les données de pré-remplissage
        prefill = request.donnees or {}

        # Intégrer titre si fourni
        if request.titre_data:
            for key, value in request.titre_data.items():
                if key not in prefill and value:
                    prefill[key] = value

        # Intégrer bénéficiaires
        if request.beneficiaires:
            prefill['beneficiaires'] = request.beneficiaires

        # Intégrer prix
        if request.prix:
            prefill['prix'] = request.prix

        # Générer un dossier_id unique
        import uuid
        dossier_id = f"qr-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8]}"

        collecteur = _get_or_create_collecteur(
            dossier_id, request.categorie_bien, prefill
        )

        progress = collecteur.get_progress()

        return {
            "dossier_id": dossier_id,
            "categorie_bien": request.categorie_bien,
            "progress": progress,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erreur Q&R prefill: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erreur lors du pré-remplissage")


async def _log_qr_activity(
    etude_id: str, dossier_id: str, action: str, count: int
):
    """Log d'activité Q&R en arrière-plan."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "etude_id": etude_id,
        "dossier_id": dossier_id,
        "action": f"qr_{action}",
        "count": count,
    }

    logs_dir = PROJECT_ROOT / ".tmp" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_file = logs_dir / f"qr_activity_{datetime.now().strftime('%Y%m%d')}.jsonl"

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")


# =============================================================================
# Endpoints Workflow Promesse (orchestration complète)
# =============================================================================

# État en mémoire des workflows (en prod: Supabase)
_workflow_states: Dict[str, Dict[str, Any]] = {}


class WorkflowStartRequest(BaseModel):
    """Démarrage d'un workflow de promesse."""
    categorie_bien: str = Field("copropriete", description="copropriete, hors_copropriete, terrain_a_batir")
    sous_type: Optional[str] = Field(None, description="Sous-type: viager, creation, lotissement, etc.")
    titre_id: Optional[str] = Field(None, description="ID du titre source (pré-remplissage)")
    prefill: Optional[Dict[str, Any]] = Field(None, description="Données de pré-remplissage")


class WorkflowSubmitRequest(BaseModel):
    """Soumission de réponses dans un workflow."""
    answers: Dict[str, Any] = Field(..., description="Dict {question_id ou variable: valeur}")


@app.post("/workflow/promesse/start", tags=["Workflow"])
async def workflow_start(
    request: WorkflowStartRequest,
    background_tasks: BackgroundTasks,
    auth: AuthContext = Depends(require_write_permission),
):
    """
    Démarre un workflow de génération de promesse.

    Retourne un workflow_id, les premières questions et les données pré-remplies.
    """
    if not COLLECTEUR_DISPONIBLE:
        raise HTTPException(status_code=503, detail="Module Q&R non disponible")

    try:
        import uuid
        workflow_id = f"wf-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8]}"

        # Charger données de pré-remplissage
        prefill = request.prefill or {}
        titre_data = None

        if request.titre_id:
            supabase = get_supabase_client()
            if supabase:
                titre_resp = supabase.table("titres_propriete")\
                    .select("*")\
                    .eq("id", request.titre_id)\
                    .eq("etude_id", auth.etude_id)\
                    .single()\
                    .execute()
                if titre_resp.data:
                    titre_data = titre_resp.data
                    for key, value in titre_data.items():
                        if key not in prefill and value and key not in ('id', 'etude_id', 'created_at'):
                            prefill[key] = value

        # Créer le collecteur
        collecteur = _get_or_create_collecteur(
            workflow_id, request.categorie_bien, prefill
        )

        # Première section avec questions
        sections = collecteur.get_sections_list()
        first_section = sections[0] if sections else None
        first_questions = []
        if first_section:
            first_questions = collecteur.get_questions_for_section(first_section['key'])

        progress = collecteur.get_progress()

        # Sauvegarder l'état du workflow
        _workflow_states[workflow_id] = {
            'etude_id': auth.etude_id,
            'categorie_bien': request.categorie_bien,
            'sous_type': request.sous_type,
            'titre_id': request.titre_id,
            'status': 'collecting',
            'current_section_idx': 0,
            'created_at': datetime.now().isoformat(),
            'steps_completed': ['start'],
        }

        background_tasks.add_task(
            _log_qr_activity, auth.etude_id, workflow_id, "workflow_start", 0
        )

        return {
            "workflow_id": workflow_id,
            "categorie_bien": request.categorie_bien,
            "sous_type": request.sous_type,
            "status": "collecting",
            "sections": sections,
            "current_section": first_section,
            "questions": first_questions,
            "progress": progress,
            "viager_questions_active": request.sous_type == "viager",
        }

    except Exception as e:
        logger.error(f"Erreur workflow start: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erreur lors du démarrage du workflow")


@app.post("/workflow/promesse/{workflow_id}/submit", tags=["Workflow"])
async def workflow_submit(
    workflow_id: str,
    request: WorkflowSubmitRequest,
    background_tasks: BackgroundTasks,
    auth: AuthContext = Depends(require_write_permission),
):
    """
    Soumet des réponses dans un workflow et retourne les questions suivantes.
    """
    if not COLLECTEUR_DISPONIBLE:
        raise HTTPException(status_code=503, detail="Module Q&R non disponible")

    workflow_id = sanitize_identifier(workflow_id)
    if not workflow_id:
        raise HTTPException(status_code=400, detail="workflow_id invalide")

    try:
        collecteur = CollecteurInteractif.load_state(workflow_id)
        if not collecteur:
            raise HTTPException(status_code=404, detail="Workflow non trouvé")

        # Soumettre les réponses
        result = collecteur.submit_answers(request.answers)
        collecteur.save_state(workflow_id)

        # Progression
        progress = collecteur.get_progress()
        sections = collecteur.get_sections_list()

        # Trouver la prochaine section incomplète
        next_section = None
        next_questions = []
        for s in sections:
            if not s['complete']:
                next_section = s
                next_questions = collecteur.get_questions_for_section(s['key'])
                break

        # Mettre à jour l'état
        wf_state = _workflow_states.get(workflow_id, {})
        if next_section is None:
            wf_state['status'] = 'ready_to_generate'
            wf_state['steps_completed'] = wf_state.get('steps_completed', []) + ['collect_complete']
        else:
            wf_state['status'] = 'collecting'

        _workflow_states[workflow_id] = wf_state

        background_tasks.add_task(
            _log_qr_activity, auth.etude_id, workflow_id,
            "workflow_submit", len(request.answers)
        )

        return {
            "workflow_id": workflow_id,
            "status": wf_state.get('status', 'collecting'),
            "accepted": result['accepted'],
            "errors": result['errors'],
            "next_section": next_section,
            "next_questions": next_questions,
            "progress": progress,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur workflow submit: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erreur lors de la soumission")


@app.post("/workflow/promesse/{workflow_id}/generate", tags=["Workflow"])
async def workflow_generate(
    workflow_id: str,
    background_tasks: BackgroundTasks,
    auth: AuthContext = Depends(require_write_permission),
):
    """
    Déclenche la génération du document promesse.

    Pipeline: validation → détection type → assemblage → export DOCX → URL.
    Retourne le statut et l'URL du fichier si streaming non supporté.

    Pour le streaming SSE, utiliser GET /workflow/promesse/{id}/generate-stream.
    """
    if not COLLECTEUR_DISPONIBLE:
        raise HTTPException(status_code=503, detail="Module Q&R non disponible")

    workflow_id = sanitize_identifier(workflow_id)
    if not workflow_id:
        raise HTTPException(status_code=400, detail="workflow_id invalide")

    try:
        collecteur = CollecteurInteractif.load_state(workflow_id)
        if not collecteur:
            raise HTTPException(status_code=404, detail="Workflow non trouvé")

        donnees = collecteur.donnees
        wf_state = _workflow_states.get(workflow_id, {})
        wf_state['status'] = 'generating'
        wf_state['generation_started'] = datetime.now().isoformat()
        _workflow_states[workflow_id] = wf_state

        # --- Étape 1: Validation ---
        from execution.gestionnaires.gestionnaire_promesses import GestionnairePromesses
        gestionnaire = GestionnairePromesses()

        validation = gestionnaire.valider(donnees)
        # validation is ResultatValidationPromesse dataclass, not dict
        if not validation.valide:
            wf_state['status'] = 'validation_failed'
            _workflow_states[workflow_id] = wf_state
            return {
                "workflow_id": workflow_id,
                "status": "validation_failed",
                "erreurs": validation.erreurs,
                "warnings": validation.warnings,
            }

        # --- Étape 2: Détection 3 niveaux (catégorie + type + sous-type) ---
        detection = gestionnaire.detecter_type(donnees)

        # --- Étape 3: Génération ---
        resultat = gestionnaire.generer(donnees)

        wf_state['status'] = 'completed' if resultat.succes else 'generation_failed'
        wf_state['steps_completed'] = wf_state.get('steps_completed', []) + [
            'validation', 'detection', 'assembly', 'export'
        ]
        wf_state['fichier_docx'] = resultat.fichier_docx
        wf_state['generation_completed'] = datetime.now().isoformat()
        _workflow_states[workflow_id] = wf_state

        # Sync en arrière-plan
        background_tasks.add_task(
            _log_qr_activity, auth.etude_id, workflow_id, "workflow_generate", 1
        )

        response = {
            "workflow_id": workflow_id,
            "status": wf_state['status'],
            "categorie_bien": detection.categorie_bien.value,
            "sous_type": detection.sous_type,
            "type_promesse": resultat.type_promesse.value if hasattr(resultat, 'type_promesse') else None,
            "fichier_docx": resultat.fichier_docx,
            "erreurs": resultat.erreurs if hasattr(resultat, 'erreurs') else [],
            "warnings": resultat.warnings if hasattr(resultat, 'warnings') else [],
        }

        if resultat.fichier_docx:
            filename = Path(resultat.fichier_docx).name
            response["fichier_url"] = f"/files/{filename}"

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur workflow generate: {e}", exc_info=True)
        wf_state = _workflow_states.get(workflow_id, {})
        wf_state['status'] = 'generation_failed'
        wf_state['error'] = str(e)
        _workflow_states[workflow_id] = wf_state
        raise HTTPException(status_code=500, detail="Erreur lors de la génération")


@app.get("/workflow/promesse/{workflow_id}/generate-stream", tags=["Workflow"])
async def workflow_generate_stream(
    workflow_id: str,
    auth: AuthContext = Depends(require_write_permission),
):
    """
    Génération avec streaming SSE des étapes.

    Événements envoyés:
    - step: {step: "validation", message: "Validation des données..."}
    - step: {step: "detection", message: "Détection catégorie..."}
    - step: {step: "assembly", message: "Assemblage du document..."}
    - step: {step: "export", message: "Export DOCX..."}
    - complete: {fichier_url: "/files/xxx.docx"}
    - error: {message: "..."}
    """
    if not COLLECTEUR_DISPONIBLE:
        raise HTTPException(status_code=503, detail="Module Q&R non disponible")

    workflow_id = sanitize_identifier(workflow_id)
    if not workflow_id:
        raise HTTPException(status_code=400, detail="workflow_id invalide")

    collecteur = CollecteurInteractif.load_state(workflow_id)
    if not collecteur:
        raise HTTPException(status_code=404, detail="Workflow non trouvé")

    async def event_generator():
        import asyncio
        donnees = collecteur.donnees
        wf_state = _workflow_states.get(workflow_id, {})

        try:
            # Étape 1: Validation
            yield {"event": "step", "data": json.dumps(
                {"step": "validation", "message": "Validation des données..."}
            )}
            await asyncio.sleep(0.1)

            from execution.gestionnaires.gestionnaire_promesses import GestionnairePromesses
            gestionnaire = GestionnairePromesses()
            validation = gestionnaire.valider(donnees)

            # validation is ResultatValidationPromesse dataclass, not dict
            if not validation.valide:
                yield {"event": "error", "data": json.dumps(
                    {"message": "Validation échouée", "erreurs": validation.erreurs}
                )}
                return

            # Étape 2: Détection 3 niveaux
            yield {"event": "step", "data": json.dumps(
                {"step": "detection", "message": "Détection catégorie + sous-type..."}
            )}
            await asyncio.sleep(0.1)
            detection = gestionnaire.detecter_type(donnees)
            sous_info = f" ({detection.sous_type})" if detection.sous_type else ""

            # Étape 3: Assemblage
            yield {"event": "step", "data": json.dumps(
                {"step": "assembly", "message": f"Assemblage template {detection.categorie_bien.value}{sous_info}..."}
            )}
            await asyncio.sleep(0.1)

            # Étape 4: Export
            yield {"event": "step", "data": json.dumps(
                {"step": "export", "message": "Export DOCX en cours..."}
            )}

            resultat = gestionnaire.generer(donnees)

            if resultat.succes:
                filename = Path(resultat.fichier_docx).name if resultat.fichier_docx else None
                wf_state['status'] = 'completed'
                wf_state['fichier_docx'] = resultat.fichier_docx
                _workflow_states[workflow_id] = wf_state

                yield {"event": "complete", "data": json.dumps({
                    "message": "Document prêt",
                    "fichier_url": f"/files/{filename}" if filename else None,
                    "type_promesse": resultat.type_promesse.value if hasattr(resultat, 'type_promesse') else None,
                    "sous_type": detection.sous_type,
                })}
            else:
                yield {"event": "error", "data": json.dumps({
                    "message": "Génération échouée",
                    "erreurs": resultat.erreurs if hasattr(resultat, 'erreurs') else [],
                })}

        except Exception as e:
            logger.error(f"Erreur streaming workflow: {e}", exc_info=True)
            yield {"event": "error", "data": json.dumps({
                "message": str(e),
            })}

    try:
        from sse_starlette.sse import EventSourceResponse
        return EventSourceResponse(event_generator())
    except ImportError:
        raise HTTPException(
            status_code=503,
            detail="Streaming SSE non disponible. Installer: pip install sse-starlette"
        )


@app.get("/workflow/promesse/{workflow_id}/status", tags=["Workflow"])
async def workflow_status(
    workflow_id: str,
    auth: AuthContext = Depends(verify_api_key),
):
    """
    Retourne l'état d'un workflow de promesse.
    """
    workflow_id = sanitize_identifier(workflow_id)
    if not workflow_id:
        raise HTTPException(status_code=400, detail="workflow_id invalide")

    # Vérifier l'état en mémoire
    wf_state = _workflow_states.get(workflow_id)

    # Si pas en mémoire, vérifier si session Q&R existe
    if not wf_state and COLLECTEUR_DISPONIBLE:
        collecteur = CollecteurInteractif.load_state(workflow_id)
        if collecteur:
            progress = collecteur.get_progress()
            return {
                "workflow_id": workflow_id,
                "status": "collecting",
                "progress": progress,
            }

    if not wf_state:
        raise HTTPException(status_code=404, detail="Workflow non trouvé")

    result = {
        "workflow_id": workflow_id,
        "status": wf_state.get('status', 'unknown'),
        "categorie_bien": wf_state.get('categorie_bien'),
        "created_at": wf_state.get('created_at'),
        "steps_completed": wf_state.get('steps_completed', []),
    }

    if wf_state.get('fichier_docx'):
        filename = Path(wf_state['fichier_docx']).name
        result['fichier_url'] = f"/files/{filename}"

    if wf_state.get('error'):
        result['error'] = wf_state['error']

    # Ajouter la progression Q&R si disponible
    if COLLECTEUR_DISPONIBLE:
        collecteur = CollecteurInteractif.load_state(workflow_id)
        if collecteur:
            result['progress'] = collecteur.get_progress()

    return result


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
        logger.error(f"Erreur listing titres: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erreur lors de la recherche")


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
        logger.error(f"Erreur récupération titre: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erreur lors de la recherche")


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
        logger.error(f"Erreur recherche: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erreur lors de la recherche")


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
        logger.error(f"Erreur recherche: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erreur lors de la recherche")


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
        logger.error(f"Erreur conversion: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erreur lors de la conversion")


# =============================================================================
# Endpoints Document Review (revue paragraphe par paragraphe)
# =============================================================================


def split_markdown_sections(markdown_text: str) -> List[Dict[str, Any]]:
    """Découpe un document Markdown en sections par heading H2."""
    sections = []
    current_title = "Introduction"
    current_content: List[str] = []
    section_idx = 0

    for line in markdown_text.split("\n"):
        if line.startswith("## "):
            if current_content or section_idx == 0:
                content_text = "\n".join(current_content).strip()
                if content_text:
                    sections.append({
                        "id": f"section_{section_idx}",
                        "index": section_idx,
                        "title": current_title,
                        "content": content_text,
                        "heading_level": 2,
                    })
                    section_idx += 1
            current_title = line[3:].strip()
            current_content = []
        else:
            current_content.append(line)

    # Dernière section
    content_text = "\n".join(current_content).strip()
    if content_text:
        sections.append({
            "id": f"section_{section_idx}",
            "index": section_idx,
            "title": current_title,
            "content": content_text,
            "heading_level": 2,
        })

    return sections


@app.get("/document/{workflow_id}/sections", tags=["Document Review"])
async def get_document_sections(
    workflow_id: str,
    auth: AuthContext = Depends(verify_api_key),
):
    """
    Découpe un document Markdown généré en sections pour review paragraphe par paragraphe.
    Retourne la liste des sections avec titre et contenu.
    """
    # Chercher le fichier .md du workflow
    md_file = None
    search_dirs = [
        PROJECT_ROOT / ".tmp" / "actes_generes",
        Path(os.getenv("NOTAIRE_OUTPUT_DIR", "outputs")),
        PROJECT_ROOT / "outputs",
    ]

    for search_dir in search_dirs:
        if not search_dir.exists():
            continue
        # Chercher dans le dossier du workflow
        workflow_dir = search_dir / workflow_id
        if workflow_dir.exists():
            for f in workflow_dir.glob("*.md"):
                md_file = f
                break
        # Chercher par nom de fichier contenant le workflow_id
        if not md_file:
            for f in search_dir.glob(f"*{workflow_id}*.md"):
                md_file = f
                break
        if md_file:
            break

    if not md_file:
        raise HTTPException(
            status_code=404,
            detail=f"Document non trouvé pour le workflow {workflow_id}"
        )

    try:
        markdown_text = md_file.read_text(encoding="utf-8")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lecture document: {e}")

    sections = split_markdown_sections(markdown_text)

    return {
        "workflow_id": workflow_id,
        "fichier": str(md_file.name),
        "sections_count": len(sections),
        "sections": sections,
    }


class ParagraphFeedbackRequest(BaseModel):
    """Feedback sur une section/paragraphe du document généré."""
    workflow_id: str = Field(..., description="ID du workflow de génération")
    section_id: str = Field(..., description="ID de la section (ex: section_3)")
    section_title: str = Field("", description="Titre de la section")
    action: str = Field(..., description="approuver, corriger, commenter")
    contenu: Optional[str] = Field(None, description="Texte corrigé ou commentaire")
    raison: Optional[str] = Field(None, description="Raison du feedback")


@app.post("/feedback/paragraphe", tags=["Document Review"])
async def submit_paragraph_feedback(
    request: ParagraphFeedbackRequest,
    background_tasks: BackgroundTasks,
    auth: AuthContext = Depends(require_write_permission),
):
    """
    Enregistre un feedback paragraphe par paragraphe dans Supabase.
    Utilisé par la notaire pour valider ou corriger chaque section du document.
    """
    try:
        supabase = get_supabase_client()
    except Exception:
        supabase = None

    feedback_data = {
        "etude_id": auth.etude_id,
        "section_id": request.section_id,
        "action": request.action,
        "contenu": request.contenu,
        "raison": request.raison or "",
        "metadata": {
            "source": "paragraph_review",
            "workflow_id": request.workflow_id,
            "section_title": request.section_title,
        },
    }

    if supabase:
        try:
            result = supabase.table("feedbacks_promesse").insert(
                feedback_data
            ).execute()
            feedback_id = result.data[0]["id"] if result.data else None
        except Exception as e:
            logger.warning(f"Supabase insert feedback failed: {e}")
            feedback_id = None
    else:
        feedback_id = None
        # Fallback: log local
        logs_dir = PROJECT_ROOT / ".tmp" / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        log_file = logs_dir / "paragraph_feedbacks.jsonl"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(feedback_data, ensure_ascii=False) + "\n")

    return {
        "succes": True,
        "feedback_id": feedback_id,
        "message": f"Feedback '{request.action}' enregistré pour {request.section_id}",
    }


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
