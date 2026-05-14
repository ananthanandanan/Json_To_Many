from __future__ import annotations

import click


def split_csv(ctx, param, value: str | None) -> list[str] | None:
    """Comma-split a Click string option into a list of trimmed tokens.

    None stays None so the converter can distinguish 'flag not passed' from
    'flag passed with empty value'.
    """
    if value is None:
        return None
    return [item.strip() for item in value.split(",") if item.strip()]


def parse_kv(ctx, param, values: tuple[str, ...] | None) -> dict[str, str] | None:
    """Parse repeated key=val flags into a dict.

    First '=' splits the token, so values may contain '='. Empty RHS is
    allowed. Values are always strings — no YAML/JSON coercion.
    """
    if not values:
        return None
    out: dict[str, str] = {}
    for raw in values:
        if "=" not in raw:
            raise click.BadParameter(f"expected key=val, got {raw!r}")
        key, val = raw.split("=", 1)
        key = key.strip()
        if not key:
            raise click.BadParameter(f"empty key in {raw!r}")
        out[key] = val
    return out
