import io
import time

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from backend.app import app
from backend.database import Job, SessionLocal
from backend.security import limiter
from backend.storage import job_directory
from backend.workers import cleanup


@pytest.fixture
def client():
    limiter.buckets.clear()
    with TestClient(app) as client:
        client.post("/api/v1/session")
        yield client


def png():
    stream = io.BytesIO()
    Image.new("RGB", (8, 8)).save(stream, format="PNG")
    return stream.getvalue()


def upload(client, operation="sanitize", name="image.png", data=None):
    return client.post(f"/api/v1/jobs/{operation}", files={"files": (name, data or png(), "image/png")})


def test_complete_sanitization_and_deletion(client):
    response = upload(client)
    assert response.status_code == 202, response.text
    identifier = response.json()["job_id"]
    result = client.get(f"/api/v1/jobs/{identifier}").json()
    assert result["status"] == "completed", result
    assert client.get(f"/api/v1/files/{identifier}").status_code == 200
    assert not (job_directory(identifier) / "input-0.bin").exists()
    assert client.delete(f"/api/v1/files/{identifier}").status_code == 204
    assert client.get(f"/api/v1/files/{identifier}").status_code == 404


def test_unauthorized_download_and_report(client):
    identifier = upload(client).json()["job_id"]
    with TestClient(app) as other:
        other.post("/api/v1/session")
        assert other.get(f"/api/v1/jobs/{identifier}").status_code == 404
        assert other.get(f"/api/v1/files/{identifier}").status_code == 404
        assert other.delete(f"/api/v1/files/{identifier}").status_code == 404


def test_mime_mismatch_cannot_be_sanitized(client):
    identifier = upload(client, name="photo.jpg.exe", data=b"MZ" + b"0" * 100).json()["job_id"]
    report = client.get(f"/api/v1/jobs/{identifier}").json()
    assert report["status"] == "failed"
    assert not report["download_available"]


def test_filename_traversal_stays_inside_generated_directory(client):
    identifier = upload(client, name="../../image.png").json()["job_id"]
    assert client.get(f"/api/v1/jobs/{identifier}").json()["filenames"] == ["image.png"]


def test_cross_origin_mutation_and_invalid_id(client):
    assert client.post("/api/v1/session", headers={"Origin": "https://attacker.invalid"}).status_code == 403
    assert client.get("/api/v1/files/not-a-uuid").status_code == 404
    assert client.get("/api/v1/health").headers["x-content-type-options"] == "nosniff"


def test_expired_job_is_inaccessible_and_cleaned(client):
    identifier = upload(client).json()["job_id"]
    with SessionLocal() as database:
        database.get(Job, identifier).expires = time.time() - 1
        database.commit()
    assert client.get(f"/api/v1/files/{identifier}").status_code == 404
    cleanup()
    assert not job_directory(identifier).exists()


def test_oversized_request_rejected_before_upload(client):
    response = client.post("/api/v1/jobs/analyze", content=b"", headers={"Content-Length": str(30 * 1024 * 1024)})
    assert response.status_code == 413


def test_authentication_password_is_hashed(client):
    credentials = {"username": "testuser", "password": "correct horse battery staple"}
    assert client.post("/api/v1/auth/register", json=credentials).status_code == 201
    assert client.post("/api/v1/auth/logout").status_code == 204
    assert client.get("/api/v1/jobs").status_code == 401
    assert client.post("/api/v1/auth/login", json=credentials).status_code == 200