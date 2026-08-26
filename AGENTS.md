<claude-mem-context>
# Memory Context

# [MT完备性] recent context, 2026-04-28 8:02pm GMT+8

No previous sessions found.
</claude-mem-context>

## Cloud Agent environment

Pinned dependencies are installed to `$HOME/.venvs/p3` and linked as `.venv` on each boot (`scripts/cloud-agent-start.sh`). Use the README commands as written:

```bash
PYTHONPATH=src .venv/bin/pytest tests/ -q
PYTHONPATH=src SMS_VERSION=v4 P2_PRIMARY_VERSION=v3b \
  .venv/bin/python scripts/build_paper_numbers.py
```

LLM API keys in `.env` are optional. Cache-replay and the unit suite do not need them.
