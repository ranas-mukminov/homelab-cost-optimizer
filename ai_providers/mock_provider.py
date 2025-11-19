from __future__ import annotations

from typing import Any, Dict

from .base import BaseAIProvider


class MockProvider(BaseAIProvider):
    name = "mock"

    def generate_blueprint_suggestions(self, context: Dict[str, Any]) -> str:
        topology = context.get("topology", "homelab")
        nodes = context.get("nodes", [])
        return (
            f"Deterministic suggestion for {topology}: allocate {len(nodes)} nodes, "
            "spread control plane across first two nodes, keep NAS isolated."
        )

    def generate_cost_optimization_report(self, context: Dict[str, Any], prompt: str) -> str:
        nodes = ", ".join(context.get("plan", {}).get("nodes_powered_down", [])) or "none"
        return (
            "Mock report:\n"
            f"Power draw {context.get('power_draw_watts', 0)} W with monthly cost {context.get('monthly_cost', 0)} {context.get('currency', 'USD')}.\n"
            f"Nodes to power down: {nodes}.\nPrompt: {prompt}"
        )
