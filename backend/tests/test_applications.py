import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    """Each test runs against its own empty database file."""
    monkeypatch.setenv("TRACKER_DB", str(tmp_path / "test.db"))
    with TestClient(app) as c:  # entering the context runs startup, which creates the table
        yield c


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_list_is_empty_at_first(client):
    assert client.get("/applications").json() == []


def test_create_application_uses_defaults(client):
    r = client.post("/applications", json={"company": "Acme", "role": "SWE Intern"})
    assert r.status_code == 201
    body = r.json()
    assert body["id"] == 1
    assert body["status"] == "wishlist"
    assert body["applied_date"] is None


def test_create_with_all_fields(client):
    payload = {
        "company": "Globex", "role": "Backend Intern", "status": "applied",
        "applied_date": "2026-10-20", "url": "https://example.com/job", "notes": "Referred by a friend",
    }
    body = client.post("/applications", json=payload).json()
    assert {k: body[k] for k in payload} == payload


def test_whitespace_is_stripped(client):
    r = client.post("/applications", json={"company": "  Acme  ", "role": " SWE "})
    assert r.json()["company"] == "Acme" and r.json()["role"] == "SWE"


@pytest.mark.parametrize("bad", [
    {"role": "SWE"},                                        # company missing
    {"company": "", "role": "SWE"},                         # company empty
    {"company": "   ", "role": "SWE"},                      # company only whitespace
    {"company": "Acme", "role": "SWE", "status": "maybe"},  # unknown status
    {"company": "Acme", "role": "SWE", "applied_date": "yesterday"},  # not a date
])
def test_invalid_input_is_rejected(client, bad):
    assert client.post("/applications", json=bad).status_code == 422


def test_list_returns_newest_first(client):
    client.post("/applications", json={"company": "First", "role": "A"})
    client.post("/applications", json={"company": "Second", "role": "B"})
    companies = [a["company"] for a in client.get("/applications").json()]
    assert companies == ["Second", "First"]