"""
API REST de búsqueda para n8n — versión ligera con TF-IDF + Qdrant.
No requiere descarga de modelos pesados (sentence-transformers ~120MB).
Usa scikit-learn TfidfVectorizer como fallback y Qdrant como opcional.
"""

import sys, os, json, logging, hashlib
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from config import (
    QDRANT_HOST, QDRANT_PORT, QDRANT_COLLECTION,
    EMBEDDING_MODEL, API_HOST, API_PORT, SEARCH_TOP_K,
    SEARCH_SCORE_THRESHOLD, LOG_LEVEL, KNOWLEDGE_DIR,
    CHUNK_SIZE, CHUNK_OVERLAP,
)

logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("api")

app = FastAPI(title="Med360 Knowledge API", version="1.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ── Motor de búsqueda ──────────────────────────────────────

class SearchEngine:
    """Híbrido: intenta Qdrant con embeddings, fallback a TF-IDF."""

    def __init__(self):
        self.qdrant_client: Optional[object] = None
        self.qdrant_available = False
        self.tfidf_vectorizer = None
        self.tfidf_matrix = None
        self.chunks = []
        self._init_qdrant()
        self._init_tfidf()

    def _init_qdrant(self):
        try:
            from qdrant_client import QdrantClient
            client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT, timeout=5)
            client.get_collection(QDRANT_COLLECTION)
            self.qdrant_client = client

            from langchain_huggingface import HuggingFaceEmbeddings
            self.embeddings = HuggingFaceEmbeddings(
                model_name=EMBEDDING_MODEL,
                model_kwargs={"device": "cpu"},
                encode_kwargs={"normalize_embeddings": True},
            )
            self.qdrant_available = True
            log.info("Qdrant + embeddings disponibles")
        except Exception as e:
            log.warning("Qdrant/embeddings no disponible: %s — usando TF-IDF", str(e)[:80])

    def _init_tfidf(self):
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity
            self.TfidfVectorizer = TfidfVectorizer
            self.cosine_similarity = cosine_similarity
            self._load_chunks()
            self._build_tfidf()
            log.info("TF-IDF: %d chunks indexados", len(self.chunks))
        except Exception as e:
            log.warning("TF-IDF fallback no disponible: %s", e)

    def _load_chunks(self):
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        from langchain_community.document_loaders import TextLoader

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP,
            separators=["\n## ", "\n### ", "\n#### ", "\n", " "],
        )
        self.chunks = []
        for md_file in sorted(KNOWLEDGE_DIR.glob("*.md")):
            loader = TextLoader(str(md_file), encoding="utf-8")
            docs = loader.load()
            source = md_file.stem
            split_docs = splitter.split_documents(docs)
            for d in split_docs:
                self.chunks.append({"content": d.page_content, "source": source})

    def _build_tfidf(self):
        texts = [c["content"] for c in self.chunks]
        self.tfidf_vectorizer = self.TfidfVectorizer(max_features=5000, stop_words=None)
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(texts)

    def search_tfidf(self, query: str, top_k: int = SEARCH_TOP_K):
        if not self.tfidf_vectorizer:
            return []
        q_vec = self.tfidf_vectorizer.transform([query])
        scores = self.cosine_similarity(q_vec, self.tfidf_matrix)[0]
        top_indices = scores.argsort()[-top_k:][::-1]
        results = []
        for idx in top_indices:
            if scores[idx] > SEARCH_SCORE_THRESHOLD:
                results.append({
                    "content": self.chunks[idx]["content"][:1000],
                    "source": self.chunks[idx]["source"],
                    "score": round(float(scores[idx]), 4),
                })
        return results

    def search_qdrant(self, query: str, top_k: int = SEARCH_TOP_K):
        if not self.qdrant_available:
            return []
        try:
            q_emb = self.embeddings.embed_query(query)
            hits = self.qdrant_client.search(
                collection_name=QDRANT_COLLECTION,
                query_vector=q_emb,
                limit=top_k,
                score_threshold=SEARCH_SCORE_THRESHOLD,
                with_payload=True,
            )
            results = []
            for r in hits:
                if r.payload:
                    results.append({
                        "content": r.payload.get("page_content", "")[:1000],
                        "source": r.payload.get("metadata", {}).get("source", "desconocido"),
                        "score": round(r.score, 4),
                    })
            return results
        except Exception as e:
            log.error("Error búsqueda Qdrant: %s", e)
            return []

    def search(self, query: str, top_k: int = SEARCH_TOP_K):
        results = self.search_qdrant(query, top_k)
        if not results:
            log.info("Qdrant sin resultados, usando TF-IDF")
            results = self.search_tfidf(query, top_k)
        return results


# ── Inicialización ─────────────────────────────────────────
engine = SearchEngine()

# ── Modelos ────────────────────────────────────────────────
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
    engine: str

class HealthResponse(BaseModel):
    status: str
    qdrant: bool
    tfidf: bool
    chunks: int

# ── Endpoints ──────────────────────────────────────────────
@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="ok",
        qdrant=engine.qdrant_available,
        tfidf=engine.tfidf_vectorizer is not None,
        chunks=len(engine.chunks),
    )

@app.post("/search", response_model=SearchResponse)
async def search(req: SearchRequest):
    results = engine.search(req.query, req.top_k)
    return SearchResponse(
        query=req.query,
        results=[SearchResult(**r) for r in results],
        total=len(results),
        engine="qdrant" if engine.qdrant_available and results else "tfidf",
    )

@app.get("/sources")
async def list_sources():
    sources = sorted(set(c["source"] for c in engine.chunks))
    return {"sources": sources, "total": len(sources)}

if __name__ == "__main__":
    log.info("Iniciando API en %s:%d", API_HOST, API_PORT)
    uvicorn.run(app, host=API_HOST, port=API_PORT, log_level=LOG_LEVEL.lower())
