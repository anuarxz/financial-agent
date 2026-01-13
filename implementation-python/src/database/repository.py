"""Repository pattern for database operations."""

from decimal import Decimal
from typing import Any

from src.database.connection import DatabaseConnection
from src.schemas import TableName


class FinancialRepository:
    """Repository for financial data operations."""

    # Mapping of table names to their specific fields (excluding common fields)
    TABLE_FIELDS: dict[TableName, list[str]] = {
        TableName.EXPENSES: ["amount", "category", "description"],
        TableName.SAVINGS: ["amount", "goal", "description"],
        TableName.INVESTMENTS: ["amount", "asset_type", "description"],
    }

    def __init__(self, db_connection: DatabaseConnection):
        """Initialize repository with database connection.

        Args:
            db_connection: Database connection manager instance.
        """
        self._db = db_connection

    def insert(self, table: TableName, data: dict[str, Any]) -> dict[str, Any]:
        """Insert a record into the specified table.

        Args:
            table: Target table name.
            data: Record data to insert.

        Returns:
            The inserted record with generated fields.

        Raises:
            ValueError: If table is invalid or required fields are missing.
        """
        fields = self.TABLE_FIELDS.get(table)
        if not fields:
            raise ValueError(f"Invalid table: {table}")

        # Filter data to only include valid fields
        filtered_data = {k: v for k, v in data.items() if k in fields and v is not None}

        if not filtered_data:
            raise ValueError("No valid data provided for insertion")

        columns = list(filtered_data.keys())
        placeholders = ["%s"] * len(columns)
        values = list(filtered_data.values())

        query = f"""
            INSERT INTO {table.value} ({', '.join(columns)})
            VALUES ({', '.join(placeholders)})
            RETURNING *
        """

        with self._db.get_cursor() as cursor:
            cursor.execute(query, values)
            result = cursor.fetchone()
            return self._serialize_record(dict(result))

    def query(
        self,
        table: TableName,
        filters: dict[str, Any] | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Query records from the specified table.

        Args:
            table: Target table name.
            filters: Optional filters to apply (column: value).
            limit: Maximum number of records to return.

        Returns:
            List of matching records.

        Raises:
            ValueError: If table is invalid.
        """
        if table not in self.TABLE_FIELDS:
            raise ValueError(f"Invalid table: {table}")

        query = f"SELECT * FROM {table.value}"
        values: list[Any] = []

        if filters:
            # Build WHERE clause with valid fields only
            valid_filters = {
                k: v for k, v in filters.items()
                if k in self.TABLE_FIELDS[table] + ["id", "created_at"] and v is not None
            }

            if valid_filters:
                conditions = [f"{col} = %s" for col in valid_filters.keys()]
                query += f" WHERE {' AND '.join(conditions)}"
                values = list(valid_filters.values())

        query += f" ORDER BY created_at DESC LIMIT %s"
        values.append(limit)

        with self._db.get_cursor() as cursor:
            cursor.execute(query, values)
            results = cursor.fetchall()
            return [self._serialize_record(dict(row)) for row in results]

    def _serialize_record(self, record: dict[str, Any]) -> dict[str, Any]:
        """Serialize a database record for JSON compatibility.

        Args:
            record: Raw database record.

        Returns:
            Serialized record with proper types.
        """
        serialized = {}
        for key, value in record.items():
            if isinstance(value, Decimal):
                serialized[key] = float(value)
            elif hasattr(value, "isoformat"):
                serialized[key] = value.isoformat()
            else:
                serialized[key] = value
        return serialized
