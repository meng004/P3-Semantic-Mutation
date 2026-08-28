# P3 C3 ordinal-8 first paired mutant evidence — outcome-blind preregistration

Status: preregistered, outcome-blind, not executed.
Claim C3 remains `blocked`. This document authorizes one semantic mutant and one first-order syntactic baseline for the first frozen ordinal-8 contract only. It does not authorize a formal subject run and does not produce kill/survival observations.

## 1. Frozen selection (no re-selection)

Canonical slot order is already frozen. This slice uses only the first slot.

| Field | Frozen value |
|---|---|
| evidence commit | `3f81139d2c620136a20fd16a16d057bd2698f1cd` |
| parent implementation commit | `f969d3354fef85ffef338b5d5b19980659c7ea96` |
| contract root | `data/p3_v3/phase2/ordinal8-partial-contract-freeze` |
| `contracts.json` SHA-256 | `f89e979b4c2392ed440e37a92f9742ff68618c2961926f70bfe6096f99958457` |
| `slot_id` | `a2f7a2164e7968cb5a6edf0aafa9bb406b8ba089df79cccdc565bdd9164cd913` |
| family / mechanism | INV / TF |
| `site_id` | `f37fc591deeeadf562c46130a6cc598ca142c552bbadd1d66b0d5b0d143e2fd3` |
| qualified name | `numpy.array_api.linalg:cholesky` |
| source path | `numpy/array_api/linalg.py` |
| frozen site span | `46:0-62:24` |
| `contract_id` | read-only from frozen `contracts.json`; expected prefix `449bc0e7` |
| `generator_id` | `CONTRACT_ARRAY_DOMAIN_V1` |
| oracle | `CHOLESKY_RECONSTRUCTION_V1` / `factor_times_transpose_reconstructs_input` |
| expected violation direction | `reconstruction_error_exceeds_tolerance` |
| inventory artifact | `a2f7cf47fc0ddb3db5f1a3268fa319debf8388061b2157b88c633ab0f4ed0c5c` |

The five frozen `input_id` values are consumed in inventory order and may not be replaced, reordered, or subsetted:

1. `82261a722a9730fd1e03c3b138f24bc7ecac9de710de9fd9ac7ae38e04a3c2b2`
2. `cbd30153ac94b040e5fee28d8c559db619ec4f7342c9fb2c2b881ed02a2d21b2`
3. `3ae9ca4d6efa478cff35e7ffb5d5be8f6dd9dea8443c43018933a206fceae2f7`
4. `499142be0698116e670bfbead9881e25ed54e3be9ff3e157c23b73e5c0d6d102`
5. `a3faf1a42deb3e155b457d1d7278b0388672895dba880b89b3c653a8484182b7`

Each payload is a 3×3 symmetric positive-definite `matrix` and does not set `upper`. The subject therefore takes the default `upper=False` path.

MONO slots `77f69dc9343febceb4f3f5163d6da260dbb08ed3e1a08bd30828bec11d9ca40a` and `07546603ddbc9fca6e73bc7f7e551fa52f9dfd94c648c19e7b96cb12bcb0aac0` remain absent and are never selectable.

CMP and SI contracts are not read for execution outcomes and are not eligible for this slice.

## 2. Semantic mutant (exactly one)

Operator id: `INV_TF_SCALE_CHOLESKY_FACTOR_V1`.

Exact edit, source-order unique in `numpy/array_api/linalg.py` inside the frozen `cholesky` span:

```
return Array._new(L)
```

is replaced by:

```
return Array._new(2 * L)
```

Span obligation: only the successful `upper=False` return at the end of `cholesky` (frozen line 62). The call `np.linalg.cholesky(x._array)` remains. No test is weakened. No call is deleted. No forced exception is introduced.

Activation obligation: each of the five frozen SPD matrices must reach that return with `upper=False`.

