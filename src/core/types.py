"""Custom SQLAlchemy types for database compatibility."""
import json
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
