#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT"

if command -v pip-audit >/dev/null 2>&1; then
  pip-audit || true
else
  echo "pip-audit not installed; skipping" >&2
fi

if command -v bandit >/dev/null 2>&1; then
  bandit -q -r optimizer ai_providers
else
  echo "bandit not installed; skipping" >&2
fi
