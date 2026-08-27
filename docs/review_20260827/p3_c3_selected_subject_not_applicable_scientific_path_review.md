# P3 C3 Selected-Subject 10/10 NOT_APPLICABLE Scientific Path Review

Date: 2026-08-27
Task: `P3_C3_SELECTED_SUBJECT_NOT_APPLICABLE_SCIENTIFIC_PATH_REVIEW`
Model / reasoning: `gpt-5.6-sol` / high
Mode: evidence interpretation and path adjudication only
Verification status: `ANALYZED`
Reproducibility: `NOT_APPLICABLE` (no new experiment)

## 1. Unique terminal

`NO_PREEXISTING_SUCCESSOR_RULE`

Decision order applied as written. Later terminals were not considered
once an earlier terminal was excluded:

| Code | Result |
|---|---|
| A. `SITE_SELECTION_EVIDENCE_CONFLICT` | excluded: identity checks passed |
| B. `SELECTED_SUBJECT_ELIGIBILITY_UPDATE_READY` | excluded: no preexisting mechanical eligibility/exclusion seam is completed by these closures |
| C. `PREEXISTING_SUCCESSOR_AUTHORIZED` | excluded: no pre-result successor trigger; rank 2 is not authorized |
| D. `NO_PREEXISTING_SUCCESSOR_RULE` | selected |

This review does not update eligibility, does not authorize rank 2, does
not design a prospective v2 successor, and does not edit the claim
ledger.

The confirmatory Package A path on the frozen selected subject stops
here.

Unique next task:

`P3_C3_FROZEN_PATH_CLOSURE_AND_REPRIORITIZATION`

## 2. Evidence identity

Worktree: `/tmp/p3-c3-applicability-authority`
Branch: `codex/p3-c3-applicability-authority`
HEAD and `origin/codex/p3-c3-applicability-authority`:
`e6f9e84a5a71900e0fb6f0655393c5e1b613b6a5`
Worktree porcelain at review start: empty.

Selected subject:

- neutral snapshot ID:
  `6e05301ec7ec79d16233c086e5fc4a0b714e82a6ec8d6a86ca1218be67135062`
- controlled subject ID:
  `942d190c2c3972a6a6e9feb6ef5d4abee1d939cb0aa9ee676232ab0184dead09`

Official closure directory:

`data/p3_v3/phase2/site-closures/6e05301ec7ec79d16233c086e5fc4a0b714e82a6ec8d6a86ca1218be67135062`

Read-only checks that passed:

- exactly 10 regular JSON files; no symlink or second closure tree;
- repository-wide `slot-closure-*.json` count is 10;
- the 10 filenames cover exactly the frozen inventory rows for this
  controlled subject ID;
- families are INV, MONO, CONV, DYN, CMP, two slots each;
- every closure is
  `state=APPLICABILITY_CLOSED_NOT_APPLICABLE`,
  `path=APPLICABILITY_CLOSED_NOT_APPLICABLE`,
  `site_id=null`;
- every closure satisfies
  `artifact_sha256 = canonical_sha256(body without artifact_sha256)`;
- production `validate-applicability-authority` exited 0 with
  `status=PASS`, `subject_count=35`, `slot_count=350`;
- the official site-selection write process remains the single commit
  `e6f9e84a` (`data(p3-v3): freeze selected subject site closures`);
  no retry commit and no second official directory exist.

Site selection was not rerun.

## 3. Exact observation

The subject, under the already frozen cohort-wide applicability
authority, has 10/10 slots inapplicable.

More precisely:

Under the frozen Public Behavior Frame, the 3338 frozen canonical sites
derived from that frame, the five frozen static predicates, and the
frozen join / tail / token / `schema_kind` rules, each of this subject's
10 frozen family/mechanism slots closed as
`APPLICABILITY_CLOSED_NOT_APPLICABLE`. Unused slot budget was not
transferred.

That is the entire confirmatory observation.

## 4. Forbidden extrapolations

The evidence does **not** support, and the frozen rules forbid treating
the observation as, any of the following:

- "Eigen does not contain these semantic constructs."
- "Eigen has no site suitable for mutation."
- "The five semantic families do not exist in Eigen."
- "The subject is scientifically empty or should be deleted from the
  Phase-1 cohort."
