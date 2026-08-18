from __future__ import annotations

import json

import pytest

from postgres_schema_inspector.config import (
    connection_url,
    enforce_schema_policy,
    load_config,
)
from postgres_schema_inspector.errors import SchemaInspectorError


def write_config(path, **overrides):
    config = {
        "connection": {
            "hostEnv": "ETL_SCHEMA_DB_HOST",
            "portEnv": "ETL_SCHEMA_DB_PORT",
            "databaseEnv": "ETL_SCHEMA_DB_NAME",
            "userEnv": "ETL_SCHEMA_DB_USER",
            "passwordEnv": "ETL_SCHEMA_DB_PASSWORD",
        },
        "environment": "development",
        "allowProduction": False,
        "allowedSchemas": ["mapping_test", "mapping"],
        "deniedSchemas": ["internal"],
    }
    config.update(overrides)
    config_dir = path / ".opencode"
    config_dir.mkdir(parents=True)
    (config_dir / "postgres-schema.json").write_text(
        json.dumps(config), encoding="utf-8"
    )


def test_discovers_config_upward(tmp_path):
    write_config(tmp_path)
    nested = tmp_path / "a" / "b"
    nested.mkdir(parents=True)

    config = load_config(nested)

    assert config.connection.host_env == "ETL_SCHEMA_DB_HOST"
    assert config.allowed_schemas == frozenset({"mapping_test", "mapping"})


def test_nearest_config_wins(tmp_path):
    write_config(tmp_path, allowedSchemas=["mapping_test"])
    child = tmp_path / "child"
    child.mkdir()
    write_config(child, allowedSchemas=["io_platform"])

    config = load_config(child / "nested")

    assert config.allowed_schemas == frozenset({"io_platform"})


def test_missing_config(tmp_path):
    with pytest.raises(SchemaInspectorError) as exc:
        load_config(tmp_path)

    assert exc.value.code == "CONFIG_NOT_FOUND"


def test_invalid_json_config(tmp_path):
    config_dir = tmp_path / ".opencode"
    config_dir.mkdir()
    (config_dir / "postgres-schema.json").write_text("{", encoding="utf-8")

    with pytest.raises(SchemaInspectorError) as exc:
        load_config(tmp_path)

    assert exc.value.code == "INVALID_CONFIG"


def test_missing_connection_env(tmp_path, monkeypatch):
    write_config(tmp_path)
    monkeypatch.delenv("ETL_SCHEMA_DB_HOST", raising=False)
    config = load_config(tmp_path)

    with pytest.raises(SchemaInspectorError) as exc:
        connection_url(config)

    assert exc.value.code == "CONNECTION_ENV_MISSING"
    assert "ETL_SCHEMA_DB_HOST" in exc.value.message


def test_connection_url_from_env_parts(tmp_path, monkeypatch):
    write_config(tmp_path)
    monkeypatch.setenv("ETL_SCHEMA_DB_HOST", "localhost")
    monkeypatch.setenv("ETL_SCHEMA_DB_PORT", "5433")
    monkeypatch.setenv("ETL_SCHEMA_DB_NAME", "ta_data")
    monkeypatch.setenv("ETL_SCHEMA_DB_USER", "schema reader")
    monkeypatch.setenv("ETL_SCHEMA_DB_PASSWORD", "p@ss/word")
    config = load_config(tmp_path)

    assert (
        connection_url(config)
        == "postgresql://schema%20reader:p%40ss%2Fword@localhost:5433/ta_data"
    )


def test_connection_url_defaults_port(tmp_path, monkeypatch):
    write_config(
        tmp_path,
        connection={
            "hostEnv": "ETL_SCHEMA_DB_HOST",
            "databaseEnv": "ETL_SCHEMA_DB_NAME",
            "userEnv": "ETL_SCHEMA_DB_USER",
            "passwordEnv": "ETL_SCHEMA_DB_PASSWORD",
        },
    )
    monkeypatch.setenv("ETL_SCHEMA_DB_HOST", "localhost")
    monkeypatch.setenv("ETL_SCHEMA_DB_NAME", "ta_data")
    monkeypatch.setenv("ETL_SCHEMA_DB_USER", "opencode_schema_reader")
    monkeypatch.setenv("ETL_SCHEMA_DB_PASSWORD", "secret")
    config = load_config(tmp_path)

    assert connection_url(config) == (
        "postgresql://opencode_schema_reader:secret@localhost:5432/ta_data"
    )


