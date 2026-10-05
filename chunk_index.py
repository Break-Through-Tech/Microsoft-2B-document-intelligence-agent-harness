"""Content-hash chunk IDs and ChromaDB sync, so re-indexing updates records instead of duplicating them."""
import hashlib


def assign_chunk_ids(filenames, texts):
    """Return one ID per chunk: "<filename>::<sha256[:16]>", with "::2", "::3"... when a text repeats in the same file."""
    ids = []
    seen = {}
    for filename, text in zip(filenames, texts, strict=True):
        normalized = " ".join(text.split())
        digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]
        base = f"{filename}::{digest}"
        seen[base] = seen.get(base, 0) + 1
        ids.append(base if seen[base] == 1 else f"{base}::{seen[base]}")
    return ids


def sync_collection(collection, ids, documents, metadatas, embeddings):
    """Upsert all chunks, then delete every record whose ID is not in `ids`."""
    collection.upsert(ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings)
    keep = set(ids)
    stale = [record_id for record_id in collection.get(include=[])["ids"] if record_id not in keep]
    if stale:  # Chroma rejects delete() with an empty ID list
        collection.delete(ids=stale)
    return {"upserted": len(ids), "deleted": len(stale), "total": collection.count()}
