# P3 C3 Two-Stage Prospective Paired Slice Design

Date: 2026-08-28
Status: `TWO_STAGE_PROSPECTIVE_PAIRED_SLICE_DESIGN_READY`
Task: `P3_C3_TWO_STAGE_PROSPECTIVE_PAIRED_SLICE_DESIGN`
Model / reasoning: `gpt-5.6-sol` / high
Mode: scientific design only; no controller, no experiment, no implementation plan
Verification status: `ANALYZED`
Reproducibility: `NOT_APPLICABLE`

This document is the unique two-stage prospective design that replaces
official progress on
`p3-c3-prospective-multiproject-paired-slice-v1`. It inherits, and does
not rewrite:

- `CONTRACT_AUTHORITY_REQUIRED_BEFORE_SLICE_B`
- `TWO_STAGE_PROSPECTIVE_SLICE_REQUIRED`

C3 remains `blocked`. No successor paired evidence exists. This file is
not an observation, not a Stage I run, and not a Stage II authorization.

Confirmed direction: full fixed Stage I over ordinals 9–22, then full
disclosure, then a new Stage II version. Stage I does not write "no
contract authority yet" as subject ineligibility and does not consume
Stage II successor qualification.

Unique next task after this file is accepted:

`P3_C3_TWO_STAGE_PROSPECTIVE_PAIRED_SLICE_DESIGN_REVIEW`

## 1. Identities

These identities are distinct. They must not be reused as aliases.

| Role | Identity |
|---|---|
| Closed paired slice (old Slice B) | `p3-c3-prospective-multiproject-paired-slice-v1` |
| Old official namespace | `data/p3_v3/phase3/prospective-multiproject-paired-slice-v1` |
| Old staging namespace | `data/p3_v3/phase3/prospective-multiproject-paired-slice-v1.staging` |
| Stage I slice | `p3-c3-prospective-multiproject-applicability-stage1-v2` |
| Stage I official namespace | `data/p3_v3/phase3/prospective-multiproject-applicability-stage1-v2/` |
| Stage I staging namespace | `data/p3_v3/phase3/prospective-multiproject-applicability-stage1-v2.staging/` |
| Stage I success terminal | `STAGE1_APPLICABILITY_CENSUS_COMPLETE` |
| Stage I terminal schema_version | `p3-c3-prospective-multiproject-applicability-stage1-v2-terminal-v1` |
| Stage II slice | `p3-c3-prospective-multiproject-paired-stage2-v2` |
| Stage II official namespace | `data/p3_v3/phase3/prospective-multiproject-paired-stage2-v2/` |
| Stage II staging namespace | `data/p3_v3/phase3/prospective-multiproject-paired-stage2-v2.staging/` |
| Stage II authority-gap record | `STAGE2_AUTHORITY_UNAVAILABLE` |
| Stage II scientific success | `PAIRED_EVIDENCE_COMPLETE` |
| Stage II cohort found | `STAGE2_TWO_NEW_PROJECTS_FOUND` |
| Stage II cohort exhausted | `STAGE2_CANDIDATE_UNIVERSE_EXHAUSTED` |
| Stage II terminal schema_version | `p3-c3-prospective-multiproject-paired-stage2-v2-terminal-v1` |

This design task must not create any of those directories. Later
implementation binds this file's SHA-256 and the implementing commit.
Those hashes are not invented here.

Authorization flags are separate and remain unset by this task:

| Flag | Scope | Required value in this task |
|---|---|---|
| `OFFICIAL_RUN_AUTHORIZED` | old v1 Slice B only | unset or `False`; setting `True` is forbidden |
| future Stage I official flag | Stage I only | unset; Stage I complete does not set Stage II |
| future Stage II official flag | Stage II only | unset; requires a later separate authorization |

## 2. Disposition of old Slice B

1. Old Slice B has never run officially. Its official and staging
   namespaces do not exist.
2. It is closed because nonempty source-authorized contracts have
   maximum reachable count 0 under
   `freeze_production_contracts()` for ordinals 9–22.
3. Its design, controller, processor, tests, and historical audits are
   retained. This document does not delete or rewrite them.
