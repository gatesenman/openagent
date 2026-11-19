#!/usr/bin/env bash
# Run the backend test suite and the desktop typecheck/build gate.
# A full Tauri pack needs rustc 1.90+ and is not required here.
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"

if [ -n "${OPENAGENT_TEST_PYTHON:-}" ]; then
  python="$OPENAGENT_TEST_PYTHON"
elif [ -x "$root/.venv/bin/python" ]; then
  python="$root/.venv/bin/python"
else
  python="python3"
fi

echo "backend: $python -m pytest tests/"
(cd "$root/backend" && "$python" -m pytest tests/ -q --tb=short)

echo "desktop: npm run test:gate"
(cd "$root/desktop" && npm run test:gate)
