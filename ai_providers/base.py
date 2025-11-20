from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseAIProvider(ABC):
    name: str

    @abstractmethod
    def generate_blueprint_suggestions(self, context: Dict[str, Any]) -> str:
        """Return human-readable blueprint suggestions."""

    @abstractmethod
    def generate_cost_optimization_report(self, context: Dict[str, Any], prompt: str) -> str:
        """Return summarized optimizer results."""


class ProviderNotAvailable(RuntimeError):
    pass


def ensure_env(var_name: str) -> str:
    import os

    value = os.getenv(var_name)
    if not value:
        raise ProviderNotAvailable(f"Environment variable {var_name} is required")
    return value