- "Package A failed because the subject was ineligible at intake."
- "C3 is falsified" or "C3 may now be upgraded."

Those stronger statements would require a different measurement: source
semantics, a complete construct ontology, mutation outcomes, or an
applicability rule other than the frozen predicates. The predicates are
static join and token rules over already frozen PBF rows. A false
predicate is not an existence proof about Eigen.

## 5. Eligibility authority audit

### 5.1 What `eligible_for_construct=true` means

Authority: `data/p3_v3/p12_intake/verified_bridge.json` record for this
neutral snapshot; `data/p3_v3/protocol/package_policy.md` §5.1.1;
authority design §4.

Observation: this record is
`eligible_for_construct=true`,
`eligible_for_criterion=true`,
`eligibility_reason="Defect4MR verified_full formal item (frozen admission)"`.
The field set is the frozen P12 intake schema. The authority loader is
required to ignore `eligible_for_construct` and
`eligible_for_criterion` when projecting controlled subject IDs.

Conclusion: `eligible_for_construct=true` is Phase-1 / bridge admission
into the construct cohort. It does not guarantee Package A
applicability, first-applicable site existence, or later C3 evidence.

### 5.2 Is there a mechanical update seam?

Audited surfaces:

- claim ledger C3: `status` and `upgrade_condition` only; no
  subject-eligibility field;
- bridge record: frozen admission booleans and a frozen prose reason;
  no "set false if 10/10 NOT_APPLICABLE" rule;
- Phase-1 `source-scale-*` and PBF objects: no eligibility / exclusion
  field;
- derived-subject object: identity and chronology hashes only; no
  Package A eligibility field was read or found at the identity layer;
- slot inventory / authority manifest: identity, inventory, and
  implementation bindings; outcome fields are forbidden;
- `unsupported_or_exclusion_reason` in
  `src/p3_v3/bridge_and_frames.py` is an adapter-discovery field, not an
  applicability-closure field;
- analysis spec §10 / §11.1: a target family with no confirmed mutant
  is `UNMEASURED`, not a cohort-exclusion flip;
  §11.2 requires certified-mutant overlap and paired funnels, which
  these closures do not produce.

Conclusion: existing frozen authority does not define a subject
eligibility, Package A eligibility, formal denominator-membership, or
exclusion-reason field that these 10 closures can update without adding
a state, schema, rule, or post-hoc interpretation.

Terminal B is therefore unavailable. This review does not invent such a
seam.

### 5.3 What the frozen rules *do* say about this observation

Authority: `operator_catalogue.md` §6.2 and §6.4;
`site_policy.md` (UNPROFILED is not NOT_APPLICABLE);
authority design §1, §5, §11;
single-subject Package A design §3.1 items 6–7.

Observation: an inapplicable slot is recorded and is not transferred to
another family or subject. A `NOT_APPLICABLE` slot has no contract,
`E_CONTRACT`, patch, or witness. Package A cannot close a
contract/`E_CONTRACT` path on an inapplicable slot. `UNPROFILED` was
not used as `NOT_APPLICABLE`.

Conclusion: the 10 closures are the prescribed terminal for those
slots. They close the current subject's confirmatory construction
continuation. They do not rewrite Phase-1 admission.

## 6. Successor authority audit

### 6.1 What existed before the closures

The single-subject Package A design entered this branch at
`0d566371a27448196177cd911850a56826f94bfc`
(2026-08-27 09:26:20 +0000), before closures
`e6f9e84a5a71900e0fb6f0655393c5e1b613b6a5`
(2026-08-27 10:48:45 +0000).

That pre-result design:

- records an outcome-blind ranking used to freeze **one** subject;
- lists rank 2 as the second row of that ranking table;
- then states, as a freeze rule, "No second subject is authorized";
- freezes this subject and says it "may not be replaced";
- repeats "Do not select a second subject."

Phase-0 protocol files frozen on 2026-08-12
(`operator_catalogue.md`, `site_policy.md`, `package_policy.md`,
`analysis_spec.md`) define slot-level non-transfer and
`NOT_APPLICABLE` chronology. They do not define:

