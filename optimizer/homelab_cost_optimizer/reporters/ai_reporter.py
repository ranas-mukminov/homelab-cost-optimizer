from __future__ import annotations

from typing import Any, Dict

from ai_providers.base import BaseAIProvider

from ..estimators.cost_estimator import CostReport
from ..estimators.power_estimator import PowerReport
from ..models import ConsolidationPlan, Inventory


def generate_ai_report(
    provider: BaseAIProvider,
    inventory: Inventory,
    power_report: PowerReport,
    cost_report: CostReport,
    plan: ConsolidationPlan | None,
) -> str:
    payload: Dict[str, Any] = {
        "nodes": [node.name for node in inventory.nodes],
        "workloads": [workload.name for workload in inventory.workloads],
        "power_draw_watts": power_report.total_watts,
        "monthly_cost": cost_report.total_monthly_cost,
        "currency": cost_report.currency,
        "plan": {
            "nodes_powered_down": plan.powered_down_nodes if plan else [],
            "moves": [
                {
                    "workload": move.workload.name,
                    "source": move.source_node,
                    "target": move.target_node,
                }
                for move in (plan.moves if plan else [])
            ],
            "savings_monthly": plan.estimated_monthly_savings if plan else 0.0,
        },
    }
    prompt = (
        "Summarize the optimizer results, highlight savings opportunities, list top 3 actions, "
        "and describe risk or validation steps."
    )
    try:
        return provider.generate_cost_optimization_report(payload, prompt)
    except Exception as exc:  # pragma: no cover - best effort fallback
        return (
            "AI report unavailable due to error: "
            + str(exc)
            + "\nFallback summary: consolidate nodes "
            + ", ".join(payload["plan"]["nodes_powered_down"]) or "no consolidation"
        )
