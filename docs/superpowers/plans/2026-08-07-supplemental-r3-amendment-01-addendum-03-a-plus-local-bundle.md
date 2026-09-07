# Supplemental R3 Amendment 01 Addendum 03 A+ Local Bundle Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:executing-plans` to execute this plan task-by-task,
> `superpowers:using-git-worktrees` before creating the isolated bundle branch,
> `superpowers:test-driven-development` for implementation, and
> `superpowers:verification-before-completion` before each commit and handoff.
> Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and independently audit a frozen, zero-evidence-request
Supplemental R3 execution bundle so the next Cursor VM performs no development
and proceeds from verified bootstrap directly to collection and screening.

**Architecture:** A new isolated worktree starts exactly at immutable scientific
authority `31a4a8249f4ba6de12ba92291ab0cd55a65043b4`. A test-only RED commit is
followed by a minimum GREEN implementation commit and a bundle-seal commit.
The bundle reuses only frozen authority inputs and general R2 implementation
patterns; it copies no file or state from a failed Supplemental R3 execution.

**Tech Stack:** Python 3.11+, pytest, canonical JSON/CSV, SHA-256, Git, GitHub
GraphQL through `gh api graphql`, and POSIX atomic filesystem operations. Every
Local Desktop shell command in this plan is prefixed with `rtk`.

## Global Constraints

- Frozen A+ design SHA-256:
  `c6f950f01f3def9d6aad32e29bb8af9ae1bf7a8dd1bc4ef68c1b0ffe5a780820`.
- Scientific authority:
  `31a4a8249f4ba6de12ba92291ab0cd55a65043b4`.
- R2 tree object:
  `2e8fe75233bed73c9facb1c66b5d72b6a172487d`, exactly 634 tracked paths.
- Canonical admission sheet blob/SHA-256:
  `5ef073d4d6297639695491c46d20733236bede52` /
  `77f729b1297ef24d4223d5277b093c93ad84711dfbbe69a1927398d49d387a0a`.
- Parent plan SHA-256 values:
  `7adda5c7df3b792ba112e3348d64434d6543d867d339d5e301d2b096119ceac5`,
  `7363445ea67618e9f5bb378a0b45eaad07ed4c57f9fcce87323d99a1a6d59c5b`,
  and `98fe5a3a73b1b38e9a061174a2142a0fe8b3e14d24e39d8af1c412b6af04ca36`.
- Bundle branch:
  `codex/supplemental-r3-amendment-01-execution-bundle-a03`.
- Isolated worktree:
  `/Users/limeng/Papers/P3-SemanticMutation/.worktrees/supplemental-r3-a03-bundle`.
- No production Supplemental R3 evidence request is allowed in this local
  plan. Every GraphQL/REST/browser/manual evidence path is blocked by spies;
  `evidence_request_count` remains zero.
- Do not inspect, copy, clean, or reuse failed commit/session/runtime state,
  including `743f5552fd5912f2705f7f256dda0f5179393842`,
  `bc-9bcdda05-3350-49aa-b4c6-c60fbb236f30`,
  `bc-1368031b-b5fa-43c2-9074-c49b862ca08e`, or
  `/tmp/supplemental-r3-a01-bootstrap-addendum-02-fvuyvctg`.
- Load the Batch 3 deny identity only from frozen SCOPE and compare it with the
  frozen manifest. Never embed a second literal in source, tests, logs, bundle
  manifest, plan, payload, or handoff.
- Preserve all original R3 contracts/queries/provenance and every original R2
  path, byte, mode, symlink target, and tree object.
- Preserve R2 state 67 total / 9 `ADMIT_PENDING_REPRO` / 58 excluded, A2
  `PENDING`, and blank aliases/`analysis_id`.
- Fixed shortfall remains GPyTorch 2 / chaospy 3 / SALib 3 independently, with
  no replacement, cross-repository substitution, over-yield transfer, issue
  reuse, or fix reuse.
