import pytest
from homelab_cost_optimizer.models import Inventory


def test_inventory_validation_missing_node_name():
    data = {"nodes": [{"kind": "server"}], "workloads": []}
    with pytest.raises(ValueError, match="Node missing required field 'name'"):
        Inventory.from_dict(data)


def test_inventory_validation_missing_workload_name():
    data = {"nodes": [{"name": "node1"}], "workloads": [{"vcpus": 1}]}
    with pytest.raises(ValueError, match="Workload missing required field 'name'"):
        Inventory.from_dict(data)


def test_inventory_valid():
    data = {
        "nodes": [{"name": "node1", "total_cpu": 10}],
        "workloads": [{"name": "app1", "vcpus": 1}],
    }
    inv = Inventory.from_dict(data)
    assert len(inv.nodes) == 1
    assert inv.nodes[0].name == "node1"
    assert len(inv.workloads) == 1
    assert inv.workloads[0].name == "app1"
