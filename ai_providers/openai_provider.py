from __future__ import annotations

from typing import Any, Dict

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - optional dependency
    OpenAI = None  # type: ignore

from .base import BaseAIProvider, ProviderNotAvailable, ensure_env


class OpenAIProvider(BaseAIProvider):
    name = "openai"

    def __init__(self, model: str = "gpt-4o-mini") -> None:
        if OpenAI is None:
            raise ProviderNotAvailable("openai package is not installed; install with [ai] extra")
        api_key = ensure_env("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def generate_blueprint_suggestions(self, context: Dict[str, Any]) -> str:
        prompt = (
            "You are an IaC architect. Given the following hardware inventory and intended topology, "
            "propose Terraform/Ansible variable values and explain trade-offs.\n"
            f"Context: {context}"
        )
        return self._complete(prompt)

    def generate_cost_optimization_report(self, context: Dict[str, Any], prompt: str) -> str:
        message = (
            "Create a FinOps-style summary with numbered recommendations, "
            "highlighting power savings and consolidation risks.\n"
            f"Prompt: {prompt}\nContext: {context}"
        )
        return self._complete(message)

    def _complete(self, message: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": message}],
            temperature=0.3,
        )
        return response.choices[0].message.content or ""