- all-not-applicable then rank 2;
- a successor sequence;
- a maximum number of attempted subjects;
- a cohort-exhaustion rule that names the next subject.

The applicability-authority design likewise forbids budget transfer
and does not authorize a next subject after all slots close
inapplicable.

### 6.2 Ranking is not successor authorization

The rank table is the pre-result rule for choosing the unique first
subject. Presence of a rank-2 row does not prospectively trigger
construction on that row after the first subject's closures are
observed.

Using that table now as a successor list would treat a selection-order
appendix as an unwritten optional-stopping rule.

Terminal C requires a preexisting, mechanically unique next-subject
trigger. That trigger is absent. The preexisting text is the opposite:
no second subject is authorized.

## 7. Outcome-adaptive selection risk

Automatically enabling rank 2 after seeing 10/10
`APPLICABILITY_CLOSED_NOT_APPLICABLE` would be outcome-adaptive
selection and optional stopping:

1. the unique confirmatory subject was frozen before sites were
   closed;
2. the closures are the first confirmatory applicability outcome;
3. no pre-registered rule said "if all ten slots are inapplicable,
   open the next ranked subject";
4. choosing rank 2 now uses that outcome to enlarge the confirmatory
   sample;
5. transferring unused budget to another subject is independently
   forbidden.

This review therefore does not authorize rank 2 and does not recover
another archive.

## 8. Effect on Package A, C3, and the claim ledger

Package A, current confirmatory path:

- the selected subject's 10 slots are formally closed inapplicable;
- no `SITE_FROZEN` object exists for this subject;
- catalogue chronology therefore cannot enter
  `CONTRACT_FROZEN → E_CONTRACT_FROZEN → PATCH_FROZEN` on these
  slots;
- Package A cannot complete as a construction package on this
  frozen subject;
- the confirmatory Package A path stops; it is not repaired by
  replacing the subject.

C3 / claim ledger:

- `C3_SEMANTIC_CONSTRUCT_DISTINCTNESS` remains `blocked`;
- `upgrade_condition` remains
  "RQ2 paired evidence and uncertainty accounting complete";
- analysis spec §11.2 still requires certified-mutant / syntactic
  overlap and paired funnels, which do not exist;
- one inapplicable subject cannot complete that upgrade condition;
- this review does not modify
  `research/evidence/p3_claim_ledger_v1.3.0.yml`.

The observation is a valid negative observation on the frozen
authority. It is not a C3 result.

## 9. New prospective slice: allowed only as a new version

A later slice may be designed. This review does not design or
authorize it. If one is later proposed, the minimum boundary is:

- it must use a new explicit version; it is not confirmatory Package
  A continued;
- the present 10/10 result is prior information and must be
  disclosed;
- successor count, order, stop rule, and scientific use must be
  frozen before any next subject's sites are opened;
- "rank 2 already appeared in the old table" is not pre-authorization;
- whether later results may enter C3 / RQ2 must be decided separately
  by the analysis spec and claim ledger;
- unused budget from these 10 slots still does not transfer.

## 10. Unique next task

`P3_C3_FROZEN_PATH_CLOSURE_AND_REPRIORITIZATION`

Do not, in that next task or this one:

- auto-select rank 2;
- rewrite predicates, slots, authority, or ranking;
- treat this review as a C3 upgrade;
- append an after-the-fact successor rule to the confirmatory path.

## 11. Files read and not read

Read, and only for eligibility, successor, chronology, or identity:

- `research/evidence/p3_claim_ledger_v1.3.0.yml` (C3 status / upgrade
  condition / ledger ceiling)
- `data/p3_v3/protocol/site_policy.md`
- `data/p3_v3/protocol/operator_catalogue.md`
- `data/p3_v3/protocol/package_policy.md`
- `data/p3_v3/protocol/analysis_spec.md` (§10, §11.1, §11.2)
- `docs/superpowers/specs/2026-08-27-p3-c3-single-subject-package-a-design.md`
- `docs/superpowers/specs/2026-08-27-p3-c3-applicability-predicate-authority-design.md`
- `data/p3_v3/phase2/applicability-authority.json`
- `data/p3_v3/phase2/slot-inventory.json`
- the 10 official closures under the selected-subject directory
- `data/p3_v3/p12_intake/verified_bridge.json` (this record's
  eligibility and identity fields; schema keys)
