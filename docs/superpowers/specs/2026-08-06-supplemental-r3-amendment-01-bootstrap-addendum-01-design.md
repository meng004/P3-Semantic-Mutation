# Supplemental R3 Amendment 01 Bootstrap Execution Addendum 01 Design

## Purpose

Bootstrap Execution Addendum 01 creates a new, independently authorized Cursor
cloud execution under the already audited Supplemental R3 Amendment 01
governance. It preserves
`31a4a8249f4ba6de12ba92291ab0cd55a65043b4` as the immutable evidence authority
while accommodating Cursor's observed platform checkout at fixed main commit
`3c518b8467f74c9a6efd11f2db267f9f30e1c822`.

This Addendum is a new protocol instance, not a retry, repair, continuation, or
resumption of either the historical failed `743f5552...` execution or the
terminated Amendment 01 Cursor session
`bc-9bcdda05-3350-49aa-b4c6-c60fbb236f30`.

## Authority and Bootstrap Closure

The new Cursor cloud VM must begin with all of these platform-provisioned
facts:

- model `Grok 4.5 High Fast`;
- repository `meng004/P3-Semantic-Mutation`;
- initial HEAD exactly `3c518b8467f74c9a6efd11f2db267f9f30e1c822`;
- empty worktree and index;
- canonical origin URL for that repository;
- configured fetch refspec text recorded without enumerating refs; and
- a brand-new VM and conversation whose session identity differs from both
  failed sessions.

Before any shell command, the user must provide this exact authorization:

```text
AUTHORIZE SUPPLEMENTAL_R3_EVIDENCE_AMENDMENT_01_BOOTSTRAP_ADDENDUM_01 FROM 31a4a8249f4ba6de12ba92291ab0cd55a65043b4 VIA PLATFORM_HEAD 3c518b8467f74c9a6efd11f2db267f9f30e1c822
```

The bootstrap records and validates the initial HEAD, status, origin URL, and
configured fetch refspec text one at a time. Each next command is permitted only
after the preceding command and its assertion pass; any mismatch is terminal.

After those checks pass, exactly one fetch is allowed:

```bash
git fetch --no-tags origin refs/heads/codex/phase3-supplemental-r3-ref-isolation-amendment:refs/remotes/origin/codex/phase3-supplemental-r3-ref-isolation-amendment
```

The fetched ref must resolve exactly to
`31a4a8249f4ba6de12ba92291ab0cd55a65043b4`. The VM then creates the new local
branch
`cursor/grok-phase3-supplemental-r3-amendment-01-bootstrap-addendum-01-evidence`
directly from that immutable SHA. The fetch is the sole authorized construction
of the Addendum execution closure. No other ref may be fetched, listed,
resolved, or used as input.

## Inherited Constraints

The Addendum supersedes only Amendment 01's requirement that the
platform-provisioned initial HEAD already equal the immutable authority, its
associated prohibition on using the single exact fetch to construct the
execution closure, and the cross-instance no-reexecution clause solely to
authorize one fresh Addendum bootstrap sequence. This does not resume or rerun
the failed session: no command is issued in it, no state is copied from it, and
no evidence request from it is repeated. All other Amendment 01 requirements
remain binding:

- Batch 3 deny identity is loaded only from frozen inputs, absent from active
  ancestry and payload lineage, and never passed to Git;
- no global ref or object inventory and no inspection or mutation of unrelated
  stale refs;
- byte-, path-, mode-, symlink-, blob-, and tree-identity of all original R2
  material;
- exact GPyTorch/chaospy/SALib shortfall vector 2/3/3 with no substitutions;
- node-by-node RED followed by the same GREEN matrix;
- injected command-runner spy and stale-ref rename invariance tests;
- no production evidence request before the pre-network seal;
- exactly one acquisition pass and no retries;
- first operational failure permanently terminates the Addendum run;
- no readiness, r8, canonical/admission freeze, PR, merge, rebase,
  cherry-pick, downstream analysis, or scientific count change; and
- no `rtk` prefix in Cursor VM commands.

The Amendment 01 failure report is external historical provenance only. It is
not copied into the repository, used as execution state, or presented as an
input to the Addendum code or evidence pipeline.

## Protocol Isolation

All new protocol identities and writable run-specific artifacts use Addendum
names. At minimum:

- protocol:
  `SUPPLEMENTAL_R3_EVIDENCE_AMENDMENT_01_BOOTSTRAP_ADDENDUM_01`;
- inherited amendment ID: `AMENDMENT_01_REF_ISOLATION`;
- bootstrap addendum ID: `BOOTSTRAP_EXECUTION_ADDENDUM_01`;
- parent locked execution-plan SHA-256:
  `7adda5c7df3b792ba112e3348d64434d6543d867d339d5e301d2b096119ceac5`;
- Bootstrap Addendum execution-plan SHA-256: supplied by the final Local
  Desktop audit as a separate line in the initiating Cursor message and bound
  by the bootstrap projection, pre-network seal, verification log, and handoff;
- branch:
  `cursor/grok-phase3-supplemental-r3-amendment-01-bootstrap-addendum-01-evidence`;
- candidate root:
  `/tmp/supplemental-r3-amendment-01-bootstrap-addendum-01-candidate`;
- journal:
  `/tmp/supplemental-r3-amendment-01-bootstrap-addendum-01-command-journal.jsonl`;
- bootstrap log:
  `BOOTSTRAP_COMMANDS_AMENDMENT_01_BOOTSTRAP_ADDENDUM_01.json`;
- first-failure record:
  `FIRST_FAILURE_AMENDMENT_01_BOOTSTRAP_ADDENDUM_01.json`;
- command log: `COMMAND_LOG_AMENDMENT_01_BOOTSTRAP_ADDENDUM_01.json`;
- verification log:
  `VERIFICATION_LOG_AMENDMENT_01_BOOTSTRAP_ADDENDUM_01.json`; and
- pre-network seal:
  `PRE_NETWORK_AUTHORITY_AMENDMENT_01_BOOTSTRAP_ADDENDUM_01.json`.

Original R3 files, Amendment 01 files, the blocked Amendment 01 execution
identity, and all R2 files are read-only. No Addendum failure path may overwrite
earlier failure provenance.

## Failure Semantics

Every bootstrap assertion is evaluated immediately after the command that
supplies it. If the initial HEAD is not exactly `3c518b...`, execution stops
before status, origin, refspec, or fetch commands. If status is dirty, execution
stops before origin inspection. If origin is wrong, execution stops before
refspec inspection. If the configured refspec cannot be recorded or is empty,
execution stops before the sole fetch. Because SCOPE is unavailable at the
platform HEAD, the deny comparison is deferred until after the exact authority
switch and is then performed textually against the captured refspec output. The
configured text is provenance only; it never widens the single exact fetch
command authorized by this Addendum.

A Task 1 failure writes no repository file, creates no commit, and performs no
push. Later failures retain Amendment 01's pre-publication diagnostic-only and
post-publication no-write rules, but use only Addendum artifact names. No failed
Addendum command or check may be retried in the same or another VM. A first
Addendum failure consumes this one-time cross-instance authorization.

## Success Structure

The successful history remains linear:

1. immutable authority `31a4a824...`;
2. Addendum code/test commit;
3. Addendum pre-network seal commit;
4. complete 2/3/3 payload commit; and
5. sole direct-child handoff commit.

The branch is pushed once without force and then the VM stops. The only success
verdict is
`SUPPLEMENTAL_R3_AMENDMENT_01_BOOTSTRAP_ADDENDUM_01_EVIDENCE_HANDOFF_PENDING_LOCAL_AUDIT`.
The only failure verdict is
`SUPPLEMENTAL_R3_AMENDMENT_01_BOOTSTRAP_ADDENDUM_01_BLOCKED_FIRST_FAILURE`.

## Acceptance Criteria

The final Cursor instruction is acceptable only if an independent audit proves
that it:

1. binds the two excluded failed sessions and prohibits their reuse;
2. admits only the exact `3c518b...` platform start and exact one-fetch
   transition to `31a4a824...`;
3. preserves every Batch 3, R2, 2/3/3, RED/GREEN, command-spy, stale-ref,
   atomicity, and fail-stop constraint;
4. renames every writable run-specific path and protocol identity to the
   Addendum while keeping inherited inputs read-only;
5. contains no readiness, r8, canonical freeze, PR, merge, retry, or resume
   authorization; and
6. binds both the parent locked plan SHA and its own separately supplied
   SHA-256 lock before any execution authorization.
