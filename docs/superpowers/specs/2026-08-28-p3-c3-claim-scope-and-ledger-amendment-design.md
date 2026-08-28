# P3 C3 Claim Scope and Ledger Amendment Design

Date: 2026-08-28
Status: `CLAIM_SCOPE_AND_LEDGER_AMENDMENT_DESIGN_READY`
Task: `P3_C3_CLAIM_SCOPE_AND_LEDGER_AMENDMENT_DESIGN`
Model / reasoning: `gpt-5.6-sol` / high
Mode: amendment design only; no ledger edit, no manuscript edit, no experiment, no implementation plan
Verification status: `ANALYZED`
Reproducibility: `NOT_APPLICABLE`

This file is the unique, directly implementable design for shrinking
current-paper C3 / RQ2 scope onto already produced official evidence.
It does not add a scientific observation. It does not start another
subject table, another Stage I or Stage II version, or another
predicate set.

Binding prior decision:

`NEXT_PATH_CLAIM_SCOPE_REDUCTION`

Unique next task after this file is accepted:

`P3_C3_CLAIM_SCOPE_AND_LEDGER_AMENDMENT_IMPLEMENTATION`

That next task edits the living ledger and the living claim-authority
addendum. It must not insert another design, another path choice, or
a schema invention.

## 1. Decision and stopping boundary

The current two-stage prospective route is closed. Stage I set the
Stage II candidate universe to the empty set. The path decision
forbids a second comparison among another subject table, another
predicate set, and claim-scope reduction. This design therefore
implements only claim-scope reduction.

Stopping boundary for the current paper:

1. Keep `C3_SEMANTIC_CONSTRUCT_DISTINCTNESS` at `blocked`.
2. Do not write C3 as `supported`, `qualified`, or `observed`.
3. Do not invent a ledger status token.
4. Remove the original multi-project confirmatory sentence from the
   current paper's main contribution list. The claim object itself
   stays in the ledger as the still-unmet ceiling.
5. Position ordinal 8 as a `single-project paired-evidence pilot`.
6. Position Stage I as a `prospective applicability census under a
   frozen authority`.
7. Keep RQ2. Shrink the current-paper answerable range to:
   single-project paired behavior; exact overlap; and why
   multi-project evidence remains unidentifiable.
8. Do not search for a second or third paired-evidence project on
   the present C3 route.
9. Do not assemble another subject table, another Stage I version,
   another predicate set, or another paired runner for the present C3.
10. Do not start Stage I or Stage II again. The current two-stage
    path stays closed.

This design adds no observation, no controller, no hash gate, and no
parallel validation chain.

## 2. Authoritative evidence

Read-only identities used by this design. Counts are taken from the
named fields only. P12 objects were not opened.

### 2.1 Path decision

| Item | Value |
|---|---|
| Path | `docs/review_20260828/p3_claim_path_reprioritization_after_stage1_empty_candidates.md` |
| File SHA-256 | `dcba9d459eb58bf2984d117b826077998f1069120eb630d004a74ae337836079` |
| Terminal | `NEXT_PATH_CLAIM_SCOPE_REDUCTION` |

### 2.2 Stage I disclosure

| Item | Value |
|---|---|
| Path | `docs/review_20260828/p3_c3_stage1_applicability_census_scientific_disclosure.md` |
| File SHA-256 | `9f0040f460d48310d764c10a75319b8ec4fb4fdb6b691e78b153d284cdaa0552` |

### 2.3 Stage I terminal

| Item | Value |
|---|---|
| Path | `data/p3_v3/phase3/prospective-multiproject-applicability-stage1-v2/cohort-terminal.json` |
| File SHA-256 | `f2e9af90ed31bd118a80808a04e3af66c5abee539f0093c6087c176e2bee51ab` |
| Artifact SHA-256 | `45757bb594d582b380ee7955f0caeab92adfd3c10702c31cf788f896a6595a97` |
| `schema_version` | `p3-c3-prospective-multiproject-applicability-stage1-v2-terminal-v1` |
| `slice_id` | `p3-c3-prospective-multiproject-applicability-stage1-v2` |
| `terminal_status` | `STAGE1_APPLICABILITY_CENSUS_COMPLETE` |
| Subjects | 14; `successor_ordinal` 9 through 22 |
| `site_frozen_count` sum | 0 |
| `not_applicable_count` sum | 140 |
| Stage II candidate universe | 0 (`site_frozen_count >= 1`) |