- No readiness, r8, canonical/admission freeze, reproducer, mutation,
  prediction, detection, downstream analysis, manuscript edit, PR, merge,
  rebase, or cherry-pick.
- The bundle branch may be pushed once only after both independent audits pass.
  It is never merged and no PR is created.

---

## File Structure

### RED test commit

| Path | Responsibility |
| --- | --- |
| `tests/external_slice/test_supplemental_r3_ref_isolation.py` | Bundle lineage, bootstrap spool, journal, command-runner spy, stale-ref rename, Batch 3 closure |
| `tests/external_slice/test_mine_supplemental_r3.py` | Frozen GraphQL transport, pagination, raw hashes, phrase membership, collision and independent stop cases |
| `tests/external_slice/test_check_supplemental_r3_admission.py` | Five-layer binding, decisions, R2 immutability, atomic publication, forbidden-output guards |
| `tests/external_slice/test_check_supplemental_r3_handoff_hashes.py` | Seal/payload/handoff ancestry, path sets, hashes, terminal command contract |
| `tests/external_slice/supplemental_r3_bootstrap_addendum_03_tdd_nodes.json` | Exact ordered node IDs and RED failure signatures |
| `tests/external_slice/run_supplemental_r3_bootstrap_addendum_03_tdd_matrix.py` | One-node-at-a-time RED/GREEN runner with request-count and skip/error rejection |

### GREEN implementation commit

| Path | Responsibility |
| --- | --- |
| `scripts/external_slice/supplemental_r3_common.py` | Canonical serialization, hashing, frozen-input checks, path guard, terminal command runner and atomic publication helpers |
| `scripts/external_slice/supplemental_r3_bootstrap.py` | Bundle verification, early-summary/spool validation, exclusive journal initialization and VM pre-network sealing |
| `scripts/external_slice/mine_supplemental_r3.py` | Single-process discovery, issue/fix capture, queue-order screening and candidate-tree construction |
| `scripts/external_slice/check_supplemental_r3_admission.py` | Independent replay, decisions, quotas, R2 freeze, candidate verification and transactional publication |
| `scripts/external_slice/check_supplemental_r3_handoff_hashes.py` | Staged payload, direct-child handoff, terminal history and hash verification |

### Bundle-seal commit

| Path | Responsibility |
| --- | --- |
| `data/external_slice/supplemental_r3/EXECUTION_BUNDLE_AMENDMENT_01_BOOTSTRAP_ADDENDUM_03.json` | Canonical authority/design/parent-plan/file/environment/test-log manifest |
| `data/external_slice/supplemental_r3/LOCAL_RED_LOG_AMENDMENT_01_BOOTSTRAP_ADDENDUM_03.json` | Ordered independent RED node results and zero-request proof |
| `data/external_slice/supplemental_r3/LOCAL_GREEN_LOG_AMENDMENT_01_BOOTSTRAP_ADDENDUM_03.json` | Identical GREEN node results, full-suite result and zero-request proof |

Audit reports remain outside the bundle commit to avoid self-reference. The
later Addendum 03 execution plan binds their hashes.

---

### Task 1: Create and Prove the Isolated Authority Worktree

**Files:**
- Create: isolated worktree only; no repository file.
- Read: authority tree and frozen R3/R2 inputs.

**Interfaces:**
- Consumes: immutable authority and clean local repository metadata.
- Produces: clean bundle branch rooted exactly at authority.

- [ ] **Step 1: Verify branch/worktree absence**

Run read-only checks for the exact worktree path and bundle branch. A
pre-existing path or branch is not deleted or reused; stop and report it.

- [ ] **Step 2: Create the worktree once**

```bash
rtk git worktree add -b codex/supplemental-r3-amendment-01-execution-bundle-a03 /Users/limeng/Papers/P3-SemanticMutation/.worktrees/supplemental-r3-a03-bundle 31a4a8249f4ba6de12ba92291ab0cd55a65043b4
```

- [ ] **Step 3: Verify authority and clean state**

