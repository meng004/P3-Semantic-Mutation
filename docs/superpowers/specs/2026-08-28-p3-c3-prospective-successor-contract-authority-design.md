# P3 C3 Prospective Successor Contract Authority Design

Date: 2026-08-28
Status: `TWO_STAGE_PROSPECTIVE_SLICE_REQUIRED`
Task: `P3_C3_PROSPECTIVE_SUCCESSOR_CONTRACT_AUTHORITY_DESIGN`
Model / reasoning: `gpt-5.6-sol` / high
Mode: architectural design of the contract-authority slice only
Verification status: `ANALYZED`
Reproducibility: `NOT_APPLICABLE` (this task produces a design, not an observation)

This document is the unique contract-authority design for ordinals 9–22
under the already approved prospective multiproject paired slice. It is
not an implementation, not a Slice B authorization, not a pair or runner
plan, and not a scientific observation. C3 remains `blocked`. No paired
evidence has been produced for any successor.

Unique terminal:

`TWO_STAGE_PROSPECTIVE_SLICE_REQUIRED`

The document's existence does not make a nonempty source-authorized
contract possible under the current Slice B version.

## 1. Inherited facts that this design must not rewrite

The prior scientific terminal remains:

`CONTRACT_AUTHORITY_REQUIRED_BEFORE_SLICE_B`

Retained production facts:

1. `freeze_production_contracts()` in
   `src/p3_v3/multiproject_production_processor.py` validates
   `data/p3_v3/protocol/contract-generator-registry.json` and then
   returns `()` for every successor. It does not call any generator and
   does not transfer ordinal-8 templates.
2. The official one-shot pipeline therefore cannot reach
   `construct_production_pairs` or `execute_production_pairs` with a
   nonempty contract. Those seams raise authority errors only when given
   a nonempty input; the empty path never reaches them.
3. `PAIRED_EVIDENCE_COMPLETE` has maximum reachable count 0 on ordinals
   9–22 under the current version.
4. If any slot is `SITE_FROZEN` and contracts are empty, the production
   pipeline writes `SITE_ELIGIBLE_NO_AUTHORIZED_CONTRACT` as the subject
   terminal, persists it through the official/staging namespace of
   `p3-c3-prospective-multiproject-paired-slice-v1`, and applies
   `NO_SCIENTIFIC_RETRY`.
5. Official and staging directories for that slice still do not exist.
   No successor has yet been consumed. This design must keep that true.
6. The approved multiproject design
   (`docs/superpowers/specs/2026-08-28-p3-c3-prospective-multiproject-paired-slice-design.md`)
   already separated Slice B (source/applicability one-shot) from Slice C
   (contract/mutant freeze on found projects). The implemented processor
   collapsed those slices into one official subject consumption.

This design does not reopen ordinal 8, does not alter those terminals,
and does not treat generator-file existence as contract authority.

## 2. Source-authorized contract

A contract is source-authorized only when all seven conditions hold.
Presence of a registered generator, a family name, or a nonempty
envelope is not sufficient.

1. The generator domain matches the semantic goal of the frozen
   behavior family:
   - `INV`: invariant or conservation;
   - `MONO`: monotonicity or order;
   - `CONV`: convergence or limiting behaviour;
   - `DYN`: state, trajectory, or dynamical evolution;
   - `CMP`: comparison, relative relation, or representation
     consistency.
2. The chosen site's public input interface can consume that domain.
   Family-name similarity is not interface evidence.
3. The original, semantic, and syntactic variants accept the same five
   inputs.
4. An original oracle or a metamorphic relation is defined.
5. Input generation, serialization, and invocation adaptation do not
   depend on post-run results.
6. The authority is frozen before any specific applicable site is
   opened.
7. Ordinal-8 NumPy invocation logic is not used as proof that another
   project is executable.

Conditions 2 and 6 can hold together only when a pre-outcome, cohort-wide
static rule already proves that every site matching the rule consumes
the same domain. If that proof requires the first-applicable site, a
repository URL, a symbol, a span, or an invented family-to-generator
table, the contract is not source-authorized.

