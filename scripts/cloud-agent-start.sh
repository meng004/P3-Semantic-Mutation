#!/usr/bin/env bash
# Per-boot: restore the workspace .venv path used by README / CI commands.
set -euo pipefail

VENV="${HOME}/.venvs/p3"
LINK="${PWD}/.venv"

if [[ ! -x "${VENV}/bin/python" ]]; then
  echo "cloud-agent-start: missing ${VENV}; run install first" >&2
  exit 1
fi

if [[ -e "${LINK}" && ! -L "${LINK}" ]]; then
  echo "cloud-agent-start: ${LINK} exists and is not a symlink" >&2
  exit 1
fi

ln -sfn "${VENV}" "${LINK}"
echo "cloud-agent-start: ${LINK} -> ${VENV}"
