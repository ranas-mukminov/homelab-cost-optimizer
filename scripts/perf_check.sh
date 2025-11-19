#!/usr/bin/env bash
set -euo pipefail

python - <<'PY'
from optimizer.homelab_cost_optimizer.models import Inventory, Node, PowerProfile, Workload
from optimizer.homelab_cost_optimizer.estimators.power_estimator import build_power_report
from optimizer.homelab_cost_optimizer.config import ElectricityConfig
from optimizer.homelab_cost_optimizer.estimators.cost_estimator import estimate_cost
from optimizer.homelab_cost_optimizer.consolidators.heuristic_consolidator import HeuristicConsolidator
from optimizer.homelab_cost_optimizer.config import ScenarioConfig
import time

profile = PowerProfile(name="default", base_idle_watts=60, watts_per_cpu_core=10, watts_per_gb_ram=1)
nodes = [Node(name=f"node-{i}", kind="hypervisor", total_cpu=32, total_memory_gb=256, power_profile=profile) for i in range(100)]
workloads = [
    Workload(
        name=f"vm-{i}",
        workload_type="vm",
        vcpus=2,
        memory_gb=4,
        utilization_cpu=0.2,
        utilization_memory=0.2,
        node=nodes[i % len(nodes)].name,
    )
    for i in range(1000)
]
inv = Inventory(nodes=nodes, workloads=workloads)
start = time.time()
power = build_power_report(inv)
electricity = ElectricityConfig(currency="USD", price_per_kwh=0.2)
cost = estimate_cost(power, electricity)
scenario = ScenarioConfig(name="perf", cpu_threshold=0.3, ram_threshold=0.3, max_node_utilization=0.8)
consolidator = HeuristicConsolidator(scenario, electricity)
plan = consolidator.build_plan(inv)
delta = time.time() - start
print(f"Runtime: {delta:.2f}s, moves: {len(plan.moves)}")
PY