```bash
rtk git rev-parse HEAD
rtk git status --porcelain=v1
rtk git rev-parse HEAD^{tree}
rtk git rev-parse HEAD:data/external_slice/supplemental_r2
rtk git ls-tree -r --name-only HEAD data/external_slice/supplemental_r2
rtk git rev-parse HEAD:data/external_slice/admission_sheet.csv
```

Require HEAD equals authority, status is empty, authority tree equals
`a993c5537680358870e1dfaf9614a3c31b9f42d6`, R2 tree and 634-path count match
Global Constraints, and the admission-sheet blob matches. Record outputs in the
Local Desktop transcript; create no repository log yet.

### Task 2: Write the Complete Lazy-Import RED Contract

**Files:**
- Create: all six RED-test-commit files listed in File Structure.
- Production files: absent.

**Interfaces:**
- Consumes: only frozen repository bytes and synthetic in-memory fixtures.
- Produces: a complete node manifest whose every node has one exact missing
  production symbol/behavior signature.

- [ ] **Step 1: Write bootstrap/ref-isolation tests**

Define lazy imports inside test bodies and cover:

- exact bundle commit/tree/manifest and linear authority -> RED -> GREEN -> seal
  ancestry;
- one exact fetch and rejection of alternate/wildcard/second fetches;
- no code/test/package-install command in the future VM trace;
- one `mkdtemp` allocation with private nonsymlink root;
- exact pre-journal tree
  `bootstrap-spool/task1-command-summary.json` and absence of journal,
  candidate and report paths;
- canonical early summary, exclusive journal creation, fsync, contiguous
  sequence and literal runtime-root continuity;
- extra entry, symlink, hard link, path escape, alternate root, fallback path,
  unresolved token and second allocation failures;
- command-runner terminal transition and refusal of every later non-shutdown
  command;
- in-memory stale-ref rename invariance with byte-identical ordered spy trace;
- deny loaded once from SCOPE/manifest with no ref/object inventory or targeted
  deny command; and
- zero access to all failed runtime paths.

- [ ] **Step 2: Write transport/miner tests**

Use synthetic GraphQL bytes to cover exact query/variables/raw/manifest hashes;
repository order; discovery pagination; total counts; issue type/state/URL;
complete labels/comments/timeline; independent cursors; complete parents;
phrase matching on only frozen surfaces; cutoff; deduplication; R2/canonical
collisions; queue order; row evidence binding; independent 2/3/3 stops;
exhaustion; no replacement; and one request per page/row.

- [ ] **Step 3: Write admission/publication tests**

Cover A1/A3 biconditional, A2 `PENDING`, blank blind fields, retained scientific
exclusions, `NOT_REVIEWED_AFTER_STOP`, snapshot -> queue -> decision -> sheet ->
evidence one-field mutations, unchanged R2 tree/paths/bytes/modes/symlinks,
canonical-sheet immutability, candidate-root-only construction, transactional
publication rollback at every move boundary, and absence of partial payload.

- [ ] **Step 4: Write handoff/history tests**

Cover bundle-seal -> VM-seal -> payload -> sole direct-child handoff ancestry;
exact staged/path allowlists; SELF resolution; all four plan hashes; design,
bundle and spool bindings; 2/3/3; terminal command predeclaration; one push;
and rejection of readiness/r8/freeze/PR/merge/downstream paths and commands.

- [ ] **Step 5: Write the deterministic matrix runner**

The runner provides these exact modes:

```text
--phase red --manifest PATH --report PATH
--phase green --manifest PATH --report PATH
--verify-log-pair --red-report PATH --green-report PATH
```

For each manifest node it launches exactly one pytest node with `--maxfail=1`,
requires one collected test, and rejects SKIP/XFAIL/collection ERROR/duplicate
node/unrelated failure. RED accepts only the bound missing-production signature;
GREEN requires PASS. Reports are canonical JSON, preserve ordered argv/exits/
stdout/stderr hashes, and assert `evidence_request_count: 0`.

- [ ] **Step 6: Run collection-only validation**

