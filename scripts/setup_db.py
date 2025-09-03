"""
Setup the development database:
- Ensure the Postgres database exists (create if missing)
- Apply Alembic migrations to the latest head

Usage: python scripts/setup_db.py
"""

from __future__ import annotations

import sys
from typing import Optional

from alembic import command
from alembic.config import Config
from sqlalchemy.engine import make_url

from app.config import settings


def ensure_postgres_database_exists(database_url: str) -> None:
    """Create the target Postgres database if it doesn't exist.

    Connects to the default 'postgres' database using the same credentials
    and host/port as the target URL, checks for existence, and creates it
    when missing.
    """
    import psycopg2

    url = make_url(database_url)
    if url.database is None:
        raise RuntimeError("Database name is not specified in DATABASE_URL")

    admin_db = "postgres"
    admin_dsn = (
        f"host={url.host or 'localhost'} "
        f"port={url.port or 5432} "
        f"user={url.username or 'postgres'} "
        f"password={url.password or ''} "
        f"dbname={admin_db}"
    )

    target_dbname = url.database

    try:
        with psycopg2.connect(admin_dsn) as conn: 
            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (target_dbname,))
                exists = cur.fetchone() is not None
                if not exists:
                    print(f"[setup-db] Creating database '{target_dbname}'...")
                    cur.execute(f'CREATE DATABASE "{target_dbname}"')
                else:
                    print(f"[setup-db] Database '{target_dbname}' already exists.")
    except psycopg2.Error as e:
        raise RuntimeError(f"Failed ensuring database exists: {e}") from e


def run_alembic_upgrade(alembic_ini_path: str = "alembic.ini", revision: str = "head") -> None:
    cfg = Config(alembic_ini_path)
    command.upgrade(cfg, revision)


def main() -> int:
    db_url = settings.database_url
    url = make_url(db_url)

    print(f"[setup-db] Using database URL: {url.drivername}://{url.username}@{url.host}:{url.port}/{url.database}")

    # Only attempt create-if-missing for Postgres
    if url.drivername.startswith("postgresql"):
        ensure_postgres_database_exists(db_url)
    else:
        print("[setup-db] Skipping database existence check (non-Postgres URL).")

    print("[setup-db] Applying Alembic migrations to head...")
    run_alembic_upgrade()
    print("[setup-db] Database is ready.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

