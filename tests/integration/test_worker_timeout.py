import json
import subprocess
import time
import uuid
from unittest.mock import patch

from backend.database import Job, SessionLocal, initialize_database
from backend.security import seal, unseal
from backend.storage import job_directory
from backend.workers import process_job


def test_timeout_cleans_input_output_and_password():
    initialize_database()
    identifier = str(uuid.uuid4())
    directory = job_directory(identifier)
    directory.mkdir(parents=True)
    (directory / "input-0.bin").write_bytes(b"test")
    (directory / "output.png").write_bytes(b"partial")
    with SessionLocal() as database:
        database.add(Job(id=identifier, owner=str(uuid.uuid4()), operation="protect", created=time.time(),
                         expires=time.time() + 3600, filenames=json.dumps(["file"]), declared_mimes="[]",
                         options=seal({"password": "secret password"})))
        database.commit()
    with patch("backend.workers.subprocess.run", side_effect=subprocess.TimeoutExpired("runner", 1)):
        process_job(identifier)
    assert not directory.exists()
    with SessionLocal() as database:
        job = database.get(Job, identifier)
        assert job.status == "failed"
        assert unseal(job.options) == {}