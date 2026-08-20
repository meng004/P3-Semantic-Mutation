# Cursor VM Launch Packet: P3-V3-MEF-ALIGN-01

## Task identity

- Task ID: `P3-V3-MEF-ALIGN-01`
- Task type: development and synthetic verification; **not** a scientific run.
- Repository: `meng004/P3-Semantic-Mutation`
- Required model: `Grok 4.5 High`
- Source branch carrying the plan: `codex/p3-semantic-mutant-construction-principles`
- Exact implementation base commit:
  `a03bd17dabee9e2eba3997f5d4eaceb56865aff0`
- Exact implementation base tree:
  `ffadc76662c42b24abda75375949294810761b5b`
- Execution branch:
  `cursor/p3-v3-minimum-evidence-foundation-alignment`
- Implementation plan:
  `docs/superpowers/plans/2026-08-10-p3-v3-minimum-evidence-foundation-alignment-implementation.md`
- Implementation-plan SHA-256:
  `7c55ab41327395b819571da3931f142e916ac9d96910fec10b7d3cdd6e6c4ab3`
- Governing scientific plan:
  `docs/superpowers/plans/2026-08-08-p3-semantic-mutant-argumentation-experiment.md`
- Scientific-plan SHA-256:
  `fea00496801c31ba074aa74742f5e6a77019ffc2e344642122a15462d7443830`
- Governing evidence design:
  `docs/superpowers/specs/2026-08-08-p3-v3-evidence-foundation-design.md`
- Evidence-design SHA-256:
  `7e614e96aac833786d1b29580f8fae7d3f03c6567d7ca94f3e3c017addad2fa9`

## Objective

Align the existing P3 v3 minimum-evidence implementation with the frozen,
non-circular experiment design. Preserve existing canonical-artifact, pinned-Git,
package, immutable-ledger, and repeatable-preflight primitives. Add the revised
public behavior frame, outcome-blind Profiling Workload, failure-conservative
technique classification, deterministic `E_COMMON` and `E_CONTRACT`, Package
A/B role isolation, atomic job identity, frozen P12 missingness estimand, and
the synthetic Phase 0 -> Phase 7 evidence path.

Success proves only that the minimum evidence channel is implemented and
synthetically verified. It does not provide evidence for RQ1-RQ4.

## Authorization and execution boundary

This packet is an instruction artifact, not authorization from Local Desktop to
start a VM. Start only after the user creates a brand-new Cursor cloud Agent/VM
and pastes this packet into a new conversation.

The source commit must already be reachable from the remote source branch. If it
is not, return `P3_V3_MEF_ALIGN_SOURCE_COMMIT_UNAVAILABLE` and stop. This is a
repeatable development bootstrap failure, not a consumed scientific run.

Development test failures are expected under RED -> GREEN. Diagnose and repair
them normally. Do not apply the former Supplemental-R3 “first failure consumes
authorization” rule. Scientific authorization does not begin in this task
because this task is forbidden from creating a real scientific job.

## Non-negotiable scope

Allowed production files:

```text
src/p3_v3/artifacts.py
src/p3_v3/bridge_and_frames.py
src/p3_v3/packages.py
src/p3_v3/run_records.py
src/p3_v3/preflight.py
scripts/p3_v3/evidence.py
```

`artifacts.py` should remain unchanged unless an existing primitive has a
demonstrated defect that blocks the governing design. Tests and synthetic
fixtures may be changed under `tests/p3_v3/`. The historical implementation
plan may receive only the supersession note required by Task 9.

Forbidden:

- access, copy, reveal, or modify real P12 Holdout/Package C content;
- read a real buggy/fixed pair, issue, patch, or reference MR;
- construct a real semantic or syntactic mutant;
- execute a real MR or collect a real outcome;
- use network evidence or external model calls in tests;
- write manuscript results or change RQ claims from `blocked`;
- add a generic workflow/schema framework, a custom Cursor controller, YAML
  authority, or a new production module;
- modify the governing scientific plan or evidence-design bytes;
- create a PR, merge, rebase, cherry-pick, or force-push;
- use `rtk` in Cursor VM commands.

