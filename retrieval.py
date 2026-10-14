from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

CHROMA_PATH = Path(__file__).parent / "chroma_db"
COLLECTION_NAME = "northstar_docs"
MODEL_NAME = "nomic-ai/nomic-embed-text-v1.5"

# Load the model and the collection once, when this file is imported
_model = SentenceTransformer(MODEL_NAME, trust_remote_code=True)
_collection = chromadb.PersistentClient(path=str(CHROMA_PATH)).get_collection(COLLECTION_NAME)


def search(question: str, k: int = 5) -> list[dict]:
    """Return the k chunks closest to the question."""
    # Questions use the "search_query: " prefix (documents use "search_document: ")
    embedding = _model.encode(f"search_query: {question}").tolist()
    results = _collection.query(
        query_embeddings=[embedding],
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )
    return [
        {
            "file": meta["filename"],
            "distance": dist,
            "text": text,
            "metadata": meta,  # full metadata, so we can inspect the evidence
        }
        for text, meta, dist in zip(
            results["documents"][0], results["metadatas"][0], results["distances"][0]
        )
    ]