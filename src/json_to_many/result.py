from dataclasses import dataclass, field


@dataclass
class ConversionStats:
    rows: int = 0
    fields: int = 0
    warnings: list[str] = field(default_factory=list)


@dataclass
class ConversionResult:
    data: str
    format: str
    stats: ConversionStats
