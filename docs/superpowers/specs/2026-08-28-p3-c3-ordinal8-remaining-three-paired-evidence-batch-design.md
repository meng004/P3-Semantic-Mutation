# P3 C3 ordinal-8 remaining-three paired-evidence batch — outcome-blind preregistration

Status: preregistered, outcome-blind, not executed.
Claim C3 remains `blocked`. This document authorizes one semantic mutant and one first-order syntactic baseline for each of the three remaining frozen legal contracts, plus one 45-cell batch runner. It does not authorize a formal subject run and does not produce new kill/survival observations.

## 0. Prior disclosure (INV/TF already observed)

The first legal contract has already been executed. Those observations are disclosed here and are forbidden as a reason to change remaining slot selection, mutants, baselines, oracles, or inputs.

| Item | Frozen value |
|---|---|
| evidence commit | `1b945f1bf3238c03c9ad4dc7170dc69e6bb744c1` |
| record | `data/p3_v3/phase3/ordinal8-first-paired-evidence-clean-replay-v1/clean-replay.json` |
| artifact SHA-256 | `f0ce09ff92e181fda27573c612643d3b48a8e4e24081d390f19acc4ebbd8897f` |
| file SHA-256 | `5b734c2a21283d6cdb83a5827d50bdf688d69eb7e2dcd620d69b01a9875000ff` |
| INV/TF original | 5/5 SURVIVE |
| INV/TF semantic (`INV_TF_SCALE_CHOLESKY_FACTOR_V1`) | 5/5 KILL |
| INV/TF syntactic (`FIRST_ORDER_BOOLEAN_LITERAL_FLIP_V1`) | 5/5 KILL |
| binary kill-rate difference | 0 |

The two INV/TF patches remain excluded from this batch:

- semantic `9f0bfbb4d14bb944bf13cfdb97e135590f71208b62eabeb8b3d78937f6cfcda6`
- syntactic `234be58e515729e102dbb255564960e3767e939301d37e30a72a9fc333867f82`

Old infrastructure-failure evidence, the controlled-NumPy qualification, the controlled runtime, and this first clean-replay record must not be deleted or rewritten.

## 1. Frozen remaining selection (canonical order, no subset)

Contract root: `data/p3_v3/phase2/ordinal8-partial-contract-freeze`.
`contracts.json` SHA-256: `f89e979b4c2392ed440e37a92f9742ff68618c2961926f70bfe6096f99958457`.
Identities are read from that freeze. They are not recomputed or rewritten.

MONO slots `77f69dc9343febceb4f3f5163d6da260dbb08ed3e1a08bd30828bec11d9ca40a` and `07546603ddbc9fca6e73bc7f7e551fa52f9dfd94c648c19e7b96cb12bcb0aac0` never enter. INV/TF slot `a2f7a2164e7968cb5a6edf0aafa9bb406b8ba089df79cccdc565bdd9164cd913` is not re-executed.

Construction-mechanism axis uses the frozen historical IDs in `src/p2/mutators/operator_registry.py`: TF is a training/fit-set or produced-value transform; SI is a structure/index error. Semantic-contract families remain INV and CMP.

### 1.1 INV/SI

| Field | Frozen value |
|---|---|
| `slot_id` | `e8fd94d60c42ed7357d8e00ebc1135b55b44dbde4978f887ab54abe94b261c6c` |
| family / mechanism | INV / SI |
| `site_id` | `f37fc591deeeadf562c46130a6cc598ca142c552bbadd1d66b0d5b0d143e2fd3` |
| qualified name | `numpy.array_api.linalg:cholesky` |
| source path | `numpy/array_api/linalg.py` |
| source file SHA-256 | `b64e5f8c46b457c94a96f74da90bff368f409f9f77f27519f0c84e9517803b00` |
| frozen site span | `46:0-62:24` |
| `contract_id` | `bf30280854c72200869c82aec832543c94e50db14d918e40646c05ff8659ed10` |
| `generator_id` | `CONTRACT_ARRAY_DOMAIN_V1` |
| oracle | `CHOLESKY_RECONSTRUCTION_V1` / `factor_times_transpose_reconstructs_input` |
| activation obligation | `factorization_succeeds` |
| expected violation direction | `reconstruction_error_exceeds_tolerance` |
| tolerance | absolute `1e-10`, relative `1e-10` |
| inventory artifact | `4294c1a9c2f781c819e69d30c8e49826ef8320363e91224d8504f86bc859abad` |
| input aggregate | `477ddc91a3606bb19ca68d0f18c8b1744a865e1d547f5c14017c82ed74b16246` |

Frozen input IDs, inventory order:

1. `bafc971271795518178a0c595c4c64092bc9abb44a37a93b24a404e98e54d078`
2. `cde5b4777711071dfadb51c74bad4544c76788150d753468f51711ee3678d7a1`
3. `40373f5853a5b8cd82760ac4c3af62b85b830317d165a2c8c6a4ff290614a65d`
4. `6c2a8c10a883a22695336af7300527a25e996dc5a55bbe6f9dda7a41c0beaa72`
5. `76e75bf0a2eba34f5b91748bcd24646429275a48cda10d2bc0365f10b20834fd`

### 1.2 CMP/TF

| Field | Frozen value |
|---|---|
| `slot_id` | `e0b42ce7f2c60d9b3d0feae5ce3280d1619ec78b75c22c3e41fc6c936c3485e6` |
| family / mechanism | CMP / TF |
| `site_id` | `c7ca9add6d16308fcbc02989173ca8e786eab212724104feb6250ebf1a333c35` |
| qualified name | `numpy.typing.tests.test_typing:get_test_cases` |
| source path | `numpy/typing/tests/test_typing.py` |
| source file SHA-256 | `79058ab5ef500e34fde14babf0c5535b5613ba125371c12577a879b304c37c6c` |
| frozen site span | `123:0-129:60` |
| `contract_id` | `52e6e0336c207d7c3a38284907890fca9a750ff454e7851b2062f4d9d6b10570` |
| `generator_id` | `CONTRACT_SEQUENCE_DOMAIN_V1` |
| oracle | `PYTHON_SUFFIX_PROJECTION_V1` / `yielded_ids_equal_python_suffix_projection` |
| activation obligation | `at_least_one_accepted_and_one_rejected_suffix` |
| expected violation direction | `yielded_ids_differ_from_suffix_projection` |
| tolerance | `exact_set` |
| accepted / rejected suffixes | `.py`, `.pyi` / `.txt` |
| inventory artifact | `6465e0425d36515ebd966a6361932ac5a3f162c9a3141e9a72080faa0e357421` |
| input aggregate | `74259d06afd257f2d9a8d0854bdcfdca5546f9b3ec44daed9b27b4df08256b8b` |

Frozen input IDs, inventory order:

1. `177271477e557055b0eae40ad55409bedcd6336173054e1f248b3c8a008e71db`
2. `d731142f32f15bf44e7475ba6c41a41d14583d07649a0e22ed767a41376270cf`
3. `1673ef30f59ebbe02deca678d04a2113906186a0bef91677f8f15a781858a9b5`
4. `8e9857f5b13c86a9b69ad9b401bcaa3ff21e9732895da9f21bd2dd446fc055ec`
5. `25b89d6a90b9bd027618b73d41dad4a7accc1fe629523c875ac3ee8f50d642a4`

### 1.3 CMP/SI

| Field | Frozen value |
|---|---|
| `slot_id` | `06556e4b744f26766ef8593fc4ae727103082944ae6b26c6179fc947c3a2f1f5` |
| family / mechanism | CMP / SI |
| `site_id` | `c7ca9add6d16308fcbc02989173ca8e786eab212724104feb6250ebf1a333c35` |
| qualified name | `numpy.typing.tests.test_typing:get_test_cases` |
| source path | `numpy/typing/tests/test_typing.py` |
| source file SHA-256 | `79058ab5ef500e34fde14babf0c5535b5613ba125371c12577a879b304c37c6c` |
| frozen site span | `123:0-129:60` |
| `contract_id` | `607a987a8ed4d868903e2ba322d02e2bc2038ab97c6df94951ec37f2d16d850f` |
| `generator_id` | `CONTRACT_SEQUENCE_DOMAIN_V1` |
| oracle | `PYTHON_SUFFIX_PROJECTION_V1` / `yielded_ids_equal_python_suffix_projection` |
| activation obligation | `at_least_one_accepted_and_one_rejected_suffix` |
| expected violation direction | `yielded_ids_differ_from_suffix_projection` |
| tolerance | `exact_set` |
| inventory artifact | `db5943676f7d969f021735d375bcfd4768fe0a09a986f510e8d84b838bf71b66` |
| input aggregate | `9288075930671af56e298a0a44383739786ac13e762cfe3c447c77635b415361` |

Frozen input IDs, inventory order:

1. `edc0788958caebf8732955e946ec93ee7f67bde0de2b28243d6309651f4e0c57`
2. `c7b46a0acaac520220aa9ccc4fb005bb2811a9837cac4c48018cbb4782d587be`
3. `5bf881af9f49c5f53df0c21918161bc87fb68d76aaa1c149aeb5942b395ae1dd`
4. `899e1cf136f1fadd1e224e6687a784b747b6137251d2a8ea74d17a77e17dbe1f`
5. `4f9f97b4d159437b242e2f5f8716599364138480c53a683af357fdd7f3a462f7`

