# P3 v3 Synthetic Phase 0/2 Cursor VM Instruction

## Status and authority

This document is a non-authorizing verification instruction. Copying or reading
it does **not** authorize a Cursor VM launch. The user must separately authorize
one fresh VM/conversation after reviewing these bytes.

- Repository: `meng004/P3-Semantic-Mutation`
- Model: `Grok 4.5 High`
- Required implementation commit:
  `8b675c9e7a2f8d99a9abe0f5d618edb9e289db43`
- Scientific-plan SHA-256:
  `911562938a14ad3955a6c1e38080185ba78e92dbf4401efcb10d7c169e4a2772`
- Evidence-design SHA-256:
  `e2a943b30f8096aa65a72c43aa514df67b8d58e16fcf7209930799ee4444c346`
- Scope: synthetic Phase 0 protocol binding and Phase 2 repeatable preflight only
- Cursor commands do not use `rtk`.

## Session gate

Use a brand-new Cursor VM and a brand-new conversation. Do not reuse any prior
Supplemental R3, P3 v3, or failed VM conversation. Before running a command,
confirm that the selected model is exactly `Grok 4.5 High`, the repository is
exactly `meng004/P3-Semantic-Mutation`, and the platform checkout is already at
the required implementation commit.

This gate authorizes no network evidence collection. Platform-provided checkout
is the only repository provisioning assumed by this instruction.

## Allowed command sequence

Run one command at a time, in the repository root, in the exact order below.
Inspect the exit code before continuing. Shell-variable assignment, inline
Python controllers, generated helper scripts, dependency installation, and
command substitution are not part of this instruction. The exact per-command
`PYTHONPATH=src` prefix shown below is permitted; no persistent assignment or
`export` is permitted.

### Task 1 — checkout and capability preflight

```bash
git rev-parse HEAD
git status --porcelain=v1
python3 scripts/p3_v3/evidence.py --help
```

Required assertions:

1. `git rev-parse HEAD` prints exactly
   `8b675c9e7a2f8d99a9abe0f5d618edb9e289db43`;
2. tracked and untracked status output is empty; and
3. CLI help exits 0 and lists exactly the ten frozen commands.

If any assertion fails, report `P3_V3_SYNTHETIC_PHASE0_PHASE2_PREFLIGHT_BLOCKED`
with the command, exit code, and observed output. Because this is non-scientific
preflight, diagnosis and a later fresh rerun are allowed after Local Desktop
review; no scientific authorization is consumed.

### Task 2 — synthetic Phase 0 protocol path

```bash
PYTHONPATH=src python3 -m pytest tests/p3_v3/test_cli.py -q
```

Required assertion: all tests pass, including rejection of a different
well-formed authority hash and verification of both canonical JSON and JSONL
evidence.

### Task 3 — synthetic Phase 2 path

```bash
PYTHONPATH=src python3 -m pytest tests/p3_v3/test_synthetic_phase_path.py tests/p3_v3/test_preflight.py -q
```

Required assertions:

1. the public CLI completes synthetic protocol → pinned synthetic bridge →
   deterministic frames → Package A → preflight;
2. the preflight receipt contains a canonical artifact SHA-256;
3. repository identity accepts normalized HTTPS/SSH forms without requiring one
   raw origin spelling;
4. a failed synthetic preflight can be repeated; and
5. no `intent.json` is created.

### Task 4 — focused regression gate

```bash
PYTHONPATH=src python3 -m pytest tests/p3_v3 -q
```

Required assertion: the complete focused suite passes. Then stop. Do not run any
additional shell command, create a commit, or publish a branch.

## Success report

Return only a concise report headed:

`P3_V3_SYNTHETIC_PHASE0_PHASE2_VERIFIED`

Include the VM/conversation ID, model, exact HEAD, each command exit code, the
focused test count, and an explicit statement that no live P12 data, network
evidence, scientific intent, Package C, mutant, MR execution, commit, or push was
used.

## Prohibited actions

This instruction does not authorize:

- fetching, pulling, switching, repairing, committing, pushing, PR, or merge;
- package installation or environment mutation;
- connection to a live Defect4MR/P12 release or disclosure of any P12 holdout;
- generation or review of semantic mutants;
- candidate/reference MR construction, selection, or execution;
- Package C creation, transfer, mount, or inspection;
- any scientific job intent, evidence collection, statistical analysis, claim
  update, manuscript edit, or downstream experiment; or
- treating a synthetic PASS as evidence for RQ1–RQ4.

The next authorized activity after a PASS is Local Desktop review of the
synthetic verification report and implementation of the four blockers recorded
in the minimum-foundation plan. A real P12 or controlled-study phase requires a
new plan, frozen inputs, review, and separate user authorization.
