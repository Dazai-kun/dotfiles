from __future__ import annotations

import json

from postgres_schema_inspector import cli


def test_cli_structured_error_for_missing_config(tmp_path, capsys):
    exit_code = cli.main(
        [
            "--schema",
            "mapping_test",
            "--table",
            "p_daily_ssps",
            "--start-dir",
            str(tmp_path),
        ]
    )

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 1
    assert payload["error"]["code"] == "CONFIG_NOT_FOUND"
    assert captured.err == ""


def test_cli_invalid_identifier_before_config(tmp_path, capsys):
    exit_code = cli.main(
        [
            "--schema",
            "bad.schema",
            "--table",
            "p_daily_ssps",
            "--start-dir",
            str(tmp_path),
        ]
    )

    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 1
    assert payload["error"]["code"] == "INVALID_IDENTIFIER"
