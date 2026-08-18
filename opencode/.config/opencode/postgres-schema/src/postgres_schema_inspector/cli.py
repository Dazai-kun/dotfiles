from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from postgres_schema_inspector.config import (
    connection_url,
    enforce_schema_policy,
    load_config,
)
from postgres_schema_inspector.errors import SchemaInspectorError
from postgres_schema_inspector.identifiers import validate_identifier
from postgres_schema_inspector.inspect import InspectOptions, inspect_table
from postgres_schema_inspector.redact import redact_text


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Inspect an allowlisted PostgreSQL table schema."
    )
    parser.add_argument("--schema", required=True)
    parser.add_argument("--table", required=True)
    parser.add_argument("--start-dir", default=".")
    parser.add_argument("--include-ddl", action="store_true")
    parser.add_argument(
        "--include-indexes", action=argparse.BooleanOptionalAction, default=True
    )
    parser.add_argument(
        "--include-comments", action=argparse.BooleanOptionalAction, default=True
    )
    parser.add_argument(
        "--include-partitioning", action=argparse.BooleanOptionalAction, default=True
    )
    return parser


def run(argv: list[str] | None = None) -> dict[str, Any]:
    args = _parser().parse_args(argv)
    schema = validate_identifier(args.schema)
    table = validate_identifier(args.table)
    config = load_config(Path(args.start_dir))
    enforce_schema_policy(config, schema)
    url = connection_url(config)
    return inspect_table(
        config,
        url,
        schema,
        table,
        InspectOptions(
            include_ddl=args.include_ddl,
            include_indexes=args.include_indexes,
            include_comments=args.include_comments,
            include_partitioning=args.include_partitioning,
        ),
    )


def main(argv: list[str] | None = None) -> int:
    try:
        print(json.dumps(run(argv), indent=2, sort_keys=True, default=str))
        return 0
    except SchemaInspectorError as exc:
        print(json.dumps(exc.to_json(), indent=2, sort_keys=True))
        return 1
    except Exception as exc:  # pragma: no cover - defensive boundary
        print(redact_text(exc), file=sys.stderr)
        error = SchemaInspectorError(
            "INTERNAL_ERROR", "Unexpected schema inspection failure."
        )
        print(json.dumps(error.to_json(), indent=2, sort_keys=True))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
