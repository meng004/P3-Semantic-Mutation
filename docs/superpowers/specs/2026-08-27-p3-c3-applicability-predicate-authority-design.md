# P3 C3 Applicability Predicate Authority Design

Date: 2026-08-27
Status: `DESIGN_FOR_REVIEW`
Mode: prospective, outcome-blind, subject-independent Phase-2 authority design
Origin: controller-approved 35-subject / 350-slot / five-predicate rules; Phase-0 site policy and operator catalogue as scientific principles only
Verification status: `ANALYZED`
Reproducibility: `NOT_APPLICABLE` (this task produces a design, not a freeze)
Task success terminal after review: `AUTHORITY_DESIGN_READY`

This document is a design for missing authority. It is not a frozen
inventory, registry, manifest, site-selection result, or scientific
experiment. C3 remains `blocked`.

## 1. Scientific purpose

Package A site selection is defined as: freeze ten family/mechanism slots
per confirmatory subject, scan canonical sites with a static family
predicate, and take the first strict `true` or close
`APPLICABILITY_CLOSED_NOT_APPLICABLE`. Unused budget does not transfer.

That procedure is prospective only if the 350-slot inventory and the five
predicates exist, are subject-independent, and are hash-bound before any
concrete site path, symbol, or span is read. Those artifacts do not exist
on the current HEAD. This design specifies them so a later implementation
plan can add one production seam without writing subject-specific or
after-the-fact rules.

Completing the later implementation still does not upgrade C3. It only
makes first-applicable closure auditable.

## 2. Scope and non-goals

In scope:

- one 35-subject identity-only projection seam;
- mechanical generation of exactly 350 slots;
- five global static predicates;
- one predicate registry;
- one authority manifest;
- the unique production loader that later site-closure consumers must use.

Out of scope, and not performed by this task:

- writing production modules or JSON artifacts;
- running site selection or creating `SITE_FROZEN` objects;
- creating contracts, `E_CONTRACT`, patches, mutants, or baselines;
- reading any real site, source file, archive, profiling result, technique
  profile, RQ handoff, claim outcome, P12 defect material, or Package C;
- adding a second manifest, claim ledger, parallel validator, or new
  authorization format;
- adding a new schema file;
- changing the claim ledger or C3 `status`.

Earlier Phase-2 planning text, including
`docs/superpowers/plans/2026-08-08-p3-v3-phase0-phase2-cursor-vm.md` and
operator-catalogue §6.2, is provenance only. It is not frozen executable
authority.

## 3. Chronology and blindness

Required later chronology, once implemented:

1. Load the 35-subject identity projection without outcome fields.
2. Generate and verify the 350-slot inventory. Slots contain no site.
3. Load and verify the predicate registry and implementation bytes.
4. Validate the single authority manifest against those identities.
5. Only then enumerate canonical sites and evaluate predicates.

Forbidden chronology:

1. Open a subject's sites or source.
2. Edit slot assignment or a predicate.
3. Regenerate inventory or closure.
4. Record the result as if the rule had been frozen first.

Predicates read only the current canonical site, the PBF rows exactly
joined to that site (including a static `schema_kind` attachment defined
below), the family, and the frozen registry rule. They do not read the
filesystem, source text, profiling, patches, MRs, outcomes, or
subject/project identity. `UNPROFILED` is not `NOT_APPLICABLE`.

## 4. 35-subject identity input seam

The confirmatory cohort is the existing 35 Phase-1 controlled subjects.
No subject is added or removed.

`subject-frames.json` does not exist. Each
`derived-subject-<neutral_snapshot_id>.json` contains a usable
`subject.controlled_subject_id`, but the same file also embeds `sites`,
`primary_technique`, `technique_vector`, `profiling_results`, and
`technique_profile`. That document is not an allowed authority input.

The production loader therefore must not receive derived-subject files.
Those files carry `sites`, `primary_technique`, `technique_vector`,
`profiling_results`, and `technique_profile`. It must build a narrow
identity-only projection as follows.

Identity inputs, and only these fields:

1. `data/p3_v3/p12_intake/verified_bridge.json` `records[]` fields
   `neutral_snapshot_id`, `normalized_source_tree_sha256`, and
   `build_descriptor_sha256`. The snapshot ID is a filename key used only
   to pair the matching workload artifact. It is not a sort key. The
   loader must ignore every other record field, including
   `fixed_tree_commitment`, `source_archive_sha256`, `eligibility_reason`,
   `eligible_for_construct`, and `eligible_for_criterion`.
