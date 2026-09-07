# Supplemental R3 Amendment 01 Bootstrap Execution Addendum 02 Design

## Purpose

Bootstrap Execution Addendum 02 authorizes one new Cursor cloud execution
under the already audited Supplemental R3 Amendment 01 governance. It replaces
only the failed run-environment assumptions exposed by the two terminated
bootstrap executions:

1. the platform starts at fixed main
   `3c518b8467f74c9a6efd11f2db267f9f30e1c822`, not directly at immutable
   authority `31a4a8249f4ba6de12ba92291ab0cd55a65043b4`; and
2. a nominally new Cursor execution cannot assume that a globally fixed path
   under `/tmp` is absent.

Addendum 02 is a new one-time protocol instance. It does not resume, repair,
clean, or rerun either prior execution.

## Root-Cause Finding

The Addendum 01 plan simultaneously required:

- the fixed journal path
  `/tmp/supplemental-r3-amendment-01-bootstrap-addendum-01-command-journal.jsonl`;
- exclusive creation of that file; and
- permanent termination if the file already existed.

The observed first failure was exactly the exclusive-create collision. The
instruction contained no session-specific namespace and no permitted way to
distinguish a stale file, a reused VM snapshot, or an earlier initializer
invocation. Therefore the root cause is the protocol's fixed-path freshness
assumption, not the journal implementation and not the evidence pipeline.

Deleting, renaming, truncating, or reusing the existing journal would repair or
resume failed state and is forbidden. Changing to another fixed filename would
repeat the same design error.

## Chosen Design: One Atomic Runtime-Root Allocation

After every immutable-authority and baseline assertion passes, but before any
test/code edit or journal initialization, the new VM executes exactly one
standard-library allocation command. That command uses `tempfile.mkdtemp` to
atomically create a private empty directory beneath `/tmp` with prefix
`supplemental-r3-a01-bootstrap-addendum-02-` and prints one canonical JSON
record containing its absolute path.

The allocator's internal collision avoidance is one filesystem allocation
operation, not an operational retry. The command is never invoked twice. A
nonzero result, malformed output, non-`/tmp` path, symlink, wrong mode,
nonempty directory, or reused path is the run's first failure.

The exact emitted path becomes `RUNTIME_ROOT`. It is copied literally into
subsequent argv; shell variables, command substitution, environment-variable
inheritance, and a fixed pointer file are forbidden. These paths are derived:

- journal: `RUNTIME_ROOT/command-journal.jsonl`;
- candidate root: `RUNTIME_ROOT/candidate`;
- RED report: `RUNTIME_ROOT/red-report.json`;
- GREEN report: `RUNTIME_ROOT/green-report.json`.

The Addendum 01 fixed journal path may appear only as inert text in synthetic
negative-test fixtures. No operational command may access it. The old path may
exist, but it remains outside the execution-input closure and must not be read,
listed, resolved, deleted, renamed, truncated, or used as evidence.

## Authority and Bootstrap Closure

The platform gate remains the audited Addendum 01 sequence:

1. confirm a brand-new Cursor cloud VM/conversation and exact model
   `Grok 4.5 High Fast` before shell;
2. require initial HEAD `3c518b8467f74c9a6efd11f2db267f9f30e1c822`;
3. require a clean status and canonical `meng004/P3-Semantic-Mutation` origin;
4. record configured fetch-refspec text without enumerating refs;
5. execute one exact fetch of
   `refs/heads/codex/phase3-supplemental-r3-ref-isolation-amendment`;
6. require the fetched identity
   `31a4a8249f4ba6de12ba92291ab0cd55a65043b4`;
7. create a new Addendum 02 branch directly at that authority; and
8. verify the exact ancestry, authority tree, original R2 tree/634 paths,
   admission-sheet blob/hash, and frozen inputs one command at a time.

Only after those checks pass is `RUNTIME_ROOT` allocated. A failure before the
command-journal initializer remains transcript-only. No failed path is cleaned.

## Protocol Identity and Lineage

Canonical identities are:

- protocol:
  `SUPPLEMENTAL_R3_EVIDENCE_AMENDMENT_01_BOOTSTRAP_ADDENDUM_02`;
