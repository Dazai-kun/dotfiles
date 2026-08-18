from __future__ import annotations

import re

from postgres_schema_inspector.errors import InvalidIdentifierError

IDENTIFIER_RE = re.compile(r"^[a-z_][a-z0-9_]{0,62}$")


def validate_identifier(value: str) -> str:
    if not IDENTIFIER_RE.fullmatch(value):
        raise InvalidIdentifierError(value)
    return value
