"""Opaque sessions, encrypted job parameters, and bounded rate accounting."""

import base64
import hashlib
import json
import os
import secrets
import threading
import time
from collections import OrderedDict

import redis
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from fastapi import HTTPException, Request

from backend.config import settings
from backend.database import Session, SessionLocal


def seal(options: dict) -> str:
    nonce = os.urandom(12)
    data = AESGCM(bytes.fromhex(settings.secret_key)).encrypt(nonce, json.dumps(options).encode(), b"job-options-v1")
    return base64.b64encode(nonce + data).decode("ascii")


def unseal(value: str) -> dict:
    data = base64.b64decode(value, validate=True)
    return json.loads(AESGCM(bytes.fromhex(settings.secret_key)).decrypt(data[:12], data[12:], b"job-options-v1"))


def create_session(owner: str, authenticated: bool = False) -> str:
    token = secrets.token_urlsafe(32)
    with SessionLocal() as database:
        database.add(Session(token_hash=hashlib.sha256(token.encode()).hexdigest(), owner=owner,
                             expires=time.time() + settings.retention_seconds, authenticated=authenticated))
        database.commit()
    return token


def current_session(request: Request) -> Session:
    token = request.cookies.get("fileshield_session", "")
    if len(token) > 128:
        raise HTTPException(401, "Session required")
    with SessionLocal() as database:
        session = database.get(Session, hashlib.sha256(token.encode()).hexdigest())
        if not session or session.expires <= time.time():
            raise HTTPException(401, "Session required or expired")
        return session


class RateLimiter:
    def __init__(self):
        self.lock = threading.Lock()
        self.buckets = OrderedDict()
        self.client = redis.Redis.from_url(settings.redis_url) if settings.redis_url else None

    def check(self, category: str, identity: str, limit: int, seconds: int = 60):
        window = int(time.time()) // seconds
        key = f"fileshield:rate:{category}:{hashlib.sha256(identity.encode()).hexdigest()}:{window}"
        if self.client:
            try:
                count = self.client.eval("local n=redis.call('INCR',KEYS[1]); if n==1 then redis.call('EXPIRE',KEYS[1],ARGV[1]) end; return n", 1, key, seconds + 1)
            except redis.RedisError as error:
                raise HTTPException(503, "Rate limiting unavailable") from error
        else:
            with self.lock:
                count = self.buckets.get(key, 0) + 1
                self.buckets[key] = count
                if len(self.buckets) > 10000:
                    self.buckets.popitem(last=False)
        if count > limit:
            raise HTTPException(429, "Rate limit exceeded", headers={"Retry-After": str(seconds)})


limiter = RateLimiter()