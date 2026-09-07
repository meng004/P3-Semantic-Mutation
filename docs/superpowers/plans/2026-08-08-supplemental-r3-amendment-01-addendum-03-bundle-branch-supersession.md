# Supplemental R3 Amendment 01 Addendum 03 Bundle Branch Supersession

**Status:** immutable transport-only supersession for the final Cursor VM execution plan.

**Authority:** `31a4a8249f4ba6de12ba92291ab0cd55a65043b4`.

**Superseded transport value:** `codex/supplemental-r3-amendment-01-execution-bundle-a03`.

**Replacement transport value:** `codex/supplemental-r3-amendment-01-execution-bundle-a03r1`.

## Reason

The superseded remote branch already contains the earlier audited-but-operationally-incomplete bundle `a0b9bc07473a8656e4447d1fca5cfdc05aa3d8cd`. Replacing that remote ref would require a force update, which is prohibited. The replacement branch is a new, previously unpublished ref and permits a single ordinary push of the corrected linear bundle.

## Exact scope

This document supersedes only the bundle transport ref used by the sole pre-journal authorization fetch. It does not supersede or change:

- protocol `SUPPLEMENTAL_R3_EVIDENCE_AMENDMENT_01_BOOTSTRAP_ADDENDUM_03`;
- amendment ID `AMENDMENT_01_REF_ISOLATION`;
- bootstrap addendum ID `BOOTSTRAP_EXECUTION_ADDENDUM_03`;
- immutable authority `31a4a8249f4ba6de12ba92291ab0cd55a65043b4`;
- the three parent plan SHA-256 values `7adda5c7df3b792ba112e3348d64434d6543d867d339d5e301d2b096119ceac5`, `7363445ea67618e9f5bb378a0b45eaad07ed4c57f9fcce87323d99a1a6d59c5b`, and `98fe5a3a73b1b38e9a061174a2142a0fe8b3e14d24e39d8af1c412b6af04ca36`;
- Batch 3 exclusion, R2 byte/tree immutability, original R3 immutability, independent GPyTorch/chaospy/SALib quota stops `2/3/3`, first-failure shutdown, no retry/resume, or stale-ref rename tests;
- the evidence-only boundary `PENDING_LOCAL_AUDIT`;
- prohibitions on readiness, r8, canonical freeze, force push, PR, merge, and downstream execution.

The final Cursor VM execution plan must quote this document's SHA-256 and state that its own locked SHA-256 incorporates this transport-only supersession.