- inherited amendment ID: `AMENDMENT_01_REF_ISOLATION`;
- bootstrap addendum ID: `BOOTSTRAP_EXECUTION_ADDENDUM_02`;
- branch:
  `cursor/grok-phase3-supplemental-r3-amendment-01-bootstrap-addendum-02-evidence`.

The new instruction binds both prior audited plan hashes:

- original Amendment 01 plan:
  `7adda5c7df3b792ba112e3348d64434d6543d867d339d5e301d2b096119ceac5`;
- Bootstrap Addendum 01 plan:
  `7363445ea67618e9f5bb378a0b45eaad07ed4c57f9fcce87323d99a1a6d59c5b`.

The final Local Desktop audit supplies the Addendum 02 plan hash separately in
the initiating Cursor message. All three hashes flow through bootstrap
projection, pre-network seal, verification log, and handoff.

The instruction excludes:

- the historical failed conversation associated with commit
  `743f5552fd5912f2705f7f256dda0f5179393842`;
- terminated session `bc-9bcdda05-3350-49aa-b4c6-c60fbb236f30`; and
- the terminated Addendum 01 conversation that produced the
  `journal path already exists` terminal report, even though its session ID was
  not supplied to Local Desktop.

## Inherited Scientific and Governance Constraints

Addendum 02 does not change:

- Batch 3 exclusion loaded only from frozen SCOPE/manifest after the authority
  switch, with no deny literal embedded in commands or tests;
- prohibition on global ref/object inventory and on inspecting unrelated stale
  refs;
- complete original R2 path, byte, mode, symlink, blob, and tree identity;
- frozen R2 state 67 total / 9 pending / 58 excluded;
- fixed GPyTorch/chaospy/SALib shortfall vector 2/3/3;
- no replacement, cross-repository substitution, issue/fix reuse, or quota
  reinterpretation;
- node-by-node RED followed by the same GREEN matrix;
- command-runner spy and stale-ref rename invariance tests;
- no production evidence request before the pre-network seal;
- one acquisition pass and first-failure terminal behavior; and
- no readiness, r8, canonical/admission freeze, PR, merge, rebase,
  cherry-pick, downstream analysis, or `rtk` in Cursor commands.

## Failure Semantics

Every Task 1 command is followed by its assertion before the next command.
Before `shutdown_runner_armed=true`, a failure preserves only the Cursor
transcript and successfully created runtime root/journal; it performs no
diagnostic repository edit, commit, push, cleanup, or second command. After the
runner is armed, the audited path-isolated diagnostic publication remains
available only before candidate publication. After candidate publication or a
payload commit, failures perform no diagnostic repository mutation or push.

The runtime root and everything under it are never cleaned on failure. This
preserves provenance and avoids turning cleanup into repair. A first Addendum
02 failure consumes the one-time authorization and cannot be retried in another
VM.

## Required Regression Coverage

In addition to every Addendum 01 test family, the RED/GREEN manifest must cover:

1. a pre-existing Addendum 01 fixed journal path has no effect and receives
   zero read/write/delete/resolve spy calls;
2. the allocator is called exactly once after all authority gates and before
   any test/code edit or journal initialization;
3. the returned runtime root is absolute, under `/tmp`, prefix-bound, private,
   empty, nonsymlink, and unique;
4. allocator failure is terminal and produces no cleanup or fallback path;
5. unresolved `RUNTIME_ROOT`, shell expansion, path drift, root reuse,
   nonempty/symlink roots, and fixed fallback paths are rejected;
6. every external artifact path shares the one literal resolved root;
7. journal initialization succeeds when unrelated old fixed paths exist and
   fails only if its newly allocated root is internally contaminated before
   initialization; and
8. bootstrap projection, seal, verification, failure record, payload, and
   handoff bind the allocation argv/output and all three plan hashes.

## Success Criteria

The successful history remains authority -> code/test -> pre-network seal ->
complete 2/3/3 payload -> sole direct-child handoff. It is pushed once without
force and stops with verdict
`SUPPLEMENTAL_R3_AMENDMENT_01_BOOTSTRAP_ADDENDUM_02_EVIDENCE_HANDOFF_PENDING_LOCAL_AUDIT`.

The only failure verdict is
`SUPPLEMENTAL_R3_AMENDMENT_01_BOOTSTRAP_ADDENDUM_02_BLOCKED_FIRST_FAILURE`.
Neither verdict changes paper claims or admits evidence before the later Local
Desktop audit.
