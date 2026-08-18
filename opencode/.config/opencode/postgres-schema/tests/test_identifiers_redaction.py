from __future__ import annotations

import pytest

from postgres_schema_inspector.errors import SchemaInspectorError
from postgres_schema_inspector.identifiers import validate_identifier
from postgres_schema_inspector.redact import redact_text, redact_url


@pytest.mark.parametrize("identifier", ["mapping_test", "p_daily_ssps", "a", "a1_b2"])
def test_valid_identifiers(identifier):
    assert validate_identifier(identifier) == identifier


@pytest.mark.parametrize(
    "identifier",
    ["Mapping", "p.daily", "1table", "table-name", " table", "table ", '"Mixed"', ""],
)
def test_invalid_identifiers(identifier):
    with pytest.raises(SchemaInspectorError) as exc:
        validate_identifier(identifier)

    assert exc.value.code == "INVALID_IDENTIFIER"


def test_redact_url_password():
    assert (
        redact_url("postgresql://user:secret@localhost:5432/analytics")
        == "postgresql://user:<redacted>@localhost:5432/analytics"
    )


def test_redact_text_password():
    text = redact_text("failed postgresql://user:secret@localhost/db?password=other")

    assert "secret" not in text
    assert "other" not in text
    assert "<redacted>" in text