2. The `artifact_sha256` field of
   `data/p3_v3/phase1_frames/out/profiling-workload-<neutral_snapshot_id>.json`.
   That value is `public_workload_set_sha256`. The loader must ignore
   `selected_rows`, `selected_behavior_ids`, `budget`, `scale_class`,
   `category_order`, `selected_category_counts`, and
   `controlled_subject_source_id`. It must not open any
   profiling-result file.

Rebuild, using existing `canonical_sha256`:

```text
controlled_subject_id = canonical_sha256({
  "normalized_source_tree_sha256": <bridge record>,
  "build_descriptor_sha256": <bridge record>,
  "public_workload_set_sha256": <workload artifact_sha256>,
  "domain": "P3-SUBJECT-v1"
})
```

Loader rules:

- emit exactly 35 unique lowercase SHA-256 strings;
- reject duplicate, missing, or malformed IDs;
- sort the 35 IDs by UTF-8 / ASCII byte order ascending;
- set `subject_index` to the post-sort position `0..34`;
- do not sort or filter by snapshot ID, project name, scale, profiling
  status, or technique;
- do not return any field other than `controlled_subject_id`.

The canonical JSON array of those 35 sorted IDs is the subject-identity
projection. Its `canonical_sha256` is bound in the single authority
manifest. The array is stored as a field of that manifest, not as a
second ledger.

## 5. 350-slot generation

Frozen sequences:

```text
SEMANTIC_CONTRACT_FAMILIES = ("INV", "MONO", "CONV", "DYN", "CMP")
MECHANISM_ORDER = ("CE", "OS", "HP", "TF", "SI")
```

For each `subject_index` in `0..34`, each family in the family tuple,
and each `slot_ordinal` in `{0, 1}`:

```text
mechanism = MECHANISM_ORDER[(subject_index + slot_ordinal) % 5]
```

The mechanism rule is identical for every family. Site-selection results
do not change mechanism. An inapplicable slot stays in its family and
subject; its budget is not transferred.

### 5.1 Counts

| Quantity | Formula | Value |
|---|---|---|
| Total slots | 35 subjects × 5 families × 2 ordinals | 350 |
| Slots per subject | 5 × 2 | 10 |
| Slots per family | 35 × 2 | 70 |
| Slots per family/mechanism | see below | 14 |

Fix family `F` and mechanism index `m` in `0..4`. The generating rule is
`(subject_index + slot_ordinal) % 5 == m`.

- `slot_ordinal = 0` gives `subject_index % 5 == m`: seven indices
  (`m, m+5, …, m+30`).
- `slot_ordinal = 1` gives `subject_index % 5 == (m + 4) % 5`: seven
  other indices.

Those two residue classes are disjoint, so each family/mechanism cell
has exactly 14 slots. Check: 5 families × 5 mechanisms × 14 = 350.

### 5.2 Slot identity

```text
slot_id = canonical_sha256({
  "domain": "P3-SLOT-IDENTITY-v1",
  "controlled_subject_id": controlled_subject_id,
  "semantic_contract_family": family,
  "slot_ordinal": ordinal,
  "permitted_construction_mechanism": mechanism
})
```

Each inventory row has exactly these fields, in this meaning:

- `slot_id`
- `controlled_subject_id`
- `semantic_contract_family`
- `slot_ordinal`
- `permitted_construction_mechanism`

The row does not contain a site, applicability result, profiling field,
contract, patch, or outcome. The same 35-ID input always rebuilds the
same 350 rows and the same `slot_id` values.

### 5.3 Canonical inventory order

Sort rows by:

1. `controlled_subject_id` (UTF-8 byte order);
2. family position in `SEMANTIC_CONTRACT_FAMILIES`;
3. `slot_ordinal`;
4. `permitted_construction_mechanism` by `MECHANISM_ORDER`;
5. `slot_id`.

Because mechanism is a function of subject index and ordinal, rule 4
does not reorder a correctly generated inventory; it only makes a
corrupt row detectable.

## 6. Exact join, tail, and tokens

### 6.1 Site-to-row join

