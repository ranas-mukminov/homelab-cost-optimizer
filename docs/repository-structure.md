# Repository Structure

```
homelab-cost-optimizer/
├── README.md                # Project overview, bilingual summary, quick start
├── LICENSE                  # Apache-2.0 license
├── LEGAL.md                 # Responsible-use and legal guidance
├── CONTRIBUTING.md          # Contribution workflow and expectations
├── CHANGELOG.md             # Version history
├── pyproject.toml           # Python packaging configuration
├── setup.cfg                # Entry points and tooling config
├── .editorconfig            # Consistent formatting rules
├── .gitignore               # Local and build artifacts to ignore
├── blueprints/              # Terraform, Ansible, k3d assets and AI helper
│   ├── README.md            # Catalog usage guide (added later)
│   ├── docs/                # Topology notes and diagrams
│   ├── terraform/           # Reusable Terraform blueprints
│   ├── ansible/             # Roles, inventories, playbooks
│   ├── k3d/                 # k3d cluster definitions
│   └── ai/                  # Blueprint AI adapter glue
├── optimizer/               # Python package implementing collectors/CLI
│   ├── README.md            # Package-specific quick start
│   └── homelab_cost_optimizer/
│       ├── collectors/      # Proxmox/libvirt/Docker/K8s data sources
│       ├── estimators/      # Power + cost estimation logic
│       ├── consolidators/   # Heuristic consolidation planners
│       ├── reporters/       # Text/Markdown/AI report generators
│       ├── config.py        # Config parsing helpers
│       └── cli.py           # Typer CLI entrypoint
├── ai_providers/            # Provider abstraction + OpenAI/mock implementations
├── config/                  # Example YAML configs (electricity, optimizer)
├── tests/                   # Unit/integration suites
│   ├── unit/
│   └── integration/
├── scripts/                 # lint.sh, format.sh, security_scan.sh, perf_check.sh
└── .github/workflows/       # CI and security workflows
```
