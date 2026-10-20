import pytest
from inspection import inspect


def make_result(filename, distance):
    return {
        "file": filename,
        "distance": distance,
        "text": f"Evidence from {filename}",
        "metadata": {"filename": filename},
    }


@pytest.mark.parametrize(
    "question, results, expected",
    [
        # Test cases with sufficient and up-to-date information
        (
            "What is the policy for 2026?",
            [
                make_result("policy-2026.pdf", 0.1),
                make_result("guide-2026.pdf", 0.2),
            ],
            {
                "is_sufficient": True,
                "chunks": [
                    make_result("policy-2026.pdf", 0.1),
                    make_result("guide-2026.pdf", 0.2),
                ],
            },
        ),
        (
            "What is the guide for 2026?",
            [
                make_result("guide-2026.pdf", 0.15),
                make_result("policy-2025.pdf", 0.3),
            ],
            {
                "is_sufficient": True,
                "chunks": [make_result("guide-2026.pdf", 0.15)],
            },
        ),
        # Test cases with insufficient or outdated information
        (
            "What is the policy for 2027?",
            [
                make_result("policy-2025.pdf", 0.1),
                make_result("guide-2025.pdf", 0.2),
            ],
            {"is_sufficient": False, "chunks": []},
        ),
        (
            "What is the guide for 2027?",
            [
                make_result("guide-2025.pdf", 0.3),
                make_result("policy-2024.pdf", 0.4),
            ],
            {"is_sufficient": False, "chunks": []},
        ),
        # Test prioritization of latest data
        (
            "What is the policy?",
            [
                make_result("policy-2026.pdf", 0.2),
                make_result("policy-2025.pdf", 0.1),
                make_result("guide-2026.pdf", 0.25),
            ],
            {
                "is_sufficient": True,
                "chunks": [
                    make_result("policy-2026.pdf", 0.2),
                    make_result("guide-2026.pdf", 0.25),
                ],
            },
        ),
        (
            "What is the guide?",
            [
                make_result("guide-2026.pdf", 0.1),
                make_result("guide-2025.pdf", 0.2),
            ],
            {
                "is_sufficient": True,
                "chunks": [make_result("guide-2026.pdf", 0.1)],
            },
        ),
        # Edge cases with no results
        (
            "What is the policy for 2028?",
            [],
            {"is_sufficient": False, "chunks": []},
        ),
        (
            "What is the guide for 2028?",
            [],
            {"is_sufficient": False, "chunks": []},
        ),
        # Edge cases with distant results
        (
            "What is the policy?",
            [
                make_result("policy-2026.pdf", 0.35),
                make_result("policy-2025.pdf", 0.4),
            ],
            {"is_sufficient": False, "chunks": []},
        ),
        (
            "What is the guide?",
            [
                make_result("guide-2026.pdf", 0.3),
                make_result("guide-2025.pdf", 0.35),
            ],
            {"is_sufficient": False, "chunks": []},
        ),
    ]
    + [
        # Additional cases to reach 20 tests
        (
            f"Test question {i}",
            [
                make_result(f"file-{i}-2026.pdf", 0.1),
                make_result(f"file-{i}-2025.pdf", 0.2),
            ],
            {
                "is_sufficient": True,
                "chunks": [make_result(f"file-{i}-2026.pdf", 0.1)],
            },
        )
        for i in range(11, 21)
    ],
)
def test_inspect_balanced_cases(monkeypatch, question, results, expected):
    monkeypatch.setattr("inspection.search", lambda q, k: results)
    answer = inspect(question)
    assert answer == expected