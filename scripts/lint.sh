#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT"

ruff .
black --check optimizer ai_providers tests
isort --check-only optimizer ai_providers tests

if command -v yamllint >/dev/null 2>&1; then
  yamllint .
else
  echo "yamllint not installed; skipping" >&2
fi

if command -v terraform >/dev/null 2>&1; then
  terraform fmt -check -recursive blueprints/terraform
  for dir in blueprints/terraform/*/; do
    terraform -chdir="$dir" validate || true
  done
else
  echo "terraform not installed; skipping fmt/validate" >&2
fi

if command -v ansible-lint >/dev/null 2>&1; then
  ansible-lint blueprints/ansible
else
  echo "ansible-lint not installed; skipping" >&2
fi
