<claude-mem-context>
# Memory Context

# [MT完备性] recent context, 2026-04-28 8:02pm GMT+8

No previous sessions found.
</claude-mem-context>

## Cursor Cloud specific instructions

This repo is a Python replication package (no GUI/web server). The "application"
is the deterministic cache-replay statistical pipeline; see `README.md` §3 and
`REPRODUCIBILITY.md` for the canonical commands. The startup update script already
creates `.venv` and installs `requirements-frozen.txt`, so you normally just
activate/use `.venv`.

- Python & venv: runtime is system `python3.12` (CI uses 3.12; `.python-version`
  says 3.11 but is not used here). The venv lives at `.venv`. Creating it needs the
  system package `python3.12-venv` (installed during environment setup / captured in
  the snapshot); it is a system dependency, so it is intentionally NOT in the update
  script. `requirements-frozen.txt` includes `pytest` but not the other `dev` extras
  (`ruff`, `pytest-cov`, `mypy`) from `pyproject.toml`; `pip install ruff` on demand.
- Always run Python with `PYTHONPATH=src` (both `p2` and `p3_v3` packages live under
  `src/`). Canonical test command: `PYTHONPATH=src .venv/bin/pytest -q`.
- Test-suite runtime is heavy: the full suite is ~1690 tests and takes ~35 min on
  this VM because `tests/p3_v3/` and `tests/external_slice/` spawn many git/subprocess/
  C++ (`gcc`/`g++`) fixtures. The README's "192 tests" predates the P3 additions. For a
  quick check, scope to a subdir (e.g. `PYTHONPATH=src .venv/bin/pytest tests/stats -q`).
- KNOWN-RED on `main` (pre-existing, NOT an environment problem): the 28 tests in
  `tests/external_slice/test_check_supplemental_r2_admission.py` and
  `tests/p3_v3/test_preflight.py::test_preflight_passes_without_creating_scientific_intent`
  fail. This matches GitHub Actions (`.github/workflows/sanity.yml` is red on `main`;
  it stops at the first failure via `--maxfail=1`). Do not treat these as setup breakage.
  The `preflight` case is additionally sensitive to the Cloud VM git config, which
  rewrites `git@github.com:`/`ssh://` remotes to HTTPS (`url.<token>.insteadOf`), so the
  test's expected `origin_transport == "SSH"` resolves to `HTTPS` here.
- `external_slice` admission tests compare files against the transport-baseline commit
  object `020b60fb83f7eb1d34f143458fca62beab5aa398` via `git show`/`git ls-tree`; a full
  clone already contains it (CI fetches it explicitly as `refs/remotes/origin/transport-baseline`).
- Headline replication (the real "hello world"), no API keys, fully deterministic:
  `PYTHONPATH=src SMS_VERSION=v4 P2_PRIMARY_VERSION=v3b .venv/bin/python scripts/build_paper_numbers.py`
  must leave `git diff data/results/paper_numbers_v4.json` empty. BOTH env vars are
  required (see `REPRODUCIBILITY.md` §4A). Regenerate paper figures with
  `PYTHONPATH=src .venv/bin/python scripts/generate_figures.py` (writes `figs/*.png`).
- LLM API keys (`.env` from `.env.example`) are ONLY needed for Path B (re-calling LLMs
  to regenerate mutant pools); they are not needed for any headline-number replication.