### 2.4 Claim ledger (amendment target)

| Item | Value |
|---|---|
| Path | `research/evidence/p3_claim_ledger_v1.3.0.yml` |
| File SHA-256 | `bf4979662697b2d0565bb70eec88b22673e84bee93b61234555342efb4082a68` |
| C3 `claim_id` | `C3_SEMANTIC_CONSTRUCT_DISTINCTNESS` |
| C3 `status` | `blocked` |
| C3 `upgrade_condition` | `RQ2 paired evidence and uncertainty accounting complete` |

This YAML ledger has no `evidence_references` field. Evidence binding
uses existing prose in `status_policy.note`. The JSON object validated
by `validate_claim_ledger()` in `src/p3_v3/run_records.py`
(`schema_version: p3-claim-evidence-v1`) is a different artefact. Do
not edit that schema and do not copy its fields into the YAML ledger.

### 2.5 Ordinal-8 paired pilot (field-restricted)

| Item | Value |
|---|---|
| Human handoff | `docs/review_20260828/p3_c3_ordinal8_paired_evidence_rq2_handoff.md` |
| Human handoff file SHA-256 | `9cb105c60e4fd8f351c1f2e84c2691994226efc43e351f37b77b3522b4a5936d` |
| Machine handoff | `data/p3_v3/phase3/ordinal8-paired-evidence-rq2-handoff.json` |
| Machine handoff file SHA-256 | `ad3361f990ff0a611ece2704077780d7f097459560085eb9a996acb8b69e1b3d` |
| Machine handoff artifact SHA-256 | `a846ca2edded55ed48e0e9071a9aa218efc3dbcc9bd302a77ceb53bce9d822c5` |
| Exact overlap | `data/p3_v3/phase3/ordinal8-exact-overlap-v1/exact-overlap.json` |
| Exact overlap file SHA-256 | `d64872250399ac0230d55d2e7fa2883fed783110061188d3fe6597272f571074` |
| Exact overlap artifact SHA-256 | `f4ca00694f4a3a0a63df151bf7cce96a66ae957d0d11d85ca056cb0e6b438071` |
| Project | NumPy; one subject |
| `analysis_units.n_projects` | 1 |
| `analysis_units.n_pairs` | 4 |
| Original baseline | 20/20 cells `SURVIVE` |
| Semantic mutants | 4/4 pair `KILL` |
| Syntactic mutants | 3/4 pair `KILL`, 1/4 pair `SURVIVE` |
| Normalized-patch exact overlap | 0/4 |
| Mutant-tree exact overlap | 0/4 |

The machine handoff still stores overlap as `UNMEASURED` because it
was written before the overlap artefact. Implementation must cite the
exact-overlap artefact for the 0/4 counts. Do not rewrite the handoff
in this amendment.

### 2.6 Layered conclusions that the amendment must preserve

Observed:

1. Ordinal 8 is a single-project paired pilot on NumPy.
2. There are 4 frozen semantic/syntactic pairs.
3. Semantic mutants are 4/4 `KILL`.
4. Syntactic mutants are 3/4 `KILL` and 1/4 `SURVIVE`.
5. Normalized-patch exact overlap is 0/4.
6. Mutant-tree exact overlap is 0/4.
7. Stage I completed 140 official applicability closures on the 14
   subjects at ordinals 9-22.
8. There are 0 `SITE_FROZEN` closures and 140
   `APPLICABILITY_CLOSED_NOT_APPLICABLE` closures.
9. Under the preregistered mechanical rule, the Stage II candidate
   universe is 0.

Qualified:

1. The 0/140 count holds only for the frozen Public Behavior Frame,
   slot inventory, applicability predicates, first-applicable
   selection boundary, and the ordinal 9-22 successor universe.
2. The current two-stage prospective version cannot produce another
   paired project.
3. Stage I lawfully closed the current Stage II path.

