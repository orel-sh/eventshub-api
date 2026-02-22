import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app

client = TestClient(app)


# ── Helpers ──────────────────────────────────────────────────────────────────

MOCK_EVENT = {
    "_id": MagicMock(__str__=lambda s: "64a1b2c3d4e5f6a7b8c9d0e1"),
    "title": "Test Event",
    "description": "A test event",
    "location": {"city": "Tel Aviv", "country": "Israel", "lat": 32.08, "lng": 34.78},
    "date": "2026-03-15T18:00:00",
    "max_participants": 50,
}

MOCK_USER = {
    "_id": MagicMock(__str__=lambda s: "64a1b2c3d4e5f6a7b8c9d0e2"),
    "name": "Test User",
    "email": "test@example.com",
    "role": "user",
    "password": "hashed",
}

MOCK_ADMIN = {**MOCK_USER, "role": "admin"}


# ── Auth tests ────────────────────────────────────────────────────────────────

class TestAuth:
    def test_register_success(self):
        with patch("app.routes.auth.users_collection") as mock_col:
            mock_col.find_one.return_value = None
            mock_col.insert_one.return_value = MagicMock(inserted_id="abc123")
            response = client.post("/auth/register", json={
                "name": "Orel", "email": "orel@test.com", "password": "secret123"
            })
        assert response.status_code == 201
        assert "id" in response.json()

    def test_register_duplicate_email(self):
        with patch("app.routes.auth.users_collection") as mock_col:
            mock_col.find_one.return_value = MOCK_USER
            response = client.post("/auth/register", json={
                "name": "Orel", "email": "orel@test.com", "password": "secret123"
            })
        assert response.status_code == 409

    def test_login_invalid_credentials(self):
        with patch("app.routes.auth.users_collection") as mock_col:
            mock_col.find_one.return_value = None
            response = client.post("/auth/login", json={
                "email": "nobody@test.com", "password": "wrong"
            })
        assert response.status_code == 401


# ── Events tests ──────────────────────────────────────────────────────────────

class TestEvents:
    def test_get_events(self):
        with patch("app.routes.events.events_collection") as mock_col:
            mock_col.find.return_value = [MOCK_EVENT]
            response = client.get("/events/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_event_not_found(self):
        with patch("app.routes.events.events_collection") as mock_col:
            mock_col.find_one.return_value = None
            response = client.get("/events/64a1b2c3d4e5f6a7b8c9d0e1")
        assert response.status_code == 404

    def test_get_event_invalid_id(self):
        response = client.get("/events/not-a-valid-id")
        assert response.status_code == 400

    def test_create_event_requires_admin(self):
        with patch("app.auth.jwt.get_current_user", return_value=MOCK_USER):
            response = client.post("/events/", json={
                "title": "New Event",
                "description": "desc",
                "location": {"city": "TLV", "country": "IL", "lat": 32.0, "lng": 34.0},
                "date": "2026-06-01T10:00:00",
                "max_participants": 100,
            }, headers={"Authorization": "Bearer faketoken"})
        assert response.status_code == 403


# ── Registrations tests ───────────────────────────────────────────────────────

class TestRegistrations:
    def test_register_duplicate(self):
        with patch("app.routes.registrations.events_collection") as mock_events, \
             patch("app.routes.registrations.registrations_collection") as mock_regs, \
             patch("app.auth.jwt.get_current_user", return_value=MOCK_USER):

            mock_events.find_one.return_value = MOCK_EVENT
            mock_regs.find_one.return_value = {"email": "orel@test.com"}  # already registered

            response = client.post("/registrations/", json={
                "event_id": "64a1b2c3d4e5f6a7b8c9d0e1",
                "email": "orel@test.com",
                "user_name": "Orel",
            }, headers={"Authorization": "Bearer faketoken"})

        assert response.status_code == 409

    def test_register_event_full(self):
        full_event = {**MOCK_EVENT, "max_participants": 1}
        with patch("app.routes.registrations.events_collection") as mock_events, \
             patch("app.routes.registrations.registrations_collection") as mock_regs, \
             patch("app.auth.jwt.get_current_user", return_value=MOCK_USER):

            mock_events.find_one.return_value = full_event
            mock_regs.find_one.return_value = None
            mock_regs.count_documents.return_value = 1  # already at capacity

            response = client.post("/registrations/", json={
                "event_id": "64a1b2c3d4e5f6a7b8c9d0e1",
                "email": "new@test.com",
                "user_name": "New User",
            }, headers={"Authorization": "Bearer faketoken"})

        assert response.status_code == 409
