#!/usr/bin/env bash
# Idempotent repository bootstrap for the P2/P3 semantic-mutation experiments.
# Creates a Python 3.12 virtualenv and installs the pinned dependency set.
set -euo pipefail

cd "$(dirname "$0")/.."

# The base image ships python3.12 but not the venv seed package; add it once.
if ! python3.12 -m venv --help >/dev/null 2>&1 || ! dpkg -s python3.12-venv >/dev/null 2>&1; then
  sudo apt-get update
  sudo apt-get install -y --no-install-recommends python3.12-venv
fi

# Create the virtualenv only if it is missing or broken (keeps install idempotent).
if [ ! -x .venv/bin/python ]; then
  python3.12 -m venv .venv
fi

.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements-frozen.txt

echo "install.sh: environment ready (.venv with pinned deps)."