Blocked:

1. Multi-project construct-distinctness is not established.
2. Project-clustered uncertainty is unidentifiable.
3. `n_projects` remains 1.
4. C3 remains `blocked`.
5. `RQ2 paired evidence and uncertainty accounting complete` remains
   unmet.

## 3. Claim disposition

Fixed dispositions for implementation. No other status token is
authorized.

| Item | Disposition |
|---|---|
| C3 scientific status | remain `blocked` |
| C3 as `supported` / `qualified` / `observed` | forbidden |
| Original multi-project confirmatory sentence | not a current-paper main contribution |
| Ordinal 8 | `single-project paired-evidence pilot` |
| Stage I | `prospective applicability census under a frozen authority` |
| 0/140 placement | living Methods/Flow, pilot Results, or Limitations text only, and only with the frozen bounds stated |
| 0/140 in Abstract, Contributions, or Conclusion | forbidden as a general negative finding |
| RQ2 | keep; shrink current-paper answerable range only |
| Second or third project on this C3 route | stop seeking |
| Another subject table, predicate set, or paired runner for this C3 | do not create |
| Another path comparison of the same three options | do not perform |

RQ2 current-paper answerable range:

1. Single-project paired kill/survival on the four frozen NumPy pairs.
2. Exact normalized-patch overlap and exact mutant-tree overlap on
   those pairs.
3. Why multi-project construct-distinctness and project-clustered
   uncertainty remain unidentifiable (`n_projects = 1`; Stage II
   candidate universe = 0).

RQ2 is not deleted. Family-coverage differences that were never
measured stay unmeasured. Structural non-overlap remains a
construct-distinctness observation on this pilot, not a testing-value
result.

## 4. Claim ledger amendment

Target file: `research/evidence/p3_claim_ledger_v1.3.0.yml`.

Existing C3 fields: `claim_id`, `rqs`, `text`,
`governing_initial_status`, `status`, `upgrade_condition`.
Existing ledger-wide fields that may carry scope: `status_policy.note`.
Do not add `evidence_references`, a second ledger, or a new status
token.

Existing scripts (`scripts/p3_v3/build_ordinal8_paired_evidence_rq2_handoff.py`,
`scripts/p3_v3/measure_ordinal8_exact_overlap.py`) require the exact
substring `upgrade_condition: "RQ2 paired evidence and uncertainty
accounting complete"` and C3 `status: blocked`. Implementation must
keep both strings byte-identical.

### 4.1 Field table

| field/path | current meaning | proposed value/meaning | evidence binding | reason |
|---|---|---|---|---|
| `ledger_id` | YAML ledger identity | keep | none | not a C3 claim field |
| `status` | `frozen-execution-ceiling` | keep | none | the ceiling remains; this amendment records scope, not a lift |
| `frozen_at` | ledger freeze timestamp | keep | none | historical freeze date is not rewritten |
| `scope_authority` | `research/p3-semantic-mutation-core-claims-rqs-v1.3.0.md` | keep path; that file receives the living addendum in section 5 | core-claims addendum | authority pointer already exists |
| `governing_scientific_plan` | frozen plan path | keep | none | RQ2/C3 rows there stay verbatim |
| `governing_scientific_plan_sha256` | plan hash | keep | none | no plan rewrite |
| `supersedes_execution_authority` | v1.2.0 pointer | keep | none | lineage only |
| `claims[C3].claim_id` | `C3_SEMANTIC_CONSTRUCT_DISTINCTNESS` | keep | none | identity |
| `claims[C3].rqs` | `[RQ2]` | keep | none | RQ2 is not deleted |
| `claims[C3].text` | `Semantic mutants are construct-distinct from the chosen syntactic baseline` | keep the original sentence | none | rewriting the sentence would look like the unmet ceiling had been replaced by a now-meetable pilot claim |
| `claims[C3].governing_initial_status` | `blocked` | keep | none | initial status is historical |
| `claims[C3].status` | `blocked` | keep `blocked` | handoff `claim_ceiling.claim_status=blocked`; overlap `claim_ceiling.claim_status=blocked`; Stage I added no paired project | upgrade condition unmet; `n_projects = 1` |
| `claims[C3].upgrade_condition` | `RQ2 paired evidence and uncertainty accounting complete` | keep the exact string; record in `status_policy.note` that it remains unmet and that meeting it is outside the current paper's main contributions | same as C3 status | existing contract and existing script pins; do not imply the condition is met |
| `status_policy.execution_authority_requires` | `blocked` | keep | none | execution ceiling unchanged for every enumerated claim |
| `status_policy.note` | `The synthetic infrastructure path records no scientific result and cannot upgrade any claim.` | replace with the exact note in section 4.2 | paths and SHA-256 values in section 2, written as prose citations | only existing free-text field that can bind evidence without a new schema |
| `claims[C1]` through `claims[C2]`, `claims[C4]` through `claims[C8]` | other claims | no edit | none | no direct field dependency |