def test_connection_url_loads_project_dotenv(tmp_path, monkeypatch):
    write_config(tmp_path)
    monkeypatch.delenv("ETL_SCHEMA_DB_HOST", raising=False)
    monkeypatch.delenv("ETL_SCHEMA_DB_PORT", raising=False)
    monkeypatch.delenv("ETL_SCHEMA_DB_NAME", raising=False)
    monkeypatch.delenv("ETL_SCHEMA_DB_USER", raising=False)
    monkeypatch.delenv("ETL_SCHEMA_DB_PASSWORD", raising=False)
    (tmp_path / ".env").write_text(
        "\n".join(
            [
                "ETL_SCHEMA_DB_HOST=localhost",
                "ETL_SCHEMA_DB_PORT=5432",
                "ETL_SCHEMA_DB_NAME=ta_data",
                "ETL_SCHEMA_DB_USER=opencode_schema_reader",
                "ETL_SCHEMA_DB_PASSWORD='secret value'",
            ]
        ),
        encoding="utf-8",
    )
    config = load_config(tmp_path)

    assert connection_url(config) == (
        "postgresql://opencode_schema_reader:secret%20value@localhost:5432/ta_data"
    )


def test_project_dotenv_does_not_override_environment(tmp_path, monkeypatch):
    write_config(tmp_path)
    monkeypatch.setenv("ETL_SCHEMA_DB_HOST", "env-host")
    monkeypatch.setenv("ETL_SCHEMA_DB_PORT", "5432")
    monkeypatch.setenv("ETL_SCHEMA_DB_NAME", "ta_data")
    monkeypatch.setenv("ETL_SCHEMA_DB_USER", "opencode_schema_reader")
    monkeypatch.setenv("ETL_SCHEMA_DB_PASSWORD", "env-secret")
    (tmp_path / ".env").write_text(
        "ETL_SCHEMA_DB_HOST=file-host\nETL_SCHEMA_DB_PASSWORD=file-secret\n",
        encoding="utf-8",
    )
    config = load_config(tmp_path)

    assert connection_url(config) == (
        "postgresql://opencode_schema_reader:env-secret@env-host:5432/ta_data"
    )


def test_allowed_schema(tmp_path):
    write_config(tmp_path)
    config = load_config(tmp_path)

    enforce_schema_policy(config, "mapping_test")


def test_not_allowlisted_schema(tmp_path):
    write_config(tmp_path)
    config = load_config(tmp_path)

    with pytest.raises(SchemaInspectorError) as exc:
        enforce_schema_policy(config, "private_data")

    assert exc.value.code == "SCHEMA_NOT_ALLOWED"


def test_denied_schema(tmp_path):
    write_config(tmp_path)
    config = load_config(tmp_path)

    with pytest.raises(SchemaInspectorError) as exc:
        enforce_schema_policy(config, "internal")

    assert exc.value.code == "SCHEMA_DENIED"


def test_denied_schema_overrides_allowed(tmp_path):
    write_config(tmp_path, allowedSchemas=["mapping_test", "internal"])
    config = load_config(tmp_path)

    with pytest.raises(SchemaInspectorError) as exc:
        enforce_schema_policy(config, "internal")

    assert exc.value.code == "SCHEMA_DENIED"


def test_production_denied_by_default(tmp_path):
    write_config(tmp_path, environment="production")

    with pytest.raises(SchemaInspectorError) as exc:
        load_config(tmp_path)

    assert exc.value.code == "PRODUCTION_ACCESS_DENIED"


def test_production_explicitly_enabled(tmp_path):
    write_config(tmp_path, environment="production", allowProduction=True)

    config = load_config(tmp_path)

    assert config.environment == "production"
