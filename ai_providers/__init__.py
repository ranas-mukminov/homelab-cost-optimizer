from __future__ import annotations

from typing import Dict, Type

from .base import BaseAIProvider, ProviderNotAvailable
from .mock_provider import MockProvider

PROVIDERS: Dict[str, Type[BaseAIProvider]] = {
    "mock": MockProvider,
}

try:  # pragma: no cover - optional dependency
    from .openai_provider import OpenAIProvider

    PROVIDERS["openai"] = OpenAIProvider
except ProviderNotAvailable:
    pass
except Exception:  # ImportError
    pass


def get_provider(name: str, **kwargs) -> BaseAIProvider:
    name = name.lower()
    if name not in PROVIDERS:
        raise ProviderNotAvailable(f"Unknown AI provider '{name}'. Available: {', '.join(PROVIDERS)}")
    return PROVIDERS[name](**kwargs)
