from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from ..models import Inventory, PowerProfile


class BaseCollector(ABC):
    """Base class for infrastructure collectors."""

    def __init__(self, power_profile: PowerProfile, **_: object) -> None:
        self.power_profile = power_profile

    @abstractmethod
    def collect(self) -> Inventory:  # pragma: no cover - interface definition
        """Collect inventory data."""

    @staticmethod
    def _bytes_to_gb(value: float) -> float:
        return round(value / (1024 ** 3), 2)

    @staticmethod
    def _kb_to_gb(value: float) -> float:
        return round(value / (1024 ** 2), 2)
