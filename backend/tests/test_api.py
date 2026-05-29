"""API tests via TestClient against an isolated, seeded SQLite database."""
from __future__ import annotations


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_list_donors_and_recipients(client):
    assert len(client.get("/api/donors").json()) == 1
    assert len(client.get("/api/recipients").json()) == 1


def test_browse_available_includes_urgency(client):
    r = client.get("/api/listings", params={"lat": 12.98, "lng": 77.60})
    assert r.status_code == 200
    listings = r.json()
    assert len(listings) >= 1
    first = listings[0]
    assert "urgency" in first and first["urgency"]["color"] in {"green", "amber", "rose", "slate"}
    assert first["distance_km"] is not None


def test_create_listing(client):
    payload = {
        "donor_id": 1,
        "food_type": "Pasta",
        "category": "cooked",
        "servings": 25,
        "prepared_at": "2030-01-01T10:00:00Z",
        "expires_at": "2030-01-01T16:00:00Z",
    }
    r = client.post("/api/listings", json=payload)
    assert r.status_code == 201
    assert r.json()["servings"] == 25


def test_create_listing_invalid_window_returns_422(client):
    payload = {
        "donor_id": 1,
        "food_type": "Pasta",
        "category": "cooked",
        "servings": 25,
        "prepared_at": "2030-01-01T16:00:00Z",
        "expires_at": "2030-01-01T10:00:00Z",
    }
    assert client.post("/api/listings", json=payload).status_code == 422


def test_create_listing_zero_servings_returns_422(client):
    payload = {
        "donor_id": 1,
        "food_type": "Pasta",
        "category": "cooked",
        "servings": 0,
        "prepared_at": "2030-01-01T10:00:00Z",
        "expires_at": "2030-01-01T16:00:00Z",
    }
    assert client.post("/api/listings", json=payload).status_code == 422


def test_claim_flow_and_conflict(client):
    listings = client.get("/api/listings").json()
    available = next(x for x in listings if x["status"] == "available")
    lid = available["id"]

    first = client.post(f"/api/listings/{lid}/claim", json={"recipient_id": 1})
    assert first.status_code == 201
    assert first.json()["servings_rescued"] == available["servings"]

    # Second claim on the now-claimed listing conflicts.
    second = client.post(f"/api/listings/{lid}/claim", json={"recipient_id": 1})
    assert second.status_code == 409


def test_listing_not_found(client):
    r = client.get("/api/listings/999999")
    assert r.status_code == 404
    assert r.json()["detail"]


def test_impact_summary_shape(client):
    r = client.get("/api/impact/summary")
    assert r.status_code == 200
    body = r.json()
    for key in ("meals_rescued", "kg_saved", "co2e_avoided_kg", "people_served"):
        assert "value" in body[key]
    assert body["meals_rescued"]["value"] >= 20  # the seeded completed pickup