## Bootstrap commands

Run each command separately. Do not prepend `rtk`.

```bash
git status --porcelain=v1
git remote get-url origin
git fetch --no-tags origin codex/p3-semantic-mutant-construction-principles
git cat-file -e a03bd17dabee9e2eba3997f5d4eaceb56865aff0^{commit}
git switch -c cursor/p3-v3-minimum-evidence-foundation-alignment a03bd17dabee9e2eba3997f5d4eaceb56865aff0
git rev-parse HEAD
git rev-parse HEAD^{tree}
git status --porcelain=v1
shasum -a 256 docs/superpowers/plans/2026-08-10-p3-v3-minimum-evidence-foundation-alignment-implementation.md
shasum -a 256 docs/superpowers/plans/2026-08-08-p3-semantic-mutant-argumentation-experiment.md
shasum -a 256 docs/superpowers/specs/2026-08-08-p3-v3-evidence-foundation-design.md
```

Bootstrap acceptance:

- the initial status is clean;
- `origin` is the `meng004/P3-Semantic-Mutation` repository, accepting either
  its SSH or HTTPS URL spelling after normalized owner/repository comparison;
- the exact base commit and tree equal the values in Task identity;
- all three SHA-256 values equal the values in Task identity;
- the new execution branch did not previously exist locally or remotely;
- status after switching is clean.

Do not repair a wrong commit by editing files. A missing remote source commit is
reported to Local Desktop as the source-unavailable verdict above.

## Baseline

Read the implementation plan and both governing documents completely. Then run:

```bash
PYTHONPATH=src python3 -m pytest tests/p3_v3 -q
```

Expected base result: `53 passed`. A different result is a development
diagnostic: investigate the environment and repository state before editing.
Do not weaken a test or change a frozen authority to manufacture the expected
count.

## Required implementation sequence

Execute the implementation plan task-by-task in the following order. For every
task, first add the specified failing tests, run its focused RED command and
confirm failure for the intended missing behavior, then implement the minimum
production change, run GREEN, review the diff, and create the exact task commit.

1. `Rebind protocol authority and remove CLI-owned scientific rules`
   - Exact commit subject: `feat(p3-v3): bind revised protocol authority`
2. `Derive the public behavior frame and exact Profiling Workload`
   - Exact commit subject: `feat(p3-v3): derive outcome-blind profiling workload`
3. `Classify implementation technique without dropping failures`
   - Exact commit subject: `feat(p3-v3): classify technique with failure bounds`
4. `Freeze deterministic generator registry and E_COMMON`
   - Exact commit subject: `feat(p3-v3): freeze common evaluation inputs`
5. `Close slot applicability and generate E_CONTRACT`
   - Exact commit subject: `feat(p3-v3): close contract input chronology`
6. `Enforce Package A/B input roles and proposer isolation`
   - Exact commit subject: `feat(p3-v3): separate package input roles`
7. `Bind atomic job identity, retry ceiling, and P12 estimand`
   - Exact commit subject: `feat(p3-v3): freeze P12 missingness estimand`
8. `Complete repeatable preflight capability gates`
   - Exact commit subject: `feat(p3-v3): verify phase preflight capabilities`
9. `Wire the thin CLI and close the synthetic Phase 0 -> Phase 7 path`
   - Exact commit subject: `feat(p3-v3): align minimum evidence foundation`

The implementation plan is authoritative for exact files, interfaces, schemas,
test cases, commands, constants, and completion boundaries. Do not compress or
reinterpret a task. If code reality conflicts with the plan, preserve the
scientific rule, make the smallest compatible implementation, and record the
deviation and evidence in the handoff.

## Scientific invariants to verify during implementation

1. Selection inputs contain no mutant, MR, P12 outcome, dynamic coverage, or
   real-defect result.
2. Public behavior discovery retains absent, unsupported, invalid, failed, and
   uncertain cases; it never replaces a subject or command by convenience.
3. Scale budgets are exactly `10/15/20`; `E_COMMON` has exactly 30 frozen
   ordinals; each applicable slot has exactly five `E_CONTRACT` ordinals.