- Phase-1 identity/chronology keys of
  `source-scale-*`, PBF, `profiling-workload-*` (keys only), and
  `derived-subject-*` (top-level and `subject` identity keys only)
- `src/p3_v3/bridge_and_frames.py` schema fragments for bridge
  records and `unsupported_or_exclusion_reason`
- git history / `git grep` on the files above, limited to successor
  and eligibility wording

Not read or consumed:

- Eigen source or archive bytes
- concrete PBF site path, symbol, or span
- profiling results
- technique profile
- RQ handoff
- claim outcomes other than C3 status / upgrade condition
- P12 issue, PR, patch, or reveal ledger
- mutation / MR outcomes

Not run: pytest, build, profiling, mutation, benchmark, site
selection, package manager.

Not modified except this document: production code, tests, authority,
closures, ledger, protocol, designs.

## 12. Final identity

HEAD: `e6f9e84a5a71900e0fb6f0655393c5e1b613b6a5`

This task does not commit or push. After this file is written, the
only expected porcelain entry is this document.

Document path:

`docs/review_20260827/p3_c3_selected_subject_not_applicable_scientific_path_review.md`

Document SHA-256 is computed after write and recorded in the task
return. It is not embedded here, because embedding the digest of a
file that contains that digest is not a self-hash of this review.

## Frozen path closure and reprioritization

Date: 2026-08-27
Task: `P3_C3_FROZEN_PATH_CLOSURE_AND_REPRIORITIZATION`
Model / reasoning: `gpt-5.6-sol` / high
Mode: scientific transition and path priority only
Verification status: `ANALYZED`
Reproducibility: `NOT_APPLICABLE` (no new experiment)

This section is a path-selection decision. It is not a scientific
result. The next scientific advance requires a later new observation.

Candidate set is closed: only
`C2_PROSPECTIVE_WORKLOAD_V2`,
`C3_PROSPECTIVE_V2`, and
`C4_KILL_MATRIX_ADEQUACY`.
Rank 2 is not enabled. A complete v2 is not designed. No experiment
is run.

### 1. Old-path closure terminal

`C3_CONFIRMATORY_PACKAGE_A_PATH_CLOSED`

Exact observation retained from the official closures:

该主体在冻结 authority 下 10/10 slots 不适用。

Read-only identity of that closed path:

| Item | Frozen value |
|---|---|
| Official closure commit | `e6f9e84a5a71900e0fb6f0655393c5e1b613b6a5` |
| Unique subject (neutral snapshot) | `6e05301ec7ec79d16233c086e5fc4a0b714e82a6ec8d6a86ca1218be67135062` |
| Frozen controlled subject ID | `942d190c2c3972a6a6e9feb6ef5d4abee1d939cb0aa9ee676232ab0184dead09` |
| 10/10 slots | `APPLICABILITY_CLOSED_NOT_APPLICABLE` |
| `SITE_FROZEN` objects for this subject | `0` |
| Authority validator (already recorded; not rerun) | `PASS` / 35 subjects / 350 slots |
| Eligibility mechanical update seam | absent |
| Pre-result successor, max-attempt, or exhaustion rule | absent |
| Pre-result confirmatory design | no second subject authorized; selected subject may not be replaced; do not select a second subject |
| C3 ledger | `status=blocked`; `upgrade_condition=RQ2 paired evidence and uncertainty accounting complete` |

The closed object is the old confirmatory Package A path on this
frozen subject. The closures remain valid negative observations under
the frozen authority. They are not rewritten.

Forbidden readings that this closure does **not** authorize:

- that the subject lacks the target semantic constructs;
- that the subject has no site suitable for mutation;
- that the cohort contains no applicable subject;
- that rank 2 would also be inapplicable;
- that a predicate or harness failed.

### 2. Three-path comparison

