"""Tests for chunk_index.py. Uses fake embeddings and a temporary ChromaDB, so no model is downloaded."""
from pathlib import Path

import chromadb
import pytest
from chromadb.config import Settings

from chunk_index import assign_chunk_ids, sync_collection

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


@pytest.fixture
def collection(tmp_path):
    """A fresh ChromaDB collection in a temporary folder (never ./chroma_db)."""
    client = chromadb.PersistentClient(path=str(tmp_path / "chroma"), settings=Settings(anonymized_telemetry=False))
    return client.get_or_create_collection("test_docs", metadata={"hnsw:space": "cosine"})


def fake_embedding(text):
    """Small deterministic non-zero vector, so no model is needed."""
    return [1.0, float(len(text) % 7), float(sum(map(ord, text)) % 11)]


def sync(collection, filenames, texts):
    """Build IDs for the chunks and sync them with fake embeddings."""
    ids = assign_chunk_ids(filenames, texts)
    metadatas = [{"filename": filename} for filename in filenames]
    embeddings = [fake_embedding(text) for text in texts]
    return sync_collection(collection, ids, texts, metadatas, embeddings)


def stored_ids(collection):
    return set(collection.get(include=[])["ids"])


def test_ids_are_unique_and_deterministic():
    filenames = ["a.pdf", "a.pdf", "b.docx"]
    texts = ["first chunk", "second chunk", "third chunk"]
    ids = assign_chunk_ids(filenames, texts)
    assert len(set(ids)) == len(ids)
    assert assign_chunk_ids(filenames, texts) == ids
    assert ids[0].startswith("a.pdf::")


def test_same_text_in_different_files_gets_different_ids():
    ids = assign_chunk_ids(["a.pdf", "b.pdf"], ["shared text", "shared text"])
    assert ids[0] != ids[1]


def test_same_text_twice_in_one_file_gets_different_ids():
    ids = assign_chunk_ids(["a.pdf", "a.pdf"], ["repeated text", "repeated text"])
    assert ids[0] != ids[1]
    assert ids[1] == ids[0] + "::2"


def test_syncing_twice_keeps_count(collection):
    filenames = ["a.pdf", "a.pdf", "b.docx"]
    texts = ["one", "two", "three"]
    first = sync(collection, filenames, texts)
    second = sync(collection, filenames, texts)
    assert first["total"] == second["total"] == collection.count() == 3
    assert second["deleted"] == 0


def test_changed_chunk_replaces_old_record(collection):
    sync(collection, ["a.pdf"] * 3, ["one", "two", "three"])
    old_id = assign_chunk_ids(["a.pdf"], ["two"])[0]

    result = sync(collection, ["a.pdf"] * 3, ["one", "two (edited)", "three"])

    assert result["deleted"] == 1
    assert collection.count() == 3
    assert old_id not in stored_ids(collection)


def test_document_with_fewer_chunks_drops_extra_records(collection):
    sync(collection, ["a.pdf"] * 3, ["one", "two", "three"])
    result = sync(collection, ["a.pdf"] * 2, ["one", "two"])
    assert result["deleted"] == 1
    assert collection.count() == 2


def test_old_position_ids_are_deleted(collection):
    texts = ["one", "two"]
    collection.add(
        ids=["a.pdf#chunk_0", "a.pdf#chunk_1"],
        documents=texts,
        metadatas=[{"filename": "a.pdf"}] * 2,
        embeddings=[fake_embedding(text) for text in texts],
    )

    result = sync(collection, ["a.pdf"] * 2, texts)

    assert result["deleted"] == 2
    assert collection.count() == 2
    assert not any("#chunk_" in record_id for record_id in stored_ids(collection))


def test_data_folder_has_expected_files():
    files = [path.name for path in DATA_DIR.iterdir() if path.name != ".gitkeep"]
    assert len([name for name in files if name.endswith(".pdf")]) == 7
    assert len([name for name in files if name.endswith(".docx")]) == 3
    assert "northstar_examination_and_grading_policy_2025.pdf" in files
    assert "northstar_examination_and_grading_policy_2026.pdf" in files
