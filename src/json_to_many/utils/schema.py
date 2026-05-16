from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .json_utils import flatten_json, normalize_input
from .type_infer import infer_type as _infer_type


@dataclass
class FieldInfo:
    name: str
    type: str
    coverage: float
    sample: str


@dataclass
class SchemaResult:
    record_count: int
    fields: list[FieldInfo] = field(default_factory=list)


def _format_sample(value: object) -> str:
    if value is None:
        return "null"
    if isinstance(value, str):
        truncated = value[:40]
        return f'"{truncated}"'
    if isinstance(value, list):
        preview = str(value[:3])
        return preview if len(value) <= 3 else preview[:-1] + ", ...]"
    return str(value)


def analyze_schema(data: Any) -> SchemaResult:
    data = normalize_input(data)
    records: list[dict] = []
    if isinstance(data, dict):
        records = [data]
    elif isinstance(data, list):
        records = [r for r in data if isinstance(r, dict)]

    record_count = len(records)
    if record_count == 0:
        return SchemaResult(record_count=0)

    field_counts: dict[str, int] = {}
    field_types: dict[str, set[str]] = {}
    field_samples: dict[str, str] = {}

    for record in records:
        flat = flatten_json(record)
        for key, value in flat.items():
            field_counts[key] = field_counts.get(key, 0) + 1
            inferred = _infer_type(value)
            field_types.setdefault(key, set()).add(inferred)
            if key not in field_samples and value is not None:
                field_samples[key] = _format_sample(value)

    fields: list[FieldInfo] = []
    for name, count in field_counts.items():
        types = field_types[name] - {"null"}
        if len(types) > 1:
            resolved_type = "mixed"
        elif len(types) == 1:
            resolved_type = next(iter(types))
        else:
            resolved_type = "null"

        fields.append(
            FieldInfo(
                name=name,
                type=resolved_type,
                coverage=round((count / record_count) * 100, 1),
                sample=field_samples.get(name, "null"),
            )
        )

    fields.sort(key=lambda f: (-f.coverage, f.name))
    return SchemaResult(record_count=record_count, fields=fields)
