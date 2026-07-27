"""
API REST de búsqueda semántica para n8n.
Provee un endpoint /search que n8n usa como herramienta del agente.
"""

import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from qdrant_client import QdrantClient
from langchain_huggingface import HuggingFaceEmbeddings
import uvicorn

from config import (
    QDRANT_HOST, QDRANT_PORT, QDRANT_COLLECTION, EMBEDDING_MODEL,
    API_HOST, API_PORT, SEARCH_TOP_K, SEARCH_SCORE_THRESHOLD, LOG_LEVEL,
)

logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("api")

# ── Inicialización ──────────────────────────────────────
app = FastAPI(
    title="Med360 Knowledge API",
    description="API de búsqueda semántica para el agente Dr. Medici de Medicamentum360",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

embeddings = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL,
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)

qdrant = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

# ── Modelos ─────────────────────────────────────────────
class SearchRequest(BaseModel):
    query: str
    top_k: int = SEARCH_TOP_K

class SearchResult(BaseModel):
    content: str
    source: str
    score: float

class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]
    total: int

class HealthResponse(BaseModel):
    status: str
    collection: str
    vectors: int


# ── Endpoints ───────────────────────────────────────────
@app.get("/health", response_model=HealthResponse)
async def health():
    """Verifica que la API y Qdrant estén operativos."""
    try:
        info = qdrant.get_collection(QDRANT_COLLECTION)
        return HealthResponse(
            status="ok",
            collection=QDRANT_COLLECTION,
            vectors=info.points_count,
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Qdrant no disponible: {e}")


@app.post("/search", response_model=SearchResponse)
async def search(req: SearchRequest):
    """Busca en la base de conocimiento usando embeddings."""
    try:
        query_embedding = embeddings.embed_query(req.query)

        results = qdrant.search(
            collection_name=QDRANT_COLLECTION,
            query_vector=query_embedding,
            limit=req.top_k,
            score_threshold=SEARCH_SCORE_THRESHOLD,
            with_payload=True,
        )

        hits = []
        for r in results:
            if r.payload:
                hits.append(SearchResult(
                    content=r.payload.get("page_content", "")[:1000],
                    source=r.payload.get("metadata", {}).get("source", "desconocido"),
                    score=round(r.score, 4),
                ))

        log.info("Búsqueda: '%s' → %d resultados", req.query[:80], len(hits))
        return SearchResponse(query=req.query, results=hits, total=len(hits))

    except Exception as e:
        log.error("Error en búsqueda: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sources")
async def list_sources():
    """Lista las fuentes disponibles en la base de conocimiento."""
    try:
        # Scroll para obtener todas las fuentes únicas
        sources = set()
        offset = None
        while True:
            points, offset = qdrant.scroll(
                collection_name=QDRANT_COLLECTION,
                limit=100,
                offset=offset,
                with_payload=True,
            )
            for p in points:
                if p.payload:
                    src = p.payload.get("metadata", {}).get("source", "?")
                    sources.add(src)
            if offset is None:
                break

        return {"sources": sorted(sources), "total": len(sources)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Entrypoint ──────────────────────────────────────────
if __name__ == "__main__":
    log.info("Iniciando Med360 Knowledge API en %s:%d", API_HOST, API_PORT)
    uvicorn.run(app, host=API_HOST, port=API_PORT, log_level=LOG_LEVEL.lower())
