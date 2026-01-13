"""Database initialization script."""

import sys
from pathlib import Path

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import get_settings


def create_database_if_not_exists() -> bool:
    settings = get_settings()

    conn = psycopg2.connect(
        host=settings.database_host,
        port=settings.database_port,
        user=settings.database_user,
        password=settings.database_password,
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

    cursor = conn.cursor()

    cursor.execute(
        "SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s",
        (settings.database_name,),
    )
    exists = cursor.fetchone()

    if not exists:
        cursor.execute(f'CREATE DATABASE "{settings.database_name}"')
        print(f"Database '{settings.database_name}' created successfully.")
        created = True
    else:
        print(f"Database '{settings.database_name}' already exists.")
        created = False

    cursor.close()
    conn.close()

    return created


def initialize_schema() -> None:
    """Create database tables."""
    settings = get_settings()

    conn = psycopg2.connect(settings.database_url)
    cursor = conn.cursor()

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

    cursor.execute(schema_sql)
    conn.commit()

    print("Database schema initialized successfully.")

    cursor.close()
    conn.close()


def main() -> None:
    try:
        create_database_if_not_exists()
        initialize_schema()
        print("=" * 50)
        print("Initialization completed")
    except psycopg2.OperationalError as e:
        print(f"\nError connecting to PostgreSQL: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
