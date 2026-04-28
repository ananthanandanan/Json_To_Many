from abc import ABC, abstractmethod
from typing import Any

from ..result import ConversionResult, ConversionStats


class BaseConverter(ABC):
    def __init__(self, data: dict | list, **options: Any) -> None:
        self.data = data
        self.options = options
        self._stats = ConversionStats()

    @abstractmethod
    def converter(self) -> None:
        pass

    @abstractmethod
    def save_to_file(self, file_name: str) -> None:
        pass

    @abstractmethod
    def get_converted_data(self) -> ConversionResult:
        pass
