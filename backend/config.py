"""Explicit deployment configuration; insecure defaults are development-only."""

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    production: bool = os.getenv("FILESHIELD_ENV", "development") == "production"
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./temp/fileshield.db")
    redis_url: str = os.getenv("REDIS_URL", "")
    storage: Path = Path(os.getenv("STORAGE_ROOT", "./temp/jobs"))
    origin: str = os.getenv("PUBLIC_ORIGIN", "http://localhost:5173")
    secret_key: str = os.getenv("FILESHIELD_SECRET_KEY", "")
    require_scan: bool = os.getenv("REQUIRE_SCAN", "true").lower() == "true"
    clamav_host: str = os.getenv("CLAMAV_HOST", "clamav")
    retention_seconds: int = int(os.getenv("RETENTION_SECONDS", "3600"))
    process_timeout: int = int(os.getenv("MAX_PROCESS_TIME", "60"))
    max_request_size: int = 26 * 1024 * 1024

    def validate(self):
        if self.retention_seconds < 60 or self.retention_seconds > 86400:
            raise RuntimeError("Retention must be between 60 seconds and 24 hours")
        if not 1 <= self.process_timeout <= 300:
            raise RuntimeError("Process timeout must be between 1 and 300 seconds")
        if self.production:
            if not self.database_url.startswith("postgresql") or not self.redis_url:
                raise RuntimeError("Production requires PostgreSQL and Redis")
            if not self.origin.startswith("https://") or not self.require_scan:
                raise RuntimeError("Production requires HTTPS origin and malware scanning")
        if len(self.secret_key) != 64:
            raise RuntimeError("Set FILESHIELD_SECRET_KEY to 32 random bytes encoded as 64 hex characters")
        bytes.fromhex(self.secret_key)


settings = Settings()