The three input-ID sets are pairwise disjoint. Each inventory has exactly five `CONTRACT_INPUT_GENERATED` rows. INV/TF inputs do not re-enter.

## 2. Semantic mutants (exactly one per slot)

### 2.1 INV/SI — `INV_SI_TRANSPOSE_CHOLESKY_FACTOR_V1`

Exact unique edit in `numpy/array_api/linalg.py` inside `46:0-62:24`:

```
    return Array._new(L)
```

is replaced by:

```
    return Array._new(L.T)
```

Span: `62:4-62:24`. Patch SHA-256: `880e678e69a48664af113042ea1828cc1fe3db7d75f2f98a9c2f5d7d0c9909c4`.

This is a structure/index error: the returned factor's triangular orientation is inverted. It is not a rename of the INV/TF scale `2 * L`. The call `np.linalg.cholesky(x._array)` remains. No call is deleted. No forced exception is introduced. No oracle is weakened.

Activation: each of the five frozen SPD matrices must reach the `upper=False` return.
Expected violation: `L.T @ (L.T).T = L.T @ L` fails to reconstruct `A = L @ L.T` beyond tolerance `1e-10`.

### 2.2 CMP/TF — `CMP_TF_EXTEND_ACCEPTED_SUFFIX_SET_V1`

Exact unique edit in `numpy/typing/tests/test_typing.py` inside `123:0-129:60`:

```
            if ext in (".pyi", ".py"):
```

is replaced by:

```
            if ext in (".pyi", ".py", ".txt"):
```

Span: `127:22-127:37`. Patch SHA-256: `bc9f5b151d48cae4a76e46e3276d75e04b018b09c5764e3ab844e113c943b29a`.

This is a TF produced-set transform: the accepted suffix set is enlarged so rejected `.txt` entries enter the yielded IDs. The walk and yield remain. No call is deleted. No exception is forced.

Activation: each frozen five-entry sequence already contains at least one accepted and one rejected suffix.
Expected violation: yielded IDs include `.txt` stems and therefore differ from the python-suffix projection under `exact_set`.

### 2.3 CMP/SI — `CMP_SI_INDEX_EXTENSION_FIELD_V1`

Exact unique edit in the same function, not the CMP/TF semantic patch:

```
            if ext in (".pyi", ".py"):
```

is replaced by:

```
            if short_fname in (".pyi", ".py"):
```

Span: `127:15-127:18`. Patch SHA-256: `0693d22901aaff058f78a08ec5f341b80a59be065048e81b5f780d129ef6d7f7`.

This is a structure/index error: the membership test binds the basename instead of the extension. It does not share the CMP/TF suffix-set transform. Walk and yield remain.

Expected violation: no payload stem equals `.py` or `.pyi`, so the yielded set is empty and differs from the python-suffix projection.

## 3. First-order syntactic baselines (exactly one per slot)

Closed first-order catalogue, applied inside the selected site span after excluding that slot's semantic span and any already-preregistered INV/TF patch:

- boolean literal flip (`False` ↔ `True`);
- membership / comparison inversion (`not in` ↔ `in`, `!=` ↔ `==`, `<` ↔ `>=`, `>` ↔ `<=`);
- constant replacement of one local string or integer token.

A token whose only effect on the frozen activation path is a forced exception is skipped. The first remaining applicable token is used. No second candidate is substituted later.

### 3.1 INV/SI — `FIRST_ORDER_MEMBERSHIP_FLIP_CHOLESKY_COMPLEX_V1`

The INV/TF syntactic token `upper: bool = False` is already consumed and is forbidden. The dtype-guard `not in` on line 54 is skipped because it would force `TypeError` on every frozen float matrix. The first remaining token is the membership test on the unused upper/complex branch:

```
        if U.dtype in [complex64, complex128]:
```

is replaced by:

```
        if U.dtype not in [complex64, complex128]:
```

Span: `59:19-59:21`. Patch SHA-256: `0e36dff5212a1db0978b5caa2a7077c6ded2b3630e83446f2e4fd523b7c5e42b`.

### 3.2 CMP/TF — `FIRST_ORDER_MEMBERSHIP_FLIP_GET_TEST_CASES_V1`

```
            if ext in (".pyi", ".py"):
```

is replaced by:

```
            if ext not in (".pyi", ".py"):
```

