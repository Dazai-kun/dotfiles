from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import quote

from postgres_schema_inspector.errors import (
    ConfigNotFoundError,
    ConnectionEnvMissingError,
    InvalidConfigError,
    ProductionAccessDeniedError,
    SchemaDeniedError,
    SchemaNotAllowedError,
)


@dataclass(frozen=True, slots=True)
class ConnectionEnvConfig:
    host_env: str
    port_env: str | None
    database_env: str
    user_env: str
    password_env: str
    sslmode_env: str | None


@dataclass(frozen=True, slots=True)
class ProjectConfig:
    path: Path
    connection: ConnectionEnvConfig
    environment: str
    allow_production: bool
    allowed_schemas: frozenset[str]
    denied_schemas: frozenset[str]
    statement_timeout_ms: int
    connection_timeout_ms: int
    snapshot_dir: Path | None


def discover_config(start_dir: Path) -> Path:
    current = start_dir.resolve()
    if current.is_file():
        current = current.parent

    for directory in (current, *current.parents):
        candidate = directory / ".opencode" / "postgres-schema.json"
        if candidate.is_file():
            return candidate
    raise ConfigNotFoundError()


def _require_str(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value:
        raise InvalidConfigError(
            f"Configuration field '{key}' must be a non-empty string."
        )
    return value


def _optional_str(data: dict[str, Any], key: str, default: str) -> str:
    value = data.get(key, default)
    if not isinstance(value, str) or not value:
        raise InvalidConfigError(
            f"Configuration field '{key}' must be a non-empty string."
        )
    return value


def _optional_bool(data: dict[str, Any], key: str, default: bool) -> bool:
    value = data.get(key, default)
    if not isinstance(value, bool):
        raise InvalidConfigError(f"Configuration field '{key}' must be a boolean.")
    return value


def _optional_int(data: dict[str, Any], key: str, default: int) -> int:
    value = data.get(key, default)
    if not isinstance(value, int) or value <= 0:
        raise InvalidConfigError(
            f"Configuration field '{key}' must be a positive integer."
        )
    return value


def _schema_list(data: dict[str, Any], key: str, required: bool) -> frozenset[str]:
    value = data.get(key)
    if value is None and not required:
        return frozenset()
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise InvalidConfigError(
            f"Configuration field '{key}' must be a list of strings."
        )
    return frozenset(value)


def _connection_config(data: dict[str, Any]) -> ConnectionEnvConfig:
    value = data.get("connection")
    if not isinstance(value, dict):
        raise InvalidConfigError("Configuration field 'connection' must be an object.")
    port_env = value.get("portEnv")
    if port_env is not None and (not isinstance(port_env, str) or not port_env):
        raise InvalidConfigError(
            "Configuration field 'connection.portEnv' must be a non-empty string."
        )
    sslmode_env = value.get("sslmodeEnv")
    if sslmode_env is not None and (
        not isinstance(sslmode_env, str) or not sslmode_env
    ):
        raise InvalidConfigError(
            "Configuration field 'connection.sslmodeEnv' must be a non-empty string."
        )
    return ConnectionEnvConfig(
        host_env=_require_str(value, "hostEnv"),
        port_env=port_env,
        database_env=_require_str(value, "databaseEnv"),
        user_env=_require_str(value, "userEnv"),
        password_env=_require_str(value, "passwordEnv"),
        sslmode_env=sslmode_env,
    )


def load_config(start_dir: Path) -> ProjectConfig:
    path = discover_config(start_dir)
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise InvalidConfigError(f"Invalid JSON in {path}: {exc.msg}.") from exc
    if not isinstance(raw, dict):
        raise InvalidConfigError("Configuration root must be a JSON object.")

    snapshot_value = raw.get("snapshotDir")
    snapshot_dir = None
    if snapshot_value is not None:
        if not isinstance(snapshot_value, str) or not snapshot_value:
            raise InvalidConfigError(
                "Configuration field 'snapshotDir' must be a non-empty string."
            )
        snapshot_dir = (path.parent / snapshot_value).resolve()

    config = ProjectConfig(
        path=path,
        connection=_connection_config(raw),
        environment=_optional_str(raw, "environment", "development"),
        allow_production=_optional_bool(raw, "allowProduction", False),
        allowed_schemas=_schema_list(raw, "allowedSchemas", required=True),
        denied_schemas=_schema_list(raw, "deniedSchemas", required=False),
        statement_timeout_ms=_optional_int(raw, "statementTimeoutMs", 10000),
        connection_timeout_ms=_optional_int(raw, "connectionTimeoutMs", 5000),
        snapshot_dir=snapshot_dir,
    )
    if not config.allowed_schemas:
        raise InvalidConfigError(
            "Configuration field 'allowedSchemas' must not be empty."
        )
    if config.environment == "production" and not config.allow_production:
        raise ProductionAccessDeniedError()
    return config


def enforce_schema_policy(config: ProjectConfig, schema: str) -> None:
    if schema in config.denied_schemas:
        raise SchemaDeniedError(schema)
    if schema not in config.allowed_schemas:
        raise SchemaNotAllowedError(schema)


def connection_url(config: ProjectConfig) -> str:
    _load_project_dotenv(config.path.parent.parent / ".env")
    host = _env_value(config.connection.host_env)
    port = (
        _env_value(config.connection.port_env) if config.connection.port_env else "5432"
    )
    database = _env_value(config.connection.database_env)
    user = _env_value(config.connection.user_env)
    password = _env_value(config.connection.password_env)
    url = (
        f"postgresql://{quote(user, safe='')}:{quote(password, safe='')}"
        f"@{host}:{port}/{quote(database, safe='')}"
    )
    if config.connection.sslmode_env:
        sslmode = os.environ.get(config.connection.sslmode_env)
        if sslmode:
            url = f"{url}?sslmode={quote(sslmode, safe='')}"
    return url


def _env_value(env_name: str) -> str:
    value = os.environ.get(env_name)
    if not value:
        raise ConnectionEnvMissingError(env_name)
    return value


def _load_project_dotenv(path: Path) -> None:
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        key, value = _parse_dotenv_line(line)
        if key and key not in os.environ:
            os.environ[key] = value


def _parse_dotenv_line(line: str) -> tuple[str | None, str]:
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return None, ""
    if stripped.startswith("export "):
        stripped = stripped[7:].lstrip()
    if "=" not in stripped:
        return None, ""
    key, value = stripped.split("=", 1)
    key = key.strip()
    value = value.strip()
    if not key:
        return None, ""
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        value = value[1:-1]
    return key, value
