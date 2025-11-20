from homelab_cost_optimizer.config import ElectricityConfig, ElectricityPeriod
from homelab_cost_optimizer.estimators.cost_estimator import estimate_cost
from homelab_cost_optimizer.estimators.power_estimator import estimate_node_power
from homelab_cost_optimizer.models import Node, PowerProfile, Workload


def test_estimate_node_power_idle():
    profile = PowerProfile("test", base_idle_watts=50, watts_per_cpu_core=10, watts_per_gb_ram=1)
    node = Node("node1", "server", 10, 32, profile)
    # No workloads
    usage = estimate_node_power(node, [])
    assert usage.watts == 50.0


def test_estimate_node_power_with_load():
    profile = PowerProfile("test", base_idle_watts=50, watts_per_cpu_core=10, watts_per_gb_ram=1)
    node = Node("node1", "server", 10, 32, profile)
    # Workload: 2 vCPUs @ 50%, 4GB RAM @ 50%
    # CPU load = 2 * 0.5 = 1.0 core
    # RAM load = 4 * 0.5 = 2.0 GB
    # Watts = 50 + (10 * 1.0) + (1 * 2.0) = 50 + 10 + 2 = 62
    w1 = Workload("w1", "vm", 2, 4, 0.5, 0.5, "node1")
    usage = estimate_node_power(node, [w1])
    assert usage.watts == 62.0


def test_estimate_node_power_min_utilization():
    profile = PowerProfile("test", base_idle_watts=50, watts_per_cpu_core=10, watts_per_gb_ram=1)
    node = Node("node1", "server", 10, 32, profile)
    # Workload: 2 vCPUs @ 0%, 4GB RAM @ 0%
    # Should floor to 0.1
    # CPU load = 2 * 0.1 = 0.2
    # RAM load = 4 * 0.1 = 0.4
    # Watts = 50 + (10 * 0.2) + (1 * 0.4) = 50 + 2 + 0.4 = 52.4
    w1 = Workload("w1", "vm", 2, 4, 0.0, 0.0, "node1")
    usage = estimate_node_power(node, [w1])
    assert usage.watts == 52.4


def test_estimate_cost_simple():
    from homelab_cost_optimizer.estimators.power_estimator import NodePowerUsage, PowerReport

    profile = PowerProfile("test", 50, 10, 1)
    node = Node("node1", "server", 10, 32, profile)
    power_report = PowerReport([NodePowerUsage(node, 100.0)])  # 100 Watts

    config = ElectricityConfig("USD", 0.10, [])  # $0.10 per kWh

    # Monthly cost = 100W * 730h / 1000 = 73 kWh
    # Cost = 73 * 0.10 = $7.30
    report = estimate_cost(power_report, config, monthly_hours=730)

    assert report.total_monthly_cost == 7.30
    assert len(report.per_node) == 1
    assert report.per_node[0].monthly_cost == 7.30


def test_estimate_cost_periods():
    from homelab_cost_optimizer.estimators.power_estimator import NodePowerUsage, PowerReport

    profile = PowerProfile("test", 50, 10, 1)
    node = Node("node1", "server", 10, 32, profile)
    power_report = PowerReport([NodePowerUsage(node, 100.0)])

    # 2 periods: Day ($0.20), Night ($0.10). Average = $0.15
    periods = [ElectricityPeriod("Day", 0.20), ElectricityPeriod("Night", 0.10)]
    config = ElectricityConfig("USD", 0.0, periods)

    # Cost = 73 kWh * $0.15 = 10.95
    report = estimate_cost(power_report, config)
    assert report.total_monthly_cost == 10.95
