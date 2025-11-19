from homelab_cost_optimizer.estimators.cost_estimator import estimate_cost
from homelab_cost_optimizer.estimators.power_estimator import build_power_report
from homelab_cost_optimizer.config import ElectricityConfig
from homelab_cost_optimizer.models import Inventory, Node, PowerProfile, Workload


def _inventory() -> Inventory:
    profile = PowerProfile(name="default", base_idle_watts=60, watts_per_cpu_core=10, watts_per_gb_ram=1)
    node = Node(name="node1", kind="hypervisor", total_cpu=8, total_memory_gb=64, power_profile=profile)
    workload = Workload(
        name="vm1",
        workload_type="vm",
        vcpus=2,
        memory_gb=4,
        utilization_cpu=0.5,
        utilization_memory=0.5,
        node="node1",
    )
    return Inventory(nodes=[node], workloads=[workload])


def test_power_and_cost_estimation():
    inventory = _inventory()
    power_report = build_power_report(inventory)
    assert power_report.total_watts > 60

    electricity = ElectricityConfig(currency="USD", price_per_kwh=0.2)
    cost_report = estimate_cost(power_report, electricity, monthly_hours=10)
    assert cost_report.total_monthly_cost > 0
