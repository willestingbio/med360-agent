"""
Ingestión de la base de conocimiento → chunks → embeddings → Qdrant.
Uso: python src/ingest.py [--recreate]
"""

import sys
import json
import hashlib
import logging
from pathlib import Path

import tiktoken
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

# Añadir src al path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import (
    KNOWLEDGE_DIR, QDRANT_HOST, QDRANT_PORT, QDRANT_COLLECTION,
    EMBEDDING_MODEL, EMBEDDING_DIM, CHUNK_SIZE, CHUNK_OVERLAP, LOG_LEVEL,
)

logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("ingest")

recreate = "--recreate" in sys.argv


def get_document_id(content: str) -> str:
    """Genera un ID determinístico para un chunk basado en su contenido."""
    return hashlib.md5(content.encode()).hexdigest()[:16]


def load_knowledge_base() -> list:
    """Carga todos los archivos .md de la base de conocimiento."""
    docs = []
    for md_file in sorted(KNOWLEDGE_DIR.glob("*.md")):
        loader = TextLoader(str(md_file), encoding="utf-8")
        loaded = loader.load()
        source = md_file.stem
        for doc in loaded:
            doc.metadata["source"] = source
            doc.metadata["filename"] = md_file.name
        docs.extend(loaded)
        log.info("Cargado: %s (%d caracteres)", md_file.name, len(loaded[0].page_content) if loaded else 0)
    return docs


def chunk_documents(docs: list) -> list:
    """Divide los documentos en chunks con solapamiento."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n## ", "\n### ", "\n#### ", "\n", " "],
        length_function=len,
    )
    chunks = splitter.split_documents(docs)
    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = i
        chunk.metadata["doc_id"] = get_document_id(chunk.page_content)
    log.info("Documentos divididos en %d chunks (size=%d, overlap=%d)", len(chunks), CHUNK_SIZE, CHUNK_OVERLAP)
    return chunks


def create_embeddings():
    """Crea el modelo de embeddings según la configuración."""
    log.info("Cargando modelo de embeddings: %s", EMBEDDING_MODEL)
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )


def setup_qdrant():
    """Configura la colección en Qdrant."""
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    collections = [c.name for c in client.get_collections().collections]

    if QDRANT_COLLECTION in collections:
        if recreate:
            log.info("Eliminando colección existente: %s", QDRANT_COLLECTION)
            client.delete_collection(QDRANT_COLLECTION)
        else:
            log.info("Colección ya existe: %s. Usa --recreate para reindexar.", QDRANT_COLLECTION)
            return client

    log.info("Creando colección: %s (dim=%d)", QDRANT_COLLECTION, EMBEDDING_DIM)
    client.create_collection(
        collection_name=QDRANT_COLLECTION,
        vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE),
    )
    return client


def main():
    log.info("=== Ingestión de Base de Conocimiento Med360 ===")
    log.info("Directorio: %s", KNOWLEDGE_DIR)
    log.info("Qdrant: %s:%d / %s", QDRANT_HOST, QDRANT_PORT, QDRANT_COLLECTION)

    # 1. Cargar documentos
    docs = load_knowledge_base()
    if not docs:
        log.error("No se encontraron documentos en %s", KNOWLEDGE_DIR)
        sys.exit(1)

    # 2. Chunking
    chunks = chunk_documents(docs)

    # 3. Embeddings
    embeddings = create_embeddings()

    # 4. Qdrant
    client = setup_qdrant()

    # 5. Indexar
    log.info("Indexando %d chunks en Qdrant...", len(chunks))
    QdrantVectorStore.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=QDRANT_COLLECTION,
        url=f"http://{QDRANT_HOST}:{QDRANT_PORT}",
        prefer_grpc=False,
        force_recreate=False,
    )

    # 6. Resumen
    info = client.get_collection(QDRANT_COLLECTION)
    log.info("=== Indexación completada ===")
    log.info("Colección: %s", QDRANT_COLLECTION)
    log.info("Vectores: %d", info.points_count)
    log.info("Fuentes: %s", [d.metadata.get("source", "?") for d in docs])

    # 7. Guardar metadata de la indexación
    meta = {
        "collection": QDRANT_COLLECTION,
        "chunks": len(chunks),
        "embedding_model": EMBEDDING_MODEL,
        "chunk_size": CHUNK_SIZE,
        "chunk_overlap": CHUNK_OVERLAP,
    }
    (Path(__file__).resolve().parent.parent / "data" / "ingestion_meta.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False)
    )


if __name__ == "__main__":
    main()