4. Later work must not set `OFFICIAL_RUN_AUTHORIZED=True` for old
   Slice B. Filling `freeze_production_contracts()` on that version,
   or running `process_production_subject()` /
   `run_production_subject_pipeline()` as an official v1 subject, is
   forbidden.
5. The two-stage design has new slice and version identities, listed
   in §1.
6. The two-stage design is not a resume, retry, or parameter revision
   of old Slice B. It does not inherit v1 subject terminals as Stage I
   outcomes.

Old v1 funnel codes remain historical vocabulary. Stage I must not
write them. Stage II may reuse `PAIRED_EVIDENCE_COMPLETE` as the paired
success code because that is the unchanged research target. Stage II
must not reuse `SITE_ELIGIBLE_NO_AUTHORIZED_CONTRACT`,
`PAIR_CONSTRUCTION_UNAVAILABLE`, or `MULTIPROJECT_COHORT_EXHAUSTED`.

## 3. Stage I scientific question

Stage I asks exactly one question:

Under the frozen applicability authority, frozen source identities,
and frozen ordinal 9–22 universe, which of each subject's ten slots
close as `SITE_FROZEN`, and which close as
`APPLICABILITY_CLOSED_NOT_APPLICABLE`?

Stage I does not answer:

- whether a source-authorized contract exists;
- whether a semantic/syntactic pair can be constructed;
- whether a mutant is `KILL` or `SURVIVE`;
- construct distinctness;
- testing value;
- whether C3 may be upgraded.

A `SITE_FROZEN` slot is an applicability observation. It is not Stage
II enrollment and not paired-evidence qualification.

## 4. Stage I universe and stop rule

Hard values:

| Field | Frozen value |
|---|---|
| successor ordinals | 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22 |
| subject count | 14 |
| processing order | that ordinal sequence only |
| slots per subject | 10 |
| total closures | 140 |
| early stop | forbidden |
| user-supplied order, max-attempts, or map | forbidden |
| ordinal 8 | excluded |

Stage I must not stop early because a slot is `SITE_FROZEN`, because a
repository is new, because a count is large or small, or because a
later Stage II candidate looks likely. It must not skip, replace, or
reorder subjects.

Stage I scientific success requires 14/14 subjects and 140/140
closures, then the unique success terminal
`STAGE1_APPLICABILITY_CENSUS_COMPLETE`.

Stage I failure:

- preflight or execution failure must not write the success terminal;
- unprocessed subjects must not be written as
  `APPLICABILITY_CLOSED_NOT_APPLICABLE`;
- automatic retry or resume is forbidden;
- already atomically written partial closures remain;
- any later recovery requires a new authorization and a version
  judgment outside this document.

## 5. Stage I allowed and forbidden seams

Stage I may call only:

- `freeze_subject_identity` / `bind_production_project_identity` /
  `load_frozen_successors` / `load_frozen_bridge_identity_records`;
- `recover_production_source` for identity reuse of the already
  recovered archive and extracted tree;
- `load_applicability_authority`;
- `canonicalize_production_sites` (the existing `_sites` wrapper);
- `close_slot_with_authority` / `close_slot`;
- existing exclusive canonical writers and validators
  (`write_canonical_json`, `canonical_sha256`, `file_sha256`).

The existing loop inside `close_production_applicability` may be reused
as the ten-slot closer only if the Stage I controller stops after the
ten `p3-slot-closure-v1` objects are validated and written. Reusing
that loop is not permission to call the nine-stage production
pipeline.

Stage I must not call:

- `process_production_subject` or `run_production_subject_pipeline`;
- `freeze_production_contracts` or any contract `generate()`;
- `construct_production_pairs` or any mutant constructor;
- `execute_production_pairs` or any ordinal-8 runner;
- `measure_production_overlap`;
- subject build, test, or oracle execution;
- old v1 official or staging writers.

Stage I may open the current ordinal's Public Behavior Frame only
through the existing closer, only after a later Stage I official
authorization, and only for that ordinal. This design task does not
open any frame or site.

## 6. Stage I outputs

Reuse `p3-slot-closure-v1`. Do not invent a second slot-closure
schema. Each subject has exactly ten closures, written in the frozen
inventory order for that `controlled_subject_id`:

