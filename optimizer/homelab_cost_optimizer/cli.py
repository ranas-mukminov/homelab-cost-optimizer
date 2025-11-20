
from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console

from ai_providers import ProviderNotAvailable, get_provider

from .collectors import collect as run_collector
from .config import load_electricity_config, load_optimizer_config
from .consolidators.heuristic_consolidator import HeuristicConsolidator
from .estimators.cost_estimator import estimate_cost
from .estimators.power_estimator import build_power_report
from .models import Inventory
from .reporters import generate_ai_report, generate_markdown_report, generate_text_report

app = typer.Typer(help="Homelab cost optimizer CLI")
console = Console()


def _load_inventory(path: Path) -> Inventory:
    data = json.loads(path.read_text())
    return Inventory.from_dict(data)


@app.command()
def collect(
    source: Annotated[str, typer.Option(help="Source platform: proxmox|libvirt|docker|k8s")],
    output: Annotated[Path, typer.Option(help="Destination JSON file")],
    optimizer_config: Annotated[Path, typer.Option(help="Optimizer config")] = Path("config/optimizer.example.yaml"),
    power_profile_name: Annotated[str, typer.Option(help="Power profile to use for nodes")] = "default",
    base_url: Annotated[Optional[str], typer.Option(help="Proxmox API URL")] = None,
    token_id: Annotated[Optional[str], typer.Option(help="Proxmox API token ID")] = None,
    token_secret: Annotated[Optional[str], typer.Option(help="Proxmox API token secret")] = None,
    verify_ssl: Annotated[bool, typer.Option(help="Verify TLS certificates")] = True,
    uri: Annotated[str, typer.Option(help="Libvirt connection URI")] = "qemu:///system",
    host_name: Annotated[str, typer.Option(help="Local host name for libvirt/docker")] = "edge-host",
    context: Annotated[Optional[str], typer.Option(help="Kubernetes context name")] = None,
) -> None:
    optimizer_conf = load_optimizer_config(optimizer_config)
    power_profile = optimizer_conf.get_power_profile(power_profile_name)
    kwargs = {"power_profile": power_profile}
    if source == "proxmox":
        if not (base_url and token_id and token_secret):
            raise typer.BadParameter("base_url, token_id, and token_secret are required for Proxmox")
        kwargs.update({
            "base_url": base_url,
            "token_id": token_id,
            "token_secret": token_secret,
            "verify_ssl": verify_ssl,
        })
    elif source == "libvirt":
        kwargs.update({"uri": uri, "host_name": host_name})
    elif source == "docker":
        kwargs.update({"host_name": host_name})
    elif source == "k8s":
        kwargs.update({"context": context})
    inventory = run_collector(source, **kwargs)
    output.write_text(json.dumps(inventory.to_dict(), indent=2))
    console.print(f"Inventory saved to {output}")


@app.command()
def analyze(
    input: Annotated[Path, typer.Option(help="Inventory JSON from the collect step")],
    electricity_config: Annotated[Path, typer.Option(help="Electricity tariff configuration")],
    optimizer_config: Annotated[Path, typer.Option(help="Optimizer config")] = Path("config/optimizer.example.yaml"),
    scenario: Annotated[Optional[str], typer.Option(help="Scenario name to evaluate")] = None,
    report_format: Annotated[str, typer.Option(help="Report style: text or markdown")] = "text",
    output: Annotated[Path, typer.Option(help="Output file path")] = Path("report.txt"),
) -> None:
    inventory = _load_inventory(input)
    electricity = load_electricity_config(electricity_config)
    optimizer_conf = load_optimizer_config(optimizer_config)

    power_report = build_power_report(inventory)
    cost_report = estimate_cost(power_report, electricity)

    plan = None
    if scenario:
        scenario_conf = optimizer_conf.get_scenario(scenario)
        consolidator = HeuristicConsolidator(scenario_conf, electricity)
        plan = consolidator.build_plan(inventory)

    if report_format == "markdown":
        content = generate_markdown_report(inventory, power_report, cost_report, plan)
    else:
        content = generate_text_report(inventory, power_report, cost_report, plan)

    output.write_text(content)
    console.print(f"Report written to {output}")


@app.command()
def suggest(
    input: Annotated[Path, typer.Option(help="Inventory JSON")],
    electricity_config: Annotated[Path, typer.Option(help="Electricity tariff file")],
    optimizer_config: Annotated[Path, typer.Option(help="Optimizer config")] = Path("config/optimizer.example.yaml"),
    scenario: Annotated[str, typer.Option(help="Scenario to run")] = "consolidate-low-util",
    output: Annotated[Path, typer.Option(help="Markdown report output")] = Path("suggestions.md"),
    ai_report: Annotated[bool, typer.Option(help="Generate AI report")] = False,
    ai_provider: Annotated[str, typer.Option(help="AI provider name")] = "mock",
    ai_output: Annotated[Optional[Path], typer.Option(help="File to store AI narrative")] = None,
) -> None:
    inventory = _load_inventory(input)
    electricity = load_electricity_config(electricity_config)
    optimizer_conf = load_optimizer_config(optimizer_config)

    scenario_conf = optimizer_conf.get_scenario(scenario)
    consolidator = HeuristicConsolidator(scenario_conf, electricity)
    power_report = build_power_report(inventory)
    cost_report = estimate_cost(power_report, electricity)
    plan = consolidator.build_plan(inventory)

    markdown = generate_markdown_report(inventory, power_report, cost_report, plan)
    output.write_text(markdown)
    console.print(f"Scenario report stored at {output}")

    if ai_report:
        try:
            provider = get_provider(ai_provider)
            ai_content = generate_ai_report(provider, inventory, power_report, cost_report, plan)
        except ProviderNotAvailable as exc:
            console.print(f"[yellow]AI provider unavailable: {exc}")
            return
        if ai_output:
            ai_output.write_text(ai_content)
            console.print(f"AI narrative stored at {ai_output}")
        else:
            console.print("AI summary:\n" + ai_content)


if __name__ == "__main__":
    app()
