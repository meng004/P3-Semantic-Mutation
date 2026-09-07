# Supplemental R3 Amendment 01 Bootstrap Addendum 03 A+ Design

## Purpose

Bootstrap Addendum 03 A+ replaces the repeatedly failing build-and-execute
architecture with a two-stage, evidence-gated workflow:

1. Local GPT Desktop builds, tests, freezes, and independently audits a complete
   execution bundle without issuing any production evidence request.
2. One brand-new Cursor cloud VM verifies that exact bundle and performs only
   environment admission, pre-network sealing, object collection, screening,
   payload verification, and handoff.

The next Cursor VM must not write production code or tests. Its first live
GraphQL request occurs only after the bundle, immutable scientific authority,
VM environment, command journal, and pre-network seal have all passed.

## Root-Cause and Architectural Finding

Three one-time Cursor executions have terminated before evidence collection:

1. the original Amendment 01 plan assumed the platform checkout started at
   immutable authority `31a4a8249f4ba6de12ba92291ab0cd55a65043b4`, but the
   platform supplied `3c518b8467f74c9a6efd11f2db267f9f30e1c822`;
2. Bootstrap Addendum 01 used a globally fixed journal path with
   exclusive-create semantics, and that path already existed; and
3. Bootstrap Addendum 02 atomically allocated a unique runtime root but required
   the entire root to remain empty while simultaneously requiring large Task 1
   outputs to be preserved for bootstrap projection. Cursor materialized four
   helper outputs into that root and correctly failed the empty-root invariant.

The third failure is not merely another filename defect. The governing
architecture asked a single fail-once VM to perform bootstrap, creatively build
an unproven acquisition system, establish RED/GREEN evidence, and conduct the
irreversible experiment. Any ordinary development mistake consumed the only
execution authorization. Adding another narrow exception would leave the same
structural risk in place.

## Supersession Boundary

Addendum 03 A+ inherits Supplemental R3 Amendment 01, Bootstrap Addendum 01,
and Bootstrap Addendum 02 except for these two provisions:

- it replaces Addendum 02's whole-runtime-root emptiness rule with a typed,
  allowlisted bootstrap spool and a journal-target-absence rule; and
- it replaces in-VM code/test authoring with a locally built, immutable,
  independently audited execution bundle.

It does not change Batch 3 exclusion, scientific authority, frozen inputs,
R2 identity, repository quotas, screening rules, evidence endpoints, first-live-
failure semantics, terminal payload structure, or downstream prohibitions.

## Canonical Identities

- Scientific authority:
  `31a4a8249f4ba6de12ba92291ab0cd55a65043b4`.
- Platform initial HEAD:
  `3c518b8467f74c9a6efd11f2db267f9f30e1c822`.
- Protocol:
  `SUPPLEMENTAL_R3_EVIDENCE_AMENDMENT_01_BOOTSTRAP_ADDENDUM_03`.
- Inherited amendment ID: `AMENDMENT_01_REF_ISOLATION`.
- Bootstrap addendum ID: `BOOTSTRAP_EXECUTION_ADDENDUM_03`.
- Local bundle branch:
  `codex/supplemental-r3-amendment-01-execution-bundle-a03`.
- Future Cursor evidence branch:
  `cursor/grok-phase3-supplemental-r3-amendment-01-bootstrap-addendum-03-evidence`.

The final bundle commit SHA, bundle tree SHA, bundle manifest SHA-256, and
Addendum 03 plan SHA-256 are intentionally assigned only after local
construction and independent audit. The future launch packet must contain
their exact values; none may be a runtime-discovered moving target. The launch
packet's own SHA-256 is recorded only in the external Local Desktop audit
record after packet composition; it is not embedded in itself.

The locked plan lineage is:

- original Amendment 01 plan SHA-256
  `7adda5c7df3b792ba112e3348d64434d6543d867d339d5e301d2b096119ceac5`;
- Bootstrap Addendum 01 plan SHA-256
  `7363445ea67618e9f5bb378a0b45eaad07ed4c57f9fcce87323d99a1a6d59c5b`;
- Bootstrap Addendum 02 plan SHA-256
  `98fe5a3a73b1b38e9a061174a2142a0fe8b3e14d24e39d8af1c412b6af04ca36`;
  and
- the future Bootstrap Addendum 03 plan SHA-256 supplied after its independent
  Local Desktop audit.

To avoid a hash cycle, the bundle manifest binds this design SHA-256 and the
three already frozen parent-plan hashes, but not the not-yet-written Addendum 03
plan hash. After the bundle and its audits are frozen, the Addendum 03 plan
binds the exact design, bundle commit/tree/manifest, and bundle-audit report
hashes. The later VM seal, verification log, payload, and handoff bind that
complete chain plus the fourth Addendum 03 plan hash, without embedding the
Batch 3 deny identity.