| Field | A. `C2_PROSPECTIVE_WORKLOAD_V2` | B. `C3_PROSPECTIVE_V2` | C. `C4_KILL_MATRIX_ADEQUACY` |
|---|---|---|---|
| Scientific object | New versioned prospective executable workload plus a non-Boost formal receipt | New versioned prospective/exploratory applicability slice; not confirmatory Package A continued | P3-v3 family-aware SMS / residual explanation on frozen denominators |
| Current frozen start | 35-subject audit `NO_PROSPECTIVE_EXECUTABLE_WORKLOAD` on `54768641` (12 `NO_FROZEN_WORKLOAD`, 1 `TERMINAL_RETRY_FORBIDDEN`, 22 `WORKLOAD_EXECUTION_UNDERSPECIFIED`, 0 `PROSPECTIVE_EXECUTABLE`) | Closed confirmatory path above; 35-ID authority, 350-slot inventory, and 5 predicates remain; `SITE_FROZEN=0` | C4 upgrade_condition is "Frozen kill matrix and all required adequacy views complete"; no P3-v3 kill matrix exists |
| Scientifically legal now? | Yes as a later v2 redesign; continuing the frozen workloads is forbidden; Boost.Math retry is forbidden | Yes only as a newly versioned slice that discloses the 10/10 result and freezes successor / stopping / eligibility rules before any next subject's sites are opened | Not yet. C4 remains strictly downstream of C3 / Phase 4 |
| First new observation | One legal formal profiling receipt on a newly designed prospective workload | One official 10-slot applicability closure set on a subject uniquely named by an already-frozen v2 successor rule | One claim-aligned controlled kill row that can enter the frozen kill matrix and §10 adequacy views |
| Can that observation change eligibility or a satisfied upgrade fragment? | It can add an RQ1 profiling fragment. It cannot flip construct/applicability eligibility, and it cannot satisfy analysis-spec §11.1 diversity/completeness | Yes: it can change v2-defined subject/cohort applicability eligibility. It cannot complete the C3 upgrade_condition | Not reachable until frozen semantic and syntactic denominators and a formal MR inventory exist |
| Independent stages to that observation | 4 | 2 | 8 |
| New production / new external inputs | New workload object; new non-Boost runner; at least one source archive (0 present) | New prospective protocol version only; existing authority, predicates, inventory, and `close_slot_with_authority` stay | New denominator, baseline, MR inventory, execution, and adequacy seams after C3 |
| Reusable frozen inputs | 35 Phase-1 identities/frames; closed Boost.Math formal path must not be reused | 35-ID projection, 350 slots, 5 predicates, authority loader, 35 PBF files (count layer only), selected-subject closures as disclosed prior information | Protocol text and `verify-mr-inventory` only. `data/v5/kill_matrix_v5.json` is not P3 evidence |

The earlier `/workspace` decision
`docs/review_20260827/p3_claim_path_reprioritization.md`
used a different rule (one experiment must be able to change a claim
`status`) and ended at `NO_NEAR_TERM_CLAIM_CHANGING_PATH`. That is a
different decision contract, not an identity contradiction with this
section. This section uses the eligibility-or-upgrade-fragment rule
stated below. Ledger, closure, and C2-audit identities agree.

### 3. Stages to the first new observation

Design-file completion, code completion, and test passage are stages
or engineering preparation. They are not observations.

A. `C2_PROSPECTIVE_WORKLOAD_V2` (4):

1. Freeze a new prospective executable-workload v2 object. The existing
   35-row audit forbids another formal receipt from the frozen
   workloads.
2. Add a non-Boost production runner. `scripts/p3_v3/profile.py`
   exposes only `run-cxx-header-workload`; Boost.Math
   (`74cdc825…`) is `TERMINAL_RETRY_FORBIDDEN`.
   `scripts/p3_v3/audit_prospective_workloads.py` is absent from this
   worktree and must not be rerun.
3. Obtain and bind at least one source archive. Local
   `data/p3_v3/p12_intake/archives/` does not exist; 0 `.tar` files
   are present.
4. Execute one formal profiling run that can emit a legal new receipt.

B. `C3_PROSPECTIVE_V2` (2):

1. Freeze a new explicit prospective protocol version before any next
   subject's sites are opened: successor universe, subject order,
   maximum attempted subjects, exhaustion/stopping rule, eligibility
   interpretation, whether unused budget may move across subjects, and
   the slice's evidence use and ceiling for C3. This task does not
   write that protocol.