`build_contract_inputs()` can emit five `E_CONTRACT` rows from a already
frozen `{contract_id, generator_id, domain, site_id}` object. That
function is an envelope seam, not authority. The five production
generators implement only `generate(schema_bytes, seed) -> envelope`.
They contain no invocation, no oracle, and no C, Fortran, or C++
calling convention.

## 3. Frozen inputs this design used

Allowed static inputs actually read:

- the approved prospective multiproject design and the v2 successor /
  stopping-rule design;
- the ordinal-8 partial contract-authority design and module;
- `contract-generator-registry.json` and the five generator modules;
- `slot_inventory.py` and `data/p3_v3/phase2/slot-inventory.json`;
- the applicability predicate registry and implementation;
- PBF / `public_schemas` structural definitions in
  `bridge_and_frames.py`;
- `freeze_production_contracts` and the production pipeline terminals;
- successor build-descriptor `ecosystem` and `language_family`;
- `site_policy.md` E_CONTRACT rules, operator-catalogue family
  meanings, and analysis-spec §11.2;
- cohort-wide PBF category and `schema_kind` counts, plus key structure,
  for the 14 successor frames.

Inventory mechanisms are the frozen values. They are not assumed to be
only `TF` and `SI`. The construction-mechanism axis is:

`MECHANISM_ORDER = ("CE", "OS", "HP", "TF", "SI")`

For subject index `i` in the sorted 35-subject projection and slot
ordinal `o` in `{0, 1}`:

`mechanism = MECHANISM_ORDER[(i + o) % 5]`

That formula matches every inventory row of ordinals 9–22 (0 mismatches).
All five mechanisms appear. Mechanism records how a later patch may be
shaped. It does not select a contract generator, domain, oracle, or
invocation.

Descriptor identity, not a selection key:

| ecosystem / language_family | successor count |
|---|---|
| cmake / c | 8 |
| cmake / fortran | 3 |
| autotools / c | 2 |
| cmake / cpp | 1 |

Cohort-wide PBF structure for ordinals 9–22, with no path, symbol, or
span values read:

| aggregate | value |
|---|---|
| frames | 14 |
| row total | 6346 |
| `public_schemas` total | 434 |
| site objects | 333097 |
| row `schema_kind` field | absent on every row |
| `public_schemas.schema_kind` | `CLI_TOKEN_GRAMMAR_V1` only (434/434) |
| `CONTRACT_*` kinds | 0 |
| `NUMERIC_ARRAY_DOMAIN_V1` | 0 |
| `JSON_SCHEMA_DRAFT2020_12_V1` | 0 |
| `TEXT_IO_SCHEMA_V1` | 0 |
| subjects with `PUBLIC_API` rows | 14/14 |
| subjects with `CLI` rows | 10/14 |
| subjects with `EXAMPLE` rows | 13/14 |
| subjects with `BENCHMARK` rows | 10/14 |
| subjects with `PROJECT_TEST` rows | 14/14 |
| subjects with any `public_schemas` kind other than `CLI_TOKEN_GRAMMAR_V1` | 0/14 |

Site object keys are exactly
`{path, symbol, start_line, start_col, end_line, end_col}`.
`public_schemas` keys are exactly
`{provenance_path, provenance_span_or_key, raw_schema, schema_kind}`.

Not read: any concrete site path, symbol, or span; predicate results;
first-applicable site; source bytes; issue, PR, patch, reveal, or
mutation outcomes; profiling outcomes; ordinal-8 kill or survival as a
contract-selection reason.

## 4. Comparison of schemes A, B, and C

### 4.1 Scheme A: pre-outcome cohort-wide contract policy

Scheme A would bind generator and domain from fields knowable before any
site outcome: frozen family, frozen mechanism, PBF category, and
`schema_kind`. The rule would be constant across repository, ordinal,
site, and run result.

Scheme A is the preferred candidate and was evaluated first. It does not
hold.

Why it is not executable as source-authorized authority:

1. Family names and generator identifiers occupy different namespaces.
   Applicability uses E_COMMON kinds
   (`NUMERIC_ARRAY_DOMAIN_V1`, `JSON_SCHEMA_DRAFT2020_12_V1`,
   `TEXT_IO_SCHEMA_V1`, `CLI_TOKEN_GRAMMAR_V1`). Contract generators
   accept only `CONTRACT_*_DOMAIN_V1` domain objects. No frozen mapping
   from E_COMMON kind to contract domain exists.
2. The 14 successor frames contain none of the E_COMMON kinds that
   `INV` and `MONO` require, and none of the five contract kinds. The
   only published schema kind is `CLI_TOKEN_GRAMMAR_V1`.
3. cmake and autotools adapters emit `PUBLIC_API` as
   `HEADER_SURFACE_V1` and do not place those objects in
   `public_schemas`. `attach_schema_kind()` therefore cannot attach
   `NUMERIC_ARRAY_DOMAIN_V1` or `JSON_SCHEMA_DRAFT2020_12_V1` to a
   successor `PUBLIC_API` row. That is adapter structure, not a site
   outcome. It still does not authorize a contract; it only shows that
   an `INV`/`MONO` plus `CONTRACT_ARRAY_DOMAIN_V1` rule would have no
   static schema to consume.
4. Mechanism never enters generator selection in the frozen protocol.
   Using `CE`/`OS`/`HP`/`TF`/`SI` as a generator key would invent a
   rule that the inventory does not state.
5. Condition 2 requires a consumable public interface. First-applicable
   site is a runtime predicate result and is unknown before official
   close. A cohort-wide rule that ignores interface evidence fails
   condition 2. A rule that waits for the chosen site fails condition 6.
6. Conditions 3 and 4 require a shared five-input calling convention and
   an oracle. The five generators produce envelopes only. The only
   existing oracles are ordinal-8 `CHOLESKY_RECONSTRUCTION_V1` and
   `PYTHON_SUFFIX_PROJECTION_V1`. Transferring them violates condition 7
   and the ordinal-8 design's own refusal to invent a `MONO` premise.
7. Domain parameters (`matrix_size`, suffix lists, enum values) are not
   present in successor `public_schemas`. Inventing them is not
   pre-outcome source authority.

Rejected tempting A variant: bind `CMP` plus `CLI_TOKEN_GRAMMAR_V1` to
`CONTRACT_SEQUENCE_DOMAIN_V1` because all 14 frames carry that kind and
ordinal 8 used sequence inputs for `CMP`. That binding is invalid.
`CLI_TOKEN_GRAMMAR_V1` is `{kind, program, tokens, vocabulary}`. The
sequence generator requires
`{accepted_suffixes, rejected_suffixes, entry_count}` and emits
filename entries. The ordinal-8 oracle is Python suffix projection of
`.py` / `.pyi`. That is NumPy `get_test_cases` authority, not a
cohort-wide C, Fortran, or C++ CLI contract. Adopting it would be
exactly the family-name and outcome-transfer error this task forbids.

An honest empty-always A policy would be cohort-wide and pre-outcome,
but it would leave nonempty source-authorized contracts deterministically
unreachable. That is not
`PROSPECTIVE_CONTRACT_AUTHORITY_DESIGN_READY`.

Scheme A is therefore rejected. The rejection is a proof that no
legal nonempty mapping exists from the allowed frozen fields, not a
preference for a later version.

### 4.2 Scheme B: repository or ecosystem-wide adapter policy

Scheme B would be allowed only if one rule applied to every matching
site in a repository or ecosystem and an existing static authority
already stated that rule. A 14-row URL or site table is forbidden.

Scheme B does not hold.

1. `CMAKE_CTEST_V1` and `AUTOTOOLS_MAKECHECK_V1` are Public Behavior
   Frame discovery adapters. They enumerate tests, executables, headers,
   and sites. They are not contract, oracle, or paired-execution
   adapters.
2. Shared ecosystem does not imply a shared consumable domain. cmake/c
   covers distinct public surfaces. The descriptors were read only as
   identity metadata and are not selection keys.
3. No existing static authority says that every matching site in a
   successor repository consumes `CONTRACT_ARRAY_DOMAIN_V1`,
   `CONTRACT_SEQUENCE_DOMAIN_V1`, or any other contract domain.