## Permanently Excluded Execution State

The following are immutable failure provenance and may not be resumed, retried,
repaired, cleaned, copied, cherry-picked, or used as bundle or experiment input:

- the failed conversation associated with commit
  `743f5552fd5912f2705f7f256dda0f5179393842`;
- terminated session `bc-9bcdda05-3350-49aa-b4c6-c60fbb236f30`;
- the terminated Addendum 01 journal-collision conversation; and
- terminated Addendum 02 session
  `bc-1368031b-b5fa-43c2-9074-c49b862ca08e`, including runtime root
  `/tmp/supplemental-r3-a01-bootstrap-addendum-02-fvuyvctg` and all four helper
  files reported beneath it.

No local or Cursor command may inspect, delete, rename, truncate, hash, list, or
otherwise access any failed runtime path. The user-supplied terminal reports
remain external audit inputs and are not copied into scientific artifacts.

## Stage A: Local Execution-Bundle Construction

### Isolation and lineage

Local GPT Desktop creates a fresh isolated worktree and new bundle branch
directly from scientific authority. All local shell commands use `rtk`. No file
from a failed Cursor branch, worktree, runtime root, or conversation is reused.

The immutable bundle history is linear and has three commits:

1. **RED test commit** — adds only tests, the complete node manifest, and the
   deterministic test runner. Production acquisition modules are absent. Every
   listed node is run independently and must fail only for its bound missing
   production symbol or behavior.
2. **GREEN implementation commit** — adds the minimum production modules. The
   identical node manifest runs GREEN, followed by the complete repository test
   suite and `git diff --check`.
3. **Bundle-seal commit** — adds only the canonical execution-bundle manifest,
   local RED/GREEN logs, dependency/environment identity, ordered file hashes,
   and authority/R2/frozen-input checks.

The bundle branch is not merged and receives no PR. It is pushed only after all
local checks and both independent audits pass. The exact terminal commit is the
only bundle ref target authorized for the future Cursor fetch.

### Local networking boundary

Bundle construction may use normal dependency or Git transport needed for
local development, but every production Supplemental R3 evidence endpoint is
blocked by injected spies. The evidence-request counter must remain zero across
RED, GREEN, full-suite, replay, and audit runs. Tests use only synthetic bytes
and frozen repository fixtures.

No GitHub issue/fix GraphQL query, browser lookup, REST fallback, search query,
or manual evidence collection is permitted during Stage A.

### Bundle contents

The successful bundle may add only:

- `scripts/external_slice/supplemental_r3_common.py`;
- `scripts/external_slice/supplemental_r3_bootstrap.py`;
- `scripts/external_slice/mine_supplemental_r3.py`;
- `scripts/external_slice/check_supplemental_r3_admission.py`;
- `scripts/external_slice/check_supplemental_r3_handoff_hashes.py`;
- the four Supplemental R3 test modules;
- the Addendum 03 node manifest and deterministic RED/GREEN runner;
- `EXECUTION_BUNDLE_AMENDMENT_01_BOOTSTRAP_ADDENDUM_03.json`;
- `LOCAL_RED_LOG_AMENDMENT_01_BOOTSTRAP_ADDENDUM_03.json`;
- `LOCAL_GREEN_LOG_AMENDMENT_01_BOOTSTRAP_ADDENDUM_03.json`.

It contains no live raw response, discovered issue, review queue, screening
decision, candidate sheet, admission evidence, payload, handoff, readiness,
r8, freeze, reproducer, mutation, or downstream artifact.

### Frozen scientific state

Every bundle commit must preserve byte-for-byte and path-for-path:

- the complete original Supplemental R3 frozen inputs and failed-run
  provenance at authority;
- R2 tree object `2e8fe75233bed73c9facb1c66b5d72b6a172487d`, all 634
  tracked paths, modes, symlink targets, and bytes;
- `data/external_slice/admission_sheet.csv` blob
  `5ef073d4d6297639695491c46d20733236bede52` and SHA-256
  `77f729b1297ef24d4223d5277b093c93ad84711dfbbe69a1927398d49d387a0a`;
- frozen R2 state 67 total / 9 `ADMIT_PENDING_REPRO` / 58 excluded; and
- blank aliases and `analysis_id`, with A2 remaining `PENDING`.

## Stage A Test and Audit Requirements

The local RED/GREEN matrix must cover every inherited family and these
Addendum 03 regressions:

