#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT"

black optimizer ai_providers tests
isort optimizer ai_providers tests

if command -v terraform >/dev/null 2>&1; then
  terraform fmt -recursive blueprints/terraform
else
  echo "terraform not installed; skipping terraform fmt" >&2
fi
