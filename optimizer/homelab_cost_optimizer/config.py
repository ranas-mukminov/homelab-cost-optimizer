from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

import yaml

from .models import PowerProfile


@dataclass
class ElectricityPeriod:
    name: str
    price_per_kwh: float


@dataclass
class ElectricityConfig:
    currency: str
    price_per_kwh: float
    periods: List[ElectricityPeriod] = field(default_factory=list)

    def effective_price(self) -> float:
        if not self.periods:
            return self.price_per_kwh
        return sum(period.price_per_kwh for period in self.periods) / len(self.periods)


@dataclass
class ScenarioConfig:
    name: str
    cpu_threshold: float
    ram_threshold: float
    max_node_utilization: float
    cpu_headroom: float = 0.1
    ram_headroom: float = 0.1


@dataclass
class ReportingConfig:
    markdown_template: str = "default"
    enable_ai: bool = False


@dataclass
class OptimizerConfig:
    power_profiles: Dict[str, PowerProfile]
    scenarios: Dict[str, ScenarioConfig]
    reporting: ReportingConfig

    def get_power_profile(self, profile_name: str) -> PowerProfile:
        if profile_name not in self.power_profiles:
            raise KeyError(f"Unknown power profile '{profile_name}'")
        return self.power_profiles[profile_name]

    def get_scenario(self, scenario_name: str) -> ScenarioConfig:
        if scenario_name not in self.scenarios:
            raise KeyError(f"Unknown scenario '{scenario_name}'")
        return self.scenarios[scenario_name]


def _read_yaml(path: str | Path) -> Dict:
    data = yaml.safe_load(Path(path).read_text())
    return data or {}


def load_electricity_config(path: str | Path) -> ElectricityConfig:
    data = _read_yaml(path)
    periods = [
        ElectricityPeriod(name=item["name"], price_per_kwh=float(item["price_per_kwh"]))
        for item in data.get("periods", [])
    ]
    return ElectricityConfig(
        currency=data.get("currency", "USD"),
        price_per_kwh=float(data.get("price_per_kwh", 0.2)),
        periods=periods,
    )


def load_optimizer_config(path: str | Path) -> OptimizerConfig:
    data = _read_yaml(path)
    power_profiles = {
        name: PowerProfile(
            name=name,
            base_idle_watts=float(profile.get("base_idle_watts", 50)),
            watts_per_cpu_core=float(profile.get("watts_per_cpu_core", 10)),
            watts_per_gb_ram=float(profile.get("watts_per_gb_ram", 1)),
        )
        for name, profile in data.get("power_profiles", {}).items()
    }
    if not power_profiles:
        power_profiles["default"] = PowerProfile(
            name="default",
            base_idle_watts=60,
            watts_per_cpu_core=12,
            watts_per_gb_ram=0.9,
        )
    scenarios = {
        name: ScenarioConfig(
            name=name,
            cpu_threshold=float(scenario.get("cpu_threshold", 0.2)),
            ram_threshold=float(scenario.get("ram_threshold", 0.3)),
            max_node_utilization=float(scenario.get("max_node_utilization", 0.75)),
            cpu_headroom=float(scenario.get("cpu_headroom", 0.1)),
            ram_headroom=float(scenario.get("ram_headroom", 0.1)),
        )
        for name, scenario in data.get("scenarios", {}).items()
    }
    if not scenarios:
        scenarios["consolidate-low-util"] = ScenarioConfig(
            name="consolidate-low-util",
            cpu_threshold=0.25,
            ram_threshold=0.3,
            max_node_utilization=0.7,
        )
    reporting_data = data.get("reporting", {})
    reporting = ReportingConfig(
        markdown_template=reporting_data.get("markdown_template", "default"),
        enable_ai=bool(reporting_data.get("enable_ai", False)),
    )
    return OptimizerConfig(
        power_profiles=power_profiles,
        scenarios=scenarios,
        reporting=reporting,
    )
