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
        # General questions about academic integrity
        (
            "What are the rules for using AI in homework?",
            [
                make_result("northstar_academic_integrity_policy_2026.pdf", 0.1),
                make_result("northstar_examination_and_grading_policy_2025.pdf", 0.3),
            ],
            {
                "is_sufficient": True,
                "chunks": [make_result("northstar_academic_integrity_policy_2026.pdf", 0.1)],
            },
        ),
        (
            "What are the consequences of plagiarism?",
            [
                make_result("northstar_academic_integrity_policy_2026.pdf", 0.2),
            ],
            {
                "is_sufficient": True,
                "chunks": [make_result("northstar_academic_integrity_policy_2026.pdf", 0.2)],
            },
        ),
        # Specific questions about admissions and enrollment
        (
            "How do I apply for enrollment in 2026?",
            [
                make_result("northstar_admissions_and_enrollment_guide_2026.pdf", 0.1),
            ],
            {
                "is_sufficient": True,
                "chunks": [make_result("northstar_admissions_and_enrollment_guide_2026.pdf", 0.1)],
            },
        ),
        (
            "What documents are required for enrollment?",
            [
                make_result("northstar_admissions_and_enrollment_guide_2026.pdf", 0.15),
            ],
            {
                "is_sufficient": True,
                "chunks": [make_result("northstar_admissions_and_enrollment_guide_2026.pdf", 0.15)],
            },
        ),
        # Questions with no sufficient information
        (
            "If I miss a class, can I do it online?",
            [],
            {"is_sufficient": False, "chunks": []},
        ),
        (
            "Does the university support remote internships?",
            [],
            {"is_sufficient": False, "chunks": []},
        ),
        (
            "How can I get my phone repaired?",
            [],
            {"is_sufficient": False, "chunks": []},
        ),
        (
            "Who works at mental health services?",
            [],
            {"is_sufficient": False, "chunks": []},
        ),
        (
            "Are there scholarships dedicated to international students?",
            [],
            {"is_sufficient": False, "chunks": []},
        ),
        # Questions about attendance and participation
        (
            "What is the attendance policy for missing classes?",
            [
                make_result("northstar_attendance_and_course_participation_policy_2026.docx", 0.1),
            ],
            {
                "is_sufficient": True,
                "chunks": [make_result("northstar_attendance_and_course_participation_policy_2026.docx", 0.1)],
            },
        ),
        (
            "Can I participate in a make-up session if a miss a lab session?",
            [
                make_result("northstar_attendance_and_course_participation_policy_2026.docx", 0.2),
            ],
            {
                "is_sufficient": True,
                "chunks": [make_result("northstar_attendance_and_course_participation_policy_2026.docx", 0.2)],
            },
        ),
        # Questions about grading policies
        (
            "What is the grading scale?",
            [
                make_result("northstar_examination_and_grading_policy_2026.pdf", 0.1),
            ],
            {
                "is_sufficient": True,
                "chunks": [make_result("northstar_examination_and_grading_policy_2026.pdf", 0.1)],
            },
        ),
        (
            "How can I reschedule an exam?",
            [
                make_result("northstar_examination_and_grading_policy_2026.pdf", 0.2),
            ],
            {
                "is_sufficient": True,
                "chunks": [make_result("northstar_examination_and_grading_policy_2026.pdf", 0.2)],
            },
        ),
        # Questions about internships
        (
            "What are the requirements for internships?",
            [
                make_result("northstar_internship_guidelines_2026.docx", 0.1),
            ],
            {
                "is_sufficient": True,
                "chunks": [make_result("northstar_internship_guidelines_2026.docx", 0.1)],
            },
        ),
        (
            "Can I get credit for an internship?",
            [
                make_result("northstar_internship_guidelines_2026.docx", 0.2),
            ],
            {
                "is_sufficient": True,
                "chunks": [make_result("northstar_internship_guidelines_2026.docx", 0.2)],
            },
        ),
        # Questions about laboratory safety
        (
            "What are the lab hours?",
            [
                make_result("northstar_laboratory_safety_handbook_2026.docx", 0.1),
            ],
            {
                "is_sufficient": True,
                "chunks": [make_result("northstar_laboratory_safety_handbook_2026.docx", 0.1)],
            },
        ),
        (
            "What should I do in case of a lab accident?",
            [
                make_result("northstar_laboratory_safety_handbook_2026.docx", 0.2),
            ],
            {
                "is_sufficient": True,
                "chunks": [make_result("northstar_laboratory_safety_handbook_2026.docx", 0.2)],
            },
        ),
        # Questions about library services
        (
            "How can I borrow books from the library?",
            [
                make_result("northstar_library_services_and_use_rules_2026.pdf", 0.1),
            ],
            {
                "is_sufficient": True,
                "chunks": [make_result("northstar_library_services_and_use_rules_2026.pdf", 0.1)],
            },
        ),
        (
            "What are the library opening hours?",
            [
                make_result("northstar_library_services_and_use_rules_2026.pdf", 0.2),
            ],
            {
                "is_sufficient": True,
                "chunks": [make_result("northstar_library_services_and_use_rules_2026.pdf", 0.2)],
            },
        ),
        # Questions about scholarships
        (
            "How can I apply for financial aid?",
            [
                make_result("northstar_scholarship_and_financial_aid_guide_2026.pdf", 0.1),
            ],
            {
                "is_sufficient": True,
                "chunks": [make_result("northstar_scholarship_and_financial_aid_guide_2026.pdf", 0.1)],
            },
        ),
        (
            "What scholarships are available for 2026?",
            [
                make_result("northstar_scholarship_and_financial_aid_guide_2026.pdf", 0.2),
            ],
            {
                "is_sufficient": True,
                "chunks": [make_result("northstar_scholarship_and_financial_aid_guide_2026.pdf", 0.2)],
            },
        ),
        # Questions about campus services
        (
            "What student services are available on campus?",
            [
                make_result("northstar_student_handbook_and_campus_services_2026.pdf", 0.1),
            ],
            {
                "is_sufficient": True,
                "chunks": [make_result("northstar_student_handbook_and_campus_services_2026.pdf", 0.1)],
            },
        ),
        (
            "How can I access disability accessibility resources?",
            [
                make_result("northstar_student_handbook_and_campus_services_2026.pdf", 0.2),
            ],
            {
                "is_sufficient": True,
                "chunks": [make_result("northstar_student_handbook_and_campus_services_2026.pdf", 0.2)],
            },
        ),
    ],
)
def test_inspect_realistic_questions(monkeypatch, question, results, expected):
    monkeypatch.setattr("inspection.search", lambda q, k: results)
    answer = inspect(question)
    assert answer == expected