`semantic_contract_family` in
`("INV", "MONO", "CONV", "DYN", "CMP")`, then `slot_ordinal` in
`(0, 1)`.

Each closure remains the existing exact object:

```text
schema_version = "p3-slot-closure-v1"
slot_id
controlled_subject_id
site_id          # SHA-256 string if SITE_FROZEN, else null
state            # SITE_FROZEN | APPLICABILITY_CLOSED_NOT_APPLICABLE
path             # APPLICABLE | APPLICABILITY_CLOSED_NOT_APPLICABLE
artifact_sha256  # canonical_sha256 of the other fields
```

Proposed official layout, not created by this task:

```text
data/p3_v3/phase3/prospective-multiproject-applicability-stage1-v2/
  cohort-terminal.json
  subjects/
    <ordinal-two-digit>-<controlled_subject_id>/
      <slot_id>.json
```

The unique scientific success object is `cohort-terminal.json`.
Per-subject paired `subject-record.json` objects from old v1 are not
used.

### 6.1 Stage I cohort terminal

`schema_version` is
`p3-c3-prospective-multiproject-applicability-stage1-v2-terminal-v1`.
This string lives in the later controller and in the written terminal.
No independent schema file or manifest is added.

Exact fields, no extras:

| Field | Type | Rule |
|---|---|---|
| `schema_version` | string | the Stage I terminal schema_version above |
| `slice_id` | string | `p3-c3-prospective-multiproject-applicability-stage1-v2` |
| `design_commit` | SHA-256 hex | implementing commit bound by later Slice A |
| `design_file_sha256` | SHA-256 hex | this design file |
| `applicability_authority_artifact_sha256` | SHA-256 hex | existing authority artifact |
| `slot_inventory_artifact_sha256` | SHA-256 hex | existing inventory artifact |
| `project_cluster_authority_artifact_sha256` | SHA-256 hex | existing project-cluster authority; identity binding only |
| `controller_source_sha256` | SHA-256 hex | Stage I controller source |
| `terminal_status` | string | only `STAGE1_APPLICABILITY_CENSUS_COMPLETE` |
| `subjects` | list length 14 | ordinal order 9–22 |
| `artifact_sha256` | SHA-256 hex | `canonical_sha256` of the other fields |

Each `subjects[i]` exact object:

| Field | Type | Rule |
|---|---|---|
| `successor_ordinal` | int | 9–22 in order |
| `neutral_snapshot_id` | SHA-256 hex | frozen successor identity |
| `controlled_subject_source_id` | SHA-256 hex | frozen successor identity |
| `controlled_subject_id` | SHA-256 hex | frozen successor identity |
| `project_cluster_key` | string | existing binder; not a Stage I stop key |
| `closure_artifact_sha256s` | list length 10 | inventory order; each is the matching closure `artifact_sha256` |
| `site_frozen_count` | int | 0–10; must equal rebuilt `SITE_FROZEN` count |
| `not_applicable_count` | int | 0–10; must equal rebuilt `APPLICABILITY_CLOSED_NOT_APPLICABLE` count |

Forbidden terminal fields: timestamps, hostnames, randoms, contract
ids, pair counts, kill/survival, overlap, eligibility flags,
`PAIRED_EVIDENCE_COMPLETE`, `SITE_ELIGIBLE_NO_AUTHORIZED_CONTRACT`,
`PAIR_CONSTRUCTION_UNAVAILABLE`, `MULTIPROJECT_COHORT_EXHAUSTED`,
ordinal-8 retained paired observation.

### 6.2 Consistency rules

A written Stage I success terminal is valid only if all of the
following hold:

1. `subjects` has length 14 and ordinals `9..22` in that order.
2. Each row identity matches `load_frozen_successors()` at that
   ordinal.
3. Each row has exactly ten closure hashes, and those files exist,
   validate as `p3-slot-closure-v1`, and belong to that
   `controlled_subject_id`.
