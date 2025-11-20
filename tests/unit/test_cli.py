from __future__ import annotations

import json
from pathlib import Path

from homelab_cost_optimizer.cli import app
from homelab_cost_optimizer.models import Inventory, Node, PowerProfile, Workload
from typer.testing import CliRunner

runner = CliRunner()


def _inventory() -> Inventory:
    profile = PowerProfile(name="default", base_idle_watts=60, watts_per_cpu_core=10, watts_per_gb_ram=1)
    node = Node(name="node1", kind="hypervisor", total_cpu=8, total_memory_gb=32, power_profile=profile)
    workload = Workload(
        name="vm1",
        workload_type="vm",
        vcpus=2,
        memory_gb=2,
        utilization_cpu=0.3,
        utilization_memory=0.3,
        node="node1",
    )
    return Inventory(nodes=[node], workloads=[workload])


def _write_files(tmp_path: Path) -> tuple[Path, Path, Path]:
    inventory = _inventory()
    inventory_file = tmp_path / "inventory.json"
    inventory_file.write_text(json.dumps(inventory.to_dict()))

    electricity = tmp_path / "electricity.yaml"
    electricity.write_text("currency: USD\nprice_per_kwh: 0.2\n")

    optimizer = tmp_path / "optimizer.yaml"
    optimizer.write_text(
        """
        power_profiles:
          default:
            base_idle_watts: 60
            watts_per_cpu_core: 10
            watts_per_gb_ram: 1
        scenarios:
          consolidate-low-util:
            cpu_threshold: 0.5
            ram_threshold: 0.5
            max_node_utilization: 0.8
        """
    )
    return inventory_file, electricity, optimizer


def test_analyze_command(tmp_path):
    inventory_file, electricity, optimizer = _write_files(tmp_path)
    output = tmp_path / "report.txt"
    result = runner.invoke(
        app,
        [
            "analyze",
            "--input",
            str(inventory_file),
            "--electricity-config",
            str(electricity),
            "--optimizer-config",
            str(optimizer),
            "--output",
            str(output),
        ],
    )
    assert result.exit_code == 0
    assert output.exists()


def test_suggest_command(tmp_path):
    inventory_file, electricity, optimizer = _write_files(tmp_path)
    output = tmp_path / "suggestions.md"
    result = runner.invoke(
        app,
        [
            "suggest",
            "--input",
            str(inventory_file),
            "--electricity-config",
            str(electricity),
            "--optimizer-config",
            str(optimizer),
            "--output",
            str(output),
        ],
    )
    assert result.exit_code == 0
    assert output.exists()
