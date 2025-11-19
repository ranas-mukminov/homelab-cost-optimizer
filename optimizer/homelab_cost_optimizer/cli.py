from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

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
    source: str = typer.Option(..., help="Source platform: proxmox|libvirt|docker|k8s"),
    output: Path = typer.Option(..., help="Destination JSON file"),
    optimizer_config: Path = typer.Option(Path("config/optimizer.example.yaml"), help="Optimizer config"),
    power_profile_name: str = typer.Option("default", help="Power profile to use for nodes"),
    base_url: Optional[str] = typer.Option(None, help="Proxmox API URL"),
    token_id: Optional[str] = typer.Option(None, help="Proxmox API token ID"),
    token_secret: Optional[str] = typer.Option(None, help="Proxmox API token secret"),
    verify_ssl: bool = typer.Option(True, help="Verify TLS certificates"),
    uri: str = typer.Option("qemu:///system", help="Libvirt connection URI"),
    host_name: str = typer.Option("edge-host", help="Local host name for libvirt/docker"),
    context: Optional[str] = typer.Option(None, help="Kubernetes context name"),
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
    input: Path = typer.Option(..., help="Inventory JSON from the collect step"),
    electricity_config: Path = typer.Option(..., help="Electricity tariff configuration"),
    optimizer_config: Path = typer.Option(Path("config/optimizer.example.yaml"), help="Optimizer config"),
    scenario: Optional[str] = typer.Option(None, help="Scenario name to evaluate"),
    report_format: str = typer.Option("text", help="Report style: text or markdown"),
    output: Path = typer.Option(Path("report.txt"), help="Output file path"),
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
    input: Path = typer.Option(..., help="Inventory JSON"),
    electricity_config: Path = typer.Option(..., help="Electricity tariff file"),
    optimizer_config: Path = typer.Option(Path("config/optimizer.example.yaml"), help="Optimizer config"),
    scenario: str = typer.Option("consolidate-low-util", help="Scenario to run"),
    output: Path = typer.Option(Path("suggestions.md"), help="Markdown report output"),
    ai_report: bool = typer.Option(False, help="Generate AI report"),
    ai_provider: str = typer.Option("mock", help="AI provider name"),
    ai_output: Optional[Path] = typer.Option(None, help="File to store AI narrative"),
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
