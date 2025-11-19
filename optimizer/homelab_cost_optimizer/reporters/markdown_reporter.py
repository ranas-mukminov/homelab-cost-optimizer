from __future__ import annotations

from typing import List

from ..estimators.cost_estimator import CostReport
from ..estimators.power_estimator import PowerReport
from ..models import ConsolidationPlan, Inventory


def generate_markdown_report(
    inventory: Inventory,
    power_report: PowerReport,
    cost_report: CostReport,
    plan: ConsolidationPlan | None,
) -> str:
    lines: List[str] = []
    lines.append("# Homelab Cost Optimizer Summary")
    lines.append("")
    lines.append(f"**Nodes**: {len(inventory.nodes)} | **Workloads**: {len(inventory.workloads)}")
    lines.append(f"**Power draw**: {power_report.total_watts} W | **Monthly cost**: {cost_report.total_monthly_cost} {cost_report.currency}")
    lines.append("")
    lines.append("## Per-node energy & cost")
    lines.append("| Node | Watts | Monthly cost |")
    lines.append("| --- | ---: | ---: |")
    for power_entry, cost_entry in zip(power_report.per_node, cost_report.per_node):
        lines.append(
            f"| {power_entry.node.name} | {power_entry.watts} | {cost_entry.monthly_cost} {cost_report.currency} |"
        )
    lines.append("")
    if plan:
        lines.append("## Consolidation scenario")
        nodes_line = f"**Nodes to power down**: {', '.join(plan.powered_down_nodes) or 'none'}"
        savings_line = (
            f"**Estimated savings**: {plan.estimated_watts_saved} W / {plan.estimated_monthly_savings} {cost_report.currency} per month"
        )
        lines.append(nodes_line)
        lines.append(savings_line)
        if plan.moves:
            lines.append("")
            lines.append("### Proposed workload moves")
            lines.append("| Workload | From | To |")
            lines.append("| --- | --- | --- |")
            for move in plan.moves:
                lines.append(f"| {move.workload.name} | {move.source_node} | {move.target_node} |")
        if plan.notes:
            lines.append("")
            lines.append(f"> {plan.notes}")
    else:
        lines.append("No consolidation scenario calculated in this run.")
    return "\n".join(lines)
