"""
API Tests
"""
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import app.main as main
from app.data import COURSE_CATALOG
from app.services import parse_prereqs, upcoming_semesters

client = TestClient(main.app)

CODES = {c["code"] for c in COURSE_CATALOG}


@pytest.fixture(autouse=True)
def force_rule_based(monkeypatch):
    monkeypatch.setattr(main.recommendation_service, "ai_enabled", False)


@pytest.fixture
def profile():
    path = Path(__file__).parent / "profiles" / "profile_01.json"
    return json.loads(path.read_text())


def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "healthy"
    assert isinstance(body["ai_enabled"], bool)


def test_catalog_integrity():
    assert len(CODES) == len(COURSE_CATALOG)
    for course in COURSE_CATALOG:
        for prereq in parse_prereqs(course["prerequisites"]):
            assert prereq in CODES, f"{course['code']} references missing {prereq}"


def test_courses_filters():
    res = client.get("/api/courses", params={"major": "Information Systems"})
    assert res.status_code == 200
    body = res.json()
    assert body["total"] > 0
    assert all(c["major"] == "Information Systems" for c in body["courses"])

    res = client.get("/api/courses", params={"search": "machine learning"})
    assert res.status_code == 200
    assert res.json()["total"] > 0


def test_course_detail_and_404():
    res = client.get("/api/courses/CS101")
    assert res.status_code == 200
    assert res.json()["code"] == "CS101"

    res = client.get("/api/courses/NOPE999")
    assert res.status_code == 404


def test_prerequisite_chain_and_404():
    res = client.get("/api/prerequisites/CS301")
    assert res.status_code == 200
    chain = res.json()["chain"]
    chain_codes = [c["code"] for c in chain]
    assert chain_codes[-1] == "CS301"
    assert {"CS101", "CS201", "CS250", "MATH201"}.issubset(set(chain_codes))

    res = client.get("/api/prerequisites/NOPE999")
    assert res.status_code == 404


def test_recommendations(profile):
    res = client.post("/api/recommendations", json=profile)
    assert res.status_code == 200
    body = res.json()
    assert body["source"] == "rules"
    recs = body["recommendations"]
    assert 0 < len(recs) <= 8
    completed = set(profile["completedCourses"])
    for rec in recs:
        assert rec["courseCode"] in CODES
        assert rec["courseCode"] not in completed
        assert rec["priority"] in {"high", "medium", "low"}
    semesters = set(upcoming_semesters())
    assert {rec["semester"] for rec in recs}.issubset(semesters)


def test_plan_respects_credits_and_prerequisites(profile):
    res = client.post("/api/plan", json=profile)
    assert res.status_code == 200
    body = res.json()
    assert body["source"] == "rules"
    plan = body["plan"]
    assert len(plan) > 0

    completed = set(profile["completedCourses"])
    max_credits = profile["creditHoursPerSemester"]
    for semester in plan:
        assert semester["totalCredits"] <= max_credits
        assert semester["totalCredits"] == sum(c["credits"] for c in semester["courses"])
        for course in semester["courses"]:
            for prereq in parse_prereqs(course["prerequisites"]):
                assert prereq in completed, (
                    f"{course['courseCode']} scheduled in {semester['semester']} "
                    f"before prerequisite {prereq}"
                )
        completed.update(c["courseCode"] for c in semester["courses"])


def test_profile_validation():
    res = client.post("/api/recommendations", json={
        "name": "Bob",
        "major": "Computer Science",
        "year": "Freshman",
        "careerGoals": "software engineer",
        "creditHoursPerSemester": 0,
    })
    assert res.status_code == 422
