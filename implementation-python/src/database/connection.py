"""Database connection management."""

from contextlib import contextmanager
from typing import Generator

import psycopg2
from psycopg2.extensions import connection as PgConnection
from psycopg2.extras import RealDictCursor

from src.config import get_settings


class DatabaseConnection:
    """Manages PostgreSQL database connections."""

    def __init__(self, database_url: str | None = None):
        """Initialize database connection manager.

        Args:
            database_url: PostgreSQL connection URL. Uses settings if not provided.
        """
        self._database_url = database_url or get_settings().database_url

    @contextmanager
    def get_connection(self) -> Generator[PgConnection, None, None]:
        """Get a database connection context manager.

        Yields:
            PostgreSQL connection object.
        """
        conn = psycopg2.connect(self._database_url)
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    @contextmanager
    def get_cursor(self) -> Generator[RealDictCursor, None, None]:
        """Get a database cursor context manager with dict results.

        Yields:
            PostgreSQL cursor with RealDictCursor factory.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            try:
                yield cursor
            finally:
                cursor.close()

    def initialize_schema(self) -> None:
        """Create database tables if they don't exist."""
        schema_sql = """
        CREATE TABLE IF NOT EXISTS expenses (
            id SERIAL PRIMARY KEY,
            amount DECIMAL(12, 2) NOT NULL CHECK (amount > 0),
            category VARCHAR(100) NOT NULL,
            description VARCHAR(500),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS savings (
            id SERIAL PRIMARY KEY,
            amount DECIMAL(12, 2) NOT NULL CHECK (amount > 0),
            goal VARCHAR(100) NOT NULL,
            description VARCHAR(500),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS investments (
            id SERIAL PRIMARY KEY,
            amount DECIMAL(12, 2) NOT NULL CHECK (amount > 0),
            asset_type VARCHAR(100) NOT NULL,
            description VARCHAR(500),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        with self.get_cursor() as cursor:
            cursor.execute(schema_sql)