2. Run one official site-selection write on the unique next subject
   named by that already-frozen rule, using the existing
   `load_applicability_authority` / `close_slot_with_authority` seam
   and that subject's already frozen PBF identity and site count.

C. `C4_KILL_MATRIX_ADEQUACY` (8):

1. A later C3 path must first produce at least one applicable
   `SITE_FROZEN` slot. None exist now (`site_frozen_files=0`;
   selected subject `SITE_FROZEN=0`).
2. `CONTRACT_FROZEN` on that slot. `empty-contracts.json` is `{}`.
3. `E_CONTRACT_FROZEN`. The live
   `input_generator_registry.json` lists only the five `E_COMMON`
   generators; no `CONTRACT_*` generator is registered.
4. Confirmatory proposal and certification to a frozen semantic-mutant
   denominator. No propose/certify production command exists.
5. Frozen first-order syntactic baseline denominator. Catalogue §7 is
   text only; `pass1_baseline_manifest.json` is a Phase-1 frame
   baseline, not that population.
6. Formal evaluated-MR inventory. `verify-mr-inventory` is a verifier
   over an absent chain.
7. Controlled execution rows in Package B (`package_policy.md`
   §12.1 item 2).
8. First claim-aligned kill observation that can enter the frozen
   kill matrix and the §10 adequacy views required by C4.

P2/v5 `data/v5/kill_matrix_v5.json` is not a substitute for steps
6–8.

### 4. Reusable frozen inputs

Shared and already frozen:

- claim ledger v1.3.0 (file SHA-256
  `bf4979662697b2d0565bb70eec88b22673e84bee93b61234555342efb4082a68`);
  C2/C3/C4 remain `blocked`;
- analysis spec §11.1, §11.2, §10 adequacy views, and §11.3 RQ3
  scoring rules;
- site policy, operator catalogue, and package policy (2026-08-12);
- 35 source-scale, 35 PBF, 35 profiling-workload, and 35
  derived-subject identity objects;
- PBF count layer only: 35 files; 23 nonzero site arrays; 12 empty;
  min 0 / max 62240 / sum 396511 sites. No unread subject's path,
  symbol, or span was opened;
- applicability authority: 35 controlled-subject IDs in
  `subject_identity_projection` (includes
  `942d190c2c3972a6a6e9feb6ef5d4abee1d939cb0aa9ee676232ab0184dead09`);
  350 inventory slots; 5 predicates
  (`APPLICABILITY_INV_V1` … `APPLICABILITY_CMP_V1`);
- production seam
  `validate-applicability-authority` /
  `close_slot_with_authority`;
- official selected-subject closures (10 files, one directory).

Path-specific reuse:

- C2: Phase-1 frames and the already-closed Boost.Math formal attempt
  as a negative bound only. The Boost runner is not reusable for a
  next receipt.
- C3 v2: the entire authority/predicate/inventory/PBF-count layer
  above. First official closures on the selected subject did not
  require a source archive.
- C4: protocol text and the verifier command only.

### 5. Missing external inputs and production seams

A. C2:

- a new prospective workload specification;
- a non-Boost formal runner;
- at least one source archive;
- a unique per-row execution action for the new workload.

B. C3 v2:

- a new prospective protocol version that freezes successor universe,
  order, max attempts, stopping, eligibility interpretation,
  cross-subject budget, and C3 evidence ceiling;
- disclosure of the present 10/10 result as prior information (this
  section supplies the disclosure; it does not write the protocol).

Not required for the first v2 applicability observation:

- rewrite of the 35-ID authority, 350-slot inventory, or five
  predicates;
- source archive recovery;
- propose/certify/baseline commands.

Still blocking any C3 *claim* upgrade after that first observation:

- `SITE_FROZEN → CONTRACT_FROZEN → E_CONTRACT_FROZEN`;
- registered `CONTRACT_*` generators;
- propose / certify production commands;
- certified semantic mutants;
- syntactic baseline population;
- `empty-slots.json = []` and `empty-contracts.json = {}`.

C. C4:

- frozen P3-v3 semantic-mutant denominator: absent;
- frozen syntactic baseline denominator: absent;
- formal MR inventory product: absent;
- controlled execution rows: absent;
- kill-matrix / adequacy CLI: absent.

