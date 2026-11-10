from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from json_to_many.cli.main import cli


def test_output_dir_pointing_at_file_is_clean_error(tmp_path: Path):
    src = tmp_path / "users.json"
    src.write_text(json.dumps([{"id": 1}]))
    blocked = tmp_path / "blocked"
    blocked.write_text("x")
    result = CliRunner().invoke(
        cli, ["convert", str(src), "--to", "csv", "-d", str(blocked)]
    )
    assert result.exit_code == 1
    assert "Traceback" not in result.output
    assert "blocked" in result.output