1. the future VM performs no code or test edit;
2. verifier fixtures require an exact bundle commit/tree/manifest and support
   the complete four-plan lineage; the actual Stage A seal binds the frozen
   design and three existing parent plans, while the later execution plan/VM
   supplies the fourth hash without a cycle;
3. the bundle commit chain is linear, direct from authority, and contains no
   merge or unlisted commit;
4. a one-byte synthetic mutation of any design/plan/bundle/source/test/log/
   manifest binding fails before any evidence request;
5. the bootstrap allocator is called once and yields a private nonsymlink
   runtime root under `/tmp`;
6. the pre-journal tree may contain only `bootstrap-spool/`, and that directory
   may contain only the canonical summary described below;
7. the journal target, candidate root, RED/GREEN report paths, and all payload
   paths must be absent before initialization;
8. an existing unrelated old fixed journal or failed runtime path has no effect
   and receives zero spy accesses;
9. any extra spool entry, symlink, hard link, wrong type, path escape, changed
   hash, second allocator, alternate root, fallback path, or unresolved token is
   terminal;
10. journal initialization imports the early transcript exactly once, creates
    the journal exclusively, fsyncs it, and permits no unjournaled later
    command;
11. every later command uses the same literal runtime root;
12. the command-runner spy rejects retries, shell interpolation, forbidden Git
    access, and post-failure commands;
13. renaming an unrelated synthetic stale ref leaves verdict and ordered
    command trace byte-identical;
14. the Batch 3 deny value is loaded only from frozen SCOPE/manifest and is
    absent from active inputs, ancestry, payload, and handoff lineage;
15. R2 path/byte/tree/mode/symlink and admission-sheet drift fail;
16. GPyTorch/chaospy/SALib stop independently at exactly 2/3/3 with no
    replacement or cross-repository transfer;
17. snapshot -> queue -> decision -> candidate sheet -> evidence bindings fail
    on every one-field mutation;
18. failure shutdown is reachable and unique at pre-journal, post-journal,
    pre-seal, live-request, candidate-publication, payload, handoff, and push
    boundaries; and
19. readiness, r8, canonical/admission freeze, PR, merge, rebase, cherry-pick,
    reproducer, mutation, and downstream commands or artifacts are rejected.

Two independent reviewers audit the frozen bundle:

- a specification reviewer checks scientific/governance inheritance and
  evidence bindings; and
- an operational reviewer checks command reachability, journal/spool state,
  first-failure shutdown, network counts, and terminal Git history.

Both must return PASS with no findings against the same frozen commit and tree.
Their reports remain Local Desktop external attestations so they cannot create
a self-referential audited commit. The final launch packet binds both report
hashes, the frozen bundle commit, and the frozen bundle tree. A mechanical
post-audit verifier proves the reports name that exact commit/tree and that the
bundle bytes did not move during review.
Any finding reopens Stage A locally; it does not consume a Cursor execution
authorization because no production evidence request or evidence VM exists.

## Stage B: Evidence-Only Cursor VM

### Session gate

The future run requires one brand-new Cursor cloud VM and one brand-new Cursor
conversation using exactly Grok 4.5 High Fast. Cursor commands never use `rtk`.
The first message contains one exact Addendum 03 authorization sentence and the
frozen hashes for all parent plans, the Addendum 03 plan, bundle commit, bundle
tree, bundle manifest, and external bundle-audit reports.

No prior authorization carries forward. The first Addendum 03 operational
failure consumes the new one-time authorization.

### Minimal bootstrap

The VM performs only this pre-runner sequence, with each assertion evaluated
before the next command:

1. verify platform HEAD, clean status, canonical origin, and nonempty configured
   fetch-refspec text;
2. execute one exact no-tags fetch of the audited bundle ref;
3. require the fetched commit, tree, manifest, and linear parents to equal the
   launch packet, with the RED test commit directly descending from scientific
   authority;
4. create the new evidence branch directly at the bundle-seal commit;
5. verify clean status plus the short authority-tree, R2-tree,
   admission-sheet-blob, and bundle-manifest identity outputs only;
6. allocate one private runtime root; and
7. materialize the canonical early-command summary in the controlled spool and
   initialize the bundled command runner/journal exactly once.

There is no source edit, test edit, package installation, exploratory shell
command, repair, or retry in Stage B.

The 634-path R2 listing, per-file byte/mode checks, and complete frozen-file
SHA-256 verification run only after journal initialization through the bundled
runner. No long-output helper extraction is needed before the journal exists.

### Controlled bootstrap spool

The runtime root is atomically created once with prefix
`supplemental-r3-a01-bootstrap-addendum-03-` beneath `/tmp`, mode `0700`, and
must initially be empty and nonsymlink.

