from fastapi.testclient import TestClient

from app.main import app


def test_list_test_categories_includes_known_categories():
    client = TestClient(app)
    response = client.get("/tests/categories")
    assert response.status_code == 200
    categories = response.json()
    assert "escalation" in categories
    assert "guardrails" in categories


def test_run_tests_for_a_small_category_returns_parsed_results():
    client = TestClient(app)
    response = client.post("/tests/run", json={"category": "escalation"})
    assert response.status_code == 200
    body = response.json()

    assert body["category"] == "escalation"
    assert body["total"] >= 3
    assert body["passed"] == body["total"]
    assert body["failed"] == 0
    assert len(body["tests"]) == body["total"]
    assert all({"name", "outcome", "duration_seconds"} <= t.keys() for t in body["tests"])
    assert all(t["outcome"] == "passed" for t in body["tests"])


def test_run_tests_for_unknown_category_returns_404():
    client = TestClient(app)
    response = client.post("/tests/run", json={"category": "does-not-exist"})
    assert response.status_code == 404
