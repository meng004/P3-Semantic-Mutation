#!/usr/bin/env bash
# Idempotent Cloud Agent install: pinned Python deps live outside /workspace
# so a later checkout does not erase the environment-build snapshot.
set -euo pipefail

VENV="${HOME}/.venvs/p3"
REQ="${PWD}/requirements-frozen.txt"
TRANSPORT_BASELINE="020b60fb83f7eb1d34f143458fca62beab5aa398"

if [[ ! -f "${REQ}" ]]; then
  echo "cloud-agent-install: missing ${REQ}" >&2
  exit 1
fi

if ! python3 -c "import ensurepip, venv" >/dev/null 2>&1; then
  sudo apt-get update
  sudo DEBIAN_FRONTEND=noninteractive apt-get install -y python3-venv python3-dev
fi

mkdir -p "$(dirname "${VENV}")"
if [[ ! -x "${VENV}/bin/python" ]]; then
  python3 -m venv "${VENV}"
fi

"${VENV}/bin/python" -m pip install --upgrade pip
"${VENV}/bin/pip" install -r "${REQ}"

if git remote get-url origin >/dev/null 2>&1; then
  git fetch --no-tags --depth=1 origin \
    "+${TRANSPORT_BASELINE}:refs/remotes/origin/transport-baseline" || \
    echo "cloud-agent-install: transport-baseline fetch skipped" >&2
fi

echo "cloud-agent-install: ready (${VENV})"
"${VENV}/bin/python" -c "import numpy,scipy,pytest; print('python', __import__('sys').version.split()[0])"
