from __future__ import annotations

import json
import os
from urllib.parse import urlsplit

import pytest

from postgres_schema_inspector.cli import main

pytestmark = pytest.mark.integration


def _integration_url() -> str:
    value = os.environ.get("POSTGRES_SCHEMA_INTEGRATION_URL")
    if not value:
        pytest.skip("POSTGRES_SCHEMA_INTEGRATION_URL is not set")
    lowered = value.lower()
    if "prod" in lowered or "production" in lowered:
        pytest.fail("Refusing to run integration tests against production-like URL")
    return value


def test_optional_integration_basic_table(tmp_path, monkeypatch, capsys):
    url = _integration_url()
    parsed = urlsplit(url)
    if not parsed.hostname or not parsed.username or not parsed.password:
        pytest.fail(
            "POSTGRES_SCHEMA_INTEGRATION_URL must include host, user, and password"
        )
    config_dir = tmp_path / ".opencode"
    config_dir.mkdir()
    (config_dir / "postgres-schema.json").write_text(
        json.dumps(
            {
                "connection": {
                    "hostEnv": "POSTGRES_SCHEMA_INTEGRATION_HOST",
                    "portEnv": "POSTGRES_SCHEMA_INTEGRATION_PORT",
                    "databaseEnv": "POSTGRES_SCHEMA_INTEGRATION_DATABASE",
                    "userEnv": "POSTGRES_SCHEMA_INTEGRATION_USER",
                    "passwordEnv": "POSTGRES_SCHEMA_INTEGRATION_PASSWORD",
                },
                "environment": "development",
                "allowProduction": False,
                "allowedSchemas": ["public"],
                "deniedSchemas": [],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("POSTGRES_SCHEMA_INTEGRATION_HOST", parsed.hostname)
    monkeypatch.setenv("POSTGRES_SCHEMA_INTEGRATION_PORT", str(parsed.port or 5432))
    monkeypatch.setenv("POSTGRES_SCHEMA_INTEGRATION_DATABASE", parsed.path.lstrip("/"))
    monkeypatch.setenv("POSTGRES_SCHEMA_INTEGRATION_USER", parsed.username)
    monkeypatch.setenv("POSTGRES_SCHEMA_INTEGRATION_PASSWORD", parsed.password)

    exit_code = main(
        [
            "--schema",
            "public",
            "--table",
            "postgres_schema_test",
            "--start-dir",
            str(tmp_path),
        ]
    )

    payload = json.loads(capsys.readouterr().out)
    assert exit_code in {0, 1}
    if exit_code == 0:
        assert payload["schema"] == "public"
        assert payload["table"] == "postgres_schema_test"
    else:
        assert payload["error"]["code"] in {
            "TABLE_NOT_FOUND",
            "INSUFFICIENT_PERMISSION",
        }
