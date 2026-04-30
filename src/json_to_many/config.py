from __future__ import annotations

import os
import sys
from typing import Any

if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib  # type: ignore[no-redef]
    except ImportError:
        tomllib = None  # type: ignore[assignment]

_CONFIG_FILENAME = ".json2many.toml"


def _find_config(start: str) -> str | None:
    current = os.path.abspath(start)
    while True:
        candidate = os.path.join(current, _CONFIG_FILENAME)
        if os.path.isfile(candidate):
            return candidate
        parent = os.path.dirname(current)
        if parent == current:
            return None
        current = parent


def load_config(start_dir: str | None = None) -> dict[str, Any]:
    """Load .json2many.toml from start_dir or the nearest parent directory.

    Returns an empty dict if no config file is found or tomllib is unavailable.
    """
    if tomllib is None:
        return {}

    search_from = start_dir or os.getcwd()
    path = _find_config(search_from)
    if path is None:
        return {}

    with open(path, "rb") as f:
        return tomllib.load(f)


def merge_options(
    config: dict[str, Any],
    output_format: str,
    explicit_options: dict[str, Any],
) -> dict[str, Any]:
    """Merge config file options with explicit call-site options.

    Priority (highest wins): explicit_options > converters.<format> > defaults.
    """
    defaults: dict[str, Any] = config.get("defaults", {})
    format_config: dict[str, Any] = config.get("converters", {}).get(
        output_format.lower(), {}
    )
    return {**defaults, **format_config, **explicit_options}
