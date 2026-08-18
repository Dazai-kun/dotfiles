from __future__ import annotations

import json

import pytest

from postgres_schema_inspector.config import ConnectionEnvConfig, ProjectConfig
from postgres_schema_inspector.inspect import InspectOptions, inspect_table


class FakeInfo:
    dbname = "analytics"


class FakeCursor:
    def __init__(self, connection):
        self.connection = connection
        self.result = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def execute(self, sql, params):
        self.result = self.connection.dispatch(sql, params)

    def fetchone(self):
        return self.result[0] if self.result else None

    def fetchall(self):
        return self.result


class FakeConnection:
    def __init__(self):
        self.info = FakeInfo()
        self.closed = False
        self.read_only = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        self.closed = True
        return False

    def cursor(self, row_factory=None):
        return FakeCursor(self)

    def dispatch(self, sql, params):
        if "show server_version_num" in sql:
            return [{"server_version_num": "160000"}]
        if "from pg_catalog.pg_namespace" in sql:
            return [{"oid": 1}]
        if "from pg_catalog.pg_class c" in sql and "c.relkind in" in sql:
            return [
                {
                    "oid": 10,
                    "schema_name": "mapping_test",
                    "table_name": "p_daily_ssps",
                    "relkind": "r",
                    "table_type": "BASE TABLE",
                    "table_comment": "daily SSP facts",
                }
            ]
        if "from information_schema.columns" in sql:
            return [
                {
                    "ordinalPosition": 1,
                    "name": "date",
                    "dataType": "date",
                    "postgresType": "date",
                    "nullable": False,
                    "default": None,
                    "generated": False,
                    "generationExpression": None,
                    "identity": False,
                    "identityGeneration": None,
                    "comment": "report date",
                },
                {
                    "ordinalPosition": 2,
                    "name": "campaign_id",
                    "dataType": "text",
                    "postgresType": "text",
                    "nullable": False,
                    "default": None,
                    "generated": False,
                    "generationExpression": None,
                    "identity": False,
                    "identityGeneration": None,
                    "comment": None,
                },
            ]
        if "from pg_catalog.pg_constraint" in sql:
            return [
                {
                    "name": "p_daily_ssps_pk",
                    "contype": "p",
                    "definition": "PRIMARY KEY (date, campaign_id)",
                    "columns": ["date", "campaign_id"],
                    "foreignSchema": None,
                    "foreignTable": None,
                    "foreignColumns": [],
                },
                {
                    "name": "p_daily_ssps_campaign_uq",
                    "contype": "u",
                    "definition": "UNIQUE (campaign_id)",
                    "columns": ["campaign_id"],
                    "foreignSchema": None,
                    "foreignTable": None,
                    "foreignColumns": [],
                },
                {
                    "name": "p_daily_ssps_campaign_fk",
                    "contype": "f",
                    "definition": (
                        "FOREIGN KEY (campaign_id) REFERENCES "
                        "mapping.p_campaigns(campaign_id)"
                    ),
                    "columns": ["campaign_id"],
                    "foreignSchema": "mapping",
                    "foreignTable": "p_campaigns",
                    "foreignColumns": ["campaign_id"],
                },
            ]
        if "from pg_catalog.pg_indexes" in sql:
            return [
                {"name": "p_daily_ssps_pk", "definition": "CREATE UNIQUE INDEX ..."}
            ]
        if "pg_get_partkeydef" in sql:
            return [{"partitionKey": None, "parentSchema": None, "parentTable": None}]
        if "from pg_catalog.pg_inherits" in sql:
            return []
        return []


def test_inspect_table_json_shape_and_connection_cleanup(monkeypatch, tmp_path):
    fake = FakeConnection()
    snapshot_dir = tmp_path / "schemas"
    snapshot_dir.mkdir()
    (snapshot_dir / "mapping_test.p_daily_ssps.sql").write_text(
        "CREATE TABLE different();\n", encoding="utf-8"
    )

    def fake_connect(*args, **kwargs):
        return fake

    monkeypatch.setattr(
        "postgres_schema_inspector.inspect.psycopg.connect", fake_connect
    )
    config = ProjectConfig(
        path=tmp_path / ".opencode" / "postgres-schema.json",
        connection=ConnectionEnvConfig(
            host_env="ETL_SCHEMA_DB_HOST",
            port_env="ETL_SCHEMA_DB_PORT",
            database_env="ETL_SCHEMA_DB_NAME",
            user_env="ETL_SCHEMA_DB_USER",
            password_env="ETL_SCHEMA_DB_PASSWORD",
            sslmode_env=None,
        ),
        environment="development",
        allow_production=False,
        allowed_schemas=frozenset({"mapping_test"}),
        denied_schemas=frozenset(),
        statement_timeout_ms=10000,
        connection_timeout_ms=5000,
        snapshot_dir=snapshot_dir,
    )

    result = inspect_table(
        config,
        "postgresql://user:password@localhost/db",
        "mapping_test",
        "p_daily_ssps",
        InspectOptions(include_ddl=True),
    )

    json.dumps(result)
    assert result["database"] == "analytics"
    assert result["primaryKey"][0]["columns"] == ["date", "campaign_id"]
    assert result["uniqueConstraints"][0]["columns"] == ["campaign_id"]
    assert result["foreignKeys"][0]["foreignTable"] == "p_campaigns"
    assert result["indexes"][0]["name"] == "p_daily_ssps_pk"
    assert result["tableComment"] == "daily SSP facts"
    assert result["ddl"].startswith("CREATE TABLE")
    assert result["schemaSnapshot"]["exists"] is True
    assert result["schemaSnapshot"]["drift"] is True
    assert fake.closed is True
    assert fake.read_only is True


def test_no_comments_option(monkeypatch, tmp_path):
    fake = FakeConnection()
    monkeypatch.setattr(
        "postgres_schema_inspector.inspect.psycopg.connect", lambda *a, **k: fake
    )
    config = ProjectConfig(
        path=tmp_path / ".opencode" / "postgres-schema.json",
        connection=ConnectionEnvConfig(
            host_env="ETL_SCHEMA_DB_HOST",
            port_env="ETL_SCHEMA_DB_PORT",
            database_env="ETL_SCHEMA_DB_NAME",
            user_env="ETL_SCHEMA_DB_USER",
            password_env="ETL_SCHEMA_DB_PASSWORD",
            sslmode_env=None,
        ),
        environment="development",
        allow_production=False,
        allowed_schemas=frozenset({"mapping_test"}),
        denied_schemas=frozenset(),
        statement_timeout_ms=10000,
        connection_timeout_ms=5000,
        snapshot_dir=None,
    )

    result = inspect_table(
        config,
        "postgresql://user:password@localhost/db",
        "mapping_test",
        "p_daily_ssps",
        InspectOptions(include_comments=False),
    )

    assert result["tableComment"] is None
    assert result["columns"][0]["comment"] is None


def test_imported_pytest_available_for_marker():
    assert pytest is not None
