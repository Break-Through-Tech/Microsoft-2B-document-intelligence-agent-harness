
from pathlib import Path
from tempfile import TemporaryDirectory

import chromadb
import pymupdf
import pymupdf4llm
from docx import Document
from markitdown import MarkItDown
from langchain_text_splitters import RecursiveCharacterTextSplitter

from chunk_index import assign_chunk_ids
from retrieval import _collection, _model


# Match the original notebook's chunking configuration.
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=550,
    chunk_overlap=75,
    separators=["\n\n", "\n", ". ", " ", ""]
)


def extract_text(file_path: Path, file_type: str):
    """Extract text blocks with optional page numbers and document metadata."""

    if file_type == "pdf":
        with pymupdf.open(str(file_path)) as document:
            pages = pymupdf4llm.to_markdown(document, page_chunks=True)
            metadata = document.metadata or {}
        return [(page["text"], number) for number, page in enumerate(pages, 1)], metadata

    elif file_type == "docx":
        text = MarkItDown().convert(str(file_path)).text_content

        doc = Document(str(file_path))
        props = doc.core_properties

        metadata = {
            "format": "DOCX",
            "title": props.title or "",
            "author": props.author or "",
            "subject": props.subject or "",
            "keywords": props.keywords or "",
            "creator": props.last_modified_by or "",
        }

    elif file_type == "txt":
        try:
            text = file_path.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError:
            text = file_path.read_text(encoding="cp1252")

        metadata = {"format": "TXT"}

    else:
        raise ValueError(f"Unsupported file type: {file_type}")

    return [(text, None)], metadata


def ingest_uploaded_file(uploaded_file):
    """
    Extract, chunk, embed, and store one uploaded document.

    Existing Northstar documents are preserved.
    Re-uploading a filename replaces its previous uploaded chunks.
    """

    filename = Path(uploaded_file.name).name
    file_type = Path(filename).suffix.lower().lstrip(".")

    if file_type not in {"pdf", "docx", "txt"}:
        raise ValueError("Only PDF, DOCX, and TXT files are supported.")

    with TemporaryDirectory() as temp_dir:
        file_path = Path(temp_dir) / filename
        file_path.write_bytes(uploaded_file.getvalue())

        text_blocks, doc_metadata = extract_text(file_path, file_type)

    if not any(text and text.strip() for text, _ in text_blocks):
        raise ValueError(f"No readable text was extracted from {filename}.")

    chunk_pages = [
        (chunk, page)
        for text, page in text_blocks
        if text
        for chunk in text_splitter.split_text(text)
    ]
    chunks = [chunk for chunk, _ in chunk_pages]

    if not chunks:
        raise ValueError(f"No text chunks were created for {filename}.")

    # Prefix IDs to prevent collisions with the original Northstar corpus.
    id_filenames = [f"uploaded::{filename}"] * len(chunks)
    ids = assign_chunk_ids(id_filenames, chunks)

    documents = chunks
    metadatas = []

    for chunk_number, (_, page) in enumerate(chunk_pages):
        metadata = {
            "filename": filename,
            "filepath": f"uploaded/{filename}",
            "file_type": file_type,
            "chunk_id": chunk_number,
            "doc_title": str(doc_metadata.get("title") or filename),
            "doc_author": str(doc_metadata.get("author") or ""),
            "doc_format": str(doc_metadata.get("format") or file_type.upper()),
            "creation_date": str(doc_metadata.get("creationDate") or ""),
            "mod_date": str(doc_metadata.get("modDate") or ""),
            "uploaded_by_user": True,
        }
        if page is not None:
            metadata["page"] = page
        metadatas.append(metadata)

    # Generate embeddings using the same model and document prefix
    # as the original notebook.
    embedding_inputs = [
        f"search_document: {chunk}" for chunk in documents
    ]

    embeddings = _model.encode(
        embedding_inputs,
        show_progress_bar=False,
        batch_size=32
    ).tolist()

    # Find previous uploads with the same filename.
    previous = _collection.get(
        where={
            "$and": [
                {"uploaded_by_user": True},
                {"filename": filename},
            ]
        },
        include=[]
    )

    old_ids = set(previous["ids"])
    new_ids = set(ids)

    # Upsert first, then remove stale chunks from the previous upload.
    _collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings
    )

    stale_ids = list(old_ids - new_ids)

    if stale_ids:
        _collection.delete(ids=stale_ids)

    return {
        "filename": filename,
        "chunks_added": len(chunks),
        "total_chunks": _collection.count()
    }


def clear_uploaded_documents():
    """Delete only user-uploaded documents, preserving the original corpus."""

    uploaded = _collection.get(
        where={"uploaded_by_user": True},
        include=[]
    )

    ids = uploaded["ids"]

    if ids:
        _collection.delete(ids=ids)

    return len(ids)