4. Technique inference is category-equal and failure-conservative. No robust
   winner means `TECH_UNCERTAIN`.
5. `E_COMMON` is frozen before sites/contracts and is the only primary RQ3/RQ4
   input. `E_CONTRACT` is pre-patch and may enter only activation,
   certification, or explicitly labelled sensitivity work.
6. NOT_APPLICABLE and applicable slot paths are mutually exclusive and
   chronologically closed.
7. Package A proposer views exclude profiling outcomes and both evaluation-input
   inventories. Package A/B exclude Package C.
8. Every result has an earlier immutable intent. Development preflight creates
   no scientific intent and may be rerun after diagnosis.
9. Infrastructure attempts are limited to three for an identical frozen job;
   deterministic/scientific terminal results are not retried.
10. The Phase 7 denominator is frozen before outcomes. Primary inference is the
    intention-to-evaluate lower bound; upper-bound and complete-case analyses are
    secondary and report both unresolved classes.
11. Every RQ claim remains `blocked` throughout this task.

## Verification commands

After Task 9, run exactly:

```bash
PYTHONPATH=src python3 -m pytest tests/p3_v3 -q
PYTHONPATH=src python3 -m pytest -q
PYTHONPATH=src python3 -m ruff check src/p3_v3 scripts/p3_v3 tests/p3_v3
git diff --check a03bd17dabee9e2eba3997f5d4eaceb56865aff0..HEAD
git status --porcelain=v1
```

If the repository uses an environment-specific Python executable, first prove
that it is Python 3.11 and substitute only that executable token. Do not change
test selection or add pytest environment filters.

Then produce a node-level evidence map in the final handoff:

- every numbered test requirement in evidence-design Section 12 -> one or more
  exact pytest node IDs;
- every acceptance criterion in Section 13 -> exact test node IDs and, where
  necessary, a source invariant;
- identify any criterion established only by a self-declared field; that is a
  blocking gap, not a pass.

## Final acceptance conditions

The task passes only if all of the following are true:

- exact source commit/tree and all three authority hashes matched at bootstrap;
- all nine task commits exist in order on the execution branch;
- focused `tests/p3_v3` and the complete repository test suite pass;
- Ruff and `git diff --check` pass;
- the execution worktree is clean after all commits;
- the CLI exposes exactly the ten commands in evidence-design Section 4.6;
- the synthetic Phase 0 -> Phase 7 test performs no network or real-P12 access;
- the 25-test/20-criterion evidence map has no uncovered or self-certified row;
- no forbidden file, scientific run, outcome, claim change, PR, merge, rebase,
  cherry-pick, or force-push occurred.

## Publication and handoff

Only after every acceptance condition passes, push the execution branch once:

```bash
git push -u origin cursor/p3-v3-minimum-evidence-foundation-alignment
```

Do not create a PR or merge. Return this structured handoff:

```text
P3_V3_MEF_ALIGN_IMPLEMENTATION_COMPLETE
task_id: P3-V3-MEF-ALIGN-01
base_commit: a03bd17dabee9e2eba3997f5d4eaceb56865aff0
execution_branch: cursor/p3-v3-minimum-evidence-foundation-alignment
final_commit: <40 lowercase hex>
focused_tests: <passed count and duration>
repository_tests: <passed count and duration>
ruff: PASS
diff_check: PASS
worktree_clean: true
section_12_coverage: 25/25
section_13_coverage: 20/20
claims_status: blocked
real_p12_access: false
real_scientific_jobs: 0
push: PASS
limitations: <concise list or NONE>
```

If a blocking implementation or environment problem remains after diagnosis,
do not claim completion and do not weaken the design. Return:

```text
P3_V3_MEF_ALIGN_IMPLEMENTATION_BLOCKED
task_id: P3-V3-MEF-ALIGN-01
last_completed_task: <0-9>
head: <40 lowercase hex>
failing_command: <exact argv>
failure: <concise diagnosis>
scientific_evidence_collected: false
claims_status: blocked
recommended_next_action: <specific corrective action>
```
