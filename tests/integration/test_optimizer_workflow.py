from __future__ import annotations

import json
from pathlib import Path

from homelab_cost_optimizer.config import load_electricity_config, load_optimizer_config
from homelab_cost_optimizer.consolidators.heuristic_consolidator import HeuristicConsolidator
from homelab_cost_optimizer.estimators.cost_estimator import estimate_cost
from homelab_cost_optimizer.estimators.power_estimator import build_power_report
from homelab_cost_optimizer.models import Inventory, Node, PowerProfile, Workload
from homelab_cost_optimizer.reporters.markdown_reporter import generate_markdown_report


def _inventory() -> Inventory:
    profile = PowerProfile(name="default", base_idle_watts=60, watts_per_cpu_core=10, watts_per_gb_ram=1)
    nodes = [
        Node(name="node1", kind="hypervisor", total_cpu=8, total_memory_gb=32, power_profile=profile),
        Node(name="node2", kind="hypervisor", total_cpu=8, total_memory_gb=32, power_profile=profile),
    ]
    workloads = [
        Workload(
            name="vm1",
            workload_type="vm",
            vcpus=2,
            memory_gb=4,
            utilization_cpu=0.3,
            utilization_memory=0.3,
            node="node1",
        )
    ]
    return Inventory(nodes=nodes, workloads=workloads)


def test_full_workflow(tmp_path):
    electricity_file = tmp_path / "elect.yaml"
    electricity_file.write_text("currency: USD\nprice_per_kwh: 0.2\n")
    optimizer_file = tmp_path / "optimizer.yaml"
    optimizer_file.write_text(
        """
        power_profiles:
          default:
            base_idle_watts: 60
            watts_per_cpu_core: 10
            watts_per_gb_ram: 1
        scenarios:
          consolidate-low-util:
            cpu_threshold: 0.5
            ram_threshold: 0.6
            max_node_utilization: 0.8
        """
    )

    inventory = _inventory()
    electricity = load_electricity_config(electricity_file)
    optimizer_conf = load_optimizer_config(optimizer_file)
    power_report = build_power_report(inventory)
    cost_report = estimate_cost(power_report, electricity)
    consolidator = HeuristicConsolidator(optimizer_conf.get_scenario("consolidate-low-util"), electricity)
    plan = consolidator.build_plan(inventory)
    markdown = generate_markdown_report(inventory, power_report, cost_report, plan)
    assert "Nodes to power down" in markdown
    assert plan.estimated_monthly_savings >= 0
