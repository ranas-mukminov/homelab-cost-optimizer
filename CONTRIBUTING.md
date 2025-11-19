# Contributing

Thank you for helping improve homelab-cost-optimizer! Please follow the steps below so reviews go smoothly.

1. **Discuss first** – open an issue describing the change (new blueprint, collector, bugfix). Attach diagrams or example inventories when relevant.
2. **Branch & scope** – use topic branches (`feature/xyz`) and keep pull requests focused on one logical change.
3. **Coding style** – Python code follows Black/Isort/Ruff, Terraform uses `terraform fmt`, Ansible YAML uses 2-space indents.
4. **Tests** – add or update unit/integration tests. Run locally: `pytest`, `scripts/lint.sh`, `scripts/security_scan.sh`, `scripts/perf_check.sh`.
5. **Docs** – update README sections, blueprint READMEs, and CHANGELOG entries describing user-facing changes.
6. **Sign-off** – confirm you have the right to contribute the code and it complies with Apache-2.0.

Pull requests that fail lint/tests/security gates or include credentials will be rejected. Thank you for keeping the project safe and reproducible!