Span: `127:19-127:21`. Patch SHA-256: `ded9d61b450522e708287648175236fb31ff48e5584a8c0e6303d5e200c362a2`.

### 3.3 CMP/SI — `FIRST_ORDER_CONSTANT_REPLACE_PY_SUFFIX_V1`

```
            if ext in (".pyi", ".py"):
```

is replaced by:

```
            if ext in (".pyi", ".pyc"):
```

Span: `127:31-127:36`. Patch SHA-256: `ca203bbc8b9be344a54cf4b8f93e57bc4e46725c961bc0e472ea7d6cc6e99a93`.

## 4. Six-patch uniqueness and certification

The six new patches and the two excluded INV/TF patches are pairwise distinct by `patch_sha256`, operator id, and `(path, source, target)`. CMP/TF and CMP/SI do not share a semantic patch. INV/SI does not copy the INV/TF scale mutant.

Certification, before any real subject execution:

- `PATCH_SCOPE_PASS`: only the preregistered path and span change;
- `UNIQUENESS_PASS`: the six hashes differ from each other and from the two INV/TF hashes;
- chronology `SITE_FROZEN -> CONTRACT_FROZEN -> E_CONTRACT_FROZEN -> PATCH_FROZEN -> CERTIFICATION_WITNESS_SELECTED -> TERMINAL_STATE`;
- interface preserved; no call deleted; no import broken; oracle and tolerance unchanged.

## 5. Stop rules

- Three slots, fixed order INV/SI, CMP/TF, CMP/SI.
- One semantic mutant and one syntactic baseline per slot.
- Each slot consumes its own five frozen rows only.
- Each variant (original, semantic, syntactic) runs once per input.
- Total cells: `3 × 3 × 5 = 45`.
- Per-cell timeout: 60 seconds.
- Isolated controlled-NumPy subprocess per cell. Ambient NumPy `2.4.4` must not enter the import closure.
- Retry, resume, replacement, skip, slot rebinding, input substitution, and extra mutants are forbidden.
- Formal FAIL, TIMEOUT, and `FAIL_INFRASTRUCTURE` are retained. No automatic rerun.
- INV/TF 5/5–5/5 results must not revise any remaining patch.

## 6. Controlled batch runner (prepare only; do not invoke)

| Item | Frozen value |
|---|---|
| CLI | `scripts/p3_v3/run_ordinal8_remaining_three_paired_batch_v1.py` |
| module | `src/p3_v3/ordinal8_remaining_three_paired_batch_v1.py` |
| runtime | `/tmp/p3-c3-ordinal8-remaining-three-paired-batch-v1` |
| output | `data/p3_v3/phase3/ordinal8-remaining-three-paired-batch-v1` |
| staging | `data/p3_v3/phase3/ordinal8-remaining-three-paired-batch-v1.staging` |
| record | `data/p3_v3/phase3/ordinal8-remaining-three-paired-batch-v1/paired-batch.json` |
| `batch_version` | `ordinal8-remaining-three-paired-batch-v1` |

The runner rejects an already-existing runtime, output, or staging root and exposes no selector arguments. The record is validated in memory and written atomically. It must bind:

- this preregistration commit and file SHA;
- implementation commit and runner SHA;
- qualification artifact `501203515a524bcd4b51a6148908af25dbdd09932c7790e2e257404533d80abf`;
- prior INV/TF evidence artifact `f0ce09ff92e181fda27573c612643d3b48a8e4e24081d390f19acc4ebbd8897f`;
- the three slot/site/contract/inventory/input-aggregate identities;
- the six patches and certification results;
- `prior_result_disclosed=true`;
- `not_prior_runner_retry=true`.

It must not call `scripts/p3_v3/run_ordinal8_first_paired_evidence.py` or `scripts/p3_v3/run_ordinal8_controlled_numpy_clean_replay_v1.py`. Per-cell terminals and per-mutant kill/survival for all six mutants are required. An aggregate mutation score is not a substitute.

Qualification commit `256305eb7d0bd835cb1fc37d99e5cc1732fefba2`, controlled interpreter `/tmp/p3-c3-ordinal8-controlled-numpy-runtime/venv/bin/python`, and NumPy `2.0.0.dev0` are reused read-only. The runtime is not rebuilt and qualification is not rerun.

This preparation task must not call the formal batch runner and must not emit new scientific kill/survival results.

## 7. Validation boundary

Focused tests may use synthetic fixtures or stubbed processes only. They must not import or execute the real NumPy subject and must not produce scientific kill/survival observations. Outcome sources outside the allowlist (P12 issues, patches, reveal ledgers, kill matrices, profiling results, technique profiles, MONO sites, other-subject sources) remain unread.