### 6. What the first new observation can change

| Path | Eligibility | Claim-upgrade fragment |
|---|---|---|
| C2 | No. `eligible_for_construct` is Phase-1 / bridge admission and is not updated by a profiling receipt | Adds at most one RQ1 profiling receipt. Analysis-spec §11.1 still requires complete funnels, ≥75 confirmed non-equivalent semantic mutants, family/size/technique floors, and multi-subject/multi-repository diversity. One receipt cannot mark any of those gates satisfied |
| C3 v2 | Yes, if and only if the v2 protocol first freezes the eligibility interpretation. The next official 10-slot result can then update that v2 subject/cohort applicability eligibility. It cannot rewrite the old confirmatory closures or Phase-1 admission | Cannot complete "RQ2 paired evidence and uncertainty accounting complete". A later applicable slot would still face the contract-generator, mutant, and baseline blockers above |
| C4 | No near-term eligibility effect | First kill row would begin the "frozen kill matrix and all required adequacy views" fragment, but that row is not reachable from the current denominator/MR state |

### 7. Adaptive-selection risk

Automatically opening rank 2, or any other unread subject, because
the selected subject closed 10/10
`APPLICABILITY_CLOSED_NOT_APPLICABLE`, would be outcome-adaptive
selection and optional stopping. The pre-result confirmatory design
forbade a second subject. The old rank table is not successor
authorization.

C3 v2 is legal only if that risk is moved into an explicit new
version:

- disclose the 10/10 result as already observed;
- freeze successor universe, order, max attempts, stopping,
  eligibility interpretation, and budget-transfer rule *before*
  opening the next subject's sites;
- do not relabel the new slice as confirmatory Package A;
- do not amend the old closures after seeing the next result.

This section selects the C3 v2 *path*. It does not name rank 2, does
not open another subject's sites, and does not treat ranking as
authorization.

C2 v2 has a separate adaptive risk: repairing or rerunning a frozen
workload after the audit terminal. That is independently forbidden.

C4 has no present selection risk because no kill denominator exists
to choose from.

### 8. Fixed selection-rule verdicts

Lexicographic order; no subjective weights.

1. The path must be scientifically legal on current evidence.
   C2 v2: pass, as a redesign, not as a retry.
   C3 v2: pass, as a new versioned prospective slice with disclosed
   prior information and pre-observation successor freeze.
   C4: fail as a near-term path; required denominators and MR inputs
   are absent, and C4 is downstream of C3 / Phase 4.
2. The next formal observation must be able to change subject/cohort
   eligibility or a satisfied fragment of a frozen upgrade condition.
   C3 v2: pass (v2 applicability eligibility).
   C2 v2: partial only (profiling fragment; no gate becomes
   satisfied; no eligibility change).
   C4: not reachable.
3. The path must not depend on a forbidden retry, a post-result rule
   rewrite, or undisclosed adaptive selection.
   C3 v2: pass only because successor/stopping rules will be frozen
   first and the 10/10 result is disclosed here.
   C2 v2: pass only as a new workload, not a Boost/audit rerun.
   C4: not reached.
4. Fewest independent stages to the first new observation.
   C3 v2 = 2; C2 v2 = 4; C4 = 8. C3 v2 wins.
5. Fewest new production implementations and new external inputs.
   C3 v2 needs a protocol version. C2 v2 needs a workload, a runner,
   and an archive. C4 needs the entire downstream chain. C3 v2 wins.
6. Most reusable frozen source, identity, authority, and production
   seams. C3 v2 reuses the 35-ID authority, 350 slots, predicates,
   and PBF-count layer. C3 v2 wins.
7. Residual tie-break `C3 > C2 > C4` is not required.

C4 is eliminated by rules 1–2. C2 remains legal but loses rules 4–6.

### 9. Unique terminal

`NEXT_PATH_C3_PROSPECTIVE_V2`

All four required conditions hold:

- a new versioned prospective slice can be established legally;
- existing authority and predicates need not be modified;
- successor and stopping rules can be frozen before the next
  subject's sites are opened;
- that path reaches a new applicability-eligibility observation in
  fewer stages than C2 or C4.