A PBF row is joined to a site if and only if both hold:

1. `site.path == row.provenance_path` (exact string equality);
2. `symbol_tail(site.symbol) == symbol_tail(row.entrypoint)` (exact
   equality after the tail rule below).

`normalized_entrypoint` is not a join key. There is no fuzzy match,
edit distance, prefix match, or semantic guess. Comparison is
case-sensitive on the extracted tails.

`symbol_tail(value)`:

1. require `value` to be a string; otherwise the value does not join;
2. take the substring after the last `:`, or the whole string if none;
3. from that result, take the substring after the last `.`, or the
   whole result if none.

Synthetic examples, not from any cohort subject:

| Input | After last `:` | After last `.` | Tail |
|---|---|---|---|
| `ns:pkg.Type.method` | `pkg.Type.method` | `method` | `method` |
| `Type.method` | `Type.method` | `method` | `method` |
| `method` | `method` | `method` | `method` |
| `ns:method` | `method` | `method` | `method` |
| `pkg.Type` | `pkg.Type` | `Type` | `Type` |

Join results are sorted by the row's existing canonical identity:
`behavior_id` ascending, then `artifact_sha256` ascending. A row missing
`behavior_id` or `artifact_sha256` is dropped (fail closed for that
row). One site may join zero, one, or many rows. Zero joins make every
predicate return `false`.

### 6.2 Static `schema_kind` attachment

PBF `rows` carry `category`, `provenance_path`, `entrypoint`, and
`declared_input_schema_sha256`. They do not carry `schema_kind`.
`schema_kind` lives on the same frame's `public_schemas`.

After a row joins a site, attach `schema_kind` from the unique
`public_schemas` entry whose `canonical_sha256(raw_schema)` equals
`row.declared_input_schema_sha256`. The hash is the existing
`src/p3_v3/artifacts.py` `canonical_sha256`, which is the same
canonical JSON SHA already used to write `declared_input_schema_sha256`.
If that match is not unique, or `raw_schema` /
`declared_input_schema_sha256` is missing, leave `schema_kind` unset.
Predicates that require a named `schema_kind` then fail that row. This
attachment reads only the frozen PBF document. It does not read source
files.

The objects passed as `joined_public_rows` are these joined rows after
attachment. They are still static PBF data.

### 6.3 Tokenization

When a rule needs tokens:

1. Unicode casefold the string;
2. split on every character that is not an ASCII letter or ASCII digit;
   underscore is a boundary;
3. drop empty tokens;
4. accept only complete-token equality;
5. do not search substrings.

Synthetic examples, not from any cohort subject:

| Input | Tokens | `iterate` in tokens | `sim` in tokens |
|---|---|---|---|
| `do_iterate` | `do`, `iterate` | true | false |
| `myIterate` | `myiterate` | false | false |
| `converged` | `converged` | false | false |
| `path/sim/run.py` | `path`, `sim`, `run`, `py` | false | true |
| `simulation` | `simulation` | false | false |
| `traj-evolve` | `traj`, `evolve` | false | false |

## 7. Five predicate specifications

Production interface:

```text
evaluate_predicate(predicate_id, site, joined_public_rows) -> bool
```

Common rules:

- the return type must be exactly `bool`;
- unknown `predicate_id` raises a fail-closed evidence error;
- a missing required site field (`path`, `symbol`) raises a fail-closed
  evidence error;
- a joined row missing a field required by the active clause does not
  satisfy that clause;
- the registry maps `predicate_id` to family and implementation;
- no subject-specific override and no runtime fallback;
- no always-true or always-false placeholder;
- predicates do not sort sites and do not select sites;
- first-applicable remains
  `select_first_applicable_site` / `close_slot`.

Zero joined rows: all five predicates return `false`.

### 7.1 INV — `APPLICABILITY_INV_V1`

Return `true` if and only if at least one joined row has
`category == "PUBLIC_API"` and `schema_kind` in
`{"NUMERIC_ARRAY_DOMAIN_V1", "JSON_SCHEMA_DRAFT2020_12_V1"}`.

### 7.2 MONO — `APPLICABILITY_MONO_V1`

Return `true` if and only if at least one joined row has
`category == "PUBLIC_API"` and
`schema_kind == "NUMERIC_ARRAY_DOMAIN_V1"`.