4. Writing one rule per originating repository would be a six-row
   project table. Writing one rule per ordinal would be a fourteen-row
   table. Both are the project-special mapping this task forbids.
5. Even a genuine ecosystem-wide CLI grammar rule would still lack an
   original oracle, a three-variant invocation seam, and domain bytes
   that the sequence or enum generators can consume. Scheme B would
   still collapse to guessing an interface.

Scheme B is therefore rejected. It is not hidden outcome-adaptive
selection, because no legal static adapter authority exists to hide.

### 4.3 Scheme C: new two-stage prospective slice

Scheme C is the remaining legal path.

Stage I freezes source identity and the existing-authority 10-slot
applicability observation. It does not freeze contracts. It does not
write `SITE_ELIGIBLE_NO_AUTHORIZED_CONTRACT` as a final paired-evidence
ineligibility. It does not consume a successor as a paired-evidence
unit. It does not write the official or staging namespace of
`p3-c3-prospective-multiproject-paired-slice-v1`.

After Stage I observations for the opened ordinals are fully disclosed,
a new version may establish contract and pair authority from those
disclosed observations plus any still-frozen pre-outcome fields. That
later authority is a new prospective version. It is not a resume or
retry of the current Slice B.

Stage II, under that new version only, may freeze source-authorized
contracts and then run paired evidence. Pair and runner design remain
out of this task.

Scheme C is required because A and B both need either an invented
interface or a look at a specific applicable site. Principle 4 forbids
retreating to a family-to-generator table in order to avoid a new
version.

### 4.4 Choice

| scheme | falsifiable | executable without site outcome | makes nonempty source-authorized contract possible now | decision |
|---|---|---|---|---|
| A | yes | no, not as a nonempty source-authorized policy | no | rejected |
| B | yes | no; no cohort-wide adapter authority | no | rejected |
| C | yes, by later version identity and disclosure | Stage I yes; Stage II only after disclosure | not under current Slice B; possible only after a new version | selected |

Unique terminal: `TWO_STAGE_PROSPECTIVE_SLICE_REQUIRED`.

This is not `CONTRACT_AUTHORITY_DESIGN_INFEASIBLE`. Two-stage work
remains inside the current research range: the approved design already
separated applicability search from later contract freeze, and no
successor has been consumed. Infeasibility would require that even a
new version after disclosed Stage I observations could not be stated.
That claim is not available, because those observations have not been
disclosed.

## 5. Why the current Slice B cannot legally continue

The current prospective version is
`p3-c3-prospective-multiproject-paired-slice-v1`. Its production
entry is `process_production_subject()` /
`run_production_subject_pipeline()`.

That version cannot continue as Slice B for four independent reasons.

1. Nonempty contracts are deterministically unreachable. The freeze
   seam returns `()`. Filling it inside this version would require
   exactly the A or B authority that this design proved absent.
