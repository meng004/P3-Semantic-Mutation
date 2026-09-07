# P3 Phase 2 Master Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement the *sub-plan named by the
> current task*, not this file. This master plan is the package index and
> gate authority. It does not contain implementation code.
>
> This file is not a scientific-run authorization and not a
> production-preparation authorization.

**Goal:** Freeze a six-file Phase 2 plan package that can later, after
independent Sol High PASS and Task P1, authorize Protocol V5 design,
capability implementation, final V5 emission, and two separately
authorized execution windows.

**Architecture:** One master index plus five subsystem plans. Protocol
authority is two-stage (V-DESIGN then V-FINAL). Capability work is
split across preflight/pilot, profiling, and slot/contract/close.
Lane X is split into production-preparation (X1–X3) and scientific
profiling (X4–X12).

**Tech Stack:** Python 3.12 (`/opt/anaconda3/bin/python`, pytest 8.4.2);
stdlib-only scientific modules under `src/p3_v3`; CLI
`scripts/p3_v3/evidence.py`.

## Global Constraints

- Freeze anchor until P1: `HEAD = origin/main = 8cd3e2da8ab31cc313a17fed01dc63ea84d59690`.
- Protocol V4 file SHA-256
  `240d8270d41802c9d5b86f30564eadd1a86fd9ed09de2c7e947d17c1a4d78519`.
- Protocol V4 artifact SHA-256
  `c4606414b3bfd3a9df10a19959dedb3e08add25b220179ef891be24bda5eb882`.
- Scientific plan SHA-256
  `fea00496801c31ba074aa74742f5e6a77019ffc2e344642122a15462d7443830`.
- Evidence design SHA-256
  `7e614e96aac833786d1b29580f8fae7d3f03c6567d7ca94f3e3c017addad2fa9`
  as recorded in live Protocol V4. V-DESIGN re-reads the file and binds
  the observed predecessor hash.
- Funnel: `ADAPTER_UNSUPPORTED=3`, `ADAPTER_EXECUTION_FAILED=9`,
  `EXECUTABLE=23`. Do not relabel to 3/5/27.
- Frozen subjects 35; executable 23; non-executable 12; selected
  profiling rows 460; empty workload receipts 12; `E_COMMON` rows 1050;
  declared slots 350 = 35 × 5 × 2; slot closures today 0.
- Claims stay `blocked`.
- No P12 reveal, Package C, buggy tree, defect patch, reference MR, or
  experimental outcome may be read.
- No Cursor VM, no network, no fetch/pull/push/PR/merge unless the user
  later authorizes a specific command.
- Local shells use `rtk`. Do not invoke bare `git` / `ls` / `rg` /
  `cat` / `cd`. Existence checks use `rtk run -c 'test ! -f path'`.
- Scientific environment and later proposers stay Grok 4.5 High.
  Grok 4.6 High may revise plans and later perform non-scientific
  mechanical implementation only. Independent review is GPT-5.6 Sol
  High, high reasoning.
- Grok 4.6 must not be written into any scientific environment record.

---

## Repair Round 2 changelog

R1 packed protocol, preflight, pilot, materialization, runner, trace,
slots, contracts, package, and close into one 2734-line file. R2 splits
that file into a six-file package, makes Protocol V5 two-stage, adds
source-materialization authority, separates 460 denominator rows from
`N_bound_jobs`, fail-closes native tracing, adds the attempt→receipt
reducer, uses independent pilot schemas, and splits the two user
authorizations.

---

## 1. Plan package

| Path | Responsibility |
|---|---|
| `docs/superpowers/plans/2026-08-15-p3-phase2-preflight-profiling-frame-close.md` | Master index, gates, ETA, stop conditions |
| `docs/superpowers/plans/2026-08-15-p3-phase2-v5-authority.md` | V-DESIGN and V-FINAL authority |
| `docs/superpowers/plans/2026-08-15-p3-phase2-preflight-pilot.md` | 35-subject materialization, preflight, PILOT_ONLY |
| `docs/superpowers/plans/2026-08-15-p3-phase2-profiling-capability.md` | 460-row inventory, runner, tracer, reducer, rebind, cohorts |
| `docs/superpowers/plans/2026-08-15-p3-phase2-slot-contract-close.md` | 350 slots, predicates, ContractAuthority, Package A, close |
| `docs/superpowers/plans/2026-08-15-p3-phase2-authorized-execution-runbook.md` | X1–X12, two user authorizations |

Do not implement from this master file. Each subsystem task names its
sub-plan.

## 2. Fixed scientific inputs

