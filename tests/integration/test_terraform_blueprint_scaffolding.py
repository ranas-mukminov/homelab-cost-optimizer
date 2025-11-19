from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
BLUEPRINTS = [
    ROOT / "blueprints" / "terraform" / "proxmox-homelab",
    ROOT / "blueprints" / "terraform" / "k3s-ci-monitoring",
    ROOT / "blueprints" / "terraform" / "micro-saas",
]
REQUIRED_FILES = ["main.tf", "variables.tf", "outputs.tf", "versions.tf"]


@pytest.mark.parametrize("blueprint", BLUEPRINTS)
def test_blueprint_files_exist(blueprint: Path):
    for filename in REQUIRED_FILES:
        assert (blueprint / filename).exists()


def test_terraform_validate(tmp_path):
    terraform = shutil.which("terraform")
    if not terraform:
        pytest.skip("terraform binary not available")

    for blueprint in BLUEPRINTS:
        workdir = tmp_path / blueprint.name
        shutil.copytree(blueprint, workdir)
        subprocess.run([terraform, "init", "-backend=false"], cwd=workdir, check=True)
        subprocess.run([terraform, "validate"], cwd=workdir, check=True)