Before journal initialization, the only permitted tree is:

```text
RUNTIME_ROOT/
└── bootstrap-spool/
    └── task1-command-summary.json
```

`bootstrap-spool` is a real directory beneath the runtime root. The summary is
a canonical regular JSON file constructed from the Cursor transcript and
contains every pre-runner argv, ordered stdout/stderr hashes, raw exits,
immediate assertion verdicts, UTC bounds, session/model identity, all locked
hashes, and zero evidence-request count. It contains no Batch 3 deny literal.

The bundled initializer validates the exact tree and summary, rejects every
additional entry or alternate spelling, and exclusively creates
`RUNTIME_ROOT/command-journal.jsonl`. It imports the pre-runner records, fsyncs
them, appends its own result, and then makes every later shell/Git/test/network
operation pass through the frozen command runner. The spool remains immutable
and its byte hash is carried through the VM seal, verification log, payload,
and handoff.

The whole runtime root is deliberately not required to be empty. The invariant
is instead exact typed membership plus absence of every not-yet-created target.
This directly prevents recurrence of the Addendum 02 failure.

### Direct path to experiment

After journal initialization, the VM runs the frozen GREEN matrix and full
suite once against the exact audited bundle. The handoff binds both the local
test-only RED commit/log and the local plus VM GREEN runs. This preserves a
mechanical RED -> GREEN proof without asking the evidence VM to develop code.

The VM then creates and commits its environment-specific pre-network seal. The
seal proves zero evidence requests, exact authority/bundle lineage, complete
command provenance, unchanged R2 and frozen inputs, and the allocated
runtime/spool binding.

The immediately following operation is the single live acquisition process.
No additional implementation, readiness, exploratory analysis, or pre-study
task intervenes.

## Live Collection and Screening

The single acquisition process uses only the three frozen GraphQL documents.
It fully traverses discovery connections, derives membership locally, removes
frozen R2/canonical collisions, and reviews rows in frozen repository order.

Repository stops remain independent and fixed:

- GPyTorch: 2 new distinct admits;
- chaospy: 3 new distinct admits; and
- SALib: 3 new distinct admits.

There is no replacement, over-yield transfer, cross-repository substitution,
issue reuse, fix reuse, quota reinterpretation, or repeated evidence request.
A scientifically excluded row is retained and the frozen queue may proceed to
its next row; an operational request/command/invariant failure terminates the
entire run immediately.

## Failure and Success Semantics

Before journal initialization, failure preserves only the Cursor transcript and
permitted spool bytes; it performs no repository diagnostic edit, commit, push,
cleanup, or second command. After initialization, the frozen runner records the
first failure and becomes terminal. Diagnostic publication is allowed only if
the locally tested shutdown runner is armed and no candidate payload has been
published. After candidate publication or payload commit, failure performs no
diagnostic commit or push.

No failed command, test, checker, Git operation, evidence request, row request,
or insufficient-yield outcome is retried, resumed, repaired, or continued in
the same or another VM.

Success produces an environment-seal commit, a complete payload commit, and a
sole direct-child handoff commit, followed by one non-force push and immediate
termination. It creates no PR and performs no merge.

## Research-Evidence Boundary

The bundle, VM seal, payload, and handoff are evidence infrastructure and
candidate evidence only. They do not change manuscript claims or scientific
admission automatically. The only success verdict is
`SUPPLEMENTAL_R3_AMENDMENT_01_BOOTSTRAP_ADDENDUM_03_EVIDENCE_HANDOFF_PENDING_LOCAL_AUDIT`.

Only a later, separately authorized Local Desktop evidence audit may classify
individual claims as supported, observed, qualified, insufficient, or blocked.
No readiness, r8, canonical/admission freeze, reproducer, mutation, prediction,
detection, downstream analysis, manuscript edit, PR, or merge is authorized.

## Acceptance Criteria

Addendum 03 A+ is ready for a new Cursor VM only when all of the following are
true:

1. the three-commit local bundle exists directly above authority and contains
   no live evidence;
2. local node-by-node RED and identical GREEN are hash-bound and independently
   replayable;
3. all local tests, frozen-input checks, R2 checks, command-spy cases, and
   Addendum 03 spool regressions pass;
4. two independent audits return PASS against one frozen bundle commit/tree;
5. the complete Cursor execution plan is frozen and independently audited;
6. the launch packet embeds the exact plan and all fixed hashes;
7. the user separately authorizes one new Addendum 03 Cursor VM; and
8. the VM instruction contains no development task before the live collection
   process.
