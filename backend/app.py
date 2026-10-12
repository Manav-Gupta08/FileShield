"""Same-origin REST API; uploads are opaque bytes until a worker examines them."""

import asyncio
import hashlib
import json
import logging
import threading
import time
import uuid
from contextlib import asynccontextmanager

from argon2 import PasswordHasher
from argon2.exceptions import VerificationError
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse, JSONResponse
from pydantic import ValidationError
from sqlalchemy import func, select, text
from sqlalchemy.exc import IntegrityError
from starlette.datastructures import UploadFile

from backend.config import settings
from backend.database import Job, Session, SessionLocal, User, initialize_database
from backend.schemas import Credentials, Options
from backend.security import create_session, current_session, limiter, seal
from backend.storage import display_filename, job_directory, remove_job_files
from backend.workers import cleanup, process_job
from fileshield.detection import MAX_FILE_SIZE


logger = logging.getLogger("fileshield.api")
password_hasher = PasswordHasher()
dummy_hash = password_hasher.hash("dummy-password-not-an-account")
OPERATIONS = {"analyze", "release", "metadata", "sanitize", "hash", "compare", "scan", "images", "batch", "pdf", "archives", "protect", "decrypt"}
admission_lock = threading.Lock()


async def retention_loop():
    while True:
        await asyncio.sleep(30)
        await asyncio.to_thread(cleanup)


@asynccontextmanager
async def lifespan(application):
    settings.validate()
    settings.storage.mkdir(parents=True, exist_ok=True, mode=0o700)
    if not settings.production:
        initialize_database()
    await asyncio.to_thread(cleanup)
    task = asyncio.create_task(retention_loop())
    try:
        yield
    finally:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


class BodyLimit:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        total = 0
        async def bounded_receive():
            nonlocal total
            message = await receive()
            total += len(message.get("body", b""))
            if total > settings.max_request_size:
                raise HTTPException(413, "Request exceeds 26 MiB")
            return message
        await self.app(scope, bounded_receive, send)


app = FastAPI(title="FileShield", version="0.1.0", lifespan=lifespan)
app.add_middleware(BodyLimit)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    identity = request.client.host if request.client else "unknown"
    try:
        limiter.check("requests", identity, 120)
        if request.method not in {"GET", "HEAD", "OPTIONS"}:
            origin = request.headers.get("origin")
            if origin and origin != settings.origin:
                raise HTTPException(403, "Cross-origin mutation denied")
            if request.headers.get("sec-fetch-site") == "cross-site":
                raise HTTPException(403, "Cross-site request denied")
        length = request.headers.get("content-length")
        if length and (not length.isdigit() or int(length) > settings.max_request_size):
            raise HTTPException(413, "Invalid or excessive request size")
        response = await call_next(request)
    except HTTPException as error:
        response = JSONResponse({"detail": error.detail}, status_code=error.status_code, headers=error.headers)
    response.headers.update({"X-Content-Type-Options": "nosniff", "Referrer-Policy": "no-referrer",
                             "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
                             "Content-Security-Policy": "default-src 'none'; frame-ancestors 'none'",
                             "Cache-Control": "no-store"})
    if settings.production:
        response.headers["Strict-Transport-Security"] = "max-age=31536000"
    return response


def set_cookie(response: Response, token: str):
    response.set_cookie("fileshield_session", token, httponly=True, secure=settings.production,
                        samesite="strict", max_age=settings.retention_seconds, path="/api/v1")


@app.get("/api/v1/health")
def health():
    return {"status": "ok", "antivirus_required": settings.require_scan, "environment": "production" if settings.production else "development"}


@app.post("/api/v1/session")
def anonymous_session(request: Request, response: Response):
    limiter.check("session", request.client.host if request.client else "unknown", 10)
    try:
        session = current_session(request)
        return {"authenticated": session.authenticated}
    except HTTPException:
        set_cookie(response, create_session(str(uuid.uuid4())))
        return {"authenticated": False}


@app.post("/api/v1/auth/register", status_code=201)
def register(credentials: Credentials, request: Request, response: Response):
    limiter.check("auth", request.client.host if request.client else "unknown", 5)
    owner = str(uuid.uuid4())
    with SessionLocal() as database:
        database.add(User(id=owner, username=credentials.username.lower(), password_hash=password_hasher.hash(credentials.password)))
        try:
            database.commit()
        except IntegrityError as error:
            raise HTTPException(409, "Account cannot be created") from error
    set_cookie(response, create_session(owner, True))
    return {"authenticated": True}


@app.post("/api/v1/auth/login")
def login(credentials: Credentials, request: Request, response: Response):
    limiter.check("auth", request.client.host if request.client else "unknown", 5)
    with SessionLocal() as database:
        user = database.scalar(select(User).where(User.username == credentials.username.lower()))
        try:
            valid = password_hasher.verify(user.password_hash if user else dummy_hash, credentials.password)
        except VerificationError:
            valid = False
        if not valid or not user:
            raise HTTPException(401, "Invalid credentials")
        set_cookie(response, create_session(user.id, True))
        return {"authenticated": True}


@app.post("/api/v1/auth/logout", status_code=204)
def logout(request: Request, response: Response, session: Session = Depends(current_session)):
    with SessionLocal() as database:
        stored = database.get(Session, session.token_hash)
        if stored:
            database.delete(stored)
            database.commit()
    response.delete_cookie("fileshield_session", path="/api/v1")