```bash
rtk env PYTHONPATH=src python3 -m pytest --collect-only -q tests/external_slice/test_supplemental_r3_ref_isolation.py tests/external_slice/test_mine_supplemental_r3.py tests/external_slice/test_check_supplemental_r3_admission.py tests/external_slice/test_check_supplemental_r3_handoff_hashes.py
```

Require every manifest node appears exactly once and collection succeeds even
though all five production files are absent.

### Task 3: Capture RED and Create the Test-Only Commit

**Files:**
- Create outside repository: a private temporary RED report.
- Commit: only the six RED files.

**Interfaces:**
- Consumes: complete lazy-import node manifest.
- Produces: immutable test-only commit and canonical RED report bytes.

- [ ] **Step 1: Run the RED matrix once against absent production**

```bash
rtk env PYTHONPATH=src python3 tests/external_slice/run_supplemental_r3_bootstrap_addendum_03_tdd_matrix.py --phase red --manifest tests/external_slice/supplemental_r3_bootstrap_addendum_03_tdd_nodes.json --report /tmp/supplemental-r3-a03-local-red.json
```

The runner must exit zero only after every node produced its exact RED. Confirm
zero evidence requests and no production file was created.

- [ ] **Step 2: Verify and commit tests only**

```bash
rtk git diff --check
rtk git status --porcelain=v1
rtk git add tests/external_slice/test_supplemental_r3_ref_isolation.py tests/external_slice/test_mine_supplemental_r3.py tests/external_slice/test_check_supplemental_r3_admission.py tests/external_slice/test_check_supplemental_r3_handoff_hashes.py tests/external_slice/supplemental_r3_bootstrap_addendum_03_tdd_nodes.json tests/external_slice/run_supplemental_r3_bootstrap_addendum_03_tdd_matrix.py
rtk git commit -m "test(external): define supplemental R3 Addendum 03 execution bundle"
```

Require this commit's sole parent is scientific authority and its changed path
set equals the six test files.

### Task 4: Implement the Common Runner and Bootstrap Boundary

**Files:**
- Create: `scripts/external_slice/supplemental_r3_common.py`.
- Create: `scripts/external_slice/supplemental_r3_bootstrap.py`.
- Test: `tests/external_slice/test_supplemental_r3_ref_isolation.py`.

**Interfaces:**
- Produces:
  `GateError`, `canonical_json_bytes`, `sha256_file`, `atomic_write_bytes`,
  `load_authority_contract`, `verify_frozen_inputs`, `CommandRecord`,
  `TerminalCommandRunner`, `validate_runtime_root`,
  `validate_bootstrap_summary`, `initialize_journal`, `verify_bundle`, and
  `materialize_pre_network_seal`.

- [ ] **Step 1: Implement canonical and immutable-input primitives**

Use byte reads, canonical compact JSON, same-directory temp files, fsync and
`os.replace`. `verify_frozen_inputs` compares manifest hashes, authority Git
objects, the complete R2 634-path manifest including modes/symlink targets and
per-file bytes, and the canonical admission sheet. It rejects untracked files
under R2 and never loads the Batch 3 deny value from any source except SCOPE and
its manifest copy.

- [ ] **Step 2: Implement the argv-only terminal runner**

`TerminalCommandRunner.run(argv: Sequence[str], *, evidence_request: bool)`
uses `shell=False`, records UTC bounds and raw stream hashes, increments the
request counter before an evidence call, fsync-appends JSONL, and becomes
terminal on the first nonzero or invariant failure. It refuses retry keys,
duplicate evidence identities, shell metacharacter transport, forbidden Git
operations, and all commands after failure except the predeclared shutdown
allowlist.

- [ ] **Step 3: Implement typed spool/journal initialization**

`validate_runtime_root` requires a real mode-0700 `/tmp` directory with exact
prefix. `validate_bootstrap_summary` requires the only pre-journal tree to be
the canonical summary under `bootstrap-spool/`, validates its complete early
trace and locked bindings, and confirms all future targets absent.
`initialize_journal` uses `O_CREAT|O_EXCL`, mode 0600, imports ordered records,
fsyncs, records its own completion, and never deletes or rewrites the spool.

