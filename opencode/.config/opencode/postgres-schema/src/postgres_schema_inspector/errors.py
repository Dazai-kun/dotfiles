from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class SchemaInspectorError(Exception):
    code: str
    message: str

    def to_json(self) -> dict[str, Any]:
        return {"error": {"code": self.code, "message": self.message}}


class ConfigNotFoundError(SchemaInspectorError):
    def __init__(self) -> None:
        super().__init__(
            "CONFIG_NOT_FOUND",
            "No .opencode/postgres-schema.json configuration file found.",
        )


class InvalidConfigError(SchemaInspectorError):
    def __init__(self, message: str) -> None:
        super().__init__("INVALID_CONFIG", message)


class ConnectionEnvMissingError(SchemaInspectorError):
    def __init__(self, env_name: str) -> None:
        super().__init__(
            "CONNECTION_ENV_MISSING",
            f"Configured connection environment variable '{env_name}' is missing.",
        )


class InvalidIdentifierError(SchemaInspectorError):
    def __init__(self, identifier: str) -> None:
        super().__init__(
            "INVALID_IDENTIFIER",
            f"Invalid PostgreSQL identifier '{identifier}'. Only normal "
            "unquoted identifiers are supported.",
        )


class SchemaDeniedError(SchemaInspectorError):
    def __init__(self, schema: str) -> None:
        super().__init__(
            "SCHEMA_DENIED",
            f"Schema '{schema}' is explicitly denied by the project configuration.",
        )


class SchemaNotAllowedError(SchemaInspectorError):
    def __init__(self, schema: str) -> None:
        super().__init__(
            "SCHEMA_NOT_ALLOWED",
            f"Schema '{schema}' is not permitted by the project configuration.",
        )


class ProductionAccessDeniedError(SchemaInspectorError):
    def __init__(self) -> None:
        super().__init__(
            "PRODUCTION_ACCESS_DENIED",
            "Production schema inspection is disabled by project configuration.",
        )
