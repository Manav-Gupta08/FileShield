"""Explicit bootstrap for a new database; not a schema migration system."""

from backend.config import settings
from backend.database import initialize_database


if __name__ == "__main__":
    settings.validate()
    initialize_database()
    print("Database schema initialized. Existing schema changes require reviewed migrations.")