### 7.3 CONV — `APPLICABILITY_CONV_V1`

Return `true` if and only if at least one joined row has `category` in
`{"BENCHMARK", "EXAMPLE"}` and the site-symbol token set intersects
`{"iterate", "step", "solve", "minimize", "converge"}`.

### 7.4 DYN — `APPLICABILITY_DYN_V1`

Return `true` if and only if at least one joined row has `category` in
`{"EXAMPLE", "PROJECT_TEST"}` and the site-path token set intersects
`{"sim", "traj", "dyn", "evolve", "integrate"}`.

### 7.5 CMP — `APPLICABILITY_CMP_V1`

Return `true` if and only if at least one joined row has
`category == "CLI"` or `schema_kind` in
`{"TEXT_IO_SCHEMA_V1", "CLI_TOKEN_GRAMMAR_V1"}`.

## 8. Registry structure

One file, later, not created now:

`data/p3_v3/protocol/applicability-predicate-registry.json`

Canonical JSON object with `schema_version`
`p3-applicability-predicate-registry-v1`, `artifact_sha256`, and exactly
five `predicates` rows, in family order INV, MONO, CONV, DYN, CMP.

Each row has exactly:

| Field | INV | MONO | CONV | DYN | CMP |
|---|---|---|---|---|---|
| `predicate_id` | `APPLICABILITY_INV_V1` | `APPLICABILITY_MONO_V1` | `APPLICABILITY_CONV_V1` | `APPLICABILITY_DYN_V1` | `APPLICABILITY_CMP_V1` |
| `semantic_contract_family` | `INV` | `MONO` | `CONV` | `DYN` | `CMP` |
| `accepted_site_categories` | `["PUBLIC_API"]` | `["PUBLIC_API"]` | `["BENCHMARK","EXAMPLE"]` | `["EXAMPLE","PROJECT_TEST"]` | `["CLI"]` plus schema-kind clause |
| `required_static_fields` | site `path`,`symbol`; row `category`,`schema_kind` | same | site `path`,`symbol`; row `category` | site `path`; row `category` | site `path`,`symbol`; row `category` or `schema_kind` |
| `decision_rule` | §7.1 text | §7.2 text | §7.3 text | §7.4 text | §7.5 text |
| `implementation_path` | `src/p3_v3/applicability_predicates.py` | same | same | same | same |
| `implementation_source_sha256` | SHA-256 of that file | same | same | same | same |

`decision_rule` records the verifiable condition. It does not copy the
Python function body. CMP `accepted_site_categories` documents the CLI
category; the schema-kind alternative remains in `decision_rule`.

## 9. Single authority manifest

One file, later, not created now:

`data/p3_v3/phase2/applicability-authority.json`

This is the only Phase-2 applicability authority manifest. It binds:

| Field | Bound identity |
|---|---|
| `authority_id` | `p3-v3-phase2-applicability-authority-v1` |
| `schema_version` | `p3-applicability-authority-v1` |
| `subject_identity_projection` | the 35 sorted `controlled_subject_id` strings |
| `subject_identity_projection_sha256` | `canonical_sha256` of that array |
| `site_policy_sha256` | current file SHA-256 of `data/p3_v3/protocol/site_policy.md` |
| `operator_catalogue_sha256` | current file SHA-256 of `data/p3_v3/protocol/operator_catalogue.md` |
| `slot_inventory_artifact_sha256` | artifact hash of `slot-inventory.json` |
| `slot_implementation_source_sha256` | file SHA-256 of `src/p3_v3/slot_inventory.py` |
| `predicate_registry_artifact_sha256` | artifact hash of the registry |
| `predicate_implementation_source_sha256` | file SHA-256 of `src/p3_v3/applicability_predicates.py` |
| `canonicalization_implementation_source_sha256` | file SHA-256 of `src/p3_v3/artifacts.py` |
| `artifact_sha256` | `canonical_sha256` of the manifest body without this field |

It does not bind site-selection results, contracts, patches, mutants, or
outcomes. When a later protocol revision absorbs these bindings, this
independent manifest is deleted. Two parallel authorities must not remain.

Known current protocol file hashes, for later binding, not claimed as
already bound by a Phase-2 manifest:

- `site_policy.md`: `9772430e0a2539667a9aaa776b47ecae92a7830e19ec0a6e75a5dda9cfdfdcf7`
- `operator_catalogue.md`: `060671a031c36699fe63c7376afbb4714c84b25eab28f06445804ee8d232a635`

## 10. Module boundaries

Proposed production files, not created by this task:

1. `src/p3_v3/slot_inventory.py`
   Validate the 35 IDs, generate 350 rows, compute `slot_id`, apply
   canonical order. No site selection.
2. `src/p3_v3/applicability_predicates.py`
   Exact join, tail extraction, tokenization, five pure predicates,
   `evaluate_predicate`, and the unique authority loader. No filesystem
   reads of subject source. Registry and manifest paths are the only
   allowed file reads, and only inside the loader.
3. `data/p3_v3/protocol/applicability-predicate-registry.json`
4. `data/p3_v3/phase2/slot-inventory.json`
   350 canonical rows, mechanically generated, never hand-edited.
5. `data/p3_v3/phase2/applicability-authority.json`

Existing seams that remain:

- `canonical_sha256` / `canonical_json_bytes` in `src/p3_v3/artifacts.py`;
- `_sites`, `select_first_applicable_site`, and `close_slot` in
  `src/p3_v3/bridge_and_frames.py`;
- `scripts/p3_v3/evidence.py build-frames --slots` and
  `--applicability-map`.

`close_slot` uses exact-object `_SLOT_SCHEMA` `{slot_id,
controlled_subject_id}`. The inventory row has three extra fields. The
production wrapper must pass only that two-field subset into `close_slot`.
It must not widen `_SLOT_SCHEMA` and must not add a new schema file.

`evidence.py` currently treats `--applicability-map` as `site_id -> bool`
and defaults missing keys to `False`. After implementation, the unique
loader must replace that lookup. Callers must not supply a private
predicate or a handwritten map.

Unique consumer seam:

```text
load_applicability_authority(manifest_path) -> Authority
close_slot_with_authority(authority, inventory_row, canonical_sites, pbf) -> closure
```

`load_applicability_authority` rebuilds the 35 IDs, rebuilds the 350-row
inventory, checks every bound SHA, and refuses to return if any check
fails. `close_slot_with_authority` joins PBF rows for each site, calls
`evaluate_predicate` for the row's family, and delegates selection to
`select_first_applicable_site` / `close_slot`. Every Phase-2 consumer
imports this pair. No consumer re-validates the bytes itself.

## 11. Error semantics

| Condition | Effect |
|---|---|
| Duplicate, missing, or non-SHA subject ID | fail closed; no inventory |
| Rebuilt IDs ≠ bound projection | fail closed; no inventory |
| Rebuilt inventory ≠ `slot-inventory.json` | fail closed |
| Unknown `predicate_id` | fail closed evidence error |
| Site missing `path` or `symbol` | fail closed evidence error |
| Predicate return is not `bool` | existing `E_APPLICABILITY_RESULT` |
| Canonical site order violated | existing `E_SITE_ORDER` |
| Authority byte mismatch | fail closed; no closure |
| Zero joined rows | all predicates return `false` |
| Inapplicable slot | `APPLICABILITY_CLOSED_NOT_APPLICABLE`; no transfer |

## 12. Minimal focused tests

Write these tests later. This task does not create or run them.

Slot inventory:

1. 35 unique subject IDs yield exactly 350 slots.
2. Each subject has 10 slots.
3. Each family has 70 slots.
4. Each family/mechanism pair has 14 slots.
5. Every `slot_id` rebuilds and all 350 values are unique.
6. Shuffling the input subject order does not change the inventory.
7. Duplicate, missing, or illegal subject IDs fail closed.
8. Inventory rows have no site, profiling, contract, patch, or outcome field.

Predicates:

9. Exact join succeeds and fails on synthetic path/tail pairs.
10. Tail extraction uses only the last `:` and last `.`.
11. Token boundaries reject substring hits (`simulation` is not `sim`).
12. Each predicate has one synthetic true fixture.
13. Each predicate has one synthetic false fixture.
14. Zero joined rows make all five predicates false.
15. Multiple joined rows are canonical and deterministic.
16. Non-bool returns, unknown `predicate_id`, and missing site fields fail closed.
17. Predicate functions do not accept subject or project ID parameters.
18. Predicate functions do not read the filesystem or environment variables.