- [ ] **Step 4: Implement bundle and seal verification**

`verify_bundle` accepts exact expected commit/tree/manifest arguments and
verifies the three-commit linear chain to authority without global ref/object
enumeration. `materialize_pre_network_seal` binds bundle lineage, environment,
journal prefix, spool hash, VM GREEN result, frozen inputs and zero requests.

- [ ] **Step 5: Run the focused GREEN subset**

```bash
rtk env PYTHONPATH=src python3 -m pytest -q tests/external_slice/test_supplemental_r3_ref_isolation.py
```

### Task 5: Implement Frozen Transport and Single-Pass Mining

**Files:**
- Create: `scripts/external_slice/mine_supplemental_r3.py`.
- Test: `tests/external_slice/test_mine_supplemental_r3.py`.

**Interfaces:**
- Produces:
  `load_frozen_contract`, `GraphQLCommandRunner`, `capture_discovery`,
  `build_issue_snapshot`, `build_review_queue`, `capture_issue_evidence`,
  `capture_fix_evidence`, `apply_repository_stop`, and `execute`.

- [ ] **Step 1: Implement frozen contract/query loading**

Verify exact query byte hashes before construction of any request. Encode
variables as UTF-8 canonical JSON. Reject forbidden transports and increment
the shared runner's evidence count before `gh api graphql`.

- [ ] **Step 2: Implement complete discovery capture**

Traverse `Repository.issues` for each repository in SCOPE order with independent
cursor continuity, raw-byte preservation and page manifests. Validate typename,
repository, CLOSED state, canonical issue URL, cutoff, complete labels and
stable total count. Derive phrase membership locally after terminal pagination.

- [ ] **Step 3: Implement collision and queue construction**

Load R2/canonical collision keys from frozen inputs, exclude every collision,
deduplicate all five uniqueness keys, order deterministically, and assign IDs
from 06/03/01 without consuming an ID twice.

- [ ] **Step 4: Implement issue/fix evidence capture and decision input**

Capture complete comments/timeline and complete commit parents with independent
cursors and raw-byte manifests. Accept one canonical decision record per queue
row, validate all copied fields and A1/A3 decision biconditional, retain
scientific exclusions, and reject EOF/reorder/revision/extra fields.

- [ ] **Step 5: Implement independent repository stops**

Stop only the current repository at 2/3/3, mark later rows
`NOT_REVIEWED_AFTER_STOP`, and fail `DISTRIBUTION_TARGET_AT_RISK` on exhaustion.
Never request substitute evidence or move surplus between repositories.

- [ ] **Step 6: Run the focused GREEN subset**

```bash
rtk env PYTHONPATH=src python3 -m pytest -q tests/external_slice/test_mine_supplemental_r3.py
```

### Task 6: Implement Independent Admission, Publication, and Handoff Checks

**Files:**
- Create: `scripts/external_slice/check_supplemental_r3_admission.py`.
- Create: `scripts/external_slice/check_supplemental_r3_handoff_hashes.py`.
- Test: both corresponding test modules.

**Interfaces:**
- Admission produces:
  `reconstruct_from_raw`, `verify_five_layer_binding`, `verify_quotas`,
  `build_candidate_payload`, `verify_candidate_payload`, and
  `publish_candidate_transactionally`.
- Handoff produces:
  `verify_staged_payload`, `build_handoff`, and `verify_handoff`.

- [ ] **Step 1: Implement independent replay and decisions**

Do not call miner builders. Reconstruct pages, manifests, snapshot, queue,
decisions, sheet and evidence directly from raw bytes/contracts; validate every
hash/order/cursor/collision/stop/uniqueness/blind-field relationship.

- [ ] **Step 2: Implement candidate-only output**

Build all live artifacts beneath the VM-external candidate root. Require exact
2/3/3, unchanged 67/9/58 R2 state, A2 `PENDING`, blank blind fields, and no
forbidden token/path before publication.