Narrow implementation impact, not expanded by this task: if any test
or pin later compares the whole YAML file to
`bf4979662697b2d0565bb70eec88b22673e84bee93b61234555342efb4082a68`,
that pin must move to the post-amendment digest. Do not add a hash
gate to create that pin.

### 4.2 Exact replacement for `status_policy.note`

Implementation must write this note as a single YAML double-quoted
string, preserving the C3 `upgrade_condition` string elsewhere in the
file:

```text
Current-paper C3/RQ2 scope is a single-project paired-evidence pilot on NumPy (ordinal 8; n_projects = 1; 4 frozen pairs) plus a prospective applicability census under a frozen authority (ordinals 9-22; 0 SITE_FROZEN / 140 APPLICABILITY_CLOSED_NOT_APPLICABLE; Stage II candidate universe = 0). These observations do not satisfy C3 upgrade_condition "RQ2 paired evidence and uncertainty accounting complete". Multi-project construct-distinctness and project-clustered uncertainty remain unidentifiable. C3 remains blocked. The original multi-project confirmatory sentence is outside the current paper's main contributions. Evidence cited in existing prose form: docs/review_20260828/p3_c3_ordinal8_paired_evidence_rq2_handoff.md; data/p3_v3/phase3/ordinal8-paired-evidence-rq2-handoff.json (artifact SHA-256 a846ca2edded55ed48e0e9071a9aa218efc3dbcc9bd302a77ceb53bce9d822c5); data/p3_v3/phase3/ordinal8-exact-overlap-v1/exact-overlap.json (artifact SHA-256 f4ca00694f4a3a0a63df151bf7cce96a66ae957d0d11d85ca056cb0e6b438071); data/p3_v3/phase3/prospective-multiproject-applicability-stage1-v2/cohort-terminal.json (artifact SHA-256 45757bb594d582b380ee7955f0caeab92adfd3c10702c31cf788f896a6595a97); docs/review_20260828/p3_c3_stage1_applicability_census_scientific_disclosure.md; docs/review_20260828/p3_claim_path_reprioritization_after_stage1_empty_candidates.md. Execution authority still requires blocked status for every enumerated claim; this note records scope, not a status change.
```

### 4.3 Adjacent claims

C2, C4, and C5 have no field that reads C3 status or the current
note. Implementation must not edit them. C5 remains a P12 claim and
is outside this amendment. C1 remains the protocol-definition claim
and is not rewritten as a multi-project result.

## 5. Manuscript amendment

No P3 IMRaD manuscript exists at this HEAD. P2 files
(`论文初稿P2_IST.md`, `论文初稿P2_EN.md`, `source/main.tex`) are a
different paper and must not be edited. The historical outline
`research/paper-outline-semantic-mutation-mr-adequacy.md` is already
marked superseded by the v1.2.0 / v1.3.0 claim authority and must
not be revived. The governing plan copies RQ2 and the C3 row
verbatim; those rows stay verbatim.

Living manuscript-adjacent seam:

`research/p3-semantic-mutation-core-claims-rqs-v1.3.0.md`

That file currently copies RQ2 and the claim-ceiling table from the
governing plan. Implementation must keep that verbatim copy and
append one addendum after the existing claim-ceiling table. It must
not create Abstract, Contributions, Methods, Results, Discussion, or
Conclusion files in order to look complete.