Selection seam:

19. Canonical sites select the first applicable site.
20. Non-canonical site order is rejected by the existing seam.
21. No applicable site yields `APPLICABILITY_CLOSED_NOT_APPLICABLE`.
22. An inapplicable slot does not transfer budget.
23. Shuffling PBF row input order does not change the predicate result.

Authority binding:

24. The original manifest, registry, inventory, and source identities pass.
25. Changing any bound byte fails validation.
26. The authority object contains no site result, contract, patch, or outcome.
27. The 35-subject projection contains only SHA-256 IDs.

Later implementation runs only these focused tests, the related
bridge/closure regressions, and `git diff --check`. No full-suite mandate.

## 13. Minimal defensive control

Concrete failure scenario:
After inspecting a subject's concrete sites, an implementer changes slot
assignment or a predicate implementation, then regenerates first-applicable
closures.

Harmed asset:
Prospective validity of C3 construct distinctness, unbiased site
selection, and an auditable chronology.

Trigger sequence:
Open subject sites → edit rule or implementation → regenerate inventory
or closure → record the after-the-fact choice as a frozen result.

Observable consequence:
The same authority version yields different slot or site results on the
same input, or a formal closure cannot bind the predicate bytes that
produced it.

Why existing mechanisms are not enough:
Git records history but a commit does not state which registry, inventory,
and implementation bytes a formal closure consumed. Ordinary tests can
check synthetic examples but do not bind official run inputs. Primary
keys, type checks, and uniqueness constraints cannot stop a rule from
being rebound after sites were seen.

Existing mechanisms that do not apply, and why:
Database transactions and uniqueness constraints do not apply; official
evidence is files. A version number does not prove file bytes. The
existing Phase-0 protocol manifest does not contain these missing
Phase-2 artifacts.

Minimal added control:
One cohort-wide `applicability-authority.json` that binds only the slot
inventory, the predicate registry, the two implementation sources, and
the existing protocol and canonicalization identities.

Why this module/seam:
Every site closure must pass through `load_applicability_authority`.
One check covers every consumer.

Proof test:
After changing the slot inventory, the registry, or either implementation
byte, authority validation fails. The original fixed input passes.

Maintenance cost and failure mode:
One new manifest version and one shared loader. A legitimate code change
requires a new authority version. A wrong binding blocks site closure.

Future deletion condition:
If a later single main protocol manifest absorbs these bindings, delete
this independent Phase-2 manifest. Do not keep two authorities.

## 14. Claim interpretation

This design is engineering and experimental pre-work. It is not new C3
experimental data. Implementing it later does not upgrade
`research/evidence/p3_claim_ledger_v1.3.0.yml`. C3
`C3_SEMANTIC_CONSTRUCT_DISTINCTNESS` remains `blocked`, with
`upgrade_condition` still "RQ2 paired evidence and uncertainty
accounting complete".

## 15. Implementation exclusions

This task does not:

- create the five production files;
- implement Python modules;
- generate `slot-inventory.json` or the registry;
- write `applicability-authority.json`;
- run tests;
- run site selection;
- create `SITE_FROZEN`, contracts, patches, or mutants;
- modify the single-subject Package A design document;
- modify the claim ledger, Phase-1 artifacts, PBF files, or archives.

`empty-slots.json` (`[]`), `empty-applicability.json` (`{}`), and
`empty-contracts.json` (`{}`) remain the current empty inputs until a
later implementation replaces the `--slots` / `--applicability-map` seam
with the authority loader.

## 16. Review checklist

- Status is `DESIGN_FOR_REVIEW`, not a freeze.
- Counts are 35, 350, 10, 70, and 14, with the residue-class proof.
- Five predicates match the controller text.
- Join, tail, and token rules are exact and have only synthetic examples.
- One manifest, one registry, one inventory, one loader.
- `close_slot` still receives the two-field subset.
- No real site path, symbol, or span.
- No subject-specific override and no named-subject special case.
- No applicability prediction for any subject.
- Next task is an implementation plan, not implementation or a run.

## 17. Unique next task

`P3_C3_APPLICABILITY_PREDICATE_AUTHORITY_IMPLEMENTATION_PLAN`

Do not execute that task here. Do not implement the modules or emit the
JSON artifacts in this document.