- [ ] **Step 3: Implement transactional publication**

Validate the complete mirrored candidate tree first. Move only absent allowed
targets into the repository with a publication journal; on any exception,
restore the exact pre-publication tree inside the same command. Never publish a
partial candidate or any path after terminal failure.

- [ ] **Step 4: Implement staged payload and handoff checks**

Verify exact changed/staged path sets, payload parentage, bundle/plan/design/
spool/journal bindings, direct-child handoff, SELF resolution, 2/3/3 and the
predeclared terminal command sequence. Reject PR/merge/readiness/r8/freeze or
downstream artifacts.

- [ ] **Step 5: Run both focused GREEN subsets**

```bash
rtk env PYTHONPATH=src python3 -m pytest -q tests/external_slice/test_check_supplemental_r3_admission.py tests/external_slice/test_check_supplemental_r3_handoff_hashes.py
```

### Task 7: Capture Complete GREEN and Create the Implementation Commit

**Files:**
- Create outside repository: private GREEN report.
- Commit: only the five production files.

**Interfaces:**
- Consumes: unchanged RED node manifest.
- Produces: minimum implementation commit and canonical GREEN report.

- [ ] **Step 1: Run the identical GREEN matrix**

```bash
rtk env PYTHONPATH=src python3 tests/external_slice/run_supplemental_r3_bootstrap_addendum_03_tdd_matrix.py --phase green --manifest tests/external_slice/supplemental_r3_bootstrap_addendum_03_tdd_nodes.json --report /tmp/supplemental-r3-a03-local-green.json
```

- [ ] **Step 2: Verify RED/GREEN pairing and full suite**

```bash
rtk env PYTHONPATH=src python3 tests/external_slice/run_supplemental_r3_bootstrap_addendum_03_tdd_matrix.py --verify-log-pair --red-report /tmp/supplemental-r3-a03-local-red.json --green-report /tmp/supplemental-r3-a03-local-green.json
rtk env PYTHONPATH=src python3 -m pytest -q
rtk git diff --check
```

All commands must exit zero, both reports must name the same ordered node set,
and every request counter must be zero.

- [ ] **Step 3: Commit production only**

```bash
rtk git add scripts/external_slice/supplemental_r3_common.py scripts/external_slice/supplemental_r3_bootstrap.py scripts/external_slice/mine_supplemental_r3.py scripts/external_slice/check_supplemental_r3_admission.py scripts/external_slice/check_supplemental_r3_handoff_hashes.py
rtk git commit -m "feat(external): implement supplemental R3 Addendum 03 execution bundle"
```

Require the sole parent is the RED commit and the changed path set equals the
five production files.

### Task 8: Materialize and Commit the Bundle Seal

**Files:**
- Create: the three bundle-seal files listed in File Structure.

**Interfaces:**
- Consumes: authority, RED commit/log, GREEN commit/log, environment and exact
  file hashes.
- Produces: immutable bundle-seal commit for independent review.

- [ ] **Step 1: Materialize canonical local logs**

Copy the canonical RED/GREEN report bytes into their repository paths using the
bundled materializer. Do not hand-edit reports.

- [ ] **Step 2: Build the execution-bundle manifest**

The manifest binds design SHA, three parent-plan SHAs, authority/tree, RED and
GREEN commits/parents, ordered test/production hashes, log hashes, Python/
pytest/Git/OS/dependency identities, complete frozen R3 hashes, R2 tree and
634-path byte/mode manifest, canonical-sheet identity, zero network counts,
allowed path sets, future CLI schemas, and limitations. It does not contain the
future Addendum 03 plan hash or audit verdicts.

- [ ] **Step 3: Verify seal consistency**

Run the bundled verifier against the worktree and require no tracked, index,
untracked, path, byte, mode, or tree drift outside the three new seal files.

- [ ] **Step 4: Commit seal only**