4. Closure order matches the inventory order in §6.
5. `site_frozen_count + not_applicable_count = 10`.
6. Those counts equal the rebuilt closure states.
7. The 140 closures are the complete Stage I observation set.
8. `artifact_sha256` equals `canonical_sha256` of the body.
9. Old v1 official and staging namespaces still do not exist.
10. Ordinal 8 is absent from `subjects`.

If any rule fails, the object is not a scientific success terminal.

## 7. Stage I claim and evidence ceiling

After a valid Stage I terminal, reports may write:

- observed: 14/14 subjects and 140/140 slots received applicability
  closure;
- observed: `SITE_FROZEN` and `APPLICABILITY_CLOSED_NOT_APPLICABLE`
  counts, including counts by frozen family and inventory mechanism
  reconstructed from closures plus inventory;
- qualified: the applicable sites found by the frozen authority on
  this 14-subject cohort.

Reports must not write:

- a subject is suitable or unsuitable for semantic mutation;
- a subject without a contract is ineligible;
- a target semantic construct is absent;
- C3 is upgraded;
- paired evidence increased;
- `n_projects` increased.

After Stage I:

- C3 remains `blocked`;
- `n_projects` remains 1 (ordinal 8 only);
- the claim ledger is not automatically modified;
- no subject has been consumed as a Stage II successor.

Reconstructed family/mechanism counts are census observations. They
are not prevalence claims and not contract authority.

## 8. Stage II start conditions

Stage II may be designed in detail for official execution, and later
authorized, only when all of the following hold:

1. A valid Stage I official terminal exists.
2. That terminal reconstructs 14/14 subjects and 140/140 closures.
3. The Stage I observation set has been disclosed as prior
   information.
4. The Stage II version explicitly binds the Stage I
   `cohort-terminal.json` artifact SHA-256.
5. No Stage II kill, survival, or overlap outcome has been viewed.
6. Contract, mutant, input, and runner authority for the opened
   Stage II candidate are frozen before that candidate's official
   paired execution.

Stage II is not a Stage I retry. It consumes the disclosed Stage I
census as a public frozen input. Stage I completion must not start
Stage II.

Stage II is a disclosed adaptive follow-up. It is not the original
confirmatory Package A path and not old Slice B.

## 9. Stage II candidate universe

Candidates are derived mechanically from the Stage I terminal and the
140 closures. No human map is permitted.

Derivation:

1. Read the Stage I success terminal.
2. Rebuild every closure from `closure_artifact_sha256s`.
3. Keep a subject if and only if `site_frozen_count >= 1` and the
   rebuilt closures confirm at least one `SITE_FROZEN` state.
4. Drop every subject whose ten closures are
   `APPLICABILITY_CLOSED_NOT_APPLICABLE`.
5. Keep the remaining subjects in the original ordinal 9–22 relative
   order.
6. Exclude ordinal 8.
7. Add no extra-table subject.

The candidate list must not be reordered by repository, language,
expected implementation ease, site count, or preference.

If Stage I observes zero `SITE_FROZEN` slots, the Stage II candidate
universe is empty. An authorized Stage II would then write
`STAGE2_CANDIDATE_UNIVERSE_EXHAUSTED` with zero paired executions.
Stage I itself must not write that terminal and must not interpret
zero `SITE_FROZEN` as "no semantic constructs".

## 10. Stage II authority freeze

For each Stage II candidate, before any paired execution, freeze in
this order:

1. selected canonical site identity from the already disclosed Stage I
   closure (`site_id` on each `SITE_FROZEN` slot used);
2. source-interface evidence that the chosen site can consume the
   intended domain;
3. source-authorized contract, using the seven conditions in
   `docs/superpowers/specs/2026-08-28-p3-c3-prospective-successor-contract-authority-design.md`
   §2;
4. exactly five `E_CONTRACT` inputs;
5. semantic mutant;
6. first-order syntactic baseline;
7. invocation adapter;
8. original oracle or metamorphic relation;
9. controlled runtime and build descriptor;
10. exact-overlap measurement boundary.

A family-to-generator table, a 14-row site table, and ordinal-8 NumPy
invocation transfer remain forbidden as the source of items 2, 3, 7,
and 8. Those items may be stated only after Stage I disclosure and
only as a new-version authority.

