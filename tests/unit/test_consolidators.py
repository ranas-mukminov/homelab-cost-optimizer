from homelab_cost_optimizer.config import ElectricityConfig, ScenarioConfig
from homelab_cost_optimizer.consolidators.heuristic_consolidator import HeuristicConsolidator
from homelab_cost_optimizer.models import Inventory, Node, PowerProfile, Workload

PROFILE = PowerProfile(
    name="default", base_idle_watts=50, watts_per_cpu_core=10, watts_per_gb_ram=1
)


def build_inventory() -> Inventory:
    nodes = [
        Node(
            name="node1", kind="hypervisor", total_cpu=8, total_memory_gb=32, power_profile=PROFILE
        ),
        Node(
            name="node2", kind="hypervisor", total_cpu=8, total_memory_gb=32, power_profile=PROFILE
        ),
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
        ),
        Workload(
            name="vm2",
            workload_type="vm",
            vcpus=2,
            memory_gb=4,
            utilization_cpu=0.3,
            utilization_memory=0.3,
            node="node1",
        ),
    ]
    return Inventory(nodes=nodes, workloads=workloads)


def test_consolidator_moves_workloads():
    inventory = build_inventory()
    scenario = ScenarioConfig(
        name="consolidate-low-util",
        cpu_threshold=0.6,
        ram_threshold=0.6,
        max_node_utilization=0.9,
    )
    electricity = ElectricityConfig(currency="USD", price_per_kwh=0.2)
    consolidator = HeuristicConsolidator(scenario, electricity)
    plan = consolidator.build_plan(inventory)
    assert plan.moves
    assert plan.estimated_monthly_savings >= 0