def owned_job(identifier: str, session: Session) -> Job:
    try:
        job_directory(identifier)
    except ValueError as error:
        raise HTTPException(404, "Job not found") from error
    with SessionLocal() as database:
        job = database.get(Job, identifier)
        if not job or job.owner != session.owner or job.expires <= time.time():
            logger.warning(json.dumps({"event": "job_access_denied"}))
            raise HTTPException(404, "Job not found")
        return job


@app.post("/api/v1/jobs/{operation}", status_code=202)
async def submit(operation: str, request: Request, tasks: BackgroundTasks, session: Session = Depends(current_session)):
    if operation not in OPERATIONS:
        raise HTTPException(404, "Unsupported operation")
    limiter.check("jobs", session.owner, 20 if session.authenticated else 5)
    with SessionLocal() as database:
        pending = database.scalar(select(func.count()).select_from(Job).where(Job.status.in_(["queued", "processing"])))
        if pending >= 10:
            raise HTTPException(429, "Processing capacity reached")
    identifier = str(uuid.uuid4())
    directory = job_directory(identifier)
    directory.mkdir(mode=0o700, parents=True)
    names, mimes = [], []
    try:
        async with request.form(max_files=10, max_fields=1, max_part_size=8192) as form:
            if any(key not in {"files", "options"} for key in form):
                raise HTTPException(422, "Unknown upload field")
            uploads = form.getlist("files")
            if not uploads or any(not isinstance(upload, UploadFile) for upload in uploads):
                raise HTTPException(422, "At least one file is required")
            if operation == "compare" and len(uploads) != 2:
                raise HTTPException(422, "Comparison requires exactly two files")
            if operation not in {"batch", "pdf", "compare"} and len(uploads) != 1:
                raise HTTPException(422, "This operation accepts one file")
            try:
                options = Options.model_validate_json(form.get("options", "{}"))
            except (ValidationError, TypeError) as error:
                raise HTTPException(422, "Invalid operation parameters") from error
            if operation in {"protect", "decrypt"} and not options.password:
                raise HTTPException(422, "Password required")
            total = 0
            for index, upload in enumerate(uploads):
                names.append(display_filename(upload.filename or ""))
                mimes.append((upload.content_type or "")[:128])
                size = 0
                with (directory / f"input-{index}.bin").open("xb") as stream:
                    while chunk := await upload.read(65536):
                        size += len(chunk)
                        total += len(chunk)
                        if size > MAX_FILE_SIZE or total > MAX_FILE_SIZE:
                            raise HTTPException(413, "Upload exceeds 25 MiB total file limit")
                        stream.write(chunk)
                if size == 0:
                    raise HTTPException(422, "Empty files are not accepted")
        with admission_lock, SessionLocal() as database:
            if settings.production:
                database.execute(text("SELECT pg_advisory_xact_lock(71423001)"))
            pending = database.scalar(select(func.count()).select_from(Job).where(Job.status.in_(["queued", "processing"])))
            if pending >= 10:
                raise HTTPException(429, "Processing capacity reached")
            database.add(Job(id=identifier, owner=session.owner, operation=operation, status="queued", created=time.time(),
                             expires=time.time() + settings.retention_seconds, filenames=json.dumps(names),
                             declared_mimes=json.dumps(mimes), options=seal(options.model_dump())))
            database.commit()
        if settings.redis_url:
            process_job.apply_async(args=[identifier], expires=settings.retention_seconds)
        else:
            tasks.add_task(process_job, identifier)
        return {"job_id": identifier}
    except Exception as error:
        remove_job_files(identifier)
        with SessionLocal() as database:
            job = database.get(Job, identifier)
            if job:
                database.delete(job)
                database.commit()
        if isinstance(error, HTTPException):
            raise
        if isinstance(error, ValueError):
            raise HTTPException(422, "Invalid upload") from error
        raise HTTPException(503, "Job submission unavailable") from error


@app.get("/api/v1/jobs")
def history(session: Session = Depends(current_session)):
    with SessionLocal() as database:
        jobs = database.scalars(select(Job).where(Job.owner == session.owner, Job.expires > time.time()).order_by(Job.created.desc()).limit(50)).all()
        return [{"job_id": job.id, "operation": job.operation, "status": job.status, "expires": job.expires} for job in jobs]


@app.get("/api/v1/jobs/{identifier}")
def get_job(identifier: str, session: Session = Depends(current_session)):
    job = owned_job(identifier, session)
    return {"job_id": job.id, "status": job.status, "operation": job.operation, "filenames": json.loads(job.filenames),
            "expires": job.expires, "result": json.loads(job.report), "error": job.error,
            "download_available": job.status == "completed" and bool(job.output_name)}


@app.get("/api/v1/files/{identifier}")
def download(identifier: str, session: Session = Depends(current_session)):
    job = owned_job(identifier, session)
    if job.status != "completed" or not job.output_name:
        raise HTTPException(409, "Output is not available")
    path = job_directory(identifier) / job.output_name
    if not path.is_file():
        raise HTTPException(404, "Output expired or deleted")
    return FileResponse(path, filename=job.output_name, media_type="application/octet-stream", headers={"Cache-Control": "no-store"})


@app.delete("/api/v1/files/{identifier}", status_code=204)
def delete_file(identifier: str, session: Session = Depends(current_session)):
    job = owned_job(identifier, session)
    if job.status in {"queued", "processing"}:
        raise HTTPException(409, "Wait for processing to finish before deletion")
    remove_job_files(identifier)
    with SessionLocal() as database:
        stored = database.get(Job, identifier)
        if stored:
            database.delete(stored)
            database.commit()