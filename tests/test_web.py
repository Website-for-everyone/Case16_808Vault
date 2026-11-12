import pytest
from fastapi.testclient import TestClient
from web.app import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "808_vault_api"

def test_get_tracks():
    response = client.get("/api/tracks")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["tracks"]) >= 4
    first = data["tracks"][0]
    assert "bpm" in first
    assert "key" in first
    assert "waveform_peaks" in first

def test_get_licenses():
    response = client.get("/api/licenses")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["licenses"]) >= 4
    types = [l["type"] for l in data["licenses"]]
    assert "WAV Lease" in types
    assert "Exclusive Rights" in types

def test_book_session_valid():
    payload = {
        "client_name": "Test Artist",
        "client_contact": "@test_artist",
        "studio_room": "Main Control Room",
        "booking_date": "2026-12-01",
        "booking_time": "15:30 - 19:30",
        "notes": "Testing sound equipment"
    }
    response = client.post("/api/book-session", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "BK-" in data["booking"]["booking_id"]
    assert data["booking"]["client_name"] == "Test Artist"

def test_order_license_valid():
    payload = {
        "client_name": "Beat Buyer",
        "client_contact": "+79991234567",
        "track_id": "trk-01",
        "license_type": "WAV Lease",
        "artist_pseudonym": "MC Sound"
    }
    response = client.post("/api/order-license", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "ORD-808-" in data["order"]["order_id"]

def test_index_page():
    response = client.get("/")
    assert response.status_code == 200
    assert "808 VAULT" in response.text
    assert "waveform-canvas" in response.text