### 5.1 Section table

| manuscript section | current claim/risk | required amendment | evidence | prohibited overclaim |
|---|---|---|---|---|
| Abstract | no P3 Abstract exists; no current P3 Abstract asserts a multi-project C3 result | `NO_CHANGE`; do not create an Abstract | none | do not create an Abstract in order to host 0/140 or the NumPy pilot as a general finding |
| Introduction / Contributions | no P3 contributions section exists; the unmet C3 sentence still sits in the living claim-ceiling table as a blocked claim | `NO_CHANGE` to any Introduction file; record in the core-claims addendum that the original multi-project confirmatory sentence is not a current-paper main contribution | path decision; C3 remains `blocked` | do not list multi-project construct-distinctness as a delivered contribution |
| RQ2 definition | living RQ2 question is the frozen difference question; it does not yet state the current-paper answerable range | keep the frozen question; append the current-paper answerable-range paragraph in section 5.2 | ordinal-8 handoff and exact overlap; Stage I terminal | do not delete RQ2; do not rewrite the frozen question into a NumPy-only question |
| Methods | no P3 Methods section exists | `NO_CHANGE`; do not create Methods | none | a later Methods/Flow sentence may report the 140-slot census only with the frozen PBF, inventory, and predicate bounds; this amendment does not write that section |
| Results | no P3 Results section exists; the only official paired counts are the NumPy pilot | `NO_CHANGE` to a Results file; place the core wording in the core-claims addendum | ordinal-8 handoff and exact overlap | do not present 4/4 vs 3/4 or 0/4 overlap as a multi-project comparison |
| Limitations | no P3 Limitations section exists; Stage I disclosure already forbids transporting 0/140 | `NO_CHANGE` to a Limitations file; the addendum must state `n_projects = 1` and unidentifiable project-clustered uncertainty | Stage I disclosure; handoff uncertainty fields | do not write 0/140 as an industrial applicability rate |
| Discussion | no P3 Discussion exists | `NO_CHANGE` | none | do not write that semantic mutants are generally better than, or generally different from, syntactic mutants |
| Conclusion | no P3 Conclusion exists | `NO_CHANGE`; do not create a Conclusion | none | do not place 0/140 or the NumPy pilot in a Conclusion as a general negative or general positive finding |
| Living core-claims addendum | `scope_authority` currently has no current-paper scope paragraph after the verbatim table | append exactly one addendum titled `Current-paper RQ2/C3 scope` after the claim-ceiling table, using the wording in section 5.2 | all objects in section 2 | do not change the verbatim RQ2 block or the C3 table row; do not mark C3 as anything other than `blocked` |
| Governing scientific plan | frozen verbatim source of RQ2 and C3 | `NO_CHANGE` | none | do not silently rewrite the historical plan to match the addendum |
| Historical outline | superseded planning outline; still talks about a future multi-program empirical paper | `NO_CHANGE` | none | do not treat planned multi-program text as an already delivered result |
| P2 manuscripts | different paper | `NO_CHANGE` | none | do not import P3 counts into P2 |

### 5.2 Implementable core wording

Implementation must use the following meaning. Wording may be
tightened for grammar, but the scientific content must not change.

```text
On one NumPy subject and four frozen pairs, semantic mutants are
4/4 KILL, syntactic mutants are 3/4 KILL and 1/4 SURVIVE, and both
exact-overlap measures are 0/4. That result is a single-project
paired-evidence pilot, not a multi-project comparison. A later
140-slot applicability census on 14 preregistered successors, under
the frozen Public Behavior Frame, slot inventory, and predicate
bounds, produced 0 SITE_FROZEN. This version therefore has no
Stage II candidate. Multi-project construct-distinctness and
project-clustered uncertainty remain unidentifiable.
```

Required addendum facts, in addition to that paragraph:

1. C3 remains `blocked`.
2. `n_projects = 1`.
3. Stage II candidate universe = 0.
4. `upgrade_condition` remains
   `RQ2 paired evidence and uncertainty accounting complete` and is
   unmet.
5. 0/140 is bound to the frozen PBF, inventory, predicates,
   first-applicable boundary, and ordinals 9-22.