Expected violation direction: `reconstruction_error_exceeds_tolerance`. Scaling the factor by 2 maps a valid factorization `A ≈ L Lᵀ` onto `A ≉ (2L)(2L)ᵀ = 4 A` under the frozen reconstruction oracle and tolerance `1e-10`.

Scientific rationale (outcome-blind): the frozen contract reconstructs the input from the returned factor. Changing the returned factor while leaving factorization itself intact is a targeted INV/TF intervention on the selected site, not a derivation from a known bug, patch, or mutation outcome.

## 3. First-order syntactic baseline (exactly one)

Operator id: `FIRST_ORDER_BOOLEAN_LITERAL_FLIP_V1`.

Mechanical selection rule, fixed before any compile/test/kill observation:

1. Restrict candidates to `numpy/array_api/linalg.py` function `cholesky`, frozen span `46:0-62:24`.
2. Exclude the semantic-mutant return token span.
3. In source order, take the first one-token first-order edit from this closed catalogue:
   - boolean literal flip (`False` ↔ `True`, `True` ↔ `False`);
   - comparison inversion (`not in` ↔ `in`, `!=` ↔ `==`, `<` ↔ `>=`, `>` ↔ `<=`);
   - integer literal `n` → `n+1` if `n ≥ 0`, else `n-1`.
4. Stop at the first applicable token. Do not inspect later tokens. Do not substitute a second candidate if this one later fails to apply.

Unique selected edit: the default argument token on the function signature.

```
def cholesky(x: Array, /, *, upper: bool = False) -> Array:
```

is replaced by:

```
def cholesky(x: Array, /, *, upper: bool = True) -> Array:
```

This is one local AST/token edit in the same source file and the same direct implementation boundary as the semantic mutant. Its identity must differ from the semantic patch.

If this unique baseline is not applicable at formal execution time, the formal terminal retains that failure. A second baseline is forbidden.

## 4. Stop rules

- Semantic mutants: exactly one.
- Syntactic baselines: exactly one.
- Both consume the same five frozen rows and no others.
- Each variant (original subject, semantic mutant, syntactic baseline) is executed once per input.
- Retry, resume, replacement, additional mutants, slot rebinding, contract rebinding, and input substitution are forbidden.
- Original-subject execution may only confirm that the five inputs satisfy activation. Those observations must not revise either mutant.

## 5. Identity and fail-closed obligations

Implementation must refuse to proceed unless all of the following match the freeze:

- HEAD / evidence commit `3f81139d2c620136a20fd16a16d057bd2698f1cd`
- controlled source-tree identity already bound to ordinal 8
- `slot_id` `a2f7a216…`
- `site_id` `f37fc591…`
- `contract_id` read from frozen `contracts.json` (prefix `449bc0e7…`)
- inventory artifact `a2f7cf47…`
- exactly the five input IDs above
- each patch modifies only its preregistered span
- semantic and syntactic patch identities differ
- MONO slots never appear

User-supplied alternate slot, contract, patch, input set, or run count is rejected.

## 6. Controlled runner (prepare only; do not invoke)

| Item | Frozen value |
|---|---|
| CLI | `scripts/p3_v3/run_ordinal8_first_paired_evidence.py` |
| runtime root | `/tmp/p3-c3-ordinal8-first-paired-evidence` |
| output root | `data/p3_v3/phase3/ordinal8-first-paired-evidence` |

The runner must reject an already-existing runtime, output, or staging root. It exposes no `--retry`, `--resume`, `--skip`, `--mutant`, or `--slot` selectors. Writes are atomic. The record must keep per-input terminals for original, semantic, and syntactic variants, plus per-mutant kill/survival, retaining failure and timeout as formal observations.

This preparation task must not call the formal runner and must not emit scientific kill/survival results.

## 7. Validation boundary

Focused tests may use synthetic fixtures or stubbed processes only. They must not import or execute the real NumPy subject and must not produce scientific kill/survival observations. Outcome sources (P12 issues, patches, reveal ledgers, profiling results, technique profiles, other-contract run results) remain outside the readable set.