If the complete ten-item authority cannot be established for at least
one pair on that candidate:

- record `STAGE2_AUTHORITY_UNAVAILABLE`;
- do not run that candidate;
- do not call the record a mutation failure, site failure, or
  scientific ineligibility;
- continue to the next Stage II candidate in the frozen ordinal
  order.

That continue rule is preregistered. It is the only Stage II action
after `STAGE2_AUTHORITY_UNAVAILABLE`. The candidate is consumed for
this Stage II version and cannot be retried inside it.

If official paired execution starts after a complete freeze and then
fails as identity or infrastructure, the slice stops. That failure
must not be rewritten as `STAGE2_AUTHORITY_UNAVAILABLE` to skip
ahead.

## 11. Stage II project stopping rule

Research target, unchanged:

- ordinal 8 NumPy remains the first already-observed project;
- Stage II walks the frozen candidate ordinal order;
- stop when two `PAIRED_EVIDENCE_COMPLETE` subjects have distinct
  `project_cluster_key` values, both different from the ordinal-8
  project key;
- together with ordinal 8 this is a 3-project pilot;
- or stop when every Stage II candidate has been processed.

`project_cluster_key` comes from the existing project-cluster
authority. A second project authority is forbidden. Several subjects
from one project cannot count as several projects.

Forbidden:

- choosing the next subject from kill, survival, or overlap;
- continuing after the two-new-project stop;
- treating the 3-project pilot as a C3-sufficient sample;
- rerunning or reselecting ordinal 8.

Stage II cohort success terminals:

- `STAGE2_TWO_NEW_PROJECTS_FOUND`
- `STAGE2_CANDIDATE_UNIVERSE_EXHAUSTED`

Those terminals are Stage II objects. They are not Stage I terminals
and not old v1 `MULTIPROJECT_*` terminals.

C3 remains `blocked` after either Stage II cohort terminal.
`BOOTSTRAP_IMPLEMENTATION_AUTHORITY_REQUIRED` remains inherited from
the approved multiproject design. This document does not bind a
bootstrap algorithm.

## 12. Stage II pair budget and reduction

Keep the approved multiproject bounds:

- take every source-authorized semantic–syntactic pair on a subject,
  at most 4 pairs;
- `PAIRED_EVIDENCE_COMPLETE` requires at least 1 pair;
- each pair uses original, semantic, and syntactic variants on the
  same 5 frozen inputs;
- input cells are repeated measures, not independent samples;
- the pair is the within-subject primary reduction;
- subjects inside a project are equally weighted;
- the project is the clustered-uncertainty unit;
- ordinal 8 keeps its existing 4 pairs and is not rerun.

`D_subject` remains semantic pair-level kill proportion minus
syntactic pair-level kill proportion. Those numbers are Stage II
paired observations. They are not Stage I census quantities and are
not used to choose the next candidate.

## 13. Error classes and no-retry

Scientific observations:

- Stage I closure state (`SITE_FROZEN` or
  `APPLICABILITY_CLOSED_NOT_APPLICABLE`);
- Stage II paired `KILL` / `SURVIVE`;
- Stage II exact overlap.

Authority or implementation failures:

- source identity conflict;
- incomplete contract authority;
- mutant construction unavailable;
- controlled runner unavailable;
- infrastructure failure.

Authority absence must not be written as scientific ineligibility.
Stage I must not write `SITE_ELIGIBLE_NO_AUTHORIZED_CONTRACT`.
Stage II writes `STAGE2_AUTHORITY_UNAVAILABLE` when the ten-item
freeze cannot be completed, and writes
`INFRASTRUCTURE_FAILURE` or `IDENTITY_CONFLICT` when official
execution fails after a completed freeze.

Each stage has exactly one official authorization. The two
authorizations are separate. Completing Stage I does not authorize
Stage II. Completing a Stage II authority freeze for one candidate
does not authorize the next candidate's official run until the Stage
II controller, under its own official flag, reaches that candidate.

`NO_SCIENTIFIC_RETRY` holds inside each stage. A new version after a
stopped failure is not defined here.

## 14. Future implementation slices

These names order later work. They are not an implementation plan.
Completing one slice must not start the next.

