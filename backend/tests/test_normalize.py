from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.db import engine
from app.main import app
from app.models import Application, User
from app.seed import seed_demo_data
from app.services.normalize import confusion_fold, normalize_id


def test_normalize_and_confusion_fold():
    assert normalize_id("nze141-1234 567") == "NZE1411234567"
    assert normalize_id(None) == ""
    assert confusion_fold("1NZ-O123") == "1N20123"


def test_login_returns_token_for_all_demo_users():
    with Session(engine) as session:
        seed_demo_data(session)

    client = TestClient(app)
    for username in ["citizen1", "citizen2", "officer1", "admin1"]:
        response = client.post("/api/auth/login", json={"username": username, "password": "demo123"})
        assert response.status_code == 200, response.text
        payload = response.json()
        assert payload["role"] in {"citizen", "officer", "admin"}
        assert payload["token"]
        assert payload["full_name"]


def test_seed_has_240_applications():
    with Session(engine) as session:
        seed_demo_data(session)
        users = session.exec(select(User)).all()
        applications = session.exec(select(Application)).all()
        assert len(users) == 4
        assert len(applications) == 240
