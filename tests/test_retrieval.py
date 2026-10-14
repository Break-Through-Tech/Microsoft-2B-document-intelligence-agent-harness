"""Tests for retrieval.py. They use the real model and the real ./chroma_db, so they are slower than test_pipeline.py."""
from retrieval import search

EXAM_QUESTION = "deadline to request rescheduling a final exam"
OFF_TOPIC_QUESTION = "where can I park my car on campus"


def test_search_returns_k_results():
    assert len(search(EXAM_QUESTION, k=3)) == 3
    assert len(search(EXAM_QUESTION, k=5)) == 5


def test_each_result_has_file_distance_and_text():
    for result in search(EXAM_QUESTION, k=3):
        assert result["file"].endswith((".pdf", ".docx"))
        assert 0 <= result["distance"] <= 2
        assert result["text"].strip()


def test_results_are_sorted_by_distance():
    distances = [result["distance"] for result in search(EXAM_QUESTION, k=5)]
    assert distances == sorted(distances)


def test_exam_question_finds_exam_policy():
    files = [result["file"] for result in search(EXAM_QUESTION, k=3)]
    assert "northstar_examination_and_grading_policy_2026.pdf" in files


def test_off_topic_question_is_farther_than_real_question():
    real = search(EXAM_QUESTION, k=1)[0]["distance"]
    off_topic = search(OFF_TOPIC_QUESTION, k=1)[0]["distance"]
    assert off_topic > real