| Artifact | Identity |
|---|---|
| Review/planning HEAD | `8cd3e2da8ab31cc313a17fed01dc63ea84d59690` |
| Protocol V4 file SHA-256 | `240d8270d41802c9d5b86f30564eadd1a86fd9ed09de2c7e947d17c1a4d78519` |
| Protocol V4 artifact SHA-256 | `c4606414b3bfd3a9df10a19959dedb3e08add25b220179ef891be24bda5eb882` |
| Pass-1 baseline manifest | `b0be90ded75a4242bf883698d2b8c3f0c55d70b1b0928d7068bc1a3797e4eb11` |
| Raw `subject-frames.json` | `588ff83530c16ef2647b523c157bf5585320dae17754918364db8bd96c5e304b` |
| Receipts file SHA-256 | `8eeccfe4d1aebb09e6ee9ad2fadb82ac5b8697c40f602592faa6b3878692a440` |
| Bridge artifact | `99f36f87499b7e332beca9677e53671b144f1b37ed2250e0c74b8f757498d661` |
| Frozen subjects | 35 |
| Executable subjects | 23 |
| Non-executable subjects | 12 |
| Common-input rows | 1050 |
| Selected profiling rows | 460 |
| Empty workload receipts | 12 |
| Declared slots | 350 |
| Claims | `blocked` |

Observed selected-row entrypoint prefixes on the frozen 460 rows
(2026-08-15, keys only): `header=150`, `target=55`, `example=96`,
`benchmark=61`, `ctest=67`, `project_test=22`, Python-like=8, `cli=1`.
Those counts are inventory facts, not a job-count promise.

`C_CONSTRUCT` and `C_CRITERION` keep different denominators.

## 3. Lanes and required order

```text
PLAN_REVIEW_PASS
  → P1 freeze entire six-file plan package
  → P0 Phase 1 closure docs
  → V-DESIGN packet commit → STOP → Sol High → reviewer verdict commit
  → capability implementation (preflight/pilot, profiling, slot/close)
  → V-FINAL packet commit → STOP → Sol High → reviewer verdict commit
  → implementation review packet commit → STOP → Sol High → verdict commit
  → user production-preparation authorization
  → X1–X3
  → user scientific profiling authorization
  → X4–X12
  → Phase 2 final review packet commit → STOP → Sol High → verdict commit
```

P1 is the first repository commit after plan PASS. P0 must not precede
P1.

P1 commits exactly:

- the six plan files
- `docs/review_20260815/phase2_plan_package_manifest.json`
- `docs/review_20260815/phase2_plan_freeze_receipt.md`

The manifest binds every plan path, every raw SHA-256, the canonical
sorted file list, the manifest self-hash, reviewer, plan verdict,
predecessor HEAD `8cd3e2da8ab31cc313a17fed01dc63ea84d59690`, and
`claims=blocked`.

Any later textual edit of a plan file invalidates the previous plan
verdict. The package must be re-submitted for Sol High review. P1 must
not say that a PASS allows silent plan edits.

Implementation review range is

`8cd3e2da8ab31cc313a17fed01dc63ea84d59690..IMPLEMENTATION_HEAD`

or

`P1_COMMIT^..IMPLEMENTATION_HEAD`

Do not write `P1_COMMIT..HEAD` and claim that range includes P1.

## 4. Review PASS transition

Every independent review uses this sequence:

1. Builder finishes artifacts.
2. Builder writes packet and task report.
3. Builder commits the packet.
4. Stop and emit the matching `*_REVIEW_CANDIDATE`.
5. GPT-5.6 Sol High reviews the fixed commit/range read-only.
6. Reviewer emits PASS or BLOCK text.
7. Controller archives that exact reviewer text into a verdict
   artifact. The executor must not write PASS, must not invent a
   reviewer name, and must not edit the conclusion.
8. Controller commits the verdict in a separate commit.
9. Downstream gates read the verdict artifact and its hash.

Verdict required fields: reviewer, model, reasoning setting, reviewed
commit, review range, packet SHA-256, plan-package SHA-256, relevant
protocol SHA-256, suite command/count/exit when a suite ran, PASS or
BLOCK, artifact self-hash.

## 5. Two user authorizations

### 5.1 Production-preparation authorization

Allows X1 real preflight, X2 actual `PILOT_ONLY`, and X3 inventory
freeze. Forbids confirmatory scientific intents.

Requires: plan package PASS and P1 freeze; V-DESIGN PASS; capability
implementation PASS; V-FINAL PASS; implementation review PASS; claims
blocked; Package C absent; explicit user sentence authorizing
production preparation.

### 5.2 Scientific profiling authorization

Allows X4 to write the first confirmatory `create_intent` for
`N_bound_jobs` only, then X5–X12.

Requires all of:

1. revised plan PASS
2. V-DESIGN PASS
3. V-FINAL PASS
4. clean-worktree suite PASS
5. implementation independent review PASS
6. X1 preflight PASS
7. X2 pilot PASS
8. X3 inventory frozen
9. `total_rows=460`
10. `N_bound_jobs + N_preclosed_rows = 460`
11. 12 empty workload receipts retained
12. claims blocked
13. Package C absent
14. explicit user sentence authorizing scientific profiling

## 6. Sub-plan acceptance summaries

### 6.1 V5 authority

V-DESIGN is a prospective scientific controller amendment, not an
engineering schema completion. It names predecessor hashes, the
35/460/3-9-23/1050 preservation requirements, the execution-row
closure estimand, the family→mechanism matrix and its reason, and
every new schema. V-FINAL emits live `p3-protocol-v2` only after
concrete manifests exist and binds those manifest hashes. Old
scientific hashes are predecessor hashes only. No X1 without V-FINAL
PASS.

### 6.2 Preflight / pilot

A `SourceMaterializationManifest` covers exactly 35 blinded
fixed-source archives. Preflight runs 23 smokes and retains 12 frozen
failures. Package C is rejected by class, tree hash, and identity
fields. Pilot uses independent `p3-pilot-intent-v1` schemas and an
independent ledger.

### 6.3 Profiling capability

```text
N_total_rows = 460
N_bound_jobs = count(status == EXECUTION_PLAN_BOUND)
N_preclosed_rows = 460 - N_bound_jobs
```

Only `N_bound_jobs` receive scientific intents. Preclosed rows become
outcome-blind `ADAPTER_UNCERTAIN` closures and stay in the 460-row
denominator. The only defined tracer is CPython `sys.setprofile` for
Python recipes. Native CMake/Meson/Autotools strategies are
`TRACER_UNAVAILABLE` and fail closed. The attempt→receipt reducer
covers every selected `behavior_id` exactly once.

### 6.4 Slot / contract / close

350 slots are pre-bound. Predicates are family-specific static rules,
never always-true. `build_contract_authority` extracts contracts from
mounted public documentation. If extraction cannot emit a real
contract for an applicable slot, the function returns
`PHASE2_CONTRACT_AUTHORITY_BLOCKED` and X8 stops. Dummy contracts are
forbidden. In-repo materials do not currently contain the 35 blinded
archives, so production contract emission is blocked until
materialization and extraction succeed.

### 6.5 Authorized execution runbook

X1–X3 after production-preparation authorization. X4–X12 after
scientific profiling authorization. Each node keeps input hashes,
counts, exit, checkpoint, resume, and no-duplicate-start rules.

## 7. Lane X node dependence

```text
X1 preflight
  → X2 PILOT_ONLY
  → X3 freeze inventory (460 rows, N_bound, N_preclosed, 12 empty)
  → [scientific authorization]
  → X4 execute N_bound_jobs only
  → X5 ledger validation
  → X6 build_profiling_receipt_from_attempts
  → X7 35-subject rebind
  → X8 cohorts
  → X9 350 slot/contract close
  → X10 Package A
  → X11 shuffle
  → X12 close + independent final review
```

X4 must not hard-code expected jobs = 460.

## 8. Claims / evidence gate

| Object | Location | Rule |
|---|---|---|
| score-task | created in P0 | no claim upgrade |
| experiment ledger | created in P0 | empty until authorized runs |
| claim ledger | created in P0 | C1–C8 and RQ1–RQ4 stay `blocked` |
| Phase 2 evidence | after X12 | profiling success is not a paper result |

## 9. ETA

Implementation (P1 through implementation-review verdict), excluding
Lane X: 10–16 working days.

Authorized execution: X1 15–90 min; X2 30–180 min; X3 15–60 min; X4
hours to days for `N_bound_jobs` only; X5–X12 1–8 hours plus Sol High
latency. Do not treat any single profiling number as an ETA.

## 10. Stop conditions

Emit `PHASE2_PLAN_BLOCKED` or later `PHASE2_IMPLEMENTATION_BLOCKED` if:

1. HEAD is not the authorized anchor.
2. A step needs P12 reveal, Package C, patches, MRs, or outcomes.
3. Network or Cursor VM is required.
4. V5 would change 35/460/3-9-23/1050.
5. A step would write a confirmatory intent before §5.2 is green.
6. A step would use dummy contracts or an undefined tracer.
7. A plan file is edited after a PASS without a new review.

---

## Controller notes

- This planning round ends at `PHASE2_PLAN_REVIEW_CANDIDATE_R2`.
- No P1, no implementation, no commit, no push in the planning round.
- Do not ask for an execution mode.