6. RQ2 remains; the current paper answers only the three items in
   section 3.

If a later manuscript is drafted from this design, the core wording
may enter Methods/Flow, pilot Results, or Limitations only. It must
not enter Abstract, Contributions, or Conclusion as a general
finding. That later manuscript is not created by the next
implementation task.

## 6. Allowed and forbidden interpretations

Allowed:

1. Ordinal 8 is a single-project paired-evidence pilot on NumPy.
2. On those four frozen pairs, semantic mutants are 4/4 `KILL` and
   syntactic mutants are 3/4 `KILL` (1/4 `SURVIVE`).
3. Both exact-overlap measures are 0/4 on those pairs.
4. Exact non-overlap on this pilot is a construct-distinctness
   observation for these pairs, not a testing-value result.
5. Stage I is a prospective applicability census under a frozen
   authority.
6. Under that frozen authority, 0 of 140 slots were `SITE_FROZEN`.
7. The current two-stage version has no Stage II candidate.
8. C3 stays `blocked` because multi-project construct-distinctness
   and project-clustered uncertainty remain unidentifiable.
9. RQ2 stays; its current-paper answers are the pilot, the overlap
   counts, and the missing multi-project identification.

Forbidden:

1. Do not state that the 14 subjects or their programs lack the
   target construct.
2. Do not transport 0/140 as an industrial applicability rate.
3. Do not state that semantic mutation is generally better than, or
   generally different from, syntactic mutation.
4. Do not transport the NumPy pilot as a multi-project result.
5. Do not write Stage I as C3-supporting evidence.
6. Do not treat 18 programs or 35 defects as 18 runnable
   paired-evidence projects.
7. Do not rewrite already produced results, and do not substitute a
   new analysis for the missing multi-project data.
8. Do not write that C3 has been met, lifted, or moved to any status
   other than `blocked`.
9. Do not start another subject table, another predicate set, or
   another paired runner for the present C3.
10. Do not start Stage I or Stage II again on this version.

## 7. Verification

This design task verifies only the items below. It does not run
pytest, a build, profiling, mutation, Stage I, Stage II, any
subject, any runner, or a full suite.

1. The four core evidence identities in section 2 match the files at
   HEAD `7e28b6fc3bae36327e1dd39e4a323d79b70bf738`.
2. Internal consistency:
   C3 stays `blocked`;
   `n_projects = 1`;
   Stage II candidate universe = 0;
   upgrade condition text is unchanged and unmet;
   0/140 is qualified, not transported;
   RQ2 is kept;
   no second project is sought.
3. This file must not propose lifting C3, a general missing-construct
   finding, a multi-project confirmatory result, another subject
   table, another predicate set, a repeated Stage I or Stage II
   start, or placeholder tokens.
4. `git diff --check` must be clean.
5. The working-tree diff must contain only this file.

Implementation verification (next task, not this task):

1. YAML C3 `status` remains `blocked`.
2. YAML C3 `upgrade_condition` remains the exact historical string.
3. `status_policy.note` matches section 4.2.
4. Core-claims addendum matches section 5.2 meaning.
5. No other claim row changes.
6. No schema field is added.
7. Diff contains only the ledger file and the core-claims addendum,
   unless a later pin must follow the new ledger digest.

## 8. Completion and no-reopening rule

Success terminal for this design task:

`CLAIM_SCOPE_AND_LEDGER_AMENDMENT_DESIGN_READY`

Unique next task:

`P3_C3_CLAIM_SCOPE_AND_LEDGER_AMENDMENT_IMPLEMENTATION`

That task implements sections 4 and 5 only. It must not:

1. change C3 away from `blocked`;
2. add a ledger field or a second ledger;
3. write an implementation plan or a second design;
4. choose among another subject table, another predicate set, and
   claim-scope reduction again;
5. start Stage I, Stage II, or any paired runner;
6. open P12, a reveal, a patch, or a mutation outcome;
7. treat this design as an observation that C3 is now met.

After implementation, the scientific key path is the amended ledger
plus the living addendum. The closed Stage II path stays closed.
The missing multi-project data stay missing. The next paper-facing
work uses the wording already fixed here.