This is not `NEXT_PATH_C2_PROSPECTIVE_WORKLOAD_V2`, because C3 v2 is
legal and nearer.
This is not `NEXT_PATH_C4_FOUNDATION`, because C4 has no frozen
denominator or MR product.
This is not `NO_VALID_NEAR_TERM_PATH`, because C3 v2 is valid under
the stated boundary.
This is not `REPRIORITIZATION_EVIDENCE_CONFLICT`: closure, ledger,
analysis spec, and candidate identities agree.

### 10. Unique next task

`P3_C3_PROSPECTIVE_V2_SUCCESSOR_AND_STOPPING_RULE_DESIGN`

That later task may freeze successor universe, order, max attempts,
stopping, eligibility interpretation, budget-transfer, and C3
evidence ceiling. It may not auto-select rank 2, rewrite the old
closures, modify authority/predicates, or treat this path choice as
a C3 result.

### 11. C3 / claim-ledger hold state

Unchanged and not edited:

- `C2_CERTIFIED_MUTANTS_ACROSS_SCALES_TECHNIQUES`: `blocked`;
  upgrade_condition remains the RQ1 behavior-frame, profiling,
  diversity, and completeness gates;
- `C3_SEMANTIC_CONSTRUCT_DISTINCTNESS`: `blocked`;
  upgrade_condition remains
  "RQ2 paired evidence and uncertainty accounting complete";
- `C4_FAMILY_AWARE_SMS_RESIDUAL_EXPLANATION`: `blocked`;
  upgrade_condition remains
  "Frozen kill matrix and all required adequacy views complete";
- `C5_P12_CRITERION_INCREMENTAL_VALUE`: `blocked` (not a candidate).

`research/evidence/p3_claim_ledger_v1.3.0.yml` is not modified.

### 12. Read and unread scope

Read for comparison only:

- this decision document's prior sections;
- `research/evidence/p3_claim_ledger_v1.3.0.yml` (C2/C3/C4/C5 status
  and upgrade conditions);
- `data/p3_v3/protocol/analysis_spec.md` §10, §11.1, §11.2, §11.3;
- `data/p3_v3/protocol/site_policy.md`;
- `data/p3_v3/protocol/operator_catalogue.md` §6.2, §6.4, §7;
- `data/p3_v3/protocol/package_policy.md` §5.1.1 and §12.1;
- C2 audit object `54768641:docs/review_20260827/p3_prospective_workload_selection_audit.md`;
- `/workspace/docs/review_20260827/p3_claim_path_reprioritization.md`
  (read-only; `/workspace` not modified);
- authority, slot inventory, predicate registry, and input-generator
  registry identity/count fields;
- `scripts/p3_v3` command surface (`evidence.py` subcommands;
  `profile.py` = `run-cxx-header-workload` only);
- `src/p3_v3` seams
  `load_applicability_authority`, `close_slot_with_authority`,
  `SITE_FROZEN` chronology helpers;
- 35-subject identity and PBF/source-scale/workload file counts;
- archive-path existence (absent);
- `empty-slots.json` / `empty-contracts.json`;
- git history showing protocol files on 2026-08-12 and the
  single-subject design at `0d566371` before closures `e6f9e84a`.

Count-only checks on unread subjects:

- 35 PBF files exist;
- site-array lengths only (min 0, max 62240, 23 nonzero);
- 0 local source archives;
- exactly one closure directory, the already selected subject.

Not read:

- unread subjects' PBF site path, symbol, or span;
- Eigen or any other source/archive bytes;
- profiling receipts, technique profiles, or RQ handoffs as new
  evidence;
- P12 issue/PR/patch/reveal ledgers;
- mutation or MR outcomes;
- `data/v5/kill_matrix_v5.json` contents (existence only).

Not run: profiling, mutation, build, compiler, benchmark, pytest,
site selection, Boost.Math, Attempt-2, qualification, the 35-subject
workload audit, or `validate-applicability-authority`.

Not created: prospective v2 design, schema, manifest, ledger,
authorization file, contract, mutant, baseline, or kill matrix.

Not modified except this document: production code, tests, authority,
inventory, predicates, closures, ledger, protocol, or `/workspace`.
