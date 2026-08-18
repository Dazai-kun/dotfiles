from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import psycopg
from psycopg.rows import dict_row

from postgres_schema_inspector.config import ProjectConfig
from postgres_schema_inspector.errors import SchemaInspectorError
from postgres_schema_inspector.redact import redact_text


@dataclass(frozen=True, slots=True)
class InspectOptions:
    include_ddl: bool = False
    include_indexes: bool = True
    include_comments: bool = True
    include_partitioning: bool = True


def _first(
    conn: psycopg.Connection[Any], sql: str, params: tuple[Any, ...]
) -> dict[str, Any] | None:
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(sql, params)
        return cur.fetchone()


def _all(
    conn: psycopg.Connection[Any], sql: str, params: tuple[Any, ...]
) -> list[dict[str, Any]]:
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(sql, params)
        return list(cur.fetchall())


def _table_info(
    conn: psycopg.Connection[Any], schema: str, table: str
) -> dict[str, Any]:
    schema_row = _first(
        conn,
        "select oid from pg_catalog.pg_namespace where nspname = %s",
        (schema,),
    )
    if schema_row is None:
        raise SchemaInspectorError(
            "SCHEMA_NOT_FOUND", f"Schema '{schema}' does not exist."
        )

    row = _first(
        conn,
        """
        select
            c.oid,
            n.nspname as schema_name,
            c.relname as table_name,
            c.relkind,
            case c.relkind
                when 'r' then 'BASE TABLE'
                when 'p' then 'PARTITIONED TABLE'
                when 'v' then 'VIEW'
                when 'm' then 'MATERIALIZED VIEW'
                when 'f' then 'FOREIGN TABLE'
                else c.relkind::text
            end as table_type,
            obj_description(c.oid, 'pg_class') as table_comment
        from pg_catalog.pg_class c
        join pg_catalog.pg_namespace n on n.oid = c.relnamespace
        where n.nspname = %s
          and c.relname = %s
          and c.relkind in ('r', 'p', 'v', 'm', 'f')
        """,
        (schema, table),
    )
    if row is None:
        raise SchemaInspectorError(
            "TABLE_NOT_FOUND", f"Table '{schema}.{table}' does not exist."
        )
    return row


def _columns(
    conn: psycopg.Connection[Any], schema: str, table: str
) -> list[dict[str, Any]]:
    rows = _all(
        conn,
        """
        select
            c.ordinal_position as "ordinalPosition",
            c.column_name as name,
            c.data_type as "dataType",
            case
                when c.udt_schema = 'pg_catalog' then c.udt_name
                else c.udt_schema || '.' || c.udt_name
            end as "postgresType",
            c.is_nullable = 'YES' as nullable,
            c.column_default as default,
            c.is_generated <> 'NEVER' as generated,
            nullif(c.generation_expression, '') as "generationExpression",
            c.is_identity = 'YES' as identity,
            nullif(c.identity_generation, '') as "identityGeneration",
            col_description(
                format('%%I.%%I', c.table_schema, c.table_name)::regclass::oid,
                c.ordinal_position
            ) as comment
        from information_schema.columns c
        where c.table_schema = %s
          and c.table_name = %s
        order by c.ordinal_position
        """,
        (schema, table),
    )
    return rows


