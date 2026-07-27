# med360-agent — Configuración central
# Versión: 1.0

import os
from pathlib import Path

# ── Rutas ──────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
KNOWLEDGE_DIR = BASE_DIR / "knowledge-base"
DATA_DIR = BASE_DIR / "data"

# ── Qdrant ────────────────────────────────────────────
QDRANT_HOST = os.getenv("QDRANT_HOST", "qdrant")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "med360_knowledge")

# ── Embeddings ────────────────────────────────────────
# Proveedor: "openai" | "google" | "cohere" | "sentence_transformers"
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "sentence_transformers")
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    # modelo multilingüe ligero (~120 MB), optimizado para español
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)
EMBEDDING_DIM = 384  # dimensión del modelo MiniLM

# ── Chunking ──────────────────────────────────────────
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))

# ── API ───────────────────────────────────────────────
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8001"))
SEARCH_TOP_K = int(os.getenv("SEARCH_TOP_K", "5"))
SEARCH_SCORE_THRESHOLD = float(os.getenv("SEARCH_SCORE_THRESHOLD", "0.3"))

# ── OpenAI (opcional, si EMBEDDING_PROVIDER=openai) ───
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

# ── Google (opcional) ─────────────────────────────────
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# ── Logging ───────────────────────────────────────────
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
