# Supplemental R3 Amendment 01 Cursor Instruction — Local Desktop Audit

Date: 2026-08-06  
Environment: Local GPT Desktop / GPT-5.6 Sol High  
Immutable authority: `31a4a8249f4ba6de12ba92291ab0cd55a65043b4`  
Instruction: `docs/superpowers/plans/2026-08-06-supplemental-r3-amendment-01-cursor-vm.md`  
Instruction SHA-256: `7adda5c7df3b792ba112e3348d64434d6543d867d339d5e301d2b096119ceac5`

## Verdict

**`PASS_LOCKED_AWAITING_SEPARATE_USER_AUTHORIZATION`**

The instruction is complete and internally executable as a fail-closed
successor to Amendment 01. It is bound to the immutable Local Desktop audit
authority and does not authorize the current task to start Cursor.

This verdict approves only the instruction text. It does not claim that a
Cursor VM exists, that RED or GREEN tests ran, that evidence was requested, or
that a payload or handoff was produced. A later user message must separately
authorize a brand-new Cursor VM and brand-new conversation.

## Authority Replay

| Check | Fixed/observed value | Result |
| --- | --- | --- |
| Authority commit | `31a4a8249f4ba6de12ba92291ab0cd55a65043b4` | PASS |
| Authority tree | `a993c5537680358870e1dfaf9614a3c31b9f42d6` | PASS |
| R2 complete subtree | `2e8fe75233bed73c9facb1c66b5d72b6a172487d` | PASS |
| R2 tracked path count | 634 | PASS |
| Canonical admission-sheet blob | `5ef073d4d6297639695491c46d20733236bede52` | PASS |
| Canonical admission-sheet SHA-256 | `77f729b1297ef24d4223d5277b093c93ad84711dfbbe69a1927398d49d387a0a` | PASS |
| Instruction SHA-256 | `7adda5c7df3b792ba112e3348d64434d6543d867d339d5e301d2b096119ceac5` | PASS |

The original Supplemental R3 contracts, queries, Amendment JSON files,
failure provenance, and R2 collision inputs remain read-only authorities in
the instruction. The instruction does not repeat the Batch 3 deny SHA; future
code/tests/commands must load it from the frozen SCOPE JSON pointer.

## Complete Binding Matrix

| Required boundary | Instruction binding | Result |
| --- | --- | --- |
| Batch 3 exclusion | Exact HEAD ancestry, single fetch target, object/ref access, active-input, literal-occurrence, payload-lineage, and command provenance gates; no global ref inventory | PASS |
| R2 immutability | Whole R2 subtree object, 634-path manifest, bytes/modes/symlinks/untracked checks, canonical sheet blob/hash, pre-network and pre-payload replay | PASS |
| Fixed shortfall | GPyTorch/chaospy/SALib exactly 2/3/3; no replacement, reuse, over-yield reassignment, or cross-repository substitution | PASS |
| True RED -> GREEN | Complete node manifest; node-by-node RED with exact failure signatures; collection masking, skip, unrelated error, or unexpected PASS rejected; same nodes GREEN before live acquisition | PASS |
| Command-runner spy | Injected argv runner, terminal failure state, request counter, forbidden Git operations, and subsequent-command rejection | PASS |
| Stale-ref rename | In-memory ref map; renamed synthetic ref must preserve PASS verdict and byte-identical spy trace without enumeration, resolution, deletion, or object read | PASS |
| First failure / no retry | Designated RED exception only; every operational failure terminal; no retry/resume/repair; bootstrap, pre-publication, transactional publication, and post-publication shutdowns isolated | PASS |
| Payload atomicity | VM-external candidate root, full verification before transactional publication, rollback-on-publication-failure, path-isolated diagnostic commit, and zero push after publication failure | PASS |
| Forbidden successors | Mechanical path/command guards and negative tests cover readiness, r8, canonical freeze, PR creation, merge/rebase/cherry-pick, and force-push | PASS |
| Environment separation | Local commands use `rtk`; every future Cursor command is plain; model is Grok 4.5 High Fast in one new VM/conversation | PASS |
| Failed session isolation | `743f5552fd5912f2705f7f256dda0f5179393842` is immutable provenance only; resume, retry, continuation, work copying, and old-branch execution are forbidden | PASS |
| Separate authorization | Exact authorization sentence required before the first future Cursor shell command; current instruction remains LOCKED | PASS |

## Independent Two-Axis Audit

### Standards axis

**PASS; findings: 0.**

The independent standards reviewer locked and rehashed the final instruction
bytes. It found no documented-standard breach and no judgement-call finding.
It specifically rechecked initial HEAD/dirty handling, Task 1 zero-write
failure, diagnostic `commit --only`, post-publication zero-push behavior,
journal initialization and command wrapping, fixed CLI argv, transactional
rollback, staged allowlist, and mechanical handoff construction.

### Specification axis

**PASS; findings: 0.**

The independent specification reviewer locked and rehashed the same final
instruction bytes. It found every user requirement and every applicable
`31a4a824...` Amendment/R3/R2 authority clause completely bound, with no
missing, partial, contradictory, or scope-creep behavior.

## Static Verification

- Placeholder scan: no `TBD`, `TODO`, deferred implementation marker, or
  unresolved SHA/path placeholder.
- Markdown fence and trailing-whitespace scan: clean.
- Cursor bash-prefix scan: no `rtk` command inside a Cursor `bash` block.
- Batch 3 occurrence scan: no literal deny SHA in the instruction.
- Post-journal command scan: no unwrapped top-level Git command and no Python
  command lacking a journal-aware/self-recording interface.
- Required-term scan: authority, R2 tree/bytes, 2/3/3, RED/GREEN, spy,
  stale-ref rename, first-failure/no-retry, readiness, r8, canonical freeze,
  PR/merge, new VM/session, and failed-session retirement are all explicit.

## Preserved Current State

- Cursor VM/conversation created: **no**.
- Failed Cursor conversation resumed or retried: **no**.
- Evidence or GitHub issue request made: **no**.
- R3 implementation, RED/GREEN output, candidate payload, or handoff created:
  **no**.
- Readiness, r8, canonical freeze, PR, or merge created/run: **no**.
- Local branch, commit, stage, push, PR, or merge performed by this drafting
  task: **no**.

The next lawful action is not automatic execution. It is a separate user
authorization to create a brand-new Cursor cloud VM/conversation and supply
the locked instruction verbatim.
