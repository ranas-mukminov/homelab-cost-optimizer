from __future__ import annotations

from typing import List

from ..estimators.cost_estimator import CostReport
from ..estimators.power_estimator import PowerReport
from ..models import ConsolidationPlan, Inventory


def generate_text_report(
    inventory: Inventory,
    power_report: PowerReport,
    cost_report: CostReport,
    plan: ConsolidationPlan | None,
) -> str:
    lines: List[str] = []
    lines.append("Homelab Cost Optimizer Report")
    lines.append("================================")
    lines.append(f"Nodes analyzed: {len(inventory.nodes)}")
    lines.append(f"Workloads analyzed: {len(inventory.workloads)}")
    lines.append("")
    lines.append(f"Total power draw: {power_report.total_watts} W")
    lines.append(f"Monthly cost: {cost_report.total_monthly_cost} {cost_report.currency}")
    lines.append("")
    lines.append("Per-node breakdown:")
    for power_entry, cost_entry in zip(power_report.per_node, cost_report.per_node, strict=True):
        lines.append(
            f"- {power_entry.node.name}: {power_entry.watts} W / {cost_entry.monthly_cost} {cost_report.currency}/month"
        )
    lines.append("")
    if plan:
        lines.append("Consolidation scenario:")
        lines.append(f"- Nodes to power down: {', '.join(plan.powered_down_nodes) or 'none'}")
        lines.append(
            f"- Estimated savings: {plan.estimated_watts_saved} W (~{plan.estimated_monthly_savings} {cost_report.currency}/month)"
        )
        if plan.moves:
            lines.append("Suggested moves:")
            for move in plan.moves:
                lines.append(f"  * {move.workload.name}: {move.source_node} -> {move.target_node}")
        if plan.notes:
            lines.append(f"Note: {plan.notes}")
    else:
        lines.append("No consolidation scenario calculated in this run.")
    return "\n".join(lines)