| Slice | Content | Authorization |
|---|---|---|
| A | Stage I controller and focused validation | separate |
| B | Stage I preflight and one official applicability census | separate |
| Human scientific review | disclose Stage I observation; freeze the Stage II candidate universe from the Stage I terminal | separate |
| C | per-candidate contract, pair, and runner authority construction | separate |
| D | Stage II controller and focused validation | separate |
| E | Stage II preflight and one official paired run | separate |

Slice A and Slice D must not open official namespaces. Slice B must
not call contract, pair, or runner seams. Slice C must not run paired
execution. Slice E must not start unless §8 holds.

Old Slice B is not one of these slices.

## 15. Anti-drift rules

Forbidden:

- a new contract registry for Stage I;
- pair or runner implementation inside Stage I;
- back-filling contracts onto old Slice B;
- a 14-row manual site or repository contract table;
- a new claim ledger;
- a second project-cluster authority;
- hash, gate, or manifest files that do not bind Stage I closures or
  Stage II official objects;
- a full-suite test obligation as a scientific prerequisite;
- opening successor sites or sources during this design task;
- counting design, implementation, or test pass as scientific
  progress.

The next scientific progress is a Stage I observation: 140 closures
and one Stage I success terminal. Another parallel protocol without
that observation would be drift.

## 16. Falsifiable acceptance

Future Stage I implementation must prove:

1. exactly 14 subjects and 140 closures;
2. no call to contract, pair, or runner seams;
3. no early stop;
4. malformed identity fails closed;
5. partial failure does not write
   `STAGE1_APPLICABILITY_CENSUS_COMPLETE`;
6. the Stage I terminal rebuilds every closure identity;
7. old Slice B official namespace still does not exist;
8. ordinal 8 is not a Stage I subject.

Future Stage II implementation must prove:

1. the candidate universe rebuilds from the Stage I artifact alone;
2. candidate order remains ordinal order;
3. `STAGE2_AUTHORITY_UNAVAILABLE` produces no paired observation;
4. the slice stops when two distinct non-NumPy projects are complete;
5. cell, pair, subject, and project reductions follow §12;
6. ordinal 8 is a frozen historical input and is not rerun.

This design task does not run those proofs.

## 17. Claim ceiling

| Item | Value |
|---|---|
| `C3_SEMANTIC_CONSTRUCT_DISTINCTNESS` | `blocked` |
| upgrade condition | `RQ2 paired evidence and uncertainty accounting complete` |
| claim ledger | unmodified |
| ledger SHA-256 | `bf4979662697b2d0565bb70eec88b22673e84bee93b61234555342efb4082a68` |
| Stage I effect on C3 | none |
| Stage I effect on `n_projects` | none; remains 1 |
| Stage II 3-project pilot | does not automatically upgrade C3 |
| successor paired evidence now | none |

## 18. Exclusions kept by this task

This task did not:

- modify production code or tests;
- create Stage I or Stage II output directories;
- run an applicability predicate;
- read a real successor site path, symbol, span, or source file;
- write a contract, mutant, or runner;
- write an implementation plan;
- modify the claim ledger;
- create an authorization file;
- set `OFFICIAL_RUN_AUTHORIZED`;
- run pytest, a build, a compiler, a subject, or an experiment.

Ordinal-8 handoff and overlap files were consulted only for field
structure and the already frozen historical identity of ordinal 8.
Their kill, survival, and difference numbers are not Stage I or
Stage II selection rules.

## 19. Design self-review

- No open design placeholders remain.
- Stage I and Stage II identities are distinct.
- Stage I does not produce paired eligibility.
- Stage I does not consume Stage II successors.
- Stage II is a disclosed adaptive follow-up.
- Authority failure is not a scientific ineligibility code.
- No repository or site special case is used as authority.
- Old evidence is unmodified.
- C3 remains blocked.
- `git diff --check` is required on the commit that adds this file.

## 20. Unique next task

`P3_C3_TWO_STAGE_PROSPECTIVE_PAIRED_SLICE_DESIGN_REVIEW`

That task reviews this design. It must not implement Slice A, must
not start Stage I, and must not authorize old Slice B.