def _constraints(
    conn: psycopg.Connection[Any], table_oid: int
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    rows = _all(
        conn,
        """
        select
            con.conname as name,
            con.contype,
            pg_get_constraintdef(con.oid, true) as definition,
            coalesce(
                array_agg(att.attname order by keys.ordinality)
                    filter (where att.attname is not null),
                array[]::name[]
            ) as columns,
            fn.nspname as "foreignSchema",
            fc.relname as "foreignTable",
            coalesce(
                array_agg(fatt.attname order by fkeys.ordinality)
                    filter (where fatt.attname is not null),
                array[]::name[]
            ) as "foreignColumns"
        from pg_catalog.pg_constraint con
        left join lateral unnest(con.conkey) with ordinality
            as keys(attnum, ordinality) on true
        left join pg_catalog.pg_attribute att
            on att.attrelid = con.conrelid
           and att.attnum = keys.attnum
        left join pg_catalog.pg_class fc on fc.oid = con.confrelid
        left join pg_catalog.pg_namespace fn on fn.oid = fc.relnamespace
        left join lateral unnest(con.confkey) with ordinality
            as fkeys(attnum, ordinality)
            on fkeys.ordinality = keys.ordinality
        left join pg_catalog.pg_attribute fatt
            on fatt.attrelid = con.confrelid
           and fatt.attnum = fkeys.attnum
        where con.conrelid = %s
          and con.contype in ('p', 'u', 'f')
        group by con.oid, con.conname, con.contype, fc.relname, fn.nspname
        order by con.contype, con.conname
        """,
        (table_oid,),
    )

    primary_key: list[dict[str, Any]] = []
    unique_constraints: list[dict[str, Any]] = []
    foreign_keys: list[dict[str, Any]] = []
    for row in rows:
        item = {
            "name": row["name"],
            "columns": list(row["columns"]),
            "definition": row["definition"],
        }
        if row["contype"] == "p":
            primary_key.append(item)
        elif row["contype"] == "u":
            unique_constraints.append(item)
        elif row["contype"] == "f":
            item.update(
                {
                    "foreignSchema": row["foreignSchema"],
                    "foreignTable": row["foreignTable"],
                    "foreignColumns": list(row["foreignColumns"]),
                }
            )
            foreign_keys.append(item)
    return primary_key, unique_constraints, foreign_keys


def _indexes(
    conn: psycopg.Connection[Any], schema: str, table: str, include: bool
) -> list[dict[str, Any]]:
    if not include:
        return []
    return _all(
        conn,
        """
        select
            indexname as name,
            indexdef as definition
        from pg_catalog.pg_indexes
        where schemaname = %s
          and tablename = %s
        order by indexname
        """,
        (schema, table),
    )


def _partitioning(
    conn: psycopg.Connection[Any], table_oid: int, include: bool
) -> dict[str, Any] | None:
    if not include:
        return None
    info = _first(
        conn,
        """
        select
            pg_get_partkeydef(c.oid) as "partitionKey",
            pn.nspname as "parentSchema",
            pc.relname as "parentTable"
        from pg_catalog.pg_class c
        left join pg_catalog.pg_inherits inh on inh.inhrelid = c.oid
        left join pg_catalog.pg_class pc on pc.oid = inh.inhparent
        left join pg_catalog.pg_namespace pn on pn.oid = pc.relnamespace
        where c.oid = %s
        """,
        (table_oid,),
    )
    children = _all(
        conn,
        """
        select
            cn.nspname as schema,
            cc.relname as table,
            pg_get_expr(cc.relpartbound, cc.oid, true) as bound
        from pg_catalog.pg_inherits inh
        join pg_catalog.pg_class cc on cc.oid = inh.inhrelid
        join pg_catalog.pg_namespace cn on cn.oid = cc.relnamespace
        where inh.inhparent = %s
        order by cn.nspname, cc.relname
        """,
        (table_oid,),
    )
    if info is None or (
        not info["partitionKey"] and not info["parentTable"] and not children
    ):
        return None
    key = info["partitionKey"]
    strategy = key.split("(", 1)[0].strip() if key else None
    return {
        "strategy": strategy,
        "partitionKey": key,
        "parentTable": (
            f"{info['parentSchema']}.{info['parentTable']}"
            if info["parentTable"]
            else None
        ),
        "childPartitions": children,
    }


def _ddl(
    schema: str,
    table: str,
    table_type: str,
    columns: list[dict[str, Any]],
    primary_key: list[dict[str, Any]],
    unique_constraints: list[dict[str, Any]],
    partitioning: dict[str, Any] | None,
) -> str | None:
    if table_type not in {"BASE TABLE", "PARTITIONED TABLE"}:
        return None
    parts: list[str] = []
    for column in columns:
        line = f'    "{column["name"]}" {column["dataType"]}'
        if column["default"] is not None:
            line += f" DEFAULT {column['default']}"
        if not column["nullable"]:
            line += " NOT NULL"
        parts.append(line)
    for item in primary_key + unique_constraints:
        parts.append(f'    CONSTRAINT "{item["name"]}" {item["definition"]}')
    ddl = f'CREATE TABLE "{schema}"."{table}" (\n' + ",\n".join(parts) + "\n)"
    if partitioning and partitioning["partitionKey"]:
        ddl += f" PARTITION BY {partitioning['partitionKey']}"
    return ddl + ";"


def _snapshot_comparison(
    snapshot_dir: Path | None, schema: str, table: str, ddl: str | None
) -> dict[str, Any] | None:
    if snapshot_dir is None:
        return None
    path = snapshot_dir / f"{schema}.{table}.sql"
    if not path.exists():
        return {"path": str(path), "exists": False, "drift": None}
    if ddl is None:
        return {"path": str(path), "exists": True, "drift": None}
    snapshot = path.read_text(encoding="utf-8")
    return {
        "path": str(path),
        "exists": True,
        "drift": snapshot.strip() != ddl.strip(),
    }


def inspect_table(
    config: ProjectConfig,
    connection_url: str,
    schema: str,
    table: str,
    options: InspectOptions,
) -> dict[str, Any]:
    connect_timeout_seconds = max(1, int(config.connection_timeout_ms / 1000))
    try:
        with psycopg.connect(
            connection_url,
            connect_timeout=connect_timeout_seconds,
            row_factory=dict_row,
            options=(
                f"-c statement_timeout={config.statement_timeout_ms} "
                "-c default_transaction_read_only=on"
            ),
        ) as conn:
            conn.read_only = True
            version = _first(conn, "show server_version_num", ())
            version_num = int(version["server_version_num"] if version else 0)
            if version_num < 120000:
                raise SchemaInspectorError(
                    "UNSUPPORTED_POSTGRES_VERSION",
                    "PostgreSQL 12 or newer is required for schema inspection.",
                )

            table_info = _table_info(conn, schema, table)
            table_oid = int(table_info["oid"])
            columns = _columns(conn, schema, table)
            primary_key, unique_constraints, foreign_keys = _constraints(
                conn, table_oid
            )
            indexes = _indexes(conn, schema, table, options.include_indexes)
            partitioning = _partitioning(conn, table_oid, options.include_partitioning)
            table_comment = (
                table_info["table_comment"] if options.include_comments else None
            )
            if not options.include_comments:
                for column in columns:
                    column["comment"] = None

            ddl = (
                _ddl(
                    schema,
                    table,
                    table_info["table_type"],
                    columns,
                    primary_key,
                    unique_constraints,
                    partitioning,
                )
                if options.include_ddl
                else None
            )

            return {
                "database": conn.info.dbname,
                "schema": schema,
                "table": table,
                "tableType": table_info["table_type"],
                "columns": columns,
                "primaryKey": primary_key,
                "uniqueConstraints": unique_constraints,
                "foreignKeys": foreign_keys,
                "indexes": indexes,
                "partitioning": partitioning,
                "tableComment": table_comment,
                "ddl": ddl,
                "schemaSnapshot": _snapshot_comparison(
                    config.snapshot_dir, schema, table, ddl
                ),
            }
    except SchemaInspectorError:
        raise
    except psycopg.errors.QueryCanceled as exc:
        raise SchemaInspectorError(
            "STATEMENT_TIMEOUT", "Schema inspection statement timed out."
        ) from exc
    except psycopg.errors.InsufficientPrivilege as exc:
        raise SchemaInspectorError(
            "INSUFFICIENT_PERMISSION",
            "The configured PostgreSQL role lacks permission to inspect this schema.",
        ) from exc
    except psycopg.OperationalError as exc:
        text = redact_text(exc)
        if "password authentication failed" in text.lower():
            raise SchemaInspectorError(
                "AUTHENTICATION_FAILED", "PostgreSQL authentication failed."
            ) from exc
        raise SchemaInspectorError(
            "CONNECTION_FAILED", f"PostgreSQL connection failed: {text}"
        ) from exc
