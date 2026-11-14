import hashlib

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_version():
    response = client.get("/version")
    assert response.status_code == 200
    assert response.json() == {"version": "0.1.0"}


def test_checksum():
    text = "secure delivery"
    response = client.post(
        "/checksum",
        json={"text": text},
    )

    assert response.status_code == 200
    assert response.json()["sha256"] == hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()


def test_checksum_empty_text():
    response = client.post(
        "/checksum",
        json={"text": ""},
    )
    assert response.status_code == 422


def test_checksum_exceeds_limit():
    response = client.post(
        "/checksum",
        json={"text": "x" * 4097},
    )
    assert response.status_code == 422


def test_checksum_unicode_byte_limit():
    response = client.post(
        "/checksum",
        json={"text": "🙂" * 1025},
    )
    assert response.status_code == 422


def test_checksum_missing_text():
    response = client.post(
        "/checksum",
        json={},
    )
    assert response.status_code == 422