2. Official one-shot consumption is irreversible.
   `SITE_ELIGIBLE_NO_AUTHORIZED_CONTRACT` and
   `ALL_SLOTS_NOT_APPLICABLE` are written as subject terminals. The
   stopping rule then forbids scientific retry. Running Slice B now
   would exhaust ordinals 9–22 as funnel terminals and permanently
   block the approved Slice C path ("contract/mutant freeze on found
   distinct projects").
3. Same-version repair after seeing applicability is forbidden. If
   Stage I-like closures were obtained under v1 and contracts were then
   added, the added authority would be outcome-adaptive inside one
   prospective version.
4. Pair or runner implementation would not restore reachability. Those
   seams are unreachable while contracts remain empty. Implementing
   them now would continue the deviation already named
   `CONTRACT_AUTHORITY_REQUIRED_BEFORE_SLICE_B`.

`SITE_ELIGIBLE_NO_AUTHORIZED_CONTRACT` remains a lawful scientific
funnel code after a frozen authority has been applied and has returned
no legal contract. It is not lawful as a disguise for "no authority
exists yet". Under the current version the empty freeze is an
authority gap, not a completed source-authorized decision. The correct
hold is the inherited terminal
`CONTRACT_AUTHORITY_REQUIRED_BEFORE_SLICE_B`, not an official funnel
write.

Current Slice B is therefore closed to further official progress. The
closure is prospective-version-specific. It does not rewrite the
already approved scientific objective (two new non-NumPy
`PAIRED_EVIDENCE_COMPLETE` projects). It requires a new two-stage
version instead of a resume.

## 6. Five-generator authority audit

Each row is the production `generate(schema_bytes, seed)` interface.
None of the five modules authorizes a successor contract.

| generator | input object shape | families it could serve if a source already stated that domain | static interface evidence required before authorization | authorizable without opening a specific site | invocation / oracle seam | executable contract, or data only |
|---|---|---|---|---|---|---|
| `CONTRACT_ENUM_DOMAIN_V1` | domain `{values: nonempty list}`; payload `{value}` | a family whose source-stated domain is a discrete public enumeration | a public schema or declaration that the site consumes one value from that enumeration | no; successor PBFs contain no enum domain and no `CONTRACT_ENUM_*` kind | none | data only |
| `CONTRACT_NUMERIC_DOMAIN_V1` | domain `{lower, upper}` with `lower < upper`; payload `{value}` | a family whose source-stated domain is a scalar interval | a public numeric parameter the site consumes as a scalar | no; no successor `NUMERIC_ARRAY` or numeric contract kind; interval bounds would be invented | none | data only |
| `CONTRACT_ARRAY_DOMAIN_V1` | domain `{matrix_size in [2,8], diagonal_min > 0, off_diagonal_max >= 0}`; payload SPD `{matrix}` | only an `INV` (or similar conservation) site that source-states reconstruction or an equivalent matrix invariant | a public matrix-shaped interface plus a stated reconstruction or conservation oracle | no; that is the ordinal-8 Cholesky template; successor frames have zero `NUMERIC_ARRAY_DOMAIN_V1` and zero `CONTRACT_ARRAY_*` | none in the generator; the only oracle is `CHOLESKY_RECONSTRUCTION_V1` | data only; executable only under the forbidden NumPy transfer |
| `CONTRACT_SEQUENCE_DOMAIN_V1` | domain `{accepted_suffixes, rejected_suffixes, entry_count}`; suffixes must start with `.`; payload `{entries}` filename list | only a `CMP` site that source-states suffix or membership projection over filenames | a public interface that consumes filename entries and a stated projection oracle | no; `CLI_TOKEN_GRAMMAR_V1` is argv grammar, not suffixes; the only oracle is `PYTHON_SUFFIX_PROJECTION_V1` | none in the generator | data only; executable only under the forbidden NumPy transfer |
| `CONTRACT_RELATION_PAIR_DOMAIN_V1` | domain `{lower, upper, integer: bool}`; payload ordered `{left, right}` | only a `MONO` site that source-states an order or monotonicity relation | a public interface that consumes an ordered pair and a stated order oracle | no; the ordinal-8 design already refused this for a typing fixture that stated no order; a generic pair would supply the missing premise | none | data only |

Shared audit conclusions:

- Registry membership proves only that envelope generation is
  allowlisted.
- `schema_kind` on each registry entry equals the generator id. That
  kind never appears in the 14 successor `public_schemas`.
- `build_contract_inputs()` will generate five rows once a domain is
  supplied. Supplying the domain is the authority step that A and B
  cannot perform.
- No generator contains an invocation or oracle seam. A later pair or
  runner cannot be presumed.

## 7. Ten family / mechanism slots

Each successor has ten inventory rows: five families times two slot
ordinals. Mechanism is taken from inventory, not from a `TF`/`SI`
assumption. Across ordinals 9–22 the observed slot-0 / slot-1 pairs
are `(HP, TF)`, `(SI, CE)`, `(TF, SI)`, `(CE, OS)`, and `(OS, HP)`.
Every family therefore appears with every mechanism.

The contract-authority verdict does not depend on mechanism. Mechanism
is a later construction-shape permission. The table below is the
required ten-slot matrix. For each family the two rows are slot
ordinal 0 and slot ordinal 1. The mechanism column is the inventory
rule, not a generator key.

| family | slot ordinal | inventory mechanism | allowed generator candidates | pre-outcome applicability predicate that would authorize a contract | required static PBF / schema evidence | terminal when no authority | nonempty contract on current 14 successors | status |
|---|---|---|---|---|---|---|---|---|
| INV | 0 | `MECHANISM_ORDER[(i+0)%5]` | none | none | a source-stated conservation domain plus a consumable public interface; E_COMMON `NUMERIC_ARRAY_DOMAIN_V1` or `JSON_SCHEMA_DRAFT2020_12_V1` would be necessary even to pass the existing applicability predicate, and those kinds are absent from all 14 frames | empty freeze; must not be written as official `SITE_ELIGIBLE_NO_AUTHORIZED_CONTRACT` under current v1 | unreachable under A/B | proved unreachable under A/B; possible only after a new version |
| INV | 1 | `MECHANISM_ORDER[(i+1)%5]` | none | none | same as INV / 0; mechanism does not change the domain | same | unreachable under A/B | proved unreachable under A/B; possible only after a new version |
| MONO | 0 | `MECHANISM_ORDER[(i+0)%5]` | none | none | a source-stated order relation; `CONTRACT_RELATION_PAIR_DOMAIN_V1` is not a substitute for that statement; `NUMERIC_ARRAY_DOMAIN_V1` is also absent | same | unreachable under A/B | proved unreachable under A/B; possible only after a new version |
| MONO | 1 | `MECHANISM_ORDER[(i+1)%5]` | none | none | same as MONO / 0 | same | unreachable under A/B | proved unreachable under A/B; possible only after a new version |
| CONV | 0 | `MECHANISM_ORDER[(i+0)%5]` | none | none | a source-stated convergence or limiting contract; no registered generator encodes residual, iteration, or tolerance; token intersection on a later-opened symbol is a site outcome, not authority | same | unreachable under A/B | proved unreachable under A/B; possible only after a new version |
| CONV | 1 | `MECHANISM_ORDER[(i+1)%5]` | none | none | same as CONV / 0 | same | unreachable under A/B | proved unreachable under A/B; possible only after a new version |
| DYN | 0 | `MECHANISM_ORDER[(i+0)%5]` | none | none | a source-stated trajectory or evolution contract; no registered generator encodes time, state, or integrator inputs; path-token intersection is a site outcome | same | unreachable under A/B | proved unreachable under A/B; possible only after a new version |
| DYN | 1 | `MECHANISM_ORDER[(i+1)%5]` | none | none | same as DYN / 0 | same | unreachable under A/B | proved unreachable under A/B; possible only after a new version |
| CMP | 0 | `MECHANISM_ORDER[(i+0)%5]` | none | none | a source-stated comparison or representation-consistency domain that the public interface consumes; `CLI_TOKEN_GRAMMAR_V1` is argv grammar and does not match any contract generator domain | same | unreachable under A/B | proved unreachable under A/B; possible only after a new version |
| CMP | 1 | `MECHANISM_ORDER[(i+1)%5]` | none | none | same as CMP / 0 | same | unreachable under A/B | proved unreachable under A/B; possible only after a new version |

Reading notes:

- "Proved unreachable under A/B" is a statement about source-authorized
  contracts, not a predicate result. This task did not run
  applicability predicates and did not identify a first-applicable
  site.
- `CONV`, `DYN`, and `CMP` may still become `SITE_FROZEN` under the
  existing applicability authority, because those predicates do not
  require the missing E_COMMON kinds. That possibility is why running
  current Slice B is unsafe: a `SITE_FROZEN` slot plus an empty freeze
  would consume the subject.
- `INV` and `MONO` have an additional structural gap: the existing
  predicates require schema kinds that successor frames do not publish.
  That gap is not a contract authorization, and it is not an official
  `ALL_SLOTS_NOT_APPLICABLE` result.

## 8. Authority seam and proposed files

The unique existing production seam remains:

```text
freeze_production_contracts(
    binding: FrozenSubjectBinding,
    closures: Sequence[SlotClosureRecord],
    repo_root: Path,
) -> tuple[AuthorizedContract, ...]
```

Under the current version this seam must keep returning `()` after
registry validation. It must not be filled with a family-to-generator
table, a repository table, a site table, or ordinal-8 templates.

`AuthorizedContract` already stores
`slot_id`, `contract_id`, `generator_id`, `site_id`, and `input_ids`.
`build_contract_inputs()` already emits five canonical `E_CONTRACT`
rows from a frozen contract object. Canonical hashes already use
`P3-CONTRACT-v1` and `P3-E-CONTRACT-INPUT-v1`. Slot closure already
exists. No second contract registry, no second ledger, and no new
manifest are authorized.

This task adds no artifact, schema, or manifest. A new SHA-binding
file would not create the missing interface or oracle evidence. The
only file produced here is this design document.

The next design task, not this one, names the two-stage slice identity
and its observation namespace. Constraints that task must inherit:

- do not reuse
  `data/p3_v3/phase3/prospective-multiproject-paired-slice-v1` or
  `.staging` as an observation namespace;
- do not implement `freeze_production_contracts` inside current v1;
- do not create a parallel contract-generator registry;
- if a later version needs one new authority artifact, it must justify
  why the existing registry cannot express the missing interface and
  oracle evidence, name exactly one file, reuse the existing
  self-hash convention, name exactly one consumer seam, and state the
  deletion condition;
- pair authority and runner authority stay separate from contract
  authority.

## 9. Stopping rule and no-retry

Consistency with the approved stopping rule:

1. Contract authority for a paired-evidence version must be frozen
   before that version's official Slice B equivalent runs.
2. `SITE_ELIGIBLE_NO_AUTHORIZED_CONTRACT` means: a frozen authority was
   applied and produced no legal contract. It does not mean
   "implementation missing" and does not mean "authority not yet
   designed".
3. If a later version's authority supports a slot and the production
   implementation is absent, the failure is
   `CONTRACT_AUTHORITY_REQUIRED` or an implementation failure, not
   `SITE_ELIGIBLE_NO_AUTHORIZED_CONTRACT`.
4. Applicability results must not be used to patch contracts inside
   the same prospective version.
5. A formally consumed subject cannot be resumed or retried. Current
   v1 has consumed none. Opening official v1 now would start
   consumption and close the legal two-stage path.
6. `NO_SCIENTIFIC_RETRY` remains the retry policy inside each version.
   A new version is not a retry of an old consumed subject. It is a
   new prospective identity with its own official namespace.
7. Infrastructure absence must not be labelled scientific
   ineligibility.

## 10. Scientific reachability and why READY is refused

The READY terminal required a pre-outcome, cohort-wide, implementable
authority that makes a nonempty source-authorized contract possible
for at least one real successor before official run. That bar is not
met.

Falsification status of the READY checklist against A/B:

1. A production-shaped synthetic subject can be driven
   `SITE_FROZEN -> nonempty envelope -> pair-construction seam` by
   inventing a domain. That would prove only that
   `build_contract_inputs()` works. It would not prove a
   source-authorized successor contract. Synthetic green is therefore
   not used as a READY argument.
2. Contract count and canonical order cannot be defined without a
   generator and domain. Empty is the only current deterministic
   count.
3. The same frozen input currently always yields zero `E_CONTRACT`
   rows. That is deterministic emptiness, not authorized generation.
4. Mismatched static authority already returns empty rather than
   guessing. That fail-closed behaviour is retained and is not READY.
5. Malformed or identity-conflict inputs already fail closed.
6. This design did not read kill, survival, or overlap.
7. Authority existence was judged without executing a real successor.

READY is refused because conditions 2, 4, and 6 of the
source-authorized definition cannot be satisfied from the allowed
frozen fields. TWO_STAGE is selected instead of disguising an empty or
guessed mapping as READY.

Nonempty source-authorized contracts remain deterministically
unreachable under current Slice B. They become possibly reachable only
after Stage I disclosure and a new-version contract authority. That
later possibility is not current paired evidence.

## 11. Two-stage slice boundary

This section is a scientific boundary, not an implementation plan and
not a controller. The next task must design the version. This task
must not implement it.

### 11.1 Stage I: applicability observation version

Purpose: freeze source identity and the existing 10-slot applicability
observation for ordinals that the new version opens.

Allowed products:

- recovered source identity already authorized by the existing
  recovery seam;
- ten slot closures under the existing applicability authority;
- an observation record that a subject had zero or more `SITE_FROZEN`
  slots.

Forbidden products:

- any contract object;
- any `E_CONTRACT` inventory;
- any pair, mutant, or runner artifact;
- any write to
  `data/p3_v3/phase3/prospective-multiproject-paired-slice-v1` or
  `.staging`;
- `SITE_ELIGIBLE_NO_AUTHORIZED_CONTRACT` as a paired-evidence subject
  terminal;
- treating "no contract yet" as final subject ineligibility;
- consuming the successor as a paired-evidence unit.

Stage I may stop under a stop rule that the next design must state.
That stop rule may not be "first `SITE_FROZEN` becomes the contract
site" and may not be "empty contract is ineligibility".

### 11.2 Disclosure barrier

After Stage I, the observation set is disclosed as prior information
for a new version. Disclosure is mandatory before any contract
authority that reads site identity, symbol, span, joined row, or
first-applicable result. The current task has not crossed that
barrier.

### 11.3 Stage II: new paired-evidence version

Purpose: apply a new-version contract authority, then pair and execute
only if that authority produces a source-authorized contract.

Requirements:

- new prospective slice identity;
- new official namespace;
- contract authority frozen before Stage II official run;
- no resume of current v1;
- no retry of a subject that Stage II itself later consumes;
- pair and runner remain separately authorized;
- C3 remains `blocked` until RQ2 paired evidence and uncertainty
  accounting actually exist.

Stage II may still return `SITE_ELIGIBLE_NO_AUTHORIZED_CONTRACT` after
its own frozen authority is applied. That code would then be a
completed scientific funnel, not an authority gap.

### 11.4 What this task does not decide

The next design task decides Stage I stop rules, observation schema,
version identifiers, and whether Stage II is one version or two. It
must not reopen A or B as a way to avoid disclosure. It must not
implement a controller in the design task itself.

## 12. Claim ceiling

| item | value |
|---|---|
| `C3_SEMANTIC_CONSTRUCT_DISTINCTNESS` | `blocked` |
| upgrade condition | `RQ2 paired evidence and uncertainty accounting complete` |
| claim ledger | `research/evidence/p3_claim_ledger_v1.3.0.yml`, unmodified |
| ledger SHA-256 | `bf4979662697b2d0565bb70eec88b22673e84bee93b61234555342efb4082a68` |
| successor paired evidence | none |
| n_projects for RQ2 clustering | still 1 (ordinal 8 only) |
| current Slice B | must not start |
| new family-to-generator table | forbidden |
| new contract registry / ledger / manifest | not created |

## 13. Exclusions actually kept

This task did not:

- implement `freeze_production_contracts`;
- write tests;
- write a registry, authority artifact, or authorization file;
- run an applicability predicate;
- open a real site path, symbol, or span;
- construct a mutant;
- implement pair or runner logic;
- run Slice B;
- modify the claim ledger;
- create official or staging directories;
- transfer ordinal-8 NumPy contracts.

## 14. Design self-review

- No open design placeholders remain.
- No repository or site special case is used as authority.
- No outcome-adaptive rule is proposed inside current v1.
- Generator existence is not treated as contract legality.
- No runner is implied to exist.
- Old Slice B facts are unchanged.
- C3 remains blocked.
- Paired evidence has not been produced.
- READY is not claimed from the existence of this file.

## 15. Unique next task

`P3_C3_TWO_STAGE_PROSPECTIVE_PAIRED_SLICE_DESIGN`

That task designs the new two-stage prospective version. It must not
implement the controller, must not start Stage I, and must not fill
`freeze_production_contracts` on current v1.
