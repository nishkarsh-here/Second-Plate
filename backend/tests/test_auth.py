"""Tests for registration, login and authenticated actions."""
from __future__ import annotations


def _register(client, email, role="recipient"):
    body = {"email": email, "password": "secret123", "name": "Test Org", "role": role}
    if role == "donor":
        body["donor_type"] = "restaurant"
    else:
        body["recipient_type"] = "ngo"
    return client.post("/api/auth/register", json=body)


def test_register_returns_token_and_profile(client):
    r = _register(client, "rec@example.com", "recipient")
    assert r.status_code == 201
    data = r.json()
    assert data["token_type"] == "bearer"
    assert data["access_token"]
    assert data["user"]["role"] == "recipient"
    assert data["user"]["recipient_id"] is not None


def test_me_with_token(client):
    token = _register(client, "me@example.com").json()["access_token"]
    r = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["email"] == "me@example.com"


def test_me_requires_auth(client):
    assert client.get("/api/auth/me").status_code == 401


def test_duplicate_email_conflicts(client):
    _register(client, "dup@example.com")
    assert _register(client, "dup@example.com").status_code == 409


def test_login_ok_and_wrong_password(client):
    _register(client, "login@example.com", "donor")
    ok = client.post("/api/auth/login", json={"email": "login@example.com", "password": "secret123"})
    assert ok.status_code == 200
    bad = client.post("/api/auth/login", json={"email": "login@example.com", "password": "nope"})
    assert bad.status_code == 401


def test_authenticated_donor_posts_as_self(client):
    reg = _register(client, "donor2@example.com", "donor").json()
    token = reg["access_token"]
    donor_id = reg["user"]["donor_id"]
    payload = {
        "food_type": "Pasta",
        "category": "cooked",
        "servings": 12,
        "prepared_at": "2030-01-01T10:00:00Z",
        "expires_at": "2030-01-01T16:00:00Z",
    }
    # No donor_id in the payload -> derived from the token.
    r = client.post("/api/listings", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 201
    assert r.json()["donor"]["id"] == donor_id


def test_guest_create_without_donor_id_is_rejected(client):
    payload = {
        "food_type": "Pasta",
        "category": "cooked",
        "servings": 12,
        "prepared_at": "2030-01-01T10:00:00Z",
        "expires_at": "2030-01-01T16:00:00Z",
    }
    assert client.post("/api/listings", json=payload).status_code == 400
