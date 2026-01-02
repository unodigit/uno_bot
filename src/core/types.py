"""Custom SQLAlchemy types for database compatibility."""
import json
import uuid
from typing import Any

from sqlalchemy import Text, TypeDecorator
from sqlalchemy.dialects.postgresql import JSONB


class JSONType(TypeDecorator):
    """A type that handles JSON storage with SQLite/PostgreSQL compatibility.

    For PostgreSQL: Uses native JSONB
    For SQLite: Uses Text with JSON serialization
    """

    impl = Text
    cache_ok = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Determine dialect from bind (set at runtime)
        self._is_postgres = None

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(JSONB())
        else:
            return dialect.type_descriptor(Text())

    def process_bind_param(self, value: Any | None, dialect):
        """Convert Python object to database value."""
        if value is None:
            return None
        if dialect.name == 'postgresql':
            return value
        # For SQLite, serialize to JSON string
        return json.dumps(value) if isinstance(value, (dict, list)) else value

    def process_result_value(self, value: str | None, dialect):
        """Convert database value to Python object."""
        if value is None:
            return None
        if dialect.name == 'postgresql':
            return value
        # For SQLite, deserialize from JSON string
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value


class UUIDType(TypeDecorator):
    """A type that handles UUID storage with SQLite/PostgreSQL compatibility.

    For PostgreSQL: Uses native UUID
    For SQLite: Uses Text with string representation
    """

    impl = Text
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            from sqlalchemy.dialects.postgresql import UUID as PG_UUID
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        else:
            return dialect.type_descriptor(Text())

    def process_bind_param(self, value: Any | None, dialect):
        """Convert Python UUID to database value."""
        if value is None:
            return None
        if dialect.name == 'postgresql':
            return value
        # For SQLite, convert UUID to string
        return str(value) if isinstance(value, uuid.UUID) else value

    def process_result_value(self, value: str | None, dialect):
        """Convert database value to Python UUID."""
        if value is None:
            return None
        if dialect.name == 'postgresql':
            return value
        # For SQLite, convert string to UUID
        try:
            return uuid.UUID(value) if isinstance(value, str) else value
        except (ValueError, TypeError):
            return value