```bash
rtk git add data/external_slice/supplemental_r3/EXECUTION_BUNDLE_AMENDMENT_01_BOOTSTRAP_ADDENDUM_03.json data/external_slice/supplemental_r3/LOCAL_RED_LOG_AMENDMENT_01_BOOTSTRAP_ADDENDUM_03.json data/external_slice/supplemental_r3/LOCAL_GREEN_LOG_AMENDMENT_01_BOOTSTRAP_ADDENDUM_03.json
rtk git commit -m "governance(external): seal supplemental R3 Addendum 03 execution bundle"
```

Require the sole parent is the GREEN commit and changed path set equals exactly
the three seal files.

### Task 9: Freeze and Independently Audit the Bundle

**Files:**
- Create outside bundle branch:
  `docs/review_20260807/gate_supplemental_r3_addendum_03_bundle_spec_audit.md`.
- Create outside bundle branch:
  `docs/review_20260807/gate_supplemental_r3_addendum_03_bundle_operational_audit.md`.

**Interfaces:**
- Consumes: one frozen bundle commit/tree and full test output.
- Produces: two external PASS/no-findings reports or a blocked local build.

- [ ] **Step 1: Record frozen identities**

Compute bundle commit, tree and manifest SHA-256 once. Do not edit the worktree
while reviewers run.

- [ ] **Step 2: Run independent specification audit**

Check complete design/scientific inheritance, Batch 3, R2, 2/3/3, transport,
decision, binding, zero-network and downstream boundaries.

- [ ] **Step 3: Run independent operational audit**

Check runtime/spool/journal reachability, exact command interfaces, first-
failure terminal behavior, transactional publication, terminal history and the
absence of development commands in the future VM path.

- [ ] **Step 4: Recompute identities and verify reports**

Both reports must name the same frozen commit/tree and say PASS with no
findings. Any finding is repaired locally with fresh RED/GREEN evidence and a
new frozen bundle; no Cursor authorization is consumed.

### Task 10: Push the Audited Bundle Once and Write the Evidence-Only Cursor Plan

**Files:**
- Create: Addendum 03 Cursor VM execution plan, two plan audit reports and one
  launch packet in the main Local Desktop workspace.
- Remote write: push only the audited bundle branch.

**Interfaces:**
- Consumes: frozen bundle/audit identities.
- Produces: one exact-fetch target and a fully hash-bound evidence-only packet.

- [ ] **Step 1: Push the bundle branch once without force**

```bash
rtk git push -u origin codex/supplemental-r3-amendment-01-execution-bundle-a03
```

Do not create a PR and do not merge.

- [ ] **Step 2: Write the complete Addendum 03 Cursor plan**

Embed exact bundle commit/tree/manifest and bundle-audit hashes. The plan starts
at platform HEAD, performs one exact fetch, verifies the bundle, initializes
the controlled spool/journal, reruns GREEN once, creates the VM seal, and then
immediately begins the single live collection/screening process. It contains no
source/test edit or package installation.

- [ ] **Step 3: Independently audit and freeze the Cursor plan**

Run separate specification and operational reviews against one plan SHA-256.
Require PASS with no findings and a final byte-stability recheck.

- [ ] **Step 4: Compose and verify the launch packet**

The packet includes the exact authorization sentence, Addendum 03 plan hash,
bundle identities, audit-report hashes and the complete byte-identical plan.
Record the packet's own SHA only in the external Local Desktop audit report.
Do not launch Cursor; the user separately starts and authorizes the new VM.

## Completion Gate

Do not claim the bundle or launch packet is ready unless fresh verification
proves all of the following:

1. authority -> RED -> GREEN -> bundle-seal is linear and exact;
2. every RED node failed for its bound reason and the identical node passed
   GREEN;
3. the complete repository suite and bundle verifier pass;
4. evidence request counts are all zero;
5. original R3 and complete R2 are unchanged;
6. two bundle audits and two plan audits independently PASS against stable
   bytes;
7. the pushed remote bundle ref equals the audited commit; and
8. the launch packet's embedded plan hashes to the independently audited plan.

