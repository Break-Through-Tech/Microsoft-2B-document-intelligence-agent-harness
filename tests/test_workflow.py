
import workflow


def test_sufficient_evidence_routes_to_answer(monkeypatch):
    """The workflow should generate an answer when evidence is sufficient."""

    fake_evidence = {
        "is_sufficient": True,
        "chunks": [
            {
                "file": "northstar_academic_integrity_policy_2026.pdf",
                "distance": 0.15,
                "text": "A first minor violation may result in a warning.",
                "metadata": {
                    "filename": "northstar_academic_integrity_policy_2026.pdf"
                },
            }
        ],
    }

    expected_result = {
        "answer": "A first minor violation may result in a warning.",
        "citations": ["northstar_academic_integrity_policy_2026.pdf"],
        "is_sufficient": True,
    }

    monkeypatch.setattr(
        workflow,
        "inspect",
        lambda question: fake_evidence,
    )

    def fake_answer(question, inspector=None):
        evidence = inspector(question)
        assert evidence["is_sufficient"] is True
        return expected_result

    monkeypatch.setattr(workflow, "answer", fake_answer)

    app = workflow.build_workflow()

    result = app.invoke({
        "question": "What sanctions can a student receive?"
    })

    assert result["is_sufficient"] is True
    assert result["result"]["is_sufficient"] is True
    assert result["result"]["answer"] == expected_result["answer"]


def test_insufficient_evidence_routes_to_refusal(monkeypatch):
    """The workflow should refuse when evidence is insufficient."""

    fake_evidence = {
        "is_sufficient": False,
        "chunks": [],
    }

    monkeypatch.setattr(
        workflow,
        "inspect",
        lambda question: fake_evidence,
    )

    def fake_answer(question, inspector=None):
        evidence = inspector(question)

        if not evidence["is_sufficient"]:
            return {
                "answer": (
                    "I don't have enough information in the "
                    "provided documents to answer that question."
                ),
                "citations": [],
                "is_sufficient": False,
            }

    monkeypatch.setattr(workflow, "answer", fake_answer)

    app = workflow.build_workflow()

    result = app.invoke({
        "question": "What is the university's policy on interplanetary travel?"
    })

    assert result["is_sufficient"] is False
    assert result["result"]["is_sufficient"] is False
    assert result["result"]["citations"] == []


def test_answer_node_receives_retrieved_evidence(monkeypatch):
    """The answer node should reuse evidence rather than retrieve again."""

    fake_evidence = {
        "is_sufficient": True,
        "chunks": [{"text": "Relevant policy information"}],
    }

    monkeypatch.setattr(
        workflow,
        "inspect",
        lambda question: fake_evidence,
    )

    received = {}

    def fake_answer(question, inspector=None):
        received["evidence"] = inspector(question)
        return {
            "answer": "Test answer.",
            "citations": ["test.pdf"],
            "is_sufficient": True,
        }

    monkeypatch.setattr(workflow, "answer", fake_answer)

    app = workflow.build_workflow()

    app.invoke({"question": "Test question"})

    assert received["evidence"] is fake_evidence
