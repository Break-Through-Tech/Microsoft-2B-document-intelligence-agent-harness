from retrieval import search

DISTANCE_THRESHOLD = 0.25


def inspect(question: str) -> dict[str, bool | list[dict]]:
    """Return non-2025 evidence chunks close enough to answer the question."""
    results = search(question, 5)
    current_results = [
        result
        for result in results
        if "2025" not in result["metadata"]["filename"]
    ]
    current_results.sort(key=lambda result: result["distance"])

    chunks = [
        result
        for result in current_results
        if result["distance"] <= DISTANCE_THRESHOLD
    ]
    return {"is_sufficient": bool(chunks), "chunks": chunks}
