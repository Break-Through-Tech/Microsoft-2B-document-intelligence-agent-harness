
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from answer_generation import answer, REFUSAL

CHUNK = {"file": "library_2026.pdf", "text": "# Borrowing\nStandard loans last 14 days.",
         "metadata": {"filename": "library_2026.pdf", "chunk_id": 3}}

def test_refusal_does_not_call_model():
    def no_model(**kwargs):
        raise AssertionError("Model should not run")
    result = answer("Unknown?", inspector=lambda q: {"is_sufficient": False, "chunks": []}, chat_fn=no_model)
    assert result["answer"] == REFUSAL

def test_grounded_answer_cites_section():
    def model(**kwargs):
        return {"message": {"content": "Standard loans last 14 days. [Source: library_2026.pdf, Section Borrowing]"}}
    result = answer("Loan length?", inspector=lambda q: {"is_sufficient": True, "chunks": [CHUNK]}, chat_fn=model)
    assert result["is_sufficient"]
    assert "library_2026.pdf, Section Borrowing" in result["answer"]

def test_rejects_fabricated_citation():
    def model(**kwargs):
        return {"message": {"content": "30 days. [Source: imaginary.pdf, Page 10]"}}
    result = answer("Loan length?", inspector=lambda q: {"is_sufficient": True, "chunks": [CHUNK]}, chat_fn=model)
    assert result["answer"] == REFUSAL
